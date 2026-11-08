# راهنمای واقعی WinBox —۵نوامبر۲۰۲۶

وضعیت فعلی: **DEPLOYED_VERIFIED**؛ [رسید production](../evidence/2026-11-05/winbox-core/production-verification.json) مرجع انتشار است.

## سابقهٔ پذیرش staging — پیش از انتشار

در این مرحلهٔ تاریخی، source `fedbdccffd4bda2d595bcd1136b10333be6c7f09`؛ native60، renderer16، browser1590؛ صفر ارسال فرم/تغییر production و بازیابی دقیق داده‌ها و فایل‌های staging. [رسید](../evidence/2026-11-05/winbox-core/native-staging.json).

دو مقالهٔ موجود تقویت شده‌اند:

- https://tehnet.ir/learn/mikrotik/mtcna/routeros-winbox/#winbox-real-lab —۱۴عکس: رابط‌ها، نسخه، Safe Mode/Comment/Undo، Package و Backup/Restore.
- https://tehnet.ir/learn/mikrotik/mtcna/ip-dhcp-dns/#winbox-ip-lab —۲۵عکس: Bridge، IP، DHCP Setup/lease، Snooping و ARP/MAC.

تصاویر اصلی بدون دستکاری متن/وضعیت نرم‌افزار نگهداری شده‌اند؛ کادر CSS گزینهٔ مربوط را نشان می‌دهد و کلیک تصویر، اصلِ بدون کادر را باز می‌کند. بدنهٔ مقاله قابل‌ویرایش بلوکی است؛ title/slug/excerpt/meta و نقش صفحه‌ها عوض نمی‌شود. دامنهٔ انتشار فقط۳۹PNG، یک CSS با selector مخصوص همین تصاویر و body62/63 است؛ هیچ runtime اجرایی یا صفحهٔ تازه اضافه نمی‌شود.

## لاب و شواهد واقعی

سه CHR۷٫۲۵٫۱ stable / x86_64 با QEMU/TCG قابل‌حمل و WinBox۴٫۵؛ مدیریت loopback، لینک‌های Ethernet مجازی داخلی، بدون LAN bridge/TAP/driver یا نصب hypervisor. DHCP واقعی bound و۳از۳ping داخلی؛ Undo با تأیید برگشت Comment؛ Backup رمزگذاری‌شده و Export خصوصی واقعاً ساخته شدند، load/reboot همان VM هفت پذیرش پس از بازیابی را گذراند. فرم‌های GUI Backup/Restore مشاهده شده‌اند ولی اجرای نهایی فایل‌ها از CLI خصوصی بود. Snooping با پورت untrusted=searching و Trusted DHCP=bound از سرور دوم آزمایش شد. Safe Mode پس از قطع ناگهانی، اینترنت، Windows DNS، upgrade/downgrade، Import و سخت‌افزار در این بسته آزموده نشده‌اند. [اصل۳۹عکس و metadata](../../content/winbox-guides-2026-11-05/captures.json).

## بدون تصرف دسکتاپ مالک

پس از درخواست مالک، WinBox میزبان بسته شد؛ هیچ کلیک/تایپ/فعال‌سازی پنجرهٔ میزبان یا تغییر تنظیم برق/قفل/نمایشگر انجام نمی‌شود. VM رسمی GNS3 با hash ناشر تأیید و به‌صورت headless اجرا شد؛ WinBox Linux۴٫۵ اکنون داخل Xvfb همان مهمان به R1 متصل است و تصویر واقعی framebuffer ثبت شد. ابزارهای نمایش فقط در مهمان نصب شدند. این اتصال، اجرای کامل سناریوی GNS3 نیست؛ ساخت پروژهٔ واقعی GNS3 و تصاویر درس‌های باقی‌مانده هنوز بازند.

در محصورسازی اولیهٔ پوشهٔ خصوصی، پرچم ACE فایل‌ها درست اعمال نشد و خطای دسترسی ایجاد کرد. دو پیشنهاد تعمیر گسترده در بازبینی خودکار رد شدند و اجرا نشدند. سپس فقط۶فایل مشخص لاب، با تأیید صریح مالک، برای همان هویت فعلی اصلاح شدند؛ در همین تعمیر تأییدشده هیچ ارث‌بری/گروه عمومی/Backup/حساب واقعی تغییر نکرد. فایل‌های خصوصی قدیمی دیگر محدود مانده‌اند. مقادیر، کلیدها، لاگ خام و Backup در Git نیستند؛ publication_guard و اسکن خصوصی شامل رازهای تازهٔ لاب قبل از commit/push اجرا شدند.

## قبل/بعد و پذیرش

