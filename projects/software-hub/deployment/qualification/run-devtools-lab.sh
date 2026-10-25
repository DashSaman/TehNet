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
mkdir -p "$ROOT/dev" "$ROOT/proc" "$ROOT/kit"
for pair in 'null 1 3' 'zero 1 5' 'random 1 8' 'urandom 1 9'; do read -r name major minor <<< "$pair"; mknod -m 666 "$ROOT/dev/$name" c "$major" "$minor"; done
ln -s /proc/self/fd "$ROOT/dev/fd"
ln -s /proc/self/fd/0 "$ROOT/dev/stdin"
ln -s /proc/self/fd/1 "$ROOT/dev/stdout"
ln -s /proc/self/fd/2 "$ROOT/dev/stderr"
printf '#!/bin/sh\nexit 101\n' > "$ROOT/usr/sbin/policy-rc.d"
chmod 755 "$ROOT/usr/sbin/policy-rc.d"
python3 - <<'PY'
import json,os,hashlib,time
from pathlib import Path
from tools.offline_kit import prepare
root=Path(os.environ['LAB']);ops=Path(os.environ['OPS']);profile=json.loads((ops/'metadata/profile-unaccepted.json').read_text())
if os.environ.get('SOFTWARE_REFRESH_BUDGET_FILE'):
 from tools.refresh_transport import install_budget_hook
 install_budget_hook(os.environ['SOFTWARE_REFRESH_BUDGET_FILE'])
start=time.monotonic();result=prepare(profile,root/'kit',require_accepted=False)
result['elapsed_seconds']=round(time.monotonic()-start,3);result['scope']='Actual code qualification; profile still unaccepted until offline installation and smoke pass'
(ops/'metadata/kit-preparation.json').write_text(json.dumps(result,indent=2)+'\n')
print('KIT_FULL_SIGNED_CHAIN_AND_BYTES_PASS',flush=True)
PY
cp "$OPS/devtools-smoke.py" "$LAB/kit/smoke.py"
mount --bind "$LAB/kit" "$ROOT/kit"
rm -f "$ROOT/etc/apt/sources.list.d/ubuntu.sources"
printf '' > "$ROOT/etc/apt/sources.list"
printf '127.0.0.1 localhost\n' > "$ROOT/etc/hosts"
chroot "$ROOT" dpkg-query -W -f='${Package}\t${Version}\t${Architecture}\n' > "$OPS/metadata/offline-before-packages.tsv"
unshare --net --pid --fork --mount-proc="$ROOT/proc" /bin/bash <<'OFFLINE'
set -Eeuo pipefail
ip link set lo up
python3 - <<'PY'
import os,socket,json,hashlib,subprocess,time
from pathlib import Path
root=Path(os.environ['ROOT']);ops=Path(os.environ['OPS']);kit=root/'kit';meta=ops/'metadata'
links=json.loads(subprocess.check_output(['ip','-j','link'],text=True))
assert [link['ifname'] for link in links if 'UP' in link['flags']]==['lo'],links
assert not json.loads(subprocess.check_output(['ip','-j','route'],text=True))
assert not json.loads(subprocess.check_output(['ip','-6','-j','route'],text=True))
try:socket.create_connection(('1.1.1.1',443),timeout=1)
except OSError:pass
else:raise AssertionError('External network unexpectedly available')
lists_before=len(list((root/'var/lib/apt/lists').glob('*Packages*')))
def status():return hashlib.sha256((root/'var/lib/dpkg/status').read_bytes()).hexdigest()
original=status();profile=json.loads((kit/'profile.json').read_text());required=next(p for p in profile['packages'] if p['package']=='libjq1');file=kit/'archives'/required['cache_filename'];raw=file.read_bytes();outcomes={}
def install(label):
 start=time.monotonic()
 with (meta/(label+'.log')).open('w') as out:result=subprocess.run(['chroot',str(root),'/bin/bash','/kit/install.sh'],stdout=out,stderr=subprocess.STDOUT,env={**os.environ,'DEBIAN_FRONTEND':'noninteractive'})
 return result.returncode,round(time.monotonic()-start,3)
