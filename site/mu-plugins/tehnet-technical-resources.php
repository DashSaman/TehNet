<?php
/** Plugin Name: TehNet Technical Resources
 * Description: Local calculation tools and visible editorial attribution. No telemetry or router changes.
 * Version: 0.2.0
 */
declare(strict_types=1);
namespace TehNet\TechnicalResources;
defined('ABSPATH') || exit;
require_once __DIR__.'/tehnet-technical-resources/network-readiness.php';

function wireguard_mtu(int $path,int $outer_ip): int {
    if (!in_array($outer_ip,[4,6],true) || $path<($outer_ip===6?1280:576) || $path>9000)
        throw new \InvalidArgumentException('Invalid outer IP version or measured path MTU');
    return $path-($outer_ip===6?40:20)-8-32;
}
function estimator(): string {
    return '<section class="tn-technical-tool" data-tn-mtu><h2>محاسبهٔ MTU داخلی WireGuard</h2><p>MTU مسیر بیرونیِ قابل‌استفاده را وارد کنید؛ سربار IP بیرونی، UDP و پیام دادهٔ WireGuard از آن کم می‌شود. این ابزار به روتر وصل نمی‌شود.</p><div class="tn-tool-inputs"><label>MTU مسیر بیرونی <input data-tn-path-mtu type="number" min="576" max="9000" step="1" value="1500" inputmode="numeric"></label><label>نسخهٔ IP بیرونی <select data-tn-outer-ip><option value="4">IPv4</option><option value="6">IPv6</option></select></label><button type="button" data-tn-mtu-calculate>محاسبه</button></div><output data-tn-mtu-result role="status" aria-live="polite">برای مسیر ۱۵۰۰ و IPv4 بیرونی: MTU داخلی محاسباتی ۱۴۴۰ بایت.</output><p>فرمول: MTU مسیر − سربار IP بیرونی (۲۰ یا ۴۰) − UDP (۸) − سربار پیام داده (۳۲). مقدار محاسباتی باید با مسیر و سناریوی واقعی آزمایش شود؛ EoIP، VLAN داخلی، PPPoE و تونل‌های تو در تو را جدا بررسی کنید. این محاسبه نتیجهٔ تست شبکه یا توصیهٔ قطعی تنظیم روتر نیست.</p></section>';
}
function editorial_note(): string {
    $post=get_post();
    if (!$post || $post->post_status!=='publish') return '';
    return '<aside class="tn-editorial-note"><p>تهیه و انتشار: <a href="'.esc_url(home_url('/about/')).'">تهران نتورک</a> · آخرین ویرایش: <time datetime="'.esc_attr(get_post_modified_time('c',true,$post)).'">'.esc_html(get_the_modified_date('Y-m-d',$post)).'</time></p><p><a href="'.esc_url(home_url('/technical-methodology/')).'">روش منابع، آزمون و اصلاح محتوا</a> · تاریخ ویرایش، به‌تنهایی تأیید آزمایش روی تجهیزات شما نیست.</p></aside>';
}
add_shortcode('tn_wireguard_mtu',__NAMESPACE__.'\\estimator');
add_shortcode('tn_editorial_note',__NAMESPACE__.'\\editorial_note');
add_action('wp_enqueue_scripts',static function():void {
    wp_enqueue_style('tn-accessibility',content_url('/mu-plugins/tehnet-technical-resources/accessibility.css'),[],'0.1.1');
},20);
add_action('wp_enqueue_scripts',static function():void {
    $post=get_queried_object();
    if (!$post instanceof \WP_Post || !has_shortcode($post->post_content,'tn_wireguard_mtu')) return;
    wp_enqueue_style('tn-technical-tools',content_url('/mu-plugins/tehnet-technical-resources/technical-tools.css'),[],'0.1.0');
    wp_enqueue_script('tn-technical-tools',content_url('/mu-plugins/tehnet-technical-resources/technical-tools.js'),[],'0.1.0',true);
});
