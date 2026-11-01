# بهبود خدمت موجود MikroTik

وضعیت: VERIFIED_REHEARSAL_NOT_DEPLOYED —۱نوامبر۲۰۲۶. همان ID35، عنوان «خدمات MikroTik تهران»، URL `/services/mikrotik-tehran/` و والد8. فقط body و تاریخ واقعی تغییر؛ عنوان/slug/meta/excerpt محفوظ. محتوای native/public در01:30:20UTC با after نسخهٔ committed۱۶اکتبر، SHA647165b... منطبق بود؛ GET باTLS معتبر200.

## نیاز مستقل و مرز intent

صفحهٔ قبلی فهرست خدمات و توصیهٔ کلی Backup داشت؛ مدل/نسخه/وابستگی، هدف تغییر و معیار پذیرش را برای شروع درخواست روشن نمی‌کرد. این یک کمبود توضیحی است، نه شاهد نبود توانایی خدمت یا تقاضای سنجیده‌شده. این صفحه برای درخواست اجرای مشخص روی دستگاه است؛ درس‌های RouterOS/WinBox، IP/DHCP/DNS و Routing به‌جای تکرار لینک می‌شوند. پشتیبانی، پروژهٔ راه‌اندازی و جلسهٔ ریموت مرزهای خود را حفظ می‌کنند؛ URL هم‌نیت تازه ساخته نمی‌شود.

قالب پیشنهادی شامل اطلاعات اولیهٔ غیرحساس، تطبیق دستگاه/نسخه، وابستگی و تأییدکننده، تفاوت مشاهده/تنظیم/ارتقا/Reset، خروجی قابل قبول و پنجرهٔ بازیابی است. نمونهٔ VLAN صریحاً ساختگی و اندازه‌گیری‌نشده است؛ پیکربندی آماده یا نتیجهٔ تست VLAN/امنیت/ظرفیت نیست. هیچ دستگاه، تنظیم، Import/Reset/ارتقا، backup/restore یا تست شبکه اجرا نشده است. خرید، قیمت، موجودی یا تعهد زمانی تازه تعریف نمی‌شود.

## منابع و محدودیت واقعی

دو صفحهٔ جاری اولیه در ledger آمده‌اند: [Configuration Management](https://manual.mikrotik.com/docs/getting-started/configuration-management/)، بخش‌های Export/Import، محدودیت انتقال داده و نسخه، و Safe Mode؛ [Bridging and Switching](https://manual.mikrotik.com/docs/bridging-and-switching/)، بخش پردازش سخت‌افزاری، جدول خانوادهٔ تراشه و قطع موقت وابسته به مدل. همهٔ۵۶۵/۲۵۱۳خط یا رفتار هر مدل/نسخه بررسی نشده‌اند. انتخابگر7.26، نسخهٔ دستگاه و توصیهٔ ارتقا نیست. صفحهٔ قدیمی help.mikrotik.com پیام frozen و به‌روزرسانی2026-02-23 داشت؛ مسیر مستند جاری دنبال شد و صفحهٔ منجمد به‌عنوان منبع جاری متن استفاده نشد.

این ارجاعات محدودیت‌های فنی را پشتیبانی می‌کنند؛ قالب درخواست/پذیرش، پیشنهاد تحریریه است، نه گواهی سازنده، قرارداد تأییدشده یا نتیجهٔ اجرا. Export پنهان‌ساز همهٔ اطلاعات سازمان نیست؛ در فرم اولیه فایل کامل، رمز، کلید خصوصی و آدرس مدیریتی درخواست نمی‌شود.

## پذیرش و انتشار

scope دقیق `tehnet-service-mikrotik-20261101-v1` باID35/URI/file ثابت، صفر نصبruntime و۸guard نسخهٔ جاری. تست operator/native پیش از ثبت scope باید رد شود؛ سپس native rollback/retention/negative cases و regression، browser1440/375/no-JS/anchor/phone/editor edit-reset و بازیابی دقیق state لازم‌اند. writerهای preview ترتیبی با قفل خصوصی باشند. immutable committed bundle، backup/checksum/tamper/repeat/rollback، CI تازه و برابری payload/tool/guards، پیش‌نیاز هر انتشارند. فعلاً production تغییر نکرده است.

MyTel read-only/freeze، noindex، خانه/منو/فروشگاه، دادهٔ مشتری و۲۵کالای استعلامی/صفرقابل‌خرید وپرداخت بسته حفظ شوند. rotationUNKNOWN/historyNEEDS_APPROVAL/originUNDETERMINED/منعforce-push پابرجا؛ گزارش صبح LIVE_NOT_FINAL تا۰۸:۰۰. رتبه، ترافیک، تقاضا یا توصیهٔAI در این بسته اندازه‌گیری نشده است؛ مقاله/URL تازه صفر.

پذیرش بومی:۳۹بلوک/۳۰browser/۴۱native+۴۰remote+۳۹setup،Windows۲۲PASS/۱SKIP از۲۳،۱۵TLS200/۳anchor؛ state وکاربرQA دقیقاً بازگشتند. immutable rehearsal/CI/live هنوز در انتظارند.

تمرین immutable باsource73c72112fac967c71ea4f89c0129cf4a28f87e5a،backup/checksum/tamper/apply/repeat/۴HTTP/rollback/repeat وrestore دقیقstate/metadata fixture موفق بود؛ CI/Linux وlive هنوز در انتظارند.
