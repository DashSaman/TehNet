<?php
declare(strict_types=1);
namespace TehNet\TechnicalResources;
defined('ABSPATH') || exit;

function readiness_questions(): array {
    return [
        'path'=>['نقشهٔ مسیر تماس','مسیر تلفن تا سوئیچ، روتر، ارتباط شعب و سرویس‌دهنده مشخص است؛ مسئول هر بخش و محل گلوگاه ثبت شده است.'],
        'vlan'=>['VLAN و دسترسی','تفکیک ترافیک صوت، پورت تلفن/رایانه، DHCP، DNS و دسترسی لازم بررسی شده‌اند؛ تفکیک VLAN به‌تنهایی امنیت یا کیفیت تماس را تضمین نمی‌کند.'],
        'power'=>['PoE و برق پشتیبان','بودجهٔ توان هم‌زمان سوئیچ، نیاز مدل تلفن‌ها و زمان پشتیبانی برق بررسی شده‌اند؛ تعداد پورت به‌تنهایی کافی نیست.'],
        'qos'=>['QoS در گلوگاه','محل اعتماد به علامت‌گذاری و صف خروجی مشخص است و رفتار ترافیک صوت زیر بار واقعی بررسی شده؛ همهٔ ترافیک با اولویت صوت علامت‌گذاری نمی‌شود.'],
        'wan'=>['کیفیت مسیر در ساعت شلوغ','تأخیر، تغییر تأخیر و اتلاف بسته با زمان، مسیر، ابزار و شرایط بار ثبت شده‌اند؛ یک Speedtest یا Ping کوتاه مدرک کامل کیفیت تماس نیست.'],
        'firewall'=>['فایروال و مسیر برگشت','نیازهای مجاز SIP/RTP طبق مستند همان PBX/اپراتور بررسی شده‌اند؛ بازکردن عمومی همهٔ پورت‌ها یا تغییر کورکورانهٔ SIP ALG روش ارزیابی نیست.'],
        'monitoring'=>['پایش و زمان مشترک','تجهیزات زمان هماهنگ دارند؛ بازهٔ رخداد، خطاهای پورت، مصرف لینک و دادهٔ مجاز کیفیت تماس قابل تطبیق است؛ دادهٔ مشترک از اطلاعات مشتری پاک شده است.'],
        'recovery'=>['تغییر و بازگشت','نسخهٔ پشتیبان تنظیمات، دسترسی جایگزین، پنجرهٔ تغییر، آزمون پس از تغییر و مسئول بازگشت مشخص‌اند.'],
    ];
}

function readiness_checklist(): string {
    $id=wp_unique_id('tn-readiness-');
    $html='<section class="tn-readiness" data-tn-readiness aria-labelledby="'.esc_attr($id.'title').'">';
    $html.='<h2 id="'.esc_attr($id.'title').'">چک‌لیست آمادگی شبکه برای VoIP</h2><p>این فهرست ارزیابی دستی است؛ اندازه‌گیری شبکه نیست و تأیید آماده‌بودن یا تضمین کیفیت تماس نمی‌دهد. وضعیت هر مورد را بر اساس مدرک خودتان انتخاب کنید.</p><div class="tn-readiness-grid">';
    foreach(readiness_questions()as$key=>[$label,$help]){
        $field=$id.$key;$description=$field.'-help';
        $html.='<fieldset data-tn-readiness-item data-key="'.esc_attr($key).'"><legend>'.esc_html($label).'</legend><p id="'.esc_attr($description).'">'.esc_html($help).'</p>';
        $html.='<label for="'.esc_attr($field).'">وضعیت بررسی «'.esc_html($label).'»</label><select id="'.esc_attr($field).'" data-tn-readiness-select aria-describedby="'.esc_attr($description).'">';
        foreach(['unknown'=>'هنوز بررسی نشده','ready'=>'مدرک بررسی موجود است','issue'=>'نیاز به اصلاح دارد','na'=>'در این سناریو کاربرد ندارد']as$value=>$text)$html.='<option value="'.esc_attr($value).'">'.esc_html($text).'</option>';
        $html.='</select></fieldset>';
    }
    $html.='</div><output data-tn-readiness-summary aria-live="polite">۸ مورد هنوز بررسی نشده است.</output><p class="tn-readiness-hint">با انتخاب وضعیت‌ها، خلاصه همین‌جا تغییر می‌کند. دانلود گزارش فقط روی دستگاه شما انجام می‌شود؛ چیزی برای تهران نتورک یا MyTel ارسال نمی‌شود.</p>';
    $html.='<div class="tn-readiness-actions"><button type="button" data-tn-readiness-export disabled>دانلود گزارش دستی</button><button type="button" data-tn-readiness-reset disabled>پاک‌کردن انتخاب‌ها</button></div><pre data-tn-readiness-report hidden tabindex="0" aria-label="متن گزارش دستی"></pre><noscript><p>برای استفاده از این چک‌لیست نیازی به JavaScript نیست: پرسش‌ها را بخوانید و وضعیت‌ها را روی کاغذ ثبت کنید. خلاصه و دانلود خودکار به JavaScript نیاز دارند.</p></noscript></section>';
    return $html;
}

add_shortcode('tn_voice_network_readiness',__NAMESPACE__.'\\readiness_checklist');
add_action('wp_enqueue_scripts',static function():void {
    $post=get_queried_object();
    if(!$post instanceof \WP_Post||!has_shortcode($post->post_content,'tn_voice_network_readiness'))return;
    wp_enqueue_style('tn-network-readiness',content_url('/mu-plugins/tehnet-technical-resources/network-readiness.css'),[],'0.2.0');
    wp_enqueue_script('tn-network-readiness',content_url('/mu-plugins/tehnet-technical-resources/network-readiness.js'),[],'0.2.0',true);
});
