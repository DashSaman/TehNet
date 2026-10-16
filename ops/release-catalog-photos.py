"""Explicit guarded photo migration. prepare is read-only in WP; apply/rollback require mode."""
from pathlib import Path
import argparse,datetime,hashlib,io,json,shlex,subprocess,tarfile
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('mode',choices=['prepare','apply','rollback']);args=p.parse_args()
media=root/'content/media/saieedshabake-2026-10-16';manifest=media/'manifest.json';digest=hashlib.sha256(manifest.read_bytes()).hexdigest()
directory='/root/tehnet-releases/catalog-photos-'+digest[:16]
files={'manifest.json':manifest.read_bytes(),'import.php':(root/'ops/import-catalog-photos.php').read_bytes()}
for x in json.loads(manifest.read_text(encoding='utf-8'))['products']:
    for image in x['images']:
        b=(media/image['file']).read_bytes();assert hashlib.sha256(b).hexdigest()==image['sha256'];files[image['file']]=b
payload=io.BytesIO()
with tarfile.open(fileobj=payload,mode='w:gz') as archive:
    for name,b in files.items():i=tarfile.TarInfo(name);i.size=len(b);i.mode=0o600;archive.addfile(i,io.BytesIO(b))
remote=r'''
import datetime,hashlib,io,json,os,pathlib,subprocess,sys,tarfile
os.umask(0o077);directory=pathlib.Path(DIRECTORY);directory.mkdir(exist_ok=True)
with tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()),mode='r:gz') as archive:
    for m in archive:
        assert m.isfile() and '/' not in m.name and m.name not in ['.','..']
        b=archive.extractfile(m).read();dest=directory/m.name
        if dest.exists():assert dest.read_bytes()==b,'Release drift: '+m.name
        else:dest.write_bytes(b)
assert hashlib.sha256((directory/'manifest.json').read_bytes()).hexdigest()==DIGEST
def run(argv,timeout=180):
    p=subprocess.run(argv,capture_output=True,timeout=timeout)
    if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace')[:2500])
    return p.stdout.decode()
assert run(['docker','port','tehnet-wordpress','80/tcp']).strip()=='127.0.0.1:18082'
cli=['docker','exec','tehnet-wordpress','php','/tmp/tn-store-review/wp-cli.phar','--allow-root','--path=/var/www/html','--user=AmirrezaGol']
audit=r"""$result=['home'=>['front'=>get_option('page_on_front'),'content'=>get_post_field('post_content',(int)get_option('page_on_front')),'theme'=>get_option('stylesheet')],'products'=>[],'orders'=>wc_get_orders(['limit'=>1,'paginate'=>true])->total,'index'=>get_option('blog_public')];foreach(wc_get_products(['limit'=>100,'status'=>['publish','draft','private']])as $p){if(!$p->get_meta('_tn_source_key'))continue;$result['products'][$p->get_sku()]=['id'=>$p->get_id(),'title'=>$p->get_name(),'status'=>$p->get_status(),'price'=>$p->get_price(),'regular'=>$p->get_regular_price(),'stock'=>$p->get_stock_quantity(),'manage'=>$p->get_manage_stock(),'backorders'=>$p->get_backorders(),'approved'=>$p->get_meta('_tn_sale_approved'),'source'=>$p->get_meta('_tn_source_key')];}ksort($result['products']);echo wp_json_encode($result);"""
current=json.loads(run(cli+['eval',audit]));assert len(current['products'])==25
before=directory/'business-before.json'
if before.exists():assert json.loads(before.read_text())==current,'Business state drift since prepare; review first'
else:before.write_text(json.dumps(current,ensure_ascii=False))
run(['docker','cp',str(directory),'tehnet-wordpress:/tmp/'+directory.name])
inside='/tmp/'+directory.name
command=cli+['eval-file',inside+'/import.php',inside+'/manifest.json',DIGEST]
dry=json.loads(run(command+['dry']));result={'mode':MODE,'directory':str(directory),'dry_run':dry,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
if MODE!='prepare':
    run(['systemctl','start','tehnet-store-backup.service'],timeout=180)
    backup=max(pathlib.Path('/root/tehnet-backups').glob('*-store-review'),key=lambda x:x.stat().st_mtime)
    assert (datetime.datetime.now().timestamp()-backup.stat().st_mtime)<600
    verify=subprocess.run(['sha256sum','-c','SHA256SUMS'],cwd=backup,capture_output=True);assert verify.returncode==0,'Backup checksum failed'
    result['backup']=str(backup);result['backup_checksums_verified']=True
    result['migration']=json.loads(run(command+[MODE],timeout=480))
    after=json.loads(run(cli+['eval',audit]));assert current==after,'Unexpected business state mutation'
    result['business_fields_unchanged']=True
    if MODE=='apply':
        result['repeat']=json.loads(run(command+['apply'],timeout=480));assert result['repeat']['products_changed']==0 and result['repeat']['skipped']==25
        check=r"""$r=[];foreach(wc_get_products(['limit'=>100,'status'=>['publish','draft','private']])as $p){if(!$p->get_meta('_tn_source_key'))continue;$ids=array_merge([$p->get_image_id()],$p->get_gallery_image_ids());$a=[];foreach($ids as $id){$f=get_attached_file($id);$a[]=['attachment_id'=>$id,'sha256'=>hash_file('sha256',$f),'original_sha256'=>get_post_meta($id,'_tn_original_sha256',true),'url'=>wp_get_attachment_url($id)];}$r[]=['sku'=>$p->get_sku(),'product_id'=>$p->get_id(),'url'=>get_permalink($p->get_id()),'photos'=>$a];}echo wp_json_encode($r);"""
        result['products']=json.loads(run(cli+['eval',check]));assert len(result['products'])==25
        assert sum(len(x['photos'])for x in result['products'])==30
        assert all(i['sha256']==i['original_sha256'] for x in result['products']for i in x['photos'])
        result['original_media_bytes_unchanged']=True
(directory/(MODE+'-outcome.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result))
'''.replace('DIRECTORY',repr(directory)).replace('DIGEST',repr(digest)).replace('MODE',repr(args.mode))
compile(remote,'remote-photo-release','exec')
proc=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','netauto-main','python3 -c '+shlex.quote(remote)],input=payload.getvalue(),capture_output=True,timeout=700)
if proc.returncode:raise RuntimeError((proc.stdout+proc.stderr).decode(errors='replace'))
result=json.loads(proc.stdout);out=root/'qa/store-2026-10-16';out.mkdir(exist_ok=True);(out/('photos-'+args.mode+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items()if k!='products'},ensure_ascii=True,indent=2))
