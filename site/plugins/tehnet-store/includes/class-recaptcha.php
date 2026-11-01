<?php
defined('ABSPATH') || exit;

/** Optional Google v2 adapter for existing intake handlers; secrets stay in private configuration. */
final class TehNet_Store_Recaptcha {
    private static function config(): array {
        return [
            'enabled'=>defined('TN_RECAPTCHA_ENABLED')?TN_RECAPTCHA_ENABLED===true:get_option('tn_recaptcha_enabled','no')==='yes',
            'site'=>defined('TN_RECAPTCHA_SITE_KEY')?(string)TN_RECAPTCHA_SITE_KEY:(string)get_option('tn_recaptcha_site_key',''),
            'secret'=>defined('TN_RECAPTCHA_SECRET_KEY')?(string)TN_RECAPTCHA_SECRET_KEY:(string)get_option('tn_recaptcha_secret_key',''),
        ];
    }

    public static function render(): string {
        $c=self::config();
        if(!$c['enabled'])return '';
        if($c['site']===''||$c['secret']==='')return '<p role="alert">بررسی ضداسپم فعلاً در دسترس نیست. برای ثبت نیاز با ما تماس بگیرید.</p>';
        wp_enqueue_script('tn-recaptcha',plugins_url('../assets/recaptcha.js',__FILE__),[],(string)filemtime(__DIR__.'/../assets/recaptcha.js'),true);
        return '<div class="tn-captcha"><div class="tn-captcha-widget" data-tn-recaptcha="'.esc_attr($c['site']).'"></div><p class="tn-captcha-status" role="status" aria-live="polite">برای ثبت درخواست، بررسی ضداسپم Google را تکمیل کنید.</p><noscript>بررسی ضداسپم به JavaScript نیاز دارد. برای ثبت نیاز از <a href="'.esc_url(home_url('/contact/')).'">راه‌های تماس</a> استفاده کنید.</noscript><p>این بررسی توسط Google انجام می‌شود: <a href="https://policies.google.com/privacy">حریم خصوصی</a> و <a href="https://policies.google.com/terms">شرایط استفاده</a>.</p></div>';
    }

    /** No token, secret, provider diagnostic, or customer IP is stored or returned. */
    public static function verify($token): array {
        $c=self::config();
        if(!$c['enabled'])return ['ok'=>true,'status'=>200];
        if($c['site']===''||$c['secret']==='')return ['ok'=>false,'status'=>503];
        if(!is_string($token)||$token===''||strlen($token)>4096||preg_match('/\s/',$token))return ['ok'=>false,'status'=>400];
        $response=wp_remote_post('https://www.google.com/recaptcha/api/siteverify',[
            'timeout'=>8,'redirection'=>0,'sslverify'=>true,'limit_response_size'=>8192,
            'body'=>['secret'=>$c['secret'],'response'=>$token],
        ]);
        if(is_wp_error($response)||wp_remote_retrieve_response_code($response)!==200)return ['ok'=>false,'status'=>503];
        $data=json_decode(wp_remote_retrieve_body($response),true);
        if(!is_array($data)||($data['success']??null)!==true)return ['ok'=>false,'status'=>400];
        $host=parse_url(home_url('/'),PHP_URL_HOST);
        $stamp=is_string($data['challenge_ts']??null)?strtotime($data['challenge_ts']):false;
        if(!is_string($data['hostname']??null)||$data['hostname']!==$host||$stamp===false||time()-$stamp>120||$stamp-time()>30)return ['ok'=>false,'status'=>400];
        return ['ok'=>true,'status'=>200];
    }

    public static function enforce(): void {
        $result=self::verify($_POST['g-recaptcha-response']??null);
        if(!$result['ok'])wp_die($result['status']===503?'سرویس بررسی ضداسپم فعلاً پاسخ نمی‌دهد. کمی بعد دوباره تلاش کنید یا با ما تماس بگیرید.':'بررسی ضداسپم کامل نشد یا اعتبار آن پایان یافته است. به فرم برگردید و دوباره آن را تکمیل کنید.','ثبت درخواست',['response'=>$result['status'],'back_link'=>true]);
    }
}
