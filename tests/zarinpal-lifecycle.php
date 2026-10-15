<?php
/** State-machine tests with fake Woo/ERP objects, not a native integration test. */
require __DIR__.'/zarinpal-protocol.php';
require __DIR__.'/../site/plugins/tehnet-store/includes/class-policy.php';
define('TEHNET_PAYMENT_SANDBOX_ENABLED',true);define('TEHNET_ERP_SANDBOX',true);
$GLOBALS['environment']='local';$GLOBALS['responses']=[];$GLOBALS['requests']=[];$GLOBALS['options']=[];$GLOBALS['count']=0;
function add_option($k,$v,$a='',$b=false){if(array_key_exists($k,$GLOBALS['options'])){return false;}$GLOBALS['options'][$k]=$v;return true;}
function get_option($k){return $GLOBALS['options'][$k]??false;}
function delete_option($k){unset($GLOBALS['options'][$k]);}
function home_url($path){return 'http://localhost:18083'.$path;}
function add_query_arg($args,$url){return $url.'?'.http_build_query($args);}
class WC_Order {
    public array $meta=[];public string $status='pending',$amount='11000',$transaction='',$currency='IRR';public int $completions=0;public bool $synthetic=true;
    public function __construct(public int $id){}
    public function get_id(){return $this->id;}
    public function get_payment_method(){return TehNet_Store_Zarinpal_Sandbox::ID;}
    public function get_currency(){return $this->currency;}
    public function get_total(){return $this->amount;}
    public function get_items(){return [new class($this->synthetic){public function __construct(private bool $synthetic){}public function get_product(){return new class($this->synthetic){public function __construct(private bool $synthetic){}public function get_meta($k){return $this->synthetic?'yes':'';}public function is_virtual(){return false;}public function is_downloadable(){return false;}};}}];}
    public function get_meta($k){return $this->meta[$k]??'';}
    public function update_meta_data($k,$v){$this->meta[$k]=$v;}
    public function save(){}
    public function read_meta_data($force){}
    public function get_data_store(){return new class{public function read($o){foreach($GLOBALS['concurrent_updates'][$o->id]??[] as $key=>$value){$o->$key=$value;}unset($GLOBALS['concurrent_updates'][$o->id]);}};}
    public function has_status($s){return in_array($this->status,(array)$s,true);}
    public function update_status($s,$note=''){$this->status=$s;}
    public function is_paid(){return $this->has_status(['processing','completed']);}
    public function get_transaction_id(){return $this->transaction;}
    public function payment_complete($ref){$this->transaction=$ref;$this->status='processing';++$this->completions;}
}
class TehNet_Store_ERP {
    public static string $state='reserved';public static bool $offline=false;
    public function reconcile_order($order){if(self::$offline){throw new RuntimeException('offline');}if(self::$state==='paid' && $order->transaction!==''){$order->status='processing';}return ['state'=>self::$state];}
}
function started($id,$digit){$o=new WC_Order($id);response(['code'=>100,'authority'=>'S'.str_repeat($digit,35)]);(new TehNet_Store_Zarinpal_Sandbox())->start($o);return $o;}
function receive($o,$status='OK'){$r=$o->get_meta('_tn_zp_attempt');return (new TehNet_Store_Zarinpal_Sandbox())->receive($o,$r['authority'],$r['token'],$status);}
$o=started(1,'1');$r=$o->get_meta('_tn_zp_attempt');$n=count($GLOBALS['requests']);
check($r['state']==='requested' && $r['amount']===11000 && strlen($r['token'])===64,'attempt is persisted with exact amount and strong callback token');
$api->start($o);check(count($GLOBALS['requests'])===$n,'repeated start reuses one authority');
rejected(fn()=>$api->receive($o,$r['authority'],str_repeat('a',64),'OK'),'forged callback token is rejected');
rejected(fn()=>$api->receive($o,'S'.str_repeat('9',35),$r['token'],'OK'),'authority from another order is rejected');
$o->amount='11001';rejected(fn()=>receive($o),'changed order amount is rejected');$o->amount='11000';
check(count($GLOBALS['requests'])===$n,'invalid callbacks never reach provider verification');
check(receive($o,'NOK')['state']==='not-verified' && $o->status==='pending','browser NOK alone neither pays nor cancels the reservation');
response(['code'=>101,'ref_id'=>111]);check(receive($o)['state']==='verified' && $o->completions===1,'previously verified provider response recovers payment exactly once');
$n=count($GLOBALS['requests']);check(receive($o)['state']==='verified' && $o->completions===1 && count($GLOBALS['requests'])===$n,'repeated callback reuses the durable receipt');
$GLOBALS['options']['tn_zp_order_lock_1']='interrupted';rejected(fn()=>receive($o),'concurrent/interrupted callback lock is respected');delete_option('tn_zp_order_lock_1');
$closed=started(2,'2');$closed->status='cancelled';response(['code'=>100,'ref_id'=>222]);
check(receive($closed)['state']==='needs-reconciliation' && $closed->status==='on-hold' && !$closed->completions,'late sandbox receipt cannot resurrect a canceled reservation');
check(receive($closed)['state']==='needs-reconciliation' && !$closed->completions,'late-payment marker survives repeated callbacks');
$uncertain=new WC_Order(3);$GLOBALS['responses'][]=new RuntimeException('timeout');rejected(fn()=>$api->start($uncertain),'request timeout is explicit');
check($uncertain->get_meta('_tn_zp_attempt')['state']==='unknown','unknown request outcome remains durable');$n=count($GLOBALS['requests']);
rejected(fn()=>$api->start($uncertain),'unknown request cannot create a second payment');check(count($GLOBALS['requests'])===$n,'unknown request does not retry network creation');
$real=new WC_Order(4);$real->synthetic=false;rejected(fn()=>$api->start($real),'ordinary catalog items are forbidden');
$nonrial=new WC_Order(5);$nonrial->currency='IRT';rejected(fn()=>$api->start($nonrial),'non-IRR orders are forbidden');
TehNet_Store_ERP::$state='expired';rejected(fn()=>$api->start(new WC_Order(6)),'expired ERP reservation blocks new payment');TehNet_Store_ERP::$state='reserved';
$duplicate=started(7,'7');response(['code'=>100,'ref_id'=>111]);rejected(fn()=>receive($duplicate),'one provider receipt cannot pay a second order');
$retry=started(8,'8');$GLOBALS['responses'][]=new RuntimeException('timeout');rejected(fn()=>receive($retry),'verification timeout does not mark order paid');
check(empty($retry->get_meta('_tn_zp_attempt')['ref_id']) && !$retry->completions,'verification failure preserves the unpaid order');
response(['code'=>101,'ref_id'=>888]);check(receive($retry)['state']==='verified' && $retry->completions===1,'verification retry recovers with code 101');
$hold=started(9,'9');TehNet_Store_ERP::$offline=true;response(['code'=>100,'ref_id'=>999]);
check(receive($hold)['state']==='needs-reconciliation' && $hold->get_meta('_tn_zp_attempt')['ref_id']==='999' && !$hold->completions,'ERP outage retains verified receipt on hold');
TehNet_Store_ERP::$offline=false;check(receive($hold)['state']==='verified' && $hold->completions===1,'ERP recovery applies the stored receipt once');
$hold->status='on-hold';TehNet_Store_ERP::$state='paid';check(receive($hold)['state']==='verified' && $hold->completions===1,'ERP reconciliation of paid receipt does not create a second payment');TehNet_Store_ERP::$state='reserved';
$race=started(11,'b');$GLOBALS['responses'][]=static function(){$GLOBALS['concurrent_updates'][11]=['status'=>'cancelled'];return ['status'=>200,'body'=>json_encode(['data'=>['code'=>100,'ref_id'=>1111]])];};
check(receive($race)['state']==='needs-reconciliation' && !$race->completions,'cancellation during provider verification is reloaded before completion');
$edit=started(12,'c');$GLOBALS['responses'][]=static function(){$GLOBALS['concurrent_updates'][12]=['amount'=>'11001'];return ['status'=>200,'body'=>json_encode(['data'=>['code'=>100,'ref_id'=>1212]])];};
check(receive($edit)['state']==='needs-reconciliation' && !$edit->completions && $edit->get_meta('_tn_zp_attempt')['ref_id']==='1212','concurrent amount edit retains receipt and stops completion');
$GLOBALS['environment']='production';rejected(fn()=>$api->start(new WC_Order(10)),'production guard refuses the entire order flow');
echo 'ZARINPAL_LIFECYCLE=PASSED checks='.$GLOBALS['count']."\n";
