<?php
define('ABSPATH',__DIR__);
function add_shortcode(...$a){} function add_action(...$a){}
function esc_attr($s){return htmlspecialchars((string)$s,ENT_QUOTES,'UTF-8');}
function esc_html($s){return esc_attr($s);}
function wp_unique_id($prefix=''){static$n=0;return$prefix.(++$n);}
require __DIR__.'/../site/mu-plugins/tehnet-technical-resources.php';
$count=0;
function check($v,$label){global$count;$count++;if(!$v){echo'FAIL '.$label."\n";exit(1);}echo'PASS '.$label."\n";}
check(function_exists('TehNet\\TechnicalResources\\readiness_checklist'),'network readiness shortcode implementation exists');
$html=TehNet\TechnicalResources\readiness_checklist();
check(substr_count($html,'data-tn-readiness-select')===8,'eight real manual questions');
check(substr_count($html,'<legend')===8&&substr_count($html,'<label')===8,'question groups and labels visible without JavaScript');
check(substr_count($html,'value="unknown"')===8&&substr_count($html,'value="issue"')===8,'unknown and issue are first-class states');
check(str_contains($html,'<noscript>'),'no-JS guidance retained');
check(str_contains($html,'aria-live="polite"'),'summary announced accessibly');
check(!str_contains($html,'<form')&&!str_contains($html,'type="submit"'),'tool cannot submit a service request');
check(str_contains($html,'اندازه‌گیری شبکه نیست'),'manual assessment is not misrepresented as measurement');
preg_match_all('/\bid="([^"]+)"/',$html,$a);$second=TehNet\TechnicalResources\readiness_checklist();preg_match_all('/\bid="([^"]+)"/',$second,$b);
check(count($a[1])===count(array_unique($a[1])),'instance IDs unique');
check(array_intersect($a[1],$b[1])===[],'multiple instances do not share IDs');
echo 'READINESS_CHECKS='.$count.' FAILURES=0'."\n";
