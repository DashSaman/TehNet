# تصمیم محدود index — نسخهٔ دوم
این بسته پیشنهاد اجرایی است؛ فعال‌سازی production **NEEDS_APPROVAL** است. منبع noindex قبلاً روی سرور احراز شده: Reading/Discourage search engines، گزینهٔ blog_public=0 و callback هستهٔ wp_robots_noindex. این تشخیص تکرار نشده و گزینهٔ سراسری تغییر نمی‌کند.

## دامنهٔ دقیق
inventory.json شامل هویت ۳۲ page منتشرشده و استثناهای واقعی commerce است. ۱۱ مسیر شرکت/خدمات و پنج مقصد جدیدِ v2، حداکثر ۱۶ مسیر پیشنهادی‌اند. سیاست همهٔ URLهای دیگر را index نمی‌کند. مسیرهای واقعی cart-2، tn-checkout، tn-account، support، b2b و shop، query/preview/receipt، taxonomy/post/feed/attachment، درس‌های بازبینی‌نشده و پروفایل از این دسته بیرون‌اند. software/tunnels اپلیکیشن مستقل‌اند؛ header و دسترسی آن‌ها تغییر نمی‌کند. noindex احراز هویت یا حفاظت فایل خصوصی نیست.

## کد و وضعیت پیش‌فرض
Core0.3.2 ماژول class-index-policy.php را ثبت می‌کند. نبود option مخصوص یعنی OFF و خروجی پیشین دست‌نخورده می‌ماند. install-off هیچ optionی نمی‌سازد. activation فقط یک option دقیقِ allowlist شامل path و ID می‌سازد؛ با هویت، publish بودن و نبود password هر صفحه تطبیق می‌دهد. option نامعتبر، duplicate، private path یا ID نادرست کل allowlist را می‌بندد. blog_public همیشه0 باقی می‌ماند.

در درخواست canonical بدون query و فقط برای همان page، تنها فیلتر شناخته‌شدهٔ هسته wp_robots_noindex از همان process حذف می‌شود. noindex افزونهٔ دیگر، header یا CDN پاک نمی‌شود؛ تعارض باید پذیرش را متوقف کند. برای مسیرهای دیگر، noindex/nofollow و header محدودکننده افزوده می‌شود. هیچ auth، payment، CAPTCHA یا bot policy تغییر نمی‌کند.

sitemap هسته فقط provider صفحات و IDهای همین allowlist را دارد؛ user، taxonomy، product، post و private مقصد نیستند. robots_txt فقط خط Sitemap را اضافه می‌کند؛ گروه‌های موجود و قواعد admin، Google-Extended، AI training یا Cloudflare دست‌نخورده‌اند. بر اساس source رسمی do_robots، WordPress از5.3 دیگر صرف blog_public=0 را به Disallow:/ تبدیل نمی‌کند؛ فرض وجود چنین قاعده‌ای مجوز حذف آن نیست. قواعد واقعی CDN/سرور باید در زمان انتشار خواندنی کنترل شوند؛ این fixture نمایندهٔ WAF زنده نیست.

## همان publisher؛ سه تصمیم جدا
۱. انتشار محتوای v2 با scope tehnet-commercial-decision-20261108-v2.
۲. نصب خاموش با scope tehnet-index-runtime-20261108-v1؛ فقط class جدید و bootstrap Core با checksum. فایل class ابتدا نصب و bootstrap پس از آن جایگزین می‌شود؛ rollback به ترتیب معکوس است.
۳. فعال‌سازی با scope tehnet-index-allowlist-20261108-v1؛ فایل runtime تغییر نمی‌کند، option ایجاد می‌شود. هر ۱۶ صفحه باید پیشاپیش با body hash، عنوان، هویت و excerptهای تعیین‌شده و marker صفحه‌های جدید تطبیق داشته باشد. در نبود N1/A1–A4 یا drift اجرا رد می‌شود.

هر دو scope جدید از ops/release-growth-content.py و همان immutable bundle/config/backup/runtime guard استفاده می‌کنند؛ ops/migrate-index-policy.php فقط migration بومی option است، deployer موازی نیست. مسیر خصوصی، شناسهٔ container واقعی، مجوز اجرایی و backup checksum باید خارج Git در config قرار گیرند. رشتهٔ authorization صرفاً شناسهٔ scope است و جای تأیید مالک را نمی‌گیرد. main و production در این مأموریت نوشته نشده‌اند.

## پذیرش و rollback
قبل: HTML noindex/nofollow، sitemap404، blog_public0 و option غایب. پس از install-off باید همین وضعیت بماند. پس از activation در fixture، ۱۶ مقصد200/self-canonical بدون noindex متعارض و XML با همان۱۶URL لازم است؛ مسیرهای غیرمجاز و query همچنان noindex باشند. درخواست Googlebot در fixture، crawl واقعی Google یا نتیجهٔ index نیست. robots و assetها هم جدا بررسی می‌شوند. تصویر ذخیره یا منتشر نمی‌شود.

Rollback ابتدا option activation را دقیقاً به ردیف پیشین (در این بسته absent) برمی‌گرداند؛ سپس bootstrap/class خاموش بازگردانی می‌شوند. blog_public0 تغییر نمی‌کند. snapshot خام option/autoload و journal فقط بیرون web/Git ذخیره می‌شوند. migration با قفل مشترک canonical، transaction و compare-before-write کار می‌کند؛ قبل و بعد هر عملیات، جدول‌های کسب‌وکار و گزینه‌های حساس hash می‌شوند. rollback به دیتابیس قدیمی restore نمی‌کند و دادهٔ تازهٔ مشتری را نگه می‌دارد. drift در option/file یا journal مبهم نیازمند reconciliation است، نه overwrite.

## کنترل زنده پس از تأیید
backup تازه و checksum، recovery qualification، compare آخرین main و PRهای دارای publisher/CSS مشترک، سپس staging و drift guard ضروری‌اند. cache purge فقط برای همین مسیرهای تأییدشده و در مجوز انتشار لازم است؛ تنظیم عمومی cache/WAF عوض نشود. HTML، HTTP X-Robots-Tag، robots مؤثر Googlebot، canonical، auth/receipt و XML از بیرون بررسی شوند. هر تعارض noindex یا Disallow مؤثر، انتشار index را متوقف و rollback محدود را فعال می‌کند؛ producer دیگری بی‌اجازه خاموش نشود.

GSC/Bing دادهٔ این سایت در اتصال فعلی ندادند؛ تعداد indexed URL، impression، traffic، رتبه یا توصیهٔ AI قابل اثبات نیست. removal noindex به معنای پذیرش/رتبه در Google نیست و آموزش مدل با Search visibility یکی نیست.

منابع رسمی خوانده‌شده:
- https://developer.wordpress.org/reference/functions/do_robots/
- https://developer.wordpress.org/reference/hooks/wp_sitemaps_posts_query_args/
- https://developer.wordpress.org/reference/hooks/wp_sitemaps_post_types/
- https://developer.wordpress.org/reference/hooks/wp_sitemaps_add_provider/
- https://developers.google.com/search/docs/crawling-indexing/block-indexing
