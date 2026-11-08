<?php
try{
$phase=$args[0]??'off';$checks=[];$ck=static function($ok,$label)use(&$checks){if(!$ok)throw new RuntimeException($label);$checks[]=$label;};
$ck((string)get_option('blog_public')==='0','Persisted blog_public remains0');
if($phase==='off'){
 $ck(get_option('tn_index_policy_20261108',null)===null,'No activation option installed');
 $ck(!class_exists('TehNet_Core_Index_Policy')||TehNet_Core_Index_Policy::approved()===[],'Runtime absent or OFF');
 $r=apply_filters('wp_robots',[]);$ck(!empty($r['noindex']),'Original core noindex preserved');$ck(wp_sitemaps_get_server()->sitemaps_enabled()===false,'Original sitemap disabled');
}elseif($phase==='active'){
 $ck(class_exists('TehNet_Core_Index_Policy')&&count(TehNet_Core_Index_Policy::approved())===16,'Exact16 approved current public page identities');
 $policy=new TehNet_Core_Index_Policy();$text="User-agent: Google-Extended\nDisallow: /\n\nUser-agent: *\nDisallow: /wp-admin/\nAllow: /wp-admin/admin-ajax.php\n";
 $after=$policy->robots($text,false);$ck(str_starts_with($after,rtrim($text)),'Existing managed/training crawler directives retained verbatim');$ck(substr_count($policy->robots($after,false),'Sitemap: ')===1,'Sitemap directive idempotent');
 $good=get_option(TehNet_Core_Index_Policy::OPTION);$bad=$good;$bad['approved'][]=['path'=>'/support/','id'=>196];update_option(TehNet_Core_Index_Policy::OPTION,$bad,false);$ck(TehNet_Core_Index_Policy::approved()===[],'Injected private/unapproved path fails closed');update_option(TehNet_Core_Index_Policy::OPTION,$good,false);
 $bad=$good;$bad['approved'][0]['id']=196;update_option(TehNet_Core_Index_Policy::OPTION,$bad,false);$ck(TehNet_Core_Index_Policy::approved()===[],'Path/ID mismatch fails closed');update_option(TehNet_Core_Index_Policy::OPTION,$good,false);
 $ck(count(TehNet_Core_Index_Policy::approved())===16,'Approved option restored after negative cases');
 $id=wp_insert_post(['post_type'=>'tn_ticket','post_status'=>'private','post_title'=>'Owned synthetic preservation record','post_content'=>'Synthetic data inserted after activation, before rollback'],true);$ck(!is_wp_error($id),'Create owned post-activation record for rollback preservation test');file_put_contents('/lab/index-preservation-private.json',wp_json_encode(['id'=>(int)$id]));chmod('/lab/index-preservation-private.json',0600);
}elseif($phase==='restored'){$owned=json_decode(file_get_contents('/lab/index-preservation-private.json'),true);$p=get_post($owned['id']);$ck($p&&$p->post_status==='private'&&$p->post_content==='Synthetic data inserted after activation, before rollback','Option/file rollback preserves newer business record');wp_delete_post($p->ID,true);$ck(!get_post($p->ID),'Owned preservation fixture removed');$ck(get_option('tn_index_policy_20261108',null)===null,'Exact absent option restored');$ck(!class_exists('TehNet_Core_Index_Policy'),'Owned new runtime file and bootstrap restored');$ck(!empty(apply_filters('wp_robots',[])['noindex']),'Default noindex restored');$ck(!wp_sitemaps_get_server()->sitemaps_enabled(),'Sitemap disabled again');}
else throw new RuntimeException('Unknown index test phase');
echo 'TN_INDEX_NATIVE '.wp_json_encode(['phase'=>$phase,'status'=>'PASS','checks'=>$checks,'production_mutations'=>0])."\n";
}catch(Throwable$e){echo 'TN_INDEX_NATIVE '.wp_json_encode(['status'=>'FAIL','phase'=>$phase??'','label'=>$e->getMessage()])."\n";exit(1);}
