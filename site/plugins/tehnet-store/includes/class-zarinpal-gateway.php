<?php
defined('ABSPATH') || exit;

/** Explicitly experimental and disabled by default. */
final class TehNet_Store_Zarinpal_Gateway extends WC_Payment_Gateway {
    public function __construct() {
        $this->id=TehNet_Store_Zarinpal_Sandbox::ID;
        $this->method_title='زرین‌پال — فقط آزمایش';
        $this->method_description='سندباکس برای کالای ساختگی و ERP آزمایشی؛ پرداخت واقعی ندارد.';
        $this->title='پرداخت آزمایشی زرین‌پال (بدون انتقال وجه)';
        $this->description='این خرید صرفاً آزمایشی است و کالایی ارسال نمی‌شود.';
        $this->has_fields=false;$this->supports=['products'];
        $this->form_fields=['enabled'=>['title'=>'فعال‌سازی آزمایش','type'=>'checkbox','label'=>'فقط برای سناریوی ساختگی در محیط آزمایشی','default'=>'no']];
        $this->init_settings();$this->enabled=$this->get_option('enabled','no');
        add_action('woocommerce_update_options_payment_gateways_'.$this->id,[$this,'process_admin_options']);
        add_action('woocommerce_api_'.$this->id,[$this,'callback']);
    }
    public function is_available() {
        if ($this->enabled!=='yes' || !TehNet_Store_Zarinpal_Sandbox::enabled() || !(new TehNet_Store_ERP())->ready()) { return false; }
        $cart=WC()->cart;
        if ($cart) {
            foreach ($cart->get_cart() as $row) {
                if (!isset($row['data']) || $row['data']->get_meta('_tn_sandbox_fixture')!=='yes') { return false; }
            }
        }
        return parent::is_available();
    }
    public function process_payment($order_id) {
        try {
            if (!$this->is_available()) { throw new RuntimeException('Sandbox is disabled'); }
            $order=wc_get_order($order_id);
            if (!$order instanceof WC_Order) { throw new RuntimeException('Order missing'); }
            return ['result'=>'success']+(new TehNet_Store_Zarinpal_Sandbox())->start($order);
        } catch (RuntimeException|InvalidArgumentException $error) {
            wc_add_notice('شروع پرداخت آزمایشی تأیید نشد؛ وضعیت رزرو و تلاش قبلی باید بررسی شود.','error');
            return ['result'=>'failure'];
        }
    }
    public function callback(): void {
        nocache_headers();header('X-Robots-Tag: noindex, nofollow');
        try {
            $query=[];
            foreach (['order_id','Authority','token','Status'] as $name) {
                if (!isset($_GET[$name]) || !is_string($_GET[$name])) { throw new RuntimeException('Callback argument missing'); }
                $query[$name]=wp_unslash($_GET[$name]);
            }
            if (!preg_match('/^[1-9][0-9]{0,18}$/D',$query['order_id']) || !preg_match('/^[a-f0-9]{64}$/D',$query['token'])) { throw new RuntimeException('Invalid callback'); }
            $order=wc_get_order((int)$query['order_id']);
            if (!$order instanceof WC_Order) { throw new RuntimeException('Order missing'); }
            $result=(new TehNet_Store_Zarinpal_Sandbox())->receive($order,$query['Authority'],$query['token'],$query['Status']);
            if ($result['state']==='verified') { wc_add_notice('پرداخت صرفاً آزمایشی تأیید شد؛ هیچ وجه واقعی جابه‌جا نشده است.','notice'); }
            else { wc_add_notice('پرداخت آزمایشی هنوز نهایی نشده؛ وضعیت سفارش نیازمند بررسی است.','notice'); }
            wp_safe_redirect($this->get_return_url($order));
        } catch (RuntimeException|InvalidArgumentException $error) {
            wc_add_notice('بازگشت آزمایشی تأیید نشد. اطلاعات درخواست یا وضعیت تراکنش باید بررسی شود.','error');
            wp_safe_redirect(wc_get_checkout_url());
        }
        exit;
    }
}
