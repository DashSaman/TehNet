"""Prepare only TehNet presentation files in the isolated checkout; never deploy."""
from pathlib import Path
import re,json,html
ROOT=Path(__file__).resolve().parents[2];T=ROOT/'site/themes/tehnet'
svg=(T/'assets/img/network-art.svg').read_text()
figure='<figure class="tn-home-network"><div class="tn-art-label"><span>TEHNET / DIGITAL CONNECTIONS</span><b>✳</b></div>'+svg+'<figcaption><span>زیرساختی برای ارتباط، تجربه و یادگیری</span><span>گرافیک مفهومی شبکه</span></figcaption></figure>'
home=(ROOT/'content/pages/home.html').read_text()
assert 'tn-topology' in home, 'Run once on the captured live baseline.'
home=re.sub(r'<!-- wp:html --><svg class="tn-topology".*?</svg><!-- /wp:html -->','<!-- wp:html -->'+figure+'<!-- /wp:html -->',home,count=1,flags=re.S)
home=home.replace('زیرساخت شبکهٔ سازمان شما؛ از طراحی تا پشتیبانی','زیرساخت شبکهٔ شما؛<br><em>از طراحی تا پشتیبانی</em>',1)
stats='<div class="tn-stats"><div class="tn-stat"><b>آموزش عملی</b><span>یادگیری به زبان فارسی</span></div><div class="tn-stat"><b>سناریوهای شبکه</b><span>تمرین در محیط آزمایشگاهی</span></div><div class="tn-stat"><b>خدمات حضوری</b><span>ویژه تهران</span></div><div class="tn-stat"><b>پشتیبانی ریموت</b><span>در سراسر ایران</span></div></div>'
home=re.sub(r'<!-- wp:html --><div class="tn-stats">.*?</div><!-- /wp:html -->','<!-- wp:html -->'+stats+'<!-- /wp:html -->',home,count=1,flags=re.S)
founder='''<!-- wp:html -->
<section class="tn-founder-panel" aria-labelledby="tn-founder-title"><div class="tn-founder-monogram" aria-hidden="true">AG</div><div><p class="tn-kicker">آدم‌ها پشت فناوری</p><h2 id="tn-founder-title">امیررضا گل‌آور</h2><p>کارشناس شبکه و پشتیبانی فناوری اطلاعات؛ صاحب برند تهران نتورک. آموزش کاربردی، تجربه عملی و خدمات فنی را در یک مسیر دنبال می‌کنم.</p></div><a class="tn-v-button tn-v-outline" href="/amirreza-golavar/">آشنایی با من و رزومه ←</a></section>
<!-- /wp:html -->
'''
home=home.replace('<!-- wp:group {"align":"wide","className":"tn-card tn-cta"',founder+'\n<!-- wp:group {"align":"wide","className":"tn-card tn-cta"',1)
home=home.replace('روتر، سوییچ، فایروال و تانل','روتر، سوئیچ، فایروال و تونل')
(ROOT/'content/pages/home.html').write_text(home)
header=(T/'header.php').read_text()
header=header.replace('dir="rtl">','dir="rtl" data-theme="dark">',1)
boot="<script>(function(){document.documentElement.classList.add('tn-js');try{var t=localStorage.getItem('tn-theme');document.documentElement.dataset.theme=t==='light'?'light':'dark';}catch(e){document.documentElement.dataset.theme='dark';}})();</script>"
header=re.sub(r'<script>.*?</script>',boot,header,count=1,flags=re.S)
header=header.replace('<meta name="viewport" content="width=device-width, initial-scale=1">','<meta name="viewport" content="width=device-width, initial-scale=1">\n    <meta name="theme-color" content="#080f18">\n    <meta name="color-scheme" content="dark light">')
header=header.replace('<?php wp_body_open(); ?>','<?php wp_body_open(); ?>\n<a class="tn-skip-link" href="#tn-main-content">رفتن به محتوای اصلی</a>')
header=header.replace('<nav class="tn-site-nav"','<nav id="tn-main-menu" class="tn-site-nav"',1)
header=re.sub(r' onclick="[^"]*"','',header)
header=header.replace('class="tn-theme-toggle"','class="tn-theme-toggle tn-js-only" aria-pressed="false"',1)
button='<button class="tn-menu-toggle tn-js-only" type="button" aria-label="بازکردن منو" aria-expanded="false" aria-controls="tn-main-menu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>'
header=header.replace('        </div>\n    </div>\n</header>',button+'\n        </div>\n    </div>\n</header>',1)
header=header.replace('<main class="tn-main tn-container">','<main id="tn-main-content" class="tn-main tn-container">')
(T/'header.php').write_text(header)
functions=(T/'functions.php').read_text()
functions=functions.replace("$classes[] = 'tehnet-rtl';","$classes[] = 'tehnet-rtl';\n    $classes[] = 'tn-visual';")
functions+='''
// Approved presentation layer. Existing TehNet Core and commerce stay unchanged.
function tehnet_visual_assets(): void {
    $css = 'assets/css/visual-refresh.css';
    $js = 'assets/js/visual-refresh.js';
    wp_enqueue_style('tehnet-visual-refresh', get_theme_file_uri($css), ['tehnet-style'], (string) filemtime(get_theme_file_path($css)));
    wp_enqueue_script('tehnet-visual-refresh', get_theme_file_uri($js), [], (string) filemtime(get_theme_file_path($js)), true);
}
add_action('wp_enqueue_scripts', 'tehnet_visual_assets', 20);
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
'''
(T/'functions.php').write_text(functions)
style=(T/'style.css').read_text().replace('Version: 0.4.1','Version: 0.5.0',1)
(T/'style.css').write_text(style)
footer=(T/'footer.php').read_text()
needle='<li><a href="<?php echo esc_url(home_url(\'/about/\')); ?>">درباره ما</a></li>'
assert needle in footer
footer=footer.replace(needle,needle+'\n                <li><a href="<?php echo esc_url(home_url(\'/amirreza-golavar/\')); ?>">رزومه امیررضا گل‌آور</a></li>')
(T/'footer.php').write_text(footer)
(T/'page-portfolio.php').write_text('''<?php
/** Template Name: رزومه حرفه‌ای — TehNet */
defined('ABSPATH') || exit;
get_header();
while (have_posts()) {
    the_post();
    echo '<article class="tn-profile">';
    the_content();
    echo '</article>';
}
?>
</main>
<footer class="tn-container tn-profile-foot"><span>امیررضا گل‌آور | شبکه، زیرساخت و آموزش</span><a href="<?php echo esc_url(home_url('/')); ?>">بازگشت به تهران نتورک ←</a></footer>
<?php wp_footer(); ?>
</body></html>
''')
print('Prepared homepage, header, footer, assets wiring and native profile template.')
