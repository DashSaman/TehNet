<?php
try {
/** Exact existing owner67; only the disposable closed cloud fixture is allowed. */
if(wp_get_environment_type()!=='staging'||home_url('/')!=='http://localhost:18085/'||!WP_HTTP_BLOCK_EXTERNAL||!DISABLE_WP_CRON||(string)get_option('blog_public')!=='0')throw new RuntimeException('Closed cloud staging required');
define('TN_GROWTH_LIBRARY_ONLY',true);require getenv('TN_TEST_MIGRATION');
global $manifest,$body,$directory,$checks;
$manifest=json_decode(file_get_contents(getenv('TN_TEST_MANIFEST')),true,512,JSON_THROW_ON_ERROR);
$body=file_get_contents(dirname(getenv('TN_TEST_MANIFEST')).'/queues-troubleshooting.html');
$directory=getenv('TN_TEST_DIRECTORY');$checks=0;
if(!is_dir($directory)||(fileperms($directory)&0077)!==0||!str_starts_with($directory,'/tmp/tn-queue-cloud-native-')||basename($directory)!=='evidence')throw new RuntimeException('Private owned cloud evidence directory required');
function ok(bool $value,string $label):void{global $checks;if(!$value)throw new RuntimeException('FAIL: '.$label);++$checks;echo 'PASS: '.$label."\n";}
function db_state():array{global$wpdb;$r=[];foreach(['posts','postmeta','users','usermeta']as$table){$key=$table==='postmeta'?'meta_id':($table==='usermeta'?'umeta_id':'ID');$r[$table]=$wpdb->get_results("SELECT * FROM {$wpdb->$table} ORDER BY $key",ARRAY_A);}foreach(['blog_public','page_on_front','page_for_posts','woocommerce_shop_page_id','template','stylesheet']as$key)$r['options'][$key]=$wpdb->get_row($wpdb->prepare("SELECT option_value,autoload FROM {$wpdb->options} WHERE option_name=%s",$key),ARRAY_A);return$r;}
function attempt(string $name,array $m,?string $replacement=null):TehNet_Growth_Content_Migration{global$directory,$body;$root=$directory.'/'.$name;if(!mkdir($root,0700)||!mkdir($root.'/journal',0700))throw new RuntimeException('New private attempt required');file_put_contents($root.'/queues-troubleshooting.html',$replacement??$body);file_put_contents($root.'/manifest.json',json_encode($m,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES));return new TehNet_Growth_Content_Migration($root.'/manifest.json',hash_file('sha256',$root.'/manifest.json'),$root.'/journal');}
function refused(callable $action,string $label,?string $required=null):void{try{$action();}catch(Throwable$error){ok($required===null||$error->getMessage()===$required,$label);return;}throw new RuntimeException('FAIL: not refused '.$label);}
$before=db_state();$post=get_post(67);$original=(array)$post;$meta=get_post_meta(67);$revisions=wp_get_post_revisions(67);
if(!$post||$post->post_type!=='page'||get_page_uri(67)!=='learn/mikrotik/mtcna/queues-troubleshooting'||hash('sha256',$post->post_content)!==$manifest['target']['expected_content_sha256'])throw new RuntimeException('Exact original Queue fixture required');
ok(TehNet_Growth_Content_Migration::authorizes('tehnet-winbox-queue-cloud-20261108-v1',$manifest),'Exact Queue scope authorized');
ok(!TehNet_Growth_Content_Migration::authorizes('tehnet-winbox-core-guides-20261105-v1',$manifest),'Earlier core scope cannot authorize Queue');
ok(!TehNet_Growth_Content_Migration::authorizes(false,$manifest),'Missing authorization refused');
$keep=static fn()=>0;add_filter('wp_revisions_to_keep',$keep,10);
$m=attempt('success',$manifest);$ready=$m->run('check');
ok($ready['status']==='READY'&&$ready['hubs_pending']===1&&$ready['pages_pending']===0,'Only existing Queue body pending');
ok(db_state()===$before,'Check has zero record changes');
$result=$m->run('apply');ok($result['hubs_updated']===1&&$result['pages_created']===0,'One existing body changed; zero new page');
ok(get_post(67)->post_content===$body,'Exact source body stored');
foreach(['post_title','post_name','post_parent','post_excerpt','post_status','post_type']as$field)ok((string)get_post(67)->$field===(string)$original[$field],'Protected '.$field.' unchanged');
ok(get_post_meta(67)===$meta,'All owner metadata unchanged');
foreach($revisions as$id=>$rev)ok((array)get_post($id)===(array)$rev,'Existing revision unchanged');
$after=db_state();ok($m->run('apply')['hubs_updated']===0&&db_state()===$after,'Repeat apply is record-idempotent');
global$wpdb;$wpdb->update($wpdb->posts,['post_content'=>$body."\nTNQA-newer-edit"],['ID'=>67]);clean_post_cache(67);
refused(fn()=>$m->run('rollback'),'Later foreign edit refuses rollback');
ok(str_ends_with(get_post(67)->post_content,'TNQA-newer-edit'),'Foreign edit preserved');
$wpdb->update($wpdb->posts,['post_content'=>$body],['ID'=>67]);clean_post_cache(67);
$rolled=$m->run('rollback');ok($rolled['hubs_restored']===1&&$rolled['pages_drafted']===0,'Rollback restores only Queue body');
ok(db_state()===$before,'All original posts/meta/users/revisions and protected options restored');
ok($m->run('rollback')['status']==='ROLLED_BACK'&&db_state()===$before,'Repeat rollback is idempotent');
refused(fn()=>$m->run('apply'),'Rolled-back journal cannot be replayed');
foreach(['id'=>5,'url'=>'https://tehnet.ir/elsewhere/','uri'=>'elsewhere','title_observed'=>'Wrong fixture title']as$key=>$value){$bad=$manifest;$bad['target'][$key]=$value;refused(fn()=>attempt('target-'.$key,$bad),'Owner '.$key.' drift refused');}
$bad=$manifest;$bad['content_file']='../queues-troubleshooting.html';refused(fn()=>attempt('path-drift',$bad),'Body path expansion refused');
$bad=$manifest;$bad['target']['change_fields'][]='post_excerpt';refused(fn()=>attempt('wider-fields',$bad),'Excerpt/title scope expansion refused');
$bad=$manifest;$bad['targets']=[$bad['target']];refused(fn()=>attempt('second-owner',$bad),'Unknown or second-owner manifest fields refused');
$bad=$manifest;$bad['content_sha256_lf']=str_repeat('0',64);refused(fn()=>attempt('body-digest',$bad),'Body hash drift refused');
$bad=$manifest;$bad['target']['expected_content_sha256']=str_repeat('0',64);refused(fn()=>attempt('baseline',$bad)->run('apply'),'Baseline drift refused before writes');
$front=get_option('page_on_front');update_option('page_on_front',67);try{refused(fn()=>attempt('protected-role',$manifest),'Owner newly assigned homepage role refused','Protected role cannot be an editorial target');}finally{update_option('page_on_front',$front);}
ok((string)get_option('page_on_front')===(string)$front,'Homepage role restored');
$asset='/wp-content/mu-plugins/tehnet-technical-resources/learning-media/queue-cloud-20261108/01-connected-baseline.png';
$cases=[
'foreign-src'=>[str_replace('src="'.$asset.'"','src="https://example.invalid/foreign.png"',$body),'Only scope-approved original captures with descriptive alt are approved'],
'empty-alt'=>[preg_replace('/ alt="[^"]*"/u',' alt=""',$body,1),'Only scope-approved original captures with descriptive alt are approved'],
'fake-id'=>[str_replace('<!-- wp:image {"sizeSlug"','<!-- wp:image {"id":123,"sizeSlug"',$body),'Only scope-approved original captures with descriptive alt are approved'],
'fullsize'=>[str_replace('href="'.$asset.'"','href="https://example.invalid/foreign.png"',$body),'Original full-size link and matching callout class required'],
'callout'=>[str_replace('"className":"tn-lab-capture tn-queue-shot-1"','"className":"tn-lab-capture tn-queue-shot-2"',$body),'Original full-size link and matching callout class required'],
'figure'=>[str_replace('class="wp-block-image size-full tn-lab-capture tn-queue-shot-1"','class="wp-block-image size-full tn-lab-capture tn-queue-shot-2"',$body),'Exact Queue figure class required']
];
foreach($cases as$name=>[$changed,$error]){ok($changed!==$body,'Negative media fixture differs: '.$name);$bad=$manifest;$bad['content_sha256_lf']=hash('sha256',$changed);refused(fn()=>attempt($name,$bad,$changed),'Specific media boundary: '.$name,$error);}
foreach(['raw-html'=>"<!-- wp:html --><div>forbidden</div><!-- /wp:html -->",'new-form'=>"<!-- wp:shortcode -->[tn_service_request]<!-- /wp:shortcode -->"]as$name=>$append){$changed=$body."\n".$append;$bad=$manifest;$bad['content_sha256_lf']=hash('sha256',$changed);refused(fn()=>attempt($name,$bad,$changed),'Privilege expansion refused: '.$name);}
ok(db_state()===$before,'All negative cases preserve complete original state');
$injected=false;$hook=static function()use(&$injected):void{$injected=true;update_post_meta(67,'_tnqa_foreign_hook','test-only');};add_action('save_post_page',$hook,50);try{refused(fn()=>attempt('hook-drift',$manifest)->run('apply'),'Save-hook metadata side effect rejects update');}finally{remove_action('save_post_page',$hook,50);}
ok($injected&&db_state()===$before,'Hook transaction rolls back exactly');
$locked=false;$otherHook=static function()use(&$locked):void{global$wpdb;$other=new wpdb(DB_USER,DB_PASSWORD,DB_NAME,DB_HOST);$other->suppress_errors(true);$other->query('SET SESSION innodb_lock_wait_timeout=1');$r=$other->update($wpdb->posts,['post_content'=>'TNQA concurrent'],['ID'=>67]);$locked=$r===false&&str_contains(strtolower($other->last_error),'lock wait timeout');$other->close();};add_action('save_post_page',$otherHook,50);$locking=attempt('row-lock',$manifest);try{$locking->run('apply');ok($locked,'Owner row locked before save-hook concurrent write');}finally{remove_action('save_post_page',$otherHook,50);$locking->run('rollback');}
ok(db_state()===$before,'Concurrent case exactly restored');
remove_filter('wp_revisions_to_keep',$keep,10);
echo 'QUEUE_CLOUD_NATIVE=PASS checks='.$checks."\n";

} catch(Throwable $error) {
    $file=basename($error->getFile());
    $owned=in_array($file,['cloud-queue-migration-native.php','migrate-growth-content.php'],true)||str_contains($file,'EvalFile_Command.php');
    $message=$owned&&$error instanceof RuntimeException?$error->getMessage():'NON_PUBLIC_EXCEPTION_MESSAGE_SUPPRESSED';
    $differences=[];
    if(isset($before)&&function_exists('db_state')){
        foreach(db_state()as$key=>$value){
            if(($before[$key]??null)===$value)continue;
            $differences[$key]=['before_count'=>is_array($before[$key]??null)?count($before[$key]):null,'after_count'=>is_array($value)?count($value):null];
            if($key==='options')foreach($value as$name=>$current)if(($before[$key][$name]??null)!==$current)$differences[$key]['changed'][$name]=['before_type'=>gettype($before[$key][$name]??null),'after_type'=>gettype($current)];
        }
    }
    echo 'TN_NATIVE_DIFFERENCE='.json_encode($differences,JSON_UNESCAPED_SLASHES)."\n";
    echo 'TN_NATIVE_ERROR='.json_encode(['class'=>get_class($error),'file'=>$file,'line'=>$error->getLine(),'message'=>$message,'checks'=>$checks??0],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES)."\n";
    exit(1);
}
