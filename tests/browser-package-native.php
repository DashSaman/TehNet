<?php
/* Browser-package fixture seed: decision-v2 pages + b2b/support production-truth pages. */
if(!defined('WP_CLI')||!WP_CLI||wp_get_environment_type()!=='staging'||home_url('/')!=='http://localhost:18085/')throw new RuntimeException('Owned isolated fixture required');
$phase=$args[0]??'seed';
$checks=[];$ck=static function($yes,$label)use(&$checks){if(!$yes)throw new RuntimeException($label);$checks[]=$label;};
if($phase==='seed'){
    /* Delete default WP content so import_id allocation reaches the production-truth IDs. */
    global $wpdb;
    $wpdb->query("DELETE FROM {$wpdb->posts} WHERE ID <= 100 AND post_type IN ('post','page')");
    $wpdb->query("DELETE FROM {$wpdb->postmeta} WHERE post_id <= 100");
    $wpdb->query("ALTER TABLE {$wpdb->posts} AUTO_INCREMENT = 5");
    $dec=json_decode(file_get_contents('/src/tests/fixtures/decision-v2-public-pages.json'),true,512,JSON_THROW_ON_ERROR);
    foreach($dec['pages']as$p){
        $id=wp_insert_post(wp_slash(['import_id'=>$p['id'],'post_type'=>'page','post_status'=>'publish','post_parent'=>$p['parent'],'post_name'=>$p['slug'],'post_title'=>$p['title'],'post_excerpt'=>$p['excerpt']??'Synthetic fixture','post_content'=>$p['body']]),true);
        $ck($id===$p['id'],'Exact public fixture allocation '.$p['id']);
    }
    $extra=json_decode(file_get_contents('/src/tests/fixtures/browser-journey-extra-pages.json'),true,512,JSON_THROW_ON_ERROR);
    foreach($extra['pages']as$p){
        $id=wp_insert_post(wp_slash(['import_id'=>$p['id'],'post_type'=>'page','post_status'=>'publish','post_parent'=>$p['parent'],'post_name'=>$p['slug'],'post_title'=>$p['title'],'post_content'=>$p['body']]),true);
        $ck($id===$p['id'],'Exact b2b/support fixture allocation '.$p['id']);
        $ck(hash('sha256',get_post($p['id'])->post_content)===$p['body_sha256'],'Production-truth body hash '.$p['id']);
    }
    update_option('blog_public',0);update_option('show_on_front','page');update_option('page_on_front',5);update_option('page_for_posts',69);
    update_option('woocommerce_shop_page_id',9);update_option('woocommerce_cart_page_id',107);update_option('woocommerce_checkout_page_id',109);update_option('woocommerce_myaccount_page_id',110);
    update_option('permalink_structure','/%postname%/');update_option('WPLANG','fa_IR');
    $menu=wp_create_nav_menu('Synthetic primary');foreach([5,8,6,7,9,10,11]as$id)wp_update_nav_menu_item($menu,0,['menu-item-object-id'=>$id,'menu-item-object'=>'page','menu-item-type'=>'post_type','menu-item-status'=>'publish']);set_theme_mod('nav_menu_locations',['primary'=>$menu]);
    echo 'SEED_OK ',count($checks),"\n";
}elseif($phase==='verify'){
    /* Journey targets exist with production-truth bodies; shortcodes registered. */
    foreach([33=>'709c49b6d2e0cffa4d95c3709877ff06d40daa5223a3f39894881b7a429cbe5e',191=>'df89d9251a68595cbfc002d0bc9a2d697979f8ebeeca4b8d338cdd2ef25a9df3',192=>'c03b121aa300a0139a9e4226c2db60dc7d31d8fbdc3095d309901391aa776693']as$id=>$h){
        $p=get_post($id);$ck($p&&$p->post_status==='publish','Journey target publish '.$id);
        $ck(hash('sha256',$p->post_content)===$h,'Journey target body hash '.$id);
    }
    $ck(shortcode_exists('tn_b2b_quote'),'tn_b2b_quote registered');
    $ck(shortcode_exists('tn_support_ticket'),'tn_support_ticket registered');
    $ck(has_shortcode((string)get_post_field('post_content',33),'tn_service_request')||str_contains((string)get_post_field('post_content',33),'tn_service_context'),'Page 33 carries the real CTA');
    echo 'VERIFY_OK ',count($checks),"\n";
}
