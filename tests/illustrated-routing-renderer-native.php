<?php
/** Actual WordPress renderer, isolated staging only. */
if(wp_get_environment_type()!=='staging'||home_url('/')!=='http://localhost:18085/'||!WP_HTTP_BLOCK_EXTERNAL||!DISABLE_WP_CRON||(string)get_option('blog_public')!=='0')throw new RuntimeException('Closed staging required');
$p=get_post(64);$h=do_blocks($p->post_content);$checks=0;
$ok=static function(bool $v)use(&$checks):void{if(!$v)throw new RuntimeException('Illustrated article renderer failed');++$checks;};
$ok($p->post_type==='page'&&get_page_uri($p)==='learn/mikrotik/mtcna/static-routing');
$ok(WP_Block_Type_Registry::get_instance()->is_registered('core/image'));
$ok(substr_count($h,'<figure class="wp-block-image')===4);
$ok(substr_count($h,'<img ')===4&&substr_count($h,'/learning-media/static-routing-20261104/')===8);
$ok(str_contains($h,'<strong>بررسی پاسخ در مدل</strong>')&&str_contains($h,'<strong>گام بعد بسته</strong>'));
$ok(str_contains($h,'آموزش نوشتاری مستقل')&&str_contains($h,'این تصاویر WinBox یا اجرای RouterOS نیستند'));
$ok(str_contains($h,'/lab/#static-routing-practice')&&!str_contains($h,'VideoObject')&&!str_contains($h,'youtube.com')&&!str_contains($h,'youtu.be'));
echo 'ILLUSTRATED_RENDERER=PASS checks='.$checks."\n";
