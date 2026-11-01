<?php
/** TehNet manual quote/invoice lifecycle for physical-product inquiries. */

defined('ABSPATH') || exit;

final class TehNet_Core_Quotes {
    public const QUOTE_TYPE = 'tn_quote';
    public const INVOICE_TYPE = 'tn_invoice';

    private const TRANSITIONS = [
        'quote' => [
            'new' => ['sent', 'canceled'],
            'sent' => ['accepted', 'rejected', 'expired', 'canceled'],
            'accepted' => [],
            'rejected' => [],
            'expired' => [],
            'canceled' => [],
        ],
        'invoice' => [
            'issued' => ['paid', 'canceled'],
            'paid' => [],
            'canceled' => [],
        ],
    ];

    private const LABELS = [
        'quote' => [
            'new' => 'جدید',
            'sent' => 'ارسال‌شده',
            'accepted' => 'تأییدشده',
            'rejected' => 'ردشده',
            'expired' => 'منقضی',
            'canceled' => 'لغوشده',
        ],
        'invoice' => [
            'issued' => 'صادره',
            'paid' => 'پرداخت‌شده',
            'canceled' => 'لغوشده',
        ],
    ];

    public function register(): void {
        add_action('init', [$this, 'register_post_types']);
        add_action('admin_post_tehnet_quote_from_inquiry', [$this, 'create_quote_from_inquiry']);
        add_action('admin_post_tehnet_invoice_from_quote', [$this, 'create_invoice_from_quote']);
        add_action('admin_post_tehnet_doc_print', [$this, 'render_print_view']);
        add_filter('manage_tn_inquiry_posts_columns', [$this, 'inquiry_columns']);
        add_action('manage_tn_inquiry_posts_custom_column', [$this, 'render_inquiry_column'], 10, 2);
        add_filter('manage_tn_quote_posts_columns', [$this, 'doc_columns']);
        add_action('manage_tn_quote_posts_custom_column', [$this, 'render_doc_column'], 10, 2);
        add_filter('manage_tn_invoice_posts_columns', [$this, 'doc_columns']);
        add_action('manage_tn_invoice_posts_custom_column', [$this, 'render_doc_column'], 10, 2);
        add_filter('post_row_actions', [$this, 'row_actions'], 10, 2);
        add_action('add_meta_boxes', [$this, 'meta_boxes']);
        add_action('save_post_tn_quote', [$this, 'save_quote'], 10, 2);
        add_action('save_post_tn_invoice', [$this, 'save_invoice'], 10, 2);
        add_action('admin_head', [$this, 'admin_styles']);
    }

    public function register_post_types(): void {
        $shared = [
            'public' => false,
            'publicly_queryable' => false,
            'show_ui' => true,
            'show_in_rest' => false,
            'show_in_menu' => class_exists('WooCommerce') ? 'woocommerce' : true,
            'supports' => ['title'],
            'map_meta_cap' => true,
            'capabilities' => [
                'edit_post' => 'edit_tn_commerce_document',
                'read_post' => 'read_tn_commerce_document',
                'delete_post' => 'delete_tn_commerce_document',
                'edit_posts' => 'manage_woocommerce',
                'edit_others_posts' => 'manage_woocommerce',
                'delete_posts' => 'manage_woocommerce',
                'delete_private_posts' => 'manage_woocommerce',
                'delete_published_posts' => 'manage_woocommerce',
                'edit_private_posts' => 'manage_woocommerce',
                'edit_published_posts' => 'manage_woocommerce',
                'publish_posts' => 'manage_woocommerce',
                'read_private_posts' => 'manage_woocommerce',
                'create_posts' => 'manage_woocommerce',
            ],
        ];
        register_post_type(self::QUOTE_TYPE, array_merge($shared, [
            'labels' => [
                'name' => __('پیش‌فاکتورها', 'tehnet-core'),
                'singular_name' => __('پیش‌فاکتور', 'tehnet-core'),
                'add_new_item' => __('افزودن پیش‌فاکتور', 'tehnet-core'),
            ],
        ]));
        register_post_type(self::INVOICE_TYPE, array_merge($shared, [
            'labels' => [
                'name' => __('فاکتورها', 'tehnet-core'),
                'singular_name' => __('فاکتور', 'tehnet-core'),
                'add_new_item' => __('افزودن فاکتور', 'tehnet-core'),
            ],
        ]));
    }

    /* ---------- Pure logic (no WordPress calls; unit-tested standalone) ---------- */

    public static function statuses(string $type): array {
        return array_keys(self::TRANSITIONS[self::type_key($type)] ?? []);
    }

    public static function is_valid_status(string $type, string $status): bool {
        $key = self::type_key($type);
        return $key !== '' && isset(self::TRANSITIONS[$key][$status]);
    }

    public static function can_transition(string $type, string $from, string $to): bool {
        $key = self::type_key($type);
        if ($key === '' || $from === $to) {
            return false;
        }
        return isset(self::TRANSITIONS[$key][$from]) && in_array($to, self::TRANSITIONS[$key][$from], true);
    }

    public static function label(string $type, string $status): string {
        $key = self::type_key($type);
        return self::LABELS[$key][$status] ?? $status;
    }

    private static function type_key(string $type): string {
        return match ($type) {
            'quote', self::QUOTE_TYPE => 'quote',
            'invoice', self::INVOICE_TYPE => 'invoice',
            default => '',
        };
    }

