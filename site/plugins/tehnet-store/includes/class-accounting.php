<?php
defined('ABSPATH') || exit;

/** Accounting overview and local invoice numbering. ERPNext stays the ledger of record; this class only projects shop-side state. */
final class TehNet_Store_Accounting {
    public const PROFILE_OPTION = 'tn_accounting_profile';
    public const SEQ_OPTION = 'tn_invoice_sequence';

    public static function profile(): array {
        $profile = get_option(self::PROFILE_OPTION, []);
        if (!is_array($profile)) { return []; }
        return [
            'legal_name' => (string)($profile['legal_name'] ?? ''),
            'economic_code' => (string)($profile['economic_code'] ?? ''),
            'address' => (string)($profile['address'] ?? ''),
        ];
    }

    /** Gregorian -> Jalali (integer algorithm, no external dependency). */
    public static function jalali(int $gy, int $gm, int $gd): array {
        $g_d_m = [0,31,59,90,120,151,181,212,243,273,304,334];
        $jy = $gy <= 1600 ? 0 : 979;
        $gy = $gy <= 1600 ? $gy - 621 : $gy - 1600;
        $gy2 = $gm > 2 ? $gy + 1 : $gy;
        $days = 365*$gy + intdiv($gy2+3,4) - intdiv($gy2+99,100) + intdiv($gy2+399,400) - 80 + $gd + $g_d_m[$gm-1];
        $jy += 33*intdiv($days,12053); $days %= 12053;
        $jy += 4*intdiv($days,1461); $days %= 1461;
        if ($days > 365) { $jy += intdiv($days-1,365); $days = ($days-1) % 365; }
        return [$jy, $days < 186 ? 1+intdiv($days,31) : 7+intdiv($days-186,30), 1+($days < 186 ? $days%31 : ($days-186)%30)];
    }

    /** "1405/08/03" for an ISO-ish date string; returns "" when unparsable. */
    public static function jalali_date(string $date): string {
        if (!preg_match('/^(\d{4})-(\d{2})-(\d{2})/D',$date,$m)) { return ''; }
        [$jy,$jm,$jd] = self::jalali((int)$m[1],(int)$m[2],(int)$m[3]);
        return sprintf('%04d/%02d/%02d',$jy,$jm,$jd);
    }

    /** Idempotent sequential shop-side invoice copy number "TN-FA-<jalali year>-<seq>". */
    public static function local_invoice_number(WC_Order $order): string {
        $existing = $order->get_meta('_tn_local_invoice_no');
        if (is_string($existing) && $existing !== '') { return $existing; }
        $date = $order->get_date_paid() ?: $order->get_date_created();
        $iso = $date ? $date->date('Y-m-d') : gmdate('Y-m-d');
        [$jy] = self::jalali((int)substr($iso,0,4),(int)substr($iso,5,2),(int)substr($iso,8,2));
        $seq = (int)get_option(self::SEQ_OPTION,0) + 1;
        update_option(self::SEQ_OPTION,$seq,false);
        $number = sprintf('TN-FA-%d-%04d',$jy,$seq);
        $order->update_meta_data('_tn_local_invoice_no',$number);
        $order->update_meta_data('_tn_local_invoice_at',gmdate('c'));
        $order->save();
        return $number;
    }

    /** Read-only financial projection over recent orders; never mutates state. */
    public function summary(int $limit = 200): array {
        $rows = [];
        $totals = ['orders'=>0,'paid_irr'=>0,'invoiced'=>0,'settled'=>0,'refunds'=>0,'return_requests'=>0];
        foreach (wc_get_orders(['type'=>'shop_order','limit'=>$limit,'orderby'=>'date','order'=>'DESC']) as $order) {
            if (!$order instanceof WC_Order) { continue; }
            $total = (int)round((float)$order->get_total());
            $invoiced = $order->get_meta('_tn_erp_invoice') !== '' ? 1 : 0;
            $payment = $order->get_meta('_tn_erp_payment_entry') !== '' ? 1 : 0;
            $returns = is_array($order->get_meta('_tn_return_requests')) ? count($order->get_meta('_tn_return_requests')) : 0;
            $refunded = $order->get_total_refunded() > 0 ? 1 : 0;
            $totals['orders']++;
            if (in_array($order->get_status(),['processing','completed'],true)) { $totals['paid_irr'] += $total; }
            $totals['invoiced'] += $invoiced; $totals['settled'] += $payment;
            $totals['refunds'] += $refunded; $totals['return_requests'] += $returns;
            $rows[] = [
                'order'=>$order->get_order_number(),
                'status'=>wc_get_order_status_name($order->get_status()),
                'total_irr'=>$total,
                'erp_state'=>(string)$order->get_meta('_tn_erp_state'),
                'erp_invoice'=>(string)$order->get_meta('_tn_erp_invoice'),
                'payment_entry'=>(string)$order->get_meta('_tn_erp_payment_entry'),
                'local_invoice'=>(string)$order->get_meta('_tn_local_invoice_no'),
                'refunded'=>$refunded,'returns'=>$returns,
            ];
        }
        return ['totals'=>$totals,'rows'=>$rows];
    }

