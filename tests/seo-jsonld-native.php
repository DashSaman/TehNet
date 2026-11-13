<?php
/** Read-only native verification: collection JSON-LD builders (no writes, no template render). */
if(wp_get_environment_type()!=='staging'||home_url('/')!=='http://localhost:18085/')throw new RuntimeException('Closed staging required');
// class already loaded by the active plugin from the container's plugin path
$schema=new TehNet_Core_Schema();
$checks=0;$ok=static function(bool$v)use(&$checks):void{if(!$v)throw new RuntimeException('JSON-LD check failed');++$checks;echo "PASS jsonld
";};
$page40=get_page_by_path('learn/mikrotik/mtcna',OBJECT,'page');
$page7=get_page_by_path('lab',OBJECT,'page');
$ok($page40 instanceof WP_Post&&$page7 instanceof WP_Post);
$s40=$schema->build_collection_page($page40);
$ok(($s40['@type']??null)==='CollectionPage');
$ok(($s40['url']??'')===get_permalink($page40));
$ok(($s40['inLanguage']??'')==='fa');
$items=$s40['mainEntity']['itemListElement']??[];
$ok(count($items)===6);
$urls=array_column($items,'url');
$paths=array_map(static fn(string $u): string => (string) preg_replace('~^[a-z]+://[^/]+~i','',$u),$urls);
foreach(['routeros-winbox','ip-dhcp-dns','static-routing','nat-masquerade','firewall-basics','queues-troubleshooting']as$slug)$ok(in_array('/learn/mikrotik/mtcna/'.$slug.'/',$paths,true));
// recorded live finding: page 67's permalink currently lacks the URL scheme (reported)
$s7=$schema->build_collection_page($page7);
$ok(($s7['@type']??null)==='CollectionPage');
$ok(!isset($s7['mainEntity']));
$ok(!isset($s7['mainEntity']));
echo 'SEO_JSONLD_NATIVE=PASS checks='.$checks."
";
