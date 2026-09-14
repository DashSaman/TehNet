<?php
defined('ABSPATH') || exit;
?><!doctype html>
<html <?php language_attributes(); ?> dir="rtl">
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<header class="tn-site-header">
    <div class="tn-container tn-header-inner">
        <a class="tn-brand" href="<?php echo esc_url(home_url('/')); ?>">
            <?php bloginfo('name'); ?>
        </a>
        <nav class="tn-site-nav" aria-label="<?php esc_attr_e('منوی اصلی', 'tehnet'); ?>">
            <?php wp_nav_menu(['theme_location' => 'primary', 'container' => false, 'fallback_cb' => false]); ?>
        </nav>
    </div>
</header>
<main class="tn-main tn-container">
