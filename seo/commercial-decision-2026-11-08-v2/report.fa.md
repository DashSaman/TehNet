# تحویل بستهٔ تجاری و SEO نسخهٔ دوم — ۸ نوامبر ۲۰۲۶
وضعیت: **VERIFIED_STAGING_NOT_DEPLOYED**. سورس پذیرش `ec7eb0a0f44305f3064ae7666106a0f4e4031c05`، [اجرای واقعی cloud](https://github.com/DashSaman/TehNet/actions/runs/42503696771) و [رسید ماشین‌خوان](verification.json). این گزارش و CURRENT جدید جایگزین وضعیت اجرایی v1 هستند؛ شواهد قدیمی حفظ‌اند.

## نتیجهٔ قابل مشاهده
چهار خدمت موجود توسعه یافتند؛ N1 مستقل و چهار مقالهٔ کاملِ تصمیم خرید آماده‌اند. owner8 هم به N1 و راهنماها لینک ورودی دارد. جمع متن‌های اصلی کامل **۹**، تغییرات page در fixture **۵ موجود +۵ تازه**، تغییر page در production **۰**، تعداد indexed URL احرازشده **UNKNOWN** است. CI به معنی برابری رقابتی یا انتشار نیست؛ Issues63/75 بسته نشده‌اند.

| ID | مالک/URL (برای جدیدها پیشنهادی و هنوز غایب از production) | تغییر واقعی |
|---|---|---|
| S1 | /services/network-tehran/؛29 | انتخابگر مسئله→ورودی→خروجی→خدمت، حدود حضوری/ریموت و CTA فعلی |
| S2 | /services/network-setup-tehran/؛33 | فرم خالی و نمونهٔ نیازسنجی؛ خلاصهٔ سرور با حفظ anchor و لینک N1 |
| S3 | /services/network-support-tehran/؛31 | تفکیک رخداد/نگهداری/توسعه/پایش، گزارش و موارد باز، پاسخ≠رفع |
| S4 | /services/mikrotik-tehran/؛35 | مسیر آموزش در برابر تغییر RouterOS فعال، معیار پذیرش و منابع نسخه‌دار |
| N1 | /services/server-virtualization-tehran/ | دامنهٔ مستقل workload/مهاجرت/مجوز/بازیابی، دو سناریوی فرضی، ماتریس تحویل |
| A1 | /network-support-contract-guide/ | راهنمای بندهای عملیاتی پشتیبانی و کاربرگ مقایسهٔ توافق |
| A2 | /network-project-proposal-checklist/ | پیشنهاد هم‌دامنه، فرم مقایسه، دو پیشنهاد صریحاً فرضی و هزینه‌های جدا |
| A3 | /business-server-planning-guide/ | نیازسنجی پیش از CPU/RAM، منبع داده/UNKNOWN، گزینه‌ها و نمونهٔ فرضی |
| A4 | /server-backup-restore-acceptance/ | checkpoint/backup نسخه‌دار، RPO/RTO با واحد زمان، مدرک بازیابی و NOT_TESTED |

[متن کامل Markdown/Gutenberg و متادیتا](../../content/commercial-decision-2026-11-08-v2/)، [قبل/بعد با SHA و منشأ](../../content/commercial-decision-2026-11-08-v2/before-after.json)، [صف ID/intent/source/acceptance/rollback](../../content/commercial-decision-2026-11-08-v2/action-board.json). هشت CSV و چهار HTML چاپی کامل در worksheets قرار دارند؛ خروجی عمومی از۱۲فایل PHP ثابت بدون ورودی/DB، با هدر noindex/nosniff سرو می‌شود. نام فایل دانلودی CSV، Content-Type و bytes واقعاً آزموده شدند. جدول‌ها در موبایل داخل wrapper می‌لغزند و صفحه overflow ندارد. نمونه‌ها و فرم خالی، Case یا نتیجهٔ اندازه‌گیری مشتری نیستند.

## مسیر درخواست واقعاً کار کرد
روی قالب و PHP/DB واقعی، CTA صفحهٔ N1 به فرم موجود Services و context مجاز server-scoping رسید؛ nonce واقعی، POST به admin-post موجود، رسید فاقد ایمیل/متن خصوصی و یک تیکت private/open با thread و context درست ذخیره شدند. رکورد و رسید متعلق به آزمون حذف شدند. پنج منفی nonce/context/honeypot/CAPTCHA نیز پذیرفته شدند. CAPTCHA در fixture روشن و transport ارائه‌دهنده ساختگی است؛ چالش واقعی Google/ایمیل/پرداخت/فرم production آزموده یا ارسال نشد. سامانهٔ موازی inquiry/quote/ticket ساخته نشده است.

## ناشر canonical و بازگشت
scope محتوا `tehnet-commercial-decision-20261108-v2` در همان ops/release-growth-content.py و ops/migrate-growth-content.php است. پنج owner موجود8/29/31/33/35 و پنج page جدید محدودند.8 فقط body؛29/31/33/35 body/title/excerpt. این اجازهٔ تازهٔ v2 به مجوز body-only نسخهٔ اول نسبت داده نمی‌شود. v2 candidateهای8/29 v1 را جایگزین می‌کند؛ انتشار پشت‌سرهم v1 و v2 مجاز فرض نشود.

۱۵فایل runtime مالکیت دارند:۱۲دارایی PHP ثابت، htaccess محدود directory، CSS جدول scoped و class-content-types. فایل route، فقط سه page شناخته‌شده76/188/207 را پیش از rewrite عمومی tn_lab حل می‌کند؛ همان URI و همان داده، بدون نوشتن rewrite_rules. وجود رکورد هم‌نام CPT باعث عدم override می‌شود. native قبل، shadow را بازتولید کرد؛ پس از اعمال هر سه resolver درست بودند و byte/autoload گزینهٔ rewrite ثابت ماند. این مشاهده staging است و اثبات خرابی فعلی production نیست.

check→apply→repeat با ساخت۵page و اصلاح۵owner اجرا شد؛ repeat صفر write بود. rollback همان۵owner را با متن، عنوان، excerpt، meta و revision برگرداند،۵page تازه را draft کرد و۱۵فایل را برگرداند؛ repeat rollback هم داده را تغییر نداد. کل دامنهٔ DB یا مشتریان از backup قدیمی restore نشدند. guard سخت‌گیرانهٔ محتوا همچنان در تغییر protected state واقعی، کار را متوقف و reconciliation می‌خواهد؛ helper پاک‌سازی fixture ابزار production نیست.

## تصمیم index؛ فعال‌سازی هنوز مجاز نیست
[بستهٔ E و inventory واقعی](../index-decision-2026-11-08-v2/README.fa.md) شامل۳۲page منتشرشده و استثناهای واقعی cart-2/tn-checkout/tn-account/support/b2b/shop است؛ aliasهای draft با صفحات فعال اشتباه نشده‌اند.۱۱مسیر شرکت/خدمات +۵مقصد تازه، حداکثر۱۶کاندیدا هستند؛ هیچ صفحهٔ آینده خودکار قابل‌ایندکس نمی‌شود.

دو scope مستقل از همان ناشر: `tehnet-index-runtime-20261108-v1` فقط۲فایل Core را OFF نصب می‌کند؛ `tehnet-index-allowlist-20261108-v1` هیچ فایلی نمی‌نویسد و فقط option دقیق path/ID را پس از تطبیق همهٔ body/title/excerptهای لازم و marker صفحه‌های جدید می‌سازد. blog_public همواره0 می‌ماند. فقط producer شناخته‌شدهٔ core برای canonical مجاز از همان request برداشته می‌شود؛ producer دیگر/هدر/CDN پاک نمی‌شوند.

در fixture: OFF همان noindex/sitemap404؛ فعال فقط۱۶URL200/self-canonical با XML دقیق همان۱۶؛ مسیرهای private/unlisted/query همچنان noindex؛ producer مستقل noindex عمداً نگه داشته شد؛ rollback option را به absent و۲فایل را به قبل برگرداند و یک رکورد تازهٔ کسب‌وکار را حفظ کرد. آن رکوردِ خود آزمون سپس حذف شد. robots گروه‌های موجود/کنترل training را تغییر نمی‌دهد؛ فقط Sitemap اضافه می‌شود. software/tunnels مستقل، MyTel، WAF/DNS/Origin و Google AI settings تغییر نکرده‌اند. crawl واقعی Google یا index/رتبه/AI citation اثبات نشده است.

## شواهد و محدودیت
۳۷آزمون واحد مرز ناشر، رگرسیون native قبلی۳۷، پذیرش native بلوک/KSES/داده/anchor/rollback و۲۱۱۲چک مرورگر واقعی موفق‌اند؛۳فاز HTTP index برابر49/86/49 هم پذیرفته شدند. مرورگر۴عرض1440/768/375/320 و روشن/تیرهٔ واقعی JS، RTL، فونت و asset واقعی، H1/meta/canonical/schema و لینک‌ها را آزمود. no-JS فعلی روشن است؛ تیرهٔ بدون JS ساخته/ادعا نشده است. صفر screenshot/ویدیو ساخته یا منتشر و صفر بازبینی دستی تصویری انجام شد. fixture موقت پس از آزمون جمع شد؛ staging دائمی ساخته نشد.

runtime fixture WordPress7.1.4/PHP8.3.36/MariaDB11.4.13/Woo11.2.1/theme0.5.1 است؛ Core هنگام نصب OFF0.3.2 و پس از بازگشت0.3.1 بود. آخرین خواندن مجاز قبلیِ production، PHP8.3.32 را نشان می‌داد؛ یکسانی کامل محیط ادعا نمی‌شود. fixture فقط هویت/public body و دادهٔ ساختگی دارد، نه dump مشتری. HTTP خارجی، cron، ایمیل و پرداخت بسته‌اند. خروج Node relay و حذف app/DB/CLI/network مستقل کنترل شدند.

اجرای قبلی به تغییر۶جدول داخلی Woo برخورد کرد. bootstrap واقعی public و admin-post بدون action پیش از baseline، نصب تازه را پایدار کرد؛ در اجرای نهایی changed_keys=[] و صفر نشست تازه پاک شد. هیچ protected table/guard حذف نشد. checkout فقط دو snapshot پاک source/baseline را shallow گرفت، نه تمام تاریخچه.

اسکن فهرست خصوصی روی دستگاه مالک NOT_RUN_OWNER_APPROVED_BRANCH_EXCEPTION است، فقط همین شاخه. source-pattern و publication_guard اجرا شدند؛ پاکی تاریخچه، چرخش رمز تاریخی یا مهار origin نتیجه نمی‌شود. جز خواندن فایل دستور پیوست همین درخواست، کار اجرایی از API و cloud انجام شد؛ مرورگر، VM، پروفایل/credential، فایل کار و ACL محلی مالک استفاده نشد؛ noindex دوباره با SSH عیب‌یابی نشد. منبع Reading/blog_public0 به [احراز قبلی](../readiness-2026-11-08/noindex-provenance.fa.md) ارجاع دارد.

## انتشار و کار باقی
همهٔ موارد این بسته READY برای بازبینی‌اند، **NOT_DEPLOYED**. merge، محتوای محدود، نصب runtime خاموش و فعال‌سازی allowlist گیت‌های جدا و NEEDS_APPROVAL دارند. پس از تأیید فقط bundleِ دقیق، backup تازه/checksum، recovery qualification، drift guard، staging متناسبِ آخرین main و rollback اجرا شود. source مبنای تست ec7eb0a است؛ main در آخرین خواندن04c2af9 بود و نوشته نشده است.

PR89/90/91 باز و staging-only، PR93 باز/draft با Queue synthetic پذیرفته‌شده و PR94 باز/draft هستند؛ هیچ merge/deploy این‌ها انجام نشد. PR88 قبلاً live است و replay نشود. CSS/publisher مشترک با89–91/93 باید پس از merge واقعی reconcile و bundle تازه ساخته شود؛ مجوز PR88 مصرف شده و به این بسته سرایت ندارد. `docs/agent-continuation.fa.md` و CURRENT سه فایل ادامه به همین گزارش هدایت می‌کنند.

MyTel مرجع اصلی PBX/IVR و فقط‌خواندنی ماند. هیچ قیمت/موجودی/گواهی/Case/SLA ساختگی،۱۲۰سایت بررسی‌شده،CAD دقیق۲۵کالا یا ویدیوی ضبط‌نشده ادعا نشد. رضایت انتشار Case واقعی، تأمین CAD/شناسهٔ فیزیکی، درس‌های منتظر انتشار،GNS3/۹سناریوی ضبط، دادهٔ TehNet در GSC/Bing و گیت‌های history/rotation/origin همچنان جدا هستند. [درس‌های قابل انتقال به -SEO](../../docs/seo/portable-lessons-2026-11-08-v2.fa.md) در TehNet آماده شد؛ به -SEO نوشته یا merge نشده است.
