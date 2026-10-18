#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
OPS=${OPS:?Set an isolated operator code and metadata directory}
[[ "$(readlink /proc/self/ns/mnt)" != "$(readlink /proc/1/ns/mnt)" ]] || { echo 'Requires a private mount namespace' >&2; exit 2; }
export PYTHONPATH=$OPS:${HOST_SITE:?Set the existing pinned host-site dependency directory} PYTHONDONTWRITEBYTECODE=1
gpgv --keyring /usr/share/keyrings/ubuntu-archive-keyring.gpg --status-fd 1 "$OPS/metadata/SHA256SUMS.gpg" "$OPS/metadata/SHA256SUMS" | grep -q 'VALIDSIG 843938DF228D22F7B3742BC0D94AA3F0EFE21092 '
test -f "$OPS/containers.before"
test -f "$OPS/protected.before"
LAB=$(mktemp -d /run/tehnet-offline-discovery.XXXXXX)
cleanup(){ status=$?; trap - EXIT; umount -R "$LAB"; rmdir "$LAB"; exit "$status"; }
trap cleanup EXIT
mount -t tmpfs -o noswap,size=768m,mode=700 tmpfs "$LAB"
findmnt -n -o OPTIONS "$LAB" | grep -qw noswap
export LAB OPS
python3 - <<'PY'
import os,hashlib,threading,tarfile,json,time
from pathlib import Path
from app.netguard import validate_target
from app.http_client import PinnedHTTPSConnection,abort
from tools.offline_lab import extract_clean_root
root=Path(os.environ['LAB']);meta=Path(os.environ['OPS'])/'metadata'
if os.environ.get('SOFTWARE_REFRESH_BUDGET_FILE'):
 from tools.refresh_transport import reserve_request
 reserve_request(os.environ['SOFTWARE_REFRESH_BUDGET_FILE'],40*1024**2)
host='cdimage.ubuntu.com';path='ubuntu-base/releases/24.04/release/ubuntu-base-24.04.5-base-amd64.tar.gz'
target=validate_target('https://'+host,path,{host});connection=PinnedHTTPSConnection(target,10)
timer=threading.Timer(60,abort,args=(connection,));timer.daemon=True;timer.start()
digest=hashlib.sha256();count=0;start=time.monotonic()
try:
 connection.request('GET','/'+path,headers={'Accept-Encoding':'identity','User-Agent':'TehNet-Offline-Lab/1'})
 response=connection.getresponse();assert response.status==200
 with (root/'base.tar.gz').open('xb') as f:
  while True:
   chunk=response.read1(65536)
   if not chunk:break
   count+=len(chunk)
   if count>40*1024**2:raise ValueError('Rootfs cap')
   digest.update(chunk);f.write(chunk)
