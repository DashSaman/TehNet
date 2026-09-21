<?php
/** Internal production smoke for TehNet physical inquiry. Run via WP-CLI only. */

defined('ABSPATH') || exit(1);
if (! defined('WP_CLI') || ! WP_CLI) {
    throw new RuntimeException('This smoke test must run under WP-CLI.');
}
if (! class_exists('WooCommerce') || ! class_exists('WC_Product_Simple')) {
    throw new RuntimeException('WooCommerce is not active.');
}
if (! class_exists('TehNet_Core_Inquiries') || ! class_exists('TehNet_Core_Commerce')) {
    throw new RuntimeException('TehNet commerce classes are unavailable.');
}

$product_id = 0;
$inquiry_id = 0;
$sku = 'TEHNET-SMOKE-' . wp_generate_password(10, false, false);
$mobile = '09120000000';
$quantity = 2;
$duplicate_key = '';
$assert = static function (bool $ok, string $message): void {
    if (! $ok) {
        throw new RuntimeException($message);
    }
};

try {
    $product = new WC_Product_Simple();
    $product->set_name('TEHNET INTERNAL COMMERCE SMOKE');
    $product->set_status('publish');
    $product->set_catalog_visibility('hidden');
    $product->set_virtual(false);
    $product->set_downloadable(false);
    $product->set_sku($sku);
    $product_id = (int) $product->save();
    $assert($product_id > 0, 'temporary product was not created');

    $service = new TehNet_Core_Inquiries();
    $request = [
        'product_id' => $product_id,
        'name' => 'TehNet Smoke',
        'mobile' => $mobile,
        'quantity' => (string) $quantity,
        'email' => '',
        'notes' => 'internal production smoke',
    ];
    $result = $service->process_request($request, 0);
    $assert(! is_wp_error($result), 'first inquiry returned WP_Error');
    $inquiry_id = (int) $result;
    $assert($inquiry_id > 0, 'inquiry ID is invalid');
    $assert(get_post_type($inquiry_id) === 'tn_inquiry', 'wrong inquiry post type');
    $assert(get_post_status($inquiry_id) === 'private', 'inquiry must be private');
    $assert((int) get_post_meta($inquiry_id, '_tn_product_id', true) === $product_id, 'product meta mismatch');
    $assert((string) get_post_meta($inquiry_id, '_tn_mobile', true) === $mobile, 'mobile meta mismatch');
    $assert((int) get_post_meta($inquiry_id, '_tn_quantity', true) === $quantity, 'quantity meta mismatch');

    $duplicate_key = (string) get_post_meta($inquiry_id, '_tn_duplicate_key', true);
    $assert($duplicate_key !== '' && get_transient($duplicate_key), 'duplicate transient missing');

    $second = $service->process_request($request, 0);
    $assert(is_wp_error($second) && $second->get_error_code() === 'duplicate', 'duplicate inquiry was not rejected');

    $matches = get_posts([
        'post_type' => 'tn_inquiry',
        'post_status' => 'private',
        'meta_key' => '_tn_customer_name',
        'meta_value' => 'TehNet Smoke',
        'fields' => 'ids',
        'numberposts' => -1,
    ]);
    $assert(count($matches) === 1 && (int) $matches[0] === $inquiry_id, 'duplicate inquiry record was created');

    $virtual = new WC_Product_Simple();
    $virtual->set_virtual(true);
    $virtual->set_downloadable(false);
    $assert(! TehNet_Core_Commerce::is_physical_inquiry_product($virtual), 'virtual product classified as physical inquiry');
} finally {
    if ($duplicate_key !== '') {
        delete_transient($duplicate_key);
    }
    if ($inquiry_id > 0) {
        wp_delete_post($inquiry_id, true);
    }
    if ($product_id > 0) {
        $cleanup_product = wc_get_product($product_id);
        if ($cleanup_product) {
            $cleanup_product->delete(true);
        } else {
            wp_delete_post($product_id, true);
        }
    }
}

$assert(wc_get_product_id_by_sku($sku) === 0, 'temporary product cleanup failed');
$remaining = get_posts([
    'post_type' => 'tn_inquiry',
    'post_status' => 'any',
    'meta_key' => '_tn_customer_name',
    'meta_value' => 'TehNet Smoke',
    'fields' => 'ids',
    'numberposts' => -1,
]);
$assert($remaining === [], 'temporary inquiry cleanup failed');
if ($duplicate_key !== '') {
    $assert(! get_transient($duplicate_key), 'duplicate transient cleanup failed');
}

echo "COMMERCE_LIVE_SMOKE=PASSED\n";
