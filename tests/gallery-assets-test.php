<?php
/** Isolated assets() seam with WP stubs, not native WordPress integration. */
define('ABSPATH',__DIR__.'/');
$ctx=['woo'=>true,'product'=>true];$scripts=[];$styles=[];
function is_woocommerce(){return $GLOBALS['ctx']['woo'];}
function is_product(){return $GLOBALS['ctx']['product'];}
function is_cart(){return false;}function is_checkout(){return false;}function is_account_page(){return false;}function is_shop(){return !$GLOBALS['ctx']['product'];}function is_product_taxonomy(){return false;}
function plugins_url($path,$plugin){return 'https://example.invalid/plugins/tehnet-store/'.$path;}
function wp_enqueue_script($name,$src,$deps=[],$version=false,$footer=false){$GLOBALS['scripts'][$name]=[$src,$deps,$version,$footer];}
function wp_enqueue_style($name,$src,$deps=[],$version=false){$GLOBALS['styles'][$name]=[$src,$deps,$version];}
require __DIR__.'/../site/plugins/tehnet-store/includes/class-storefront.php';
$store=(new ReflectionClass(TehNet_Store_Storefront::class))->newInstanceWithoutConstructor();
function expect($value,$label){if(!$value)throw new RuntimeException('FAIL: '.$label);echo 'PASS: '.$label."\n";}
$store->assets();
expect(isset($scripts['tn-product-gallery'],$styles['tn-product-gallery']),'Product gallery assets are enqueued');
expect($scripts['tn-product-gallery'][0]==='https://example.invalid/plugins/tehnet-store/assets/product-gallery.js'&&$scripts['tn-product-gallery'][3]===true,'Local gallery script in footer');
expect($scripts['tn-product-gallery'][2]==='0.1.0'&&$styles['tn-product-gallery'][2]==='0.1.0','Explicit asset cache revisions');
expect(isset($scripts['tn-store'],$styles['tn-store'],$styles['tn-shop-experience']),'Existing assets retained');
$scripts=[];$styles=[];$ctx['product']=false;$store->assets();
expect(!isset($scripts['tn-product-gallery'])&&!isset($styles['tn-product-gallery']),'Archive does not load product gallery assets');
$scripts=[];$styles=[];$ctx['woo']=false;$store->assets();
expect(!$scripts&&!$styles,'Non-commerce page gets no store assets');
echo "GALLERY_ASSETS=PASS checks=6\n";
