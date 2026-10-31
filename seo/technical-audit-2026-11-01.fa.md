# بازبینی محدود UX و SEO فنی —۱نوامبر۲۰۲۶

وضعیت: **AUDIT_VERIFIED؛ اصلاح schema تک‌فایلی DEPLOYED_VERIFIED؛ audit اولیه و rehearsal checkpoint تاریخی‌اند**. [رسید](../qa/growth-2026-10-31/technical-audit-and-metadata-role.json) دامنهٔ واقعی را ثبت می‌کند.

## روش و مشاهده

73 پاسخ با GET بدون ورود و TLS پیش‌فرض بررسی شد:31 مسیر عمومی غیرابزاری از موجودی،16محصول صفحهٔ نخست،4 endpoint/probe و22 لینک اصلیِ تازه؛ در مجموع25صفحهٔ محصول و68HTML باHTTP200. این اعداد شمار درخواست/سندند، نه رتبه یا ادعای پوشش تمام URLهای ممکن. sitemap.xml به wp-sitemap.xml رسید و404شد؛ probe ناموجود404 صحیح داد. raw HTML و headerها بیرون Git هستند.

در68سند موفق، یک title/H1 و canonical خودارجاع، robots noindex و JSON-LD قابل‌parse مشاهده شد. عکس‌های موجود در این اسناد attributeهای alt و width/height داشتند؛ درستی معنایی alt، مجوز تصویر یا دقت مدل سه‌بعدی با این کنترل اثبات نمی‌شود. توضیح meta در دو ابزار support/B2B غایب است؛ context عمومی ابزار و noindex باعث می‌شود این را به‌عنوان ایراد رتبه‌بندی قطعی گزارش نکنیم. توضیح مشترک دو صفحهٔ فهرست فروشگاه با canonical مستقل، خطای الزامیِ یکتایی تلقی نشد.

مرورگر واقعی:4مسیر خانه/فروشگاه/مسیرMTCNA/پروفایل ×4حالت1440،375،320 و375بدونJS =16مشاهده. HTTP200، یکH1، نبود overflow/page error، بازشدن منو و Escape/focus در موبایل، navigation بدونJS و target لینک پرش پاس شدند. این smoke محدود است؛ ممیزی کامل WCAG یا CWV میدانی نیست.

گراف کشف، queryها را کنار گذاشته و66از68HTML را از خانه می‌بیند؛ support/B2B در این مدل static-queryless نرسیدند. این حکم orphanبودن نیست: لینکِ دارای context/query عمداً کنار گذاشته شده است و باید جدا طبقه‌بندی شود. درخواست/تیکت واقعی ساخته نشد.

## تشخیص و انتخاب اصلاح

محتوای چهار مسیر learn،lab،learn/mikrotik وlearn/mikrotik/mtcna، عمدتاً مجموعه/مسیر منابع است؛ وجود یادداشت منابع به‌تنهایی نباید همهٔ آن‌ها را Article کند. این برداشت تحریریه از هدف صفحه و راهنمای ارتباط markup با محتوای اصلی است؛ هیچ manual action یا افت رتبه‌ای مشاهده نشده است. اصلاح انتخابی، حذف فقط Article در همین چهار WP page است. افزودن CollectionPage/ItemList و حذف Article از تمام WP pageها دامنه را بزرگ می‌کند؛ درس‌ها خودشان WP page هستند و باید Article خود را نگه دارند. متن، تاریخ، note، توضیح، OG،canonical،robots و دادهٔ سایت تغییر نمی‌کنند.

چهار assertion در baseline واقعاً FAIL شد؛ بعد از اصلاح هر56تست metadata پاس شد.12تست operator و16کنترل بومیِ checker فقط‌خواندنی پاس؛ هنوز این‌ها به‌تنهایی نصب فایل یا انتشار زنده نیستند. checker، baseline جدول‌های business و گزینه‌های حساس منتخب را hash می‌کند و به‌جای migration محتوا استفاده می‌شود؛ هیچ سطر DB نمی‌نویسد. apply/repeat/rollback و browser بومیِ خود فایل باید جدا qualify شوند.

## منابع خوانده‌شده و حدود

