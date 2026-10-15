"""Explicit TehNet review release. No live ERP, payment, proxy or container topology changes."""
import datetime,hashlib,io,json,os,re,subprocess,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
recovery=json.loads((root/'qa/store-2026-10-15/production-recovery.json').read_text())
assert recovery['status']=='passed' and all(recovery['isolation'].values())
backup='/root/tehnet-backups/20261015-184219-store-review'
files={}
for p in (root/'site/plugins/tehnet-store').rglob('*'):
    if p.is_file():files['content/plugins/tehnet-store/'+p.relative_to(root/'site/plugins/tehnet-store').as_posix()]=p.read_bytes()
old={}
for name in ['class-inquiries.php','class-quotes.php','class-commerce.php']:
    old[name]=hashlib.sha256((root.parent/'live-core'/name).read_bytes()).hexdigest()
    files['content/plugins/tehnet-core/includes/'+name]=(root/'site/plugins/tehnet-core/includes'/name).read_bytes()
files['catalog.json']=(root/'content/catalog/saieedshabake-2026-10-15.json').read_bytes()
files['wp-cli.phar']=(root/'ops/staging/.local/wp-cli.phar').read_bytes()
metadata={'manifest_sha256':hashlib.sha256(files['catalog.json']).hexdigest(),'old_core_sha256':old,'backup':backup,'backup_sql_sha256':recovery['sql_sha256'],'backup_files_sha256':recovery['files_sha256'],'file_sha256':{k:hashlib.sha256(v).hexdigest() for k,v in files.items()}}
files['release.json']=json.dumps(metadata).encode()
release_hash=hashlib.sha256(files['release.json']).hexdigest()
remote_dir='/root/tehnet-releases/store-review-'+release_hash[:16]
stream=io.BytesIO()
with tarfile.open(fileobj=stream,mode='w:gz') as archive:
    for name,data in files.items():
        member=tarfile.TarInfo(name);member.size=len(data);member.mode=0o600;archive.addfile(member,io.BytesIO(data))
