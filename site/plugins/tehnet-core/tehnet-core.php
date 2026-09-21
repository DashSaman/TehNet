<?php
/**
 * Plugin Name: TehNet Core
 * Plugin URI: https://tehnet.ir
 * Description: Core domain settings and content models for TehNet / Tehran Network.
 * Version: 0.2.0
 * Requires at least: 6.7
 * Requires PHP: 8.2
 * Author: TehNet
 * Text Domain: tehnet-core
 */

defined('ABSPATH') || exit;

define('TEHNET_CORE_VERSION', '0.2.0');
define('TEHNET_CORE_FILE', __FILE__);
define('TEHNET_CORE_DIR', plugin_dir_path(__FILE__));

require_once TEHNET_CORE_DIR . 'includes/class-settings.php';
require_once TEHNET_CORE_DIR . 'includes/class-content-types.php';
require_once TEHNET_CORE_DIR . 'includes/class-schema.php';
require_once TEHNET_CORE_DIR . 'includes/class-commerce.php';
require_once TEHNET_CORE_DIR . 'includes/class-inquiries.php';

function tehnet_core_boot(): void {
    (new TehNet_Core_Settings())->register();
    (new TehNet_Core_Content_Types())->register();
    (new TehNet_Core_Schema())->register();
    (new TehNet_Core_Inquiries())->register();
    if (class_exists('WooCommerce')) {
        (new TehNet_Core_Commerce())->register();
    }
}
add_action('plugins_loaded', 'tehnet_core_boot');
