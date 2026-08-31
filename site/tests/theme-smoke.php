<?php
$base = dirname(__DIR__) . '/wp-content/themes/tehnet';
$required = ['style.css','functions.php','theme.json','front-page.php','header.php','footer.php','assets/css/app.css','assets/js/theme-toggle.js'];
$missing=[]; foreach($required as $file){ if(!is_file($base.'/'.$file)) $missing[]=$file; }
if($missing){fwrite(STDERR,'Missing theme files: '.implode(', ',$missing).PHP_EOL);exit(1);}
$front=file_get_contents($base.'/front-page.php');
foreach(['/learn/','/labs/','/services/','/shop/'] as $path){if(strpos($front,$path)===false){fwrite(STDERR,"Missing homepage journey link: $path\n");exit(1);}}
echo "theme-smoke: PASS\n";
