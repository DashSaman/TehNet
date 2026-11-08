<?php
declare(strict_types=1);
try {
$phase=$args[0]??'seed';$root='/src/content/commercial-decision-2026-11-08-v2/';$m=json_decode(file_get_contents($root.'manifest.json'),true,512,JSON_THROW_ON_ERROR);
$checks=[];$ck=static function($yes,$label)use(&$checks){if(!$yes)throw new RuntimeException($label);$checks[]=$label;};
if($phase==='seed'){
 $data=json_decode(file_get_contents('/src/tests/fixtures/decision-v2-public-pages.json'),true,512,JSON_THROW_ON_ERROR);
 foreach($data['pages']as$p){$id=wp_insert_post(wp_slash(['import_id'=>$p['id'],'post_type'=>'page','post_status'=>'publish','post_parent'=>$p['parent'],'post_name'=>$p['slug'],'post_title'=>$p['title'],'post_excerpt'=>$p['excerpt']??'Synthetic fixture','post_content'=>$p['body']]),true);$ck($id===$p['id'],'Exact public fixture allocation '.$p['id']);}
 update_option('blog_public',0);update_option('show_on_front','page');update_option('page_on_front',5);update_option('page_for_posts',69);update_option('woocommerce_shop_page_id',9);update_option('woocommerce_cart_page_id',107);update_option('woocommerce_checkout_page_id',109);update_option('woocommerce_myaccount_page_id',110);
 update_option('permalink_structure','/%postname%/');update_option('WPLANG','fa_IR');
 $menu=wp_create_nav_menu('Synthetic primary');foreach([5,8,6,7,9,10,11]as$id)wp_update_nav_menu_item($menu,0,['menu-item-object-id'=>$id,'menu-item-object'=>'page','menu-item-type'=>'post_type','menu-item-status'=>'publish']);set_theme_mod('nav_menu_locations',['primary'=>$menu]);
}elseif($phase==='prepare'){
 update_option('tn_recaptcha_enabled','yes');update_option('tn_recaptcha_site_key',getenv('TN_FIXTURE_PASSWORD'));update_option('tn_recaptcha_secret_key',getenv('TN_FIXTURE_PASSWORD'));
 $before=[];foreach($m['targets']as$t){$p=get_post($t['id']);$ck(hash('sha256',$p->post_content)===$t['expected_content_sha256'],'Exact live body baseline '.$t['id']);$ck(hash('sha256',$p->post_excerpt)===$t['expected_excerpt_sha256'],'Exact live excerpt baseline '.$t['id']);$before[$t['id']]=['title'=>$p->post_title,'excerpt'=>$p->post_excerpt,'body'=>$p->post_content,'meta'=>get_post_meta($p->ID)];}
 file_put_contents('/lab/decision-before-private.json',wp_json_encode($before));chmod('/lab/decision-before-private.json',0600);
 foreach([...$m['targets'],...$m['pages']]as$t){$body=file_get_contents($root.$t['content_file']);$ck(serialize_blocks(parse_blocks($body))===$body,'Native Gutenberg parse/serialize '.$t['content_file']);$ck(wp_kses_post($body)===$body,'Native KSES '.$t['content_file']);}
}elseif($phase==='accept'){
 $before=json_decode(file_get_contents('/lab/decision-before-private.json'),true);foreach($m['targets']as$t){$p=get_post($t['id']);$ck($p->post_content===file_get_contents($root.$t['content_file']),'Canonical publisher saved exact body '.$t['id']);$ck($p->post_title===($t['title']??$before[$t['id']]['title']),'Scoped title '.$t['id']);$ck($p->post_excerpt===($t['excerpt']??$before[$t['id']]['excerpt']),'Scoped excerpt '.$t['id']);$ck(get_post_meta($p->ID)===$before[$t['id']]['meta'],'Owner meta unchanged '.$t['id']);preg_match_all('/id="([^"]+)"/',$before[$t['id']]['body'],$a);foreach($a[1]as$anchor)$ck(str_contains($p->post_content,'id="'.$anchor.'"'),'Preserved old anchor '.$anchor);}
 foreach($m['pages']as$t){$p=get_page_by_path(($t['parent_id']?'services/':'').$t['slug']);$ck($p&&$p->post_status==='publish'&&$p->post_content===file_get_contents($root.$t['content_file']),'Exact new Gutenberg page '.$t['key']);}
 $ck((string)get_option('blog_public')==='0','Global noindex remains0');
}elseif($phase==='verify-ticket'){
 global$wpdb;$ids=$wpdb->get_col("SELECT ID FROM {$wpdb->posts} WHERE post_type='tn_ticket'");$ck(count($ids)===1,'Exactly one synthetic canonical ticket');
 $id=(int)$ids[0];$ck(get_post_status($id)==='private'&&get_post_meta($id,'_tn_service_context',true)==='server-scoping'&&get_post_meta($id,'_tn_request_kind',true)==='service'&&get_post_meta($id,'_tn_ticket_state',true)==='open'&&get_post_meta($id,'_tn_email',true)==='fixture@example.invalid'&&count(get_post_meta($id,'_tn_thread',true))===1,'Server request persisted in existing private ticket infrastructure');
 wp_delete_post($id,true);$wpdb->query($wpdb->prepare("DELETE FROM {$wpdb->options} WHERE option_name LIKE %s OR option_name LIKE %s",$wpdb->esc_like('_transient_tn_service_receipt_').'%',$wpdb->esc_like('_transient_timeout_tn_service_receipt_').'%'));
 $ck($wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->posts} WHERE post_type='tn_ticket'")==='0','Owned ticket removed');
}elseif($phase==='rollback-accept'){
 $before=json_decode(file_get_contents('/lab/decision-before-private.json'),true);foreach($m['targets']as$t){$p=get_post($t['id']);$ck($p->post_content===$before[$p->ID]['body']&&$p->post_title===$before[$p->ID]['title']&&$p->post_excerpt===$before[$p->ID]['excerpt']&&get_post_meta($p->ID)===$before[$p->ID]['meta'],'Restored exact owner fields/meta '.$p->ID);}
 foreach($m['pages']as$t){$p=get_page_by_path(($t['parent_id']?'services/':'').$t['slug']);$ck($p&&$p->post_status==='draft','Rollback drafts owned new page '.$t['key']);}
 $ck((string)get_option('blog_public')==='0','Rollback keeps global noindex0');
}else throw new RuntimeException('Unknown phase');
echo 'TN_DECISION_NATIVE '.wp_json_encode(['phase'=>$phase,'status'=>'PASS','checks'=>count($checks),'labels'=>$checks,'production_mutations'=>0])."\n";
}catch(Throwable$e){echo 'TN_DECISION_NATIVE '.wp_json_encode(['status'=>'FAIL','phase'=>$phase??'unknown','label'=>$e->getMessage()])."\n";exit(1);}