[قبل موبایل۶۲](../evidence/2026-11-05/winbox-core/before-62-375-light.png)، [بعد موبایل۶۲](../evidence/2026-11-05/winbox-core/after-62-375-light.png)، [کادر واقعی موبایل۶۲](../evidence/2026-11-05/winbox-core/callout-62-375-light.png)، [بعد دسکتاپ۶۳](../evidence/2026-11-05/winbox-core/after-63-1440-light.png). قبل از production واقعی و بعد از staging است؛ عرض۳۷۵ یکسان ولی scroll متفاوت است. این‌ها آزمون خواندنی‌اند، نه ثبت تقاضای واقعی.

آزمون محلی operator:۳۶موفق، یک symlink به‌دلیل مجوز ویندوز skipped. Native۶۰ شامل حفظ identity/meta/revisions، drift دومین owner پیش از نوشتن اولی، rollback بدون تخریب ویرایش تازه، lock هم‌زمان و رد image/field/target نامجاز است. Renderer۱۶ و مرورگر۱۵۹۰ شامل۳۹تصویر/byte hash، RTL و عرض‌های۱۴۴۰/۷۶۸/۳۷۵/۳۲۰، تم‌ها، no-JS و کلیک واقعی full-size است. staging با شبکه داخلی و HTTP/mail/cron/payment بسته اجرا و سپس کاملاً بازیابی شد.

[سناریوی جداگانهٔ هر۹قسمت](../../content/video-production/2026-11-04/README.fa.md) لحن، متن، حرکت، گزینهٔ برجسته، مکث و زمان هدف دارد؛ هفت سناریو به پذیرش محدود این تصاویر وصل شده‌اند. صفر ضبط تازه؛ زمان واقعی و approval همچنان null. full audiovisual هشت منبع و موضوع۵٫۵ همچنان تأیید نشده‌اند؛ Queue یک مکمل نوشتاری مستقل است.

گام بعد در همان checkpoint تاریخی، که اکنون انجام شده و نباید تکرار شود: PR/CI دقیق head، مقایسهٔ artifact با source واجد staging، سپس فقط انتشار دارای backup تازه/checksum/drift/rollback و پذیرش مستقل زنده. MyTel read-only، noindex/payment و گیت‌های rotation/history/origin/launch حفظ‌اند؛ Issues63/75 باز و parity/اثر SEO نامحرز است.

## سابقهٔ گیت انتشار و ادامهٔ بدون دسکتاپ

