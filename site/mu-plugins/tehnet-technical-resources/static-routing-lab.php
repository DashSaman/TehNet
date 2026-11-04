<?php
declare(strict_types=1);
namespace TehNet\TechnicalResources;
defined('ABSPATH') || exit;

function static_routing_lab(): string {
    $id=wp_unique_id('tn-route-lab-');
    $h='<section class="tn-routing-lab" data-tn-routing-lab aria-labelledby="'.esc_attr($id.'title').'"><p class="tn-routing-eyebrow">تمرین مفهومی · Static Routing</p><h2 id="'.esc_attr($id.'title').'">مسیر رفت را ساختم؛ چرا پاسخ برنمی‌گردد؟</h2><p>این تمرین یک مدل آموزشی محدود است؛ RouterOS، GNS3 یا شبیه‌ساز واقعی روتر نیست. بسته‌ای ارسال و کانفیگی اجرا نمی‌شود. مسیر رفت و برگشت را جدا در همین مدل بررسی کنید.</p>';
    $h.='<h3>۱. توپولوژی و فرض‌ها را بخوانید</h3><ol class="tn-routing-topology" data-tn-routing-topology dir="ltr">';
    $nodes=[
        'client'=>['رایانهٔ نمونه',['192.0.2.10/24','GW: 192.0.2.1']],
        'r1'=>['روتر R1',['LAN: 192.0.2.1/24','Transit: 203.0.113.1/30']],
        'r2'=>['روتر R2',['Transit: 203.0.113.2/30','LAN: 198.51.100.1/24']],
        'server'=>['سرویس نمونه',['198.51.100.10/24','GW: 198.51.100.1']],
    ];
    foreach($nodes as$key=>[$title,$lines]){
        $h.='<li data-tn-routing-node="'.esc_attr($key).'" dir="rtl"><svg viewBox="0 0 48 48" width="44" height="44" aria-hidden="true" focusable="false"><rect x="5" y="10" width="38" height="25" rx="6" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 20h24M12 26h10M20 35v5m8-5v5m-12 0h16" fill="none" stroke="currentColor" stroke-width="2"/></svg><h4>'.esc_html($title).'</h4>';
        foreach($lines as$line)$h.='<p><bdi dir="ltr">'.esc_html($line).'</bdi></p>';
        $h.='</li>';
    }
    $h.='</ol><p>آدرس‌ها از بلوک‌های مخصوص مستندسازی RFC5737 هستند؛ برای استفادهٔ عملیاتی یا ارسال بسته روی اینترنت نیستند. در مدل، لینک‌ها، ARP، میزبان‌ها و Gateway آن‌ها درست و مسیریابی فعال فرض شده‌اند؛ فقط مسیرهای متصل و انتخاب‌های زیر وجود دارند. default route، فایروال، NAT، IPv6، VRF، policy routing و ECMP مدل نمی‌شوند.</p><h3>۲. مسیر هر روتر را انتخاب کنید</h3>';
    foreach(['r1'=>'R1 برای رسیدن به شبکهٔ سرویس','r2'=>'R2 برای برگشت به شبکهٔ رایانه']as$key=>$label){
        $right=$key==='r1'?'198.51.100.0/24 → 203.0.113.2':'192.0.2.0/24 → 203.0.113.1';
        $wrong=$key==='r1'?'192.0.2.0/24 → 203.0.113.2':'198.51.100.0/24 → 203.0.113.1';
        $badGateway=$key==='r1'?'198.51.100.0/24 → 203.0.113.9':'192.0.2.0/24 → 203.0.113.9';
        $h.='<label for="'.esc_attr($id.$key).'">'.esc_html($label).'</label><select id="'.esc_attr($id.$key).'" data-tn-routing-choice="'.esc_attr($key).'"><option value="">هنوز انتخاب نکرده‌ام</option><option value="missing">هیچ مسیر static اضافه نشود</option><option value="wrong-network">'.esc_html($wrong).'</option><option value="wrong-gateway">'.esc_html($badGateway).'</option><option value="correct">'.esc_html($right).'</option></select>';
    }
    $h.='<label for="'.esc_attr($id.'direction').'">کدام جهت بسته را قدم‌به‌قدم ببینیم؟</label><select id="'.esc_attr($id.'direction').'" data-tn-routing-direction><option value="forward">رفت: رایانه به سرویس</option><option value="return">برگشت: سرویس به رایانه</option></select><div class="tn-routing-actions"><button type="button" data-tn-routing-check hidden disabled>بررسی پاسخ در مدل</button><button type="button" data-tn-routing-reset hidden disabled>شروع دوباره</button></div><h3>۳. نتیجه و حرکت مفهومی بسته</h3><output data-tn-routing-result role="status" aria-live="polite">بدون JavaScript، پاسخ آموزشی و توضیح مسیر را در بخش زیر بخوانید.</output><p data-tn-routing-step aria-live="polite"></p><div class="tn-routing-actions"><button type="button" data-tn-routing-prev hidden disabled>گام قبل بسته</button><button type="button" data-tn-routing-next hidden disabled>گام بعد بسته</button></div><details><summary>پاسخ آموزشی، کانفیگ نمونه و حدود مدل</summary><p>R1 باید مقصد شبکهٔ سرویس را به همسایهٔ مستقیم R2 بفرستد. R2 هم برای پاسخ، مسیر شبکهٔ رایانه را به R1 لازم دارد. مسیر یک جهت، شاهد وجود مسیر جهت دیگر نیست. prefix اشتباه، با نبود مسیر next-hop قابل دسترس متفاوت است.</p><p>نمایش آموزشی نحو RouterOS؛ این صفحه دستور اجرا نمی‌کند. آدرس‌ها فقط مثال مستندند و کد، کانفیگ آمادهٔ شبکهٔ شما نیست:</p><pre dir="ltr"><code># R1 — documentary example only
/ip route add dst-address=198.51.100.0/24 gateway=203.0.113.2
# R2 — documentary example only
/ip route add dst-address=192.0.2.0/24 gateway=203.0.113.1</code></pre><p>این مدل، نتیجهٔ Ping، زمان تأخیر، لاگ یا خروجی واقعی RouterOS تولید نمی‌کند. برای آزمایش واقعی، محیط جدا، طرح آدرس مجاز و مجوز تصویر سیستم‌عامل را خودتان آماده کنید؛ مدل حاضر، درست‌بودن تجهیزات یا شبکهٔ عملیاتی را تأیید نمی‌کند.</p></details><noscript><p>JavaScript خاموش است؛ حرکت بسته و اعتبارسنجی انتخاب فعال نیست. توپولوژی، فرض‌ها، پاسخ و نمونهٔ آموزشی قابل خواندن‌اند.</p></noscript><p><a href="'.esc_url(home_url('/learn/mikrotik/mtcna/static-routing/')).'">توضیح نوشتاری مستقل Static Routing</a> · <a href="'.esc_url(home_url('/lab/gns3-mikrotik/')).'">آماده‌سازی محیط تمرین GNS3</a></p><p>منابعِ اصول مدل: <a href="https://manual.mikrotik.com/docs/user-guides/routing-and-networking-protocols/routing-decision/">MikroTik: مقصد، مسیر متصل و next-hop</a> و <a href="https://www.rfc-editor.org/rfc/rfc5737.html">RFC5737: آدرس‌های مستندسازی</a>. این مدل توسط این منابع یا سازنده تأیید یا گواهی نشده است.</p></section>';
    return $h;
}
add_shortcode('tn_static_routing_lab',__NAMESPACE__.'\\static_routing_lab');
add_action('wp_enqueue_scripts',static function():void {
    $post=get_queried_object();
    if(!$post instanceof \WP_Post||!has_shortcode($post->post_content,'tn_static_routing_lab'))return;
    wp_enqueue_style('tn-static-routing-lab',content_url('/mu-plugins/tehnet-technical-resources/static-routing-lab.css'),[],'0.1.0');
    wp_enqueue_script('tn-static-routing-lab',content_url('/mu-plugins/tehnet-technical-resources/static-routing-lab.js'),[],'0.1.0',true);
});
