<?php
/**
 * Plugin Name: TehNet Register Guard
 * Description: Honeypot + per-IP throttle for customer registration (WooCommerce and wp-login paths).
 * Version: 0.1.0
 */
defined('ABSPATH') || exit;

final class TehNet_Register_Guard {
    public static function init(): void {
        add_action('woocommerce_register_form_start',[self::class,'honeypot']);
        add_action('login_form_register',static function(): void { if ($_SERVER['REQUEST_METHOD']==='GET') { self::honeypot(); } });
        add_action('woocommerce_register_post',[self::class,'guard'],10,3);
        add_filter('registration_errors',[self::class,'core_guard'],10,3);
    }
    public static function honeypot(): void {
        echo '<p class="tn-reg-hp" aria-hidden="true" style="position:absolute;right:-9999px"><label>خالی بگذارید <input name="tn_hp" tabindex="-1" autocomplete="off"></label></p>';
    }
    private static function blocked(?WP_Error $errors = null): WP_Error {
        $errors=$errors ?: new WP_Error();
        if (isset($_POST['tn_hp']) && is_string($_POST['tn_hp']) && $_POST['tn_hp']!=='') { $errors->add('tn_hp','ثبت‌نام نامعتبر است.'); return $errors; }
        if (class_exists('TehNet_Store_Policy') && !TehNet_Store_Policy::throttle('register',5,86400)) { $errors->add('tn_throttle','تعداد ثبت‌نام از این اتصال زیاد است؛ فردا دوباره تلاش کنید.'); return $errors; }
        return $errors;
    }
    public static function guard(string $username,string $email,WP_Error $errors): void { self::blocked($errors); }
    public static function core_guard(WP_Error $errors,string $sanitized_user_login,string $user_email): WP_Error { return self::blocked($errors); }
}
TehNet_Register_Guard::init();
