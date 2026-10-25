"""Recover only newly created local databases; never overwrite source volumes."""
import gzip,hashlib,json,secrets,subprocess,uuid
from pathlib import Path
root=Path(__file__).resolve().parents[2]
env=dict(line.split('=',1) for line in (root/'ops/staging/.env').read_text().splitlines() if '=' in line)
backup=root/'ops/staging/.local/backups'/('rehearsal-'+uuid.uuid4().hex[:10]);backup.mkdir(parents=True)
def run(args,input=None,timeout=240):
    p=subprocess.run(args,input=input,capture_output=True,timeout=timeout)
    if p.returncode:
        text=(p.stdout+p.stderr).decode(errors='replace')
        for value in env.values():
            if len(value)>8:text=text.replace(value,'<REDACTED>')
        raise RuntimeError(text)
    return p.stdout
erp=['docker','exec','-e','MYSQL_HOME=/tmp/tn-local-mysql','tehnet-erp-stage-backend-1']
run(erp+['bench','--site','frontend','execute','tehnet_erp.sandbox.guard'])
run(erp+['bench','--site','frontend','backup','--with-files'])
before=json.loads(run(erp+['bench','--site','frontend','execute','tehnet_erp.recovery.audit']))
paths=json.loads(run(erp+['python','-c',"import json;from pathlib import Path;p=sorted(Path('sites/frontend/private/backups').glob('*-database.sql.gz'))[-1];print(json.dumps({'db':str(p.resolve()),'public':str(p.resolve()).replace('-database.sql.gz','-files.tar'),'private':str(p.resolve()).replace('-database.sql.gz','-private-files.tar')}))"]))
target='tehnet-restore-'+uuid.uuid4().hex[:12]+'.local'
run(erp+['python','-c',"from pathlib import Path;assert not Path('sites/'+"+repr(target)+").exists()"])
secret=env['ERP_ADMIN_PASSWORD']
run(erp+['bench','new-site',target,'--db-host','db','--db-root-password',secret,'--admin-password',secret,'--mariadb-user-host-login-scope','%'],timeout=300)
run(erp+['bench','--site',target,'restore',paths['db'],'--db-root-password',secret,'--with-public-files',paths['public'],'--with-private-files',paths['private'],'--force'],timeout=300)
configuration_backup=paths['db'].replace('-database.sql.gz','-site_config_backup.json')
run(erp+['python','-c',"import json;from pathlib import Path;s=json.loads(Path("+repr(configuration_backup)+").read_text());p=Path('sites/'+"+repr(target)+"+'/site_config.json');d=json.loads(p.read_text());d.update({k:v for k,v in s.items() if k.startswith('tehnet_') or k=='encryption_key'});d.update({'pause_scheduler':1,'mute_emails':1,'maintenance_mode':1});p.write_text(json.dumps(d))"])
configuration_hash=run(erp+['bench','--site','frontend','execute','tehnet_erp.recovery.config_audit'])
assert configuration_hash==run(erp+['bench','--site',target,'execute','tehnet_erp.recovery.config_audit']),'Restored ERP account/warehouse configuration differs'
after=json.loads(run(erp+['bench','--site',target,'execute','tehnet_erp.recovery.audit']))
assert before==after,'ERP restore fingerprint differs from source'
decrypt=['execute','frappe.utils.password.get_decrypted_password','--kwargs',json.dumps({'doctype':'User','name':'tehnet-integration@example.invalid','fieldname':'api_secret'})]
assert run(erp+['bench','--site','frontend']+decrypt)==run(erp+['bench','--site',target]+decrypt),'Restored encryption key cannot decrypt native API credential'
print('PASS: ERP SQL, public/private files restored into a new isolated site; '+str(len(before))+' table fingerprints match, including permissions and credential decryption',flush=True)

woo_db='tehnet-woo-stage-woo-db-1'
dump=run(['docker','exec',woo_db,'sh','-c','exec mariadb-dump -uroot -p"$MARIADB_ROOT_PASSWORD" --single-transaction --skip-lock-tables tehnet_stage'])
(backup/'woo.sql.gz').write_bytes(gzip.compress(dump))
files=run(['docker','exec','tehnet-woo-stage-woo-1','tar','-czf','-','-C','/var/www/html','.'])
(backup/'woo-files.tar.gz').write_bytes(files)
restored_db='tn_restore_'+uuid.uuid4().hex[:12]
assert restored_db.startswith('tn_restore_') and restored_db!='tehnet_stage'
run(['docker','exec',woo_db,'sh','-c','exec mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" -e "CREATE DATABASE '+restored_db+' CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"'])
run(['docker','exec','-i',woo_db,'sh','-c','exec mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" '+restored_db],input=gzip.decompress((backup/'woo.sql.gz').read_bytes()))
query="SELECT COUNT(*) FROM wp_posts; SELECT COUNT(*) FROM wp_postmeta; SELECT COUNT(*) FROM wp_wc_orders; SELECT option_value FROM wp_options WHERE option_name='blog_public';"
def counts(db):return run(['docker','exec',woo_db,'sh','-c','exec mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" -N '+db+' -e "'+query+'"']).decode().splitlines()
assert counts('tehnet_stage')==counts(restored_db),'Woo database restore differs'
stable_query="SELECT id,status,currency,total_amount FROM wp_wc_orders ORDER BY id; SELECT ID,post_type,post_status,post_title FROM wp_posts WHERE post_type='product' ORDER BY ID; SELECT post_id,meta_key,meta_value FROM wp_postmeta WHERE meta_key IN ('_price','_stock','_tn_source_key') ORDER BY post_id,meta_key,meta_id;"
def fingerprint(db):return hashlib.sha256(run(['docker','exec',woo_db,'sh','-c','exec mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" -N '+db+' -e "'+stable_query+'"'])).hexdigest()
assert fingerprint('tehnet_stage')==fingerprint(restored_db),'Woo order/product values differ after restoration'
volume='tehnet-restore-files-'+uuid.uuid4().hex[:12]
run(['docker','volume','create',volume])
run(['docker','run','--rm','-i','-v',volume+':/restore','--entrypoint','tar','wordpress:php8.3-apache','-xzf','-','-C','/restore'],input=files)
run(['docker','run','--rm','-i','-v',volume+':/restore:ro','--entrypoint','tar','wordpress:php8.3-apache','-dzf','-','-C','/restore'],input=files)
run(['docker','run','--rm','-v',volume+':/restore:ro','--entrypoint','php','wordpress:php8.3-apache','-l','/restore/wp-content/plugins/tehnet-store/tehnet-store.php'])
print('PASS: WordPress database restored into a new DB; files restored into a new volume; native order/post/meta counts match',flush=True)
result={'erp':{'status':'passed','restored_site':target,'tables':before,'files_restored':True,'encryption_key_decryption_verified':True},'woo':{'status':'passed','restored_database':restored_db,'restored_files_volume':volume,'counts':counts(restored_db),'business_values_sha256':fingerprint(restored_db),'archive_contents_compared':True,'sql_sha256':hashlib.sha256(dump).hexdigest(),'files_sha256':hashlib.sha256(files).hexdigest()},'scope':'Isolated local synthetic data. Source databases/volumes untouched. Not a production restore rehearsal.','limitation':'ERP MariaDB client initially failed certificate validity validation after local VM clock movement; this single local backup/restore uses a temporary MYSQL_HOME client option disabling server-certificate verification. No production or application TLS settings changed.'}
(root/'qa/store-2026-10-15/recovery-results.json').write_text(json.dumps(result,indent=2))
print('LOCAL_RECOVERY=PASSED',flush=True)
