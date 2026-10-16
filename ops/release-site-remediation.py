"""Bounded native release. --apply requires clean preflight, verified backup and exact file hashes."""
from pathlib import Path
import argparse,hashlib,io,json,shlex,subprocess,tarfile
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');p.add_argument('--base-release');a=p.parse_args()
names=['themes/tehnet/header.php','themes/tehnet/index.php','themes/tehnet/assets/img/tehnet-og.png','mu-plugins/tehnet-search-metadata.php','mu-plugins/tehnet-technical-resources.php','mu-plugins/tehnet-technical-resources/technical-tools.js','mu-plugins/tehnet-technical-resources/technical-tools.css','mu-plugins/tehnet-technical-resources/wireguard-mtu.py.txt','plugins/tehnet-store/tehnet-store.php','plugins/tehnet-store/includes/class-storefront.php','plugins/tehnet-store/includes/class-product-evidence.php','plugins/tehnet-store/assets/store.css','plugins/tehnet-store/assets/reviewed-model.js','plugins/tehnet-store/assets/vendor/model-viewer/model-viewer.min.js','plugins/tehnet-store/assets/vendor/model-viewer/LICENSE','plugins/tehnet-store/assets/vendor/model-viewer/PROVENANCE.json']
content=(root/'content/remediation-2026-10-16/manifest.json').read_bytes();m=json.loads(content)
names.append('mu-plugins/tehnet-technical-resources/accessibility.css')
files={n:(root/'site'/n).read_bytes()for n in names}
meta={'old':{n:m['files_before'].get(n,{}).get('sha256')for n in names},'new':{n:hashlib.sha256(b).hexdigest()for n,b in files.items()},'content_sha256':hashlib.sha256(content).hexdigest(),'migration_sha256':hashlib.sha256((root/'ops/remediate-site-content.php').read_bytes()).hexdigest()}
if a.base_release:
 base=json.loads((root/a.base_release).read_text());assert base['status']=='published';meta['old']={n:base['files'].get(n)for n in names}
digest=hashlib.sha256(json.dumps(meta,sort_keys=True).encode()).hexdigest();directory='/root/tehnet-releases/site-remediation-20261016-'+digest[:12]
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w:gz')as t:
 for n,b in {**files,'manifest.json':content,'release.json':json.dumps(meta).encode(),'remediate.php':(root/'ops/remediate-site-content.php').read_bytes()}.items():
  info=tarfile.TarInfo(n);info.size=len(b);info.mode=0o600;t.addfile(info,io.BytesIO(b))
