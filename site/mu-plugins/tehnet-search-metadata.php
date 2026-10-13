<?php
/**
 * Plugin Name: TehNet Search Metadata
 * Description: Bounded page descriptions, social metadata and truthful profile identity.
 * Version: 0.1.0
 * Requires PHP: 8.2
 *
 * Prepared as a one-file, removable MU-plugin because the live TehNet Core version
 * differs from its repository header. No theme/Core replacement is required.
 * Does NOT change indexability, canonicals, titles, robots, content or database state.
 */
declare(strict_types=1);
namespace TehNet\SearchMetadata;
defined('ABSPATH') || exit;

/** This character limit is an editorial bound, not a search-engine ranking rule. */
function clean(string $value, int $limit = 200): string {
    if ($limit < 1 || preg_match('//u', $value) !== 1) return '';
    $value = html_entity_decode($value, ENT_QUOTES | ENT_HTML5, 'UTF-8');
    $value = wp_strip_all_tags(strip_shortcodes($value));
    $value = trim((string) preg_replace('/[\s\x{00A0}]+/u', ' ', $value));
    preg_match_all('/./us', $value, $characters);
    if (count($characters[0]) <= $limit) return $value;
    $head = implode('', array_slice($characters[0], 0, max(0, $limit - 1)));
    return rtrim($head) . '…';
}

/** Avoid creating a competing metadata owner when a full SEO plugin takes over. */
function external_owner(): bool {
    $detected = defined('WPSEO_VERSION') || defined('RANK_MATH_VERSION')
        || defined('AIOSEO_VERSION') || defined('SEOPRESS_VERSION')
        || function_exists('the_seo_framework') || function_exists('tsf');
    return (bool) apply_filters('tehnet_search_metadata_external_owner', $detected);
}

/** Fallbacks describe existing page intent; explicit stored excerpts take priority. */
function descriptions(): array {
    return [
        '/' => 'تهران نتورک؛ آموزش عملی شبکه و میکروتیک، سناریوهای آزمایشگاهی، خدمات حضوری شبکه در تهران، پشتیبانی از راه دور و استعلام تجهیزات شبکه.',
        'about' => 'درباره تهران نتورک؛ آشنایی با فعالیت آموزشی و خدماتی TehNet در زمینه شبکه، لاب‌های عملی و پشتیبانی فنی.',
        'contact' => 'راه‌های ارتباط با تهران نتورک برای مشاوره خدمات شبکه، پشتیبانی از راه دور، استعلام تجهیزات و همکاری حرفه‌ای.',
        'learn' => 'بخش آموزش تهران نتورک؛ مسیر دسترسی به آموزش‌های شبکه و میکروتیک، دوره MTCNA و مطالب عملی مرتبط.',
        'lab' => 'بخش Lab تهران نتورک؛ دسترسی به مطالب عملی و سناریوهای آزمایشگاهی شبکه، از جمله تمرین میکروتیک با GNS3.',
        'services' => 'خدمات شبکه تهران نتورک؛ طراحی و راه‌اندازی شبکه، پیکربندی میکروتیک و پشتیبانی حضوری در تهران یا از راه دور در ایران.',
        'shop' => 'فروشگاه تجهیزات شبکه تهران نتورک؛ بررسی کاتالوگ و استعلام قیمت، موجودی و شرایط تأمین تجهیزات، بدون نمایش قیمت تأییدنشده.',
        'blog' => 'بلاگ تهران نتورک؛ فهرست نوشته‌های منتشرشده درباره فناوری و شبکه و دسترسی به بخش‌های آموزش و خدمات.',
        'learn/mikrotik' => 'آموزش میکروتیک در تهران نتورک؛ مسیر آشنایی با RouterOS، لاب، مسیریابی و فایروال همراه با دسترسی به دوره MTCNA.',
        'learn/mikrotik/mtcna' => 'مسیر آموزش MTCNA میکروتیک؛ ویدیوهای آموزشی، تمرین‌های GNS3 و مباحث RouterOS، IP، مسیریابی و فایروال در تهران نتورک.',
        'services/network-tehran' => 'خدمات حضوری شبکه در تهران؛ بررسی نیاز و محدوده کار، تنظیم و رفع مشکل زیرساخت شبکه برای کسب‌وکارها و مجموعه‌ها.',
        'services/network-support-tehran' => 'پشتیبانی شبکه تهران؛ بررسی قطعی، کندی و خطاهای دسترسی در شبکه موجود با تعیین محدوده عیب‌یابی و پشتیبانی.',
        'services/network-setup-tehran' => 'راه‌اندازی شبکه شرکت در تهران؛ بررسی کاربران، تجهیزات و سرویس‌ها پیش از طراحی، اجرا و توسعه زیرساخت شبکه.',
        'services/mikrotik-tehran' => 'خدمات میکروتیک تهران؛ بررسی و پیکربندی RouterOS، مسیریابی، NAT، DHCP و فایروال متناسب با نیاز شبکه.',
        'services/remote-support' => 'پشتیبانی شبکه از راه دور در ایران؛ بررسی امن تنظیمات، مسیریابی و دسترسی‌ها در مواردی که حضور فیزیکی لازم نیست.',
        'amirreza-golavar' => 'رزومه امیررضا گل‌آور؛ شبکه، زیرساخت، پشتیبانی فناوری اطلاعات و فعالیت آموزشی در تهران نتورک.',
    ];
}