    public static function normalize_amount($amount): int {
        if (is_int($amount)) {
            $value = $amount;
        } elseif (is_string($amount) && preg_match('/^\d+$/', trim($amount)) === 1) {
            $value = (int) trim($amount);
        } elseif (is_float($amount) && floor($amount) === $amount) {
            $value = (int) $amount;
        } else {
            return -1;
        }
        return $value >= 0 && $value <= 99999999999 ? $value : -1;
    }

    /** @param array<int,array{description:mixed,qty:mixed,unit_price:mixed}> $rows */
    public static function normalize_items(array $rows): array {
        $items = [];
        foreach ($rows as $row) {
            if (! is_array($row)) {
                continue;
            }
            $description = self::clean_text((string) ($row['description'] ?? ''));
            $qty = TehNet_Core_Inquiries::normalize_quantity($row['qty'] ?? '');
            $unit_price = self::normalize_amount($row['unit_price'] ?? '');
            if ($description === '' || $qty === 0 || $unit_price < 0) {
                continue;
            }
            if (preg_match('/^.{190}/us', $description, $matches) === 1) {
                $description = $matches[0];
            }
            $items[] = [
                'description' => $description,
                'qty' => $qty,
                'unit_price' => $unit_price,
            ];
            if (count($items) >= 20) {
                break;
            }
        }
        return $items;
    }

    private static function clean_text(string $text): string {
        return trim(preg_replace('/[\r\n\t]+/u', ' ', strip_tags($text)));
    }

    /** @return array{items:array,subtotal:int,discount:int,shipping:int,total:int}|WP_Error */
    public static function compute_totals(array $items, $discount, $shipping) {
        $discount = self::normalize_amount($discount);
        $shipping = self::normalize_amount($shipping);
        if ($discount < 0 || $shipping < 0) {
            return new WP_Error('invalid_amounts', 'مبالغ تخفیف/ارسال معتبر نیست.');
        }
        $subtotal = 0;
        foreach ($items as $item) {
            $qty = (int) ($item['qty'] ?? 0);
            $unit = (int) ($item['unit_price'] ?? 0);
            if ($qty < 1 || $unit < 0) {
                return new WP_Error('invalid_item', 'قلم نامعتبر.');
            }
            $subtotal += $qty * $unit;
        }
        if ($discount > $subtotal) {
            return new WP_Error('discount_too_large', 'تخفیف از جمع کل بیشتر است.');
        }
        return [
            'items' => array_values($items),
            'subtotal' => $subtotal,
            'discount' => $discount,
            'shipping' => $shipping,
            'total' => $subtotal - $discount + $shipping,
        ];
    }

    public static function ready_to_send(array $totals): bool {
        return is_array($totals) && (int) ($totals['subtotal'] ?? 0) > 0 && (int) ($totals['total'] ?? 0) > 0;
    }

    public static function build_number(string $type, int $post_id, string $ymd): string {
        $prefix = self::type_key($type) === 'invoice' ? 'I' : 'Q';
        return sprintf('%s-%s-%06d', $prefix, substr($ymd, 0, 6), max(1, $post_id));
    }

    public static function format_rials(int $amount): string {
        return number_format($amount, 0, '.', ',') . ' ریال';
    }

    public static function to_persian_digits(string $text): string {
        return strtr($text, [
            '0' => '۰', '1' => '۱', '2' => '۲', '3' => '۳', '4' => '۴',
            '5' => '۵', '6' => '۶', '7' => '۷', '8' => '۸', '9' => '۹',
        ]);
    }

    public static function format_rials_fa(int $amount): string {
        return self::to_persian_digits(number_format($amount, 0, '.', ',')) . ' ریال';
    }

    /** @return array{0:int,1:int,2:int} [jy, jm, jd] */
    public static function gregorian_to_jalali(int $gy, int $gm, int $gd): array {
        $g_day_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
        $gy2 = $gm > 2 ? $gy + 1 : $gy;
        $days = 355666 + (365 * $gy) + intdiv($gy2 + 3, 4) - intdiv($gy2 + 99, 100) + intdiv($gy2 + 399, 400) + $gd + $g_day_m[$gm - 1];
        $jy = -1595 + (33 * intdiv($days, 12053));
        $days %= 12053;
        $jy += 4 * intdiv($days, 1461);
        $days %= 1461;
        if ($days > 365) {
            $jy += intdiv($days - 1, 365);
            $days = ($days - 1) % 365;
        }
        if ($days < 186) {
            $jm = 1 + intdiv($days, 31);
            $jd = 1 + ($days % 31);
        } else {
            $jm = 7 + intdiv($days - 186, 30);
            $jd = 1 + (($days - 186) % 30);
        }
        return [$jy, $jm, $jd];
    }

    /** MySQL datetime ('Y-m-d H:i:s') to Persian-digit Jalali date ('۱۴۰۵/۰۷/۰۳'). */
    public static function jalali_from_mysql(string $mysql): string {
        $date = trim(explode(' ', trim($mysql))[0] ?? '');
        $parts = array_map('intval', explode('-', $date));
        if (count($parts) !== 3 || $parts[0] < 1 || $parts[1] < 1 || $parts[1] > 12 || $parts[2] < 1 || $parts[2] > 31) {
            return '';
        }
        [$jy, $jm, $jd] = self::gregorian_to_jalali($parts[0], $parts[1], $parts[2]);
        return self::to_persian_digits(sprintf('%04d/%02d/%02d', $jy, $jm, $jd));
    }

