<?php
/**
 * Plugin Name: TehNet Search Metadata
 * Description: Bounded page descriptions, social metadata and truthful profile identity.
 * Version: 0.2.2
 * Requires PHP: 8.2
 *
 * Isolated metadata owner; the existing Core owns LocalBusiness and Woo archives.
 * Does not change indexability, titles, robots, content or database state.
 * Supplies only the otherwise missing blog-category/tag archive canonical.
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
    $taxonomy = (function_exists('is_category') && is_category())
        || (function_exists('is_tag') && is_tag())
        || (function_exists('is_tax') && is_tax('product_cat'));
    $singular = function_exists('is_singular') && is_singular(['page','post','product']);
    $shop = function_exists('is_shop') && is_shop();
    if (!is_front_page() && !is_home() && !is_page() && !$singular && !$taxonomy && !$shop) return [];
    $post = $shop ? get_post((int)wc_get_page_id('shop')) : (is_home() && !is_front_page()
        ? get_post((int) get_option('page_for_posts')) : get_queried_object());
    if ($taxonomy && is_a($post, 'WP_Term')) {
        $url = get_term_link($post);
        if (is_wp_error($url) || !is_string($url)) return [];
        if ((int)get_query_var('paged') > 1) $url = get_pagenum_link((int)get_query_var('paged'));
        $description = clean((string)$post->description);
        if ($description === '') $description = clean('مطالب و کالاهای دستهٔ '.$post->name.' در تهران نتورک؛ برای بررسی جزئیات، صفحهٔ هر مورد را ببینید.');
        return ['description'=>$description,'url'=>$url,'title'=>clean(wp_get_document_title(),250),'site_name'=>clean(get_bloginfo('name'),120),'locale'=>get_locale(),'skip_description'=>false,'person'=>false,'image'=>social_image(0),'article'=>null,
            'canonical'=>in_array($post->taxonomy,['category','post_tag'],true) ? $url : null];
    }
    if (!$post instanceof \WP_Post || !in_array($post->post_type,['page','post','product'],true)
        || ($post->post_type !== 'page' && !$singular)
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
    if ((is_home() || $shop) && !is_front_page() && (int) get_query_var('paged') > 1)
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
        'image'=>social_image($post->ID), 'canonical'=>null,
        'article'=>editorial_schema($post,$url),
    ];
}

/** Native featured images are editable. A local brand poster is the fallback. */
function social_image(int $id): array {
    if ($id && function_exists('get_post_thumbnail_id')) {
        $aid=(int)get_post_thumbnail_id($id);
        $image=$aid ? wp_get_attachment_image_src($aid,'full') : false;
        if ($image && str_starts_with($image[0],home_url('/'))) return [$image[0],(int)$image[1],(int)$image[2]];
    }
    if (function_exists('get_theme_file_path') && is_file(get_theme_file_path('assets/img/tehnet-og.png')))
        return [get_theme_file_uri('assets/img/tehnet-og.png'),1200,630];
    return [];
}

/** Only opted-in, visibly attributed articles. No invented review or test claims. */
function editorial_schema(\WP_Post $post,string $url): ?array {
    if (!function_exists('has_shortcode') || !has_shortcode($post->post_content,'tn_editorial_note')) return null;
    // Attribution also belongs on service pages and collections; it does not change their role.
    if ($post->post_type === 'page') {
        $uri = trim((string)get_page_uri($post->ID), '/');
        if ($uri === 'services' || str_starts_with($uri, 'services/') || in_array($uri, ['learn','lab','learn/mikrotik','learn/mikrotik/mtcna'], true)) return null;
    }
    if (!function_exists('get_post_time') || !function_exists('get_post_modified_time')) return null;
    return ['@context'=>'https://schema.org','@type'=>'Article','@id'=>$url.'#article','mainEntityOfPage'=>$url,
        'headline'=>clean(get_the_title($post),250),'inLanguage'=>'fa-IR',
        'datePublished'=>get_post_time('c',true,$post),'dateModified'=>get_post_modified_time('c',true,$post),
        'author'=>['@type'=>'Organization','name'=>'تهران نتورک','url'=>home_url('/about/')],
        'publisher'=>['@id'=>home_url('/#localbusiness')]];
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
    if (!empty($data['canonical'])) echo '<link rel="canonical" href="'.esc_url($data['canonical']).'">'."\n";
    if (!empty($data['image'])) {
        foreach (['image'=>$data['image'][0],'image:width'=>$data['image'][1],'image:height'=>$data['image'][2],
            'image:alt'=>$data['title']]as $key=>$value)
            echo '<meta property="og:'.esc_attr($key).'" content="'.esc_attr((string)$value).'">'."\n";
        echo '<meta name="twitter:card" content="summary_large_image">'."\n";
    }
    if (!empty($data['article'])) echo '<script type="application/ld+json" class="tehnet-article-schema">'.wp_json_encode($data['article'],JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_HEX_TAG|JSON_HEX_AMP|JSON_HEX_APOS|JSON_HEX_QUOT).'</script>'."\n";
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
