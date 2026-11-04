<?php
/** Run only against the isolated existing native preview, with a private fixture. */
if(wp_get_environment_type()!=='staging'||home_url('/')!=='http://localhost:18085/'||!WP_HTTP_BLOCK_EXTERNAL||!DISABLE_WP_CRON||(string)get_option('blog_public')!=='0')throw new RuntimeException('Isolated native staging required');
define('TN_GROWTH_LIBRARY_ONLY',true);require getenv('TN_TEST_MIGRATION');
global $educationTemplate,$educationRoot,$educationChecks;
$educationTemplate=json_decode(file_get_contents(getenv('TN_TEST_MANIFEST')),true,512,JSON_THROW_ON_ERROR);
$educationRoot=getenv('TN_TEST_DIRECTORY');$educationChecks=0;
if(!is_dir($educationRoot)||(fileperms($educationRoot)&0077)!==0||!str_starts_with($educationRoot,'/tmp/tn-educational-native-'))throw new RuntimeException('Private owned fixture required');
function eduExpect(bool $ok,string $label):void{global $educationChecks;if(!$ok)throw new RuntimeException('FAIL: '.$label);++$educationChecks;echo 'PASS: '.$label."\n";}
function eduState():array{global $wpdb;$r=[];foreach(['posts','postmeta','users','usermeta']as$t){$key=$t==='postmeta'?'meta_id':($t==='usermeta'?'umeta_id':'ID');$r[$t]=$wpdb->get_results("SELECT * FROM {$wpdb->$t} ORDER BY $key",ARRAY_A);}return$r;}
function eduAttempt(string $name,array $m):TehNet_Growth_Content_Migration{global $educationRoot;$d=$educationRoot.'/'.$name;if(!is_dir($d)){mkdir($d,0700);mkdir($d.'/journal',0700);foreach($m['targets']as$t){$f=basename($t['content_file']);copy(dirname(getenv('TN_TEST_MANIFEST')).'/'.$f,$d.'/'.$f);}file_put_contents($d.'/manifest.json',wp_json_encode($m,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES));}return new TehNet_Growth_Content_Migration($d.'/manifest.json',hash_file('sha256',$d.'/manifest.json'),$d.'/journal');}
function eduRefused(callable $f,string $label):void{try{$f();}catch(Throwable $e){eduExpect(true,$label);return;}throw new RuntimeException('FAIL: not refused '.$label);}
$before=eduState();$m=$educationTemplate;
eduExpect(TehNet_Growth_Content_Migration::authorizes($m['key'],$m),'Explicit correction scope accepted');
eduExpect(!TehNet_Growth_Content_Migration::authorizes('tehnet-growth-20261031-v1',$m),'Older scope cannot authorize eight identities');
$migration=eduAttempt('success',$m);$ready=$migration->run('check');
eduExpect($ready['hubs_pending']===8&&$ready['pages_pending']===0&&eduState()===$before,'Preflight is read-only for exactly eight existing records');
$applied=$migration->run('apply');eduExpect($applied['hubs_updated']===8&&$applied['pages_created']===0,'Eight corrections, no new page');
foreach($m['targets']as$t){$q=get_post($t['id']);eduExpect($q->post_content===file_get_contents(dirname(getenv('TN_TEST_MANIFEST')).'/'.$t['content_file'])&&$q->post_excerpt===$t['excerpt'],'Exact body and excerpt '.$t['id']);eduExpect($q->post_title===($t['title']??$t['title_observed'])&&get_page_uri($q)===$t['uri']&&$q->post_type===$t['type'],'Title and unchanged public identity '.$t['id']);}
$after=eduState();$repeat=eduAttempt('success',$m)->run('apply');
eduExpect($repeat['hubs_updated']===0&&eduState()===$after,'Fresh-process-equivalent construction permits idempotent repeat');
eduExpect(eduAttempt('success',$m)->run('check')['status']==='APPLIED','Fresh applied preflight uses after-state journal');
global $wpdb;
$wpdb->update($wpdb->posts,['post_excerpt'=>'TNQA foreign edit'],['ID'=>70]);clean_post_cache(70);
eduRefused(fn()=>eduAttempt('success',$m)->run('rollback'),'Rollback refuses later excerpt edit');
$wpdb->update($wpdb->posts,['post_excerpt'=>$m['targets'][7]['excerpt']],['ID'=>70]);clean_post_cache(70);
$rolled=eduAttempt('success',$m)->run('rollback');eduExpect($rolled['hubs_restored']===8&&eduState()===$before,'Fresh rollback restores all original records and revisions exactly');
eduExpect(eduAttempt('success',$m)->run('rollback')['status']==='ROLLED_BACK'&&eduState()===$before,'Fresh rollback repeat is idempotent');
eduRefused(fn()=>eduAttempt('success',$m)->run('apply'),'Rolled-back release cannot be silently reused');
foreach(['missing','post-type','fields','title','digest','body-drift','excerpt-drift']as$case){$bad=$m;
 if($case==='missing')array_pop($bad['targets']);
 if($case==='post-type')$bad['targets'][7]['type']='page';
 if($case==='fields')$bad['targets'][0]['change_fields'][]='post_status';
 if($case==='title')$bad['targets'][1]['title']='Unsupported lesson';
 if($case==='digest')$bad['targets'][0]['content_sha256_lf']=str_repeat('0',64);
 if($case==='body-drift')$bad['targets'][0]['expected_content_sha256']=str_repeat('0',64);
 if($case==='excerpt-drift')$bad['targets'][0]['expected_excerpt_sha256']=str_repeat('0',64);
 eduRefused(fn()=>eduAttempt($case,$bad)->run('apply'),'Manifest boundary '.$case);
}
eduExpect(eduState()===$before,'Negative cases leave all data unchanged');
$race=eduAttempt('excerpt-race',$m);$original=get_post(70)->post_excerpt;
$wpdb->update($wpdb->posts,['post_excerpt'=>'TNQA intervening edit'],['ID'=>70]);clean_post_cache(70);
eduRefused(fn()=>$race->run('apply'),'Intervening excerpt edit after construction is preserved');
eduExpect(get_post(70)->post_excerpt==='TNQA intervening edit','Foreign excerpt was not overwritten');
$wpdb->update($wpdb->posts,['post_excerpt'=>$original],['ID'=>70]);clean_post_cache(70);
eduExpect(eduState()===$before,'Race fixture restored exactly');
$hook=static function($id):void{if((int)$id===70)update_post_meta(70,'_tnqa_forbidden_side_effect','owned');};
add_action('save_post_post',$hook,50);
try{eduRefused(fn()=>eduAttempt('hook-drift',$m)->run('apply'),'Post70 hooks cannot expand field scope');}finally{remove_action('save_post_post',$hook,50);}
eduExpect(eduState()===$before,'Rejected side effect and all eight writes transactionally restored');
echo 'EDUCATIONAL_NATIVE=PASS checks='.$educationChecks."\n";
