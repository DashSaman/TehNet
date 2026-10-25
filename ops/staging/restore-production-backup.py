"""Rehearse a private production backup in fresh local DB/volume; never replace a source."""
from pathlib import Path
import datetime,gzip,hashlib,json,re,secrets,subprocess,tarfile,uuid
root=Path(__file__).resolve().parents[2]
base=root/'ops/staging/.local/production-restore'
def run(args,data=None,timeout=180):
    p=subprocess.run(args,input=data,capture_output=True,timeout=timeout)
    if p.returncode: raise RuntimeError('Command failed: '+args[0]+' '+p.stderr.decode(errors='replace')[:1000])
    return p.stdout
expected={line.split()[1]:line.split()[0] for line in (base/'SHA256SUMS').read_text().splitlines()}
for name in ['wordpress-files.tar.gz','tehnet.sql.gz']:
    assert hashlib.sha256((base/name).read_bytes()).hexdigest()==expected[name], 'Backup transport hash mismatch'
with tarfile.open(base/'wordpress-files.tar.gz') as archive:
    for member in archive:
        assert not member.name.startswith('/') and '..' not in Path(member.name).parts, 'Unsafe archive member'
        assert not member.issym() and not member.islnk(), 'Review links before restore'
suffix=uuid.uuid4().hex[:10]; db='tn_live_restore_'+suffix; user='tn_restore_'+suffix
volume='tehnet-production-restore-'+suffix; container='tehnet-production-restore-'+suffix
password=secrets.token_hex(24); network=json.loads(run(['docker','inspect','tehnet-woo-stage-woo-db-1']))[0]['NetworkSettings']['Networks'];network=next(iter(network))
sql=gzip.decompress((base/'tehnet.sql.gz').read_bytes())
prefix=re.search(rb'CREATE TABLE `([A-Za-z0-9_]+)options`',sql).group(1).decode();assert re.fullmatch(r'[A-Za-z0-9_]+',prefix)
dbbase=['docker','exec','-i','tehnet-woo-stage-woo-db-1','sh','-c','exec mariadb -uroot -p"$MARIADB_ROOT_PASSWORD"']
run(dbbase,('CREATE DATABASE '+db+' CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; CREATE USER \''+user+"'@'%' IDENTIFIED BY '"+password+"'; GRANT ALL ON "+db+".* TO '"+user+"'@'%';").encode())
run(['docker','exec','-i','tehnet-woo-stage-woo-db-1','sh','-c','exec mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" '+db],sql)
run(['docker','volume','create',volume])
image='wordpress:php8.3-apache'
archive_bytes=(base/'wordpress-files.tar.gz').read_bytes()
run(['docker','run','--rm','-i','--network','none','-v',volume+':/restore','--entrypoint','tar',image,'-xzf','-','-C','/restore'],archive_bytes)
run(['docker','run','--rm','-i','--network','none','-v',volume+':/restore:ro','--entrypoint','tar',image,'-dzf','-','-C','/restore'],archive_bytes)
print('PASS: archive hashes, SQL import and all restored file bytes verified',flush=True)
def phpstr(s):return "'"+s.replace('\\','\\\\').replace("'","\\'")+"'"
config='<?php\n'
settings={'DB_NAME':db,'DB_USER':user,'DB_PASSWORD':password,'DB_HOST':'tehnet-woo-stage-woo-db-1','DB_CHARSET':'utf8mb4','DB_COLLATE':'','WP_HOME':'http://localhost:18086','WP_SITEURL':'http://localhost:18086','WP_ENVIRONMENT_TYPE':'staging'}
settings.update({k:secrets.token_hex(32) for k in ['AUTH_KEY','SECURE_AUTH_KEY','LOGGED_IN_KEY','NONCE_KEY','AUTH_SALT','SECURE_AUTH_SALT','LOGGED_IN_SALT','NONCE_SALT']})
for k,v in settings.items():config+='define('+phpstr(k)+','+phpstr(v)+');\n'
config+="if(!defined('DISABLE_WP_CRON')){define('DISABLE_WP_CRON',true);}define('DISALLOW_FILE_MODS',true);define('WP_HTTP_BLOCK_EXTERNAL',true);$table_prefix="+phpstr(prefix)+";if(!defined('ABSPATH')){define('ABSPATH',__DIR__.'/');}require_once ABSPATH.'wp-settings.php';"
run(['docker','run','--rm','-i','--network','none','-v',volume+':/restore','--entrypoint','sh',image,'-c','cat > /restore/wp-config.php'],config.encode())
guard="<?php add_filter('pre_wp_mail',function(){return false;});add_filter('pre_http_request',function(){return new WP_Error('restore_isolated','External HTTP disabled in restore');});"
run(['docker','run','--rm','-i','--network','none','-v',volume+':/restore','--entrypoint','sh',image,'-c','mkdir -p /restore/wp-content/mu-plugins; cat > /restore/wp-content/mu-plugins/tn-restore-isolation.php'],guard.encode())
run(['docker','run','-d','--name',container,'--network',network,'--memory','384m','--cpus','0.5','-p','127.0.0.1:18086:80','-v',volume+':/var/www/html',image])
audit="""<?php define('DISABLE_WP_CRON',true);require '/var/www/html/wp-load.php';global $wpdb;$result=[];foreach(['posts'=>'ID','postmeta'=>'meta_id','users'=>'ID','usermeta'=>'umeta_id','terms'=>'term_id','term_taxonomy'=>'term_taxonomy_id','term_relationships'=>'object_id,term_taxonomy_id','wc_orders'=>'id','wc_orders_meta'=>'id'] as $table=>$key){$rows=$wpdb->get_results('SELECT * FROM '.$wpdb->prefix.$table.' ORDER BY '.$key,ARRAY_A);$result[$table]=['count'=>count($rows),'sha256'=>hash('sha256',json_encode($rows))];}echo json_encode($result);"""
source=json.loads(run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','netauto-main','docker exec -i tehnet-wordpress php'],audit.encode()))
restored=json.loads(run(['docker','exec','-i',container,'php'],audit.encode()))
assert source==restored, 'Production business data differs from restored backup'
probe="<?php require '/var/www/html/wp-load.php';if(home_url()!=='http://localhost:18086'||wp_get_environment_type()!=='staging'){exit(1);} echo json_encode(['local_clone'=>true,'external_http_blocked'=>is_wp_error(wp_remote_get('https://example.com')),'mail_blocked'=>wp_mail('nobody@example.invalid','restore test','no delivery')===false]);"
checks=json.loads(run(['docker','exec','-i',container,'php'],probe.encode()));assert all(checks.values())
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed','scope':'Fresh production backup restored locally into new DB and new volume. No source overwritten.','sql_sha256':expected['tehnet.sql.gz'],'files_sha256':expected['wordpress-files.tar.gz'],'file_archive_compared_before_clone_configuration':True,'business_fingerprints':restored,'isolation':checks,'clone_url':'http://localhost:18086','clone_container':container,'clone_database':db,'clone_volume':volume}
(root/'qa/store-2026-10-15/production-recovery.json').write_text(json.dumps(result,indent=2))
print('PRODUCTION_BACKUP_LOCAL_RESTORE=PASSED; nine business table fingerprints match; external HTTP/mail disabled',flush=True)
