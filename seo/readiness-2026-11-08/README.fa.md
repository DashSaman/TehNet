# بستهٔ آمادگی ایندکس و کشف خدمات —۸ نوامبر۲۰۲۶
READY_FOR_REVIEW_NOT_DEPLOYED. این بسته noindex، CDN، robots، sitemap، پرداخت، CAPTCHA یا MyTel را تغییر نمی‌دهد. manifest صرفاً پیشنهاد غیرفعال۱۱URL عمومی است؛ تأیید readiness هر URL و مجوز انتشار هنوز لازم است. خارج فهرست، policy فعلی حفظ می‌شود؛ کالای استعلامی با رفع noindex قابل خرید نمی‌شود.

## مشاهدات و مالکیت
خواندن authenticated بدنهٔ۷صفحه موجود از REST انجام شد؛۰ارسال فرم. ID8 یک فرم موجود دارد و ID29 بیشتر از تماس مستقیم مسیریابی تخصصی کم دارد. بخش‌های server/branch روی33، monitoring-acceptance روی31 و firewall-acceptance روی35 وجود دارند. دو لینک عمیقِ اخیر در کارت‌های ID8 نبودند؛ فقط همان دو لینک اضافه شده‌اند. ID29 به intent ownerهای موجود و فرم canonical هدایت می‌شود؛ صفحهٔ جدیدی ساخته نشده است.

مرجع -SEO در main52cc1f1: docs/competitor-service-evidence.md، docs/cross-brand-intent-portfolios.md، docs/wordpress-service-intake-validation.md. پوشهٔ docs/research/2026-11-08-mytel-tehnet/ از connector404 داد؛ پژوهش۸نوامبر آن پوشه در دسترس نبود و خوانده‌شده ادعا نمی‌شود. اسناد موجود عمدتاً۱/۴نوامبرند؛ مقایسه تازهٔ هشت رقیب انجام‌شده ادعا نمی‌شود.

ابزار وب مستقیم نتوانست صفحات را دریافت کند؛ Parallel خانه/services را با acquired_at17اکتبر برگرداند که کهنه و مخالف بدنهٔ تازه REST است؛ برای baseline امروز کنار گذاشته شد. robots از Parallel acquired_at8نوامبر و sitemap404 گزارش شد؛ این‌ها هدر/meta HTML امروز یا خرابی سایت را ثابت نمی‌کنند. workflow جدید از cloud فقط GET معتبرTLS و metadata محدود می‌گیرد؛ خطاها UNKNOWN ثبت می‌شوند. GSC tool list_sites خطای INVALID_ARGUMENT داد؛ هیچ آمار MyTel یا جست‌وجوی عمومی جای داده TehNet قرار نگرفت.

## منبع کنترل و مسیر تصمیم P0
- robots عمومی: بلوک Managed Cloudflare با search=yes/ai-train=no و Google-Extended منع‌شده مشاهده شد؛ این control با Google Search یکی نیست. تنظیم WAF/CDN/control-plane نامعلوم؛ هیچ تغییر شبکه انجام نشده است.
- meta noindex/nofollow طبق گزارش پیشین عمدی است. WordPress blog_public/wp_robots منبع کاندیداست، نه منبع productionِ قطعی احرازشده. هدر X-Robots-Tag، افزونه/قالب و policy CDN باید در baseline مستقل تفکیک شوند.
- source قالب canonical جدا دارد؛ تغییر title/H1/URL/meta در این بسته صفر. canonical self شرط بررسی است، نه تضمین انتخاب Google.
- sitemap provider/visibility واقعی و source snippet rules هنوز باید احراز شوند.404ِ یک مسیر sitemap به معنی نبود همهٔ sitemapها نیست.
- تصمیم انتشار: برای هر کاندید، GET200بدون challenge، canonical یکتا، متن/CTA نهایی، عدم noindex در meta و header، عدم disallow برای bot مربوط و inclusion فقطURL عمومی در sitemap بررسی شود. queryهای preview/request/حساب/پرداخت و سایر استثناها حفظ شوند. هر فیلد UNKNOWN یعنی مجوز فعال‌سازی صادرنشده.
- تغییر پیشنهادی آینده پس از مجوز: snapshot خصوصیِ گزینه‌ها/robots/header/CDN، تعیین تنها producerهای مؤثر noindex، allowlist دقیق صفحه، sitemap همان allowlist، purge محدود و آزمون TLS/موبایل/no-JS/فرم بدون ارسال؛ برگشت دقیق گزینه/فایل/rule قبلی. سوییچ سراسری blog_public و حذف blanket robots مجاز نیست.

