<?php
try {
$root='/src/content/service-readiness-2026-11-08/';
$m=json_decode(file_get_contents($root.'manifest.json'),true,512,JSON_THROW_ON_ERROR);$checks=0;
function tn_check($v,$label){global$checks;if(!$v)throw new RuntimeException($label);$checks++;}
foreach($m['targets']as$t){
 $before=file_get_contents($root.$t['id'].'-before.html');$after=file_get_contents($root.$t['content_file']);
 tn_check(hash('sha256',$before)===$t['expected_content_sha256'],'baseline hash');
 tn_check(hash('sha256',$after)===$t['content_sha256'],'candidate hash');
 $slug=$t['id']===8?'services':'network-tehran';
 $id=wp_insert_post(wp_slash(['import_id'=>$t['id'],'post_type'=>'page','post_status'=>'publish','post_parent'=>$t['id']===8?0:8,'post_name'=>$slug,'post_title'=>$t['title_observed'],'post_excerpt'=>'Synthetic fixture only','post_content'=>$before]),true);
 tn_check($id===$t['id'],'exact synthetic owner');
 $saved=get_post($id);$meta=get_post_meta($id);
 tn_check(serialize_blocks(parse_blocks($after))===$after,'native block roundtrip');
 tn_check(wp_kses_post($after)===$after,'native content sanitization');
 wp_update_post(wp_slash(['ID'=>$id,'post_content'=>$after]),true);
 tn_check(get_post($id)->post_content===$after,'actual body saved');
 foreach(['post_title','post_name','post_parent','post_excerpt','post_status']as$f)tn_check(get_post($id)->$f===$saved->$f,'protected field '.$f);
 tn_check(get_post_meta($id)===$meta,'metadata unchanged');
 $render=apply_filters('the_content',get_post($id)->post_content);
 tn_check(!str_contains($render,'[tn_service_request]'),'shortcode rendered');
 tn_check($id===8?substr_count($render,'<form')===1:str_contains($render,'general-network#service-request'),'canonical request journey present');
 tn_check((string)get_option('blog_public')==='0','intentional noindex unchanged');
 wp_update_post(wp_slash(['ID'=>$id,'post_content'=>$before]),true);
 tn_check(get_post($id)->post_content===$before,'baseline body restored');
}
echo 'TN_SEO_NATIVE '.wp_json_encode(['status'=>'PASS','checks'=>$checks,'fixture_only'=>true,'runtime_match_production'=>false,'woocommerce_loaded'=>class_exists('WooCommerce'),'production_mutations'=>0,'form_submissions'=>0,'restore_scope'=>'Target bodies only; ephemeral fixture destroyed. Not canonical release rehearsal or SQL restore.'])."\n";
}catch(Throwable $e){echo 'TN_SEO_NATIVE '.wp_json_encode(['status'=>'FAIL','error_type'=>get_class($e),'label'=>$e->getMessage()])."\n";exit(1);}
