<?php
if (wp_get_environment_type() !== 'local') { throw new RuntimeException('Local tests only'); }
if (!class_exists('TehNet_Store_ERP')) { throw new RuntimeException('ERP bridge is missing'); }
$check=static function($ok,$message) { if (!$ok) { throw new RuntimeException($message); } echo "PASS: $message\n"; };
$bridge=new TehNet_Store_ERP();
$check($bridge->configured(), 'server-only ERP configuration is present');
$product=new WC_Product_Simple();$product->set_name('SYNTHETIC BRIDGE TEST ONLY');
$product->set_status('private');$product->set_regular_price('1000');
$product->update_meta_data('_tn_erp_sku','TN-SANDBOX-CABLE');
$product->update_meta_data('_tn_erp_uom','Meter');
$product->update_meta_data('_tn_sale_approved','yes');
$product->update_meta_data('_tn_sale_unit','meter');
$product->update_meta_data('_tn_min_quantity','0.5');$product->save();
try {
    $bridge->sync_product($product->get_id());$product=wc_get_product($product->get_id());
    $check((int)$product->get_meta('_tn_erp_fresh_until')>time(),'ERP snapshot refreshes verified price/availability');
    $order=wc_create_order();$order->set_currency('IRR');$order->set_billing_first_name('SYNTHETIC');
    $order->add_product($product,2.5,['subtotal'=>'2500','total'=>'2500']);
    $order->calculate_totals();$order->save();
    $offline=static fn()=>new WP_Error('synthetic_timeout','SYNTHETIC TRANSPORT FAILURE');
    add_filter('pre_http_request',$offline);
    try { $bridge->reserve_order($order);throw new RuntimeException('Expected simulated transport failure'); }
    catch (RuntimeException $error) { $check(str_contains($error->getMessage(),'unavailable'),'transport failure is explicit'); }
    finally { remove_filter('pre_http_request',$offline); }
    $box=$order->get_meta('_tn_erp_outbox');$key=array_key_first($box);
    $check($box[$key]['state']==='pending' && $box[$key]['attempts']===1,'network failure retains a durable pending event');
    $bridge->retry($order->get_id(),$key);$order=wc_get_order($order->get_id());
    $first=$bridge->reserve_order($order);$again=$bridge->reserve_order($order);
    $check($first['sales_order']===$again['sales_order'],'actual Woo order reserves exactly one native ERP sales order');
    $check($first['amount_irr']==='2500','2.5m is calculated as exactly 2500 IRR');
    $check($bridge->cancel_order($order)['state']==='canceled','Woo cancellation releases the native reservation');
    $order=wc_get_order($order->get_id());
    $check(count($order->get_meta('_tn_erp_outbox'))===2,'durable outbox retains both acknowledged event records');
    $closed=wc_create_order();$closed->set_currency('IRR');$closed->add_product($product,1,['subtotal'=>'1000','total'=>'1000']);$closed->calculate_totals();$closed->save();
    add_filter('pre_http_request',$offline);
    try { $bridge->reserve_order($closed); } catch (RuntimeException $expected) { }
    finally { remove_filter('pre_http_request',$offline); }
    $closed->update_status('cancelled');$closed_box=$closed->get_meta('_tn_erp_outbox');$closed_key=array_key_first($closed_box);
    $bridge->retry($closed->get_id(),$closed_key);$closed=wc_get_order($closed->get_id());
    $check($closed->get_meta('_tn_erp_outbox')[$closed_key]['state']==='voided','late retry cannot resurrect a canceled order reservation');
    echo "ERP_BRIDGE=PASSED\n";
} finally { wp_trash_post($product->get_id()); }
