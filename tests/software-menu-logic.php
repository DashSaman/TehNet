<?php
declare(strict_types=1);
$items=[];$next=10;$updates=0;$meta=[];
function home_url($path=''){return 'https://tehnet.ir'.$path;}
function get_nav_menu_locations(){return ['primary'=>3];}
function wp_get_nav_menu_items($id){global $items;return array_values($items);}
function wp_update_nav_menu_item($menu,$id,$args){global $items,$next,$updates;$id=$next++;$updates++;$items[$id]=(object)['ID'=>$id,'url'=>$args['menu-item-url']];return $id;}
function is_wp_error($value){return false;}
function update_post_meta($id,$key,$value){global $meta;$meta[$id][$key]=$value;}
function get_post_meta($id,$key,$single){global $meta;return $meta[$id][$key]??'';}
function wp_delete_post($id,$force){global $items;unset($items[$id]);return true;}
require __DIR__.'/../ops/lib/software-menu.php';
function check($ok,$message){if(!$ok){fwrite(STDERR,"FAIL: $message\n");exit(1);}}
$items[1]=(object)['ID'=>1,'url'=>'https://tehnet.ir/shop/'];
$first=tn_software_menu_ensure('fixture-owner');
check($first['created']===true,'creates missing menu item');
$second=tn_software_menu_ensure('fixture-owner');
check($second['created']===false && $updates===1,'repeat does not duplicate');
check(isset($items[1]) && $items[1]->url==='https://tehnet.ir/shop/','existing item preserved');
try{tn_software_menu_rollback($first['id'],'wrong-owner');check(false,'wrong owner denied');}catch(RuntimeException $e){}
tn_software_menu_rollback($first['id'],'fixture-owner');
check(count($items)===1 && isset($items[1]),'rollback removes only owned added item');
echo "SOFTWARE_MENU_LOGIC=PASS (5 checks)\n";
