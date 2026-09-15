<?php
/**
 * TehNet theme bootstrap.
 * Presentation only; business logic belongs in tehnet-core.
 */

defined('ABSPATH') || exit;

require_once get_template_directory() . '/inc/block-patterns.php';

function tehnet_theme_setup(): void {
    load_theme_textdomain('tehnet', get_template_directory() . '/languages');
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('responsive-embeds');
    add_theme_support('align-wide');
    add_theme_support('woocommerce');
    add_theme_support('html5', [
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
        'style',
        'script',
    ]);
    register_nav_menus([
        'primary' => __('منوی اصلی', 'tehnet'),
        'footer'  => __('منوی فوتر', 'tehnet'),
    ]);
}
add_action('after_setup_theme', 'tehnet_theme_setup');

function tehnet_enqueue_assets(): void {
    wp_enqueue_style(
        'tehnet-style',
        get_stylesheet_uri(),
        [],
        wp_get_theme()->get('Version')
    );
}
add_action('wp_enqueue_scripts', 'tehnet_enqueue_assets');

function tehnet_body_classes(array $classes): array {
    $classes[] = 'tehnet-rtl';
    return $classes;
}
add_filter('body_class', 'tehnet_body_classes');
