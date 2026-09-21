<?php
/** TehNet physical-product inquiry persistence and admin UI. */

defined('ABSPATH') || exit;

final class TehNet_Core_Inquiries {
    public function register(): void {
        add_action('init', [$this, 'register_post_type']);
        add_action('admin_post_tehnet_product_inquiry', [$this, 'handle_request']);
        add_action('admin_post_nopriv_tehnet_product_inquiry', [$this, 'handle_request']);
        add_filter('manage_tn_inquiry_posts_columns', [$this, 'columns']);
        add_action('manage_tn_inquiry_posts_custom_column', [$this, 'render_column'], 10, 2);
    }

    public function register_post_type(): void {
        register_post_type('tn_inquiry', [
            'labels' => [
                'name' => __('استعلام‌ها', 'tehnet-core'),
                'singular_name' => __('استعلام', 'tehnet-core'),
            ],
            'public' => false,
            'publicly_queryable' => false,
            'show_ui' => true,
            'show_in_rest' => false,
            'show_in_menu' => class_exists('WooCommerce') ? 'woocommerce' : true,
            'supports' => ['title'],
            'map_meta_cap' => true,
            'capabilities' => [
                'edit_post' => 'manage_woocommerce',
                'read_post' => 'manage_woocommerce',
                'delete_post' => 'manage_woocommerce',
                'edit_posts' => 'manage_woocommerce',
                'edit_others_posts' => 'manage_woocommerce',
                'delete_posts' => 'manage_woocommerce',
                'delete_private_posts' => 'manage_woocommerce',
                'delete_published_posts' => 'manage_woocommerce',
                'edit_private_posts' => 'manage_woocommerce',
                'edit_published_posts' => 'manage_woocommerce',
                'publish_posts' => 'manage_woocommerce',
                'read_private_posts' => 'manage_woocommerce',
                'create_posts' => 'do_not_allow',
            ],
        ]);
    }

    public static function normalize_mobile(string $mobile): string {
        $mobile = strtr(trim($mobile), [
            '۰'=>'0','۱'=>'1','۲'=>'2','۳'=>'3','۴'=>'4','۵'=>'5','۶'=>'6','۷'=>'7','۸'=>'8','۹'=>'9',
            '٠'=>'0','١'=>'1','٢'=>'2','٣'=>'3','٤'=>'4','٥'=>'5','٦'=>'6','٧'=>'7','٨'=>'8','٩'=>'9',
        ]);
        $mobile = (string) preg_replace('/[\s\-()]+/u', '', $mobile);
        if (str_starts_with($mobile, '+98')) {
            $mobile = '0' . substr($mobile, 3);
        } elseif (str_starts_with($mobile, '0098')) {
            $mobile = '0' . substr($mobile, 4);
        } elseif (str_starts_with($mobile, '98')) {
            $mobile = '0' . substr($mobile, 2);
        }
        return preg_match('/^09\d{9}$/', $mobile) === 1 ? $mobile : '';
    }

    public static function normalize_quantity($quantity): int {
        if (is_int($quantity)) {
            $value = $quantity;
        } elseif (is_string($quantity) && preg_match('/^\d+$/', trim($quantity)) === 1) {
            $value = (int) trim($quantity);
        } else {
            return 0;
        }
        return $value >= 1 && $value <= 99 ? $value : 0;
    }

