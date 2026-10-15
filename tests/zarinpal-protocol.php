<?php
/** Standalone protocol tests: PHP only; mocked HTTP, no WordPress/ERP/provider. */
define('ABSPATH',__DIR__);
$GLOBALS['environment']='local';$GLOBALS['responses']=[];$GLOBALS['requests']=[];
function wp_get_environment_type(){return $GLOBALS['environment'];}
function wp_json_encode($v){return json_encode($v,JSON_THROW_ON_ERROR);}
function wp_remote_post($url,$args){$GLOBALS['requests'][]=[$url,$args];$r=array_shift($GLOBALS['responses']);return is_callable($r)?$r():$r;}
function is_wp_error($v){return $v instanceof Exception;}
function wp_remote_retrieve_response_code($v){return $v['status'];}
function wp_remote_retrieve_body($v){return $v['body'];}
require __DIR__.'/../site/plugins/tehnet-store/includes/class-zarinpal-sandbox.php';
$count=0;
function check($ok,$label){if(!$ok){throw new RuntimeException($label);}++$GLOBALS['count'];echo "PASS: $label\n";}
function response($data,$status=200){$GLOBALS['responses'][]=['status'=>$status,'body'=>json_encode(['data'=>$data,'errors'=>[]])];}
function rejected($fn,$label){try{$fn();}catch(RuntimeException|InvalidArgumentException $e){check(true,$label);return;}throw new RuntimeException('Accepted: '.$label);}
$api=new TehNet_Store_Zarinpal_Sandbox();$authority='S'.str_repeat('0',35);
response(['code'=>100,'authority'=>$authority]);
check($api->request(11000,'http://localhost:18083/?callback=1')===$authority,'request accepts a sandbox authority');
[$url,$args]=$GLOBALS['requests'][0];$body=json_decode($args['body'],true);
check($url==='https://sandbox.zarinpal.com/pg/v4/payment/request.json','only the fixed sandbox host is used');
check($body['amount']===11000 && $body['currency']==='IRR','integer IRR is sent without a toman multiplier');
check($args['sslverify']===true && $args['redirection']===0 && $args['timeout']===25,'TLS and bounded transport cannot be weakened');
foreach([100,101] as $code){response(['code'=>$code,'ref_id'=>123456]);check($api->verify($authority,11000)==='123456','server verification code '.$code.' yields the receipt');}
rejected(fn()=>$api->verify('A'.str_repeat('0',35),11000),'production authority rejected before network');
response(['code'=>100,'authority'=>'A'.str_repeat('0',35)]);rejected(fn()=>$api->request(11000,'http://localhost:18083/'),'production authority response rejected');
foreach([['code'=>100],['code'=>100,'ref_id'=>0],['code'=>100,'ref_id'=>'1e9'],['code'=>-51,'ref_id'=>123],['code'=>101,'ref_id'=>[]]] as $bad){response($bad);rejected(fn()=>$api->verify($authority,11000),'invalid verification response rejected');}
response(['code'=>100,'ref_id'=>123],500);rejected(fn()=>$api->verify($authority,11000),'HTTP failure cannot become a receipt');
$GLOBALS['responses'][]=new RuntimeException('timeout');rejected(fn()=>$api->verify($authority,11000),'transport uncertainty cannot become a receipt');
$GLOBALS['responses'][]=['status'=>200,'body'=>'<html>'];rejected(fn()=>$api->verify($authority,11000),'invalid JSON is rejected');
foreach([0,-1] as $bad){rejected(fn()=>$api->verify($authority,$bad),'nonpositive amount rejected');}
$GLOBALS['environment']='production';$n=count($GLOBALS['requests']);rejected(fn()=>$api->verify($authority,11000),'production environment refuses sandbox verification');check(count($GLOBALS['requests'])===$n,'production guard runs before network');
echo 'ZARINPAL_PROTOCOL=PASSED checks='.$count."\n";
