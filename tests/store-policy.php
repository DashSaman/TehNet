<?php
defined('ABSPATH') || define('ABSPATH', __DIR__ . '/');
if (!class_exists('TehNet_Store_Policy')) { fwrite(STDERR,"FAIL: sale policy missing\n"); exit(1); }
$check=static function(bool $ok,string $name):void { if(!$ok){throw new RuntimeException($name);}echo "PASS: $name\n"; };
$check(TehNet_Store_Policy::irr('12.5','IRT')===125,'exact fractional toman conversion');
$check(TehNet_Store_Policy::irr('۱۲۵۰','IRR')===1250,'Persian rial digits');
$check(TehNet_Store_Policy::irr('100.00','IRR')===100,'Woo decimal money string');
foreach(['1.2','-1','1e9','100,000','NaN'] as $bad){
    try { TehNet_Store_Policy::irr($bad,'IRR');throw new RuntimeException('invalid money accepted'); }
    catch(InvalidArgumentException $e){ echo "PASS: invalid rial rejected\n"; }
}
try {TehNet_Store_Policy::irr(1.1,'IRR');throw new RuntimeException('float accepted');}catch(InvalidArgumentException $e){echo "PASS: binary float rejected\n";}
try {TehNet_Store_Policy::irr('9223372036854775807','IRT');throw new RuntimeException('overflow accepted');}catch(InvalidArgumentException $e){echo "PASS: overflow rejected\n";}
$safe=['approved'=>'yes','price'=>'1000','stock'=>1,'unit'=>'piece','minimum'=>'1','erp_fresh_until'=>200,'erp_ready'=>true];
$check(TehNet_Store_Policy::can_sell($safe,100),'verified own stock available');
foreach(['approved'=>'no','price'=>'','stock'=>0,'unit'=>'','erp_fresh_until'=>99,'erp_ready'=>false] as $key=>$value){$bad=$safe;$bad[$key]=$value;$check(!TehNet_Store_Policy::can_sell($bad,100),'fail closed '.$key);}
$check(TehNet_Store_Policy::quantity_milli('2.5')===2500,'cable quantity to exact millimeters');
$check(TehNet_Store_Policy::line_total(2500,1000)===2500,'meter line total exact IRR');
try {TehNet_Store_Policy::line_total(333,1);throw new RuntimeException('fractional rial accepted');}catch(InvalidArgumentException $e){echo "PASS: fractional rial requires repricing\n";}
echo "STORE_POLICY=PASSED\n";
