<?php
if(wp_get_environment_type()!=='staging'||home_url('/')!=='http://localhost:18085/'||!WP_HTTP_BLOCK_EXTERNAL||!DISABLE_WP_CRON||(string)get_option('blog_public')!=='0')throw new RuntimeException('Closed staging required');
$checks=0;$ok=static function(bool$v)use(&$checks):void{if(!$v)throw new RuntimeException('Real WinBox renderer failed');++$checks;};
foreach([62=>14,63=>25]as$id=>$count){$p=get_post($id);$h=do_blocks($p->post_content);$ok($p->post_type==='page');$ok(substr_count($h,'<figure class="wp-block-image')===$count);$ok(substr_count($h,'<img ')===$count);$ok(str_contains($h,'آموزش نوشتاری مستقل')&&str_contains($h,'CHR'));$ok(!str_contains($h,'VideoObject')&&!str_contains($h,'youtube.com')&&!str_contains($h,'youtu.be'));$ok(substr_count($h,'class="tn-lab-capture')===0);$ok(str_contains($h,'class="wp-block-image size-full tn-lab-capture tn-lab-shot-'));$ok(!str_contains($h,'<form'));}
echo 'WINBOX_CORE_RENDERER=PASS checks='.$checks."\n";
