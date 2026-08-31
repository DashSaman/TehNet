<?php
if(!defined('ABSPATH'))exit;
function tehnet_product_sale_mode(int $product_id):string{$mode=(string)get_post_meta($product_id,TEHNET_SALE_MODE_META,true);return in_array($mode,[TEHNET_SALE_MODE_DIRECT,TEHNET_SALE_MODE_INQUIRY],true)?$mode:TEHNET_SALE_MODE_DIRECT;}
function tehnet_register_product_sale_mode_meta():void{register_post_meta('product',TEHNET_SALE_MODE_META,['type'=>'string','single'=>true,'show_in_rest'=>true,'sanitize_callback'=>static function($value):string{return in_array($value,[TEHNET_SALE_MODE_DIRECT,TEHNET_SALE_MODE_INQUIRY],true)?$value:TEHNET_SALE_MODE_DIRECT;},'auth_callback'=>static fn()=>current_user_can('edit_products')]);}
add_action('init','tehnet_register_product_sale_mode_meta');
function tehnet_inquiry_product_is_purchasable(bool $purchasable,$product):bool{if(!$product||!method_exists($product,'get_id'))return $purchasable;return tehnet_product_sale_mode((int)$product->get_id())===TEHNET_SALE_MODE_INQUIRY?false:$purchasable;}
add_filter('woocommerce_is_purchasable','tehnet_inquiry_product_is_purchasable',10,2);
