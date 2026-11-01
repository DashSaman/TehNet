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
    $classes[] = 'tn-visual';
    return $classes;
}
add_filter('body_class', 'tehnet_body_classes');

// Approved presentation layer. Existing TehNet Core and commerce stay unchanged.
function tehnet_visual_assets(): void {
    $css = 'assets/css/visual-refresh.css';
    $js = 'assets/js/visual-refresh.js';
    wp_enqueue_style('tehnet-visual-refresh', get_theme_file_uri($css), ['tehnet-style'], (string) filemtime(get_theme_file_path($css)));
    wp_enqueue_script('tehnet-visual-refresh', get_theme_file_uri($js), [], (string) filemtime(get_theme_file_path($js)), true);
}
add_action('wp_enqueue_scripts', 'tehnet_visual_assets', 20);
function tehnet_service_catalog_assets(): void {
    if (!is_front_page() && !is_page(['services','support']) && !has_shortcode((string)get_post_field('post_content',get_queried_object_id()),'tn_service_request')) return;
    $css='assets/css/service-catalog.css';
    wp_enqueue_style('tehnet-service-catalog',get_theme_file_uri($css),['tehnet-visual-refresh'],(string)filemtime(get_theme_file_path($css)));
}
add_action('wp_enqueue_scripts','tehnet_service_catalog_assets',21);
function tehnet_corporate_assets(): void {
    $css='assets/css/corporate.css';
    wp_enqueue_style('tehnet-corporate',get_theme_file_uri($css),['tehnet-visual-refresh'],(string)filemtime(get_theme_file_path($css)));
}
add_action('wp_enqueue_scripts','tehnet_corporate_assets',22);
function tehnet_visual_controls(): void {
    echo '<button class="tn-motion-toggle tn-js-only" id="tn-motion-toggle" type="button" aria-pressed="false">توقف حرکت‌های گرافیکی</button>';
}
add_action('wp_footer', 'tehnet_visual_controls', 5);
function tehnet_profile_description(): void {
    if (is_page_template('page-portfolio.php')) {
        echo '<meta name="description" content="رزومه امیررضا گل‌آور؛ شبکه، زیرساخت، پشتیبانی فناوری اطلاعات و فعالیت آموزشی در تهران نتورک.">';
    }
}
add_action('wp_head', 'tehnet_profile_description', 5);

function tehnet_blog_canonical(): void {
    if (!is_home() || is_front_page()) return;
    $page_id = (int)get_option('page_for_posts');
    if (!$page_id) return;
    $paged = max(1, (int)get_query_var('paged'));
    $url = $paged > 1 ? get_pagenum_link($paged) : get_permalink($page_id);
    if ($url) echo '<link rel="canonical" href="' . esc_url($url) . '">';
}
add_action('wp_head', 'tehnet_blog_canonical', 5);
