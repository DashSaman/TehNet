<?php
if (!defined('ABSPATH')) { exit; }

define('TEHNET_PRO_PRODUCT_OPTION', 'tehnet_pro_product_id');
define('TEHNET_PRO_EXPIRY_META', '_tehnet_pro_expires_at');
define('TEHNET_PRO_ORDER_GRANTED_META', '_tehnet_pro_granted_expiry');

function tehnet_pro_product_id(): int {
    return absint(get_option(TEHNET_PRO_PRODUCT_OPTION, 0));
}

function tehnet_user_pro_expiry(int $user_id): int {
    return (int) get_user_meta($user_id, TEHNET_PRO_EXPIRY_META, true);
}

function tehnet_user_has_pro(int $user_id, ?int $now = null): bool {
    if ($user_id <= 0) { return false; }
    return tehnet_pro_is_active(tehnet_user_pro_expiry($user_id), $now ?? time());
}

function tehnet_register_settings(): void {
    register_setting('tehnet_settings', TEHNET_PRO_PRODUCT_OPTION, [
        'type'              => 'integer',
        'sanitize_callback' => 'absint',
        'default'           => 0,
    ]);
}
add_action('admin_init', 'tehnet_register_settings');

function tehnet_add_settings_page(): void {
    add_options_page(
        __('تنظیمات TehNet', 'tehnet-core'),
        'TehNet',
        'manage_options',
        'tehnet-settings',
        'tehnet_render_settings_page'
    );
}
add_action('admin_menu', 'tehnet_add_settings_page');

function tehnet_render_settings_page(): void {
    if (!current_user_can('manage_options')) { return; }
    ?>
    <div class="wrap">
        <h1><?php echo esc_html__('تنظیمات TehNet', 'tehnet-core'); ?></h1>
        <form method="post" action="options.php">
            <?php settings_fields('tehnet_settings'); ?>
            <table class="form-table" role="presentation">
                <tr>
                    <th scope="row"><label for="tehnet_pro_product_id"><?php echo esc_html__('شناسه محصول TehNet Pro', 'tehnet-core'); ?></label></th>
                    <td>
                        <input class="small-text" type="number" min="0" id="tehnet_pro_product_id" name="tehnet_pro_product_id" value="<?php echo esc_attr((string) tehnet_pro_product_id()); ?>">
                        <p class="description"><?php echo esc_html__('پرداخت موفق این محصول ۳۰ روز دسترسی Pro می‌دهد. خرید مجدد، زمان فعال باقی‌مانده را حفظ و ۳۰ روز به آن اضافه می‌کند.', 'tehnet-core'); ?></p>
                    </td>
                </tr>
            </table>
            <?php submit_button(); ?>
        </form>
    </div>
    <?php
}

function tehnet_order_contains_pro_product($order, int $product_id): bool {
    if ($product_id <= 0 || !$order || !method_exists($order, 'get_items')) { return false; }
    foreach ($order->get_items() as $item) {
        if (method_exists($item, 'get_product_id') && (int) $item->get_product_id() === $product_id) {
            return true;
        }
    }
    return false;
}

function tehnet_grant_pro_from_paid_order(int $order_id): void {
    if (!function_exists('wc_get_order')) { return; }

    $order = wc_get_order($order_id);
    if (!$order) { return; }

    if ((int) $order->get_meta(TEHNET_PRO_ORDER_GRANTED_META, true) > 0) { return; }

    $product_id = tehnet_pro_product_id();
    if (!tehnet_order_contains_pro_product($order, $product_id)) { return; }

    $user_id = (int) $order->get_user_id();
    if ($user_id <= 0) { return; }

    $now = time();
    $current_expiry = tehnet_user_pro_expiry($user_id);
    $next_expiry = tehnet_pro_next_expiry($now, $current_expiry);

    update_user_meta($user_id, TEHNET_PRO_EXPIRY_META, $next_expiry);
    $order->update_meta_data(TEHNET_PRO_ORDER_GRANTED_META, $next_expiry);
    $order->save();
}
add_action('woocommerce_payment_complete', 'tehnet_grant_pro_from_paid_order');

function tehnet_format_pro_status(int $user_id): string {
    $expiry = tehnet_user_pro_expiry($user_id);
    if (!tehnet_pro_is_active($expiry, time())) {
        return __('اشتراک TehNet Pro فعال نیست.', 'tehnet-core');
    }

    $date = wp_date(get_option('date_format') . ' ' . get_option('time_format'), $expiry);
    return sprintf(__('اشتراک TehNet Pro تا %s فعال است.', 'tehnet-core'), $date);
}

function tehnet_pro_status_shortcode(): string {
    if (!is_user_logged_in()) {
        return '<p>' . esc_html__('برای مشاهده وضعیت TehNet Pro وارد حساب شوید.', 'tehnet-core') . '</p>';
    }
    return '<p class="tehnet-pro-status">' . esc_html(tehnet_format_pro_status(get_current_user_id())) . '</p>';
}
add_shortcode('tehnet_pro_status', 'tehnet_pro_status_shortcode');

function tehnet_render_account_pro_status(): void {
    if (!is_user_logged_in()) { return; }
    echo '<section class="tehnet-account-pro"><h2>' . esc_html__('TehNet Pro', 'tehnet-core') . '</h2><p>' . esc_html(tehnet_format_pro_status(get_current_user_id())) . '</p></section>';
}
add_action('woocommerce_account_dashboard', 'tehnet_render_account_pro_status', 20);
