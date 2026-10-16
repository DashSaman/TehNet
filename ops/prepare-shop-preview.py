"""Private isolated native preview; fresh DB and file copy, never source writes.

Uses already-installed image IDs. No image pull, production stop or DB replacement.
Repeated invocation syncs Store source only, preserving the same isolated clone.
"""
from pathlib import Path
import io
import json
import shlex
import subprocess
import tarfile
import argparse

ROOT = Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--resume-empty-preview',action='store_true',help='Adopt only the inspected own empty DB after an interrupted initial bootstrap')
options=parser.parse_args()
files = {p.relative_to(ROOT/'site').as_posix(): p.read_bytes()
         for p in (ROOT/'site/plugins/tehnet-store').rglob('*')
         if p.is_file() and p.suffix in ['.php', '.css', '.js', '.svg', '.json']}
bundle = io.BytesIO()
with tarfile.open(fileobj=bundle, mode='w:gz') as archive:
    for name, data in files.items():
        info = tarfile.TarInfo(name); info.size = len(data)
        archive.addfile(info, io.BytesIO(data))

remote = r'''
import pathlib,subprocess,json,secrets,shutil,re,time,tarfile,io,sys,os,ipaddress,urllib.request
os.umask(0o077)
base=pathlib.Path('/root/tehnet-ux-preview-20261016');state=base/'state.json'
source=pathlib.Path('/var/lib/docker/volumes/tehnet_tehnet-wp-data/_data')
app=base/'wordpress';network='tehnet-ux-preview-20261016';db='tehnet-ux-preview-db';web='tehnet-ux-preview-wordpress'
def run(argv,data=None,timeout=180):
 p=subprocess.run(argv,input=data,capture_output=True,timeout=timeout)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[:1200])
 return p.stdout
def inspect(name):return json.loads(run(['docker','inspect',name]))[0]
assert run(['docker','port','tehnet-wordpress','80/tcp']).decode().strip()=='127.0.0.1:18082'
base.mkdir(exist_ok=True);os.chmod(base,0o700)
if not state.exists():
 assert shutil.disk_usage(base).free>4*1024**3
 images={n:inspect(n)['Image'] for n in ['tehnet-wordpress','tehnet-db']}
 # Never print/copy production credentials to the caller. Dump stays server-local.
 sql=run(['docker','exec','tehnet-db','sh','-c','exec mariadb-dump -uroot -p"$MARIADB_ROOT_PASSWORD" --single-transaction --quick --skip-lock-tables "$MARIADB_DATABASE"'])
 prefix=re.search(rb'CREATE TABLE `([A-Za-z0-9_]+)options`',sql).group(1).decode()
 assert re.fullmatch(r'[A-Za-z0-9_]+',prefix)
 if app.exists():
  assert RESUME_EMPTY,'Inspect incomplete preview; explicit empty-preview resume required'
  config=(app/'wp-config.php').read_text()
  assert "define('DB_HOST','"+db+"')" in config and "define('WP_ENVIRONMENT_TYPE','staging')" in config
  password=re.search(r"define\('DB_PASSWORD','([a-f0-9]{48})'\)",config).group(1)
  obj=inspect(db);assert obj['Image']==images['tehnet-db'] and obj['State']['Running'] and obj['HostConfig']['NetworkMode']==network
  assert 'MARIADB_ROOT_PASSWORD='+password in obj['Config']['Env'] and 'MARIADB_DATABASE=tehnetux' in obj['Config']['Env']
  assert json.loads(run(['docker','network','inspect',network]))[0]['Internal'] is True
  assert web not in run(['docker','ps','-a','--format','{{.Names}}']).decode().splitlines()
  assert 'isolated_preview' in (app/'wp-content/mu-plugins/tehnet-ux-isolation.php').read_text()
 else:
  shutil.copytree(source,app,ignore=shutil.ignore_patterns('cache','upgrade','.git'))
  password=secrets.token_hex(24)
  config="<?php\n"
  def literal(s):return "'"+s.replace('\\','\\\\').replace("'","\\'")+"'"
  settings={'DB_NAME':'tehnetux','DB_USER':'root','DB_PASSWORD':password,'DB_HOST':db,'DB_CHARSET':'utf8mb4','DB_COLLATE':'','WP_HOME':'http://localhost:18085','WP_SITEURL':'http://localhost:18085','WP_ENVIRONMENT_TYPE':'staging'}
  for k in ['AUTH_KEY','SECURE_AUTH_KEY','LOGGED_IN_KEY','NONCE_KEY','AUTH_SALT','SECURE_AUTH_SALT','LOGGED_IN_SALT','NONCE_SALT']:settings[k]=secrets.token_hex(32)
  for k,v in settings.items():config+='define('+literal(k)+','+literal(v)+');\n'
  config+="define('DISABLE_WP_CRON',true);define('DISALLOW_FILE_MODS',true);define('WP_HTTP_BLOCK_EXTERNAL',true);$table_prefix="+literal(prefix)+";if(!defined('ABSPATH')){define('ABSPATH',__DIR__.'/');}require_once ABSPATH.'wp-settings.php';"
  (app/'wp-config.php').write_text(config);os.chmod(app/'wp-config.php',0o644)
  guards=app/'wp-content/mu-plugins/tehnet-ux-isolation.php'
  guards.write_text("<?php add_filter('pre_wp_mail',static fn()=>false);add_filter('pre_http_request',static fn()=>new WP_Error('isolated_preview','External HTTP blocked'));add_filter('woocommerce_available_payment_gateways',static fn()=>[]);add_filter('pre_option_blog_public',static fn()=>0);add_action('send_headers',static function(){header('X-Robots-Tag: noindex, nofollow');});")
  os.chmod(guards,0o644)
  run(['docker','network','create','--internal',network])
  run(['docker','run','-d','--pull=never','--name',db,'--network',network,'--memory','320m','--cpus','0.5','--tmpfs','/var/lib/mysql:rw,nosuid,size=384m','-e','MARIADB_ROOT_PASSWORD='+password,'-e','MARIADB_DATABASE=tehnetux',images['tehnet-db']])
 for _ in range(60):
  ping=subprocess.run(['docker','exec',db,'sh','-c','mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" -N -e "SELECT 1"'],capture_output=True)
  if ping.returncode==0:break
  time.sleep(.5)
 else:raise RuntimeError('Isolated preview DB not ready')
 if app.exists() and RESUME_EMPTY:
  tables=run(['docker','exec',db,'sh','-c',"mariadb -uroot -p\"$MARIADB_ROOT_PASSWORD\" -N -e \"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='tehnetux'\""]).decode().strip()
  assert tables=='0','Partial DB contains data; inspect manually, never overwrite'
 run(['docker','exec','-i',db,'sh','-c','exec mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" tehnetux'],sql)
 run(['docker','run','-d','--pull=never','--name',web,'--network',network,'--memory','448m','--cpus','0.75','-p','127.0.0.1:18085:80','-v',str(app)+':/var/www/html',images['tehnet-wordpress']])
 run(['docker','cp','tehnet-wordpress:/tmp/tn-store-review/wp-cli.phar',str(base/'wp-cli.phar')])
 run(['docker','cp',str(base/'wp-cli.phar'),web+':/tmp/wp-cli.phar'])
 run(['docker','exec',web,'php','/tmp/wp-cli.phar','--allow-root','--path=/var/www/html','search-replace','https://tehnet.ir','http://localhost:18085','--all-tables-with-prefix','--precise','--skip-columns=guid','--quiet'])
 receipt={'status':'prepared','scope':'Fresh private clone; no production writes','directory':str(base),'web_container':web,'db_container':db,'web_id':inspect(web)['Id'],'db_id':inspect(db)['Id'],'network':network,'url':'http://localhost:18085','external_network':False,'cron_mail_http_disabled':True,'database_storage':'ephemeral tmpfs; recreate only after explicit inspection if stopped'}
 state.write_text(json.dumps(receipt,indent=2))
else:
 receipt=json.loads(state.read_text())
 assert inspect(web)['Id']==receipt['web_id'] and inspect(db)['Id']==receipt['db_id'],'Preview identity changed'
 assert inspect(web)['State']['Running'] and inspect(db)['State']['Running'],'Preview stopped; do not reset automatically'
 assert json.loads(run(['docker','network','inspect',network]))[0]['Internal'] is True
# Docker internal bridges deliberately suppress published ports on this host.
# SSH forwards to the private container IP; do not attach an external network.
ip=inspect(web)['NetworkSettings']['Networks'][network]['IPAddress']
assert ipaddress.ip_address(ip).is_private
receipt['forward_target']=ip+':80'
if not receipt.get('permissions_normalized'):
 assert app.resolve().is_relative_to(base.resolve()) and app.resolve()!=source.resolve()
 for p in [app,*app.rglob('*')]:
  assert not p.is_symlink(),'Review clone symlinks before changing ownership'
  os.chown(p,33,33)
 config=app/'wp-config.php';s=config.read_text()
 if "if(!defined('ABSPATH'))" not in s:config.write_text(s.replace("define('ABSPATH',__DIR__.'/');","if(!defined('ABSPATH')){define('ABSPATH',__DIR__.'/');}"))
 receipt['permissions_normalized']=True
with tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()),mode='r:gz') as archive:
 for m in archive:
  assert m.isfile() and m.name.startswith('plugins/tehnet-store/') and '..'not in pathlib.PurePosixPath(m.name).parts
  p=app/'wp-content'/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(archive.extractfile(m).read());os.chmod(p,0o644)
probe=urllib.request.Request('http://'+ip+'/shop/',headers={'Host':'localhost:18085'})
receipt['http_status']=urllib.request.urlopen(probe,timeout=30).status
state.write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt))
'''.replace('RESUME_EMPTY',repr(options.resume_empty_preview))
compile(remote, 'private-shop-preview', 'exec')
result = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', '-o', 'StrictHostKeyChecking=yes',
    'netauto-main', 'python3 -c '+shlex.quote(remote)], input=bundle.getvalue(), capture_output=True, timeout=240)
if result.returncode:
    raise RuntimeError((result.stdout+result.stderr).decode(errors='replace'))
receipt = json.loads(result.stdout)
out = ROOT/'qa/shop-ux-2026-10-16';out.mkdir(exist_ok=True, parents=True)
(out/'staging.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print('ISOLATED_SHOP_PREVIEW_READY; localhost:18085; Store files synced; production unchanged')
