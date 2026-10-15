<?php
// Explicit owner-authorized public inquiry catalog. Never turns a product into a sale.
if(!defined('WP_CLI')||!WP_CLI||!current_user_can('manage_woocommerce')){throw new RuntimeException('CLI commerce operator required');}
if(home_url()!=='https://tehnet.ir'||wp_get_environment_type()!=='production'){throw new RuntimeException('Wrong target');}
$manifest=json_decode(file_get_contents('/tmp/tn-store-review/catalog.json'),true,512,JSON_THROW_ON_ERROR);
if(hash_file('sha256','/tmp/tn-store-review/catalog.json')!=='03cc4da8ce057cf99642a158d0fcc02f3964c8c3e86518189359105a0854f19b'){throw new RuntimeException('Manifest changed');}
$renames=[17989=>'پریز برق قرمز لگراند — نیازمند تأیید مدل',17982=>'پریز برق سفید لگراند — نیازمند تأیید مدل',17941=>'ماژول کیستون پهن — نوع پورت نیازمند تأیید',17935=>'ماژول کیستون باریک — نوع پورت نیازمند تأیید'];
$plan=[];
foreach($manifest['products'] as $row){
    $id=wc_get_product_id_by_sku($row['sku']);$p=wc_get_product($id);
    if(!$p||$p->get_meta('_tn_source_key')!==$row['source_key']||$p->get_price()!==''||(string)$p->get_stock_quantity()!=='0'||$p->get_meta('_tn_sale_approved')!=='no'){throw new RuntimeException('Product changed; preserve edits');}
    if($p->get_meta('_tn_public_inquiry')==='yes'){continue;}
    if($p->get_status()!=='draft'||$p->get_name()!==$row['name']){throw new RuntimeException('Human edits require separate review');}
    $title=$renames[$row['source_id']]??$row['name'];
    if(in_array('source-sku-brand-conflict',$row['review_flags'],true)){$title=preg_replace('/(?:لگراند|نگزنس|Legrand|Nexans)/ui','',$title).' — برند نیازمند تأیید';}
    $title=str_replace('052 ','',$title);
    $plan[]=[$p,$title];
}
global $wpdb;$wpdb->query('START TRANSACTION');
try{
    $before=['coming_soon'=>get_option('woocommerce_coming_soon'),'store_pages_only'=>get_option('woocommerce_store_pages_only'),'shop_content'=>get_post(wc_get_page_id('shop'))->post_content,'products'=>[]];
    foreach($plan as [$p,$title]){
        $before['products'][]=['id'=>$p->get_id(),'title'=>$p->get_name(),'status'=>$p->get_status()];
        $p->update_meta_data('_tn_source_observed_title',$p->get_name());$p->update_meta_data('_tn_public_inquiry','yes');
        $p->update_meta_data('_tn_public_inquiry_at',gmdate('c'));$p->set_name(trim($title));$p->set_status('publish');$p->set_catalog_visibility('visible');$p->save();
        if($p->is_purchasable()){throw new RuntimeException('Inquiry product unexpectedly purchasable');}
    }
    if($plan){add_option('tn_public_inquiry_release_20261015',$before,'',false);}
    $shop=wc_get_page_id('shop');
    wp_update_post(['ID'=>$shop,'post_content'=>'<h2>تجهیزات شبکه تهران نتورک</h2><p>کابل شبکه، کیستون، سوکت و تجهیزات پسیو را بررسی و مقایسه کنید. برای انتخاب مدل مناسب و دریافت پیش‌فاکتور، از صفحه هر کالا استعلام بگیرید.</p><p><strong>قیمت، موجودی، مدل دقیق و شرایط تأمین پیش از تأیید سفارش بررسی می‌شوند.</strong></p>']);
    update_option('woocommerce_coming_soon','no');
    $wpdb->query('COMMIT');
    echo wp_json_encode(['published_inquiry_only'=>count($plan),'total_catalog'=>25,'checkout_enabled'=>false,'homepage_untouched'=>true,'visibility'=>'public catalog, no verified offers']);
}catch(Throwable $e){$wpdb->query('ROLLBACK');throw $e;}