    public static function items_from_post(array $post): array {
        $rows = [];
        $descs = (array) ($post['tn_item_desc'] ?? []);
        $qtys = (array) ($post['tn_item_qty'] ?? []);
        $prices = (array) ($post['tn_item_price'] ?? []);
        $count = max(count($descs), count($qtys), count($prices));
        for ($i = 0; $i < $count; $i++) {
            $rows[] = [
                'description' => $descs[$i] ?? '',
                'qty' => $qtys[$i] ?? '',
                'unit_price' => $prices[$i] ?? '',
            ];
        }
        return $rows;
    }

    /* ---------- WordPress-bound implementation ---------- */

    public function inquiry_columns(array $columns): array {
        $columns['tn_quote_link'] = __('پیش‌فاکتور', 'tehnet-core');
        return $columns;
    }

    public function render_inquiry_column(string $column, int $post_id): void {
        if ($column !== 'tn_quote_link') {
            return;
        }
        $quote_id = (int) get_post_meta($post_id, '_tn_inquiry_quote_id', true);
        if ($quote_id > 0 && get_post_status($quote_id) !== false) {
            printf('<a href="%s">#%d</a>', esc_url(get_edit_post_link($quote_id)), $quote_id);
        } else {
            echo '—';
        }
    }

    public function doc_columns(array $columns): array {
        return [
            'cb' => $columns['cb'] ?? '<input type="checkbox">',
            'title' => $columns['title'] ?? '',
            'tn_number' => __('شماره', 'tehnet-core'),
            'tn_customer' => __('مشتری', 'tehnet-core'),
            'tn_total' => __('مبلغ کل', 'tehnet-core'),
            'tn_status' => __('وضعیت', 'tehnet-core'),
            'date' => __('تاریخ', 'tehnet-core'),
        ];
    }

    public function render_doc_column(string $column, int $post_id): void {
        $map = ['tn_number' => '_tn_doc_number', 'tn_customer' => '_tn_doc_customer_name', 'tn_status' => '_tn_doc_status'];
        if (isset($map[$column])) {
            $value = (string) get_post_meta($post_id, $map[$column], true);
            echo esc_html($value !== '' ? $value : '—');
            return;
        }
        if ($column === 'tn_total') {
            $total = (int) get_post_meta($post_id, '_tn_doc_total', true);
            echo esc_html($total > 0 ? self::format_rials($total) : '—');
        }
    }

    public function row_actions(array $actions, $post): array {
        if (! $post instanceof WP_Post || ! current_user_can('manage_woocommerce')) {
            return $actions;
        }
        if ($post->post_type === 'tn_inquiry' && get_post_status($post) !== 'trash') {
            $actions['tn_quote'] = sprintf(
                '<a href="%s">%s</a>',
                esc_url(wp_nonce_url(admin_url('admin-post.php?action=tehnet_quote_from_inquiry&inquiry_id=' . $post->ID), 'tehnet_quote_from_inquiry_' . $post->ID)),
                esc_html__('ساخت پیش‌فاکتور', 'tehnet-core')
            );
        }
        if ($post->post_type === self::QUOTE_TYPE && (string) get_post_meta($post->ID, '_tn_doc_status', true) === 'accepted') {
            $actions['tn_invoice'] = sprintf(
                '<a href="%s">%s</a>',
                esc_url(wp_nonce_url(admin_url('admin-post.php?action=tehnet_invoice_from_quote&quote_id=' . $post->ID), 'tehnet_invoice_from_quote_' . $post->ID)),
                esc_html__('صدور فاکتور', 'tehnet-core')
            );
        }
        if (($post->post_type === self::QUOTE_TYPE || $post->post_type === self::INVOICE_TYPE) && get_post_status($post) !== 'trash') {
            $actions['tn_print'] = sprintf(
                '<a href="%s" target="_blank" rel="noopener">%s</a>',
                esc_url(wp_nonce_url(admin_url('admin-post.php?action=tehnet_doc_print&doc_id=' . $post->ID), 'tehnet_doc_print_' . $post->ID)),
                esc_html__('مشاهده و چاپ', 'tehnet-core')
            );
        }
        return $actions;
    }

    public function meta_boxes(): void {
        add_meta_box('tn_quote_details', __('جزئیات پیش‌فاکتور', 'tehnet-core'), [$this, 'render_quote_box'], self::QUOTE_TYPE, 'normal', 'high');
        add_meta_box('tn_invoice_details', __('جزئیات فاکتور', 'tehnet-core'), [$this, 'render_invoice_box'], self::INVOICE_TYPE, 'normal', 'high');
    }

    public function render_quote_box($post): void {
        $post_id = (int) ($post->ID ?? 0);
        wp_nonce_field('tehnet_save_quote', 'tn_quote_nonce');
        $this->render_items_editor($post_id, true);
        $this->render_customer_fields($post_id, true);
        $this->render_status_fields($post_id, 'quote');
    }

