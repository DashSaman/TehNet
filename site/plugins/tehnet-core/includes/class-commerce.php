<?php
/** TehNet WooCommerce inquiry-only policy. */

defined('ABSPATH') || exit;

final class TehNet_Core_Commerce {
    public function register(): void {
        add_filter('woocommerce_is_purchasable', [$this, 'filter_purchasable'], 20, 2);
        add_filter('woocommerce_get_price_html', [$this, 'filter_price_html'], 20, 2);
        add_filter('woocommerce_loop_add_to_cart_link', [$this, 'filter_loop_cta'], 20, 3);
        add_action('woocommerce_single_product_summary', [$this, 'render_inquiry_form'], 31);
        add_action('woocommerce_before_single_product', [$this, 'render_result_notice'], 5);
        add_action('wp_head', [$this, 'render_archive_canonical'], 8);
    }

    public function render_archive_canonical(): void {
        $url = '';
        if (function_exists('is_shop') && is_shop() && function_exists('wc_get_page_permalink')) {
            $url = (string) wc_get_page_permalink('shop');
        } elseif (function_exists('is_product_category') && is_product_category()) {
            $term = get_queried_object();
            if ($term instanceof WP_Term) {
                $term_link = get_term_link($term);
                if (! is_wp_error($term_link)) {
                    $url = (string) $term_link;
                }
            }
        }

        if ($url === '') {
            return;
        }
        $paged = max(1, (int) get_query_var('paged'));
        if ($paged > 1) {
            $url = (string) get_pagenum_link($paged);
        }
        printf('<link rel="canonical" href="%s" />' . "\n", esc_url($url));
    }

    public static function is_physical_inquiry_product($product): bool {
        return is_object($product)
            && method_exists($product, 'is_virtual')
            && method_exists($product, 'is_downloadable')
            && ! $product->is_virtual()
            && ! $product->is_downloadable();
    }

    public function filter_purchasable(bool $purchasable, $product): bool {
        return self::is_physical_inquiry_product($product) ? false : $purchasable;
    }

    public function filter_price_html(string $price, $product): string {
        if (! self::is_physical_inquiry_product($product)) {
            return $price;
        }
        return '<span class="tn-inquiry-price">' . esc_html__('استعلام قیمت روز', 'tehnet-core') . '</span>';
    }

    public function filter_loop_cta(string $html, $product, array $args = []): string {
        if (! self::is_physical_inquiry_product($product) || ! method_exists($product, 'get_id')) {
            return $html;
        }
        $class = trim('button tn-inquiry-button ' . ($args['class'] ?? ''));
        return sprintf(
            '<a href="%s" class="%s">%s</a>',
            esc_url(get_permalink((int) $product->get_id())),
            esc_attr($class),
            esc_html__('استعلام قیمت', 'tehnet-core')
        );
    }

    public function render_inquiry_form(): void {
        global $product;
        if (! self::is_physical_inquiry_product($product) || ! method_exists($product, 'get_id')) {
            return;
        }
        $product_id = (int) $product->get_id();
        ?>
        <form id="tehnet-inquiry" class="tn-inquiry-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
            <input type="hidden" name="action" value="tehnet_product_inquiry">
            <input type="hidden" name="product_id" value="<?php echo esc_attr((string) $product_id); ?>">
            <?php wp_nonce_field('tehnet_product_inquiry', 'tn_inquiry_nonce'); ?>
            <p class="tn-inquiry-honeypot" aria-hidden="true">
                <label>Website <input type="text" name="tn_website" value="" autocomplete="off" tabindex="-1"></label>
            </p>
            <label><?php esc_html_e('نام و نام خانوادگی', 'tehnet-core'); ?>
                <input type="text" name="name" maxlength="120" required autocomplete="name">
            </label>
            <label><?php esc_html_e('شماره موبایل', 'tehnet-core'); ?>
                <input type="tel" name="mobile" inputmode="tel" maxlength="20" required autocomplete="tel">
            </label>
            <label><?php esc_html_e('ایمیل (اختیاری)', 'tehnet-core'); ?>
                <input type="email" name="email" maxlength="190" autocomplete="email">
            </label>
            <label><?php esc_html_e('تعداد', 'tehnet-core'); ?>
                <input type="number" name="quantity" min="1" max="99" step="1" value="1" required>
            </label>
            <label><?php esc_html_e('توضیحات (اختیاری)', 'tehnet-core'); ?>
                <textarea name="notes" rows="4" maxlength="2000"></textarea>
            </label>
            <button class="tn-button" type="submit"><?php esc_html_e('استعلام قیمت', 'tehnet-core'); ?></button>
        </form>
        <?php
    }

    public function render_result_notice(): void {
        if (empty($_GET['tn_inquiry_result'])) {
            return;
        }
        $code = sanitize_key(wp_unslash((string) $_GET['tn_inquiry_result']));
        $messages = [
            'success' => ['woocommerce-message', __('درخواست استعلام ثبت شد. برای پیگیری با شما تماس گرفته می‌شود.', 'tehnet-core')],
            'duplicate' => ['woocommerce-info', __('این استعلام به‌تازگی ثبت شده است؛ نیازی به ارسال دوباره نیست.', 'tehnet-core')],
            'invalid' => ['woocommerce-error', __('اطلاعات استعلام معتبر نیست. لطفاً فرم را بررسی و دوباره ارسال کنید.', 'tehnet-core')],
            'error' => ['woocommerce-error', __('ثبت استعلام انجام نشد. لطفاً دوباره تلاش کنید.', 'tehnet-core')],
        ];
        if (! isset($messages[$code])) {
            return;
        }
        [$class, $message] = $messages[$code];
        printf('<div class="%s" role="status">%s</div>', esc_attr($class), esc_html($message));
    }
}