## جدول تغییر
| issue → evidence | existing owner | exact change | risk | check | rollback | outcome |
|---|---|---|---|---|---|---|
| کشف سخت پذیرش امنیت/پایش؛ REST تازه فقدان لینک را نشان داد |8/services |۲لینک به35#firewall-acceptance و31#monitoring-acceptance | کم، لینک/چیدمان | hash و native/لینک؛ UI browser بعداً | فقط بدنه8 با hash قبل/بعد | READY_FOR_REVIEW |
| انتخاب مسیر مبهم؛ بدنه29خوانده شد |29network-tehran |انتهای همان متن، مسیریابی به ownerهای تخصصی و فرم موجود | کم، طول موبایل | native roundtrip/sanitization؛ موبایل/RTL هنوز NOT_RUN | فقط بدنه29 با hash قبل/بعد | READY_FOR_REVIEW |
| noindex عمدی و منبع اجرایی نامعلوم |۱۱URL کاندید |index-policy.json غیرفعال و collector خواندنی | اجرای اشتباه پیشنهاد | policy disabled و exception تست می‌شود | حذف فایل پیشنهاد؛ production تغییری نکرده | NEEDS_APPROVAL |
| گزارش واقعی عمومی نداریم |قالب تحویل |نمونه صریحاً فرضی با پاسخ/رفع جدا | تصور پروژه واقعی | برچسب فرضی و بدون customer/SLA | حذف draft | READY_FOR_REVIEW |
| متخصص/Case واقعی فاقد مدرک/رضایت |قالب workflow موجود |هیچ فرد/گواهی/مشتری/نتیجه ساخته نشد | اعتبار کاذب | تأیید خصوصی شاهد و مجوز لازم | انتشار نشود | BLOCKED |

