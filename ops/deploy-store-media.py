"""Publish the verified visual/invoice allowlist over the recorded first review release."""
from pathlib import Path
import hashlib,io,json,shlex,subprocess,tarfile
root=Path(__file__).resolve().parents[1];first=json.loads((root/'qa/store-2026-10-15/production-release.json').read_text())
tests=json.loads((root/'qa/store-2026-10-15/product-media-browser.json').read_text());assert tests['status']=='passed'
assert json.loads((root/'qa/store-2026-10-15/account-browser-results.json').read_text())['customerOwnInvoice']
files={}
for p in (root/'site/plugins/tehnet-store').rglob('*'):
    if p.is_file():files['plugins/tehnet-store/'+p.relative_to(root/'site/plugins/tehnet-store').as_posix()]=p.read_bytes()
files['plugins/tehnet-core/includes/class-quotes.php']=(root/'site/plugins/tehnet-core/includes/class-quotes.php').read_bytes()
meta={'base':first['directory'],'files':{name:hashlib.sha256(data).hexdigest() for name,data in files.items()}}
files['release-media.json']=json.dumps(meta).encode();digest=hashlib.sha256(files['release-media.json']).hexdigest()
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w:gz') as archive:
    for name,data in files.items():
        info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o600;archive.addfile(info,io.BytesIO(data))
remote=r'''
import io,tarfile,subprocess,sys,pathlib,json,hashlib,os
os.umask(0o077);directory=pathlib.Path(DIRECTORY);assert not directory.exists();directory.mkdir(parents=True)
with tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()),mode='r:gz') as archive:
    assert all(m.isfile() and not m.name.startswith('/') and '..' not in pathlib.PurePosixPath(m.name).parts for m in archive)
    archive.extractall(directory,filter='data')
meta=json.loads((directory/'release-media.json').read_text());old=json.loads((pathlib.Path(meta['base'])/'release.json').read_text())
def run(args,data=None):
    p=subprocess.run(args,input=data,capture_output=True,timeout=120)
    if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[:1000])
    return p.stdout
assert run(['docker','port','tehnet-wordpress','80/tcp']).decode().strip()=='127.0.0.1:18082'
original={}
for name,digest in meta['files'].items():
    assert hashlib.sha256((directory/name).read_bytes()).hexdigest()==digest
    prior=old['file_sha256'].get('content/'+name)
    if prior:
        original[name]=run(['docker','exec','tehnet-wordpress','cat','/var/www/html/wp-content/'+name]);assert hashlib.sha256(original[name]).hexdigest()==prior,'Drift: '+name
    else:assert subprocess.run(['docker','exec','tehnet-wordpress','test','-e','/var/www/html/wp-content/'+name]).returncode!=0,'Unexpected new path: '+name
    if name.endswith('.php'):run(['docker','exec','-i','tehnet-wordpress','php','-l'],(directory/name).read_bytes())
with tarfile.open(directory/'changed-files-before.tar.gz',mode='w:gz') as archive:
    for name,data in original.items():info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o600;archive.addfile(info,io.BytesIO(data))
try:
    for name in meta['files']:
        parent=str(pathlib.PurePosixPath('/var/www/html/wp-content/'+name).parent)
        run(['docker','exec','tehnet-wordpress','mkdir','-p',parent]);run(['docker','cp',str(directory/name),'tehnet-wordpress:/var/www/html/wp-content/'+name]);run(['docker','exec','tehnet-wordpress','chown','www-data:www-data','/var/www/html/wp-content/'+name])
    for name,digest in meta['files'].items():assert hashlib.sha256(run(['docker','exec','tehnet-wordpress','cat','/var/www/html/wp-content/'+name])).hexdigest()==digest
except Exception:
    for name,data in original.items():run(['docker','exec','-i','tehnet-wordpress','sh','-c','cat > /var/www/html/wp-content/'+name],data)
    raise
result={'status':'published','directory':str(directory),'files':meta['files'],'payment_or_inventory_settings_changed':False,'theme_or_homepage_changed':False,'changed_files_backup':str(directory/'changed-files-before.tar.gz')};(directory/'outcome.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''.replace('DIRECTORY',repr('/root/tehnet-releases/store-media-'+digest[:16]))
compile(remote,'remote-store-media','exec')
p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','netauto-main','python3 -c '+shlex.quote(remote)],input=buf.getvalue(),capture_output=True,timeout=300)
if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
result=json.loads(p.stdout);(root/'qa/store-2026-10-15/production-media-release.json').write_text(json.dumps(result,indent=2));print('LIVE_MEDIA_ALLOWLIST_DEPLOYMENT=PASSED')
