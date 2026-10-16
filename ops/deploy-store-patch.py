"""Small guarded Store-only patch over a recorded release; explicit --apply required."""
from pathlib import Path
import argparse,hashlib,io,json,re,shlex,subprocess,tarfile
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--base',required=True);p.add_argument('--label',required=True);p.add_argument('--apply',action='store_true');p.add_argument('--new-file',action='append',default=[]);p.add_argument('files',nargs='+');args=p.parse_args()
assert re.fullmatch(r'[a-z0-9-]{3,50}',args.label)
base=json.loads((root/args.base).read_text());allowed={}
for name in args.files:
    path=(root/name).resolve();assert path.is_relative_to((root/'site/plugins/tehnet-store').resolve()) and path.is_file() and path.suffix in ['.php','.js','.css','.svg']
    relative=path.relative_to(root/'site').as_posix();assert relative in base['files'] or name in args.new_file,'New Store paths require explicit --new-file'
    if name in args.new_file:assert relative not in base['files'],'An existing path is not a new file'
    allowed[relative]=path.read_bytes()
assert set(args.new_file).issubset(args.files)
meta={'base':base['directory'],'label':args.label,'old':{name:base['files'].get(name) for name in allowed},'new':{name:hashlib.sha256(data).hexdigest() for name,data in allowed.items()}}
digest=hashlib.sha256(json.dumps(meta,sort_keys=True).encode()).hexdigest()
if not args.apply:print(json.dumps({'dry_run':True,'manifest':meta,'digest':digest}));raise SystemExit(0)
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w:gz') as archive:
    for name,data in allowed.items():info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o600;archive.addfile(info,io.BytesIO(data))
    data=json.dumps(meta).encode();info=tarfile.TarInfo('patch.json');info.size=len(data);info.mode=0o600;archive.addfile(info,io.BytesIO(data))
remote=r'''
import io,tarfile,sys,pathlib,subprocess,json,hashlib,os
os.umask(0o077);d=pathlib.Path(DIRECTORY);assert not d.exists(),'Inspect previous outcome before retry';d.mkdir(parents=True)
with tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()),mode='r:gz') as archive:
    assert all(m.isfile() and not m.name.startswith('/') and '..' not in pathlib.PurePosixPath(m.name).parts for m in archive);archive.extractall(d,filter='data')
meta=json.loads((d/'patch.json').read_text())
def run(argv,data=None):
    p=subprocess.run(argv,input=data,capture_output=True,timeout=120)
    if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[:1000])
    return p.stdout
assert run(['docker','port','tehnet-wordpress','80/tcp']).decode().strip()=='127.0.0.1:18082'
prior={}
for name,old in meta['old'].items():
    assert name.startswith('plugins/tehnet-store/') and '..' not in pathlib.PurePosixPath(name).parts
    if old is None:
        assert subprocess.run(['docker','exec','tehnet-wordpress','test','-e','/var/www/html/wp-content/'+name],capture_output=True).returncode==1,'New path already exists: '+name
        prior[name]=None
    else:
        prior[name]=run(['docker','exec','tehnet-wordpress','cat','/var/www/html/wp-content/'+name]);assert hashlib.sha256(prior[name]).hexdigest()==old,'Live drift: '+name
    assert hashlib.sha256((d/name).read_bytes()).hexdigest()==meta['new'][name]
    if name.endswith('.php'):run(['docker','exec','-i','tehnet-wordpress','php','-l'],(d/name).read_bytes())
with tarfile.open(d/'before.tar.gz',mode='w:gz') as archive:
    for name,data in prior.items():
        if data is not None:info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o600;archive.addfile(info,io.BytesIO(data))
try:
    for name in meta['new']:
        run(['docker','cp',str(d/name),'tehnet-wordpress:/var/www/html/wp-content/'+name]);run(['docker','exec','tehnet-wordpress','chown','www-data:www-data','/var/www/html/wp-content/'+name])
    for name,digest in meta['new'].items():assert hashlib.sha256(run(['docker','exec','tehnet-wordpress','cat','/var/www/html/wp-content/'+name])).hexdigest()==digest
except Exception:
    for name,data in prior.items():
        if data is not None:run(['docker','exec','-i','tehnet-wordpress','sh','-c','cat > /var/www/html/wp-content/'+name],data)
        elif subprocess.run(['docker','exec','tehnet-wordpress','test','-f','/var/www/html/wp-content/'+name],capture_output=True).returncode==0:
            if hashlib.sha256(run(['docker','exec','tehnet-wordpress','cat','/var/www/html/wp-content/'+name])).hexdigest()==meta['new'][name]:run(['docker','exec','tehnet-wordpress','rm','--','/var/www/html/wp-content/'+name])
    raise
result={'status':'published','directory':str(d),'files':meta['new'],'base':meta['base'],'settings_or_data_mutated':False,'backup':str(d/'before.tar.gz')};(d/'outcome.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''.replace('DIRECTORY',repr('/root/tehnet-releases/'+args.label+'-'+digest[:12]));compile(remote,'store-patch','exec')
proc=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','netauto-main','python3 -c '+shlex.quote(remote)],input=buf.getvalue(),capture_output=True,timeout=180)
if proc.returncode:raise RuntimeError((proc.stdout+proc.stderr).decode(errors='replace'))
result=json.loads(proc.stdout);(root/'qa/store-2026-10-15'/('production-'+args.label+'.json')).write_text(json.dumps(result,indent=2));print('STORE_PATCH_PUBLISHED='+args.label)