remote=r'''
import sys,pathlib,subprocess,tarfile,io,json,hashlib,os
os.umask(0o077);d=pathlib.Path(DIRECTORY);apply=APPLY;d.mkdir(parents=True,exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()),mode='r:gz')as t:
 assert all(x.isfile() and not x.name.startswith('/') and '..'not in pathlib.PurePosixPath(x.name).parts for x in t)
 for x in t:
  b=t.extractfile(x).read();dest=d/x.name;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():assert dest.read_bytes()==b,'Stage drift'
  else:dest.write_bytes(b)
assert not (d/'outcome.json').exists(),'Release already has an outcome; inspect before repeating'
meta=json.loads((d/'release.json').read_text());live=pathlib.Path('/var/lib/docker/volumes/tehnet_tehnet-wp-data/_data/wp-content')
def run(args,data=None,timeout=120,cwd=None):
 p=subprocess.run(args,input=data,capture_output=True,timeout=timeout,cwd=cwd)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[:5000])
 return p.stdout
assert run(['docker','port','tehnet-wordpress','80/tcp']).decode().strip()=='127.0.0.1:18082'
def guard_files():
 for n,old in meta['old'].items():
  f=live/n
  assert not f.is_symlink(),'Symlink live file'
  assert (f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==old)if old else not f.exists(),'Live drift: '+n
  assert hashlib.sha256((d/n).read_bytes()).hexdigest()==meta['new'][n]
guard_files()
for n in meta['new']:
 if n.endswith('.php'):run(['docker','exec','-i','tehnet-wordpress','php','-l'],(d/n).read_bytes())
run(['docker','exec','-i','tehnet-wordpress','php','-l'],(d/'remediate.php').read_bytes())
assert hashlib.sha256((d/'manifest.json').read_bytes()).hexdigest()==meta['content_sha256']
assert hashlib.sha256((d/'remediate.php').read_bytes()).hexdigest()==meta['migration_sha256']
run(['docker','exec','tehnet-wordpress','mkdir','-p','/tmp/tn-remediation'])
for n in ['manifest.json','remediate.php']:run(['docker','cp',str(d/n),'tehnet-wordpress:/tmp/tn-remediation/'+n])
def native(mode):
 raw=run(['docker','exec','-e','TN_REMEDIATION_MODE='+mode,'tehnet-wordpress','php','/tmp/tn-store-review/wp-cli.phar','--allow-root','--path=/var/www/html','--user=AmirrezaGol','eval-file','/tmp/tn-remediation/remediate.php'])
 return json.loads(raw)
check=native('check');(d/'preflight.json').write_text(json.dumps(check,indent=2))
if not apply:print(json.dumps({'status':'preflight-passed','directory':str(d),'files':len(meta['new']),'content':check}));sys.exit(0)
assert not (d/'before.tar.gz').exists(),'Inspect prior application attempt before retry'
run(['systemctl','start','tehnet-store-backup.service'],timeout=300)
backup=max(pathlib.Path('/root/tehnet-backups').glob('*-store-review'),key=lambda p:p.stat().st_mtime)
run(['sha256sum','-c','SHA256SUMS'],cwd=backup,timeout=180)
guard_files();native('check')
with tarfile.open(d/'before.tar.gz','w:gz')as t:
 for n,old in meta['old'].items():
  if old:t.add(live/n,arcname=n,recursive=False)
def replace(n,b):
 f=live/n;missing=[];parent=f.parent
 while not parent.exists():missing.append(parent);parent=parent.parent
 for parent in reversed(missing):parent.mkdir();os.chmod(parent,0o755);os.chown(parent,33,33)
 tmp=f.with_name(f.name+'.tn-remediation-tmp');tmp.write_bytes(b);os.chmod(tmp,0o644);os.chown(tmp,33,33);os.replace(tmp,f)
before={n:(live/n).read_bytes()if old else None for n,old in meta['old'].items()}
try:
 for n in sorted(meta['new'],key=lambda n:n.endswith('/tehnet-store.php')):replace(n,(d/n).read_bytes())
 for n,digest in meta['new'].items():assert hashlib.sha256((live/n).read_bytes()).hexdigest()==digest
 applied=native('apply');repeat=native('apply');assert repeat['posts_updated']==repeat['terms_updated']==repeat['pages_created']==0
 after=native('check');assert after['posts_pending']==after['terms_pending']==after['new_pending']==0
 run(['docker','cp','tehnet-wordpress:/tmp/tn-remediation/before.json',str(d/'content-before.json')])
 result={'status':'published','directory':str(d),'files':meta['new'],'content_sha256':meta['content_sha256'],'backup':str(backup),'backup_checksums_verified':True,'preflight':check,'applied':applied,'repeat':repeat,'after':after,'file_rollback':str(d/'before.tar.gz'),'content_rollback':str(d/'content-before.json')}
 (d/'outcome.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
except Exception as e:
 rollback={'error':str(e)}
 try:rollback['content']=native('rollback')
 except Exception as r:rollback['content_rollback_error']=str(r)
 for n,b in before.items():
  f=live/n
  if b is not None:replace(n,b)
  elif f.exists()and hashlib.sha256(f.read_bytes()).hexdigest()==meta['new'][n]:f.unlink()
 (d/'failed.json').write_text(json.dumps(rollback,indent=2));raise
'''.replace('DIRECTORY',repr(directory)).replace('APPLY',repr(a.apply))
compile(remote,'native-release','exec')
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','netauto-main','python3 -c '+shlex.quote(remote)],input=buf.getvalue(),capture_output=True,timeout=600)
if r.returncode:raise RuntimeError((r.stdout+r.stderr).decode(errors='replace'))
result=json.loads(r.stdout);out=root/'seo/remediation-2026-10-16';out.mkdir(exist_ok=True)
(out/(('release-followup.json'if a.base_release else'release.json')if a.apply else'preflight.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'directory':directory,'files':len(files),'content':result.get('applied',result.get('content'))},ensure_ascii=True))
