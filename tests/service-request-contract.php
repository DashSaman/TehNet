<?php
/** Server-rendered service intake contracts; real persistence is verified separately in isolated WordPress. */
define('ABSPATH', __DIR__);
function esc_attr($s){return htmlspecialchars((string)$s,ENT_QUOTES,'UTF-8');}
function esc_html($s){return esc_attr($s);}
function esc_url($s){return esc_attr($s);}
function admin_url($s){return 'https://example.test/wp-admin/'.$s;}
function wp_unslash($s){return stripslashes($s);}
function wp_nonce_field($a=-1,$n='_wpnonce',$r=true,$display=true){$s='<input name="'.$n.'" value="synthetic">';if($display)echo $s;return $s;}
require __DIR__.'/../site/plugins/tehnet-store/includes/class-tickets.php';
$n=0;function check($v,$label){global$n;$n++;if(!$v)throw new RuntimeException('FAIL '.$label);echo 'PASS '.$label."\n";}
check(is_callable([TehNet_Store_Tickets::class,'service_options']),'existing ticket class owns approved service options');
$ticket=new TehNet_Store_Tickets();
check(is_callable([$ticket,'service_shortcode']),'short service form available in existing ticket component');
foreach(['network-support','network-setup','mikrotik','remote-support','voice-network','general-network']as$key){
    check((TehNet_Store_Tickets::service_context($key)['key']??'')===$key,'approved intent '.$key);
}
foreach(['pbx','mytel','fortinet',['network-support'],null,1]as$bad)check(TehNet_Store_Tickets::service_context($bad)===[],'reject unapproved context '.gettype($bad));
$_GET=['tn_service_context'=>'mikrotik'];ob_start();$html=$ticket->service_shortcode();$stray=ob_get_clean();
check($stray==='','service shortcode returns its complete form');
check(str_contains($html,'name="action" value="tn_ticket_submit"'),'same canonical ticket action');
check(str_contains($html,'name="tn_request_kind" value="service"'),'explicit service request mode');
check(str_contains($html,'name="_wpnonce"'),'nonce belongs to returned form');
check(str_contains($html,'value="mikrotik" selected'),'known service preselected');
check(!str_contains($html,'name="tn_subject"'),'short form derives subject server-side');
foreach(['tn_name','tn_email','tn_message','tn_company','tn_hp']as$name)check(str_contains($html,'name="'.$name.'"'),'field '.$name);
check(str_contains($html,'رمز')&&str_contains($html,'پیش‌فاکتور'),'privacy and scope explained');
$_GET=['tn_service_context'=>['<script>']];$html=$ticket->service_shortcode();
check(!str_contains($html,'<script>'),'malformed query not reflected');
echo 'SERVICE_REQUEST_CONTRACTS='.$n."\n";
