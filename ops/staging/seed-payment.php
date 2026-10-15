<?php
/** Explicit synthetic checkout fixture. Never run on a real site/company. */
if (wp_get_environment_type()!=='local' || !defined('TEHNET_ERP_SANDBOX') || TEHNET_ERP_SANDBOX!==true || getenv('TEHNET_ERP_STORE_ID')!=='tehnet-local') {
    throw new RuntimeException('Only the isolated local ERP sandbox may be used');
}
$sku='TN-SANDBOX-WOO-METER';$id=wc_get_product_id_by_sku($sku);
$p=$id?wc_get_product($id):new WC_Product_Simple();
if ($id && $p->get_meta('_tn_sandbox_fixture')!=='yes') { throw new RuntimeException('Existing SKU is not owned by this fixture'); }
if (!$id) {
    $p->set_name('نمونه آزمایش خرید کابل متری — تحویلی ندارد');$p->set_slug('synthetic-checkout-meter');$p->set_sku($sku);$p->set_status('publish');
    $p->set_description('این محصول صرفاً برای آزمون محلی پرداخت و انبار ساختگی است. فروشی انجام نمی‌شود و کالایی ارسال نخواهد شد.');
    $p->set_tax_status('none');$p->set_backorders('no');
    foreach (['_tn_sandbox_fixture'=>'yes','_tn_erp_sku'=>'TN-SANDBOX-CABLE','_tn_erp_uom'=>'Meter','_tn_sale_approved'=>'yes','_tn_sale_unit'=>'meter','_tn_min_quantity'=>'0.5'] as $k=>$v) {$p->update_meta_data($k,$v);}
    $p->save();
}
(new TehNet_Store_ERP())->sync_product($p->get_id());
$p=wc_get_product($p->get_id());
update_option('woocommerce_tn_zarinpal_sandbox_settings',['enabled'=>'yes']);
update_option('woocommerce_enable_guest_checkout','yes');
update_option('woocommerce_default_country','IR:THR');update_option('woocommerce_currency','IRR');
update_option('woocommerce_calc_taxes','no');update_option('woocommerce_ship_to_countries','');
$zone_id=(int)get_option('tn_synthetic_shipping_zone',0);
if (!$zone_id) {
    $zone=new WC_Shipping_Zone();$zone->set_zone_name('آزمایش محلی؛ ارسال واقعی ندارد');$zone->set_zone_order(0);$zone->add_location('IR','country');$zone->save();
    $instance=$zone->add_shipping_method('flat_rate');
    update_option('woocommerce_flat_rate_'.$instance.'_settings',['title'=>'ارسال آزمایشی — تحویلی ندارد','tax_status'=>'none','cost'=>'1000']);
    update_option('tn_synthetic_shipping_zone',$zone->get_id());
}
$coupon_id=wc_get_coupon_id_by_code('tn-synthetic-100');
if (!$coupon_id) {$coupon=new WC_Coupon();$coupon->set_code('tn-synthetic-100');$coupon->set_discount_type('fixed_cart');$coupon->set_amount('100');$coupon->set_individual_use(true);$coupon->save();}
echo wp_json_encode(['product_id'=>$p->get_id(),'url'=>$p->get_permalink(),'scope'=>'Local synthetic fixture only; no real delivery/payment','price_irr'=>$p->get_regular_price()]);
