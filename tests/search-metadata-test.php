<?php
/** Isolated WP API stubs: unit tests, NOT a real WordPress integration test. */
declare(strict_types=1);
define('ABSPATH', __DIR__ . '/');
class WP_Post {
    public int $ID = 5;
    public string $post_type = 'page';
    public string $post_status = 'publish';
    public string $post_password = '';
    public string $post_excerpt = '';
    public string $post_content = '';
}
class WP_Term {public string $name='آموزش شبکه';public string $description='مرور آموزش شبکه و سناریوهای منتشرشده';public string $taxonomy='category';}
$ctx = []; $hooks = [];
function reset_context(): void {
    global $ctx;
    $ctx = ['front'=>true, 'home'=>false, 'page'=>true, 'admin'=>false,
        'feed'=>false, '404'=>false, 'search'=>false, 'preview'=>false,
        'path'=>'home', 'template'=>'', 'post'=>new WP_Post(), 'paged'=>1,
        'external'=>false, 'profile_owner'=>false, 'title'=>'تهران نتورک | TehNet'];
}
function is_admin(){return $GLOBALS['ctx']['admin'];}
function is_feed(){return $GLOBALS['ctx']['feed'];}
function is_404(){return $GLOBALS['ctx']['404'];}
function is_search(){return $GLOBALS['ctx']['search'];}
function is_preview(){return $GLOBALS['ctx']['preview'];}
function is_front_page(){return $GLOBALS['ctx']['front'];}
function is_home(){return $GLOBALS['ctx']['home'];}
function is_page(){return $GLOBALS['ctx']['page'];}
function is_singular($types=[]){return $GLOBALS['ctx']['singular']??false;}
function is_shop(){return $GLOBALS['ctx']['shop']??false;}
function wc_get_page_id($key){return 9;}
function is_category(){return ($GLOBALS['ctx']['taxonomy']??'')==='category';}
function is_tag(){return ($GLOBALS['ctx']['taxonomy']??'')==='post_tag';}
function is_tax($type){return ($GLOBALS['ctx']['taxonomy']??'')===$type;}
function get_term_link($t){return 'https://tehnet.ir/category/network/';}
function is_wp_error($x){return false;}
function home_url($p='/'){return 'https://tehnet.ir'.$p;}
function get_post_thumbnail_id($id){return $GLOBALS['ctx']['thumbnail']??0;}
function wp_get_attachment_image_src($id,$size){return ['https://tehnet.ir/wp-content/uploads/reviewed.webp',1024,1024];}
function has_shortcode($v,$tag){return str_contains($v,'['.$tag.']');}
function get_post_time($f,$utc,$p){return '2026-09-23T00:00:00+00:00';}
function get_post_modified_time($f,$utc,$p){return '2026-10-16T00:00:00+00:00';}
function get_the_title($p){return 'مقالهٔ فنی با منبع';}
function get_queried_object(){return $GLOBALS['ctx']['post'];}
function get_post($id){return $GLOBALS['ctx']['post'];}
function get_option($name,$default=false){return ['page_for_posts'=>69,'blog_public'=>0][$name]??$default;}
function get_page_uri($id){return $GLOBALS['ctx']['path'];}
function get_page_template_slug($id){return $GLOBALS['ctx']['template'];}
function get_permalink($id){return 'https://tehnet.ir/'.($GLOBALS['ctx']['front']?'':$GLOBALS['ctx']['path'].'/');}
function get_query_var($key,$default=0){return $key==='paged'?$GLOBALS['ctx']['paged']:$default;}
function get_pagenum_link($n){return 'https://tehnet.ir/blog/page/'.$n.'/';}
function get_bloginfo($key){return 'تهران نتورک | TehNet';}
function wp_get_document_title(){return $GLOBALS['ctx']['title'];}
function get_locale(){return 'fa_IR';}
function strip_shortcodes($value){return preg_replace('/\[[^\]]*\]/','',$value);}
function wp_strip_all_tags($value){return strip_tags(preg_replace('@<(script|style)[^>]*?>.*?</\1>@si','',$value));}
function esc_attr($v){return htmlspecialchars((string)$v,ENT_QUOTES,'UTF-8');}
function esc_url($v){return esc_attr($v);}
function wp_json_encode($v,$flags=0){return json_encode($v,$flags);}
function apply_filters($name,$v){return $name==='tehnet_search_metadata_external_owner'?$GLOBALS['ctx']['external']:$v;}
function has_action($name,$cb){return $cb==='tehnet_profile_description'&&$GLOBALS['ctx']['profile_owner']?5:false;}
function add_action($name,$cb,$priority=10){$GLOBALS['hooks'][]=[$name,$cb,$priority];}
function output(): string {ob_start(); \TehNet\SearchMetadata\render(); return (string)ob_get_clean();}
$module=__DIR__.'/../site/mu-plugins/tehnet-search-metadata.php';
if (!is_file($module)) {fwrite(STDERR,"FAIL: metadata module is missing (expected initial RED)\n");exit(1);}
require $module;
$results=[];
function check(string $name,bool $pass):void {global $results;$results[]=['name'=>$name,'pass'=>$pass];echo ($pass?'PASS':'FAIL').' '.$name."\n";}
reset_context();$out=output();
check('homepage description exactly once',substr_count($out,'name="description"')===1);
check('homepage description is meaningful Persian',str_contains($out,'آموزش عملی شبکه'));
check('title canonical robots owners untouched',!str_contains($out,'<title>')&&!str_contains($out,'rel="canonical"')&&!str_contains($out,'name="robots"'));
check('no organization or fabricated rich-result types',!preg_match('/LocalBusiness|Organization|FAQPage|AggregateRating|Product|Review/',$out));
check('no outgoing script or tracking',!str_contains($out,'src=')&&!str_contains($out,'fetch('));
check('Open Graph URL and locale',str_contains($out,'property="og:url" content="https://tehnet.ir/"')&&str_contains($out,'content="fa_IR"'));
$ctx['post']->post_excerpt='توضیح اختصاصی و قابل ویرایش';$out=output();check('manual excerpt takes priority',str_contains($out,'content="توضیح اختصاصی و قابل ویرایش"'));
$ctx['post']->post_excerpt='<script>alert(1)</script><b>متن</b> &quot; ویژه';$out=output();check('HTML and attributes escaped',!str_contains($out,'alert(1)')&&!str_contains($out,'<b>')&&str_contains($out,'&quot;'));
$long=str_repeat('آزمون فارسی ',100);$clean=\TehNet\SearchMetadata\clean($long,200);preg_match_all('/./us',$clean,$chars);
check('Unicode truncation remains valid and bounded',preg_match('//u',$clean)===1&&count($chars[0])<=200);
check('invalid UTF8 safely omitted',\TehNet\SearchMetadata\clean("\xFF")==='');
foreach(['admin','feed','404','search','preview'] as $flag){reset_context();$ctx[$flag]=true;check('skip '.$flag,output()==='');}
reset_context();$ctx['post']->post_status='draft';check('skip unpublished object',output()==='');
reset_context();$ctx['post']->post_password='secret';check('skip password protected even with cookie',output()==='');
reset_context();$ctx['post']->post_type='product';check('no interference with product metadata',output()==='');
reset_context();$ctx['post']=null;check('null queried object safely ignored',output()==='');
reset_context();$ctx['external']=true;check('external SEO owner wins',output()==='');
reset_context();$ctx['front']=false;$ctx['path']='future-page';check('no guessed description for unknown empty page',output()==='');
$ctx['post']->post_excerpt='خلاصهٔ تحریریه';check('future pages work with explicit excerpt',str_contains(output(),'خلاصهٔ تحریریه'));
reset_context();$ctx['front']=false;$ctx['path']='sample-page';$ctx['post']->post_excerpt='Sample';check('sample page is not promoted',output()==='');
reset_context();$ctx['front']=false;$ctx['home']=true;$ctx['path']='blog';$ctx['paged']=2;check('blog pagination Open Graph matches page URL',str_contains(output(),'https://tehnet.ir/blog/page/2/'));
reset_context();$ctx['front']=false;$ctx['path']='services/remote-support';check('full route keyed not leaf slug',str_contains(output(),'پشتیبانی شبکه از راه دور'));
reset_context();$ctx['front']=false;$ctx['path']='amirreza-golavar';$ctx['template']='page-portfolio.php';$ctx['post']->post_content='<h1>امیررضا گل‌آور</h1>';$ctx['profile_owner']=true;$out=output();
check('existing profile description not duplicated',substr_count($out,'name="description"')===0);
preg_match('@<script type="application/ld\+json"[^>]*>(.*?)</script>@s',$out,$m);$graph=json_decode($m[1]??'',true);
check('valid ProfilePage and Person',($graph['@type']??'')==='ProfilePage'&&($graph['mainEntity']['@type']??'')==='Person');
check('stable profile identity',($graph['mainEntity']['@id']??'')==='https://tehnet.ir/amirreza-golavar/#person');
check('no private telephone or brand social impersonation',!preg_match('/telephone|sameAs|birthDate|credential|interactionStatistic/i',$m[1]??''));
$ctx['profile_owner']=false;check('profile description available without legacy theme callback',substr_count(output(),'name="description"')===1);
$ctx['post']->post_content='<h1>شخص دیگر</h1>';check('renamed page does not get false Person schema',!str_contains(output(),'ProfilePage'));
reset_context();$before=serialize($ctx);output();check('render does not write state',serialize($ctx)===$before&&get_option('blog_public')===0);
check('registered only front-end head hook',count($hooks)===1&&$hooks[0][0]==='wp_head');
reset_context();$ctx['front']=false;$ctx['page']=false;$ctx['singular']=true;$ctx['post']->post_type='product';$ctx['post']->post_excerpt='استعلام کالای TN-SN-17929؛ مدل نیازمند تطبیق';$ctx['thumbnail']=123;$out=output();
check('public product gets editable description without fake offers',substr_count($out,'name="description"')===1&&!preg_match('/priceCurrency|Offer|aggregateRating/',$out));
check('product social image uses native full-size image dimensions',str_contains($out,'reviewed.webp')&&str_contains($out,'og:image:width" content="1024'));
$ctx['post']->post_status='private';check('private product metadata remains hidden',output()==='');
reset_context();$ctx['front']=false;$ctx['page']=false;$ctx['taxonomy']='category';$ctx['post']=new WP_Term();$out=output();
check('blog category gets one missing canonical and description',substr_count($out,'rel="canonical"')===1&&substr_count($out,'name="description"')===1);
$ctx['paged']=2;check('category pagination canonical points to its own page',str_contains(output(),'rel="canonical" href="https://tehnet.ir/blog/page/2/"'));
$ctx['taxonomy']='product_cat';$ctx['post']->taxonomy='product_cat';check('Woo product category canonical owner remains unchanged',!str_contains(output(),'rel="canonical"'));
reset_context();$ctx['front']=false;$ctx['page']=false;$ctx['singular']=true;$ctx['post']->post_type='post';$ctx['post']->post_excerpt='متن فنی با مرجع رسمی';$ctx['post']->post_content='متن [tn_editorial_note]';$out=output();
check('visible editorial note permits truthful Article dates',str_contains($out,'"@type":"Article"')&&str_contains($out,'dateModified'));
check('article author does not expose account email or phone',!preg_match('/email|telephone|sameAs|credential/',$out));
$ctx['post']->post_content='متن بدون یادداشت';check('article attribution is not invented for unmarked content',!str_contains(output(),'"@type":"Article"'));
reset_context();$ctx['front']=false;$ctx['page']=false;$ctx['shop']=true;$ctx['path']='shop';$out=output();check('Woo shop archive gets description without duplicate canonical',str_contains($out,'فروشگاه تجهیزات شبکه')&&!str_contains($out,'rel="canonical"'));
foreach(['learn','lab','learn/mikrotik','learn/mikrotik/mtcna'] as $path){
    reset_context();$ctx['front']=false;$ctx['path']=$path;$ctx['post']->post_content='فهرست منابع [tn_editorial_note]';$out=output();
    check('collection page is not inferred to be Article: '.$path,!str_contains($out,'"@type":"Article"'));
    check('collection description and social metadata retained: '.$path,substr_count($out,'name="description"')===1&&str_contains($out,'property="og:url"'));
}
foreach(['learn/mikrotik/mtcna/routeros-winbox','learn/mikrotik/mtcna/static-routing','lab/gns3-mikrotik','lab/voice-network-checklist'] as $path){
    reset_context();$ctx['front']=false;$ctx['path']=$path;$ctx['post']->post_excerpt='درس فنی مستقل';$ctx['post']->post_content='متن درس [tn_editorial_note]';
    check('real lesson keeps Article: '.$path,str_contains(output(),'"@type":"Article"'));
}
reset_context();$ctx['front']=false;$ctx['page']=false;$ctx['singular']=true;$ctx['path']='lab';$ctx['post']->post_type='post';$ctx['post']->post_excerpt='نوشته مستقل';$ctx['post']->post_content='متن [tn_editorial_note]';
check('same-slug post is not excluded as a hub',str_contains(output(),'"@type":"Article"'));
$receiptPath=getenv('TN_METADATA_TEST_RECEIPT')?:__DIR__.'/../qa/search-metadata-unit.json';
file_put_contents($receiptPath,json_encode(['scope'=>'PHP unit tests with WP stubs; not integration/live proof','results'=>$results],JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
$failed=count(array_filter($results,fn($r)=>!$r['pass']));echo 'CHECKS='.count($results).' FAILURES='.$failed."\n";exit($failed?1:0);
