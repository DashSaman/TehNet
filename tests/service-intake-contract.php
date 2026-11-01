<?php
/** WordPress nonce echo/return boundary; no database or customer writes. */
define('ABSPATH', __DIR__);
function esc_attr($s){return htmlspecialchars((string)$s,ENT_QUOTES,'UTF-8');}
function esc_html($s){return esc_attr($s);}
function esc_url($s){return esc_attr($s);}
function admin_url($p){return 'https://example.test/wp-admin/'.$p;}
function wc_get_products($a){return [];}
function get_option($key,$fallback=false){return $fallback;}
function wp_unslash($s){return stripslashes($s);}
function wp_nonce_field($action=-1,$name='_wpnonce',$referer=true,$display=true){
    $value='<input type="hidden" name="'.esc_attr($name).'" value="synthetic-guard">';
    if($referer)$value.='<input type="hidden" name="_wp_http_referer" value="/synthetic/">';
    if($display)echo $value;
    return $value;
}
require __DIR__.'/../site/plugins/tehnet-store/includes/class-recaptcha.php';
require __DIR__.'/../site/plugins/tehnet-store/includes/class-tickets.php';
require __DIR__.'/../site/plugins/tehnet-store/includes/class-quotes.php';
$checks=0;$failures=[];
function check($value,$label){global$checks,$failures;$checks++;if(!$value)$failures[]=$label;echo($value?'PASS ':'FAIL ').$label."\n";}
foreach([TehNet_Store_Tickets::class,TehNet_Store_Quotes::class]as$class){
    $_GET=[];ob_start();$html=(new $class())->shortcode();$stray=ob_get_clean();
    check($stray==='', $class.' shortcode has no stray nonce output');
    preg_match('/<form\b[^>]*>(.*?)<\/form>/s',$html,$match);
    check(str_contains($match[1]??'', 'name="_wpnonce"'),$class.' nonce belongs to returned form');
    check(str_contains($match[1]??'', 'name="_wp_http_referer"'),$class.' referer belongs to returned form');
}
check(is_callable([TehNet_Store_Tickets::class,'service_context']),'service context resolver exists');
if(is_callable([TehNet_Store_Tickets::class,'service_context'])){
    $context=TehNet_Store_Tickets::service_context('voice-network');
    check(($context['key']??'')==='voice-network'&&str_contains($context['label']??'','شبکه'),'approved networking context');
    foreach(['mytel','pbx','https://evil.test','<script>alert(1)</script>',['voice-network'],null,1]as$value)
        check(TehNet_Store_Tickets::service_context($value)===[],'unapproved or malformed context rejected: '.gettype($value));
    $_GET=['tn_service_context'=>'voice-network'];ob_start();$html=(new TehNet_Store_Tickets())->shortcode();$stray=ob_get_clean();
    check(str_contains($html,'name="tn_service_context" value="voice-network"'),'context travels in existing ticket form');
    check(str_contains($html,'name="tn_subject"')&&str_contains($html,esc_attr($context['label'])),'service subject prefilled');
    $_GET=['tn_service_context'=>['<script>']];ob_start();$html=(new TehNet_Store_Tickets())->shortcode();ob_end_clean();
    check(!str_contains($html,'<script>')&&!str_contains($html,'name="tn_service_context"'),'malformed query adds no context');
    $_GET=['tn_service'=>'voice-network'];ob_start();$html=(new TehNet_Store_Tickets())->shortcode();ob_end_clean();
    check(!str_contains($html,'name="tn_service_context"')&&!str_contains($html,'name="tn_service"'),'registered service CPT query variable is not used for intake');
}
echo 'SERVICE_INTAKE_CHECKS='.$checks.' FAILURES='.count($failures)."\n";
exit($failures?1:0);
