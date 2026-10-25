<?php
declare(strict_types=1);
require '/var/www/html/wp-load.php';
require __DIR__.'/software-menu-lib.php';
$mode=$argv[1]??'plan';
$owner=$argv[2]??'';
if ($mode==='apply' && $owner!=='') {
    echo json_encode(tn_software_menu_ensure($owner),JSON_UNESCAPED_UNICODE)."\n";
} elseif ($mode==='rollback-owner' && $owner!=='') {
    tn_software_menu_rollback_owner($owner);
    echo "MENU_ROLLBACK=PASS\n";
} elseif ($mode==='rollback' && $owner!=='' && ctype_digit($argv[3]??'')) {
    tn_software_menu_rollback((int)$argv[3],$owner);
    echo "MENU_ROLLBACK=PASS\n";
} elseif ($mode==='plan') {
    $locations=get_nav_menu_locations();
    $items=wp_get_nav_menu_items((int)($locations['primary']??0))?:[];
    echo json_encode(['primary'=>$locations['primary']??null,'items'=>array_map(static fn($item)=>['id'=>(int)$item->ID,'url'=>$item->url,'title'=>$item->title],$items)],JSON_UNESCAPED_UNICODE)."\n";
} else { fwrite(STDERR,"Invalid operation\n"); exit(1); }
