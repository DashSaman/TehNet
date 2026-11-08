<?php
if(wp_get_environment_type()!=='staging'||home_url('/')!=='http://localhost:18085/'||!WP_HTTP_BLOCK_EXTERNAL||!DISABLE_WP_CRON||(string)get_option('blog_public')!=='0')throw new RuntimeException('Closed staging required');
$p=get_post(67);$html=do_blocks($p->post_content);$checks=0;
$ok=static function(bool$value,string$label)use(&$checks):void{if(!$value)throw new RuntimeException('FAIL: '.$label);++$checks;echo 'PASS: '.$label."\n";};
$ok($p->post_type==='page'&&get_page_uri(67)==='learn/mikrotik/mtcna/queues-troubleshooting','Same existing owner');
$ok(substr_count($html,'<figure class="wp-block-image')===12,'Exactly12 native figures');
$ok(substr_count($html,'<img ')===12,'Exactly12 original images');
$ok(substr_count($html,'tn-lab-capture tn-queue-shot-')===12,'All scoped native figure classes');
$ok(str_contains($html,'WinBox')&&str_contains($html,'CHR')&&str_contains($html,'راهنمای تکمیلی مستقل'),'Truthful source and independent supplement');
$ok(!str_contains($html,'VideoObject')&&!str_contains($html,'youtube.com')&&!str_contains($html,'youtu.be'),'No invented video attribution');
$ok(!str_contains($html,'<form'),'No duplicate request form');
$ok(substr_count($html,'id="winbox-queue-cloud"')===1,'Exactly one reachable new anchor');
echo 'QUEUE_CLOUD_RENDERER=PASS checks='.$checks."\n";
