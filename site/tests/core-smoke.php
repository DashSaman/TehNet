<?php
$plugin=dirname(__DIR__).'/wp-content/plugins/tehnet-core';
$required=['tehnet-core.php','src/content-types.php','src/relations.php','src/product-inquiry.php'];
$missing=[];foreach($required as $file){if(!is_file($plugin.'/'.$file))$missing[]=$file;}
if($missing){fwrite(STDERR,'Missing plugin files: '.implode(', ',$missing).PHP_EOL);exit(1);}
$all='';foreach($required as $file)$all.=file_get_contents($plugin.'/'.$file)."\n";
foreach(['tn_lab','tn_service','_tehnet_sale_mode','direct','inquiry'] as $needle){if(strpos($all,$needle)===false){fwrite(STDERR,"Missing required core token: $needle\n");exit(1);}}
echo "core-smoke: PASS\n";
