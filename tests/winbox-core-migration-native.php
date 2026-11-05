<?php
/** Two exact existing owners; private closed staging only. */
if(wp_get_environment_type()!=='staging'||home_url('/')!=='http://localhost:18085/'||!WP_HTTP_BLOCK_EXTERNAL||!DISABLE_WP_CRON||(string)get_option('blog_public')!=='0')throw new RuntimeException('Closed native staging required');
define('TN_GROWTH_LIBRARY_ONLY',true);require getenv('TN_TEST_MIGRATION');
global $template,$bodies,$directory,$checks;
$template=json_decode(file_get_contents(getenv('TN_TEST_MANIFEST')),true,512,JSON_THROW_ON_ERROR);$bodies=[];
foreach($template['targets']as$t)$bodies[$t['id']]=file_get_contents(dirname(getenv('TN_TEST_MANIFEST')).'/'.$t['content_file']);
$directory=getenv('TN_TEST_DIRECTORY');$checks=0;
if(!is_dir($directory)||(fileperms($directory)&0077)!==0||!str_starts_with($directory,'/tmp/tn-winbox-core-native-')||basename($directory)!=='evidence')throw new RuntimeException('Owned private evidence directory required');
function expect(bool $value,string $label):void{global $checks;if(!$value)throw new RuntimeException('FAIL: '.$label);++$checks;echo 'PASS: '.$label."\n";}
function state():array{global $wpdb;$r=[];foreach(['posts','postmeta','users','usermeta']as$t){$key=$t==='postmeta'?'meta_id':($t==='usermeta'?'umeta_id':'ID');$r[$t]=$wpdb->get_results("SELECT * FROM {$wpdb->$t} ORDER BY $key",ARRAY_A);}return$r;}
function attempt(string $name,array $m):TehNet_Growth_Content_Migration{global$directory,$bodies;$root=$directory.'/'.$name;if(!mkdir($root,0700)||!mkdir($root.'/journal',0700))throw new RuntimeException('New private attempt required');foreach($m['targets']as$t){$filename=$t['content_file']??'';if(in_array($filename,['routeros-winbox.html','ip-dhcp-dns.html'],true))file_put_contents($root.'/'.$filename,$bodies[$t['id']]??$bodies[62]);}file_put_contents($root.'/manifest.json',json_encode($m,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES));return new TehNet_Growth_Content_Migration($root.'/manifest.json',hash_file('sha256',$root.'/manifest.json'),$root.'/journal');}
function refused(callable$action,string$label,?string$required=null):void{try{$action();}catch(Throwable$error){expect($required===null||$error->getMessage()===$required,$label);return;}throw new RuntimeException('FAIL: not refused '.$label);}
$before=state();$original=[];
foreach($template['targets']as&$t){$id=$t['id'];$post=get_post($id);if(!$post||$post->post_type!=='page'||get_page_uri($post)!==$t['uri'])throw new RuntimeException('Exact original lesson identity required');$t['expected_content_sha256']=hash('sha256',$post->post_content);$t['title_observed']=$post->post_title;$original[$id]=['post'=>(array)$post,'meta'=>get_post_meta($id),'revisions'=>wp_get_post_revisions($id)];}unset($t);
expect(TehNet_Growth_Content_Migration::authorizes('tehnet-winbox-core-guides-20261105-v1',$template),'Exact WinBox scope authorized');
expect(!TehNet_Growth_Content_Migration::authorizes('tehnet-illustrated-routing-20261104-v1',$template),'Earlier routing scope cannot authorize this package');
expect(!TehNet_Growth_Content_Migration::authorizes(false,$template),'Absent authorization refused');
$keep=static fn()=>0;add_filter('wp_revisions_to_keep',$keep,10);
$migration=attempt('success',$template);$ready=$migration->run('check');
expect($ready['status']==='READY'&&$ready['hubs_pending']===2&&$ready['pages_pending']===0,'Only two existing bodies pending');expect(state()===$before,'Check changes no records');
$result=$migration->run('apply');expect($result['hubs_updated']===2&&$result['pages_created']===0,'Two bodies updated and zero new page');
foreach([62,63]as$id){$post=get_post($id);expect($post->post_content===$bodies[$id],'Exact body stored for '.$id);foreach(['post_title','post_name','post_parent','post_excerpt','post_status','post_type']as$field)expect((string)$post->$field===(string)$original[$id]['post'][$field],'Protected '.$field.' retained for '.$id);expect(get_post_meta($id)===$original[$id]['meta'],'All metadata retained for '.$id);foreach($original[$id]['revisions']as$rid=>$rev)expect((array)get_post($rid)===(array)$rev,'Existing revision retained for '.$id);}
$after=state();$repeat=$migration->run('apply');expect($repeat['hubs_updated']===0&&state()===$after,'Repeat apply is record-idempotent');
global$wpdb;$wpdb->update($wpdb->posts,['post_content'=>$bodies[63]."\nTNQA-newer-edit"],['ID'=>63]);clean_post_cache(63);
refused(fn()=>$migration->run('rollback'),'Rollback refuses later edit in either owner');expect(str_ends_with(get_post(63)->post_content,'TNQA-newer-edit')&&get_post(62)->post_content===$bodies[62],'Foreign edit preserved before any rollback write');
$wpdb->update($wpdb->posts,['post_content'=>$bodies[63]],['ID'=>63]);clean_post_cache(63);$rolled=$migration->run('rollback');expect($rolled['hubs_restored']===2&&$rolled['pages_drafted']===0,'Rollback restores only both existing owners');expect(state()===$before,'All original posts/meta/users/revisions exactly restored');expect($migration->run('rollback')['status']==='ROLLED_BACK'&&state()===$before,'Repeat rollback idempotent');refused(fn()=>$migration->run('apply'),'Rolled-back journal cannot be replayed');
foreach(['id'=>5,'url'=>'https://tehnet.ir/elsewhere/','uri'=>'elsewhere','content_file'=>'../routeros-winbox.html','title_observed'=>'TNQA wrong title']as$key=>$value){$bad=$template;$bad['targets'][0][$key]=$value;refused(fn()=>attempt('target-'.$key,$bad),'Target '.$key.' drift refused');}
$bad=$template;$bad['targets'][]=$template['targets'][0];refused(fn()=>attempt('third-target',$bad),'Third target refused');
$bad=$template;$bad['targets'][1]=$bad['targets'][0];refused(fn()=>attempt('duplicate-target',$bad),'Duplicate owner refused');
$bad=$template;$bad['targets'][0]['change_fields'][]='post_excerpt';refused(fn()=>attempt('wider-fields',$bad),'Excerpt/title scope expansion refused');
$bad=$template;$bad['targets'][0]['content_sha256_lf']=str_repeat('0',64);refused(fn()=>attempt('wrong-body-digest',$bad),'Body digest drift refused');
$bad=$template;$bad['targets'][1]['expected_content_sha256']=str_repeat('0',64);refused(fn()=>attempt('wrong-baseline',$bad)->run('apply'),'Baseline drift in second owner refused before writes');
$front=get_option('page_on_front');update_option('page_on_front',62);try{refused(fn()=>attempt('protected-role',$template),'An owner newly assigned homepage role refused','Protected role cannot be an illustrated target');}finally{update_option('page_on_front',$front);}expect((string)get_option('page_on_front')===(string)$front,'Homepage role restored after negative fixture');
$safe=$bodies[62];$asset='/wp-content/mu-plugins/tehnet-technical-resources/learning-media/winbox-20261105/01-connected-overview.png';
$cases=[
 'foreign-src'=>[str_replace('src="'.$asset.'"','src="https://example.invalid/not-owned.png"',$safe),'Only scope-approved original captures with descriptive alt are approved'],
 'empty-alt'=>[preg_replace('/ alt="[^"]*"/u',' alt=""',$safe,1),'Only scope-approved original captures with descriptive alt are approved'],
 'invented-id'=>[str_replace('<!-- wp:image {"sizeSlug"','<!-- wp:image {"id":123,"sizeSlug"',$safe),'Only scope-approved original captures with descriptive alt are approved'],
 'wrong-fullsize'=>[str_replace('href="'.$asset.'"','href="https://example.invalid/elsewhere"',$safe),'Original full-size link and matching callout class required'],
 'wrong-class'=>[str_replace('"className":"tn-lab-capture tn-lab-shot-1"','"className":"tn-lab-capture tn-lab-shot-2"',$safe),'Original full-size link and matching callout class required'],
];
foreach($cases as$name=>[$changed,$error]){expect($changed!==$safe,'Negative image fixture differs: '.$name);$bodies[62]=$changed;$bad=$template;$bad['targets'][0]['content_sha256_lf']=hash('sha256',$changed);refused(fn()=>attempt($name,$bad),'Specific image boundary: '.$name,$error);}$bodies[62]=$safe;
foreach(['raw-html'=>"<!-- wp:html --><div>forbidden</div><!-- /wp:html -->",'new-form'=>"<!-- wp:shortcode -->[tn_service_request]<!-- /wp:shortcode -->"]as$name=>$addition){$bodies[62]=$safe."\n".$addition;$bad=$template;$bad['targets'][0]['content_sha256_lf']=hash('sha256',$bodies[62]);refused(fn()=>attempt($name,$bad),'No privilege for '.$name);}$bodies[62]=$safe;
expect(state()===$before,'All negative cases preserve records');
$injected=false;$hook=static function()use(&$injected):void{$injected=true;update_post_meta(63,'_tnqa_foreign_hook','test-only');};add_action('save_post_page',$hook,50);try{refused(fn()=>attempt('hook-drift',$template)->run('apply'),'Hook metadata drift rejects the atomic two-owner update');}finally{remove_action('save_post_page',$hook,50);}expect($injected&&state()===$before,'Hook side effect transaction exactly rolled back');
$locked=false;$concurrent=static function()use(&$locked):void{global$wpdb;$other=new wpdb(DB_USER,DB_PASSWORD,DB_NAME,DB_HOST);$other->suppress_errors(true);$other->query('SET SESSION innodb_lock_wait_timeout=1');$r=$other->update($wpdb->posts,['post_content'=>'TNQA concurrent'],['ID'=>63]);$locked=$r===false&&str_contains(strtolower($other->last_error),'lock wait timeout');$other->close();};add_action('save_post_page',$concurrent,50);$locking=attempt('row-lock',$template);try{$locking->run('apply');expect($locked,'Both owner rows locked before first save hook');}finally{remove_action('save_post_page',$concurrent,50);$locking->run('rollback');}expect(state()===$before,'Concurrent case restores complete original state');
remove_filter('wp_revisions_to_keep',$keep,10);echo 'WINBOX_CORE_NATIVE=PASS checks='.$checks."\n";