remote=r'''
import subprocess,sys,tarfile,io,json,hashlib,pathlib,gzip,os
os.umask(0o077)
directory=pathlib.Path(REMOTE_DIR)
assert not directory.exists(),'Release already exists; inspect saved outcome before retrying'
directory.mkdir(parents=True)
with tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()),mode='r:gz') as archive:
    for member in archive:
        assert member.isfile() and not member.name.startswith('/') and '..' not in pathlib.PurePosixPath(member.name).parts
    archive.extractall(directory,filter='data')
meta=json.loads((directory/'release.json').read_text());backup=pathlib.Path(meta['backup'])
for name,digest in meta['file_sha256'].items():assert hashlib.sha256((directory/name).read_bytes()).hexdigest()==digest
for name,key in [('wordpress-files.tar.gz','backup_files_sha256'),('tehnet.sql.gz','backup_sql_sha256')]:assert hashlib.sha256((backup/name).read_bytes()).hexdigest()==meta[key]
def run(args,data=None):
    p=subprocess.run(args,input=data,capture_output=True,timeout=180)
    if p.returncode:raise RuntimeError('Release command rejected: '+args[0]+' '+p.stderr.decode(errors='replace')[:800])
    return p.stdout
assert run(['docker','port','tehnet-wordpress','80/tcp']).decode().strip()=='127.0.0.1:18082'
def unrelated():
    names=[n for n in run(['docker','ps','--format','{{.Names}}']).decode().splitlines() if not n.startswith('tehnet-')]
    objects=json.loads(run(['docker','inspect',*sorted(names)]));return [{'name':x['Name'],'id':x['Id'],'image':x['Image'],'started_at':x['State']['StartedAt'],'ports':x['HostConfig']['PortBindings']} for x in objects]
other_before=unrelated();assert other_before==json.loads((backup/'unrelated-runtime.json').read_text()),'Unrelated runtime changed since backup; review before release'
for name,digest in meta['old_core_sha256'].items():assert hashlib.sha256(run(['docker','exec','tehnet-wordpress','cat','/var/www/html/wp-content/plugins/tehnet-core/includes/'+name])).hexdigest()==digest,'Core drift'
for source in (directory/'content').rglob('*.php'):run(['docker','exec','-i','tehnet-wordpress','php','-l'],source.read_bytes())
run(['docker','cp',str(directory),'tehnet-wordpress:/tmp/tn-store-review'])
cli=['docker','exec','tehnet-wordpress','php','/tmp/tn-store-review/wp-cli.phar','--allow-root','--path=/var/www/html','--user=AmirrezaGol']
def evaluate(code):return json.loads(run(cli+['eval',code]))
before=evaluate("if(home_url()!=='https://tehnet.ir'||wp_get_environment_type()!=='production'){throw new RuntimeException('Wrong site');} global $wpdb;echo json_encode(['posts_max'=>(int)$wpdb->get_var('SELECT MAX(ID) FROM '.$wpdb->posts),'posts_hash'=>hash('sha256',json_encode($wpdb->get_results('SELECT * FROM '.$wpdb->posts.' ORDER BY ID',ARRAY_A))),'orders'=>(int)$wpdb->get_var('SELECT COUNT(*) FROM '.$wpdb->prefix.'wc_orders'),'products'=>(int)$wpdb->get_var(\"SELECT COUNT(*) FROM {$wpdb->posts} WHERE post_type='product'\"),'active'=>get_option('active_plugins')]);")
assert before['products']==0 and before['orders']==0,'Business state changed; stop for reconciliation'
assert 'tehnet-store/tehnet-store.php' not in before['active']
activated=False
try:
    run(['docker','exec','tehnet-wordpress','sh','-c','test ! -e /var/www/html/wp-content/plugins/tehnet-store && cp -a /tmp/tn-store-review/content/plugins/tehnet-store /var/www/html/wp-content/plugins/tehnet-store && chown -R www-data:www-data /var/www/html/wp-content/plugins/tehnet-store'])
    for name in meta['old_core_sha256']:run(['docker','exec','tehnet-wordpress','cp','/tmp/tn-store-review/content/plugins/tehnet-core/includes/'+name,'/var/www/html/wp-content/plugins/tehnet-core/includes/'+name])
    run(cli+['plugin','activate','tehnet-store']);activated=True
    plan=json.loads(run(cli+['tehnet','catalog','release','/tmp/tn-store-review/catalog.json','--sha256='+meta['manifest_sha256']]))
    assert plan['dry_run'] and plan['would_create']==25
    applied=json.loads(run(cli+['tehnet','catalog','release','/tmp/tn-store-review/catalog.json','--sha256='+meta['manifest_sha256'],'--apply']))
    assert len(applied['created'])==25
    repeat=json.loads(run(cli+['tehnet','catalog','release','/tmp/tn-store-review/catalog.json','--sha256='+meta['manifest_sha256'],'--apply']))
    assert not repeat['created'] and len(repeat['skipped'])==25
    pages=evaluate("WC_Install::create_pages();$r=[];foreach(['shop','cart','checkout','myaccount'] as $key){$id=wc_get_page_id($key);if($id<1){throw new RuntimeException('Native page missing');}$r[$key]=['id'=>$id,'url'=>get_permalink($id)];}echo json_encode($r);")
    after=evaluate("global $wpdb;$products=wc_get_products(['limit'=>-1,'status'=>['draft','publish','private']]);$safe=[];foreach($products as $p){$safe[]=['id'=>$p->get_id(),'source_id'=>$p->get_meta('_tn_source_id'),'draft'=>$p->get_status()==='draft','blank_price'=>$p->get_price()==='','stock_zero'=>(string)$p->get_stock_quantity()==='0','no_backorders'=>$p->get_backorders()==='no','can_buy'=>$p->is_purchasable()];}$g=[];foreach(WC()->payment_gateways()->payment_gateways() as $key=>$gateway){$g[$key]=$gateway->enabled;}echo json_encode(['products'=>$safe,'orders'=>(int)$wpdb->get_var('SELECT COUNT(*) FROM '.$wpdb->prefix.'wc_orders'),'blog_public'=>get_option('blog_public'),'erp_ready'=>(new TehNet_Store_ERP())->ready(),'gateways'=>$g,'original_posts_hash'=>hash('sha256',json_encode($wpdb->get_results('SELECT * FROM '.$wpdb->posts.' WHERE ID<=__MAX__ ORDER BY ID',ARRAY_A)))]);".replace('__MAX__',str(before['posts_max'])))
    assert len(after['products'])==25 and all(p['draft'] and p['blank_price'] and p['stock_zero'] and p['no_backorders'] and not p['can_buy'] for p in after['products'])
    assert after['orders']==0 and str(after['blog_public'])=='0' and not after['erp_ready'] and all(v=='no' for v in after['gateways'].values())
    assert before['posts_hash']==after['original_posts_hash'],'Original content changed'
    assert unrelated()==other_before,'Unrelated runtime changed'
    result={'status':'deployed-review-only','directory':str(directory),'backup':str(backup),'manifest_sha256':meta['manifest_sha256'],'run_id':applied['run_id'],'repeat_import_skipped':len(repeat['skipped']),'pages':pages,'audit':after,'original_content_unchanged':True,'unrelated_runtime_unchanged':True,'port_unchanged':True}
    (directory/'outcome.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
except Exception:
    if activated:run(cli+['plugin','deactivate','tehnet-store'])
    with tarfile.open(backup/'wordpress-files.tar.gz') as archive:
        for name in meta['old_core_sha256']:
            data=archive.extractfile('./wp-content/plugins/tehnet-core/includes/'+name).read()
            run(['docker','exec','-i','tehnet-wordpress','sh','-c','cat > /var/www/html/wp-content/plugins/tehnet-core/includes/'+name],data)
    (directory/'FAILED.txt').write_text('Store deactivated and Core allowlist restored; any newly created drafts/pages/audit retained. Reconcile before retry.')
    raise
'''.replace('REMOTE_DIR',repr(remote_dir))
compile(remote,'remote-review-release','exec')
if os.environ.get('TEHNET_RELEASE_VALIDATE_ONLY')=='1':
    print('RELEASE_PACKAGE_VALIDATED='+release_hash);raise SystemExit(0)
process=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','netauto-main','python3 -c '+__import__('shlex').quote(remote)],input=stream.getvalue(),capture_output=True,timeout=600)
if process.returncode:raise RuntimeError((process.stdout+process.stderr).decode(errors='replace'))
result=json.loads(process.stdout);result['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();result['release_sha256']=release_hash
(root/'qa/store-2026-10-15/production-release.json').write_text(json.dumps(result,indent=2))
print('LIVE_REVIEW_DEPLOYMENT=PASSED; 25 private drafts; all payments off; original content and unrelated services unchanged')