## راهنمای جاری و محدوده
[Google robots/meta](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)، [AI features](https://developers.google.com/search/docs/appearance/ai-features)، [Google-Extended](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers#google-extended)، reviewed8نوامبر: index/snippet eligibility و crawlability برای حضور Search/AI آن لازم‌اند؛ ایندکس و نمایش تضمین نیست. فایل AI خاص یا schema اضافی شرط عمومی نیست. Google-Extended مربوط به training/grounding برخی سرویس‌های دیگر است و کلید رتبه Search نیست. گزارش Web Search با گزارش مستقل Generative AI یکی فرض نشود؛ endpoint داده جدید باید در ابزار واقعاً موجود باشد، و اینجا داده‌ای دریافت نشده است.
schema source فعلی LocalBusiness است؛ schema plugin تازه، Review/aggregateRating/FAQ یا مدرک جعلی اضافه نشده. GBP ایران، outreach، backlink و ثبت انبوه اجرا نشده‌اند.

## آزمون و ادامه
workflow فقط GitHub-hosted عمومی standard با contents:read، timeout۱۵دقیقه، بدون cache/artifact/مرورگر محلی. native fixture تازه WordPress7.1.4 با Core/Store برای authoring/render است؛ WooCommerce11.2.1 پس از شکست نخستِ shortcode به fixture افزوده شد؛ مرورگر/شباهت کامل production/تست canonical publisher و SQL restore اجرا نمی‌شوند. نتایج بعد از job ثبت می‌شوند، نه پیشاپیش PASS.
پذیرش خصوصی denied-list فقط همین شاخه طبق تأیید مالک NOT_RUN_OWNER_APPROVED_BRANCH_EXCEPTION است؛ source-pattern و publication_guard ابری جایگزین محدود. هیچ راز قدیمی یا فایل سیستم مالک خوانده نشد؛ تنها پیوست جدید خودش خوانده شد.
PR93/Queue کامل در شاخهٔ خودش c4c76ad و VERIFIED_SYNTHETIC_CLOUD_STAGING_NOT_DEPLOYED است؛ main قدیمی‌تر است. PR88 تکرار نشود؛ PR89–91/93 merge/deploy تأیید جدا می‌خواهند. MyTel read-only و برند تخصصی VoIP، noindex، inquiry-only، payment/CAPTCHA و گیت‌های امنیت حفظ‌اند.


## نتیجهٔ واقعی بسته
[PR94](https://github.com/DashSaman/TehNet/pull/94)، [run42491528157](https://github.com/DashSaman/TehNet/actions/runs/42491528157)، source630c6f3d34ab4c94919090e5cf6da64125439f8a:۴unit،۳۳native و۱۴۴component browser پاس شدند. receipt کامل/labelها: [verification.json](verification.json). native parse/serialize/KSES، ذخیره واقعی دو بدنه، حفاظت title/slug/parent/excerpt/meta، رندر shortcode واقعی باWoo11.2.1/Core/Store، باقی‌بودن noindex و بازگرداندن بدنه‌های fixture را آزمود. مرورگر1440/768/375/320، روشن/تیره/JS/no-JS،RTL/overflow و href فرم وMyTel را بررسی کرد؛ harness محتوایی با CSSسورس و قواعد wrapper/wrapping است، نه frontend کامل یا فونت/CAPTCHA.۰ارسال و۰mutation production؛ اسکرین‌شات صادر نشد.

[baseline تازه](baseline.json):۱۱صفحه200/self-canonical/یکH1/noindex,nofollow؛ robots200؛wp-sitemap.xml404. X-Robots-Tag در همین مسیر غایب؛ producer دقیق هنوز نامحرز. دریافت درست از runner، محدودیت ابزار وب قبلی را رفع کرد؛ پاسخ17اکتبر Parallel همچنان برای وضعیت امروز معتبر نیست.

شکست‌ها حفظ‌اند: run42490996662 به نبود shortcode رسید؛ Store آن را فقط با WooCommerce register می‌کند، پس fixture با asset رسمیِ hash-checked تکمیل و IDsپیش ازactivationرزرو شدند. run42491227421 موفق ولی receiptشمارنده۰ به‌علت scope محلی/global در WP-CLI داشت؛ proof۳۳تایی شمرده نشد. run42491336435 با counter/label صریح۳۳پاس، و run42491528157 با۱۴۴browser پاس شد.

[کنترل‌ها و گزارش جدید AI](ai-controls.fa.md) و [مقایسه محدود رقبا](competitor-delta.fa.md) جدا ثبت‌اند. منبع metadata سورس: MUsearch-metadata بدون تغییر robots، CoreLocalBusiness و canonical قالب؛ producer productionblog_public هنوز فقط فرضیه است. structured data افزوده نشد.

DONE: خواندن فعلی ownerها، baseline محدود، diff دو بدنه و template فرضی، native/component acceptance، منابع control جدید. READY_FOR_REVIEW: دو بدنه و policy غیرفعال۱۱URL. BLOCKED/UNKNOWN: case واقعی دارای اجازه، شواهد متخصص، GSC/Bingوکنترل مؤثر، source دقیقnoindex/CDN، activation، canonical release rehearsal وfull-frontend acceptance. این‌ها ادعای پایان سئو یا parity نیستند.
