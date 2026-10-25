"""Fix the pre-existing blog archive metadata issue found by live HTTP regression."""
from pathlib import Path
R=Path(__file__).resolve().parents[2];T=R/'site/themes/tehnet'
p=T/'index.php';s=p.read_text()
s=s.replace('get_header();','''get_header();
$tn_blog_archive = is_home() && ! is_front_page();
if ($tn_blog_archive) {
    echo '<header class="tn-section"><p class="tn-kicker">یادگیری، تجربه و فناوری</p><h1>بلاگ تهران نتورک</h1></header>';
}
''',1)
s=s.replace("<h1><?php esc_html_e('محتوایی پیدا نشد', 'tehnet'); ?></h1>","<?php if ($tn_blog_archive) : ?><p><?php esc_html_e('هنوز نوشته‌ای منتشر نشده است.', 'tehnet'); ?></p><?php else : ?><h1><?php esc_html_e('محتوایی پیدا نشد', 'tehnet'); ?></h1><?php endif; ?>")
p.write_text(s)
p=T/'functions.php';s=p.read_text();s+='''
function tehnet_blog_canonical(): void {
    if (!is_home() || is_front_page()) return;
    $page_id = (int)get_option('page_for_posts');
    if (!$page_id) return;
    $paged = max(1, (int)get_query_var('paged'));
    $url = $paged > 1 ? get_pagenum_link($paged) : get_permalink($page_id);
    if ($url) echo '<link rel="canonical" href="' . esc_url($url) . '">';
}
add_action('wp_head', 'tehnet_blog_canonical', 5);
''';p.write_text(s)
p=T/'style.css';p.write_text(p.read_text().replace('Version: 0.5.0','Version: 0.5.1',1))
print('Blog archive H1 and self-canonical repaired; indexing policy unchanged.')
