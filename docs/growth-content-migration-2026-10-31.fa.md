# migration محدود محتوای Services/Lab

وضعیت: **پیاده‌سازی و۳۷ آزمون native تأیید؛ production اجرا نشده است.** این ابزار مکمل پذیرش editor و backup/restore در `docs/editor-release-acceptance-2026-10-31.fa.md` است. فروشگاه، محصولات، خانه، منو و MyTel جزو محتوای قابل‌تغییر آن نیستند.

## دامنه و اجرا

`ops/migrate-growth-content.php` فقط با WP-CLI و کاربر دارای `manage_options` اجرا می‌شود. manifest همین بسته باید schema/key موردانتظار، دقیقاً۲ صفحه و۲ hub و SHA256 ثابت داشته باشد. مسیرهای production فقط دو فرزند شناخته‌شدهٔ Services/Lab هستند؛ parent/path بررسی و ID جدید از درج همان محیط گرفته می‌شود. صفحه‌ای که از قبل در path موردنظر وجود دارد بدون journal معتبر پذیرفته نمی‌شود. IDهای clone ورودی release نیستند.

پارامترها از تنظیمات خصوصی اجرای CLI می‌آیند:

| متغیر | کاربرد |
|---|---|
| `TN_GROWTH_MANIFEST` | فایل manifestِ کپی‌شده و بررسی‌شده |
| `TN_GROWTH_DIGEST` | SHA256 همان byteهای immutable |
| `TN_GROWTH_JOURNAL_DIR` | پوشهٔ خصوصی با mode0700، بیرون document root |
| `TN_GROWTH_MODE` | `check`، `apply` یا `rollback`؛ پیش‌فرض check |
| `TN_GROWTH_AUTHORIZED_RELEASE` | marker داخلی دامنهٔ ازقبل مجاز؛ به‌تنهایی مجوز مالک یا جای backup نیست |

اطلاعات SSH، CLI path/user واقعی، تنظیمات اتصال، dump و snapshot فقط در تنظیمات خصوصی‌اند. اجرای مستقیم این PHP، فایل‌های سایت را deploy نمی‌کند و backup تازه نمی‌سازد. قبل از production باید workflow شش‌فایلیِ کنترل‌شده، checksum/backup تازه، drift، journal و بازگشت فایل‌ها آماده و آزموده شود؛ sync۴۱فایلی clone مجاز نیست.

در staging فقط محیط شناخته‌شدهٔ loopback با mail/HTTP/cron/payment بسته پذیرفته می‌شود. در production، domain/noindex و مسیرهای دقیق مجاز بررسی می‌شوند. بلوک‌ها parse/serialize و به core paragraph/heading/list/list-item/shortcode محدودند؛ shortcodeهای همین بسته allowlist دارند. هیچ دادهٔ مشتری یا secret از فرم دریافت نمی‌شود.

## حفاظت و بازگشت

قفل فایل journal و قفل advisory دیتابیس از اجرای هم‌زمان migration جلوگیری می‌کنند. برای ویرایشگر عادی وردپرس نیز تراکنش مستقل با isolation همان تراکنشِ REPEATABLE READ و قفل ردیف/بازهٔ post، revision و postmeta گرفته می‌شود؛ وضعیت پس از گرفتن قفل دوباره اعتبارسنجی می‌شود. session دارای تراکنش قبلی یا autocommit خاموش پذیرفته نمی‌شود؛ تراکنش caller ناخواسته commit نمی‌شود. تنظیم سراسری دیتابیس تغییر نمی‌کند.

متن دو hub فقط append می‌شود. snapshotهای خصوصی شامل ردیف، meta و revisionهای قبلی‌اند. محدودیت revision تنها در همان درخواست CLI و برای رکوردهای مدیریت‌شده موقتاً نامحدود می‌شود؛ حفظ اصل revisionها پیش از commit دوباره بررسی می‌شود. هنگام rollback، hub دقیقاً بازمی‌گردد و فقط revisionهای افزوده‌شدهٔ همان تغییر پاک می‌شوند. دو صفحهٔ ساخته‌شده draft می‌شوند؛ دادهٔ موجود دیگران حذف نمی‌شود.

جدول‌های مرتبط با prefix سایت، به‌جز options و Action Scheduler، با hash ردیف‌های مرتب مقایسه می‌شوند؛ در محیط آزموده‌شده۴۷ جدول بود. رکوردهای همین دو hub/صفحات جدید و revisionهایشان از این مقایسهٔ عمومی کنار می‌روند و snapshot دقیق جدا دارند. options حساسِ انتخاب‌شده مستقیم از DB خوانده می‌شوند؛ تکیه به cache برای تشخیص drift نیست. پرداخت/ERP، noindex، خانه/منو/محصولات و دادهٔ خارج دامنه در محافظت باقی می‌مانند. ایمیل و HTTP وردپرس نیز فقط در اجرای همین CLI مسدود و filterها در پایان برداشته می‌شوند.

