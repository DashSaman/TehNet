<?php
defined('ABSPATH') || exit;
$tn_logo = file_exists(get_theme_file_path('assets/img/tehnet-logo.jpg'));
?><!doctype html>
<html <?php language_attributes(); ?> dir="rtl">
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script>(function(){try{var t=localStorage.getItem('tn-theme');if(t!=='dark'&&t!=='light'){t=window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';}document.documentElement.setAttribute('data-theme',t);}catch(e){document.documentElement.setAttribute('data-theme','light');}})();</script>
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<header class="tn-site-header">
    <div class="tn-container tn-header-inner">
        <a class="tn-brand" href="<?php echo esc_url(home_url('/')); ?>" aria-label="<?php echo esc_attr(get_bloginfo('name')); ?>">
            <?php if ($tn_logo) : ?>
                <img class="tn-brand-logo" src="<?php echo esc_url(get_theme_file_uri('assets/img/tehnet-logo.jpg')); ?>" alt="<?php echo esc_attr(get_bloginfo('name')); ?>" width="48" height="48">
            <?php endif; ?>
            <span class="tn-brand-text">
                <span class="tn-brand-name"><?php bloginfo('name'); ?></span>
                <span class="tn-brand-tag">TehNet — Connecting Tehran</span>
            </span>
        </a>
        <nav class="tn-site-nav" aria-label="<?php esc_attr_e('منوی اصلی', 'tehnet'); ?>">
            <?php wp_nav_menu(['theme_location' => 'primary', 'container' => false, 'fallback_cb' => false]); ?>
        </nav>
        <div class="tn-header-actions">
            <button class="tn-theme-toggle" type="button" aria-label="<?php esc_attr_e('تغییر حالت روشن/تیره', 'tehnet'); ?>" onclick="var d=document.documentElement,n=d.getAttribute('data-theme')==='dark'?'light':'dark';d.setAttribute('data-theme',n);try{localStorage.setItem('tn-theme',n)}catch(e){}">
                <svg class="tn-icon-moon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
                <svg class="tn-icon-sun" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
            </button>
            <a class="tn-header-cta" href="<?php echo esc_url(home_url('/contact/')); ?>">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                <?php esc_html_e('تماس با ما', 'tehnet'); ?>
            </a>
        </div>
    </div>
</header>
<main class="tn-main tn-container">
