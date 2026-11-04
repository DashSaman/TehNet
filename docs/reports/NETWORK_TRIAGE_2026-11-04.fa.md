# تصمیم‌یار دستی عیب‌یابی شبکه —۴نوامبر۲۰۲۶

وضعیت: **VERIFIED_STAGING_NOT_DEPLOYED**. این ابزار مبتنی بر قواعد قابل بازبینی است؛ AI، ابزار تشخیص زنده یا اتصال RouterOS نیست. هیچ تشخیص قطعی، فرمان خودکار، اطلاعات حساس، ذخیره در مرورگر یا backend موازی ندارد.

بازبینی تصویر موبایل، بازشدن textarea گزارش از وسط متن را نشان داد. probe واقعی با کد قبلی `scrollTop=473/selectionStart=706` بود؛ پس از انتقال نشانگر به ابتدای متن `0/0` و PASS شد. این شرط به پذیرش مرورگر سایت اضافه شد. نسخهٔ اصلاح‌شده با source `7d90b4b58d6186edbfab10800d53fd639a1ca9f6`، native44 و257بررسی یکپارچه دوباره qualify و تمام حالت‌های گزارش از ابتدای متن تأیید شد. رسید اولیهٔ source312d69c/236 در تاریخچه محفوظ است؛ تولید هنوز منتشر نشده است.

هفت مسیر: اینترنت، DNS، DHCP، VPN، ارتباط VLANها، NAT و Gateway. سه مرحلهٔ نشانه/دامنه/شاهد، دلیل تست پیشنهادی و بررسی بعدی دارند؛ «هنوز بررسی نشده» یک وضعیت معتبر است. گزارش متنیِ فقط‌خواندنی و JSON محلی ساخته می‌شوند؛ انتخاب مسئله یا بازگشت، شاهد/گزارش نامعتبر قبلی را پاک می‌کند. چند نمونه مستقل‌اند. گزارش خودکار به تیکت متصل نمی‌شود؛ کاربر می‌تواند خلاصهٔ مرورشده را دستی در همان فرم فعلی خدمات کپی کند. CTA با context موجود `network-support` است؛ خدمات تخصصی PBX/IVR به MyTel ارجاع دارند.

بدون JavaScript، هر هفت راهنما و پیوند درخواست قابل خواندن‌اند؛ خلاصه/دانلود تعاملی فعال نیست و این محدودیت در صفحه دیده می‌شود. فایل‌های ابزار فقط در صفحهٔ دارای shortcode بارگیری می‌شوند. رنگ‌ها از متغیرهای موجود `--tn-*` قالب گرفته می‌شوند، نه یک تم موازی.

## منابع و حدود فنی

در۴نوامبر بخش‌های مرتبطِ منابع رسمی خوانده شدند؛ این قواعد، جمع‌بندی تحریریه‌اند و تشخیص تضمینی سازنده نیستند:

