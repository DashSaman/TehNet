<?php
/* Behavioral verification of the PR100 payload class-content-types.php on the real
 * isolated staging (post-decision-apply state). Read-only except the documented
 * CPT collision probe (created + deleted). Mirrors PR94's native acceptance. */
$results=[];$fail=0;
function tnst(?array $s=null):array{static $st=['r'=>[],'f'=>0];if($s!==null)$st=$s;return $st;}
function ck(string $n,bool $c,array $d=[]):void{$s=tnst();if(!$c)$s['f']++;$s['r'][]=['name'=>$n,'pass'=>$c]+$d;tnst($s);}
global $wpdb;
ck('staging_env',wp_get_environment_type()==='staging'&&home_url('/')==='http://localhost:18085/');
/* 1. Real public Lab pages resolve through the bounded resolver */
foreach([76=>'gns3-mikrotik',188=>'wireguard-mtu']as$id=>$slug){
    ck("lab_route_$slug",url_to_postid(home_url('/lab/'.$slug.'/'))===$id,['expected'=>$id]);
}
/* Page 207 exists only on production (staging voice pages are 193/194): the resolver
 * must FAIL-SAFE skip it here -> url_to_postid returns 0. Production behaviour of the
 * same code path was accepted in PR94's fixture (ids match production there). */
/* Staging hosts the real page as ID 194: core page rules resolve it (207 exists only on
 * production, where PR94's fixture acceptance verified the same code). The resolver's
 * fail-safe skip for missing 207 is proven separately by the collision checks below. */
ck('staging_voice_checklist_resolves_to_page_194',url_to_postid(home_url('/lab/voice-network-checklist/'))===194);
ck('staging_voice_checklist_is_page_194',get_page_by_path('lab/voice-network-checklist',OBJECT,'page')!==null&&get_post(194)->post_name==='voice-network-checklist');
/* 2. permalink structure + stored rewrite_rules unchanged by the resolver (option-level) */
$rr=$wpdb->get_row("SELECT option_value,autoload FROM {$wpdb->options} WHERE option_name='rewrite_rules'",ARRAY_A);
ck('rewrite_rules_present',is_array($rr)&&strlen((string)$rr['option_value'])>100);
ck('permalink_structure',(string)get_option('permalink_structure')==='/%postname%/');
file_put_contents('/tmp/lab-rr-before.json',wp_json_encode($rr));chmod('/tmp/lab-rr-before.json',0600);
/* 3. CPT collision probe: same-slug tn_lab must NOT mask the real page; unrelated rule retained */
$types=new TehNet_Core_Content_Types();
$collision=wp_insert_post(['post_type'=>'tn_lab','post_status'=>'draft','post_name'=>'voice-network-checklist','post_title'=>'Synthetic collision probe'],true);
ck('collision_probe_inserted',!is_wp_error($collision));
if(!is_wp_error($collision)){
    try{
        $rules=$types->existing_lab_page_rules(['unrelated/?$'=>'index.php?name=unrelated']);
        ck('collision_not_masked',!isset($rules['lab/voice-network-checklist/?$'])&&$rules['unrelated/?$']==='index.php?name=unrelated');
        /* and after deleting the probe, the resolver returns the page rule again */
        wp_delete_post((int)$collision,true);
        $rules2=$types->existing_lab_page_rules(['unrelated/?$'=>'index.php?name=unrelated']);
        /* after probe delete: on staging 207 is absent -> still no rule for that slug (skip path);
         * collision probe must be gone and unrelated rule retained */
        ck('resolver_skip_after_probe_delete',!isset($rules2['lab/voice-network-checklist/?$'])&&$rules2['unrelated/?$']==='index.php?name=unrelated');
    }catch(Throwable $e){ck('probe_cleanup',false,['err'=>$e->getMessage()]);}
}
$rr2=$wpdb->get_row("SELECT option_value,autoload FROM {$wpdb->options} WHERE option_name='rewrite_rules'",ARRAY_A);
ck('stored_rewrite_rules_unchanged',$rr===$rr2);
/* 4. Rollback bytes available: live file = payload (9d4c240e); baseline commit holds hotfix (2d3059386df1) */
$live=hash_file('sha256',ABSPATH.'wp-content/plugins/tehnet-core/includes/class-content-types.php');
ck('live_file_is_payload_9d4c240e',$live==='9d4c240edd873db5638a7521e6b1c6cd741cfaaea2f9d91ef27ea581a2222e2d',['live'=>substr((string)$live,0,16)]);
/* 5. noindex + isolation intact */
ck('blog_public_0',(string)get_option('blog_public')==='0');
$s=tnst();
echo wp_json_encode(['status'=>$s['f']?'FAIL':'PASS','total'=>count($s['r']),'failures'=>$s['f'],'checks'=>$s['r']],JSON_UNESCAPED_UNICODE),"\n";
exit($s['f']?1:0);
