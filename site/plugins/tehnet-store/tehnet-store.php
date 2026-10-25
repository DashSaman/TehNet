<?php
/**
 * Plugin Name: TehNet Store
 * Description: Safe catalog imports and ERP-backed commerce for TehNet.
 * Version: 0.4.0
 * Requires PHP: 8.2
 * License: GPL-2.0-or-later
 */
defined('ABSPATH') || exit;
require_once __DIR__ . '/includes/class-catalog.php';
require_once __DIR__ . '/includes/class-policy.php';
require_once __DIR__ . '/includes/class-storefront.php';
require_once __DIR__ . '/includes/class-erp.php';
require_once __DIR__ . '/includes/class-operations.php';
require_once __DIR__ . '/includes/class-account.php';
require_once __DIR__ . '/includes/class-zarinpal-sandbox.php';
require_once __DIR__ . '/includes/class-product-visuals.php';
require_once __DIR__ . '/includes/class-product-evidence.php';
register_activation_hook(__FILE__,['TehNet_Store_Operations','install']);
add_action('woocommerce_blocks_payment_method_type_registration',static function($registry):void {
    if (class_exists('Automattic\\WooCommerce\\Blocks\\Payments\\Integrations\\AbstractPaymentMethodType')) {
        require_once __DIR__.'/includes/class-zarinpal-blocks.php';
        $registry->register(new TehNet_Store_Zarinpal_Blocks());
    }
});
add_action('plugins_loaded',static function():void {
    if (class_exists('WooCommerce')) {
        require_once __DIR__ . '/includes/class-zarinpal-gateway.php';
        add_filter('woocommerce_payment_gateways',static function(array $gateways):array { $gateways[]='TehNet_Store_Zarinpal_Gateway';return $gateways; });
        (new TehNet_Store_Storefront())->register(); (new TehNet_Store_ERP())->register();
        (new TehNet_Store_Operations())->register(); (new TehNet_Store_Account())->register();
        (new TehNet_Store_Product_Visuals())->register();
        (new TehNet_Store_Product_Evidence())->register();
    }
});

if (defined('WP_CLI') && WP_CLI) {
    WP_CLI::add_command('tehnet catalog release', function(array $args,array $assoc): void {
        $result=(new TehNet_Store_Catalog())->release($args[0]??'', $assoc['sha256']??'', isset($assoc['apply']));
        WP_CLI::line(wp_json_encode($result,JSON_PRETTY_PRINT|JSON_UNESCAPED_UNICODE));
    });
    WP_CLI::add_command('tehnet catalog import', function(array $args, array $assoc): void {
        if (empty($args[0]) || !is_readable($args[0])) { WP_CLI::error('Readable manifest path required.'); }
        $manifest = json_decode(file_get_contents($args[0]), true, 512, JSON_THROW_ON_ERROR);
        $result = (new TehNet_Store_Catalog())->import($manifest, !isset($assoc['apply']));
        WP_CLI::line(wp_json_encode($result, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    });
    WP_CLI::add_command('tehnet catalog rollback', function(array $args): void {
        if (empty($args[0])) { WP_CLI::error('Run ID required.'); }
        WP_CLI::line(wp_json_encode((new TehNet_Store_Catalog())->rollback($args[0]), JSON_PRETTY_PRINT));
    });
    WP_CLI::add_command('tehnet erp sync-product',function(array $args): void {
        if (empty($args[0])) { WP_CLI::error('Reviewed product ID required.'); }
        (new TehNet_Store_ERP())->sync_product(absint($args[0]));WP_CLI::success('ERP snapshot refreshed.');
    });
    WP_CLI::add_command('tehnet erp reconcile',function(array $args): void {
        $order=isset($args[0])?wc_get_order(absint($args[0])):false;
        if (!$order) { WP_CLI::error('Order ID required.'); }
        WP_CLI::line(wp_json_encode((new TehNet_Store_ERP())->reconcile_order($order),JSON_PRETTY_PRINT));
    });
}