    public function render_invoice_box($post): void {
        $post_id = (int) ($post->ID ?? 0);
        wp_nonce_field('tehnet_save_invoice', 'tn_invoice_nonce');
        $items = json_decode((string) get_post_meta($post_id, '_tn_doc_items', true), true) ?: [];
        $totals = [
            'subtotal' => (int) get_post_meta($post_id, '_tn_doc_subtotal', true),
            'discount' => (int) get_post_meta($post_id, '_tn_doc_discount', true),
            'shipping' => (int) get_post_meta($post_id, '_tn_doc_shipping', true),
            'total' => (int) get_post_meta($post_id, '_tn_doc_total', true),
        ];
        echo '<table class="widefat striped"><thead><tr><th>' . esc_html__('شرح', 'tehnet-core') . '</th><th>' . esc_html__('تعداد', 'tehnet-core') . '</th><th>' . esc_html__('مبلغ واحد', 'tehnet-core') . '</th></tr></thead><tbody>';
        if ($items === []) {
            echo '<tr><td colspan="3">—</td></tr>';
        }
        foreach ($items as $item) {
            printf(
                '<tr><td>%s</td><td>%d</td><td>%s</td></tr>',
                esc_html((string) ($item['description'] ?? '')),
                (int) ($item['qty'] ?? 0),
                esc_html(self::format_rials((int) ($item['unit_price'] ?? 0)))
            );
        }
        echo '</tbody></table>';
        printf('<p>%s: <strong>%s</strong></p>', esc_html__('جمع کل', 'tehnet-core'), esc_html(self::format_rials($totals['total'])));
        $this->render_customer_fields($post_id, false);
        $payment_ref = (string) get_post_meta($post_id, '_tn_doc_payment_ref', true);
        printf(
            '<p><label>%s<input type="text" name="tn_payment_ref" value="%s" maxlength="190"></label></p>',
            esc_html__('مرجع پرداخت (دستی)', 'tehnet-core'),
            esc_attr($payment_ref)
        );
        $this->render_status_fields($post_id, 'invoice');
    }

    private function render_items_editor(int $post_id, bool $editable): void {
        $items = json_decode((string) get_post_meta($post_id, '_tn_doc_items', true), true) ?: [];
        $discount = (string) get_post_meta($post_id, '_tn_doc_discount', true);
        $shipping = (string) get_post_meta($post_id, '_tn_doc_shipping', true);
        $rows = max(4, count($items) + 1);
        echo '<table class="widefat striped tn-items"><thead><tr><th>' . esc_html__('شرح کالا/خدمت', 'tehnet-core') . '</th><th>' . esc_html__('تعداد', 'tehnet-core') . '</th><th>' . esc_html__('مبلغ واحد (ریال)', 'tehnet-core') . '</th></tr></thead><tbody>';
        for ($i = 0; $i < $rows; $i++) {
            $item = $items[$i] ?? [];
            printf(
                '<tr><td><input type="text" name="tn_item_desc[]" value="%s" maxlength="190" style="width:100%%"></td><td><input type="number" name="tn_item_qty[]" value="%s" min="1" max="99" step="1" style="width:5em"></td><td><input type="text" name="tn_item_price[]" value="%s" inputmode="numeric" style="width:9em"></td></tr>',
                esc_attr((string) ($item['description'] ?? '')),
                esc_attr((string) ($item['qty'] ?? '')),
                esc_attr((string) ($item['unit_price'] ?? ''))
            );
        }
        echo '</tbody></table>';
        printf(
            '<p><label>%s <input type="text" name="tn_discount" value="%s" inputmode="numeric" style="width:9em"></label> &nbsp; <label>%s <input type="text" name="tn_shipping" value="%s" inputmode="numeric" style="width:9em"></label></p>',
            esc_html__('تخفیف (ریال)', 'tehnet-core'),
            esc_attr($discount),
            esc_html__('ارسال (ریال)', 'tehnet-core'),
            esc_attr($shipping)
        );
    }

    private function render_customer_fields(int $post_id, bool $editable): void {
        $name = (string) get_post_meta($post_id, '_tn_doc_customer_name', true);
        $mobile = (string) get_post_meta($post_id, '_tn_doc_mobile', true);
        $email = (string) get_post_meta($post_id, '_tn_doc_email', true);
        if ($editable) {
            printf(
                '<p><label>%s <input type="text" name="tn_customer_name" value="%s" maxlength="120"></label> <label>%s <input type="tel" name="tn_mobile" value="%s" maxlength="20"></label> <label>%s <input type="email" name="tn_email" value="%s" maxlength="190"></label></p>',
                esc_html__('نام مشتری', 'tehnet-core'),
                esc_attr($name),
                esc_html__('موبایل', 'tehnet-core'),
                esc_attr($mobile),
                esc_html__('ایمیل', 'tehnet-core'),
                esc_attr($email)
            );
        } else {
            printf('<p>%s: %s — %s</p>', esc_html__('مشتری', 'tehnet-core'), esc_html($name . ' / ' . $mobile), esc_html($email));
        }
    }

    private function render_status_fields(int $post_id, string $type): void {
        $current = (string) get_post_meta($post_id, '_tn_doc_status', true);
        if ($current === '') {
            $current = $type === 'invoice' ? 'issued' : 'new';
        }
        $options = [$current];
        foreach (self::TRANSITIONS[$type][$current] ?? [] as $next) {
            $options[] = $next;
        }
        printf('<p><label>%s <select name="tn_doc_status">', esc_html__('وضعیت', 'tehnet-core'));
        foreach ($options as $status) {
            printf('<option value="%s"%s>%s</option>', esc_attr($status), selected($status, $current, false), esc_html(self::label($type, $status)));
        }
        echo '</select></label>';
        if ($type === 'quote' && $current === 'accepted') {
            echo '<br><br>' . sprintf(
                '<a class="button button-primary" href="%s">%s</a>',
                esc_url(wp_nonce_url(admin_url('admin-post.php?action=tehnet_invoice_from_quote&quote_id=' . $post_id), 'tehnet_invoice_from_quote_' . $post_id)),
                esc_html__('صدور فاکتور از این پیش‌فاکتور', 'tehnet-core')
            );
        }
        echo '<br>' . sprintf(
            '<a class="button" href="%s" target="_blank" rel="noopener">%s</a>',
            esc_url(wp_nonce_url(admin_url('admin-post.php?action=tehnet_doc_print&doc_id=' . $post_id), 'tehnet_doc_print_' . $post_id)),
            esc_html__('مشاهده و چاپ سند', 'tehnet-core')
        );
        $log = json_decode((string) get_post_meta($post_id, '_tn_doc_status_log', true), true) ?: [];
        if ($log !== []) {
            echo '<ul class="tn-status-log">';
            foreach ($log as $entry) {
                printf('<li>%s: %s → %s</li>', esc_html((string) ($entry['at'] ?? '')), esc_html(self::label($type, (string) ($entry['from'] ?? ''))), esc_html(self::label($type, (string) ($entry['to'] ?? ''))));
            }
            echo '</ul>';
        }
        echo '</p>';
    }

