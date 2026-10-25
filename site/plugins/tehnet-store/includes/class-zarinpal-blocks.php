<?php
defined('ABSPATH') || exit;

final class TehNet_Store_Zarinpal_Blocks extends \Automattic\WooCommerce\Blocks\Payments\Integrations\AbstractPaymentMethodType {
    protected $name='tn_zarinpal_sandbox';
    private $gateway;
    public function initialize() {
        $this->gateway=WC()->payment_gateways()->payment_gateways()[$this->name]??null;
    }
    public function is_active() { return $this->gateway && $this->gateway->is_available(); }
    public function get_payment_method_script_handles() {
        wp_register_script('tn-zarinpal-sandbox-blocks',plugins_url('../assets/zarinpal-blocks.js',__FILE__),['wc-blocks-registry','wc-settings','wp-element'],'0.1.0',true);
        return ['tn-zarinpal-sandbox-blocks'];
    }
    public function get_payment_method_data() {
        return ['title'=>$this->gateway->title,'description'=>$this->gateway->description,'supports'=>['products']];
    }
}