    public function process_request(array $request, int $user_id = 0) {
        if (! function_exists('wc_get_product')) {
            return new WP_Error('woocommerce_unavailable', __('WooCommerce در دسترس نیست.', 'tehnet-core'));
        }
        $product_id = absint($request['product_id'] ?? 0);
        $product = $product_id > 0 ? wc_get_product($product_id) : false;
        if (! $product || get_post_status($product_id) !== 'publish') {
            return new WP_Error('invalid_product', __('محصول معتبر نیست.', 'tehnet-core'));
        }
        if (! TehNet_Core_Commerce::is_physical_inquiry_product($product)) {
            return new WP_Error('not_physical', __('این محصول برای استعلام فیزیکی تعریف نشده است.', 'tehnet-core'));
        }

        $name = sanitize_text_field(wp_unslash((string) ($request['name'] ?? '')));
        $mobile = self::normalize_mobile((string) ($request['mobile'] ?? ''));
        $quantity = self::normalize_quantity($request['quantity'] ?? '');
        $raw_email = trim((string) ($request['email'] ?? ''));
        $email = $raw_email === '' ? '' : sanitize_email(wp_unslash($raw_email));
        $notes = sanitize_textarea_field(wp_unslash((string) ($request['notes'] ?? '')));
        if ($name === '' || $mobile === '' || $quantity === 0) {
            return new WP_Error('invalid_fields', __('نام، موبایل یا تعداد معتبر نیست.', 'tehnet-core'));
        }
        if ($raw_email !== '' && ($email === '' || ! is_email($email))) {
            return new WP_Error('invalid_email', __('ایمیل معتبر نیست.', 'tehnet-core'));
        }

        $duplicate_hash = hash('sha256', $product_id . '|' . $mobile . '|' . $quantity);
        $duplicate_key = 'tn_inquiry_' . $duplicate_hash;
        if (get_transient($duplicate_key)) {
            return new WP_Error('duplicate', __('این استعلام به‌تازگی ثبت شده است.', 'tehnet-core'));
        }

        $product_name = sanitize_text_field((string) $product->get_name());
        $inquiry_id = wp_insert_post([
            'post_type' => 'tn_inquiry',
            'post_status' => 'private',
            'post_title' => sprintf('استعلام #%d — %s', $product_id, $name),
            'post_author' => max(0, $user_id),
        ], true);
        if (is_wp_error($inquiry_id)) {
            return $inquiry_id;
        }

        update_post_meta($inquiry_id, '_tn_product_id', $product_id);
        update_post_meta($inquiry_id, '_tn_product_name', $product_name);
        update_post_meta($inquiry_id, '_tn_quantity', $quantity);
        update_post_meta($inquiry_id, '_tn_customer_name', $name);
        update_post_meta($inquiry_id, '_tn_mobile', $mobile);
        update_post_meta($inquiry_id, '_tn_email', $email);
        update_post_meta($inquiry_id, '_tn_notes', $notes);
        update_post_meta($inquiry_id, '_tn_user_id', max(0, $user_id));
        update_post_meta($inquiry_id, '_tn_status', 'new');
        update_post_meta($inquiry_id, '_tn_duplicate_key', $duplicate_key);
        set_transient($duplicate_key, 1, 5 * MINUTE_IN_SECONDS);
        return (int) $inquiry_id;
    }

    public function handle_request(): void {
        check_admin_referer('tehnet_product_inquiry', 'tn_inquiry_nonce');
        $product_id = absint($_POST['product_id'] ?? 0);
        $fallback = home_url('/shop/');
        $product_url = $product_id > 0 ? get_permalink($product_id) : '';
        $redirect = is_string($product_url) && $product_url !== '' ? $product_url : $fallback;

        if (! empty($_POST['tn_website'])) {
            $this->redirect_with_result($redirect, 'invalid');
        }

        $result = $this->process_request($_POST, get_current_user_id());
        if (is_wp_error($result)) {
            $code = $result->get_error_code() === 'duplicate' ? 'duplicate' : 'invalid';
            $this->redirect_with_result($redirect, $code);
        }
        $this->redirect_with_result($redirect, 'success');
    }

    private function redirect_with_result(string $url, string $code): void {
        $target = add_query_arg('tn_inquiry_result', $code, $url) . '#tehnet-inquiry';
        wp_safe_redirect($target, 303);
        exit;
    }

    public function columns(array $columns): array {
        return [
            'cb' => $columns['cb'] ?? '<input type="checkbox">',
            'title' => __('استعلام', 'tehnet-core'),
            'tn_product' => __('محصول', 'tehnet-core'),
            'tn_customer' => __('مشتری', 'tehnet-core'),
            'tn_mobile' => __('موبایل', 'tehnet-core'),
            'tn_quantity' => __('تعداد', 'tehnet-core'),
            'tn_status' => __('وضعیت', 'tehnet-core'),
            'date' => __('تاریخ', 'tehnet-core'),
        ];
    }

    public function render_column(string $column, int $post_id): void {
        $map = [
            'tn_product' => '_tn_product_name',
            'tn_customer' => '_tn_customer_name',
            'tn_mobile' => '_tn_mobile',
            'tn_quantity' => '_tn_quantity',
            'tn_status' => '_tn_status',
        ];
        if (! isset($map[$column])) {
            return;
        }
        $value = (string) get_post_meta($post_id, $map[$column], true);
        echo esc_html($value !== '' ? $value : '—');
    }
}
