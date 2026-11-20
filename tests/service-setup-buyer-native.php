<?php
/**
 * Read-only native verification for tehnet-service-setup-buyer-20261113-v1.
 * Run on the isolated staging container via wp-cli eval-file with:
 *   SERVICE_SETUP_BUYER_BODY      — absolute path of the release body file
 *   SERVICE_SETUP_BUYER_MANIFEST  — absolute path of the release manifest.json
 *   SERVICE_SETUP_BUYER_MIGRATION — absolute path of ops/migrate-growth-content.php
 * Prints one JSON verdict object; exits nonzero on any failure.
 * Never writes to the database.
 * State uses function-static storage: eval-file code is method-scoped, so
 * `global` references would silently detach the results (verified failure mode).
 */
if(!defined('TN_GROWTH_LIBRARY_ONLY'))define('TN_GROWTH_LIBRARY_ONLY',1);
function tn_state(?array $set=null):array {static $state=['results'=>[],'fail'=>0];if($set!==null)$state=$set;return $state;}
function check(string $name,bool $condition,array $detail=[]):void {
    $s=tn_state();if(!$condition)$s['fail']++;$s['results'][]=['name'=>$name,'pass'=>$condition]+$detail;tn_state($s);
}
$bodyPath=getenv('SERVICE_SETUP_BUYER_BODY');$manifestPath=getenv('SERVICE_SETUP_BUYER_MANIFEST');
$migrationPath=getenv('SERVICE_SETUP_BUYER_MIGRATION');
check('env_body_path_provided',is_string($bodyPath)&&is_file($bodyPath)&&!is_link($bodyPath));
check('env_manifest_path_provided',is_string($manifestPath)&&is_file($manifestPath)&&!is_link($manifestPath));
check('env_migration_path_provided',is_string($migrationPath)&&is_file($migrationPath)&&!is_link($migrationPath));
if(tn_state()['fail']){echo wp_json_encode(['status'=>'ENV_FAIL','checks'=>tn_state()['results']]);exit(1);}
require_once $migrationPath;
check('migration_class_loaded',class_exists('TehNet_Growth_Content_Migration'));

$manifest=json_decode((string)file_get_contents($manifestPath),true,512,JSON_THROW_ON_ERROR);
$body=(string)file_get_contents($bodyPath);
$key='tehnet-service-setup-buyer-20261113-v1';

/* 1. Scope authorization (static, behavioral). */
check('authorizes_positive_scope_key',TehNet_Growth_Content_Migration::authorizes($key,['key'=>$key]));
check('authorizes_positive_master',TehNet_Growth_Content_Migration::authorizes('tehnet-growth-20261031-v1',['key'=>'tehnet-growth-20261031-v1']));
check('rejects_wrong_authorization_value',!TehNet_Growth_Content_Migration::authorizes('tehnet-other-scope',['key'=>$key]));
check('rejects_mismatched_requested_key',!TehNet_Growth_Content_Migration::authorizes($key,['key'=>'tehnet-growth-20261031-v1']));
check('rejects_non_string_authorization',!TehNet_Growth_Content_Migration::authorizes(123,['key'=>$key]));
check('rejects_missing_requested_key',!TehNet_Growth_Content_Migration::authorizes($key,[]));

/* 2. Manifest identity and drift gates against the live staging page. */
$page=get_post(33);
check('target_page_publish',!!$page&&$page->post_type==='page'&&$page->post_status==='publish');
check('manifest_key_matches',($manifest['key']??null)===$key);
check('manifest_schema_1',($manifest['schema']??null)===1);
check('target_id_33',($manifest['target']['id']??null)===33);
check('target_url_exact',($manifest['target']['url']??null)==='https://tehnet.ir/services/network-setup-tehran/');
check('change_fields_content_only',($manifest['target']['change_fields']??null)===['post_content']);
check('title_observed_matches_live',($manifest['target']['title_observed']??null)===$page->post_title,['live'=>$page->post_title]);
check('live_content_matches_manifest_baseline',in_array(hash('sha256',$page->post_content),array_filter([
    $manifest['target']['expected_content_sha256']??null,$manifest['content_sha256_lf']??null]),true),
    ['live'=>hash('sha256',$page->post_content)]);
check('body_file_matches_manifest_lf_digest',hash('sha256',$body)===($manifest['content_sha256_lf']??''));

