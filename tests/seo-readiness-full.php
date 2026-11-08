<?php
try {
$phase=$args[0]??'seed';$root='/src/content/service-readiness-2026-11-08/';
if($phase==='seed'){
 $data=json_decode(file_get_contents('/src/tests/fixtures/p94-public-service-pages.json'),true,512,JSON_THROW_ON_ERROR);
 $extra=[[5,'home','خانه'],[7,'lab','آزمایشگاه'],[9,'shop','فروشگاه'],[10,'learn','آموزش'],[13,'contact','تماس با ما'],[14,'about','درباره ما']];
 $all=$data['pages'];
 foreach($extra as[$id,$slug,$title])$all[]=['id'=>$id,'slug'=>$slug,'title'=>$title,'parent'=>0,'body'=>'<!-- wp:paragraph --><p>محیط ساختگی آزمون؛ بدون دادهٔ مشتری.</p><!-- /wp:paragraph -->'];
 usort($all,fn($a,$b)=>$a['id']<=>$b['id']);
 foreach($all as$p){$id=wp_insert_post(wp_slash(['import_id'=>$p['id'],'post_type'=>'page','post_status'=>'publish','post_parent'=>$p['parent'],'post_name'=>$p['slug'],'post_title'=>$p['title'],'post_excerpt'=>'Synthetic fixture only','post_content'=>$p['body']]),true);if($id!==$p['id'])throw new RuntimeException('Exact fixture allocation failed');}
 update_option('blog_public',0);update_option('show_on_front','page');update_option('page_on_front',5);update_option('woocommerce_shop_page_id',9);
 update_option('permalink_structure','/%postname%/');update_option('WPLANG','fa_IR');
 $menu=wp_create_nav_menu('Synthetic primary');foreach([5,8,10,7,9,14,13]as$id)wp_update_nav_menu_item($menu,0,['menu-item-object-id'=>$id,'menu-item-object'=>'page','menu-item-type'=>'post_type','menu-item-status'=>'publish']);set_theme_mod('nav_menu_locations',['primary'=>$menu]);
}else if($phase==='apply'){
 $m=json_decode(file_get_contents($root.'manifest.json'),true);
 foreach($m['targets']as$t){if(hash('sha256',get_post($t['id'])->post_content)!==$t['expected_content_sha256'])throw new RuntimeException('Fixture body drift');wp_update_post(wp_slash(['ID'=>$t['id'],'post_content'=>file_get_contents($root.$t['content_file'])]),true);}
 update_option('tn_recaptcha_enabled','yes');update_option('tn_recaptcha_site_key',getenv('TN_FIXTURE_PASSWORD'));update_option('tn_recaptcha_secret_key',getenv('TN_FIXTURE_PASSWORD'));
}else if($phase==='verify'){
 global$wpdb;$ids=$wpdb->get_col($wpdb->prepare("SELECT ID FROM {$wpdb->posts} WHERE post_type=%s",'tn_ticket'));
 if(count($ids)!==1)throw new RuntimeException('Exactly one synthetic ticket required');
 $id=(int)$ids[0];$p=get_post($id);
 if($p->post_status!=='private'||get_post_meta($id,'_tn_service_context',true)!=='general-network'||get_post_meta($id,'_tn_request_kind',true)!=='service'||get_post_meta($id,'_tn_ticket_state',true)!=='open'||get_post_meta($id,'_tn_email',true)!=='fixture@example.invalid'||count(get_post_meta($id,'_tn_thread',true))!==1)throw new RuntimeException('Canonical ticket persistence mismatch');
 wp_delete_post($id,true);
 $wpdb->query($wpdb->prepare("DELETE FROM {$wpdb->options} WHERE option_name LIKE %s OR option_name LIKE %s",$wpdb->esc_like('_transient_tn_service_receipt_').'%',$wpdb->esc_like('_transient_timeout_tn_service_receipt_').'%'));
 if($wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->posts} WHERE post_type='tn_ticket'")!=='0')throw new RuntimeException('Owned ticket cleanup failed');
 echo 'TN_P94_PERSISTENCE '.wp_json_encode(['status'=>'PASS','private_canonical_ticket'=>true,'context'=>'general-network','records_created'=>1,'owned_records_removed'=>true,'production_mutations'=>0])."\n";
}else if($phase==='diagnostic'){
 global$wpdb;$beforeRow=$wpdb->get_row("SELECT option_value,autoload FROM {$wpdb->options} WHERE option_name='blog_public'",ARRAY_A);
 $before=get_option('blog_public');$robots=apply_filters('wp_robots',[]);$site=wp_sitemaps_get_server();$normal=$site->sitemaps_enabled();
 update_option('blog_public',1);$open=apply_filters('wp_robots',[]);$sitemap_open=$site->sitemaps_enabled();update_option('blog_public',$before);
 $afterRow=$wpdb->get_row("SELECT option_value,autoload FROM {$wpdb->options} WHERE option_name='blog_public'",ARRAY_A);if($afterRow!==$beforeRow)throw new RuntimeException('Persisted visibility option restoration failed');
 echo 'TN_P94_NOINDEX_FIXTURE '.wp_json_encode(['blog_public_original'=>$before,'robots_original'=>$robots,'sitemap_original'=>$normal,'synthetic_public_1_robots'=>$open,'synthetic_public_1_sitemap'=>$sitemap_open,'restored_persisted_row'=>$afterRow===$beforeRow,'restored_value'=>(string)get_option('blog_public')===(string)$before,'production_equivalence'=>'NOT_PROVEN'])."\n";
}else throw new RuntimeException('Unknown fixture phase');
}catch(Throwable $e){echo 'TN_P94_FIXTURE_FAIL '.wp_json_encode(['class'=>get_class($e),'label'=>$e->getMessage()])."\n";exit(1);}
