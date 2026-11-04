<?php
/** Actual isolated WordPress renderer acceptance; no page save or request submission. */
if(!defined('WP_CLI')||!WP_CLI||wp_get_environment_type()!=='staging'||home_url('/')!=='http://localhost:18085/')throw new RuntimeException('Owned native staging only');
require getenv('TN_TRIAGE_COMPONENT');
$rules=TehNet\TechnicalResources\troubleshooting_rules();global $checks;$checks=0;
function triage_check(bool $value,string $label):void{global$checks;if(!$value)throw new RuntimeException('FAIL: '.$label);++$checks;}
triage_check(array_keys($rules)===['internet','dns','dhcp','vpn','vlan','nat','gateway'],'seven required problems');
foreach($rules as$rule){
    triage_check(isset($rule['observations']['unknown'])&&count($rule['observations'])>=3,'unknown and distinct observations');
    triage_check(strlen($rule['test'])>50&&strlen($rule['why'])>40&&strlen($rule['question'])>10,'substantive safe test reason and question');
    triage_check(str_starts_with($rule['source'],'https://learn.microsoft.com/')||str_starts_with($rule['source'],'https://manual.mikrotik.com/'),'official narrow source');
}
$a=do_shortcode('[tn_network_troubleshooting]');$b=do_shortcode('[tn_network_troubleshooting]');
triage_check(substr_count($a,'data-tn-triage-rule=')===7,'all seven guides are server rendered');
triage_check(!str_contains($a,'<form')&&!str_contains($a,'type="submit"'),'no duplicate request system');
triage_check(str_contains($a,'tn_service_context=network-support')&&str_contains($a,'https://mytel.one/services/'),'canonical support and MyTel boundaries');
triage_check(str_contains($a,'<noscript>')&&str_contains($a,'readonly')&&str_contains($a,'تشخیص قطعی نیست'),'honest fallback and read-only report');
preg_match_all('/\bid="([^"]+)"/',$a,$ids);preg_match_all('/\bid="([^"]+)"/',$b,$second);
triage_check(count($ids[1])===count(array_unique($ids[1]))&&array_intersect($ids[1],$second[1])===[],'multiple instance IDs unique');
foreach($ids[1]as$id)triage_check(str_contains($a,'for="'.$id.'"')||str_contains($a,'aria-labelledby="'.$id.'"'),'control/title IDs referenced');
if(getenv('TN_TRIAGE_RENDER')==='1'){
 echo '<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>آزمون تصمیم‌یار شبکه</title><link rel="stylesheet" href="/corporate.css"><link rel="stylesheet" href="/network-troubleshooting.css"><style>body{margin:0;font-family:Estedad,sans-serif}main{max-width:1080px;margin:auto;padding:16px}@font-face{font-family:Estedad;src:url(/Estedad.woff2)}html[data-theme=dark]{--bg:#091522;--surface:#102234;--text:#e6f2fa;--border:#33526b;--primary:#7fdde6;--on-primary:#092133}html{background:var(--bg,#fff);color:var(--text,#172f48)}</style></head><body><main><h1>مؤلفهٔ تصمیم‌یار شبکه؛ fixture بومی WordPress</h1>'.$a.$b.'</main><script src="/network-troubleshooting.js" defer></script></body></html>';
}else echo 'TRIAGE_NATIVE=PASS checks='.$checks."\n";
