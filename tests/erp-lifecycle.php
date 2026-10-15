<?php
if (wp_get_environment_type()!=='local') { throw new RuntimeException('Local synthetic test only'); }
if (!method_exists('TehNet_Store_ERP','reconcile_order')) { throw new RuntimeException('ERP status/refund reconciliation is missing'); }
$check=static function($ok,$message) { if (!$ok) { throw new RuntimeException($message); } echo "PASS: $message\n"; };
$bridge=new TehNet_Store_ERP();$run='woo-test-'.wp_generate_uuid4();
$product=new WC_Product_Simple();$product->set_name('SYNTHETIC LIFECYCLE TEST');$product->set_status('private');
$product->set_regular_price('1000');
foreach (['_tn_erp_sku'=>'TN-SANDBOX-CABLE','_tn_erp_uom'=>'Meter','_tn_sale_approved'=>'yes','_tn_sale_unit'=>'meter','_tn_min_quantity'=>'0.5'] as $key=>$value) { $product->update_meta_data($key,$value); }
$product->save();
try {
    $order=wc_create_order();$order->update_meta_data('_tn_synthetic_fixture','yes');$order->set_currency('IRR');$order->set_billing_first_name('SYNTHETIC');
    $order->add_product($product,2,['subtotal'=>'2000','total'=>'1900']);
    $shipping=new WC_Order_Item_Shipping();$shipping->set_method_title('SYNTHETIC SHIPPING');$shipping->set_total('200');$order->add_item($shipping);
    $order->calculate_totals();$order->save();
    $bridge->reserve_order($order);
    $bridge->send($order,'paid',['currency'=>'IRR','amount_irr'=>'2100','payment_identity'=>$run.':payment']);
    $bridge->send($order,'dispatch',['tracking_reference'=>'SYNTHETIC-TRACKING-123']);
    $bridge->send($order,'refund',['items'=>[['sku'=>'TN-SANDBOX-CABLE','qty'=>'1']],'amount_irr'=>'1050','shipping_refund_irr'=>'100','payment_identity'=>$run.':refund-one']);
    $status=$bridge->reconcile_order($order);$order=wc_get_order($order->get_id());
    $check($status['state']==='partially_refunded','ERP state reaches the actual Woo order');
    $check($order->get_meta('_tn_tracking_reference')==='SYNTHETIC-TRACKING-123','carrier tracking reaches the customer order');
    $check((string)(int)$order->get_total_refunded()==='1050','native Woo refund includes the allocated discount/shipping');
    $check(count($order->get_refunds())===1,'one ERP credit creates one native Woo refund');
    $bridge->reconcile_order($order);$order=wc_get_order($order->get_id());
    $check(count($order->get_refunds())===1,'repeated reconciliation creates no duplicate refund');
    $bridge->send($order,'refund',['items'=>[['sku'=>'TN-SANDBOX-CABLE','qty'=>'1']],'amount_irr'=>'1050','shipping_refund_irr'=>'100','payment_identity'=>$run.':refund-two']);
    $bridge->reconcile_order($order);$order=wc_get_order($order->get_id());
    $check(count($order->get_refunds())===2 && (int)$order->get_total_refunded()===2100 && $order->has_status('refunded'),'remaining return completes the native Woo refund');
    $invoice=$bridge->invoice_document($order);
    $check($invoice['currency']==='IRR' && $invoice['amount_irr']==='2100' && $invoice['invoice']!=='','account invoice uses the authoritative numbered ERP invoice');
    echo "ERP_LIFECYCLE=PASSED\n";
} finally { wp_trash_post($product->get_id()); }
