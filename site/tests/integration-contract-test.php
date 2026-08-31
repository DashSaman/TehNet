<?php
$plugin = dirname(__DIR__) . '/wp-content/plugins/tehnet-core';
$pro = $plugin . '/src/pro-membership.php';
$inquiry = $plugin . '/src/product-inquiry.php';

function tn_contract_assert($condition, string $message): void {
    if (!$condition) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
}

tn_contract_assert(is_file($pro), 'pro-membership.php exists');
$pro_code = is_file($pro) ? file_get_contents($pro) : '';
$inquiry_code = file_get_contents($inquiry);

foreach (['tehnet_pro_product_id','_tehnet_pro_expires_at','woocommerce_payment_complete','tehnet_pro_next_expiry'] as $needle) {
    tn_contract_assert(strpos($pro_code, $needle) !== false, "Pro integration contains {$needle}");
}
foreach (['woocommerce_product_options_general_product_data','woocommerce_process_product_meta','استعلام قیمت و موجودی'] as $needle) {
    tn_contract_assert(strpos($inquiry_code, $needle) !== false, "Inquiry integration contains {$needle}");
}

echo "integration-contract-test: PASS\n";
