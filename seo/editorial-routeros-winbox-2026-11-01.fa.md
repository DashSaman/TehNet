# توسعهٔ درس موجود RouterOS و Winbox

بازبینی: ۱ نوامبر ۲۰۲۶. وضعیت: `VERIFIED_NATIVE_DRAFT / NOT_DEPLOYED`.

این واحد، پنج کار خوانندهٔ TN-T021 تا TN-T025 در پرتفوی را در **همان درس موجود با ID62** پوشش می‌دهد. صفحهٔ جدید، عنوان/URL تازه، محصول، Schema جدید یا ادعای آزمایش RouterOS ایجاد نمی‌کند. فایل قابل‌ویرایش گوتنبرگ: [routeros-winbox.html](../content/growth-editorial-2026-11-01/routeros-winbox.html)؛ [manifest](../content/growth-editorial-2026-11-01/manifest.json) فقط مشخصات و انتظار محتوایی را نگه می‌دارد، نه مجوز اجرای migration قبلی.

## گپ مشاهده‌شده و ارزش افزوده

`OBSERVED`: snapshot منتشرشدهٔ درس، دو دستور Backup/Export، یک دستور reset، معرفی اتصال و محدودیت کوتاه Safe Mode داشت. نمونهٔ Backup رمز نداشت؛ عبارت «کل پیکربندی» استثناهای پایگاه داده را روشن نمی‌کرد. آمادگی بازیابی، کپی خارج از روتر، تفاوت بازیابی باینری و اجرای متن، و معیار آزمون پس از بازیابی به اندازهٔ کافی توضیح داده نشده بود. SHA محتوای مشاهده‌شده در manifest است؛ بدنهٔ خام نسخهٔ پشتیبان در Git قرار نگرفته است.

`INFERENCE / تصمیم تحریری`: اصلاح همان درس به کار خواننده نزدیک‌تر از ساخت صفحهٔ هم‌نیت «تفاوت بکاپ و اکسپورت» است. نسخهٔ پیشنهادی، مثال بدون رمز و دستور مستقیم reset را کنار می‌گذارد، انتخاب Backup/Export را به هدف وصل می‌کند و سناریو و فرم پذیرش خصوصی می‌دهد. مقایسهٔ فایل و آزمون سرویس، تصمیم طراحی تمرین‌اند؛ نتیجهٔ آزمایش یا حادثهٔ مشتری نیستند. قالب آمادهٔ تمرین، زمان بازیابی، سازگاری مدل یا صحت restore را تولید نمی‌کند.

## منابع و حدود پذیرش

همهٔ منابع زیر متعلق به MikroTik و در ۱ نوامبر ۲۰۲۶ بازبینی شده‌اند (`OFFICIAL / FACT-OFFICIAL`). تاریخ انتشارِ ادعا نشده ثبت نشده است. انتخابگر راهنمای فعلی `7.26` بود؛ نسخهٔ تجهیزات کاربر یا پیشنهاد ارتقا از آن نتیجه نمی‌شود. دامنهٔ بازبینی، بخش‌های نام‌برده است، نه تمام راهنما یا تست دستگاه.

