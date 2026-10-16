<?php
define('ABSPATH',__DIR__);function add_shortcode(...$a){}function add_action(...$a){}
require __DIR__.'/../site/mu-plugins/tehnet-technical-resources.php';$count=0;
foreach([[1500,4,1440],[1500,6,1420],[1492,4,1432],[1492,6,1412],[576,4,516],[1280,6,1200],[9000,6,8920]]as [$p,$ip,$want]){if(TehNet\TechnicalResources\wireguard_mtu($p,$ip)!==$want)throw new RuntimeException('MTU mismatch');$count++;}
foreach([[575,4],[1279,6],[9001,4],[1500,5]]as [$p,$ip]){$blocked=false;try{TehNet\TechnicalResources\wireguard_mtu($p,$ip);}catch(InvalidArgumentException $e){$blocked=true;}if(!$blocked)throw new RuntimeException('invalid input accepted');$count++;}
echo "MTU_CONTRACTS=$count PASSED\n";
