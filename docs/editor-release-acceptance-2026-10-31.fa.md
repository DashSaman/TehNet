# پذیرش ویرایشگر و آمادگی انتشار محدود

وضعیت این checkpoint: **visual/editor تأیید؛ پیش‌بررسی خواندنی production تأیید؛ انتشار انجام نشده است.** این سند ادامهٔ `docs/service-network-readiness-2026-10-31.fa.md` است، نه جایگزین گیت‌های امنیتی مستقل.

## پذیرش واقعی ویرایشگر

هر دو صفحهٔ خدمات و Lab در clone بومیِ قبلی با شبکهٔ internal و ایمیل/HTTP/cron/پرداخت بسته باز شدند. نمای کامل دسکتاپ۱۴۴۰ و موبایل۳۷۵ بررسی شد: پاسخ200، یکH1، بدون overflow افقی و محتوای قابل‌خواندن. تصویرهای کاملِ جدید artifact مربوط به screenshot بلندِ مؤلفه در آزمون قبلی را ندارند. این بررسی امتیاز دسترس‌پذیری یا عملکرد واقعی کاربران نیست.

با کاربر editor موقت و رمز تصادفیِ خصوصی، گوتنبرگ۳۸ بلوک تو‌در‌توی خدمات و۱۸ بلوک Lab را معتبر تشخیص داد؛ صفر invalid block و صفر page error. در هر صفحه یک paragraph از مسیر واقعی block store تغییر کرد، dirty/content marker تأیید و بلوک‌های اصلی برگردانده شدند. **دکمهٔ Save آزمون نشد و هیچ صفحه‌ای از مرورگر ذخیره نشد.** ذخیرهٔ native با WP-CLI و۴۱ top-level block roundtrip شاهد جداگانهٔ قبلی است؛۵۶ شامل inner list-itemهاست و شمار محتوا یا صفحهٔ تازه نیست.

گوتنبرگ markup فشردهٔ منبع را به serialization قالب‌بندی‌شده تبدیل می‌کند؛ پس raw string اولیه با serialization برابر نبود و dirty می‌تواند پس از بازگرداندن بلوک‌ها باقی بماند. آزمون نخست این دو را اشتباه یکسان فرض کرد و fail شد. پذیرش نهایی، serialization بلوک‌های پیش/پس و حذف marker را مقایسه می‌کند؛ fingerprint مستقلِ posts/postmeta/users/usermeta پس از بستن مرورگر و cleanup نیز دقیقاً برابر شروع بود. این اصلاح assertion است، نه تغییر محتوای سایت برای پنهان‌کردن خطا.

کاربر موقت و نشست‌های او حذف شدند. قفل ویرایش فقط وقتی به همان کاربر تعلق داشت با baseline تطبیق و بازگردانده شد. در تلاش اول، ورود به dashboard یک auto-draft ساخته بود و حذف کاربر آن را trash کرده بود؛ مقایسه با SQL خصوصی، همان post/revision/meta و قفل متعلق به آزمون را مشخص کرد. پاک‌سازی فقط این ردیف‌های ثابت و محافظت‌شده انجام شد و fingerprint اصلی برگشت. تلاش نهایی مستقیم به editor رفت و cleanup مالکیت‌دار داشت؛ دادهٔ قبلی دست‌نخورده ماند.

دو timeout اولیه روی بارگذاری دارایی‌های editor ثبت شدند. فایل متوقف‌شده در خود clone200 و byte-equal بود؛ همان فایل از تونل نیز کامل دریافت شد. با مهلت متناسب، حذف navigation تکراری و cache درون همان run برای byteهای واقعیِ دارایی‌های عمومی، editor باز شد. cache شامل HTML یا REST احراز‌شده نیست؛ این آزمون سرعت production محسوب نمی‌شود. دو origin خارجیِ درخواستی editor مسدود شدند. هیچ avatar/account/CDN بیرونی آزاد نشد.

رسید: `qa/growth-2026-10-31/editor-verification.json`. منبع دقیقِ اجراشده: `tests/service-intake-editor-browser.cjs`؛ hash آن در رسید است. screenshotهای admin و اطلاعات ورود فقط در شواهد خصوصی‌اند. harness به fixtureهای clone و loopback ثابت محدود است؛ وجود ENV به‌تنهایی isolation را ثابت نمی‌کند. orchestrator خصوصی پیش از ساخت کاربر، هویت container، شبکه، guardها و backup را تأیید کرده است. این شناسه‌ها برای migration تولید کاربرد ندارند.

