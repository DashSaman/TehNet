<?php
$m=json_decode(file_get_contents('/src/content/service-readiness-2026-11-08/manifest.json'),true);
foreach($m['targets']as$t){
 $result=wp_insert_post(wp_slash(['import_id'=>$t['id'],'post_type'=>'page','post_status'=>'publish','post_parent'=>$t['id']===8?0:8,'post_name'=>$t['id']===8?'services':'network-tehran','post_title'=>$t['title_observed'],'post_excerpt'=>'Synthetic fixture only','post_content'=>file_get_contents('/src/content/service-readiness-2026-11-08/'.$t['id'].'-before.html')]),true);
 if($result!==$t['id'])throw new RuntimeException('Exact fixture seed refused');
}
