<?php
/** Native isolated WordPress integration only; never run on production. */
if (!defined('WP_CLI') || !WP_CLI || wp_get_environment_type() !== 'staging' || home_url('/') !== 'http://localhost:18085/' || !current_user_can('manage_options')) {
    throw new RuntimeException('Verified isolated native preview required');
}
if (apply_filters('pre_wp_mail', null, []) !== false || !is_wp_error(apply_filters('pre_http_request', false, [], 'https://example.invalid')) || apply_filters('woocommerce_available_payment_gateways', ['probe'=>new stdClass]) !== [] || !DISABLE_WP_CRON || !WP_HTTP_BLOCK_EXTERNAL) {
    throw new RuntimeException('Preview isolation required');
}
define('TN_GROWTH_LIBRARY_ONLY', true);
require __DIR__.'/migrate-growth-content.php';

global $wpdb;
$checks=0; $owned=[]; $releaseDigests=[]; $run='tnqa-growth-'.bin2hex(random_bytes(6));$case=getenv('TN_GROWTH_TEST_CASE')?:'all';
$check=static function(bool $ok, string $label) use (&$checks):void { $checks++; if (!$ok) throw new RuntimeException('FAIL '.$label); };
$reject=static function(callable $call, string $label) use ($check):void { $failed=false; try {$call();} catch (RuntimeException $e) {$failed=true;} $check($failed,$label); };
$fingerprint=static function() use ($wpdb):string {
    return hash('sha256',serialize([$wpdb->get_results("SELECT * FROM {$wpdb->posts} ORDER BY ID",ARRAY_A),$wpdb->get_results("SELECT * FROM {$wpdb->postmeta} ORDER BY meta_id",ARRAY_A)]));
};
$before=$fingerprint();
$manifest=json_decode(file_get_contents(__DIR__.'/manifest.json'),true,512,JSON_THROW_ON_ERROR);
$base='<!-- wp:paragraph --><p>Preserved isolated QA hub.</p><!-- /wp:paragraph -->';
$make=static function(array $fields) use (&$owned,$run):int {
    $id=wp_insert_post(wp_slash(array_merge(['post_type'=>'page','post_status'=>'publish','post_title'=>$run,'meta_input'=>['_tn_growth_fixture'=>$run]],$fields)),true);
    if(is_wp_error($id))throw new RuntimeException('Fixture creation failed');$owned[]=$id;return $id;
};
$saveManifest=static function(array $m,string $name):array { $dir=__DIR__.'/'.$name;if(!mkdir($dir,0700))throw new RuntimeException('Private test journal directory');$path=$dir.'/manifest.json';file_put_contents($path,wp_json_encode($m,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES));chmod($path,0600);return [$path,hash_file('sha256',$path),$dir]; };
try {
    foreach($manifest['updates']as$i=>&$hub){$id=$make(['post_name'=>$run.'-hub-'.$i,'post_content'=>$base]);$hub['id']=$id;$hub['expected_content_sha256']=hash('sha256',$base);$manifest['pages'][$i]['parent_id']=$id;}unset($hub);
    $revisionLimit=static fn()=>2;$priorRevisions=[];
    if($case!=='race'){
        add_filter('wp_revisions_to_keep',$revisionLimit,10);
        foreach($manifest['updates']as$hub){for($n=0;$n<3;$n++)wp_update_post(wp_slash(['ID'=>$hub['id'],'post_content'=>$base.'<p>QA revision '.$n.'</p>']),true);wp_update_post(wp_slash(['ID'=>$hub['id'],'post_content'=>$base]),true);$priorRevisions[$hub['id']]=array_keys(wp_get_post_revisions($hub['id']));$check(count($priorRevisions[$hub['id']])===2,'fixture reached revision retention limit');}
    }
    [$path,$digest,$directory]=$saveManifest($manifest,'happy');
    $releaseDigests[]=$digest;
    $migration=new TehNet_Growth_Content_Migration($path,$digest,$directory);
    $pre=$migration->run('check');$check($pre['pages_pending']===2&&$pre['hubs_pending']===2,'preflight identifies only fixture work');
    $a=$migration->run('apply');$created=array_values($a['page_ids']);$owned=array_merge($owned,$created);
    $check($a['pages_created']===2&&$a['hubs_updated']===2,'apply creates two pages and appends two hubs');
    $check($a['protected_state_unchanged'],'protected data unchanged after apply');
    foreach($priorRevisions as$id=>$revisions)$check(array_diff($revisions,array_keys(wp_get_post_revisions($id)))===[],'all preexisting limited revisions retained');
    foreach($manifest['pages']as$row){$id=$a['page_ids'][$row['key']];$p=get_post($id);$check($p->post_content===$row['content']&&$p->post_title===$row['title']&&$p->post_excerpt===$row['excerpt'],'Persian quotes and content stored exactly');$check((int)$p->post_parent===$row['parent_id']&&$p->post_name===$row['slug'],'IDs resolved under current fixture parent');}
    $repeat=$migration->run('apply');$check($repeat['pages_created']===0&&$repeat['hubs_updated']===0,'repeat apply is no-op');
    $check($migration->run('check')['pages_pending']===0,'applied check is no-op');
    $id=$created[0];$original=get_post($id)->post_content;
    $wpdb->update($wpdb->posts,['post_content'=>$original.' ownership-drift'],['ID'=>$id]);clean_post_cache($id);
    $reject(fn()=>$migration->run('rollback'),'rollback refuses another editor content drift');
    $reject(fn()=>$migration->run('apply'),'repeat apply refuses drift');
    $wpdb->update($wpdb->posts,['post_content'=>$original],['ID'=>$id]);clean_post_cache($id);
    $rolled=$migration->run('rollback');$check($rolled['pages_drafted']===2&&$rolled['hubs_restored']===2,'rollback drafts owned pages and restores hubs');
    foreach($manifest['updates']as$hub)$check(get_post($hub['id'])->post_content===$base,'hub original content restored');
    foreach($created as$id)$check(get_post_status($id)==='draft','owned new page unpublished on rollback');
    $again=$migration->run('rollback');$check($again['pages_drafted']===0&&$again['hubs_restored']===0,'repeat rollback is no-op');
    $reject(fn()=>$migration->run('apply'),'rolled-back journal cannot silently reapply');
    $reject(fn()=>new TehNet_Growth_Content_Migration($path,str_repeat('0',64),$directory),'manifest checksum mismatch rejected');
    $reject(fn()=>$migration->run('unknown'),'unknown operation rejected');
    $wpdb->query('START TRANSACTION');try{$reject(fn()=>$migration->run('check'),'caller-owned transaction is never implicitly committed');}finally{$wpdb->query('ROLLBACK');}

    // A conflicting existing page must be preserved, never adopted by its slug.
    $conflict=$manifest;$conflict['pages'][0]['slug']='existing-owned-by-others';
    $conflictId=$make(['post_name'=>'existing-owned-by-others','post_parent'=>$conflict['pages'][0]['parent_id'],'post_content'=>$base]);
    [$cp,$cd,$cj]=$saveManifest($conflict,'conflict');$cm=new TehNet_Growth_Content_Migration($cp,$cd,$cj);
    $reject(fn()=>$cm->run('apply'),'existing unrelated path rejected');
    $check(get_post($conflictId)->post_content===$base,'conflicting page retained');

    // Error after a first mutation must roll back the transaction, including revisions.
    $failure=$manifest;foreach($failure['pages']as&$row)$row['slug'].='-failure';unset($row);
    [$fp,$fd,$fj]=$saveManifest($failure,'failure');$fm=new TehNet_Growth_Content_Migration($fp,$fd,$fj);
    $preFailure=$fingerprint();$throw=static function($id,$post):void {if($post->post_type==='page'&&str_ends_with($post->post_name,'-failure'))throw new RuntimeException('Synthetic bounded hook failure');};
    add_action('save_post_page',$throw,100,2);
    try {$reject(fn()=>$fm->run('apply'),'mid-apply exception rejected');}finally{remove_action('save_post_page',$throw,100);}
    $check($preFailure===$fingerprint(),'transaction failure preserves all original post/meta rows');
    $check(json_decode(file_get_contents($fj.'/journal.json'),true)['status']==='FAILED','failed journal records exact lifecycle');
    $reject(fn()=>$fm->run('apply'),'failed attempt requires explicit reconciliation');
    $check((string)get_option('blog_public')==='0','noindex retained');

    // Existing WordPress editors do not participate in the migration advisory lock.
    // A second connection must be blocked on both the row and its metadata range.
    $locked=$manifest;foreach($locked['updates']as$i=>&$hub){$id=$make(['post_name'=>$run.'-locked-hub-'.$i,'post_content'=>$base]);$hub['id']=$id;$locked['pages'][$i]['parent_id']=$id;}unset($hub);
    [$lp,$ld,$lj]=$saveManifest($locked,'locked');$releaseDigests[]=$ld;$lm=new TehNet_Growth_Content_Migration($lp,$ld,$lj);
    $second=new wpdb(DB_USER,DB_PASSWORD,DB_NAME,DB_HOST);$second->suppress_errors(true);$second->query('SET SESSION innodb_lock_wait_timeout=1');$lockId=$locked['updates'][0]['id'];$armed=true;$rowBlocked=false;$metaBlocked=false;
    $lockHook=static function($sql)use($second,$lockId,&$armed,&$rowBlocked,&$metaBlocked){global $wpdb;if($armed&&str_starts_with($sql,'UPDATE `'.$wpdb->posts.'`')&&str_contains($sql,'`post_content`')){$armed=false;$rowBlocked=$second->update($wpdb->posts,['post_content'=>'Concurrent locked write'],['ID'=>$lockId])===false&&str_contains($second->last_error,'Lock wait timeout');$metaBlocked=$second->insert($wpdb->postmeta,['post_id'=>$lockId,'meta_key'=>'_tn_growth_concurrent','meta_value'=>'must not be overwritten'])===false&&str_contains($second->last_error,'Lock wait timeout');}return $sql;};
    add_filter('query',$lockHook,100);
    try{$la=$lm->run('apply');$owned=array_merge($owned,array_values($la['page_ids']));}finally{remove_filter('query',$lockHook,100);$second->close();}
    $check($rowBlocked,'second connection cannot edit a locked managed hub');$check($metaBlocked,'second connection cannot insert into locked managed metadata range');
    $lm->run('rollback');

    // Deterministic two-connection race between validation and transaction start.
    $race=$manifest;foreach($race['updates']as$i=>&$hub){$id=$make(['post_name'=>$run.'-race-hub-'.$i,'post_content'=>$base]);$hub['id']=$id;$race['pages'][$i]['parent_id']=$id;}unset($hub);
    [$rp,$rd,$rj]=$saveManifest($race,'race');$releaseDigests[]=$rd;$rm=new TehNet_Growth_Content_Migration($rp,$rd,$rj);$ra=$rm->run('apply');$owned=array_merge($owned,array_values($ra['page_ids']));
    $second=new wpdb(DB_USER,DB_PASSWORD,DB_NAME,DB_HOST);$second->suppress_errors(true);$raceId=$race['updates'][0]['id'];$external='Concurrent editor content must survive';$armed=true;
    $raceHook=static function($sql)use($second,$raceId,$external,&$armed){global $wpdb;if($armed&&trim($sql)==='START TRANSACTION'){$armed=false;if($second->update($wpdb->posts,['post_content'=>$external],['ID'=>$raceId])!==1)throw new RuntimeException('Second connection race setup failed');}return $sql;};
    add_filter('query',$raceHook,100);
    try{$reject(fn()=>$rm->run('rollback'),'concurrent edit at rollback transaction boundary rejected');}finally{remove_filter('query',$raceHook,100);$second->close();}
    $check($wpdb->get_var($wpdb->prepare("SELECT post_content FROM {$wpdb->posts} WHERE ID=%d",$raceId))===$external,'concurrent editor content preserved');
} finally {
    if(isset($revisionLimit))remove_filter('wp_revisions_to_keep',$revisionLimit,10);
    foreach(array_reverse(array_unique($owned))as$id){
        $p=get_post($id);if(!$p)continue;
        $fixture=get_post_meta($id,'_tn_growth_fixture',true)===$run;
        $released=in_array(get_post_meta($id,'_tn_growth_release',true),$releaseDigests,true);
        if(!$fixture&&!$released)throw new RuntimeException('Fixture cleanup ownership boundary');
        if(!wp_delete_post($id,true))throw new RuntimeException('Owned fixture cleanup failed');
    }
    $cleanupEqual=$before===$fingerprint();file_put_contents(__DIR__.'/fixture-cleanup-verification-private.json',wp_json_encode(['original_posts_meta_unchanged'=>$cleanupEqual,'owned_fixture_pages_removed'=>count(array_unique($owned))]));chmod(__DIR__.'/fixture-cleanup-verification-private.json',0600);
    if(!$cleanupEqual)throw new RuntimeException('Original posts/meta changed after owned fixture cleanup');
}
$check($before===$fingerprint(),'all original posts and meta equal after fixture cleanup');
echo wp_json_encode(['status'=>'PASS','assertions'=>$checks,'original_posts_meta_unchanged'=>true,'scope'=>'Verified isolated native WordPress only','fixture_pages_cleaned'=>count(array_unique($owned)),'production_mutations'=>0]);
