"""Nine-file Store-only release: immutable hashes, full checkpoint, state guards, rollback.

Default is preflight only. --apply requires exactly the same immutable manifest.
--rollback uses the recorded archive and refuses later changes to those paths.
No migrations, product writes, payment calls, theme or Core replacement.
"""
from pathlib import Path
import argparse, datetime, hashlib, io, json, shlex, subprocess, tarfile

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();mode=p.add_mutually_exclusive_group();mode.add_argument('--apply',action='store_true');mode.add_argument('--rollback',action='store_true');a=p.parse_args()
names=['tehnet-store.php','includes/class-storefront.php','includes/class-product-evidence.php','includes/class-product-visuals.php','assets/store.js','assets/reviewed-model.js','assets/store-experience.css','assets/model-controls.js','assets/model-controls.css']
files={'plugins/tehnet-store/'+n:(root/'site/plugins/tehnet-store'/n).read_bytes()for n in names}
sha=lambda data:hashlib.sha256(data).hexdigest()
old={}
for n in files:
    q=subprocess.run(['git','show','9d28f22:site/'+n],cwd=root,capture_output=True)
    if q.returncode:
        assert n in ['plugins/tehnet-store/assets/'+s for s in ['store-experience.css','model-controls.js','model-controls.css']],q.stderr.decode()
        old[n]=None
    else:old[n]=sha(q.stdout)
state=(root/'ops/shop-experience-state.php').read_bytes()
meta={'baseline_commit':'9d28f22','old':old,'new':{n:sha(b)for n,b in files.items()},'state_sha256':sha(state)}
digest=sha(json.dumps(meta,sort_keys=True).encode());directory='/root/tehnet-releases/shop-experience-20261016-'+digest[:12]
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w:gz')as archive:
    for n,b in {**files,'manifest.json':json.dumps(meta).encode(),'state.php':state}.items():
        info=tarfile.TarInfo(n);info.size=len(b);info.mode=0o600;archive.addfile(info,io.BytesIO(b))