| ID | منبع و بخش خوانده‌شده | ادعای مجاز در این درس | محدودیت |
|---|---|---|---|
| MK-WINBOX-EDITORIAL | [Winbox](https://manual.mikrotik.com/docs/management-tools/winbox/)، Summary/Login/Neighbors | نسخهٔ۴ چندسیستمی، ترجیح IP در صورت امکان، کشف لایهٔ۲ و محدودیت MAC | نسخهٔ۳ legacy است؛ دانلود یا نصب واقعی در این واحد انجام نشده |
| MK-MAC-EDITORIAL | [MAC server](https://manual.mikrotik.com/docs/management-tools/mac-server/)، مقدمه و اتصال | وابستگی دسترسی MAC به لایهٔ۲ و سیاست رابط مورداعتماد | توصیهٔ تغییر زندهٔ شبکهٔ مشترک یا بازکردن دسترسی نیست |
| MK-CONFIG-EDITORIAL | [Configuration Management](https://manual.mikrotik.com/docs/getting-started/configuration-management/)، Safe Mode و Export/Import | رفتار نشست/تاریخچه، دامنهٔ export، تطبیق نسخه و اثر اجرایی import | نتیجهٔ لاب یا تضمین بازگشت نیست؛ نمونهٔ تمرین اجرا نشده |
| MK-BACKUP-EDITORIAL | [Backup](https://manual.mikrotik.com/docs/getting-started/configuration-management/backup/)، Save/Restore/Exceptions | همان دستگاه/نسخه، MAC address، کپی خارج از روتر و استثناهای Dude/User Manager | فایل باینری الگوی تضمینیِ مهاجرت بین دستگاه‌ها نیست |
| MK-SAVE-EDITORIAL | [backup save](https://manual.mikrotik.com/docs/cli-reference/system/backup/save/)، پارامترها | password برای رمزگذاری؛ dont-encrypt و الگوریتم‌ها | رمز نمونه یا دستور ذخیرهٔ رمز واقعی در مقاله ارائه نشده |
| MK-LOAD-EDITORIAL | [backup load](https://manual.mikrotik.com/docs/cli-reference/system/backup/load/)، اثر و پارامترها | load پس از تأیید reboot می‌کند | دستور مستقیم اجرایی load، آزمایش restore یا زمان بازیابی ارائه نشده |
| MK-IMPORT-EDITORIAL | [import](https://manual.mikrotik.com/docs/cli-reference/import/)، پارامترها | dry-run شبیه‌سازی است؛ پشتیبانی/نحو باید با نسخه تطبیق یابد | dry-run تأیید صحت سرویس یا تمام سخت‌افزارها نیست |

صفحهٔ دانلود رسمی فقط برای دریافت ابزار لینک شده است؛ شمارهٔ «آخرین نسخه» یا بررسی تمام changelog ادعا نشده است. متن شخص ثالث با نام شبیه مستندات رسمی منبع این واحد نیست. ویدیوی موجود حفظ شده، اما پشتیبانی تمام رفتارهای جدید یا بازبینی کامل آن ادعا نشده است.

## گیت آزمون و انتشار

پیش از انتشار باید parse/serialize و sanitization وردپرس، ثبت‌شدن بلوک‌های core، اعتبار تمام بلوک‌های تودرتوی editor، ویرایش بدون ذخیره و reset، desktop/mobile/no-JS، پیوندها و بازیابی fixture خود staging تأیید شوند. این‌ها آزمونِ انتشار محتوای وردپرس‌اند؛ جای آزمون RouterOS را نمی‌گیرند. در متن، نبود آزمون RouterOS صریح است و هیچ خروجی، عدد یا فرمان مخربِ اجراشده جعل نشده است.

مسیر فعلی `ops/migrate-growth-content.php` عمداً فقط دو صفحهٔ خدمات/Lab و دو hub را می‌پذیرد؛ **برای ID62 قابل استفاده نیست**. انتشار به سازوکار محدودِ ویرایش همین صفحه، backup تازه، بررسی checksum/drift، staging، ژورنال خصوصی و rollback آزموده نیاز دارد. تا آن زمان این واحد draft است. URL/Title/H1 موجود، خانه، منو، محصولات و متای آن‌ها، سفارش/مشتری، noindex، پرداخت/ERP و MyTel باید حفظ شوند.

هدف این واحد بهبود مفید و قابل بازبینی است. در این مرحله شاهد حجم تقاضا، رتبه، ترافیک، بک‌لینک، cannibalization یا پیشنهادشدن در هوش مصنوعی نداریم. دو مشاهدهٔ محدود پرتفوی، شاهد تحقیق فنی مقاله یا برتری نسبت به رقیب نیستند.

## نتیجهٔ واقعی staging

ثبت/parse/serialize/sanitization هر۵۴بلوک core پاس؛ editor هیچ بلوک نامعتبر نداشت و ویرایش آزمایشی بدون Save و reset موفق بود.۲۱کنترل browser در۱۴۴۰/۳۷۵ و no-JS، یکH1، noindex، محدودیت قابل‌دیدن، حذف نمونه‌های قبلی، لینک مرتبط و نبود overflow/page error پاس شد.۱۴پیوند محتوایی باGET مستقل وTLS معتبر۲۰۰ و URL نهاییِ همان مقصد بودند؛ پخش ویدیو بررسی نشده و لینک موجود حفظ است. بدنهٔ موقت، کاربر و lockهای آزمون پاک و fingerprint اصلی posts/meta/users برابر شد. قبل از آزمون backup خصوصیِ مستقل verify شد. این «انتشار مقاله» یا اجرای restore روی RouterOS نیست. رسید: [editorial-routeros-draft.json](../qa/growth-2026-10-31/editorial-routeros-draft.json).

در مشاهدهٔ بصری اولیه، player بیرونیِ مسدود در staging فضای بزرگی داشت؛ از این شاهد، خرابی live نتیجه نگرفتیم. برای این درس لینک واضح همان ویدیو جای auto-load قرار گرفت و نسخهٔ نهایی دوباره آزموده شد. تاریخ ویرایشِ footer در آزمونِ body-only موقت، تاریخ قدیمی بود؛ انتشار واقعی باید post_modified معتبرِ همان به‌روزرسانی را ثبت کند.