    private function apply_status_change(int $post_id, string $type, string $next): void {
        $current = (string) get_post_meta($post_id, '_tn_doc_status', true);
        if ($current === '') {
            $current = $type === 'invoice' ? 'issued' : 'new';
        }
        if ($next === $current) {
            return;
        }
        if (! self::can_transition($type, $current, $next)) {
            return;
        }
        update_post_meta($post_id, '_tn_doc_status', $next);
        $log = json_decode((string) get_post_meta($post_id, '_tn_doc_status_log', true), true) ?: [];
        $log[] = ['at' => current_time('mysql'), 'from' => $current, 'to' => $next];
        update_post_meta($post_id, '_tn_doc_status_log', wp_json_encode($log));
        if ($type === 'invoice' && $next === 'paid') {
            update_post_meta($post_id, '_tn_doc_paid_at', current_time('mysql'));
        }
    }

    public function save_quote(int $post_id, $post): void {
        if (! isset($_POST['tn_quote_nonce']) || ! wp_verify_nonce(sanitize_key((string) $_POST['tn_quote_nonce']), 'tehnet_save_quote')) {
            return;
        }
        if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) {
            return;
        }
        if (! current_user_can('manage_woocommerce') || $post->post_type !== self::QUOTE_TYPE) {
            return;
        }
        $items = self::normalize_items(self::items_from_post($_POST));
        $totals = self::compute_totals($items, wp_unslash($_POST['tn_discount'] ?? '0'), wp_unslash($_POST['tn_shipping'] ?? '0'));
        if (is_wp_error($totals)) {
            return;
        }
        update_post_meta($post_id, '_tn_doc_items', wp_json_encode($totals['items']));
        update_post_meta($post_id, '_tn_doc_subtotal', $totals['subtotal']);
        update_post_meta($post_id, '_tn_doc_discount', $totals['discount']);
        update_post_meta($post_id, '_tn_doc_shipping', $totals['shipping']);
        update_post_meta($post_id, '_tn_doc_total', $totals['total']);
        update_post_meta($post_id, '_tn_doc_customer_name', sanitize_text_field(wp_unslash((string) ($_POST['tn_customer_name'] ?? ''))));
        $mobile = TehNet_Core_Inquiries::normalize_mobile((string) ($_POST['tn_mobile'] ?? ''));
        update_post_meta($post_id, '_tn_doc_mobile', $mobile);
        update_post_meta($post_id, '_tn_doc_email', sanitize_email(wp_unslash((string) ($_POST['tn_email'] ?? ''))));
        if ((string) get_post_meta($post_id, '_tn_doc_number', true) === '') {
            update_post_meta($post_id, '_tn_doc_number', self::build_number('quote', $post_id, current_time('Ymd')));
        }
        $next = sanitize_key((string) ($_POST['tn_doc_status'] ?? ''));
        if ($next === 'sent' && ! self::ready_to_send($totals)) {
            return;
        }
        $this->apply_status_change($post_id, 'quote', $next);
    }

    public function save_invoice(int $post_id, $post): void {
        if (! isset($_POST['tn_invoice_nonce']) || ! wp_verify_nonce(sanitize_key((string) $_POST['tn_invoice_nonce']), 'tehnet_save_invoice')) {
            return;
        }
        if (defined('DOING_AUTOSAVE') && DOING_AUTOSAVE) {
            return;
        }
        if (! current_user_can('manage_woocommerce') || $post->post_type !== self::INVOICE_TYPE) {
            return;
        }
        update_post_meta($post_id, '_tn_doc_payment_ref', sanitize_text_field(wp_unslash((string) ($_POST['tn_payment_ref'] ?? ''))));
        $this->apply_status_change($post_id, 'invoice', sanitize_key((string) ($_POST['tn_doc_status'] ?? '')));
    }

    private function copy_customer_meta(int $source_id, int $target_id, array $extra = []): void {
        foreach (['_tn_customer_name' => '_tn_doc_customer_name', '_tn_mobile' => '_tn_doc_mobile', '_tn_email' => '_tn_doc_email'] as $from_key => $to_key) {
            update_post_meta($target_id, $to_key, (string) get_post_meta($source_id, $from_key, true));
        }
        foreach ($extra as $key => $value) {
            update_post_meta($target_id, $key, $value);
        }
    }

    public function create_quote_from_inquiry(): void {
        if (! current_user_can('manage_woocommerce')) {
            wp_die(__('دسترسی مجاز نیست.', 'tehnet-core'), 403);
        }
        $inquiry_id = absint($_GET['inquiry_id'] ?? 0);
        check_admin_referer('tehnet_quote_from_inquiry_' . $inquiry_id);
        $inquiry = get_post($inquiry_id);
        $fallback = (string) admin_url('edit.php?post_type=tn_inquiry');
        if (! $inquiry || $inquiry->post_type !== 'tn_inquiry') {
            wp_safe_redirect(add_query_arg('tn_doc_notice', 'missing_inquiry', $fallback));
            exit;
        }
        $existing = (int) get_post_meta($inquiry_id, '_tn_inquiry_quote_id', true);
        if ($existing > 0 && get_post_status($existing) !== false) {
            wp_safe_redirect((string) get_edit_post_link($existing, 'raw'));
            exit;
        }
        $quote_id = wp_insert_post([
            'post_type' => self::QUOTE_TYPE,
            'post_status' => 'private',
            'post_title' => sprintf('پیش‌فاکتور — %s', (string) get_post_meta($inquiry_id, '_tn_customer_name', true)),
        ], true);
        if (is_wp_error($quote_id)) {
            wp_safe_redirect(add_query_arg('tn_doc_notice', 'error', $fallback));
            exit;
        }
        $product_name = (string) get_post_meta($inquiry_id, '_tn_product_name', true);
        $quantity = (int) get_post_meta($inquiry_id, '_tn_quantity', true);
        $items = $product_name !== '' ? [['description' => $product_name, 'qty' => max(1, $quantity), 'unit_price' => 0]] : [];
        $this->copy_customer_meta($inquiry_id, (int) $quote_id, [
            '_tn_doc_items' => wp_json_encode($items),
            '_tn_doc_status' => 'new',
            '_tn_doc_status_log' => wp_json_encode([]),
            '_tn_doc_inquiry_id' => $inquiry_id,
            '_tn_doc_number' => self::build_number('quote', (int) $quote_id, current_time('Ymd')),
        ]);
        update_post_meta($inquiry_id, '_tn_inquiry_quote_id', $quote_id);
        wp_safe_redirect(add_query_arg('tn_doc_notice', 'quote_created', (string) get_edit_post_link((int) $quote_id, 'raw')));
        exit;
    }

    public function create_invoice_from_quote(): void {
        if (! current_user_can('manage_woocommerce')) {
            wp_die(__('دسترسی مجاز نیست.', 'tehnet-core'), 403);
        }
        $quote_id = absint($_GET['quote_id'] ?? 0);
        check_admin_referer('tehnet_invoice_from_quote_' . $quote_id);
        $quote = get_post($quote_id);
        $fallback = (string) admin_url('edit.php?post_type=' . self::QUOTE_TYPE);
        if (! $quote || $quote->post_type !== self::QUOTE_TYPE) {
            wp_safe_redirect(add_query_arg('tn_doc_notice', 'missing_quote', $fallback));
            exit;
        }
        if ((string) get_post_meta($quote_id, '_tn_doc_status', true) !== 'accepted') {
            wp_safe_redirect(add_query_arg('tn_doc_notice', 'quote_not_accepted', (string) get_edit_post_link($quote_id, 'raw')));
            exit;
        }
        $existing = (int) get_post_meta($quote_id, '_tn_quote_invoice_id', true);
        if ($existing > 0 && get_post_status($existing) !== false) {
            wp_safe_redirect((string) get_edit_post_link($existing, 'raw'));
            exit;
        }
        $invoice_id = wp_insert_post([
            'post_type' => self::INVOICE_TYPE,
            'post_status' => 'private',
            'post_title' => sprintf('فاکتور — %s', (string) get_post_meta($quote_id, '_tn_doc_customer_name', true)),
        ], true);
        if (is_wp_error($invoice_id)) {
            wp_safe_redirect(add_query_arg('tn_doc_notice', 'error', (string) get_edit_post_link($quote_id, 'raw')));
            exit;
        }
        $copy_keys = ['_tn_doc_items', '_tn_doc_subtotal', '_tn_doc_discount', '_tn_doc_shipping', '_tn_doc_total', '_tn_doc_customer_name', '_tn_doc_mobile', '_tn_doc_email', '_tn_doc_inquiry_id'];
        $payload = ['_tn_doc_status' => 'issued', '_tn_doc_status_log' => wp_json_encode([]), '_tn_doc_quote_id' => $quote_id, '_tn_doc_number' => self::build_number('invoice', (int) $invoice_id, current_time('Ymd'))];
        foreach ($copy_keys as $key) {
            $payload[$key] = get_post_meta($quote_id, $key, true);
        }
        foreach ($payload as $key => $value) {
            update_post_meta((int) $invoice_id, $key, $value);
        }
        update_post_meta($quote_id, '_tn_quote_invoice_id', $invoice_id);
        wp_safe_redirect(add_query_arg('tn_doc_notice', 'invoice_created', (string) get_edit_post_link((int) $invoice_id, 'raw')));
        exit;
    }

    public function render_print_view(): void {
        if (! current_user_can('manage_woocommerce')) {
            wp_die(__('دسترسی مجاز نیست.', 'tehnet-core'), 403);
        }
        $doc_id = absint($_GET['doc_id'] ?? 0);
        check_admin_referer('tehnet_doc_print_' . $doc_id);
        $post = get_post($doc_id);
        if (! $post || ! in_array($post->post_type, [self::QUOTE_TYPE, self::INVOICE_TYPE], true) || get_post_status($post) === 'trash') {
            wp_die(__('سند یافت نشد.', 'tehnet-core'), 404);
        }
        $type = $post->post_type === self::INVOICE_TYPE ? 'invoice' : 'quote';
        $items = json_decode((string) get_post_meta($doc_id, '_tn_doc_items', true), true);
        $data = [
            'type' => $type,
            'number' => (string) get_post_meta($doc_id, '_tn_doc_number', true),
            'status' => (string) get_post_meta($doc_id, '_tn_doc_status', true) ?: ($type === 'invoice' ? 'issued' : 'new'),
            'date_fa' => self::jalali_from_mysql((string) $post->post_date),
            'items' => is_array($items) ? $items : [],
            'subtotal' => (int) get_post_meta($doc_id, '_tn_doc_subtotal', true),
            'discount' => (int) get_post_meta($doc_id, '_tn_doc_discount', true),
            'shipping' => (int) get_post_meta($doc_id, '_tn_doc_shipping', true),
            'total' => (int) get_post_meta($doc_id, '_tn_doc_total', true),
            'customer_name' => (string) get_post_meta($doc_id, '_tn_doc_customer_name', true),
            'mobile' => self::to_persian_digits((string) get_post_meta($doc_id, '_tn_doc_mobile', true)),
            'email' => (string) get_post_meta($doc_id, '_tn_doc_email', true),
            'inquiry_id' => (int) get_post_meta($doc_id, '_tn_doc_inquiry_id', true),
            'quote_id' => (int) get_post_meta($doc_id, '_tn_doc_quote_id', true),
            'payment_ref' => (string) get_post_meta($doc_id, '_tn_doc_payment_ref', true),
            'paid_at_fa' => self::jalali_from_mysql((string) get_post_meta($doc_id, '_tn_doc_paid_at', true)),
            'business_name' => TehNet_Core_Settings::value('tehnet_business_name'),
            'phone' => self::to_persian_digits(TehNet_Core_Settings::value('tehnet_phone')),
            'address' => TehNet_Core_Settings::value('tehnet_address'),
            'youtube' => TehNet_Core_Settings::value('tehnet_youtube_url'),
            'site' => home_url('/'),
        ];
        $data['logo_url'] = file_exists(TEHNET_CORE_DIR . 'assets/img/tehnet-logo.jpg')
            ? plugins_url('assets/img/tehnet-logo.jpg', TEHNET_CORE_FILE)
            : '';
        nocache_headers();
        header('Content-Type: text/html; charset=utf-8');
        $this->render_print_html($data);
        exit;
    }

    private function render_print_html(array $d): void {
        $is_invoice = $d['type'] === 'invoice';
        $title = $is_invoice ? 'فاکتور فروش' : 'پیش‌فاکتور';
        $e = static fn($v): string => esc_html((string) $v);
        ?><!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex,nofollow">
<title><?php echo $e($title . ' ' . $d['number']); ?></title>
<style>
  :root { --blue:#0b4f8a; --turq:#16c7c4; --ink:#102231; --muted:#5d7182; --border:#d7e3ec; --surface:#f5f9fc; }
  * { box-sizing: border-box; }
  body { margin:0; background:#e9eef3; color:var(--ink); font-family:Tahoma,Arial,sans-serif; line-height:1.9; }
  .page { max-width:820px; margin:24px auto; background:#fff; padding:36px 40px; box-shadow:0 12px 34px rgba(9,52,89,.14); }
  .letterhead { display:flex; align-items:center; justify-content:space-between; gap:16px; }
  .letterhead img.logo { width:96px; height:96px; border-radius:16px; object-fit:cover; }
  .brand h1 { margin:0; font-size:21px; color:var(--blue); }
  .brand p { margin:2px 0; font-size:12.5px; color:var(--muted); }
  .accent { height:5px; border-radius:99px; background:linear-gradient(270deg,var(--blue),var(--turq)); margin:14px 0 20px; }
  .docmeta { display:flex; justify-content:space-between; align-items:flex-start; gap:16px; }
  .doc-title { font-size:19px; font-weight:bold; color:var(--blue); }
  .doc-title small { display:block; color:var(--muted); font-weight:normal; font-size:12px; }
  .status-badge { display:inline-block; padding:2px 12px; border-radius:99px; background:var(--surface); border:1px solid var(--border); color:var(--blue); font-size:12px; }
  .party { margin:18px 0; padding:12px 16px; background:var(--surface); border:1px solid var(--border); border-radius:12px; font-size:13px; }
  .party b { color:var(--blue); }
  table.items { width:100%; border-collapse:collapse; margin-top:8px; font-size:13px; }
  table.items th { background:var(--blue); color:#fff; padding:8px 10px; text-align:right; }
  table.items td { border-bottom:1px solid var(--border); padding:8px 10px; }
  table.items tr:nth-child(even) td { background:var(--surface); }
  td.num, th.num { text-align:center; width:44px; }
  td.qty, th.qty { text-align:center; width:70px; }
  td.price, th.price { text-align:left; width:150px; direction:ltr; }
  .totals { margin-top:14px; margin-inline-start:auto; width:320px; font-size:13px; }
  .totals div { display:flex; justify-content:space-between; padding:5px 12px; border-bottom:1px dashed var(--border); }
  .totals .grand { font-weight:bold; color:var(--blue); background:var(--surface); border-radius:8px; border-bottom:none; margin-top:4px; }
  .refline { margin-top:16px; font-size:12.5px; color:var(--muted); }
  .sign { display:flex; justify-content:space-between; margin-top:48px; font-size:13px; }
  .sign div { width:220px; text-align:center; border-top:1px solid var(--ink); padding-top:8px; }
  .foot { margin-top:28px; text-align:center; font-size:11.5px; color:var(--muted); }
  .printbar { position:fixed; bottom:16px; inset-inline-start:16px; }
  .printbar button { background:var(--blue); color:#fff; border:none; border-radius:99px; padding:10px 26px; font-family:inherit; font-size:14px; cursor:pointer; }
  @media print {
    body { background:#fff; }
    .page { margin:0; box-shadow:none; max-width:none; padding:0; }
    .printbar { display:none; }
    @page { margin: 14mm 12mm; }
  }
</style>
</head>
<body>
<div class="page">
  <div class="letterhead">
    <?php if ($d['logo_url'] !== '') : ?><img class="logo" src="<?php echo esc_url($d['logo_url']); ?>" alt="<?php echo $e($d['business_name']); ?>"><?php endif; ?>
    <div class="brand" style="margin-inline-start:auto; text-align:left;">
      <h1><?php echo $e($d['business_name']); ?></h1>
      <p><?php echo $e($d['address']); ?></p>
      <p>تلفن: <?php echo TehNet_Core_Settings::phone_html($d['phone']); ?> — <?php echo $e($d['site']); ?></p>
    </div>
  </div>
  <div class="accent"></div>
  <div class="docmeta">
    <div class="doc-title"><?php echo $e($title); ?> <span class="status-badge"><?php echo $e(self::label($d['type'], $d['status'])); ?></span>
      <small>شماره سند: <?php echo $e(self::to_persian_digits($d['number'])); ?></small>
    </div>
    <div style="font-size:12.5px; color:var(--muted); text-align:left;">
      تاریخ صدور: <?php echo $e($d['date_fa']); ?>
      <?php if ($is_invoice && $d['paid_at_fa'] !== '') : ?><br>تاریخ پرداخت: <?php echo $e($d['paid_at_fa']); ?><?php endif; ?>
    </div>
  </div>
  <div class="party">
    <b>مشتری:</b> <?php echo $e($d['customer_name'] !== '' ? $d['customer_name'] : '—'); ?>
    <?php if ($d['mobile'] !== '') : ?> — موبایل: <?php echo $e($d['mobile']); ?><?php endif; ?>
    <?php if ($d['email'] !== '') : ?> — ایمیل: <?php echo $e($d['email']); ?><?php endif; ?>
    <?php if (! $is_invoice && $d['inquiry_id'] > 0) : ?><br><b>استعلام مرتبط:</b> #<?php echo $e(self::to_persian_digits((string) $d['inquiry_id'])); ?><?php endif; ?>
    <?php if ($is_invoice && $d['quote_id'] > 0) : ?><br><b>پیش‌فاکتور مرتبط:</b> <?php echo $e(self::to_persian_digits((string) $d['quote_id'])); ?><?php endif; ?>
    <?php if ($is_invoice && $d['payment_ref'] !== '') : ?><br><b>مرجع پرداخت:</b> <?php echo $e($d['payment_ref']); ?><?php endif; ?>
  </div>
  <table class="items">
    <thead><tr><th class="num">#</th><th>شرح کالا/خدمت</th><th class="qty">تعداد</th><th class="price">مبلغ واحد (ریال)</th></tr></thead>
    <tbody>
    <?php if ($d['items'] === []) : ?>
      <tr><td class="num">—</td><td colspan="3">قلمی ثبت نشده است.</td></tr>
    <?php else : foreach ($d['items'] as $i => $item) : ?>
      <tr>
        <td class="num"><?php echo $e(self::to_persian_digits((string) ($i + 1))); ?></td>
        <td><?php echo $e($item['description'] ?? ''); ?></td>
        <td class="qty"><?php echo $e(self::to_persian_digits((string) ($item['qty'] ?? 0))); ?></td>
        <td class="price"><?php echo $e(self::format_rials_fa((int) ($item['unit_price'] ?? 0))); ?></td>
      </tr>
    <?php endforeach; endif; ?>
    </tbody>
  </table>
  <div class="totals">
    <div><span>جمع کل اقلام</span><span><?php echo $e(self::format_rials_fa($d['subtotal'])); ?></span></div>
    <?php if ($d['discount'] > 0) : ?><div><span>تخفیف</span><span><?php echo $e(self::format_rials_fa($d['discount'])); ?></span></div><?php endif; ?>
    <?php if ($d['shipping'] > 0) : ?><div><span>هزینه ارسال</span><span><?php echo $e(self::format_rials_fa($d['shipping'])); ?></span></div><?php endif; ?>
    <div class="grand"><span>مبلغ قابل پرداخت</span><span><?php echo $e(self::format_rials_fa($d['total'])); ?></span></div>
  </div>
  <?php if (! $is_invoice) : ?>
    <p class="refline">اعتبار این پیش‌فاکتور تا ۳ روز کاری از تاریخ صدور است. قیمت‌ها بر اساس قیمت روز بازار و نهایی شدن سفارش قابل تغییر هستند.</p>
  <?php else : ?>
    <p class="refline">این فاکتور به‌صورت الکترونیکی صادر شده است. لطفاً هنگام پرداخت شماره فاکتور را ذکر کنید.</p>
  <?php endif; ?>
  <div class="sign">
    <div><?php do_action('tehnet_invoice_stamp',$d); ?>مهر و امضای فروشنده</div>
    <div>امضای خریدار</div>
  </div>
  <div class="foot"><?php echo $e($d['business_name']); ?> — <?php echo $e($d['address']); ?> — تلفن <?php echo TehNet_Core_Settings::phone_html($d['phone']); ?><br><?php echo $e($d['youtube']); ?></div>
</div>
<div class="printbar"><button onclick="window.print()">چاپ / ذخیره PDF</button></div>
</body>
</html><?php
    }

    public function admin_styles(): void {
        echo '<style>.tn-status-log{margin-top:8px;color:#666;font-size:12px;list-style:disc;padding-inline-start:18px}.tn-items input{width:100%}</style>';
    }
}