بازبینی همهٔ موارد:۱نوامبر۲۰۲۶ به‌وقت تهران. محتوا به‌صورت scoped خوانده شد، نه کل مستندات.

| منبع اولیه | دامنهٔ استفاده | چیزی که ثابت نمی‌کند |
|---|---|---|
| [Google canonical](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls) | signal/hint، self-reference و لینک‌های هماهنگ | canonical انتخابی Google یا رتبه |
| [Google sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview) | کشف و عدم تضمین index؛ تاریخ منبع2025-12-10 | سایت فعلی باید برخلاف گیت مالک index شود |
| [Google robots meta](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag) | نیاز به crawl برای خواندن noindex | robots مکانیزم احراز هویت یا محتوای خصوصی است |
| [Google structured-data guidelines](https://developers.google.com/search/docs/appearance/structured-data/sd-policies) | نمایش مرتبط/واقعیِ محتوای اصلی و عدم تضمین نمایش | JSON معتبر مساوی rich result یا رشد است |
| [Google Article](https://developers.google.com/search/docs/appearance/structured-data/article) | نوع مقاله و propertyهای قابل‌اعمال | هر صفحه با source note باید Article شود |
| [Schema.org CollectionPage](https://schema.org/CollectionPage) | تعریف نوع collection؛ صفحه development بود | این نوع، rich result لازم یا تضمینی دارد |
| [Cloudflare email obfuscation](https://developers.cloudflare.com/waf/tools/scrape-shield/email-address-obfuscation/) | href جایگزین و decode script؛ به‌روزرسانی2026-08-03 |404مسیر decode به‌تنهایی لینک خراب در JS است |
| [WordPress sitemap enablement](https://developer.wordpress.org/reference/classes/wp_sitemaps/sitemaps_enabled/) | blog_public و رفتار404 هنگام غیرفعال‌بودن | تشخیص تمام filterهای سایت بدون بررسی بومی |

ایمیل پروفایل در سه عرض مرورگرِ JS به mailto تبدیل شد؛ در no-JS، وابستگی به obfuscation باقی است. جایگزین‌های عمومی تماس موجودند. Cloudflare یا نشانی ارتباطی تغییر نکرد و هیچ ایمیلی ارسال نشد. sitemap/index launch نیز گیت جدا دارد؛ noindex موجود حفظ می‌شود.

محدودیت‌ها: نه GSC/URL Inspection/Rich Results Test اجرا شده، نه هویت واقعی Googlebot/Bingbot/AI یا کیفیت میدانِ CWV/شبکهٔ ایران اندازه‌گیری شده است. گزارش حاضر جای بررسی رقبا،120فروشگاه، مجوز CAD یا بررسی تجاری25کالا را نمی‌گیرد. MyTel production فقط خواندنی و بدون تغییر است.


## پذیرش staging

source c287a86 در staging بومی با backup/checksum و drift اعمال شد؛8مسیر HTTP فقط حذف4Article را با برابری متن و سایرmetadata نشان دادند.188کنترل browser دسکتاپ/موبایل/no-JS پاس؛ سپس rollback/repeat اصل فایل را برگرداند و داده/runtime برابر ماند. DB write0؛ production هنوز انجام نشده. رسید rehearsal checkpoint مستقل است و audit اولیه را به‌عنوان دادهٔ «بعد از اصلاح» بازنویسی نمی‌کند.


## نتیجهٔ زنده

در۰۲:۲۶تهران source6728ddd با backup تازه/checksum/drift منتشر شد؛ یک فایل metadata و صفر سطر DB/محتوا، repeat بدون تغییر.13GET باTLS و188کنترل browser عمومی پاس؛ فقط Article چهارhub حذف و درس‌ها/خانه/فروشگاه/داده/۷فایل دیگر/containerها/noindex حفظ شدند. [رسید actual production](../qa/growth-2026-10-31/metadata-role-production-release.json) وضعیت فعلی است؛ از audit اولیه نتیجهٔ بعد از اصلاح نسازید. هیچ نتیجهٔ رتبه، ترافیک،RichResult یاAIcitation اندازه‌گیری نشده است.