    public function register(): void {
        add_action('admin_menu',function():void {
            add_submenu_page('tn-store','حسابداری فروشگاه','حسابداری','tn_store_settle','tn-store-accounting',[$this,'page']);
        });
        add_action('admin_post_tn_accounting_profile',[$this,'save_profile']);
    }

    public function save_profile(): void {
        if (!current_user_can('tn_store_settle')) { wp_die('دسترسی مجاز نیست.',403); }
        check_admin_referer('tn_accounting_profile');
        $profile = [];
        foreach (['legal_name'=>'sanitize_text_field','economic_code'=>'sanitize_text_field','address'=>'sanitize_text_field'] as $key=>$sanitize) {
            $raw = $_POST[$key] ?? '';
            $profile[$key] = is_string($raw) ? call_user_func($sanitize,wp_unslash($raw)) : '';
        }
        foreach (['legal_name'=>160,'economic_code'=>32,'address'=>300] as $key=>$max) {
            if (mb_strlen($profile[$key]) > $max) { $profile[$key] = mb_substr($profile[$key],0,$max); }
        }
        update_option(self::PROFILE_OPTION,$profile,false);
        wp_safe_redirect(add_query_arg(['page'=>'tn-store-accounting','tn_result'=>'ok'],admin_url('admin.php')));exit;
    }

    public function page(): void {
        if (!current_user_can('tn_store_settle')) { wp_die('دسترسی مجاز نیست.',403); }
        $summary = $this->summary();
        $profile = self::profile();
        echo '<div class="wrap" dir="rtl"><h1>حسابداری فروشگاه تهران نتورک</h1>';
        echo '<p>مرجع دفتر کل ERPNext است؛ این صفحه فقط تصویر وضعیت فروشگاه است و وجهی جابه‌جا نمی‌کند.</p>';
        if (isset($_GET['tn_result'])) { echo '<div class="notice notice-success inline"><p>پروفایل حقوقی ذخیره شد.</p></div>'; }
        echo '<h2>پروفایل حقوقی صادرکننده</h2><form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';
        wp_nonce_field('tn_accounting_profile');
        echo '<input type="hidden" name="action" value="tn_accounting_profile">';
        echo '<p><label>نام حقوقی <input name="legal_name" value="'.esc_attr($profile['legal_name']).'" size="50" maxlength="160"></label></p>';
        echo '<p><label>شناسه ملی / کد اقتصادی <input name="economic_code" value="'.esc_attr($profile['economic_code']).'" maxlength="32"></label></p>';
        echo '<p><label>نشانی ثبت‌شده <input name="address" value="'.esc_attr($profile['address']).'" size="70" maxlength="300"></label></p>';
        submit_button('ذخیره پروفایل حقوقی');
        echo '</form>';
        $t = $summary['totals'];
        echo '<h2>خلاصهٔ مالی</h2><ul>';
        echo '<li>سفارش‌های اخیر: '.(int)$t['orders'].'</li>';
        echo '<li>جمع سفارش‌های پرداخت‌شده/تکمیل‌شده: '.number_format($t['paid_irr']).' ریال</li>';
        echo '<li>فاکتور ثبت‌شدهٔ ERP: '.(int)$t['invoiced'].' | دریافت‌های تسویه‌شده: '.(int)$t['settled'].'</li>';
        echo '<li>سفارش‌های دارای استرداد: '.(int)$t['refunds'].' | درخواست مرجوعی باز: '.(int)$t['return_requests'].'</li>';
        echo '</ul>';
        echo '<h2>دفتر سفارش‌ها</h2><table class="widefat striped"><thead><tr><th>سفارش</th><th>وضعیت</th><th>مبلغ (ریال)</th><th>وضعیت ERP</th><th>فاکتور ERP</th><th>شمارهٔ محلی</th><th>دریافت</th><th>استرداد</th><th>درخواست مرجوعی</th></tr></thead><tbody>';
        foreach ($summary['rows'] as $row) {
            echo '<tr><td>'.esc_html($row['order']).'</td><td>'.esc_html($row['status']).'</td><td>'.esc_html(number_format($row['total_irr'])).'</td><td>'.esc_html($row['erp_state']).'</td><td><bdi>'.esc_html($row['erp_invoice']).'</bdi></td><td><bdi>'.esc_html($row['local_invoice']).'</bdi></td><td><bdi>'.esc_html($row['payment_entry']).'</bdi></td><td>'.($row['refunded']?'بله':'—').'</td><td>'.(int)$row['returns'].'</td></tr>';
        }
        echo '</tbody></table></div>';
    }
}
