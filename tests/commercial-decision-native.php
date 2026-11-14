<?php
try {
if(!defined('WP_CLI')||!WP_CLI||wp_get_environment_type()!=='staging'||home_url('/')!=='http://localhost:18085/'||!DISABLE_WP_CRON||!WP_HTTP_BLOCK_EXTERNAL)throw new RuntimeException('Owned isolated cloud fixture required');
$phase=$args[0]??'seed';$root='/src/content/commercial-decision-2026-11-08-v2/';$m=json_decode(file_get_contents($root.'manifest.json'),true,512,JSON_THROW_ON_ERROR);
$checks=[];$ck=static function($yes,$label)use(&$checks){if(!$yes)throw new RuntimeException($label);$checks[]=$label;};
if($phase==='seed'){
 $data=json_decode(file_get_contents('/src/tests/fixtures/decision-v2-public-pages.json'),true,512,JSON_THROW_ON_ERROR);
 foreach($data['pages']as$p){$id=wp_insert_post(wp_slash(['import_id'=>$p['id'],'post_type'=>'page','post_status'=>'publish','post_parent'=>$p['parent'],'post_name'=>$p['slug'],'post_title'=>$p['title'],'post_excerpt'=>$p['excerpt']??'Synthetic fixture','post_content'=>$p['body']]),true);$ck($id===$p['id'],'Exact public fixture allocation '.$p['id']);}
 update_option('blog_public',0);update_option('show_on_front','page');update_option('page_on_front',5);update_option('page_for_posts',69);update_option('woocommerce_shop_page_id',9);update_option('woocommerce_cart_page_id',107);update_option('woocommerce_checkout_page_id',109);update_option('woocommerce_myaccount_page_id',110);
 update_option('permalink_structure','/%postname%/');update_option('WPLANG','fa_IR');
 $menu=wp_create_nav_menu('Synthetic primary');foreach([5,8,6,7,9,10,11]as$id)wp_update_nav_menu_item($menu,0,['menu-item-object-id'=>$id,'menu-item-object'=>'page','menu-item-type'=>'post_type','menu-item-status'=>'publish']);set_theme_mod('nav_menu_locations',['primary'=>$menu]);
}elseif($phase==='prepare'){
 $ck(has_shortcode((string)get_post_field('post_content',196),'tn_support_ticket'),'Actual public support page retains canonical receipt shortcode');
 update_option('tn_recaptcha_enabled','yes');update_option('tn_recaptcha_site_key',getenv('TN_FIXTURE_PASSWORD'));update_option('tn_recaptcha_secret_key',getenv('TN_FIXTURE_PASSWORD'));
 $before=[];foreach($m['targets']as$t){$p=get_post($t['id']);$ck(hash('sha256',$p->post_content)===$t['expected_content_sha256'],'Exact live body baseline '.$t['id']);$ck(hash('sha256',$p->post_excerpt)===$t['expected_excerpt_sha256'],'Exact live excerpt baseline '.$t['id']);$before[$t['id']]=['title'=>$p->post_title,'excerpt'=>$p->post_excerpt,'body'=>$p->post_content,'meta'=>get_post_meta($p->ID)];}
 file_put_contents('/lab/decision-before-private.json',wp_json_encode($before));chmod('/lab/decision-before-private.json',0600);
 foreach([...$m['targets'],...$m['pages']]as$t){$body=file_get_contents($root.$t['content_file']);$ck(serialize_blocks(parse_blocks($body))===$body,'Native Gutenberg parse/serialize '.$t['content_file']);$ck(wp_kses_post($body)===$body,'Native KSES '.$t['content_file']);}
}elseif($phase==='baseline-routes'){
 global$wpdb;$original=$wpdb->get_row("SELECT option_value,autoload FROM {$wpdb->options} WHERE option_name='rewrite_rules'",ARRAY_A);file_put_contents('/lab/rewrite-before-private.json',wp_json_encode($original));chmod('/lab/rewrite-before-private.json',0600);
 $ck(url_to_postid(home_url('/lab/voice-network-checklist/'))===0,'Reproduced generic tn_lab shadow before bounded route repair');
 $rows=$wpdb->get_results("SELECT * FROM {$wpdb->prefix}woocommerce_sessions ORDER BY session_id",ARRAY_A);$owned=[];foreach($rows as$row)$owned[$row['session_id']]=hash('sha256',serialize($row));file_put_contents('/lab/sessions-before-private.json',wp_json_encode($owned));chmod('/lab/sessions-before-private.json',0600);
}elseif($phase==='accept'){
 global$wpdb;$original=json_decode(file_get_contents('/lab/rewrite-before-private.json'),true);$ck($wpdb->get_row("SELECT option_value,autoload FROM {$wpdb->options} WHERE option_name='rewrite_rules'",ARRAY_A)===$original,'Stored rewrite_rules unchanged');
 foreach([76=>'gns3-mikrotik',188=>'wireguard-mtu',207=>'voice-network-checklist']as$id=>$slug)$ck(url_to_postid(home_url('/lab/'.$slug.'/'))===$id,'Actual WordPress resolver reaches known public Lab page '.$id);
 $types=new TehNet_Core_Content_Types();$collision=wp_insert_post(['post_type'=>'tn_lab','post_status'=>'draft','post_name'=>'voice-network-checklist','post_title'=>'Synthetic collision probe'],true);$ck(!is_wp_error($collision),'Owned CPT collision fixture');
 try{$rules=$types->existing_lab_page_rules(['unrelated/?$'=>'index.php?name=unrelated']);$ck(!isset($rules['lab/voice-network-checklist/?$'])&&$rules['unrelated/?$']==='index.php?name=unrelated','Same-slug CPT is not silently masked; unrelated rule retained');}finally{wp_delete_post((int)$collision,true);}

 $before=json_decode(file_get_contents('/lab/decision-before-private.json'),true);foreach($m['targets']as$t){$p=get_post($t['id']);$ck($p->post_content===file_get_contents($root.$t['content_file']),'Canonical publisher saved exact body '.$t['id']);$ck($p->post_title===($t['title']??$before[$t['id']]['title']),'Scoped title '.$t['id']);$ck($p->post_excerpt===($t['excerpt']??$before[$t['id']]['excerpt']),'Scoped excerpt '.$t['id']);$ck(get_post_meta($p->ID)===$before[$t['id']]['meta'],'Owner meta unchanged '.$t['id']);preg_match_all('/id="([^"]+)"/',$before[$t['id']]['body'],$a);foreach($a[1]as$anchor)$ck(str_contains($p->post_content,'id="'.$anchor.'"'),'Preserved old anchor '.$anchor);}
 foreach($m['pages']as$t){$p=get_page_by_path(($t['parent_id']?'services/':'').$t['slug']);$ck($p&&$p->post_status==='publish'&&$p->post_content===file_get_contents($root.$t['content_file']),'Exact new Gutenberg page '.$t['key']);}
 $ck((string)get_option('blog_public')==='0','Global noindex remains0');
}elseif($phase==='verify-ticket'){
 global$wpdb;$ids=$wpdb->get_col("SELECT ID FROM {$wpdb->posts} WHERE post_type='tn_ticket'");$ck(count($ids)===1,'Exactly one synthetic canonical ticket');
 $id=(int)$ids[0];$ck(get_post_status($id)==='private'&&get_post_meta($id,'_tn_service_context',true)==='server-scoping'&&get_post_meta($id,'_tn_request_kind',true)==='service'&&get_post_meta($id,'_tn_ticket_state',true)==='open'&&get_post_meta($id,'_tn_email',true)==='fixture@example.invalid'&&count(get_post_meta($id,'_tn_thread',true))===1,'Server request persisted in existing private ticket infrastructure');
 wp_delete_post($id,true);$wpdb->query($wpdb->prepare("DELETE FROM {$wpdb->options} WHERE option_name LIKE %s OR option_name LIKE %s",$wpdb->esc_like('_transient_tn_service_receipt_').'%',$wpdb->esc_like('_transient_timeout_tn_service_receipt_').'%'));
 $ck($wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->posts} WHERE post_type='tn_ticket'")==='0','Owned ticket removed');
}elseif($phase==='cleanup-http-state'){
 global$wpdb;
 define('TN_GROWTH_LIBRARY_ONLY',true);require '/src/ops/migrate-growth-content.php';
 $j=json_decode(file_get_contents('/lab/private-release/content-journal-private.json'),true,512,JSON_THROW_ON_ERROR);
 $rc=new ReflectionClass(TehNet_Growth_Content_Migration::class);$instance=$rc->newInstanceWithoutConstructor();$p=$rc->getProperty('manifest');$p->setAccessible(true);$p->setValue($instance,['updates'=>array_map(static fn($r)=>['id'=>$r['id']],$m['targets'])]);
 $method=$rc->getMethod('protectedState');$method->setAccessible(true);$current=$method->invoke($instance,$j['page_ids']);$diff=[];foreach($current as$key=>$value)if(($j['protected'][$key]??null)!==$value)$diff[]=$key;
 echo 'TN_DECISION_PROTECTED_DIFF '.wp_json_encode(['changed_keys'=>$diff,'original_missing_keys'=>array_values(array_diff($diff,array_keys($j['protected']))),'production_mutations'=>0])."\n";
 $table=$wpdb->prefix.'woocommerce_sessions';$ck(!$diff||$diff===[$table],'Only test-owned anonymous Woo session state may require cleanup; no guard exclusion');
 $old=json_decode(file_get_contents('/lab/sessions-before-private.json'),true,512,JSON_THROW_ON_ERROR);$rows=$wpdb->get_results("SELECT * FROM `$table` ORDER BY session_id",ARRAY_A);$added=[];$found=[];
 foreach($rows as$row){$id=$row['session_id'];if(array_key_exists($id,$old)){$ck(hash('sha256',serialize($row))===$old[$id],'Original Woo session row unchanged');$found[$id]=true;}else $added[]=(int)$id;}
 $ck(count($found)===count($old)&&count($added)<=100,'Original sessions preserved and owned fixture delta bounded');
 foreach($added as$id)$ck($wpdb->delete($table,['session_id'=>$id])===1,'Delete only added session in closed synthetic fixture');
 $ck($method->invoke($instance,$j['page_ids'])===$j['protected'],'All canonical protected fingerprints exactly restored after owned HTTP cleanup');
 echo 'TN_DECISION_OWNED_HTTP_CLEANUP '.wp_json_encode(['new_synthetic_wc_sessions_removed'=>count($added),'original_rows_preserved'=>true,'production_mutations'=>0])."\n";
}elseif($phase==='rollback-accept'){
 global$wpdb;$original=json_decode(file_get_contents('/lab/rewrite-before-private.json'),true);$ck($wpdb->get_row("SELECT option_value,autoload FROM {$wpdb->options} WHERE option_name='rewrite_rules'",ARRAY_A)===$original,'Rollback preserves stored rewrite_rules byte value/autoload');$ck(url_to_postid(home_url('/lab/voice-network-checklist/'))===0,'Original Lab resolver behavior restored with owned file rollback');

 $before=json_decode(file_get_contents('/lab/decision-before-private.json'),true);foreach($m['targets']as$t){$p=get_post($t['id']);$ck($p->post_content===$before[$p->ID]['body']&&$p->post_title===$before[$p->ID]['title']&&$p->post_excerpt===$before[$p->ID]['excerpt']&&get_post_meta($p->ID)===$before[$p->ID]['meta'],'Restored exact owner fields/meta '.$p->ID);}
 foreach($m['pages']as$t){$p=get_page_by_path(($t['parent_id']?'services/':'').$t['slug']);$ck($p&&$p->post_status==='draft','Rollback drafts owned new page '.$t['key']);}
 $ck((string)get_option('blog_public')==='0','Rollback keeps global noindex0');
}else throw new RuntimeException('Unknown phase');
echo 'TN_DECISION_NATIVE '.wp_json_encode(['phase'=>$phase,'status'=>'PASS','runtime'=>['WordPress'=>$GLOBALS['wp_version'],'PHP'=>PHP_VERSION,'Core'=>defined('TEHNET_CORE_VERSION')?TEHNET_CORE_VERSION:'NONE','database'=>$GLOBALS['wpdb']->db_version()],'checks'=>count($checks),'labels'=>$checks,'production_mutations'=>0])."\n";
}catch(Throwable$e){echo 'TN_DECISION_NATIVE '.wp_json_encode(['status'=>'FAIL','phase'=>$phase??'unknown','label'=>$e->getMessage()])."\n";exit(1);}
