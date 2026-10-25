<?php
/** Read-only WP-CLI guard. No customer details or option secrets leave the host. */
if(!defined('WP_CLI')||!WP_CLI||!current_user_can('manage_options')||home_url('/')!=='https://tehnet.ir/')throw new RuntimeException('Authorized production TehNet CLI required');
function tn_ux_hash($value):string{return hash('sha256',wp_json_encode($value));}
$products=[];$published=[];$purchasable=[];$models=0;$spins=0;
foreach(get_posts(['post_type'=>'product','post_status'=>'any','numberposts'=>-1,'orderby'=>'ID','order'=>'ASC'])as $post){
    $meta=get_post_meta($post->ID);ksort($meta);$products[$post->ID]=['body'=>tn_ux_hash([$post->post_title,$post->post_content,$post->post_excerpt,$post->post_status]),'meta'=>tn_ux_hash($meta)];
    if($post->post_status!=='publish')continue;$published[]=$post->ID;$product=wc_get_product($post->ID);
    if($product->is_purchasable())$purchasable[]=$post->ID;
    if((new TehNet_Store_Product_Evidence())->model($product))$models++;
    if((new TehNet_Store_Product_Visuals())->spin_frames($product))$spins++;
}
$options=[];foreach(['blog_public','home','siteurl','stylesheet','template','show_on_front','page_on_front','page_for_posts','woocommerce_currency','woocommerce_shop_page_id','woocommerce_cart_page_id','woocommerce_checkout_page_id','woocommerce_myaccount_page_id','tn_store_settings','woocommerce_cod_settings','woocommerce_bacs_settings','woocommerce_cheque_settings','woocommerce_tn_zarinpal_sandbox_settings']as $key)$options[$key]=get_option($key);
$menus=[];$menuCount=0;foreach(wp_get_nav_menus()as $menu){$items=wp_get_nav_menu_items($menu->term_id);$menus[$menu->term_id]=$items;$menuCount+=count($items?:[]);}ksort($menus);
$home=get_post((int)get_option('page_on_front'));
$orders=wc_get_orders(['limit'=>-1,'return'=>'ids','orderby'=>'ID','order'=>'ASC','status'=>array_keys(wc_get_order_statuses())]);sort($orders);
$state=['products'=>$products,'published_product_ids'=>$published,'purchasable_ids'=>$purchasable,'real_models'=>$models,'real_spins'=>$spins,'options_sha256'=>tn_ux_hash($options),'blog_public'=>get_option('blog_public'),'menu_sha256'=>tn_ux_hash($menus),'menu_items'=>$menuCount,'home_body_sha256'=>hash('sha256',$home->post_content),'orders_count'=>count($orders),'order_ids_sha256'=>tn_ux_hash($orders),'commerce_gates'=>['environment'=>wp_get_environment_type(),'erp_ready'=>(new TehNet_Store_ERP())->ready(),'sandbox_enabled'=>TehNet_Store_Zarinpal_Sandbox::enabled()]];
if(count($published)!==25||$purchasable||$state['blog_public']!=='0'||$state['commerce_gates']['erp_ready']||$state['commerce_gates']['sandbox_enabled'])throw new RuntimeException('Unexpected production inventory or commerce gates; inspect before release');
echo wp_json_encode($state);