- [Microsoft ipconfig](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig): نمایش تنظیمات بدون پارامتر، متمایز از release/renew. هیچ دستور تغییر آدرس پیشنهاد نشده است.
- [Microsoft nslookup](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/nslookup): پرس‌وجوی نام از DNS تنظیم‌شده؛ رفتار DNS برنامه‌ها و HTTPS با IP را یکسان فرض نکنید.
- [Microsoft ping](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ping): Echo Request/Reply و تعداد پیش‌فرض چهار؛ نبود پاسخ، به‌تنهایی خرابی Gateway نیست.
- [MikroTik DHCP](https://manual.mikrotik.com/docs/network-management/dhcp/): آدرس/lease و relay، با تمایز IPv4/IPv6.
- [MikroTik NAT](https://manual.mikrotik.com/docs/firewall-and-quality-of-service/firewall/nat/): srcnat/dstnat و نگهداری تصمیم اتصال؛ پاک‌کردن tracking یا port-forward خودکار پیشنهاد نشده است.
- [MikroTik Filter](https://manual.mikrotik.com/docs/firewall-and-quality-of-service/firewall/filter/) و [Bridging](https://manual.mikrotik.com/docs/bridging-and-switching/): مسیرهای input/forward و tagging/CPU متفاوت‌اند؛ پیکربندی عمومی کپی نشده است.
- [WireGuard peers](https://manual.mikrotik.com/docs/cli-reference/interface/wireguard/peers/): فقط نمونهٔ مستند یک پروتکل، نه سند همهٔ VPNها؛ این محدودیت کنار پیوند دیده می‌شود.

صفحات Microsoft اعلان دسترسی نیز داشتند، اما بخش‌های محتوایی فوق بازیابی شدند. چند URL حدسی MikroTik ابتدا با ابزار قابل بازیابی نبودند؛ مقصدهای نهایی از پیوندهای رسمی مستندات دنبال و خوانده شدند. selector7.26 در مستند دیده شد؛ نسخهٔ نصب‌شدهٔ مشتری یا مجوز upgrade نتیجه‌گیری نشده است. هیچ شبکه، VPN، تست ICMP، تغییر تنظیمات یا سرویس مشتری واقعاً اجرا نشده است.

## شواهد پیاده‌سازی

چهار آزمون Node برای هفت مسیر، ورودی ناشناس/prototype، حذف فیلد اضافه و استقلال گزارش موفق‌اند. در renderer واقعی WordPressِ preview بسته،38assertion و حفظ همهٔ جدول‌های DB و runtimeها تأیید شد. مؤلفهٔ دو نمونه‌ای با571بررسی مرورگر و56دانلود واقعی JSON،1440/768/375/320 دو تم و320بدون JS بررسی شد. این مرحله fixture محلیِ خروجی WordPress بود؛ سفر سایت یا انتشار production محسوب نمی‌شود. سپس نام متغیرهای CSS با قالب واقعی تطبیق و عنوان منبع VPN دقیق‌تر شد؛ پذیرش یکپارچهٔ نهایی با CSS واقعی:257بررسیِ سایت، هر7مسئله، تم‌های روشن/تیره،1440/768/375/320 و320no-JS؛ دانلود واقعی JSON و CTA تا context/nonce/action موجود موفق شد. فایل‌ها در Services نامرتبط بارگیری نشدند.

آماده‌ساز محلی ابتدا به قرارداد fd قفل و طول فرمان Windows برخورد کرد؛ هر دو پیش از عمل remote بودند. شمارندهٔ نخست WP-CLI به علت scope روش eval-file صفر بود و به‌عنوان پذیرش شمارش نشد؛ با global صحیح،38 مورد ثبت شد. فایل‌های موقت همان اجرای بومی پاک و همهٔ جدول‌ها/runtimeها برابر بودند؛ گزارش خام خصوصی باقی است.

## دامنهٔ یکپارچه‌سازی

همان Lab7 و `/lab/#network-troubleshooting`، با حفظ عنوان/URL/excerpt/meta و همهٔ محتوای قبلی. بدنهٔ زنده با ترکیب دقیق دو artifact عمومی remediation2026-10-16 و growth2026-10-31 به هش `c7ef5a3…` تطبیق شد. فقط ابزار به انتهای محتوا اضافه و یادداشت ویراستاری به انتهای کل مطلب منتقل می‌شود. scope جدید چهار فایل PHP/JS/CSS/loader و فقط post_content7 دارد؛ Home، منو،۲۵کالا، مشتری/سفارش/تیکت/پیش‌فاکتور، noindex، پرداخت، CAPTCHA و MyTel در مالکیت آن نیستند. loader پس از فایل‌های وابسته نصب و پیش از آن‌ها rollback می‌شود.

مرز scope ابتدا RED شد و پس از ثبت،31آزمون اجرا شد:30PASS/1SKIP مربوط به symlink Windows. native44 برای مهاجرت، check/apply/repeat/rollback/repeat،4فایل و1بدنه، رد Home/shortcode نامجاز/HTML خام، حفظ revision و drift/row-lock موفق شد. همهٔ داده/revision/فایل/runtime قبلی دقیقاً بازیابی شد؛0ارسال و0تغییر production. [receipt و تصاویر](../evidence/2026-11-04/network-triage/native-staging.json)، source `7d90b4b58d6186edbfab10800d53fd639a1ca9f6`. تصویر قبل، نمای Lab بدون ابزار و بعد، viewport نتیجهٔ ابزار است؛ مقایسهٔ یک viewport یکسان یا بازطراحی کل قالب نیست. گام فوری PR/CI و فقط انتشار مجاز با backup تازه/checksum/drift/rollback. تا رسید نهایی، DEPLOYED نامیده نشود. Issues63/75 باز؛ FeatureB لاب مفهومی و بازبینی کامل ضبط‌ها هنوز بازند. هیچ parity، rank، traffic، تبدیل یا نتیجهٔ مشتری ادعا نمی‌شود.