remote=r'''
import datetime,hashlib,io,json,os,pathlib,subprocess,sys,tarfile
os.umask(0o077);d=pathlib.Path(DIRECTORY);d.mkdir(parents=True,exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()),mode='r:gz')as archive:
 for item in archive:
  assert item.isfile()and not item.name.startswith('/')and'..'not in pathlib.PurePosixPath(item.name).parts
  data=archive.extractfile(item).read();f=d/item.name;f.parent.mkdir(parents=True,exist_ok=True)
  if f.exists():assert f.read_bytes()==data,'Immutable release drift'
  else:f.write_bytes(data)
meta=json.loads((d/'manifest.json').read_text());live=pathlib.Path('/var/lib/docker/volumes/tehnet_tehnet-wp-data/_data/wp-content')
sha=lambda data:hashlib.sha256(data).hexdigest()
def run(argv,data=None,timeout=120,cwd=None):
 p=subprocess.run(argv,input=data,capture_output=True,timeout=timeout,cwd=cwd)
 if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[:4000])
 return p.stdout
assert run(['docker','port','tehnet-wordpress','80/tcp']).decode().strip()=='127.0.0.1:18082'
for n in meta['new']:
 assert n.startswith('plugins/tehnet-store/')and'..'not in pathlib.PurePosixPath(n).parts
 assert (live/n).resolve().is_relative_to(live.resolve())and not(live/n).is_symlink()
 assert sha((d/n).read_bytes())==meta['new'][n]
 if n.endswith('.php'):run(['docker','exec','-i','tehnet-wordpress','php','-l'],(d/n).read_bytes())
assert sha((d/'state.php').read_bytes())==meta['state_sha256']
run(['docker','exec','-i','tehnet-wordpress','php','-l'],(d/'state.php').read_bytes())
run(['docker','exec','tehnet-wordpress','mkdir','-p','/tmp/tn-shop-ux'])
run(['docker','cp',str(d/'state.php'),'tehnet-wordpress:/tmp/tn-shop-ux/state.php'])
def native():return json.loads(run(['docker','exec','tehnet-wordpress','php','/tmp/tn-store-review/wp-cli.phar','--allow-root','--path=/var/www/html','--user=AmirrezaGol','eval-file','/tmp/tn-shop-ux/state.php']))
def guard(expected):
 for n,h in expected.items():
  f=live/n
  assert (f.is_file()and sha(f.read_bytes())==h)if h else not f.exists(),'Live drift: '+n
def replace(n,b,mode=0o644,uid=33,gid=33):
 f=live/n;assert f.parent.is_dir()
 tmp=f.with_name(f.name+'.tn-ux-tmp');assert not tmp.exists()
 try:
  tmp.write_bytes(b);os.chmod(tmp,mode);os.chown(tmp,uid,gid);os.replace(tmp,f)
 finally:
  if tmp.exists():tmp.unlink()
def restore():
 guard(meta['new'])
 with tarfile.open(d/'before.tar.gz','r:gz')as archive:
  for n,h in meta['old'].items():
   f=live/n
   if h:
    item=archive.getmember(n);b=archive.extractfile(item).read();assert sha(b)==h;replace(n,b,item.mode,item.uid,item.gid)
   else:f.unlink()
 guard(meta['old'])
def smoke(expect_style):
 for path in ['/shop/','/?post_type=product&p='+str(before['published_product_ids'][0])]:
  html=run(['curl','--fail','--silent','--show-error','--location','--max-time','45','-H','Host: tehnet.ir','http://127.0.0.1:18082'+path]).decode()
  assert 'noindex'in html and 'woocommerce'in html
  if expect_style:assert 'tn-shop-experience-css'in html
before=native()
if ROLLBACK:
 result=json.loads((d/'outcome.json').read_text());assert result['status']=='published'
 assert before==result['after'],'Data drift since release; inspect rollback impact'
 restore();smoke(False);after=native();assert after==result['before']
 value={'status':'rolled-back','directory':str(d),'state_unchanged':True};(d/'rollback.json').write_text(json.dumps(value,indent=2));print(json.dumps(value));sys.exit(0)
assert not(d/'outcome.json').exists()and not(d/'before.tar.gz').exists(),'Inspect previous apply before retry'
guard(meta['old']);smoke(False);(d/'preflight.json').write_text(json.dumps(before,indent=2))
if not APPLY:print(json.dumps({'status':'preflight-passed','directory':str(d),'changed_files':meta['new'],'before':before}));sys.exit(0)
start=datetime.datetime.now(datetime.timezone.utc).timestamp()
run(['systemctl','start','tehnet-store-backup.service'],timeout=360)
backup=max(pathlib.Path('/root/tehnet-backups').glob('*-store-review'),key=lambda f:f.stat().st_mtime)
assert backup.stat().st_mtime>=start-2,'Fresh full backup required'
run(['sha256sum','-c','SHA256SUMS'],cwd=backup,timeout=180)
guard(meta['old']);assert native()==before,'Protected state drift before apply'
with tarfile.open(d/'before.tar.gz','w:gz')as archive:
 for n,h in meta['old'].items():
  if h:archive.add(live/n,arcname=n,recursive=False)
try:
 for n in sorted(meta['new'],key=lambda n:n.endswith('/tehnet-store.php')):replace(n,(d/n).read_bytes())
 guard(meta['new']);smoke(True);after=native();assert after==before,'Protected state changed'
 result={'status':'published','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'directory':str(d),'changed_files':meta['new'],'before':before,'after':after,'protected_state_unchanged':True,'backup':str(backup),'backup_checksums_verified':True,'file_rollback':str(d/'before.tar.gz'),'data_migrations':False}
 (d/'outcome.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
except Exception as error:
 # Copy failure may leave only part of the allowlist updated. Refuse human drift.
 for n,h in meta['old'].items():
  f=live/n;current=sha(f.read_bytes())if f.exists()else None
  assert current in [h,meta['new'][n]],'Rollback refused unrelated live change: '+n
 with tarfile.open(d/'before.tar.gz','r:gz')as archive:
  for n,h in meta['old'].items():
   if h:
    item=archive.getmember(n);b=archive.extractfile(item).read();assert sha(b)==h;replace(n,b,item.mode,item.uid,item.gid)
   elif(live/n).exists():(live/n).unlink()
 guard(meta['old']);(d/'failed.json').write_text(json.dumps({'error':str(error),'file_rollback_completed':True}));raise
'''.replace('DIRECTORY',repr(directory)).replace('APPLY',repr(a.apply)).replace('ROLLBACK',repr(a.rollback))
compile(remote,'shop-experience-release','exec')
q=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','netauto-main','python3 -c '+shlex.quote(remote)],input=buf.getvalue(),capture_output=True,timeout=720)
if q.returncode:raise RuntimeError((q.stdout+q.stderr).decode(errors='replace'))
result=json.loads(q.stdout);out=root/'qa/shop-ux-2026-10-16';out.mkdir(exist_ok=True)
if a.apply:
 previous=json.loads((root/'seo/remediation-2026-10-16/release-followup.json').read_text());result['files']={**previous['files'],**result['changed_files']}
(out/('rollback.json'if a.rollback else'release.json'if a.apply else'preflight.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':result['status'],'directory':directory,'files':len(files),'backup_checksums_verified':result.get('backup_checksums_verified'),'protected_state_unchanged':result.get('protected_state_unchanged')},ensure_ascii=True))
