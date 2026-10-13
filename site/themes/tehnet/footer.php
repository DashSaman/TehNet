<?php
defined('ABSPATH') || exit;

$tn_logo = file_exists(get_theme_file_path('assets/img/tehnet-logo.jpg'));
$tn_banner = file_exists(get_theme_file_path('assets/img/tehnet-banner.jpg'));
$tn_phone = (string) get_option('tehnet_phone', '021-91018746');
$tn_address = (string) get_option('tehnet_address', 'تهران، آیت‌الله کاشانی، شاهین جنوبی');
$tn_youtube = (string) get_option('tehnet_youtube_url', 'https://www.youtube.com/@tehran.network021');
$tn_telegram = (string) get_option('tehnet_telegram_url', 'https://t.me/Tehrannetwork021');
$tn_fa = static function (string $text): string {
    return strtr($text, ['0' => '۰', '1' => '۱', '2' => '۲', '3' => '۳', '4' => '۴', '5' => '۵', '6' => '۶', '7' => '۷', '8' => '۸', '9' => '۹']);
};
$tn_tel = '+98' . preg_replace('/\D/', '', ltrim($tn_phone, '0'));
$tn_icon_phone = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>';
$tn_icon_pin = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>';
$tn_icon_link = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>';
$tn_icon_youtube = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22.54 6.42a2.78 2.78 0 0 0-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.46a2.78 2.78 0 0 0-1.94 2A29 29 0 0 0 1 11.75a29 29 0 0 0 .46 5.33A2.78 2.78 0 0 0 3.4 19c1.72.46 8.6.46 8.6.46s6.88 0 8.6-.46a2.78 2.78 0 0 0 1.94-2 29 29 0 0 0 .46-5.25 29 29 0 0 0-.46-5.33z"/><polygon points="9.75 15.02 15.5 11.75 9.75 8.48 9.75 15.02"/></svg>';
$tn_icon_send = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 2 11 13"/><path d="M22 2 15 22l-4-9-9-4 20-7z"/></svg>';
$tn_icon_grid = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>';
?>
</main>
<?php if ($tn_banner) : ?>
<div class="tn-brand-strip" role="presentation" aria-hidden="true"></div>
<?php endif; ?>
<footer class="tn-site-footer">
    <div class="tn-container tn-footer-grid">
        <div class="tn-footer-col tn-footer-about">
            <div class="tn-footer-brand">
                <?php if ($tn_logo) : ?>
                    <img src="<?php echo esc_url(get_theme_file_uri('assets/img/tehnet-logo.jpg')); ?>" alt="<?php echo esc_attr(get_bloginfo('name')); ?>" width="52" height="52">
                <?php endif; ?>
                <strong><?php bloginfo('name'); ?></strong>
            </div>
            <p>طراحی، اجرا و پشتیبانی زیرساخت شبکه برای شرکت‌ها و کسب‌وکارها؛ خدمات حضوری در تهران و پشتیبانی ریموت در سراسر ایران، همراه با آموزش رایگان شبکه به زبان فارسی.</p>
        </div>
        <div class="tn-footer-col">
            <h3><?php echo $tn_icon_grid; ?><?php esc_html_e('دسترسی سریع', 'tehnet'); ?></h3>
            <ul>
                <li><a href="<?php echo esc_url(home_url('/learn/')); ?>">آموزش</a></li>
                <li><a href="<?php echo esc_url(home_url('/lab/')); ?>">لاب</a></li>
                <li><a href="<?php echo esc_url(home_url('/services/')); ?>">خدمات</a></li>
                <li><a href="<?php echo esc_url(home_url('/shop/')); ?>">فروشگاه</a></li>
                <li><a href="<?php echo esc_url(home_url('/about/')); ?>">درباره ما</a></li>
                <li><a href="<?php echo esc_url(home_url('/contact/')); ?>">تماس با ما</a></li>
            </ul>
        </div>
        <div class="tn-footer-col">
            <h3><?php echo $tn_icon_phone; ?><?php esc_html_e('تماس با ما', 'tehnet'); ?></h3>
            <ul class="tn-footer-contact">
                <li><?php echo $tn_icon_phone; ?><span>تلفن: <a href="tel:<?php echo esc_attr($tn_tel); ?>" dir="ltr"><?php echo esc_html($tn_fa($tn_phone)); ?></a></span></li>
                <li><?php echo $tn_icon_pin; ?><span><?php echo esc_html($tn_address); ?></span></li>
                <li><?php echo $tn_icon_pin; ?><span>شنبه تا پنجشنبه — با هماهنگی تلفنی</span></li>
            </ul>
        </div>
        <div class="tn-footer-col">
            <h3><?php echo $tn_icon_link; ?><?php esc_html_e('همراه ما باشید', 'tehnet'); ?></h3>
            <ul>
                <?php if ($tn_youtube !== '') : ?>
                    <li><a href="<?php echo esc_url($tn_youtube); ?>" target="_blank" rel="noopener"><?php echo $tn_icon_youtube; ?> یوتیوب تهران نتورک</a></li>
                <?php endif; ?>
                <?php if ($tn_telegram !== '') : ?>
                    <li><a href="<?php echo esc_url($tn_telegram); ?>" target="_blank" rel="noopener"><?php echo $tn_icon_send; ?> کانال تلگرام</a></li>
                <?php endif; ?>
            </ul>
        </div>
    </div>
    <div class="tn-footer-bottom">
        <div class="tn-container">© تهران نتورک | TehNet — تمامی حقوق محفوظ است.</div>
    </div>
</footer>
<?php wp_footer(); ?>
</body>
</html>
