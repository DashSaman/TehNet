<?php
defined('ABSPATH') || exit;
$tn_logo = file_exists(get_theme_file_path('assets/img/tehnet-logo.jpg'));
?><!doctype html>
<html <?php language_attributes(); ?> dir="rtl" data-theme="dark">
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#080f18">
    <meta name="color-scheme" content="dark light">
    <script>(function(){document.documentElement.classList.add('tn-js');try{var t=localStorage.getItem('tn-theme');document.documentElement.dataset.theme=t==='light'?'light':'dark';}catch(e){document.documentElement.dataset.theme='dark';}})();</script>
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="tn-skip-link" href="#tn-main-content">رفتن به محتوای اصلی</a>
<header class="tn-site-header">
    <div class="tn-container tn-header-inner">
        <a class="tn-brand" href="<?php echo esc_url(home_url('/')); ?>">
            <?php if ($tn_logo) : ?>
                <img class="tn-brand-logo" src="<?php echo esc_url(get_theme_file_uri('assets/img/tehnet-logo.jpg')); ?>" alt="" width="48" height="48">
            <?php endif; ?>
            <span class="tn-brand-text">
                <span class="tn-brand-name"><?php bloginfo('name'); ?></span>
                <span class="tn-brand-tag">TehNet — Connecting Tehran</span>
            </span>
        </a>
        <nav id="tn-main-menu" class="tn-site-nav" aria-label="<?php esc_attr_e('منوی اصلی', 'tehnet'); ?>">
            <?php wp_nav_menu(['theme_location' => 'primary', 'container' => false, 'fallback_cb' => false]); ?>
        </nav>
        <div class="tn-header-actions">
            <button class="tn-theme-toggle tn-js-only" aria-pressed="false" type="button" aria-label="<?php esc_attr_e('تغییر حالت روشن/تیره', 'tehnet'); ?>">
                <svg class="tn-icon-moon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                <svg class="tn-icon-sun" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
            </button>
            <a class="tn-header-cta" href="<?php echo esc_url(home_url('/contact/')); ?>">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                <?php esc_html_e('تماس با ما', 'tehnet'); ?>
            </a>
<button class="tn-menu-toggle tn-js-only" type="button" aria-label="بازکردن منو" aria-expanded="false" aria-controls="tn-main-menu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>
        </div>
    </div>
</header>
<main id="tn-main-content" class="tn-main tn-container">
