<?php
defined('ABSPATH') || exit;

final class TehNet_Store_Operations {
    private const ACTIONS=['sync'=>'tn_store_sync','cancel'=>'tn_store_sync','dispatch'=>'tn_store_dispatch','refund'=>'tn_store_refund','settle'=>'tn_store_settle'];
    public static function install(): void {
        foreach (['tn_store_sales'=>['فروش تهران نتورک',['tn_store_sync']], 'tn_store_warehouse'=>['انبار تهران نتورک',['tn_store_dispatch']], 'tn_store_finance'=>['مالی تهران نتورک',['tn_store_refund','tn_store_settle']], 'tn_store_support'=>['پشتیبانی فروشگاه',[]]] as $key=>$definition) {
            $role=get_role($key)?:add_role($key,$definition[0],['read'=>true]);
            if ($role) { foreach (array_merge(['tn_store_operations_view'],$definition[1]) as $cap) { $role->add_cap($cap); } }
        }
        $admin=get_role('administrator');
        if ($admin) { foreach (array_unique(array_merge(['tn_store_operations_view'],array_values(self::ACTIONS))) as $cap) { $admin->add_cap($cap); } }
    }
    public function register(): void {
        add_action('admin_menu',function():void { add_menu_page('عملیات فروشگاه','عملیات فروشگاه','tn_store_operations_view','tn-store',[$this,'page'],'dashicons-store',57); });
        add_action('admin_post_tn_store_operation',[$this,'submit']);
    }
    public function page(): void {
        if (!current_user_can('tn_store_operations_view')) { wp_die('دسترسی مجاز نیست.',403); }
        echo '<div class="wrap" dir="rtl"><h1>عملیات فروشگاه تهران نتورک</h1>';
        if (current_user_can('manage_woocommerce')) {
            echo '<p><a class="button button-primary" href="'.esc_url(add_query_arg('tn_preview','1',wc_get_page_permalink('shop'))).'">مشاهده پیش‌نمایش خصوصی فروشگاه</a> <a class="button" href="'.esc_url(admin_url('edit.php?post_type=product')).'">مدیریت کالاها</a> <a class="button" href="'.esc_url(admin_url('admin.php?page=wc-orders')).'">مدیریت سفارش‌ها</a></p>';
        }
        $ready=(new TehNet_Store_ERP())->ready();
        if (!$ready) { echo '<div class="notice notice-warning inline"><p>اتصال عملیاتی انبار و حسابداری برقرار نیست؛ فروش فیزیکی و ثبت عملیات مالی غیرفعال است. کالاهای واردشده فقط پیش‌نویس و نیازمند تأیید قیمت، موجودی و مشخصات هستند.</p></div>'; }
        echo '<p>ارسال و مرجوعی را با گردش واقعی انبار انجام دهید. ثبت استرداد و تسویه فقط پس از تطبیق مدرک بانکی انجام می‌شود؛ این فرم وجهی جابه‌جا نمی‌کند.</p>';
        if (isset($_GET['tn_result'])) { echo '<div class="notice notice-info"><p>'.esc_html($_GET['tn_result']==='ok'?'عملیات تأیید و همگام شد.':'عملیات تأیید نشد؛ وضعیت سفارش و گزارش ERP را بررسی کنید.').'</p></div>'; }
        echo '<table class="widefat striped"><thead><tr><th>سفارش</th><th>وضعیت فروشگاه</th><th>وضعیت ERP</th><th>فاکتور</th><th>رهگیری</th><th>تطبیق</th><th>بررسی مرجوعی</th></tr></thead><tbody>';
        foreach (wc_get_orders(['type'=>'shop_order','limit'=>30,'orderby'=>'date','order'=>'DESC']) as $order) {
            if (!$order instanceof WC_Order) { continue; }
            echo '<tr><td>'.esc_html($order->get_order_number()).'</td><td>'.esc_html(wc_get_order_status_name($order->get_status())).'</td><td>'.esc_html($order->get_meta('_tn_erp_state')).'</td><td>'.esc_html($order->get_meta('_tn_erp_invoice')).'</td><td>'.esc_html($order->get_meta('_tn_tracking_reference')).'</td><td>'.esc_html($order->get_meta('_tn_erp_reconciliation')).'</td><td>';
            $requests=$order->get_meta('_tn_return_requests');
            if (is_array($requests) && $requests) {
                echo '<details><summary>درخواست‌ها ('.count($requests).')</summary>';
                foreach ($requests as $request) { echo '<p>'.esc_html($request['at'].' — '.$request['reason']).'</p>'; }
                echo '</details>';
            }
            echo '</td></tr>';
        }
        echo '</tbody></table>';
        $misses=get_option('tn_search_misses',[]);
        if (is_array($misses) && $misses) {
            arsort($misses,SORT_NUMERIC);
            echo '<h2>جستجوهای بی‌نتیجه (سیگنال کالای موردنیاز مشتری)</h2><table class="widefat striped"><thead><tr><th>عبارت</th><th>تعداد</th></tr></thead><tbody>';
            foreach (array_slice($misses,0,20,true) as $miss_term=>$miss_count) { echo '<tr><td>'.esc_html($miss_term).'</td><td>'.(int)$miss_count.'</td></tr>'; }
            echo '</tbody></table>';
        }
        if (!$ready) { echo '</div>';return; }
        echo '<h2>ثبت عملیات</h2><form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';
        wp_nonce_field('tn_store_operation');echo '<input type="hidden" name="action" value="tn_store_operation">';
        echo '<p><label>شماره داخلی سفارش <input type="number" name="order_id" min="1" required></label></p><p><label>عملیات <select name="operation">';
        foreach (['sync'=>'تطبیق وضعیت','cancel'=>'لغو سفارش پرداخت‌نشده','dispatch'=>'ثبت تحویل به حمل‌کننده','refund'=>'ثبت استرداد انجام‌شده','settle'=>'ثبت تسویه بانکی تأییدشده'] as $action=>$title) {
            if (current_user_can(self::ACTIONS[$action])) { echo '<option value="'.esc_attr($action).'">'.esc_html($title).'</option>'; }
        }
        echo '</select></label></p>';
        if (current_user_can('tn_store_dispatch')) { echo '<p><label>کد رهگیری حمل <input name="tracking_reference" maxlength="140"></label></p>'; }
        if (current_user_can('tn_store_refund')) {
            echo '<p><label>SKU در ERP <input name="sku" maxlength="64"></label> <label>مقدار برگشتی <input name="qty" inputmode="decimal"></label></p><p><label>کل استرداد، ریال <input name="amount_irr" inputmode="numeric"></label> <label>سهم ارسال از استرداد، ریال <input name="shipping_refund_irr" value="0" inputmode="numeric"></label></p><p><label>شناسه یکتای استرداد تأییدشده <input name="payment_identity" maxlength="120"></label></p>';
        }
        if (current_user_can('tn_store_settle')) {
            echo '<p><label>شناسه تسویه بانکی <input name="settlement_reference" maxlength="120"></label> <label>شناسه دریافت‌ها/استردادها، جداشده با ویرگول <input name="payment_identities" size="60"></label></p><p><label>کارمزد، ریال <input name="fee_irr" inputmode="numeric"></label> <label>خالص واریزی، ریال <input name="net_irr" inputmode="numeric"></label></p>';
        }
        if (current_user_can('tn_store_refund') || current_user_can('tn_store_settle')) { echo '<p><label><input type="checkbox" name="funds_verified" value="yes"> مدرک بانکی واقعی یا مدرک صریح آزمایشی را تطبیق داده‌ام.</label></p>'; }
        if (array_filter(self::ACTIONS,static fn($cap)=>current_user_can($cap))) { submit_button('ثبت و تطبیق عملیات'); }
        echo '</form></div>';
    }
    private function input(string $key): string {
        return isset($_POST[$key]) && is_string($_POST[$key]) ? sanitize_text_field(wp_unslash($_POST[$key])) : '';
    }
    public function submit(): void {
        $operation=$this->input('operation');
        if (!isset(self::ACTIONS[$operation]) || !current_user_can(self::ACTIONS[$operation])) { wp_die('دسترسی این عملیات را ندارید.',403); }
        check_admin_referer('tn_store_operation');
        $ok=false;
        try {
            $order=wc_get_order(absint($this->input('order_id')));
            if (!$order instanceof WC_Order) { throw new RuntimeException('Order missing'); }
            $bridge=new TehNet_Store_ERP();
            if (!$bridge->ready()) { throw new RuntimeException('Operational ERP required'); }
            if ($operation==='sync') { $bridge->retry_pending($order); }
            if ($operation==='cancel') { $bridge->cancel_order($order);$order->update_status('cancelled','لغو مجاز و آزادسازی رزرو ثبت شد.'); }
            if ($operation==='dispatch') { $bridge->send($order,'dispatch',['tracking_reference'=>$this->input('tracking_reference')]); }
            if (in_array($operation,['refund','settle'],true) && $this->input('funds_verified')!=='yes') { throw new RuntimeException('Verified bank evidence required'); }
            if ($operation==='refund') {
                $bridge->send($order,'refund',['items'=>[['sku'=>$this->input('sku'),'qty'=>$this->input('qty')]],'amount_irr'=>(string)TehNet_Store_Policy::irr($this->input('amount_irr'),'IRR'),'shipping_refund_irr'=>(string)TehNet_Store_Policy::irr($this->input('shipping_refund_irr'),'IRR'),'payment_identity'=>$this->input('payment_identity')]);
            }
            if ($operation==='settle') {
                $bridge->send($order,'settle',['amount_irr'=>(string)TehNet_Store_Policy::irr($this->input('amount_irr'),'IRR'),'fee_irr'=>(string)TehNet_Store_Policy::irr($this->input('fee_irr'),'IRR'),'net_irr'=>(string)TehNet_Store_Policy::irr($this->input('net_irr'),'IRR'),'settlement_reference'=>$this->input('settlement_reference'),'payment_identities'=>array_map('trim',explode(',',$this->input('payment_identities')))]);
            }
            $bridge->reconcile_order($order);
            $order->add_order_note('عملیات '.$operation.' توسط کاربر داخلی '.get_current_user_id().' تأیید شد.');$ok=true;
        } catch (RuntimeException|InvalidArgumentException $e) { /* Private data and remote traces never enter a redirect or notice. */ }
        wp_safe_redirect(add_query_arg(['page'=>'tn-store','tn_result'=>$ok?'ok':'error'],admin_url('admin.php')));exit;
    }
}
