<?php
defined('ABSPATH') || exit;

/** Experimental protocol adapter. It has no production host or bank-refund method. */
final class TehNet_Store_Zarinpal_Sandbox {
    public const ID='tn_zarinpal_sandbox';
    // Official sandbox accepts any UUID. This is a public test identifier, not a credential.
    public const MERCHANT='e6374c3a-e0f0-553f-ae81-32734b0bc0a8';
    public static function environment(): bool { return in_array(wp_get_environment_type(),['local','staging'],true); }
    public static function enabled(): bool {
        return self::environment() && defined('TEHNET_PAYMENT_SANDBOX_ENABLED') && TEHNET_PAYMENT_SANDBOX_ENABLED===true
            && defined('TEHNET_ERP_SANDBOX') && TEHNET_ERP_SANDBOX===true;
    }
    public static function authority(string $value): bool { return preg_match('/^S[A-Za-z0-9]{35}$/D',$value)===1; }
    private function call(string $method,array $payload): array {
        if (!self::environment()) { throw new RuntimeException('Sandbox is forbidden in production'); }
        $response=wp_remote_post('https://sandbox.zarinpal.com/pg/v4/payment/'.$method.'.json',[
            'timeout'=>25,'redirection'=>0,'sslverify'=>true,
            'headers'=>['Content-Type'=>'application/json','Accept'=>'application/json'],
            'body'=>wp_json_encode(['merchant_id'=>self::MERCHANT]+$payload),
        ]);
        if (is_wp_error($response)) { throw new RuntimeException('Sandbox transport outcome is unknown; reconcile before retry'); }
        $body=json_decode(wp_remote_retrieve_body($response),true,32,JSON_BIGINT_AS_STRING);
        if (wp_remote_retrieve_response_code($response)!==200 || !is_array($body['data']??null)) {
            throw new RuntimeException('Sandbox response is invalid');
        }
        return $body['data'];
    }
    public function request(int $amount,string $callback): string {
        if ($amount<=0) { throw new InvalidArgumentException('Positive integer IRR amount required'); }
        $data=$this->call('request',['amount'=>$amount,'currency'=>'IRR','callback_url'=>$callback,'description'=>'TehNet SYNTHETIC sandbox order; no real payment']);
        if (($data['code']??null)!==100 || !is_string($data['authority']??null) || !self::authority($data['authority'])) { throw new RuntimeException('Sandbox request rejected'); }
        return $data['authority'];
    }
    public function verify(string $authority,int $amount): string {
        if ($amount<=0 || !self::authority($authority)) { throw new InvalidArgumentException('Invalid sandbox identity or IRR amount'); }
        $data=$this->call('verify',['authority'=>$authority,'amount'=>$amount]);
        $ref=$data['ref_id']??'';
        if (!in_array($data['code']??null,[100,101],true) || (!is_int($ref) && !is_string($ref)) || preg_match('/^[1-9][0-9]{0,31}$/D',(string)$ref)!==1) {
            throw new RuntimeException('Sandbox payment is not verified');
        }
        return (string)$ref;
    }
    private function guard($order): int {
        if (!self::enabled() || !$order instanceof WC_Order || $order->get_payment_method()!==self::ID || $order->get_currency()!=='IRR') {
            throw new RuntimeException('Sandbox order configuration is not approved');
        }
        if (!count($order->get_items())) { throw new RuntimeException('Synthetic items required'); }
        foreach ($order->get_items() as $line) {
            $product=$line->get_product();
            if (!$product || $product->get_meta('_tn_sandbox_fixture')!=='yes' || $product->is_virtual() || $product->is_downloadable()) {
                throw new RuntimeException('Only explicitly synthetic physical fixtures may use this gateway');
            }
        }
        $amount=TehNet_Store_Policy::irr($order->get_total(),'IRR');
        if ($amount<=0) { throw new RuntimeException('Positive IRR amount required'); }
        return $amount;
    }
    private function locked(WC_Order $order,callable $fn): array {
        $key='tn_zp_order_lock_'.$order->get_id();
        if (!add_option($key,gmdate('c'),'',false)) { throw new RuntimeException('Sandbox operation is locked; reconcile an interrupted process before unlocking'); }
        try { $this->refresh($order);return $fn(); } finally { delete_option($key); }
    }
    private function refresh(WC_Order $order): void {
        // Status/total may change while the provider request is in flight. Metadata-only
        // refresh is insufficient; use Woo's native data store (including HPOS).
        $order->get_data_store()->read($order);$order->read_meta_data(true);
    }
    public function start(WC_Order $order): array {
        return $this->locked($order,function()use($order):array {
            $amount=$this->guard($order);
            if (!$order->has_status(['pending','failed'])) { throw new RuntimeException('Order cannot start a payment'); }
            $status=(new TehNet_Store_ERP())->reconcile_order($order);
            if (($status['state']??'')!=='reserved') { throw new RuntimeException('Fresh synthetic ERP reservation required'); }
            $record=$order->get_meta('_tn_zp_attempt');
            if ($record) {
                if (($record['amount']??null)!==$amount || ($record['currency']??'')!=='IRR' || ($record['state']??'')!=='requested'
                    || !is_string($record['authority']??null) || !self::authority($record['authority'])) { throw new RuntimeException('Prior payment attempt requires reconciliation'); }
                return ['redirect'=>'https://sandbox.zarinpal.com/pg/StartPay/'.$record['authority']];
            }
            $record=['amount'=>$amount,'currency'=>'IRR','merchant'=>self::MERCHANT,'token'=>bin2hex(random_bytes(32)),'state'=>'requesting','created_at'=>gmdate('c')];
            $order->update_meta_data('_tn_zp_attempt',$record);$order->save();
            $callback=add_query_arg(['wc-api'=>self::ID,'order_id'=>$order->get_id(),'token'=>$record['token']],home_url('/'));
            try { $record['authority']=$this->request($amount,$callback);$record['state']='requested'; }
            catch (RuntimeException $error) { $record['state']='unknown';$order->update_meta_data('_tn_zp_attempt',$record);$order->save();throw $error; }
            $order->update_meta_data('_tn_zp_attempt',$record);$order->save();
            return ['redirect'=>'https://sandbox.zarinpal.com/pg/StartPay/'.$record['authority']];
        });
    }
    public function receive(WC_Order $order,string $authority,string $token,string $status): array {
        return $this->locked($order,function()use($order,$authority,$token,$status):array {
            $amount=$this->guard($order);$record=$order->get_meta('_tn_zp_attempt');
            if (!is_array($record) || !self::authority($authority) || ($record['authority']??'')!==$authority
                || !is_string($record['token']??null) || !hash_equals($record['token'],$token)
                || ($record['amount']??null)!==$amount || ($record['currency']??'')!=='IRR' || ($record['merchant']??'')!==self::MERCHANT) {
                throw new RuntimeException('Sandbox callback binding mismatch');
            }
            if ($status!=='OK') {
                // A browser query is not proof of bank failure. Keep reservation/receipt for reconciliation.
                return ['state'=>'not-verified'];
            }
            if (empty($record['ref_id'])) {
                $ref=$this->verify($authority,$amount);
                $key='tn_zp_receipt_'.hash('sha256',self::MERCHANT.':'.$ref);
                if (!add_option($key,$order->get_id(),'',false) && (int)get_option($key)!==$order->get_id()) { throw new RuntimeException('Sandbox receipt already belongs to another order'); }
                $record['ref_id']=$ref;$record['state']='verified';$record['verified_at']=gmdate('c');
                $order->update_meta_data('_tn_zp_attempt',$record);$order->save();
            }
            $this->refresh($order);
            if ($order->get_currency()!=='IRR' || TehNet_Store_Policy::irr($order->get_total(),'IRR')!==$record['amount']) {
                $order->update_status('on-hold','مبلغ سفارش هنگام تأیید پرداخت آزمایشی تغییر کرده؛ رسید نگهداری شد و تطبیق لازم است.');
                return ['state'=>'needs-reconciliation','ref_id'=>$record['ref_id']];
            }
            if ($order->is_paid() && $order->get_transaction_id()===$record['ref_id']) { return ['state'=>'verified','ref_id'=>$record['ref_id']]; }
            if ($order->get_transaction_id()!=='' && $order->get_transaction_id()!==$record['ref_id']) {
                $order->update_status('on-hold','دو شناسه متفاوت برای پرداخت آزمایشی؛ تطبیق دستی لازم است.');
                return ['state'=>'needs-reconciliation','ref_id'=>$record['ref_id']];
            }
            if ($order->has_status(['cancelled','refunded','completed']) || $order->get_meta('_tn_zp_late_payment')==='yes') {
                $order->update_meta_data('_tn_zp_late_payment','yes');$order->save();
                $order->update_status('on-hold','پرداخت صرفاً آزمایشی پس از بسته‌شدن سفارش؛ پیش از هر اقدامی تطبیق شود.');
                return ['state'=>'needs-reconciliation','ref_id'=>$record['ref_id']];
            }
            try {
                $erp=(new TehNet_Store_ERP())->reconcile_order($order);
                if ($order->is_paid() && $order->get_transaction_id()===$record['ref_id'] && in_array($erp['state']??'',['paid','dispatched'],true)) {
                    return ['state'=>'verified','ref_id'=>$record['ref_id']];
                }
                if (($erp['state']??'')!=='reserved') { throw new RuntimeException('Synthetic ERP reservation is no longer open'); }
                $order->payment_complete($record['ref_id']);
                return ['state'=>$order->has_status('on-hold')?'needs-reconciliation':'verified','ref_id'=>$record['ref_id']];
            } catch (RuntimeException $error) {
                $order->update_status('on-hold','رسید آزمایشی ذخیره شد؛ ثبت ERP یا رزرو نیازمند تطبیق است.');
                return ['state'=>'needs-reconciliation','ref_id'=>$record['ref_id']];
            }
        });
    }
}
