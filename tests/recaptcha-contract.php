<?php
/** Provider contract fixtures only. No Google requests or credentials. */
define('ABSPATH',__DIR__.'/');
$options=[];$calls=[];$response=[];
function get_option($key,$fallback=false){global $options;return $options[$key]??$fallback;}
function home_url($path=''){return 'https://tehnet.ir'.$path;}
function wp_remote_post($url,$args){global $calls,$response;$calls[]=[$url,$args];return $response;}
function is_wp_error($v){return $v instanceof Exception;}
function wp_remote_retrieve_response_code($v){return $v['response']['code']??0;}
function wp_remote_retrieve_body($v){return $v['body']??'';}
require __DIR__.'/../site/plugins/tehnet-store/includes/class-recaptcha.php';
$count=0;
function check($ok,$label){global $count;if(!$ok)throw new RuntimeException($label);++$count;echo "PASS: $label\n";}
check(TehNet_Store_Recaptcha::verify(null)['ok']&&count($calls)===0,'unconfigured intake keeps existing controls without external calls');
$options=['tn_recaptcha_enabled'=>'yes'];
check(TehNet_Store_Recaptcha::verify('fixture')['status']===503,'explicit enabled but missing config fails closed');
$options+=['tn_recaptcha_site_key'=>'fixture-public-key','tn_recaptcha_secret_key'=>'fixture-private-value'];
foreach([null,[],str_repeat('x',4097),"bad\ntoken"]as$token)check(!TehNet_Store_Recaptcha::verify($token)['ok'],'malformed token rejected');
check(count($calls)===0,'malformed tokens do not call provider');
$valid=['success'=>true,'hostname'=>'tehnet.ir','challenge_ts'=>gmdate('c')];
$response=['response'=>['code'=>200],'body'=>json_encode($valid)];
check(TehNet_Store_Recaptcha::verify('fixture-token')['ok'],'valid hostname fresh provider response accepted');
[$url,$args]=$calls[0];
check($url==='https://www.google.com/recaptcha/api/siteverify'&&$args['sslverify']===true&&$args['redirection']===0&&$args['timeout']===8,'fixed TLS provider endpoint with bounded request');
check($args['body']===['secret'=>'fixture-private-value','response'=>'fixture-token'],'no client IP or form data forwarded');
foreach([
 ['success'=>false,'error-codes'=>['timeout-or-duplicate']],
 ['success'=>'true'],
 ['hostname'=>'attacker.invalid'],
 ['hostname'=>'tehnet.ir.attacker.invalid'],
 ['challenge_ts'=>gmdate('c',time()-121)],
 ['challenge_ts'=>gmdate('c',time()+31)],
 ['challenge_ts'=>'invalid'],
]as$change){$response['body']=json_encode(array_replace($valid,$change));check(!TehNet_Store_Recaptcha::verify('fixture-token')['ok'],'invalid provider result fails closed');}
$response=['response'=>['code'=>500],'body'=>json_encode($valid)];
check(TehNet_Store_Recaptcha::verify('fixture-token')['status']===503,'upstream HTTP error is recoverable failure');
$response=['response'=>['code'=>200],'body'=>'not-json'];
check(!TehNet_Store_Recaptcha::verify('fixture-token')['ok'],'invalid JSON fails closed');
$response=new Exception('private diagnostic');
check(TehNet_Store_Recaptcha::verify('fixture-token')['status']===503,'network error fails closed');
echo "RECAPTCHA_CONTRACTS=PASSED checks=$count\n";
