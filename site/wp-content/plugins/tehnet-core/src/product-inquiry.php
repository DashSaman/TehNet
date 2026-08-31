<?php
if (!defined('ABSPATH')) { exit; }

function tehnet_product_sale_mode(int $product_id): string {
    return tehnet_normalize_sale_mode((string) get_post_meta($product_id, TEHNET_SALE_MODE_META, true));
}

function tehnet_register_product_sale_mode_meta(): void {
    register_post_meta('product', TEHNET_SALE_MODE_META, [
        'type'              => 'string',
        'single'            => true,
        'show_in_rest'      => true,
        'sanitize_callback' => 'tehnet_normalize_sale_mode',
        'auth_callback'     => static fn() => current_user_can('edit_products'),
    ]);
}
add_action('init', 'tehnet_register_product_sale_mode_meta');

function tehnet_render_product_sale_mode_field(): void {
    if (!function_exists('woocommerce_wp_select')) { return; }

    woocommerce_wp_select([
        'id'          => TEHNET_SALE_MODE_META,
        'label'       => __('روش فروش در TehNet', 'tehnet-core'),
        'description' => __('فروش مستقیم از سبد خرید یا استعلام قیمت/موجودی.', 'tehnet-core'),
        'desc_tip'    => true,
        'options'     => [
            TEHNET_SALE_MODE_DIRECT  => __('خرید مستقیم', 'tehnet-core'),
            TEHNET_SALE_MODE_INQUIRY => __('استعلام قیمت و موجودی', 'tehnet-core'),
        ],
    ]);
}
add_action('woocommerce_product_options_general_product_data', 'tehnet_render_product_sale_mode_field');

function tehnet_save_product_sale_mode(int $product_id): void {
    if (!current_user_can('edit_post', $product_id)) { return; }
    $raw = isset($_POST[TEHNET_SALE_MODE_META])
        ? sanitize_text_field(wp_unslash($_POST[TEHNET_SALE_MODE_META]))
        : TEHNET_SALE_MODE_DIRECT;
    update_post_meta($product_id, TEHNET_SALE_MODE_META, tehnet_normalize_sale_mode($raw));
}
add_action('woocommerce_process_product_meta', 'tehnet_save_product_sale_mode');

function tehnet_inquiry_product_is_purchasable(bool $purchasable, $product): bool {
    if (!$product || !method_exists($product, 'get_id')) { return $purchasable; }
    return tehnet_product_sale_mode((int) $product->get_id()) === TEHNET_SALE_MODE_INQUIRY
        ? false
        : $purchasable;
}
add_filter('woocommerce_is_purchasable', 'tehnet_inquiry_product_is_purchasable', 10, 2);

function tehnet_product_inquiry_url(int $product_id): string {
    return add_query_arg([
        'intent'  => 'product-inquiry',
        'product' => $product_id,
    ], home_url('/contact/'));
}

function tehnet_render_inquiry_cta(): void {
    global $product;
    if (!$product || !method_exists($product, 'get_id')) { return; }

    $product_id = (int) $product->get_id();
    if (tehnet_product_sale_mode($product_id) !== TEHNET_SALE_MODE_INQUIRY) { return; }

    printf(
        '<a class="button alt tehnet-inquiry-button" href="%s">%s</a>',
        esc_url(tehnet_product_inquiry_url($product_id)),
        esc_html__('استعلام قیمت و موجودی', 'tehnet-core')
    );
}
add_action('woocommerce_single_product_summary', 'tehnet_render_inquiry_cta', 31);

function tehnet_loop_inquiry_button(string $html, $product): string {
    if (!$product || !method_exists($product, 'get_id')) { return $html; }
    $product_id = (int) $product->get_id();
    if (tehnet_product_sale_mode($product_id) !== TEHNET_SALE_MODE_INQUIRY) { return $html; }

    return sprintf(
        '<a class="button tehnet-inquiry-button" href="%s">%s</a>',
        esc_url(tehnet_product_inquiry_url($product_id)),
        esc_html__('استعلام قیمت و موجودی', 'tehnet-core')
    );
}
add_filter('woocommerce_loop_add_to_cart_link', 'tehnet_loop_inquiry_button', 10, 2);
