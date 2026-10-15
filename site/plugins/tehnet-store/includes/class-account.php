<?php
defined('ABSPATH') || exit;

final class TehNet_Store_Account {
    public static function can_access(WC_Order $order,int $user_id): bool {
        return $user_id>0 && ((int)$order->get_customer_id()===$user_id || user_can($user_id,'manage_woocommerce'));
    }
    public function register(): void {
        add_action('tehnet_invoice_stamp',[self::class,'stamp']);
        add_action('woocommerce_order_details_after_order_table',[$this,'details']);
        add_action('admin_post_tn_store_invoice',[$this,'invoice']);
        add_action('admin_post_tn_store_return_request',[$this,'return_request']);
    }
    public static function stamp(): void {
        echo '<img src="'.esc_url(plugins_url('assets/invoice-stamp.svg',dirname(__DIR__).'/tehnet-store.php')).'" alt="مهر تهران نتورک" style="display:block;width:58mm;max-width:100%;height:auto;margin:8mm 0;break-inside:avoid">';
    }
    public function details($order): void {
        if (!$order instanceof WC_Order || !self::can_access($order,get_current_user_id())) { return; }
        if (isset($_GET['tn_return']) && $_GET['tn_return']==='requested') { echo '<p role="status">درخواست بررسی مرجوعی ثبت شد؛ تأیید و استرداد پس از بررسی انجام می‌شود.</p>'; }
        $tracking=$order->get_meta('_tn_tracking_reference');
        if ($tracking) { echo '<p>کد رهگیری حمل: <bdi>'.esc_html($tracking).'</bdi></p>'; }
        if ($order->get_meta('_tn_erp_invoice')) {
            $url=wp_nonce_url(add_query_arg(['action'=>'tn_store_invoice','order_id'=>$order->get_id()],admin_url('admin-post.php')),'tn_invoice_'.$order->get_id());
            echo '<p><a class="button" href="'.esc_url($url).'">مشاهده فاکتور شماره‌دار</a></p>';
        }
        if ($order->get_meta('_tn_erp_delivery_note')) {
            echo '<details><summary>درخواست بررسی مرجوعی</summary><p>ثبت درخواست به معنی تأیید مرجوعی یا استرداد وجه نیست؛ پشتیبانی شرایط و مقدار کالا را بررسی می‌کند.</p><form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';
            wp_nonce_field('tn_return_'.$order->get_id());
            echo '<input type="hidden" name="action" value="tn_store_return_request"><input type="hidden" name="order_id" value="'.esc_attr($order->get_id()).'"><label>کالا، مقدار و علت درخواست <textarea name="reason" maxlength="2000" required></textarea></label><button class="button" type="submit">ثبت درخواست بررسی</button></form></details>';
        }
    }
    private function authorized_order(string $nonce_action): WC_Order {
        $raw=$_REQUEST['order_id']??null;
        $order=is_scalar($raw)?wc_get_order(absint($raw)):false;
        if (!$order instanceof WC_Order || !self::can_access($order,get_current_user_id())) { wp_die('این سفارش در دسترس شما نیست.',403); }
        check_admin_referer($nonce_action.$order->get_id());
        return $order;
    }
    public function return_request(): void {
        $order=$this->authorized_order('tn_return_');
        if (!$order->get_meta('_tn_erp_delivery_note')) { wp_die('سند تحویل برای بررسی مرجوعی لازم است.',400); }
        $reason=isset($_POST['reason']) && is_string($_POST['reason'])?sanitize_textarea_field(wp_unslash($_POST['reason'])):'';
        if ($reason==='' || mb_strlen($reason)>2000) { wp_die('شرح معتبر درخواست لازم است.',400); }
        $requests=$order->get_meta('_tn_return_requests');$requests=is_array($requests)?$requests:[];
        if (count($requests)>=20) { wp_die('برای ادامه درخواست با پشتیبانی تماس بگیرید.',429); }
        $requests[]=['at'=>gmdate('c'),'user'=>get_current_user_id(),'reason'=>$reason,'state'=>'requested'];
        $order->update_meta_data('_tn_return_requests',$requests);$order->save();
        $order->add_order_note('درخواست بررسی مرجوعی مشتری: '.$reason);
        wp_safe_redirect(add_query_arg('tn_return','requested',$order->get_view_order_url()));exit;
    }
    public function invoice(): void {
        $order=$this->authorized_order('tn_invoice_');
        try { $invoice=(new TehNet_Store_ERP())->invoice_document($order); }
        catch (RuntimeException $e) { wp_die('فاکتور موقتاً در دسترس نیست؛ دوباره تلاش کنید.',503); }
        nocache_headers();header('Content-Type: text/html; charset=utf-8');header('X-Robots-Tag: noindex, nofollow');
        echo '<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>فاکتور تهران نتورک</title><style>body{font:16px/1.8 Tahoma,sans-serif;max-width:900px;margin:32px auto;padding:20px;color:#142c3c}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:10px;text-align:right}button{padding:12px}@media print{button{display:none}}</style><h1>فاکتور تهران نتورک</h1><p>شماره: <bdi>'.esc_html($invoice['invoice']).'</bdi> | تاریخ: '.esc_html($invoice['date']).'</p><p>سفارش: '.esc_html($order->get_order_number()).' | مشتری: '.esc_html($order->get_formatted_billing_full_name()).'</p><table><tr><th>کالا</th><th>مقدار</th><th>واحد</th><th>مبلغ خالص، ریال</th></tr>';
        foreach ($invoice['items'] as $line) { echo '<tr><td>'.esc_html($line['name']).'</td><td>'.esc_html($line['qty']).'</td><td>'.esc_html($line['uom']).'</td><td>'.esc_html($line['amount_irr']).'</td></tr>'; }
        echo '</table><p>تخفیف اعمال‌شده: '.esc_html($invoice['discount_irr']).' ریال | ارسال: '.esc_html($invoice['shipping_irr']).' ریال</p><p><strong>جمع فاکتور: '.esc_html($invoice['amount_irr']).' ریال</strong></p><p>این نسخه نمایش سند ثبت‌شده ERP است؛ تأیید الزامات و شناسه‌های صورتحساب مالیاتی جداگانه انجام می‌شود.</p>';
        self::stamp();
        echo '<button onclick="window.print()">چاپ فاکتور</button></html>';exit;
    }
}
