<?php
defined('ABSPATH') || exit;

/** Woo owns customer orders; ERPNext owns physical reservations, stock and GL. */
final class TehNet_Store_ERP {
    private function setting(string $name): string {
        return defined($name) ? (string)constant($name) : (string)getenv($name);
    }
    public function configured(): bool {
        $url=wp_parse_url($this->setting('TEHNET_ERP_URL'));
        return is_array($url) && !empty($url['host']) && empty($url['user']) && empty($url['pass'])
            && empty($url['query']) && empty($url['fragment'])
            && (($url['scheme']??'')==='https' || (wp_get_environment_type()==='local' && ($url['scheme']??'')==='http'))
            && $this->setting('TEHNET_ERP_API_KEY')!=='' && $this->setting('TEHNET_ERP_API_SECRET')!==''
            && preg_match('/^[A-Za-z0-9_-]{1,40}$/D',$this->setting('TEHNET_ERP_STORE_ID'))===1;
    }
    public function register(): void {
        add_action('woocommerce_checkout_order_processed',[$this,'checkout'],10,3);
        add_action('woocommerce_store_api_checkout_order_processed',function($order): void { $this->checkout($order->get_id(),[],$order); });
        add_action('woocommerce_payment_complete',[$this,'payment_complete']);
        add_action('woocommerce_order_status_cancelled',[$this,'canceled']);
        add_action('tn_erp_retry',[$this,'retry'],10,2);
        add_action('tn_erp_maintenance',[$this,'maintenance']);
        add_action('action_scheduler_init',[$this,'schedule']);
        add_action('woocommerce_order_details_after_order_table',[$this,'customer_documents']);
        add_filter('woocommerce_can_reduce_order_stock',[$this,'native_stock'],10,2);
        add_filter('woocommerce_can_restore_order_stock',[$this,'native_stock'],10,2);
    }
    public function ready(): bool {
        return $this->configured() && defined('TEHNET_ERP_RESERVATIONS_ENABLED') && TEHNET_ERP_RESERVATIONS_ENABLED===true
            && trim($this->setting('TEHNET_VERIFIED_GATEWAYS'))!=='';
    }
    private function request(string $method,array $payload): array {
        if (!$this->configured()) { throw new RuntimeException('ERP connection is not configured'); }
        $response=wp_remote_post(rtrim($this->setting('TEHNET_ERP_URL'),'/').'/api/method/tehnet_erp.api.'.$method,[
            'timeout'=>45,'redirection'=>0,'sslverify'=>true,
            'headers'=>['Content-Type'=>'application/json','Authorization'=>'token '.$this->setting('TEHNET_ERP_API_KEY').':'.$this->setting('TEHNET_ERP_API_SECRET'),'X-Frappe-Site-Name'=>$this->setting('TEHNET_ERP_SITE')],
            'body'=>wp_json_encode($payload),
        ]);
        // Do not store remote exception traces, credentials or customer data in logs/notices.
        if (is_wp_error($response)) { throw new RuntimeException('ERP connection unavailable; outcome requires reconciliation'); }
        $body=json_decode(wp_remote_retrieve_body($response),true);
        if (wp_remote_retrieve_response_code($response)!==200 || !is_array($body['message']??null)) {
            throw new RuntimeException('ERP rejected operation; HTTP '.wp_remote_retrieve_response_code($response));
        }
        return $body['message'];
    }
    private function reference(WC_Order $order): string {
        return $this->setting('TEHNET_ERP_STORE_ID').':'.$order->get_id();
    }
    private function physical(WC_Order $order): bool {
        foreach ($order->get_items() as $line) {
            $product=$line->get_product();
            if ($product && !$product->is_virtual() && !$product->is_downloadable()) { return true; }
        }
        return false;
    }
    public function sync_product(int $id): void {
        $product=wc_get_product($id);
        if (!$product || !$product->get_meta('_tn_erp_sku') || !$product->get_meta('_tn_erp_uom')) { throw new RuntimeException('Reviewed ERP item/UOM mapping required'); }
        $snapshot=$this->request('catalog_snapshot',['items'=>[['sku'=>$product->get_meta('_tn_erp_sku'),'uom'=>$product->get_meta('_tn_erp_uom')]]]);
        $row=$snapshot['items'][0]??[];
        if (($snapshot['currency']??'')!=='IRR' || ($row['sku']??'')!==$product->get_meta('_tn_erp_sku') || ($row['uom']??'')!==$product->get_meta('_tn_erp_uom')) { throw new RuntimeException('ERP snapshot identity mismatch'); }
        $price=TehNet_Store_Policy::irr($row['price_irr'],'IRR');
        if (!preg_match('/^\d+(?:\.\d{1,3})?$/D',$row['available_qty'])) { throw new RuntimeException('Invalid ERP quantity'); }
        $product->set_regular_price((string)$price);$product->set_sale_price('');
        $product->set_manage_stock(true);$product->set_stock_quantity($row['available_qty']);
        $product->set_backorders('no');$product->set_stock_status((float)$row['available_qty']>0?'instock':'outofstock');
        $product->update_meta_data('_tn_erp_fresh_until',time()+min(60,(int)$snapshot['ttl_seconds']));
        $product->update_meta_data('_tn_erp_conversion',$row['conversion_factor']);$product->save();
    }
    public function reserve_order(WC_Order $order): array {
        if ($order->get_currency()!=='IRR') { throw new RuntimeException('IRR order required'); }
        $items=[];$subtotal=0;
        foreach ($order->get_items() as $line) {
            $product=$line->get_product();
            if (!$product || $product->is_virtual() || $product->is_downloadable()) { throw new RuntimeException('Mixed physical/digital orders require a separate reviewed workflow'); }
            if ($product->get_meta('_tn_sale_approved')!=='yes' || !$product->get_meta('_tn_erp_sku') || !$product->get_meta('_tn_erp_uom')) { throw new RuntimeException('Unapproved ERP item mapping'); }
            $qty=(string)$line->get_quantity();$milli=TehNet_Store_Policy::quantity_milli($qty);
            $minimum=TehNet_Store_Policy::quantity_milli((string)$product->get_meta('_tn_min_quantity'));
            if ($milli<$minimum || ($product->get_meta('_tn_sale_unit')!=='meter' && $milli%1000!==0)) { throw new RuntimeException('Quantity violates the verified unit/minimum'); }
            $rate=TehNet_Store_Policy::irr($product->get_regular_price(),'IRR');
            $expected=TehNet_Store_Policy::line_total($milli,$rate);
            if ($expected!==TehNet_Store_Policy::irr($line->get_subtotal(),'IRR')) { throw new RuntimeException('Order line price mismatch'); }
            $subtotal+=$expected;
            $items[]=['sku'=>$product->get_meta('_tn_erp_sku'),'qty'=>$qty,'uom'=>$product->get_meta('_tn_erp_uom'),'unit_price_irr'=>(string)$rate];
        }
        $payload=['currency'=>'IRR','amount_irr'=>(string)TehNet_Store_Policy::irr($order->get_total(),'IRR'),
            'shipping_irr'=>(string)TehNet_Store_Policy::irr($order->get_shipping_total(),'IRR'),
            'discount_irr'=>(string)TehNet_Store_Policy::irr($order->get_discount_total(),'IRR'),
            'tax_irr'=>(string)TehNet_Store_Policy::irr($order->get_total_tax(),'IRR'),
            'customer'=>['reference'=>$this->reference($order).':customer','name'=>$order->get_formatted_billing_full_name()?:'مشتری وب'],
            'items'=>$items];
        return $this->send($order,'reserve',$payload);
    }
    public function cancel_order(WC_Order $order): array { return $this->send($order,'cancel',[]); }
    public function send(WC_Order $order,string $kind,array $data): array {
        return $this->locked($order,fn()=>$this->prepare($order,$kind,$data));
    }
    private function locked(WC_Order $order,callable $callback): array {
        $lock='tn_erp_order_lock_'.$order->get_id();
        if (!add_option($lock,gmdate('c'),'',false)) { throw new RuntimeException('ERP order operation is locked; reconcile an interrupted attempt before unlocking'); }
        try { $order->read_meta_data(true);return $callback(); }
        finally { delete_option($lock); }
    }
    private function prepare(WC_Order $order,string $kind,array $data): array {
        if (!in_array($kind,['reserve','cancel','paid','dispatch','refund','settle'],true)) { throw new RuntimeException('Invalid ERP event'); }
        $ref=$this->reference($order);
        $identity=$data['payment_identity']??$data['settlement_reference']??'';
        $key=$ref.':'.$kind.($identity!==''?':'.substr(hash('sha256',$identity),0,20):'');
        $payload=['schema_version'=>1,'event_key'=>$key,'order_ref'=>$ref,'kind'=>$kind]+$data;
        $box=$order->get_meta('_tn_erp_outbox');$box=is_array($box)?$box:[];
        if (isset($box[$key]) && $box[$key]['payload']!==$payload) { throw new RuntimeException('Immutable ERP event cannot be changed'); }
        if (isset($box[$key]['result'])) { return $box[$key]['result']; }
        $box[$key]=['payload'=>$payload,'attempts'=>$box[$key]['attempts']??0,'state'=>'pending'];
        $order->update_meta_data('_tn_erp_outbox',$box);$order->save();
        return $this->deliver($order,$key);
    }
    private function deliver(WC_Order $order,string $key): array {
        $box=$order->get_meta('_tn_erp_outbox');
        if (!isset($box[$key])) { throw new RuntimeException('Missing durable event'); }
        if (isset($box[$key]['result'])) { return $box[$key]['result']; }
        if (($box[$key]['payload']['kind']??'')==='reserve' && $order->has_status(['cancelled','failed'])) {
            $status=$this->request('status',['order_ref'=>$this->reference($order)]);
            if (!empty($status['found']) && $status['state']==='reserved') {
                $status=$this->request('event',['payload'=>['schema_version'=>1,'event_key'=>$this->reference($order).':cancel','order_ref'=>$this->reference($order),'kind'=>'cancel']]);
            } elseif (!empty($status['found']) && !in_array($status['state'],['canceled','expired'],true)) {
                throw new RuntimeException('Closed Woo order has a paid ERP reservation; reconcile before any further action');
            }
            $box[$key]['state']='voided';$box[$key]['result']=$status+['state'=>'voided'];
            $order->update_meta_data('_tn_erp_outbox',$box);$order->save();
            return $box[$key]['result'];
        }
        ++$box[$key]['attempts'];
        // Persist attempt before network I/O; timeout never fabricates a successful receipt.
        $order->update_meta_data('_tn_erp_outbox',$box);$order->save();
        try {
            $result=$this->request('event',['payload'=>$box[$key]['payload']]);
            $box[$key]['state']='acknowledged';$box[$key]['result']=$result;
            $order->update_meta_data('_tn_erp_state',$result['state']??'');
            foreach (['sales_order','invoice','payment_entry','delivery_note'] as $name) {
                if (!empty($result[$name])) { $order->update_meta_data('_tn_erp_'.$name,$result[$name]); }
            }
            $order->update_meta_data('_tn_erp_outbox',$box);$order->save();
            return $result;
        } catch (RuntimeException $e) {
            $box[$key]['state']=$box[$key]['attempts']>=8?'needs-reconciliation':'pending';
            $order->update_meta_data('_tn_erp_outbox',$box);$order->save();
            $pending=function_exists('as_get_scheduled_actions') ? as_get_scheduled_actions(['hook'=>'tn_erp_retry','args'=>[$order->get_id(),$key],'group'=>'tehnet','status'=>'pending'],'ids') : [];
            if ($box[$key]['attempts']<8 && function_exists('as_schedule_single_action') && !$pending) {
                as_schedule_single_action(time()+min(3600,60*2**$box[$key]['attempts']),'tn_erp_retry',[$order->get_id(),$key],'tehnet');
            }
            throw $e;
        }
    }
    public function retry(int $order_id,string $key): void {
        $order=wc_get_order($order_id);if (!$order) { return; }
        try { $this->locked($order,fn()=>$this->deliver($order,$key)); }
        catch (RuntimeException $e) { $order->add_order_note('همگام‌سازی ERP نیازمند بررسی است؛ جزئیات محرمانه در یادداشت ثبت نمی‌شود.'); }
    }
    public function retry_pending(WC_Order $order): void {
        $this->locked($order,function() use ($order): array {
            $box=$order->get_meta('_tn_erp_outbox');
            foreach (is_array($box)?$box:[] as $key=>$event) {
                if (!isset($event['result']) && in_array($event['state'],['pending','needs-reconciliation'],true)) { $this->deliver($order,$key); }
            }
            return [];
        });
    }
    public function schedule(): void {
        if ($this->configured() && function_exists('as_has_scheduled_action') && !as_has_scheduled_action('tn_erp_maintenance',[],'tehnet')) {
            as_schedule_recurring_action(time()+60,60,'tn_erp_maintenance',[],'tehnet');
        }
    }
    public function maintenance(): void {
        if (!$this->configured()) { return; }
        $ids=get_posts(['post_type'=>'product','post_status'=>['publish','private'],'numberposts'=>100,'fields'=>'ids','meta_query'=>[
            ['key'=>'_tn_erp_sku','compare'=>'EXISTS'],['key'=>'_tn_sale_approved','value'=>'yes'],
        ]]);
        foreach ($ids as $id) {
            try { $this->sync_product((int)$id); }
            catch (RuntimeException $e) { delete_post_meta((int)$id,'_tn_erp_fresh_until'); }
        }
        $page=max(1,(int)get_option('tn_erp_order_page',1));
        $batch=wc_get_orders(['type'=>'shop_order','limit'=>25,'page'=>$page,'paginate'=>true,'status'=>['pending','on-hold','processing','completed','cancelled','failed'],
            'meta_query'=>[['key'=>'_tn_erp_sales_order','compare'=>'EXISTS']], 'orderby'=>'date','order'=>'ASC']);
        foreach ($batch->orders as $order) {
            try { $this->reconcile_order($order); }
            catch (RuntimeException $e) {
                $order->update_meta_data('_tn_erp_reconciliation','required');$order->save();
                if (str_contains($e->getMessage(),'connection unavailable') || preg_match('/HTTP 5[0-9]{2}/',$e->getMessage())) { return; }
            }
        }
        update_option('tn_erp_order_page',$page>=max(1,$batch->max_num_pages)?1:$page+1,false);
    }
    public function reconcile_order(WC_Order $order): array {
        return $this->locked($order,function() use ($order): array {
            $status=$this->request('status',['order_ref'=>$this->reference($order)]);
            if (($status['order_ref']??'')!==$this->reference($order)) { throw new RuntimeException('ERP status identity mismatch'); }
            if (empty($status['found'])) { return $status; }
            if (($status['currency']??'')!=='IRR' || TehNet_Store_Policy::irr($status['amount_irr'],'IRR')!==TehNet_Store_Policy::irr($order->get_total(),'IRR')) { throw new RuntimeException('ERP status amount mismatch'); }
            $order->update_meta_data('_tn_erp_state',$status['state']);
            $order->update_meta_data('_tn_tracking_reference',sanitize_text_field($status['tracking_reference']??''));
            foreach (['sales_order','invoice','payment_entry','delivery_note'] as $key) {
                if (!empty($status[$key])) { $order->update_meta_data('_tn_erp_'.$key,$status[$key]); }
            }
            $order->save();
            foreach ($status['refunds']??[] as $credit) { $this->apply_credit($order,$credit); }
            $verified=$order->get_meta('_tn_payment_verified_identity');
            if ($verified && $verified===$order->get_payment_method().':'.$order->get_transaction_id() && !empty($status['payment_entry']) && in_array($status['state'],['paid','dispatched'],true) && $order->has_status(['on-hold','pending'])) {
                $order->update_status('processing','تطبیق ثبت دریافت تأییدشده در ERP تکمیل شد.');
            }
            if (in_array($status['state'],['expired','canceled'],true) && $order->has_status(['pending','failed'])) {
                $order->update_status('cancelled','رزرو ERP بسته و موجودی آزاد شد.');
            }
            if ($status['state']==='dispatched' && $order->has_status('processing')) { $order->update_status('completed','تحویل به حمل‌کننده در ERP ثبت شد.'); }
            $order->update_meta_data('_tn_erp_reconciliation','ok');$order->save();
            return $status;
        });
    }
    private function apply_credit(WC_Order $order,array $credit): void {
        $reason='ERP credit '.$credit['credit_note'];
        foreach ($order->get_refunds() as $refund) {
            if ($refund->get_meta('_tn_erp_credit_note')===$credit['credit_note'] || $refund->get_reason()===$reason) { return; }
        }
        $amount=TehNet_Store_Policy::irr($credit['amount_irr'],'IRR');$lines=[];
        if ($amount<=0 || $amount>TehNet_Store_Policy::irr((string)$order->get_remaining_refund_amount(),'IRR')) { throw new RuntimeException('ERP refund exceeds Woo remaining amount'); }
        foreach ($credit['items'] as $returned) {
            $matched=false;
            foreach ($order->get_items() as $id=>$line) {
                $product=$line->get_product();
                if ($product && $product->get_meta('_tn_erp_sku')===$returned['sku'] && $product->get_meta('_tn_erp_uom')===$returned['uom']) {
                    $lines[$id]=['qty'=>(string)$returned['qty'],'refund_total'=>(string)TehNet_Store_Policy::irr($returned['amount_irr'],'IRR'),'refund_tax'=>[]];$matched=true;break;
                }
            }
            if (!$matched) { throw new RuntimeException('ERP return line does not match the Woo order'); }
        }
        $shipping=TehNet_Store_Policy::irr($credit['shipping_irr']??'0','IRR');
        if ($shipping) {
            $shipping_lines=$order->get_items('shipping');
            if (count($shipping_lines)!==1) { throw new RuntimeException('Shipping refund allocation needs review'); }
            $lines[array_key_first($shipping_lines)]=['qty'=>1,'refund_total'=>(string)$shipping,'refund_tax'=>[]];
        }
        $refund=wc_create_refund(['order_id'=>$order->get_id(),'amount'=>(string)$amount,'reason'=>$reason,'line_items'=>$lines,'refund_payment'=>false,'restock_items'=>false]);
        if (is_wp_error($refund)) { throw new RuntimeException('Native Woo refund needs reconciliation'); }
        $refund->update_meta_data('_tn_erp_credit_note',$credit['credit_note']);$refund->save();
    }
    public function invoice_document(WC_Order $order): array {
        return $this->request('invoice_document',['order_ref'=>$this->reference($order)]);
    }
    public function checkout(int $id,array $posted,$order): void {
        if (!$order instanceof WC_Order || !$this->physical($order)) { return; }
        // Manual-sales mode: skip ERP reservation; stock/price gates already passed and the owner confirms manually.
        if (!$this->ready()) {
            if (TehNet_Store_Storefront::manual_sales()) {
                $order->update_status('on-hold','فروش دستی: در انتظار تأیید موجودی و پرداخت توسط مدیر.');
                $order->update_meta_data('_tn_manual_sale',gmdate('c'));
                $order->save();
                return;
            }
            throw new Exception('اتصال رزرو موجودی آماده نیست؛ برای این سفارش استعلام بگیرید.');
        }
        try { if (($this->reserve_order($order)['state']??'')!=='reserved') { throw new RuntimeException('Reservation is closed'); } }
        catch (RuntimeException $e) { throw new Exception('رزرو قطعی موجودی تأیید نشد. سفارش را پرداخت نکنید؛ وضعیت آن باید بررسی شود.'); }
    }
    public function payment_complete(int $id): void {
        $order=wc_get_order($id);if (!$order || !$this->physical($order)) { return; }
        $allowed=array_filter(explode(',',$this->setting('TEHNET_VERIFIED_GATEWAYS')));
        if (!in_array($order->get_payment_method(),$allowed,true) || $order->get_transaction_id()==='') {
            $order->update_status('on-hold','تأیید سمت سرور درگاه معتبر و شناسه تراکنش برای ثبت ERP لازم است.');return;
        }
        try {
            $order->update_meta_data('_tn_payment_verified_identity',$order->get_payment_method().':'.$order->get_transaction_id());$order->save();
            $this->send($order,'paid',['currency'=>$order->get_currency(),'amount_irr'=>(string)TehNet_Store_Policy::irr($order->get_total(),'IRR'),'payment_identity'=>$order->get_payment_method().':'.$order->get_transaction_id()]);
        } catch (RuntimeException $e) { $order->update_status('on-hold','ثبت دریافت ERP تأیید نشد؛ پیش از ارسال کالا تطبیق انجام شود.'); }
    }
    public function canceled(int $id): void {
        $order=wc_get_order($id);if (!$order || !$order->get_meta('_tn_erp_sales_order')) { return; }
        try { $this->cancel_order($order); }
        catch (RuntimeException $e) { $order->add_order_note('لغو ERP تأیید نشد؛ سفارش پرداخت‌شده به فرایند برگشت نیاز دارد.'); }
    }
    public function native_stock(bool $allowed,$order): bool {
        return $order instanceof WC_Order && $order->get_meta('_tn_erp_sales_order') ? false : $allowed;
    }
    public function customer_documents($order): void {
        if (!$order instanceof WC_Order) { return; }
        // Woo's order-details authorization runs before this hook; identifiers are escaped.
        foreach (['sales_order'=>'سفارش ERP','invoice'=>'شماره فاکتور','delivery_note'=>'سند تحویل'] as $key=>$label) {
            $value=$order->get_meta('_tn_erp_'.$key);
            if ($value) { echo '<p>'.esc_html($label).' : <bdi>'.esc_html($value).'</bdi></p>'; }
        }
    }
}
