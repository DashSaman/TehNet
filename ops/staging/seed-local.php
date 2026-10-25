<?php
if(wp_get_environment_type()!=='local'){throw new RuntimeException('Local sandbox only');}
$map=['cart'=>'سبد خرید','checkout'=>'تسویه‌حساب','myaccount'=>'حساب کاربری','shop'=>'فروشگاه تجهیزات شبکه'];
foreach($map as $key=>$title){$id=wc_get_page_id($key);if($id>0){wp_update_post(['ID'=>$id,'post_title'=>$title,'post_status'=>'publish','post_date'=>current_time('mysql'),'post_date_gmt'=>current_time('mysql',true)]);}}
foreach(['home'=>'خانه','learn'=>'آموزش','lab'=>'لاب','services'=>'خدمات شبکه','about'=>'درباره ما','contact'=>'تماس با ما'] as $slug=>$title){
    $path='/content-pages/'.$slug.'.html';
    if(!is_readable($path)){continue;}
    $page=get_page_by_path($slug);
    $id=wp_insert_post(['ID'=>$page?$page->ID:0,'post_type'=>'page','post_status'=>'publish','post_date'=>current_time('mysql'),'post_date_gmt'=>current_time('mysql',true),'post_name'=>$slug,'post_title'=>$title,'post_content'=>str_replace('https://tehnet.ir','http://localhost:18083',file_get_contents($path))]);
    if($slug==='home'){update_option('show_on_front','page');update_option('page_on_front',$id);}
}
$menu=wp_get_nav_menu_object('TehNet Local');$menu_id=$menu?$menu->term_id:wp_create_nav_menu('TehNet Local');
if(!wp_get_nav_menu_items($menu_id)){
    foreach(['/shop/'=>'فروشگاه','/services/'=>'خدمات','/learn/'=>'آموزش','/my-account/'=>'حساب کاربری','/cart/'=>'سبد خرید'] as $path=>$title){wp_update_nav_menu_item($menu_id,0,['menu-item-title'=>$title,'menu-item-url'=>home_url($path),'menu-item-status'=>'publish','menu-item-type'=>'custom']);}
}
$locations=get_theme_mod('nav_menu_locations',[]);$locations['primary']=$menu_id;set_theme_mod('nav_menu_locations',$locations);
update_option('woocommerce_enable_myaccount_registration','yes');
update_option('woocommerce_coming_soon','no');
update_option('woocommerce_price_num_decimals','0');
flush_rewrite_rules();
echo "LOCAL_CONTENT_SEEDED=PASSED\n";