file.write_bytes(raw[:-1]+bytes([raw[-1]^1]));result,elapsed=install('offline-corrupted-dependency')
assert result!=0 and status()==original
outcomes['corrupt_required_archive']={'exit':result,'elapsed_seconds':elapsed,'dpkg_unchanged':True};file.write_bytes(raw)
hidden=kit/'hidden-required.deb';os.replace(file,hidden);result,elapsed=install('offline-missing-dependency')
assert result!=0 and status()==original
outcomes['missing_required_archive']={'exit':result,'elapsed_seconds':elapsed,'dpkg_unchanged':True};os.replace(hidden,file)
signed=kit/'repo/dists/noble-updates/InRelease';old=signed.read_text();signed.write_text(old.replace('Origin: Ubuntu','Origin: forged',1));result,elapsed=install('offline-forged-signature')
assert result!=0 and status()==original
outcomes['forged_signed_metadata']={'exit':result,'elapsed_seconds':elapsed,'dpkg_unchanged':True};signed.write_text(old)
status_file=root/'var/lib/dpkg/status';status_bytes=status_file.read_bytes()
assert any(p['package']=='libonig5' for p in profile['packages'])
status_file.write_bytes(status_bytes+b'\nPackage: libonig5\nStatus: install ok installed\nPriority: optional\nSection: libs\nInstalled-Size: 1\nMaintainer: Offline fixture <offline@example.invalid>\nArchitecture: amd64\nVersion: 99:99\nDescription: Newer installed dependency test fixture\n\n')
newer=status();result,elapsed=install('offline-newer-dependency')
assert result!=0 and status()==newer
outcomes['newer_nonseed_dependency']={'exit':result,'elapsed_seconds':elapsed,'dpkg_unchanged':True};status_file.write_bytes(status_bytes)
result,elapsed=install('offline-clean-install')
assert result==0,(meta/'offline-clean-install.log').read_text()
assert not subprocess.check_output(['chroot',str(root),'dpkg','--audit'])
outcomes['clean_offline_install']={'exit':result,'elapsed_seconds':elapsed,'dpkg_audit':'empty'}
smoke=subprocess.run(['chroot',str(root),'python3','/kit/smoke.py'],capture_output=True,text=True)
if smoke.returncode:raise AssertionError(smoke.stdout+smoke.stderr)
data=json.loads(smoke.stdout);data['qualified_profile_sha256']=hashlib.sha256((kit/'profile.json').read_bytes()).hexdigest();data['negative_checks']=outcomes;data['baseline_status_sha256']=original;data['offline_lists_before']=lists_before;data['network_links']=links;data['network_isolation']='Fresh namespace,only loopback up,no default/foreign route; kernel-created tunnel interfaces remain DOWN; no host firewall/network change';data['rootfs']='Clean signed Ubuntu Base24.04.5 amd64,not a booted VM'
(meta/'offline-install-acceptance.json').write_text(json.dumps(data,indent=2)+'\n')
print(json.dumps({'offline_installed_packages':data['installed_packages'],'tools':data['functional_tools'],'negative_checks':outcomes}),flush=True)
PY
OFFLINE
python3 - <<'PY'
import os,json,subprocess,hashlib
from pathlib import Path
ops=Path(os.environ['OPS']);meta=ops/'metadata';lab=Path(os.environ['LAB'])
assert sorted(subprocess.check_output(['docker','ps','-a','--no-trunc','--format','{{.Names}}|{{.ID}}|{{.Image}}|{{.Ports}}'],text=True).splitlines())==sorted((ops/'containers.before').read_text().splitlines())
for line in (ops/'protected.before').read_text().splitlines():
 digest,file=line.split('  ',1);assert hashlib.sha256(Path(file).read_bytes()).hexdigest()==digest,file
group=Path('/sys/fs/cgroup')/Path('/proc/self/cgroup').read_text().split('0::',1)[1].strip().lstrip('/')
metrics={name:(group/name).read_text().strip() for name in ['memory.peak','memory.swap.current','memory.events']}
assert metrics['memory.swap.current']=='0' and 'oom_kill 0' in metrics['memory.events']
result={'tmpfs_options':subprocess.check_output(['findmnt','-n','-o','OPTIONS',str(lab)],text=True).strip(),'cgroup':metrics,'all_existing_container_fingerprints_preserved':True,'nginx_and_selected_protected_files_preserved':True,'software_payload_disk_files':0,'downloaded_archives_location':'private,noswap768MiB tmpfs; destroyed at namespace exit','baseline_and_kit_source':'official signed Ubuntu Base + original approved Arvan Ubuntu main/universe','engine_state_read':'intentionally inaccessible' if os.environ.get('LAB_STATE_READ')=='0' else 'directly inspected','state_files':None if os.environ.get('LAB_STATE_READ')=='0' else sorted(str(f.relative_to('/srv/tehnet-software')) for f in Path('/srv/tehnet-software').rglob('*') if f.is_file())}
(meta/'lab-state.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
PY
echo NATIVE_CLEAN_OFFLINE_DEVTOOLS_ACCEPTANCE_PASS