finally:timer.cancel();connection.close()
expected=next(line.split()[0] for line in (meta/'SHA256SUMS').read_text().splitlines() if line.endswith(' *ubuntu-base-24.04.5-base-amd64.tar.gz'))
assert digest.hexdigest()==expected
extract_clean_root(root/'base.tar.gz',root/'root')
result={'base':'ubuntu-base-24.04.5-base-amd64.tar.gz','base_sha256':expected,'base_bytes':count,'signature_key':'843938DF228D22F7B3742BC0D94AA3F0EFE21092','tls_verified':True,'payload_location':'private tmpfs,noswap','elapsed_seconds':round(time.monotonic()-start,3)}
(meta/'baseline.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
PY
ROOT="$LAB/root"
export ROOT
mkdir -p "$ROOT/etc/ssl/certs"
cp /etc/ssl/certs/ca-certificates.crt "$ROOT/etc/ssl/certs/ca-certificates.crt"
printf '127.0.0.1 localhost\n185.143.233.132 mirror.arvancloud.ir\n' > "$ROOT/etc/hosts"
rm -f "$ROOT/etc/apt/sources.list.d/ubuntu.sources"
if [[ -n "${SOFTWARE_REFRESH_BUDGET_FILE:-}" ]]; then
python3 - <<'PY'
from pathlib import Path
import os
from tools.refresh_transport import populate_repo
meta=Path(os.environ['OPS'])/'metadata'
populate_repo(Path(os.environ['ROOT'])/'repo',meta,os.environ['SOFTWARE_REFRESH_BUDGET_FILE'],meta/'previous-profile.json')
PY
: > "$ROOT/etc/apt/sources.list"
for suite in noble noble-updates noble-security; do
 printf 'deb [arch=amd64 signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] file:/repo %s main universe\n' "$suite" >> "$ROOT/etc/apt/sources.list"
done
else
cat > "$ROOT/etc/apt/sources.list" <<'SOURCES'
deb [arch=amd64 signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] https://mirror.arvancloud.ir/ubuntu noble main universe
deb [arch=amd64 signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] https://mirror.arvancloud.ir/ubuntu noble-updates main universe
deb [arch=amd64 signed-by=/usr/share/keyrings/ubuntu-archive-keyring.gpg] https://mirror.arvancloud.ir/ubuntu noble-security main universe
SOURCES
fi
cat > "$ROOT/etc/apt/apt.conf.d/99tehnet-lab" <<'CONF'
APT::Install-Recommends "false";
Acquire::Languages "none";
Acquire::Retries "0";
Acquire::http::AllowRedirect "false";
Acquire::https::AllowRedirect "false";
Acquire::http::Timeout "10";
Acquire::https::Timeout "10";
APT::Update::Error-Mode "any";
CONF
chroot "$ROOT" dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n' > "$OPS/metadata/baseline-packages.tsv"
if [[ -n "${SOFTWARE_REFRESH_BUDGET_FILE:-}" ]]; then
 unshare --net chroot "$ROOT" apt-get update
else
 chroot "$ROOT" apt-get update
fi
python3 - <<'PY'
import os,subprocess,re,json
from pathlib import Path
root=Path(os.environ['ROOT']);out=Path(os.environ['OPS'])/'metadata'
for file in (root/'var/lib/apt/lists').glob('*_InRelease'):(out/file.name).write_bytes(file.read_bytes())
seeds=[]
for package in ['git','curl','jq','python3.12-minimal','python3-pip','wget','rsync','openssh-client','ca-certificates']:
 text=subprocess.check_output(['chroot',str(root),'apt-cache','policy',package],text=True)
 version=re.search(r'Candidate: (\S+)',text).group(1)
 assert version!='(none)'
 seeds.append({'package':package,'version':version})
(out/'native-seeds.json').write_text(json.dumps(seeds,indent=2)+'\n')
with (out/'native-plan.txt').open('w') as stream:subprocess.run(['chroot',str(root),'apt-get','--assume-yes','--no-install-recommends','--print-uris','--download-only','install',*[s['package']+'='+s['version'] for s in seeds]],stdout=stream,check=True)
PY
cat "$OPS/metadata/native-plan.txt"
python3 - <<'PY'
import os,subprocess,json,re,hashlib
from urllib.parse import unquote
from pathlib import Path
root=Path(os.environ['LAB'])/'root';out=Path(os.environ['OPS'])/'metadata'
plan=(out/'native-plan.txt').read_text()
if os.environ.get('SOFTWARE_REFRESH_BUDGET_FILE'):plan=plan.replace("'file:/repo/","'https://mirror.arvancloud.ir/ubuntu/")
uris=re.findall(r"^'(https://[^']+)' ([^ ]+) ([0-9]+) (.+)$",plan,re.M)
assert uris and len(uris)<=200
names=set()
for url,filename,size,checksum in uris:
 assert url.startswith('https://mirror.arvancloud.ir/ubuntu/pool/') and filename.endswith('.deb')
 names.add(filename.split('_')[0])
indices=[];selected={}
for index in sorted((root/'var/lib/apt/lists').glob('*_binary-amd64_Packages*')):
 raw=subprocess.check_output(['/usr/lib/apt/apt-helper','cat-file',str(index)])
 if len(raw)>256*1024**2:raise ValueError('Index expansion cap')
 label=index.name
 for para in raw.decode().split('\n\n'):
  fields={};last=None
  for line in para.splitlines():
   if line.startswith(' '):continue
   if ':' in line:last,value=line.split(':',1);fields[last]=value.strip()
  if fields.get('Package') in names:
   key=(fields.get('Filename','').split('/')[-1])
   if any(key==unquote(u[0]).split('/')[-1] for u in uris):selected.setdefault(key,[]).append({'index':label,'record':fields})
 indices.append({'file':label,'expanded_bytes':len(raw),'expanded_sha256':hashlib.sha256(raw).hexdigest()})
for file in (root/'var/lib/apt/lists').glob('*_InRelease'):(out/file.name).write_bytes(file.read_bytes())
assert set(selected)=={unquote(u[0]).split('/')[-1] for u in uris},set(unquote(u[0]).split('/')[-1] for u in uris)-set(selected)
result={'native_uris':[dict(url=u,filename=f,size=int(s),native_checksum=c) for u,f,s,c in uris],'signed_index_records':selected,'indices':indices,'download_bytes':sum(int(u[2]) for u in uris),'package_count':len(uris),'payloads_downloaded':False}
(out/'dependency-discovery.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'packages':len(uris),'bytes':result['download_bytes'],'selected_records':len(selected)}))
PY
echo NATIVE_SIGNED_DEPENDENCY_DISCOVERY_PASS
