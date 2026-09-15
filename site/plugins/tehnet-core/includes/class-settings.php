<?php
/** TehNet editable business settings. */

defined('ABSPATH') || exit;

final class TehNet_Core_Settings {
    private const GROUP = 'tehnet_settings';
    private const PAGE = 'tehnet-settings';

    public function register(): void {
        add_action('admin_menu', [$this, 'add_menu']);
        add_action('admin_init', [$this, 'register_settings']);
        add_shortcode('tehnet_phone', [$this, 'shortcode_phone']);
        add_shortcode('tehnet_address', [$this, 'shortcode_address']);
    }

    public function add_menu(): void {
        add_options_page(
            __('تنظیمات تهران نتورک', 'tehnet-core'),
            __('TehNet', 'tehnet-core'),
            'manage_options',
            self::PAGE,
            [$this, 'render_page']
        );
    }

    public function register_settings(): void {
        $text_settings = [
            'tehnet_phone' => '021-91018746',
            'tehnet_address' => 'تهران، آیت‌الله کاشانی، شاهین جنوبی',
            'tehnet_primary_cta' => 'درخواست مشاوره شبکه',
        ];
        foreach ($text_settings as $key => $default) {
            register_setting(self::GROUP, $key, [
                'type' => 'string',
                'sanitize_callback' => 'sanitize_text_field',
                'default' => $default,
            ]);
        }

        foreach (['tehnet_youtube_url', 'tehnet_telegram_url', 'tehnet_instagram_url'] as $key) {
            register_setting(self::GROUP, $key, [
                'type' => 'string',
                'sanitize_callback' => 'esc_url_raw',
                'default' => '',
            ]);
        }

        add_settings_section(
            'tehnet_identity',
            __('اطلاعات عمومی تهران نتورک', 'tehnet-core'),
            '__return_false',
            self::PAGE
        );

        $labels = [
            'tehnet_phone' => 'شماره تماس',
            'tehnet_address' => 'آدرس',
            'tehnet_youtube_url' => 'YouTube',
            'tehnet_telegram_url' => 'Telegram',
            'tehnet_instagram_url' => 'Instagram',
            'tehnet_primary_cta' => 'متن CTA اصلی',
        ];
        foreach ($labels as $key => $label) {
            add_settings_field(
                $key,
                esc_html($label),
                [$this, 'render_field'],
                self::PAGE,
                'tehnet_identity',
                ['key' => $key]
            );
        }
    }

    public function render_field(array $args): void {
        $key = (string) ($args['key'] ?? '');
        $value = (string) get_option($key, '');
        $is_url = str_ends_with($key, '_url');
        printf(
            '<input class="regular-text" type="%1$s" name="%2$s" value="%3$s">',
            $is_url ? 'url' : 'text',
            esc_attr($key),
            esc_attr($value)
        );
    }

    public function shortcode_phone(): string {
        return esc_html((string) get_option('tehnet_phone', '021-91018746'));
    }

    public function shortcode_address(): string {
        return esc_html((string) get_option('tehnet_address', 'تهران، آیت‌الله کاشانی، شاهین جنوبی'));
    }

    public function render_page(): void {
        if (! current_user_can('manage_options')) {
            wp_die(esc_html__('دسترسی غیرمجاز است.', 'tehnet-core'));
        }
        ?>
        <div class="wrap" dir="rtl">
            <h1><?php esc_html_e('تنظیمات تهران نتورک', 'tehnet-core'); ?></h1>
            <form method="post" action="options.php">
                <?php
                settings_fields(self::GROUP);
                do_settings_sections(self::PAGE);
                submit_button();
                ?>
            </form>
        </div>
        <?php
    }
}