## پیش‌بررسی خواندنی production

main تازه fetch شد و همچنان `c05bd38` بود. دو class تیکت/B2B، فایل اصلی MU و سه فایل module جدید بررسی شدند: هر۶ مسیر live دقیقاً برابر baseline main یا مطابق انتظار غایب بودند. body دو hub Services/Lab با SHA موردانتظار manifest برابر و دو path جدید آزاد بودند.۲۵ محصول منتشرشده، صفر purchasable، noindex فعال و ERP/sandbox غیرفعال مشاهده شد. رسید `qa/growth-2026-10-31/production-preflight.json` فقط دادهٔ مناسب انتشار دارد؛ fingerprintها و هویت runtime در محل خصوصی‌اند.

این preflight اجازهٔ overwrite آینده نیست: درست پیش از اعمال دوباره hash/parent/path/marker و وضعیت protected بررسی شود. شاخه/PR هنوز deploy نیست؛ release باید۶فایلی باشد، نه sync۴۱فایلیِ clone قدیمی.

## بازیابی و گام اجرایی بعد

بازیابی تازه **VERIFIED** است: سرویس backup موجود پس از تطبیق متن کامل اجرا شد، checksum همهٔ فایل‌های فهرست‌شده تأیید و۱۰٬۰۱۶ فایل WordPress در مسیر تازه با byte اصلی مقایسه شدند. SQL در DB کاملاً جدا import و fingerprint دادهٔ۴۷ جدول business با تولید برابر شد؛ options و Action Scheduler در این مقایسهٔ پایدار نبودند، ولی در dump کاملِ بازیابی‌شده وجود داشتند. وردپرس از کپی بازیابی‌شده با URL محلی، staging/noindex و mail/HTTP/payment/cron بسته boot شد؛۲۵ محصول و صفر purchasable مشاهده شد. دو container و network داخلیِ متعلق به rehearsal پس از احراز ID/label حذف شدند. ID/start/network/port همهٔ runtimeهای قبلی و دادهٔ business تولید ثابت ماندند. preview قبلی نیز دست‌نخورده ماند. رسید عمومی: `qa/growth-2026-10-31/production-recovery.json`.

اختلاف اولیهٔ SHA script به CRLF checkout در مقابل LF فایل نصب‌شده مربوط بود؛ مقایسهٔ متن کامل و digest نرمال‌شده برابر شد. هیچ script/سرویس backup تعویض نشد. یک syntax error اولیهٔ helper پیش از هر SSH اجرا متوقف شد. استخراج نخست با بازخوانی همان عضو در gzip seekهای پرهزینه داشت؛ فقط worker با digest دقیق فرمان متوقف شد، در آن لحظه هیچ container بازیابی ساخته نشده بود و backup/کپی ناقص خصوصی حفظ شدند. اجرای نهایی streaming بود، از هر عضو یک‌بار خواند و hash فایل بازشده روی دیسک را مستقل مقایسه کرد؛ حد حجم و حداقل فضای آزاد نیز اعمال شد.

این پذیرش، بازیابی WordPress/SQL است؛ به معنی تمرین برگشت Nginx/compose/SSH/DNS، حفاظت Origin یا OOB نیست. backup/دادهٔ خام/فایل تنظیمات خصوصی‌اند. پیش از انتشار واقعی drift/تازگی backup دوباره احراز شود.

پس از نتیجهٔ بازیابی: migration محدود و idempotent با journal خصوصی، resolve کردن ID جدید همان محیط از parent/path، آزمون apply/repeat/rollback در محیط جدا، سپس release واجد گیت و public smoke. خانه، منو، دادهٔ مشتری/محصول، noindex و MyTel freeze باید با fingerprint و مشاهدهٔ متناسب حفظ شوند. اگر gate شکست خورد، FAILED/BLOCKED واقعی ثبت و کار مستقل ادامه یابد؛ گذشت زمان مجوز انتشار نیست.
