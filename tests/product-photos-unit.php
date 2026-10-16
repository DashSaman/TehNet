<?php
// Independent runtime contract: no WordPress/DB/network required.
define('ABSPATH',__DIR__);$product=null;
class WC_Product {
 public $meta=['_tn_source_key'=>'fixture','_tn_source_id'=>18002];public $image=0;public $gallery=[];
 function get_meta($k){return $this->meta[$k]??'';}function get_image_id(){return $this->image;}
 function get_gallery_image_ids(){return $this->gallery;}function get_name(){return 'FIXTURE';}function get_id(){return 10;}
}
function plugins_url($p,$f){return '/plugin/'.$p;}function esc_url($s){return htmlspecialchars($s,ENT_QUOTES);}
function esc_attr($s){return htmlspecialchars($s,ENT_QUOTES);}function esc_html($s){return htmlspecialchars((string)$s,ENT_QUOTES);}
function wp_get_attachment_image_url($id,$size){return '/uploads/'.$id.'.jpg';}
function get_post_field($field,$id){global $foreign;return $id===($foreign??0)?99:10;}function wp_attachment_is_image($id){return true;}
function wp_json_encode($v){return json_encode($v);}
function add_filter(...$args){}function add_action($hook,$callback,...$args){global $enqueueCallback;if($hook==='wp_enqueue_scripts')$enqueueCallback=$callback;}
function is_product(){return true;}function get_queried_object_id(){return 10;}function wc_get_product($id){global $fixtureProduct;return $fixtureProduct;}
function wp_enqueue_script($handle,...$args){global $scripts;$scripts[]=$handle;}
require __DIR__.'/../site/plugins/tehnet-store/includes/class-product-visuals.php';
$s=new TehNet_Store_Product_Visuals();$product=new WC_Product();$count=0;
function check($ok,$name){global $count;if(!$ok){throw new RuntimeException($name);}echo "PASS $name\n";$count++;}
check(str_contains($s->image('native',$product),'tn-product-illustration'),'media-empty fixture keeps clearly labelled fallback');
$product->image=11;$product->meta['_tn_photo_release']='fixture';
$html=$s->image('<img src="/uploads/11.jpg">',$product);
check(str_contains($html,'/uploads/11.jpg')&&str_contains($html,'tehnet.ir'),'native photograph preserved with website overlay');
check(!str_contains($html,'illustrations/'),'native photo never replaced by generic art');
ob_start();$s->viewer();$v=ob_get_clean();check(!str_contains($v,'data-tn-model='),'photo product never presents schematic as 360');
check(!str_contains($v,'data-tn-spin='),'one photo does not produce a spin');
$product->gallery=[12];ob_start();$s->viewer();$v=ob_get_clean();check(!str_contains($v,'data-tn-spin='),'two views do not claim 360');
$product->meta['_tn_spin_attachment_ids']=range(20,31);$product->meta['_tn_spin_reviewed']='no';
check($s->spin_frames($product)===[],'unreviewed frames rejected');
$product->meta['_tn_spin_reviewed']='yes';check(count($s->spin_frames($product))===12,'reviewed same-product photo sequence accepted');
ob_start();$s->viewer();$v=ob_get_clean();check(str_contains($v,'data-tn-spin=')&&!str_contains($v,'data-tn-model='),'reviewed photos use genuine frame viewer');
if(isset($argv[1])){file_put_contents($argv[1],$v);}
$foreign=25;check($s->spin_frames($product)===[],'another product attachment rejected');$foreign=0;
$product->meta['_tn_spin_attachment_ids']=array_fill(0,12,20);check($s->spin_frames($product)===[],'duplicate frames cannot fake a 360 sequence');
$product->meta['_tn_source_key']='';check($s->image('untouched',$product)==='untouched','unrelated product preserved');
$product->meta['_tn_source_key']='fixture';$fixtureProduct=$product;$s->register();$scripts=[];$enqueueCallback();check($scripts===[],'photo-only product loads no schematic module');
$product=null;$scripts=[];$enqueueCallback();check($product===$fixtureProduct&&$scripts===[],'enqueue resolves queried product before the Woo loop');
$product->meta['_tn_spin_attachment_ids']=range(20,31);$scripts=[];$enqueueCallback();check($scripts===['tn-photo-spin'],'reviewed sequence selects photo loader only');
check(str_contains($s->gallery('<div><a><img src="/uploads/11.jpg"></a></div>',11),'tehnet.ir'),'native gallery gets website overlay');
echo "PHOTO_CONTRACTS=$count PASSED\n";
