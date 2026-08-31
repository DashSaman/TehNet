<?php
/** Plugin Name: TehNet Core
 * Description: TehNet-specific content types, relationships and shop behavior.
 * Version: 0.1.0
 */
if(!defined('ABSPATH'))exit;
define('TEHNET_CORE_VERSION','0.1.0');
define('TEHNET_SALE_MODE_META','_tehnet_sale_mode');
define('TEHNET_SALE_MODE_DIRECT','direct');
define('TEHNET_SALE_MODE_INQUIRY','inquiry');
require_once __DIR__.'/src/domain.php';
require_once __DIR__.'/src/content-types.php';
require_once __DIR__.'/src/relations.php';
require_once __DIR__.'/src/product-inquiry.php';