/** An empty model deliberately emits nothing for unsupported/private contexts. */
function model(): array {
    if (is_admin() || is_feed() || is_404() || is_search() || is_preview()) return [];
    if (!is_front_page() && !is_home() && !is_page()) return [];
    $post = is_home() && !is_front_page()
        ? get_post((int) get_option('page_for_posts')) : get_queried_object();
    if (!$post instanceof \WP_Post || $post->post_type !== 'page'
        || $post->post_status !== 'publish' || $post->post_password !== '') return [];
    $path = is_front_page() ? '/' : trim((string) get_page_uri($post->ID), '/');
    if ($path === 'sample-page') return [];
    $fallbacks = descriptions();
    $description = clean((string) $post->post_excerpt);
    if ($description === '') $description = $fallbacks[$path] ?? '';
    if ($description === '') return [];
    $profile = $path === 'amirreza-golavar'
        && get_page_template_slug($post->ID) === 'page-portfolio.php';
    $legacy_profile_description = $profile
        && has_action('wp_head', 'tehnet_profile_description') !== false;
    // The legacy theme owns this exact profile description; do not duplicate it.
    if ($legacy_profile_description) $description = $fallbacks[$path];
    $url = get_permalink($post->ID);
    if (is_home() && !is_front_page() && (int) get_query_var('paged') > 1)
        $url = get_pagenum_link((int) get_query_var('paged'));
    if (!is_string($url) || $url === '') return [];
    $visible = wp_strip_all_tags((string) $post->post_content);
    return [
        'description' => $description, 'url' => $url,
        'title' => clean((string) wp_get_document_title(), 250),
        'site_name' => clean((string) get_bloginfo('name'), 120),
        'locale' => get_locale(), 'skip_description' => $legacy_profile_description,
        'person' => $profile && str_contains($visible, 'امیررضا')
            && str_contains($visible, 'گل‌آور'),
    ];
}

function render(): void {
    if (external_owner()) return;
    $data = model();
    if ($data === []) return;
    if (!$data['skip_description'])
        echo '<meta name="description" content="' . esc_attr($data['description']) . '">' . "\n";
    foreach (['type'=>'website', 'title'=>$data['title'], 'description'=>$data['description'],
        'url'=>$data['url'], 'site_name'=>$data['site_name'], 'locale'=>$data['locale']] as $key=>$value) {
        echo '<meta property="og:' . esc_attr($key) . '" content="' . esc_attr($value) . '">' . "\n";
    }
    if (!$data['person']) return;
    $schema = [
        '@context'=>'https://schema.org', '@type'=>'ProfilePage',
        '@id'=>$data['url'].'#profile', 'url'=>$data['url'],
        'name'=>$data['title'], 'inLanguage'=>'fa-IR',
        'mainEntity'=>[
            '@type'=>'Person', '@id'=>$data['url'].'#person',
            'name'=>'امیررضا گل‌آور', 'alternateName'=>'Amirreza Golavar',
            'url'=>$data['url'],
        ],
    ];
    $json = wp_json_encode($schema, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES
        | JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT);
    if (is_string($json)) echo '<script type="application/ld+json" class="tehnet-profile-schema">'.$json.'</script>'."\n";
}
add_action('wp_head', __NAMESPACE__ . '\\render', 12);
