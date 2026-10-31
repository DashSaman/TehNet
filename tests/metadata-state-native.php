<?php
/** Independently isolated staging only; no customer/synthetic DB rows are written. */
if (wp_get_environment_type()!=='staging' || home_url('/')!=='http://localhost:18085/' || !WP_HTTP_BLOCK_EXTERNAL || !DISABLE_WP_CRON) throw new RuntimeException('Owned isolated native staging required');
global $tnMetadataDirectory,$tnMetadataManifest,$tnMetadataChecker,$tnMetadataChecks;
$tnMetadataDirectory=getenv('TN_TEST_DIRECTORY');$tnMetadataManifest=json_decode(file_get_contents(getenv('TN_TEST_MANIFEST')),true,512,JSON_THROW_ON_ERROR);$tnMetadataChecker=getenv('TN_TEST_MIGRATION');$tnMetadataChecks=0;
function metadata_expect(bool $value,string $label):void {global $tnMetadataChecks;if (!$value) throw new RuntimeException('FAIL: '.$label);++$tnMetadataChecks;echo 'PASS: '.$label."\n";}
function metadata_refuse(callable $action,string $label):void {try {$action();} catch (Throwable $error) {metadata_expect(true,$label);return;}throw new RuntimeException('FAIL: did not refuse '.$label);}
function metadata_state():string {global $wpdb;$rows=[];foreach (['posts','postmeta','users','usermeta'] as $name) {$key=$name==='postmeta'?'meta_id':($name==='usermeta'?'umeta_id':'ID');$rows[$name]=$wpdb->get_results("SELECT * FROM {$wpdb->$name} ORDER BY $key",ARRAY_A);}return hash('sha256',serialize($rows));}
function metadata_attempt(string $name,?array $manifest=null):string {
    global $tnMetadataDirectory,$tnMetadataManifest;
    if (!is_string($tnMetadataDirectory) || !str_starts_with($tnMetadataDirectory,'/tmp/tn-editorial-native-') || basename($tnMetadataDirectory)!=='evidence') throw new RuntimeException('Owned fixture root required');
    $root=$tnMetadataDirectory.'/'.$name;if (!mkdir($root,0700) || !mkdir($root.'/journal',0700)) throw new RuntimeException('New owned attempt required');
    file_put_contents($root.'/manifest.json',json_encode($manifest??$tnMetadataManifest));return $root;
}
function metadata_invoke(string $root,string $mode='check',?string $digest=null):array {
    global $tnMetadataChecker;
    foreach (['TN_GROWTH_MANIFEST'=>$root.'/manifest.json','TN_GROWTH_DIGEST'=>$digest??hash_file('sha256',$root.'/manifest.json'),'TN_GROWTH_JOURNAL_DIR'=>$root.'/journal','TN_GROWTH_MODE'=>$mode] as $key=>$value) putenv($key.'='.$value);
    ob_start();try {include $tnMetadataChecker;return json_decode(ob_get_contents(),true,512,JSON_THROW_ON_ERROR);} finally {ob_end_clean();}
}
$before=metadata_state();$root=metadata_attempt('success');
$ready=metadata_invoke($root);metadata_expect($ready['status']==='READY' && $ready['database_rows_written']===0,'Native preflight ready without DB writes');
metadata_expect(!is_file($root.'/journal/journal.json') && metadata_state()===$before,'Preflight creates no applied journal or DB records');
$applied=metadata_invoke($root,'apply');metadata_expect($applied['status']==='APPLIED' && $applied['protected_digest']===$ready['protected_digest'],'Applied private journal retains baseline data digest');
metadata_expect(metadata_invoke($root,'apply')['database_rows_written']===0 && metadata_state()===$before,'Repeated apply never writes database rows');
metadata_expect(metadata_invoke($root)['status']==='APPLIED','Repeated check recognizes applied journal');
$original=file_get_contents($root.'/journal/journal.json');$bad=json_decode($original,true);$bad['protected_digest']=str_repeat('0',64);file_put_contents($root.'/journal/journal.json',json_encode($bad));
try {metadata_refuse(fn()=>metadata_invoke($root),'Protected-digest drift fails closed');} finally {file_put_contents($root.'/journal/journal.json',$original);}
metadata_expect(metadata_invoke($root,'rollback')['status']==='ROLLED_BACK' && metadata_state()===$before,'Rollback journal requires no data restoration');
metadata_expect(metadata_invoke($root,'rollback')['status']==='ROLLED_BACK','Rollback repeat is safe');
metadata_refuse(fn()=>metadata_invoke($root,'apply'),'Rolled journal cannot be reused');
metadata_refuse(fn()=>metadata_invoke(metadata_attempt('no-journal'),'rollback'),'No-journal rollback refused');
metadata_refuse(fn()=>metadata_invoke(metadata_attempt('bad-digest'),'check',str_repeat('0',64)),'Manifest digest mismatch refused');
$bad=$tnMetadataManifest;$bad['runtime_file']='themes/tehnet/header.php';metadata_refuse(fn()=>metadata_invoke(metadata_attempt('other-file',$bad)),'Another runtime file refused');
$bad=$tnMetadataManifest;$bad['database_changes_allowed']=true;metadata_refuse(fn()=>metadata_invoke(metadata_attempt('db-write',$bad)),'Database-write scope refused');
metadata_refuse(fn()=>metadata_invoke(metadata_attempt('mode'),'unknown'),'Unknown mode refused');
$wide=metadata_attempt('permissions');chmod($wide.'/journal',0755);try {metadata_refuse(fn()=>metadata_invoke($wide),'Public-readable journal refused');} finally {chmod($wide.'/journal',0700);}
metadata_expect(metadata_state()===$before,'All original posts metadata users and user metadata retained');
echo 'METADATA_STATE=PASS checks='.$tnMetadataChecks."\n";