/* 3. Body structural validation mirroring the migration blocks() contract. */
check('body_canonical_serialization',serialize_blocks(parse_blocks($body))===$body);
check('body_kses_stable',wp_kses_post($body)===$body);
$allowed=['core/paragraph','core/heading','core/list','core/list-item'];
$inventory=[];$badFreeform=0;$walk=static function(array $blocks)use(&$walk,&$inventory,&$badFreeform):void {foreach($blocks as$b){
    if($b['blockName']===null){if(trim($b['innerHTML'])!=='')$badFreeform++;continue;} // whitespace freeforms mirror the migration walk
    $inventory[$b['blockName']]=($inventory[$b['blockName']]??0)+1;$walk($b['innerBlocks']??[]);}};
$walk(parse_blocks($body));
check('only_allowed_block_types',count(array_diff(array_keys($inventory),$allowed))===0,['inventory'=>$inventory]);
check('no_non_whitespace_freeform',$badFreeform===0,['count'=>$badFreeform]);
check('no_shortcode_blocks',!isset($inventory['core/shortcode']));
$h2s=[];foreach(parse_blocks($body) as$b)if(($b['blockName']??'')==='core/heading')$h2s[]=wp_strip_all_tags($b['innerHTML']);
check('six_h2_sections',count($h2s)===6,['count'=>count($h2s)]);
foreach(['فرایند کار از درخواست تا تحویل','تحویل‌دادنی‌های پایه پروژه','مرزهای خدمت؛ چه چیزهایی جزو این خدمت نیست','بعد از راه‌اندازی','چرا تهران نتورک','درخواست بررسی پروژه']as$required)
    check('h2_present_'.substr(md5($required),0,6),in_array($required,$h2s,true),['section'=>$required]);

/* 4. Internal links: same-origin, no javascript:, every target published. */
$hrefs=[];$proc=new WP_HTML_Tag_Processor($body);
while($proc->next_tag('A')){$href=$proc->get_attribute('href');if(is_string($href))$hrefs[]=$href;}
check('links_present',count($hrefs)>=6,['count'=>count($hrefs)]);
$pathMap=[];
foreach($hrefs as$href){
    check('link_same_origin_'.substr(md5($href),0,6),preg_match('#^/[a-z0-9\-\/]*?/?([?\#].*)?$#',$href)||str_starts_with($href,'https://tehnet.ir/'),
        ['href'=>$href]);
    check('no_javascript_links',!preg_match('/^\s*javascript:/i',$href),['href'=>$href]);
    $path=preg_replace('#[?\#].*$#','',(string)parse_url($href,PHP_URL_PATH));
    $path=trim($path,'/');if($path==='')$path='/';
    if(!isset($pathMap[$path])){
        $target=$path==='/'?get_post(get_option('page_on_front')):get_page_by_path($path,OBJECT,'page');
        $pathMap[$path]=$target&&$target->post_status==='publish';
    }
    check('link_target_published_'.substr(md5($href),0,6),$pathMap[$path],['href'=>$href,'path'=>$path]);
}
$external=array_values(array_filter($hrefs,static fn($h)=>str_starts_with($h,'http')&&!str_starts_with($h,'https://tehnet.ir/')));
check('no_external_links',count($external)===0,['external'=>$external]);

/* 5. Honesty limits: no fabricated guarantees or unverified claims. */
foreach(['تضمین','۵۰٪','بهترین','ارزان‌ترین','سریع‌ترین','100%','ضمانت‌نامه']as$claim)
    check('no_overclaim_'.substr(md5($claim),0,6),!str_contains($body,$claim),['marker'=>$claim]);

/* 6. Negative: a tampered body must be refused by the pipeline gates. */
$tampered=str_replace('<!-- wp:paragraph -->','<!-- wp:paragraph --><script>alert(1)</script>',$body);
check('negative_tampered_kses_unstable',wp_kses_post($tampered)!==$tampered);
$tampered2='<!-- wp:image --><figure class="wp-block-image"><img src="/x.png" alt="x"/></figure><!-- /wp:image -->'."\n".$body;
$inv2=[];$walk2=static function(array $blocks)use(&$walk2,&$inv2):void {foreach($blocks as$b){if($b['blockName']!==null)$inv2[$b['blockName']]=1;$walk2($b['innerBlocks']??[]);}};
$walk2(parse_blocks($tampered2));
check('negative_disallowed_block_detected',isset($inv2['core/image']));

/* 7. Meta: the suite itself must have executed its full check list. */
$s=tn_state();
check('meta_suite_ran_all_checks',count($s['results'])>=55,['executed'=>count($s['results'])]);

echo wp_json_encode(['status'=>$s['fail']?'FAIL':'PASS','total'=>count($s['results']),'failures'=>$s['fail'],'checks'=>$s['results']],JSON_UNESCAPED_UNICODE|JSON_PRETTY_PRINT),"\n";
exit($s['fail']?1:0);
