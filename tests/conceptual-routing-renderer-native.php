<?php
/** Native preview only; exercise the installed shortcode without writing any records. */
if(!defined('WP_CLI')||!WP_CLI||wp_get_environment_type()!=='staging'||home_url('/')!=='http://localhost:18085/')throw new RuntimeException('Owned isolated preview only');
global $routingChecks;$routingChecks=0;
function route_renderer_check(bool $value,string $label):void{global$routingChecks;if(!$value)throw new RuntimeException('FAIL: '.$label);++$routingChecks;}
$a=do_shortcode('[tn_static_routing_lab]');$b=do_shortcode('[tn_static_routing_lab]');
route_renderer_check(substr_count($a,'data-tn-routing-node=')===4,'four explicit topology nodes');
route_renderer_check(substr_count($a,'data-tn-routing-choice=')===2&&substr_count($a,'value="correct"')===2,'two independent route exercises');
route_renderer_check(str_contains($a,'شبیه‌ساز واقعی روتر نیست')&&str_contains($a,'بسته‌ای ارسال')&&str_contains($a,'RFC5737'),'model limits and documentation addresses visible');
route_renderer_check(str_contains($a,'<noscript>')&&str_contains($a,'<details>')&&str_contains($a,'/ip route add'),'manual no-JS answer and educational syntax visible');
route_renderer_check(!str_contains($a,'<form')&&!str_contains($a,'<input')&&!str_contains($a,'type="submit"'),'no network target input or duplicate form');
preg_match_all('/\bid="([^"]+)"/',$a,$ids);preg_match_all('/\bid="([^"]+)"/',$b,$other);
route_renderer_check(count($ids[1])===4&&count($ids[1])===count(array_unique($ids[1]))&&array_intersect($ids[1],$other[1])===[],'multiple instances have unique label IDs');
route_renderer_check(shortcode_exists('tn_network_troubleshooting')&&str_contains(do_shortcode('[tn_network_troubleshooting]'),'data-tn-triage'),'previous manual triage retained');
echo 'ROUTING_RENDERER=PASS checks='.$routingChecks."\n";
