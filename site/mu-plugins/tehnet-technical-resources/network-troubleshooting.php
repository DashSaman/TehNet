<?php
declare(strict_types=1);
namespace TehNet\TechnicalResources;
defined('ABSPATH') || exit;

/** Reviewed manual decision support. No input leaves the browser and no commands are run. */
function troubleshooting_rules(): array {
    return [
        'internet'=>[
            'title'=>'اینترنت قطع است',
            'test'=>'ابتدا وضعیت اتصال کابل یا Wi-Fi و سپس دسترسی به یک سرویس داخلیِ مجاز را روی همان دستگاه بررسی کنید. در Windows، اجرای بدون پارامتر ipconfig فقط برای دیدن وضعیت آدرس و Gateway است؛ خروجی کامل را اینجا وارد نکنید.',
            'why'=>'تفکیک شبکهٔ محلی از مسیر اینترنت، دامنهٔ بررسی را کوچک می‌کند؛ بازشدن یک سرویس داخلی، سلامت DNS یا اینترنت را اثبات نمی‌کند.',
            'question'=>'از بررسی اولیه چه می‌دانید؟',
            'observations'=>[
                'unknown'=>['هنوز بررسی نکرده‌ام','از وضعیت اتصال و یک سرویس داخلی شروع کنید؛ فعلاً مدرکی برای نسبت‌دادن اختلال به ISP یا روتر نداریم.'],
                'local-fails'=>['اتصال یا سرویس داخلی هم مشکل دارد','بررسی رابط دستگاه، آدرس‌دهی و مسیر محلی را به مسئول شبکه ارجاع دهید؛ علت می‌تواند بیش از یک بخش باشد.'],
                'local-works'=>['سرویس داخلی کار می‌کند، اینترنت نه','مسیر خروج، نام‌گشایی و وضعیت سرویس‌دهنده باید جدا بررسی شوند؛ این مشاهده به‌تنهایی خرابی NAT یا ISP را تأیید نمی‌کند.'],
            ],
            'source'=>'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig',
        ],
        'dns'=>[
            'title'=>'DNS یا بازشدن نام‌ها مشکل دارد',
            'test'=>'در Windows، با nslookup نامِ غیرحساس و مورد تأیید مسئول شبکه را از DNS تنظیم‌شده پرس‌وجو کنید؛ نام داخلی یا پاسخ کامل را ارسال نکنید. نتیجه را با دسترسی IP به مقصد مجاز مقایسه کنید، نه بازکردن تصادفی سایت HTTPS با IP.',
            'why'=>'پرس‌وجوی نام و دسترسی IP دو شاهد متفاوت‌اند. مرورگر ممکن است از DoH، proxy یا cache متفاوتی استفاده کند؛ خطای HTTPS با IP نیز آزمون معتبر DNS نیست.',
            'question'=>'نتیجهٔ پرس‌وجوی نام و دسترسی IP چیست؟',
            'observations'=>[
                'unknown'=>['هنوز مقایسه نکرده‌ام','نام مجاز، زمان و نوع خطا را بدون جزئیات حساس برای خود ثبت کنید؛ تشخیص هنوز باز است.'],
                'name-fails'=>['پرس‌وجوی نام خطا دارد؛ آزمون مجاز IP پاسخ دارد','مسیر resolver، DNS تنظیم‌شده و تفاوت برنامه‌ها نیاز به بررسی دارد؛ موفقیت یک Ping فقط همان پاسخ ICMP را نشان می‌دهد.'],
                'both-fail'=>['هم نام و هم آزمون IP مشکل دارند','پیش از تغییر DNS، آدرس‌دهی و مسیر دسترسی را هم بررسی کنید؛ صرف خطای نام، خرابی DNS را ثابت نمی‌کند.'],
            ],
            'source'=>'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/nslookup',
        ],
        'dhcp'=>[
            'title'=>'DHCP آدرس نمی‌دهد',
            'test'=>'وضعیت دریافت خودکار آدرس و آدرس فعلی رابط را فقط روی دستگاه خود ببینید؛ در Windows، ipconfig بدون پارامتر تنظیمات را نمایش می‌دهد. برای این بررسی نیازی به release، renew یا قطع رابط نیست.',
            'why'=>'وجود یا نبود آدرس مورد انتظار، نقطهٔ شروع بررسی lease و مسیر DHCP است. درخواست broadcast برای عبور از شبکهٔ مسیریابی‌شده معمولاً به relay مناسب نیاز دارد؛ IPv4 و IPv6 یکسان نیستند.',
            'question'=>'وضعیت آدرس دستگاه چیست؟',
            'observations'=>[
                'unknown'=>['هنوز وضعیت آدرس را نمی‌دانم','بدون انتشار IP یا MAC، فقط وجود آدرس مورد انتظار و دریافت خودکار را با مسئول شبکه بررسی کنید.'],
                'no-address'=>['آدرس مورد انتظار دریافت نشده','مسئول شبکه باید رابط/VLAN، ظرفیت و وضعیت lease سرور و در صورت نیاز relay را بررسی کند؛ این مشاهده به‌تنهایی خرابی سرور DHCP نیست.'],
                'has-address'=>['آدرس مورد انتظار وجود دارد','آدرس داشتن، درستی Gateway، DNS یا اعتبار lease را تضمین نمی‌کند؛ تنظیمات مورد انتظار و مسیر بعدی را جدا تطبیق دهید.'],
            ],
            'source'=>'https://manual.mikrotik.com/docs/network-management/dhcp/',
        ],
        'vpn'=>[
            'title'=>'VPN سازمانی وصل نمی‌شود',
            'test'=>'فقط نوع خطای نمایش‌داده‌شده و زمان آن را برای خود ثبت کنید: رد هویت، timeout یا اتصال بدون دسترسی سرویس. نام کاربری، رمز، کلید، فایل کانفیگ و آدرس endpoint لازم نیست.',
            'why'=>'برقراری تونل، احراز هویت و دسترسی سرویس پشت تونل، مرحله‌های جدا هستند؛ هر پروتکل و نسخه نیز رفتار خودش را دارد.',
            'question'=>'کدام وضعیت را دیده‌اید؟',
            'observations'=>[
                'unknown'=>['خطای مشخصی ندارم یا بررسی نشده','نوع VPN و مرحلهٔ توقف را از مسئول مجاز بپرسید؛ ابزار پروتکل یا علت خرابی را حدس نمی‌زند.'],
                'auth'=>['خطای احراز هویت دیده‌ام','از مسیر امنِ مسئول حساب، وضعیت مجوز و روش ورود بررسی شود؛ رمز را در فرم خدمات نفرستید و تلاش ورود را پشت‌سرهم تکرار نکنید.'],
                'timeout'=>['timeout یا قطع پیش از اتصال','دسترسی مسیر، endpoint و سیاست‌های مجاز به بررسی مسئول دو طرف نیاز دارند؛ فایروال را برای آزمون عمومی خاموش نکنید.'],
                'service'=>['تونل متصل است؛ سرویس پشت آن در دسترس نیست','مسیر رفت/برگشت، نام‌گشایی و مجوز همان سرویس جدا بررسی شوند؛ وضعیت connected به‌تنهایی مدرک سلامت سرویس نیست.'],
            ],
            'source'=>'https://manual.mikrotik.com/docs/cli-reference/interface/wireguard/peers/',
            'source_label'=>'نمونهٔ مستندات WireGuard؛ جایگزین مستند پروتکل VPN شما نیست',
        ],
        'vlan'=>[
            'title'=>'بین VLANها ارتباط نیست',
            'test'=>'با مجوز مسئول، وضعیت یک سرویس مشخص در همان VLAN و در VLAN مقصد را مقایسه کنید. مقصدها را در ابزار ننویسید و برای آزمون، عضویت پورت یا vlan-filtering را تغییر ندهید.',
            'why'=>'عبور لایهٔ۲، مسیریابی بین شبکه‌ها و سیاست دسترسی جدا هستند. موفقیت ارتباط داخل VLAN، عبور مجاز میان VLANها را تضمین نمی‌کند.',
            'question'=>'نتیجهٔ مقایسهٔ مجاز چیست؟',
            'observations'=>[
                'unknown'=>['هنوز مقایسه نکرده‌ام','ابتدا مقصد و کاربرد مجاز را با مسئول روشن کنید؛ مسدودبودن ارتباط ممکن است سیاست صحیح شبکه باشد.'],
                'same-only'=>['داخل VLAN کار می‌کند؛ بین VLANها نه','مسئول باید Gateway/مسیر برگشت و قواعد forward را همراه با tagging و دسترسی CPU بررسی کند؛ تغییر کور پورت یا فایروال لازم نیست.'],
                'same-fails'=>['داخل همان VLAN هم مشکل داریم','دامنهٔ بررسی را به رابط، عضویت پورت، tagging و آدرس‌دهی هم گسترش دهید؛ هنوز خرابی routing ثابت نشده است.'],
            ],
            'source'=>'https://manual.mikrotik.com/docs/bridging-and-switching/',
        ],
        'nat'=>[
            'title'=>'NAT یا دسترسی سرویس درست عمل نمی‌کند',
            'test'=>'مشخص کنید مسئله خروج کاربر به اینترنت است یا ورود به یک سرویس مجاز. مسئول شبکه می‌تواند مسیر و شمارندهٔ قانون مرتبط را بدون تغییر بخواند؛ خودتان قانون عمومی، port-forward یا پاک‌کردن connection tracking اجرا نکنید.',
            'why'=>'srcnat و dstnat کاربردهای متفاوت دارند. NAT جای مجوز فایروال نیست؛ RouterOS تصمیم NAT را برای اتصال دنبال می‌کند و مسیر برگشت نیز اهمیت دارد.',
            'question'=>'مشکل در کدام جهت است؟',
            'observations'=>[
                'unknown'=>['جهت یا شاهد کافی مشخص نیست','ابتدا کاربرد و جهت ارتباط مجاز را تعیین کنید؛ نام NAT در شرح مشکل، علت را ثابت نمی‌کند.'],
                'outbound'=>['خروج کاربر به سرویس بیرونی','مسیر خروج، قانون srcnat مرتبط و دسترسی سرویس جدا بررسی شوند؛ موفقیت خود روتر لزوماً موفقیت کاربران پشت آن نیست.'],
                'inbound'=>['ورود به یک سرویس مجاز از بیرون','مسیر تا سازمان، وضعیت آدرس‌دهی سرویس‌دهنده، dstnat، مجوز forward و مسیر برگشت باید با مسئول بررسی شوند؛ از داخل LAN نتیجهٔ دسترسی بیرونی را فرض نکنید.'],
            ],
            'source'=>'https://manual.mikrotik.com/docs/firewall-and-quality-of-service/firewall/nat/',
        ],
        'gateway'=>[
            'title'=>'Gateway پاسخ نمی‌دهد',
            'test'=>'ابتدا Gateway انتخاب‌شدهٔ همان رابط را فقط محلی ببینید. اگر مسئول اجازه داده، حداکثر چهار Echo Request به همان Gateway بفرستید؛ در Windows تعداد پیش‌فرض Ping چهار است. هیچ مقصد یا خروجی خامی در این ابزار وارد نمی‌شود.',
            'why'=>'عدم پاسخ ICMP ممکن است از سیاست یا محدودیت پاسخ‌گویی باشد؛ آن را با وضعیت رابط و دسترسی یک سرویس مجاز مقایسه کنید. پاسخ Ping نیز سلامت کل شبکه را ثابت نمی‌کند.',
            'question'=>'چه مشاهده‌ای دارید؟',
            'observations'=>[
                'unknown'=>['آزمون مجاز انجام نشده','Gateway مورد انتظار و وضعیت رابط را با مسئول تطبیق دهید؛ هنوز شاهدی برای خرابی روتر نیست.'],
                'no-ping'=>['Echo Reply ندارم؛ وضعیت سرویس روشن نیست','مسیر محلی و سیاست ICMP باید جدا بررسی شوند؛ نبود پاسخ، به‌تنهایی قطع Gateway نیست.'],
                'service-works'=>['Ping پاسخ ندارد ولی سرویس مجاز کار می‌کند','این دو شاهد را کنار هم ثبت کنید؛ مسیر سرویس فعال است و پاسخ ICMP ممکن است محدود باشد.'],
            ],
            'source'=>'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ping',
        ],
    ];
}

