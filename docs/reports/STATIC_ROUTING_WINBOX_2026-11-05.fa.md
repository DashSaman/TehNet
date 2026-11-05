# درس مسیریابی استاتیک با WinBox واقعی — ۵ نوامبر ۲۰۲۶

وضعیت: **VERIFIED_STAGING_NOT_DEPLOYED**. Source `143804e` روی شاخهٔ `feat/static-routing-winbox-20261105`؛ production source همچنان `69243f4` است و انتشار تازه **NEEDS_APPROVAL**.

## چه چیزی ساخته شد

مالک موجود ID64 (`/learn/mikrotik/mtcna/static-routing/`) بدون تغییر title/URL/excerpt/meta و بدون صفحهٔ تازه، یک بخش آموزش تصویری واقعی گرفت (`#winbox-static-route`): بدنهٔ قبلی و چهار تصویر مفهومیِ مرورگریِ آن دست‌نخورده ماندند و ده تصویر تازه از WinBox4.5 متصل به CHR7.25.1 به آن اضافه شد. دامنهٔ release دقیقاً: یک `post_content`، ده PNG تازه در `learning-media/routing-20261105/`، و متغیرهای CSS کادر راهنما (`tn-lab-shot-r1..r10`) در همان stylesheet موجود؛ صفر فایل اجرایی.

## مسیر واقعی آموزش

جدول مسیرها قبل از تغییر (فقط DAC) → ثبت شکست واقعی با ابزار Ping (`100% packet loss`، `no route to host`) → نوشتن مسیر از `IP > Routes > New` با `Dst. Address` و `Gateway` → نشان‌های `ACTIVE | STATIC` و ردیف `AS` → پذیرش با ping سالم (`0% packet loss`) → خطای رایج و بازگشت امن با `Disable` (پرچم `XS`) و `Enable` دوباره. سناریوی لاب: شبکهٔ `198.51.100.0/24` به‌صورت شبیه‌سازی‌شده روی loopback روتر دوم؛ آدرس‌ها RFC 5737؛ CLI فقط مکملِ برچسب‌خورده، نه جایگزین GUI.

## پذیرش اجراشده

- native: **50** چک (شامل مثبت/منفی: حفاظت title/excerpt/meta، ردِ scope گسترش، drift هر دو هش، تصاویر خارج از scope، hook drift، قفل ردیف، idempotency apply/rollback) — [آزمون](../../tests/static-routing-winbox-migration-native.php)
- renderer: **8** چک (۱۴ figure = ۴ مفهومی قبلی + ۱۰ تازه؛ کلاس‌ها؛ بدون VideoObject/form)
- مرورگر staging: **444** چک در 1440/768/375/320 روشن‌وتیره و 320 no-JS؛ بازشدن واقعی عکس full-size؛ هش bytes تمام ده PNG با خروجی سرویس برابر — [آزمون](../../tests/static-routing-winbox-site-readonly.cjs)
- قبل‌ازتغییر در production زنده: PASS (فقط خواندن GET)
- apply=11فایل/1بدنه/0صفحه، repeat=0، rollback کامل؛ بازیابی دقیق داده/فایل/runtime تأیید شد؛ **صفر** تغییر production و صفر ارسال فرم

رسید sanitized: [staging-verification.json](../evidence/2026-11-05/static-routing-winbox/staging-verification.json) — تصاویر قبل/بعد و کادر در همان پوشه.

## مرز محیط ضبط

هر ده عکس از framebuffer مهمان لینوکسی (Xvfb) با xdotool داخل مهمان گرفته شد؛ **هیچ** کلیک/تایپ/جابه‌جایی پنجره در دسکتاپ میزبان انجام نشد. این نشست WinBox بدون نوار عنوان OS اجرا می‌شد (تفاوت با ۳۹عکس قبلی)؛ نوار وضعیت پایین با `TN-LAB-R1 | 127.0.0.1:18291 | CHR | 7.25.1` در هر ده قاب، اتصال واقعی را نشان می‌دهد و این تفاوت در [captures.json](../../content/static-routing-winbox-2026-11-05/captures.json) ثبت شده است.

## باقی‌مانده

- انتشار production این بسته: **NEEDS_APPROVAL** (تأیید PR88 به این بسته تعمیم ندارد)
- همان گپ قبلی: nat-masquerade، firewall-basics، queues-troubleshooting بدون تصویر واقعی؛ GNS3_BOOT/PACKETS باز؛ ۹ سناریوی ضبط همچنان پیشنهادی با actual duration/approval null؛ -SEO PR27 باز؛ Issues63/75 باز