مقایسهٔ درون تراکنش بر دید سازگار همان تراکنش تکیه دارد؛ همهٔ نوشتن‌های مستقل مشتریان در کل سایت قفل نمی‌شوند. این ابزار دادهٔ بیرون دامنه را بازنویسی نمی‌کند. پذیرش release باید مشاهدهٔ مناسبِ پیش/پس را نیز ثبت کند و تغییر مشروع هم‌زمان را با تغییر خود migration خلط نکند.

وضعیت journal: `PREPARED` → `COMMIT_READY` → `APPLIED`، و برای بازگشت `ROLLED_BACK`. خطای درون تراکنش rollback شده با `FAILED` ثبت می‌شود. خطا یا قطع مبهم نزدیک commit به بررسی مستقل نیاز دارد؛ `COMMIT_READY`/`NEEDS_RECONCILIATION` مجوز تکرار خودکار نیستند. journal با mode0600 و rename اتمی نگه داشته می‌شود. صرف پاک‌کردن journal یا ساختن آن داخل web root روش رفع خطا نیست.

اجرای دوبارهٔ apply پس از تأیید snapshotها صفر تغییر دارد؛ rollback دوباره هم صفر تغییر. اگر ویرایشگر دیگری محتوا، meta، قفل ویرایش یا revision را عوض کرده باشد، عملیات fail-closed است و آن تغییر overwrite نمی‌شود. این محدودیت عمداً به معنی «rollback در هر وضعیت آینده بدون بازبینی» نیست.

## آزمون واقعی و بازبینی

`tests/growth-content-migration-native.php` روی clone بومی با هویت و isolation تأییدشده اجرا شد؛ fixtureها parentهای تازه دارند و صفحات قبلیِ بررسی editor دست‌نخورده می‌مانند.۳۷ assertion شامل apply، ذخیرهٔ دقیق فارسی/quote، repeat، checksum، مسیر متعلق به دیگران، drift، caller transaction، خطای hook وسط عملیات، rollback/repeat و noindex پاس شد.۱۳ صفحهٔ مصنوعی و revisionهای وابسته cleanup و fingerprint همهٔ posts/postmeta دقیقاً برابر قبل شد. backup کاملِ پیش از هر run خصوصی است. source hash و رسید مناسب انتشار در `qa/growth-2026-10-31/migration-verification.json` هستند.

یک بازبین محدود native GPT-6.1 Sol با effort متوسط، فقط این دو فایل و خطر transaction/journal/rollback را خواند؛ آزمون native را او اجرا نکرد. دو یافتهٔ واقعی نسخهٔ پیش‌نویس با آزمون تازه بازتولید شدند: از دست رفتن تغییر concurrent در پنجرهٔ پیش از rollback (P1) و prune شدن revision قبلی در سقف نگهداری (P2). هر دو پیش از production اصلاح شدند. آزمون race از اتصال دوم در مرز START TRANSACTION استفاده می‌کند؛ آزمون دیگر نشان داد UPDATE و INSERT metadata اتصال دوم در زمان قفل، timeout می‌شوند و چیزی overwrite نمی‌شود. retention fixture دقیقاً۲ revision داشت و همهٔ اصل‌ها پس از apply باقی ماندند. نسخهٔ اولیه۲۸check این دو حالت را پوشش نمی‌داد؛ پاس نهایی۳۷ است.

اولین تلاش harness به محدودیت `strict_types` در WP-CLI eval-file برخورد کرد و پیش از fixture متوقف شد؛ declaration از driver برداشته شد. تلاش بعد نبود implementation را نشان داد. خطاهای موردانتظار و دو regression واقعی در رسید تفکیک شده‌اند؛ raw stack/SQL/نشانی‌ها خصوصی‌اند. GLM یا CLI بیرونی تازه استفاده نشد.

گام بعد: workflow انتقال۶فایل با moduleها پیش از MU loader، preflight تازه و backup/checksum، همین migration و smoke خواندنی؛ بازگشت محتوا باید پیش از حذف moduleهای جدید انجام شود. وضعیت main/PR/CI و تغییرات دیگران پیش از ادغام و apply بررسی و snapshot خصوصی لازم گرفته شود. گیت‌های مستقل رمز تاریخی، تاریخچه و Origin/OOB همچنان بازند.
