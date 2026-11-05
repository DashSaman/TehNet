# راهنمای واقعی WinBox —۵نوامبر۲۰۲۶

وضعیت: **VERIFIED_STAGING_NOT_DEPLOYED**. Source `fedbdccffd4bda2d595bcd1136b10333be6c7f09`؛ native60، renderer16، browser1590؛ صفر ارسال فرم/تغییر production و بازیابی دقیق داده‌ها و فایل‌های staging. [رسید](../evidence/2026-11-05/winbox-core/native-staging.json).

دو مقالهٔ موجود تقویت شده‌اند:

- https://tehnet.ir/learn/mikrotik/mtcna/routeros-winbox/#winbox-real-lab —۱۴عکس: رابط‌ها، نسخه، Safe Mode/Comment/Undo، Package و Backup/Restore.
- https://tehnet.ir/learn/mikrotik/mtcna/ip-dhcp-dns/#winbox-ip-lab —۲۵عکس: Bridge، IP، DHCP Setup/lease، Snooping و ARP/MAC.

تصاویر اصلی بدون دستکاری متن/وضعیت نرم‌افزار نگهداری شده‌اند؛ کادر CSS گزینهٔ مربوط را نشان می‌دهد و کلیک تصویر، اصلِ بدون کادر را باز می‌کند. بدنهٔ مقاله قابل‌ویرایش بلوکی است؛ title/slug/excerpt/meta و نقش صفحه‌ها عوض نمی‌شود. دامنهٔ انتشار فقط۳۹PNG، یک CSS با selector مخصوص همین تصاویر و body62/63 است؛ هیچ runtime اجرایی یا صفحهٔ تازه اضافه نمی‌شود.

## لاب و شواهد واقعی

سه CHR۷٫۲۵٫۱ stable / x86_64 با QEMU/TCG قابل‌حمل و WinBox۴٫۵؛ مدیریت loopback، لینک‌های Ethernet مجازی داخلی، بدون LAN bridge/TAP/driver یا نصب hypervisor. DHCP واقعی bound و۳از۳ping داخلی؛ Undo با تأیید برگشت Comment؛ Backup رمزگذاری‌شده و Export خصوصی واقعاً ساخته شدند، load/reboot همان VM هفت پذیرش پس از بازیابی را گذراند. فرم‌های GUI Backup/Restore مشاهده شده‌اند ولی اجرای نهایی فایل‌ها از CLI خصوصی بود. Snooping با پورت untrusted=searching و Trusted DHCP=bound از سرور دوم آزمایش شد. Safe Mode پس از قطع ناگهانی، اینترنت، Windows DNS، upgrade/downgrade، Import و سخت‌افزار در این بسته آزموده نشده‌اند. [اصل۳۹عکس و metadata](../../content/winbox-guides-2026-11-05/captures.json).

## بدون تصرف دسکتاپ مالک

پس از درخواست مالک، WinBox میزبان بسته شد؛ هیچ کلیک/تایپ/فعال‌سازی پنجرهٔ میزبان یا تغییر تنظیم برق/قفل/نمایشگر انجام نمی‌شود. VM رسمی GNS3 با hash ناشر تأیید و به‌صورت headless اجرا شد؛ WinBox Linux۴٫۵ اکنون داخل Xvfb همان مهمان به R1 متصل است و تصویر واقعی framebuffer ثبت شد. ابزارهای نمایش فقط در مهمان نصب شدند. این اتصال، اجرای کامل سناریوی GNS3 نیست؛ ساخت پروژهٔ واقعی GNS3 و تصاویر درس‌های باقی‌مانده هنوز بازند.

تلاش گستردهٔ اصلاح ACL به‌دلیل دامنهٔ بیش از نیاز، در بازبینی خودکار رد شد و اجرا نشد. فقط۶فایل مشخص لاب، با تأیید صریح مالک، برای همان هویت فعلی اصلاح شدند؛ هیچ ارث‌بری/گروه عمومی/Backup/حساب واقعی تغییر نکرد. فایل‌های خصوصی قدیمی دیگر محدود مانده‌اند. مقادیر، کلیدها، لاگ خام و Backup در Git نیستند؛ publication_guard و اسکن خصوصی شامل رازهای تازهٔ لاب قبل از commit/push اجرا شدند.

## قبل/بعد و پذیرش

[قبل موبایل۶۲](../evidence/2026-11-05/winbox-core/before-62-375-light.png)، [بعد موبایل۶۲](../evidence/2026-11-05/winbox-core/after-62-375-light.png)، [کادر واقعی موبایل۶۲](../evidence/2026-11-05/winbox-core/callout-62-375-light.png)، [بعد دسکتاپ۶۳](../evidence/2026-11-05/winbox-core/after-63-1440-light.png). قبل از production واقعی و بعد از staging است؛ عرض۳۷۵ یکسان ولی scroll متفاوت است. این‌ها آزمون خواندنی‌اند، نه ثبت تقاضای واقعی.

آزمون محلی operator:۳۶موفق، یک symlink به‌دلیل مجوز ویندوز skipped. Native۶۰ شامل حفظ identity/meta/revisions، drift دومین owner پیش از نوشتن اولی، rollback بدون تخریب ویرایش تازه، lock هم‌زمان و رد image/field/target نامجاز است. Renderer۱۶ و مرورگر۱۵۹۰ شامل۳۹تصویر/byte hash، RTL و عرض‌های۱۴۴۰/۷۶۸/۳۷۵/۳۲۰، تم‌ها، no-JS و کلیک واقعی full-size است. staging با شبکه داخلی و HTTP/mail/cron/payment بسته اجرا و سپس کاملاً بازیابی شد.

[سناریوی جداگانهٔ هر۹قسمت](../../content/video-production/2026-11-04/README.fa.md) لحن، متن، حرکت، گزینهٔ برجسته، مکث و زمان هدف دارد؛ هفت سناریو به پذیرش محدود این تصاویر وصل شده‌اند. صفر ضبط تازه؛ زمان واقعی و approval همچنان null. full audiovisual هشت منبع و موضوع۵٫۵ همچنان تأیید نشده‌اند؛ Queue یک مکمل نوشتاری مستقل است.

گام بعد: PR/CI دقیق head، مقایسهٔ artifact با source واجد staging، سپس فقط انتشار دارای backup تازه/checksum/drift/rollback و پذیرش مستقل زنده. MyTel read-only، noindex/payment و گیت‌های rotation/history/origin/launch حفظ‌اند؛ Issues63/75 باز و parity/اثر SEO نامحرز است.