function troubleshooting_assistant(): string {
    $id=wp_unique_id('tn-triage-');$rules=troubleshooting_rules();
    $h='<section class="tn-triage" data-tn-triage aria-labelledby="'.esc_attr($id.'title').'"><p class="tn-triage-eyebrow">تصمیم‌یار دستی · قواعد نسخهٔ ۱</p><h2 id="'.esc_attr($id.'title').'">از نشانهٔ اختلال تا درخواست دقیق‌تر</h2><p>این ابزار اندازه‌گیری شبکه یا تشخیص قطعی نیست. فقط انتخاب‌های همین صفحه روی دستگاه شما پردازش می‌شوند؛ به روتر وصل نمی‌شود و فرمانی اجرا نمی‌کند. رمز، IP، MAC، نام داخلی و خروجی کانفیگ نمی‌خواهد.</p>';
    $h.='<p data-tn-triage-progress role="status" aria-live="polite">راهنمای دستی هفت مسئلهٔ شبکه</p><fieldset data-tn-triage-step="1"><legend>۱. کدام نشانه را دیده‌اید؟</legend><label for="'.esc_attr($id.'problem').'">نوع مسئله</label><select id="'.esc_attr($id.'problem').'" data-tn-triage-problem><option value="">یک مسئله را انتخاب کنید</option>';
    foreach($rules as$key=>$rule)$h.='<option value="'.esc_attr($key).'">'.esc_html($rule['title']).'</option>';
    $h.='</select></fieldset><fieldset data-tn-triage-step="2"><legend>۲. دامنهٔ مشاهده چقدر است؟</legend><p>فقط آنچه واقعاً دیده‌اید انتخاب کنید؛ محل، نام سازمان یا شناسهٔ دستگاه لازم نیست.</p><label for="'.esc_attr($id.'scope').'">افراد یا بخش‌های درگیر</label><select id="'.esc_attr($id.'scope').'" data-tn-triage-scope>';
    foreach(['unknown'=>'هنوز مشخص نیست','one'=>'یک دستگاه مشاهده شده','several'=>'چند دستگاه یا یک بخش','widespread'=>'چند بخش یا شعبه مشاهده شده']as$key=>$label)$h.='<option value="'.esc_attr($key).'">'.esc_html($label).'</option>';
    $h.='</select></fieldset><div data-tn-triage-step="3"><h3>۳. شاهد و بررسی بعدی</h3>';
    foreach($rules as$key=>$rule){
        $field=$id.$key;$h.='<article data-tn-triage-rule="'.esc_attr($key).'"><h4>'.esc_html($rule['title']).'</h4><p data-tn-triage-test>'.esc_html($rule['test']).'</p><p><strong>دلیل این بررسی: </strong><span data-tn-triage-why>'.esc_html($rule['why']).'</span></p><label for="'.esc_attr($field).'">'.esc_html($rule['question']).'</label><select id="'.esc_attr($field).'" data-tn-triage-observation>';
        foreach($rule['observations']as$value=>[$label,$advice])$h.='<option value="'.esc_attr($value).'" data-advice="'.esc_attr($advice).'">'.esc_html($label).'</option>';
        $h.='</select><p><a href="'.esc_url($rule['source']).'">'.esc_html($rule['source_label']??'منبع رسمیِ نکتهٔ فنی این مسیر').'</a></p></article>';
    }
    $h.='</div><div class="tn-triage-actions"><button type="button" data-tn-triage-back disabled hidden>مرحلهٔ قبل</button><button type="button" data-tn-triage-next disabled hidden>مرحلهٔ بعد</button><button type="button" data-tn-triage-build disabled hidden>ساخت خلاصهٔ دستی</button><button type="button" data-tn-triage-reset disabled hidden>شروع دوباره</button></div><div data-tn-triage-result hidden><h3>خلاصهٔ مشاهده، نه تشخیص نهایی</h3><p data-tn-triage-advice aria-live="polite"></p><label for="'.esc_attr($id.'summary').'">متن برای مرور و انتقال دستی به درخواست خدمات</label><textarea id="'.esc_attr($id.'summary').'" data-tn-triage-summary readonly rows="9"></textarea><button type="button" data-tn-triage-download disabled>دانلود JSON روی دستگاه</button><p>خلاصه به تیکت پیوست یا ارسال نشده است. در صورت تمایل، آن را پس از مرور در شرح درخواست موجود کپی کنید؛ نتیجهٔ واقعی تست‌ها را فقط در حد غیرحساس اضافه کنید.</p></div><noscript><p>JavaScript خاموش است؛ تمام راهنماها را می‌توانید بخوانید و مشاهدهٔ غیرحساس خود را دستی جمع‌بندی کنید. ساخت خلاصه و دانلود تعاملی فعال نیست.</p></noscript><p class="tn-triage-boundary">هیچ تغییر پیکربندی در این مسیر پیشنهاد نمی‌شود؛ تغییر عملیاتی فقط با مسئول مجاز، پشتیبان، دسترسی جایگزین و روش بازگشت است. مسائل تخصصی PBX و IVR در <a href="https://mytel.one/services/">خدمات مایتل</a> پیگیری می‌شوند.</p><p><a class="tn-button" href="'.esc_url(home_url('/services/?tn_service_context=network-support#service-request')).'">درخواست عیب‌یابی از مسیر فعلی خدمات</a></p></section>';
    return $h;
}
add_shortcode('tn_network_troubleshooting',__NAMESPACE__.'\\troubleshooting_assistant');
add_action('wp_enqueue_scripts',static function():void {
    $post=get_queried_object();
    if(!$post instanceof \WP_Post||!has_shortcode($post->post_content,'tn_network_troubleshooting'))return;
    wp_enqueue_style('tn-network-troubleshooting',content_url('/mu-plugins/tehnet-technical-resources/network-troubleshooting.css'),[],'0.1.0');
    wp_enqueue_script('tn-network-troubleshooting',content_url('/mu-plugins/tehnet-technical-resources/network-troubleshooting.js'),[],'0.1.0',true);
});
