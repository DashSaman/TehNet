<?php
/** TehNet editable Gutenberg patterns. */

defined('ABSPATH') || exit;

function tehnet_register_block_patterns(): void {
    if (! function_exists('register_block_pattern')) {
        return;
    }

    register_block_pattern_category('tehnet', [
        'label' => __('تهران نتورک', 'tehnet'),
    ]);

    register_block_pattern('tehnet/hero', [
        'title' => __('قهرمان صفحه تهران نتورک', 'tehnet'),
        'categories' => ['tehnet'],
        'content' => <<<'HTML'
<!-- wp:group {"align":"wide","className":"tn-card","layout":{"type":"constrained"}} -->
<div class="wp-block-group alignwide tn-card">
<!-- wp:paragraph --><p><strong>تهران نتورک | TehNet</strong></p><!-- /wp:paragraph -->
<!-- wp:heading {"level":1} --><h1 class="wp-block-heading">آموزش، اجرا و پشتیبانی حرفه‌ای شبکه</h1><!-- /wp:heading -->
<!-- wp:paragraph --><p>از آموزش‌های رایگان تا خدمات شبکه، لاب‌های عملی و تجهیزات؛ همه در یک مسیر فنی و قابل اعتماد.</p><!-- /wp:paragraph -->
<!-- wp:buttons --><div class="wp-block-buttons">
<!-- wp:button --><div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="/learn/">شروع آموزش</a></div><!-- /wp:button -->
<!-- wp:button {"className":"is-style-outline"} --><div class="wp-block-button is-style-outline"><a class="wp-block-button__link wp-element-button" href="/services/">درخواست خدمات</a></div><!-- /wp:button -->
</div><!-- /wp:buttons -->
</div><!-- /wp:group -->
HTML,
    ]);
    register_block_pattern('tehnet/journeys', [
        'title' => __('چهار مسیر تهران نتورک', 'tehnet'),
        'categories' => ['tehnet'],
        'content' => <<<'HTML'
<!-- wp:group {"align":"wide","layout":{"type":"constrained"}} -->
<div class="wp-block-group alignwide">
<!-- wp:heading {"textAlign":"center"} --><h2 class="wp-block-heading has-text-align-center">هر چیزی که برای شبکه لازم داری</h2><!-- /wp:heading -->
<!-- wp:columns --><div class="wp-block-columns">
<!-- wp:column --><div class="wp-block-column"><!-- wp:group {"className":"tn-card"} --><div class="wp-block-group tn-card"><!-- wp:heading {"level":3} --><h3 class="wp-block-heading">آموزش</h3><!-- /wp:heading --><!-- wp:paragraph --><p>آموزش‌های رایگان و کاربردی شبکه به زبان فارسی.</p><!-- /wp:paragraph --></div><!-- /wp:group --></div><!-- /wp:column -->
<!-- wp:column --><div class="wp-block-column"><!-- wp:group {"className":"tn-card"} --><div class="wp-block-group tn-card"><!-- wp:heading {"level":3} --><h3 class="wp-block-heading">Lab</h3><!-- /wp:heading --><!-- wp:paragraph --><p>اسکریپت، کانفیگ، فایل و تمرین عملی برای اجرای سریع‌تر.</p><!-- /wp:paragraph --></div><!-- /wp:group --></div><!-- /wp:column -->
<!-- wp:column --><div class="wp-block-column"><!-- wp:group {"className":"tn-card"} --><div class="wp-block-group tn-card"><!-- wp:heading {"level":3} --><h3 class="wp-block-heading">خدمات</h3><!-- /wp:heading --><!-- wp:paragraph --><p>خدمات حضوری تهران و پشتیبانی ریموت در سراسر ایران.</p><!-- /wp:paragraph --></div><!-- /wp:group --></div><!-- /wp:column -->
<!-- wp:column --><div class="wp-block-column"><!-- wp:group {"className":"tn-card"} --><div class="wp-block-group tn-card"><!-- wp:heading {"level":3} --><h3 class="wp-block-heading">فروشگاه</h3><!-- /wp:heading --><!-- wp:paragraph --><p>محصولات دیجیتال و تجهیزات شبکه با استعلام قیمت روز.</p><!-- /wp:paragraph --></div><!-- /wp:group --></div><!-- /wp:column -->
</div><!-- /wp:columns -->
</div><!-- /wp:group -->
HTML,
    ]);
    register_block_pattern('tehnet/contact-cta', [
        'title' => __('دعوت به تماس تهران نتورک', 'tehnet'),
        'categories' => ['tehnet'],
        'content' => <<<'HTML'
<!-- wp:group {"align":"wide","className":"tn-card","layout":{"type":"constrained"}} -->
<div class="wp-block-group alignwide tn-card">
<!-- wp:heading {"textAlign":"center"} --><h2 class="wp-block-heading has-text-align-center">برای اجرای شبکه یا رفع مشکل کمک می‌خواهی؟</h2><!-- /wp:heading -->
<!-- wp:paragraph {"align":"center"} --><p class="has-text-align-center">در تهران خدمات حضوری و در سراسر ایران پشتیبانی ریموت ارائه می‌کنیم.</p><!-- /wp:paragraph -->
<!-- wp:buttons {"layout":{"type":"flex","justifyContent":"center"}} --><div class="wp-block-buttons">
<!-- wp:button --><div class="wp-block-button"><a class="wp-block-button__link wp-element-button" href="/contact/">تماس با تهران نتورک</a></div><!-- /wp:button -->
</div><!-- /wp:buttons -->
</div><!-- /wp:group -->
HTML,
    ]);
}
add_action('init', 'tehnet_register_block_patterns');