[PR88](https://github.com/DashSaman/TehNet/pull/88) و commitهای `49c80f0`، `fedbdcc` و `2572709` push شدند؛ CI [42022049778](https://github.com/DashSaman/TehNet/actions/runs/42022049778) موفق است. بازبینی خودکار ادغام را به‌دلیل نبود تأیید صریح همین انتشار رد کرد. هیچ merge/main/deploy یا مسیر جایگزین اجرا نشد؛ تأیید ادغام و انتشار محدود از مالک درخواست شده و **NEEDS_APPROVAL** است. ناشر تازه با شرط artifact برابر، backup تازه، checksum/drift/rollback آماده ولی اجرا نشده است. گذشت زمان مجوز نیست.

تجربهٔ قابل انتقال همراه منابع رسمی فعلی Google در [-SEO PR27](https://github.com/DashSaman/-SEO/pull/27)، commit `d78f2d1` ثبت شد؛ CI [42023703979](https://github.com/DashSaman/-SEO/actions/runs/42023703979) موفق است. این PR نیز ادغام نشده و baseline71%/20 مقصد dashboard تغییری نکرده‌اند. مقاله‌های جدید، ویدیوی تازه و نتیجهٔ SEO ادعا نمی‌شود.

[WinBox واقعیِ نمایشگر مستقل](../evidence/2026-11-05/winbox-core/independent-guest-winbox.png) و [رسید محدود لاب](../evidence/2026-11-05/winbox-core/independent-lab.json) ثبت شدند. داخل GNS3 یک CHR و یک VPCS با یک لینک و بدون Cloud/NAT ساخته شدند. API Server2.2.61 با Web UI2.2.58 مشاهده شد؛ این دو شماره یکسان فرض نشوند. [فهرست پروژه](../evidence/2026-11-05/winbox-core/gns3-project-list.png) و [گراف هنگام started](../evidence/2026-11-05/winbox-core/gns3-project-started.png) واقعی‌اند؛ روتر در UI با برچسب خودکار TN-GNS3-R3 دیده می‌شود، نه برچسب فرضی R1.

خطای مسیر image اصلاح شد: path در پاسخ compute API نسبی است؛ محل واقعی از images_path تنظیمات مهمان و زیرپوشه QEMU گرفته شد. اجرای داخلی با TCG و بدون enable-kvm تأیید شد؛ RAM512 به1024MiB مطابق [توصیهٔ رسمی CHR](https://manual.mikrotik.com/docs/getting-started/installation-and-upgrade/install/chr-installation/) تغییر و readback شد، ولی boot همچنان در Load system مشاهده شد و console/ping پذیرفته نشدند. علت نهایی تعیین نشده؛ افزایش RAM «رفع‌شده» نام‌گذاری نمی‌شود. فقط دو node همان پروژه برای کاهش بار CPU متوقف شدند؛ پروژه/دیسک/تنظیم‌ها حفظ و GNS3_BOOT/PACKETS هنوز IN_PROGRESS هستند. سه CHR مستقلِ مبنای۳۹عکس، پذیرش‌های قبلی خود را دارند و با پایلوت تو‌در‌تو اشتباه نشوند.

گام مستقل بعدی: بررسی boot از همان پروژه و snapshot خصوصی موجود، بدون دوباره‌ساختن آن یا نصب hypervisor/driver/تغییر Windows؛ سپس عکس‌ها و متن واقعی درس GNS3 و پذیرش staging خودش. قواعد ادامهٔ بدون دسکتاپ در [راهنمای لاب](../labs/CAPTURE_WITHOUT_HOST_DESKTOP_2026-11-05.fa.md) است. هیچ تعمیر ACL فراتر از۶فایل، bootstrap مجدد رمز، ناشر قدیمی یا اتوماسیون متوقف‌شده تکرار نشود.

## انتشار تأییدشده و پذیرش مستقل زنده —۵نوامبر۲۰۲۶

مالک صریحاً «ادغام و انتشار محدود تأیید است» را اعلام کرد؛ گیت قبلی فقط برای همین PR88 و دامنهٔ دو درس برداشته شد. head `0d012c7` و CI42026474340 بررسی و PR88 در main با commit `69243f4bd4814b4abeea5b8deb888ec1ceb13431` ادغام شد. snapshot خصوصی قبل از sync گرفته شد. artifact تمام اعضا/فایل‌ها/tool/runtime_guard با source واجد staging `fedbdccffd4bda2d595bcd1136b10333be6c7f09` برابر بود.

ناشر تازه فقط body62/63،۳۹PNG و CSS کادر راهنما را با backup تازه/checksum، drift guard و rollback آزموده‌شده منتشر کرد. apply=40فایل/2بدنه/0صفحه و repeat=0تغییر؛ هیچ ناشر قدیمی یا تاریخچه‌ای replay نشد. همهٔ۴۰فایل عمومی با TLS و bytes دقیق پذیرفته شدند. حالت ERP/payment، CAPTCHA، noindex، theme mods، cron، دادهٔ محافظت‌شده، تصاویر/قیمت/حالت استعلام۲۵محصول و runtime سرویس‌ها حفظ شدند. خانه و فروشگاه جابه‌جا نشدند؛ MyTel production تغییر نکرد.

پذیرش مستقل مرورگر زنده: **730 بررسی موفق** در1440light،375light/dark و320no-JS، بارگذاری۳۹عکس، کادرهای متناسب، RTL/عدم overflow و کلیک واقعی عکس full-size؛0ارسال یا درخواست نوشتن. staging1590 با ماتریس گسترده‌تر و exact restore قبلی، پذیرش جداست. شش عکس زنده و [رسید sanitized](../evidence/2026-11-05/winbox-core/production-verification.json) ثبت شدند.

- [WinBox، Safe Mode و Backup](https://tehnet.ir/learn/mikrotik/mtcna/routeros-winbox/#winbox-real-lab)
- [Bridge، IP، DHCP و Snooping](https://tehnet.ir/learn/mikrotik/mtcna/ip-dhcp-dns/#winbox-ip-lab)
- [نمای موبایل واقعی WinBox](../evidence/2026-11-05/winbox-core/live-callout-62-375-light.png)
- [نمای موبایل واقعی IP/DHCP](../evidence/2026-11-05/winbox-core/live-callout-63-375-light.png)

این تأیید شامل -SEO PR27، پرداخت واقعی، حذف noindex، GNS3ِ ناپذیرفته، rewrite/force-push یا شبکهٔ مشترک نیست. GNS3_BOOT/PACKETS و full audiovisual هشت منبع/موضوع۵٫۵ باز مانده‌اند؛ صفر ضبط تازه و actual duration/approval همچنان null. صرف انتشار/تعداد تست، رقابت یا اثر SEO را اثبات نمی‌کند؛63/75 بسته نشوند. ادامهٔ مستقل از پروژهٔ GNS3 موجود و snapshot خصوصی، بدون تصرف دسکتاپ یا تغییر Windows و بدون دوباره‌ساختن محیط انجام شود.
