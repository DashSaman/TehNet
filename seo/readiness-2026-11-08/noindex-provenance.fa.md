# منبع noindex — تفکیک مشاهده، بازتولید و گیت دسترسی
Reviewed:2026-11-08. هیچ تنظیم production تغییر نکرده است.

## مشاهدهٔ production
baseline معتبرTLS همان صفحات عادی را200، canonical خودصفحه وmeta noindex,nofollow نشان داد؛ X-Robots-Tag در آن درخواست‌ها نبود. مسیر رسید درخواست جداست: class-tickets.php عمداً برای tn_service_receipt هدر noindex و no-referrer می‌فرستد؛ این producer اختصاصیِ رسید، توضیح noindex صفحات عادی نیست. robotsCloudflareهم‌زمان search=yes/Allow دارد؛ این مجوز crawl، meta noindex را خنثی نمی‌کند.

## source مستند و فرضیهٔ فعلی
[WordPress wp_robots_noindex](https://developer.wordpress.org/reference/functions/wp_robots_noindex/) وقتی blog_public کاذب باشد [wp_robots_no_robots](https://developer.wordpress.org/reference/functions/wp_robots_no_robots/) را فرا می‌خواند؛ آن تابع noindex وnofollow می‌گذارد. [WP_Sitemaps::sitemaps_enabled](https://developer.wordpress.org/reference/classes/wp_sitemaps/sitemaps_enabled/) نیز پیش‌فرض را از blog_public می‌گیرد و می‌تواند به404بینجامد. بنابراین **blog_public=0 در Settings→Reading فرضیهٔ قوی و سازگار با شواهد است، نه خواندن قطعی همین گزینه در production**.

سورس mainِ CoreSchema، MUsearch-metadata و canonicalقالب بررسی شدند؛ metadata MU صریحاً indexability را تغییر نمی‌دهد. این بررسی نسخهٔ repo است، نه hash قطعی تمام runtime فایل‌های زنده یا CDN؛ producer دیگری را بدون inventoryحذف نمی‌کنیم.

## مانع احراز قطعی
- run_wp_cli option get blog_public از connector به404مسیرهای WPVibe رسید؛ plugin-backed tools موجود نیستند. طبق پیام ابزار، آن مسیرها دوباره امتحان نشدند.
- coreREST GET settings فقط show_on_front/page_on_front را برگرداند؛ blog_public expose نشده است. غایب‌بودن field مساوی0نیست.
- GET تشخیص visibility و Jetpack settings هرکدام rest_no_route داد؛ این‌ها شاهد تنظیم نیستند.
- نصب/فعال‌کردن افزونه، snippet یا تغییر rule برای افزودن دسترسی انجام نشد. فایل، credential، SSH یا مرورگر سیستم مالک استفاده نشد.

## آمادهٔ احراز با مسیر مجاز سرور
ops/inspect-indexability-readonly.php فقط blog_public و نام callbackهای مرتبط را می‌خواند؛ فقط در context موجود WP-CLI سرور قابل اجراست، هیچ update_option، SQL یا نصب ندارد. خروجی شامل path کامل، IP، credential یا دادهٔ مشتری نیست. فعلاً روی production اجرا نشده و وجود ابزار به معنی دسترسی نیست. پس از ارائهٔ مسیر خواندنیِ مجاز سرور/خروجی تأییدشده، مقدار و callbackهای مؤثر با public HEAD/metaهم‌بسته شوند. noindex تا آن زمان دست‌نخورده می‌ماند.

در fixtureابری producerWordPressبا snapshot→blog_public1→بازخوانی→بازیابی0 به‌طور مستقل بازتولید می‌شود؛ این mutation فقط در دیتابیس ساختگی است و اثبات مقدار یا اختیار تغییر production نیست. نتیجهٔ واقعی این آزمایش در receiptِ بسته ثبت می‌شود.
