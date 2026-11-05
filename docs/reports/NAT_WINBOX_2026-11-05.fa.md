# درس NAT و Masquerade با WinBox واقعی — ۵ نوامبر ۲۰۲۶

وضعیت: **VERIFIED_STAGING_NOT_DEPLOYED**. Source `a3596e7` روی شاخهٔ `feat/nat-winbox-20261105` (از main؛ فایل‌های مشترک CSS/migratorِ بستهٔ مسیریابیِ در انتظارِ PR89 را حمل نمی‌کند)؛ production source همچنان `69243f4` و انتشار تازه **NEEDS_APPROVAL**.

## چه چیزی ساخته شد

مالک موجود ID65 (`/learn/mikrotik/mtcna/nat-masquerade/`) بدون تغییر title/URL/excerpt/meta و بدون صفحهٔ تازه، بخش تصویری واقعی گرفت (`#nat-real-lab`): سیزده عکس اصلی WinBox4.5/CHR7.25.1 + شمارنده‌ها و رکورد ترجمهٔ conntrack. دامنهٔ release: یک post_content، سیزده PNG در `learning-media/nat-20261105/` و متغیرهای CSS (`tn-nat-shot-1..13`) در همان stylesheet موجود؛ صفر فایل اجرایی.

## تفکیک مفاهیم (طبق درخواست مالک)

- **مسیریابی**: مشتری مسیر مقاصد دور را از گیت‌وی R1 می‌گیرد (`10.20.0.10` → گیت‌وی `10.20.0.1`).
- **مسیر برگشت**: R2 عمداً هیچ مسیری به `10.20.0.0/24` ندارد — همان چیزی که بدون NAT باعث timeout می‌شود.
- **NAT**: قانون `srcnat + masquerade` با شرط `Dst. Address=198.51.100.0/24` و `Out. Interface=bridge-lab`؛ رکورد Connections نشان می‌دهد پاسخ‌ها به `192.0.2.1` (آدرس NAT‌شده) برمی‌گردند و بعد de-NAT به مشتری می‌رسند.
- **conntrack در برابر قانون**: پس از Disable، pingهای جدید timeout می‌گیرند؛ جریان‌های قبلی تا پایان timeout خودشان ممکن است زنده بمانند — پاک‌سازی فقط رکورد همان جریان لاب (مقصد 198.51.100.1) از Connections انجام شد؛ نشست مدیریت دست نخورد.
- pingهای موفق، جریان داخلی لاب‌اند؛ در متن مقاله صریحاً «اینترنت یا شبکهٔ واقعی نیست» نوشته شده.

## پذیرش اجراشده

- native: **50** چک (مثبت/منفی: حفاظت title/excerpt/meta، ردِ دومین هدف، drift هر دو هش، تصاویر خارج از scope، hook drift، قفل ردیف، idempotency) — [آزمون](../../tests/nat-winbox-migration-native.php)
- renderer: **8** چک (۱۳ figure؛ کلاس‌ها؛ بدون VideoObject/form) — [آزمون](../../tests/nat-winbox-renderer-native.php)
- مرورگر staging: **555** چک در 1440/768/375/320 روشن‌وتیره و 320 no-JS؛ full-size واقعی؛ هش bytes تمام سیزده PNG — [آزمون](../../tests/nat-winbox-site-readonly.cjs)
- قبل‌ازتغییر در production زنده: PASS (GET فقط)
- apply=14فایل/1بدنه/0صفحه، repeat=0، rollback کامل؛ بازیابی دقیق داده/فایل/runtime؛ **صفر** تغییر production و صفر ارسال

رسید sanitized: [staging-verification.json](../evidence/2026-11-05/nat-winbox/staging-verification.json) — تصاویر قبل/بعد و کادر در همان پوشه.

## اصلاحات لاب حین ضبط (شفاف‌سازی)

در میانهٔ ضبط مشخص شد سناریوی اولیه یک اشکال مفهومی داشت: «LAN خصوصی» به‌صورت آدرس دوم روی همان L2 مشترک تعریف شده بود و R1 مسیر برگشت به آن را نداشت؛ پاسخ‌ها بعد از de-NAT روی R1 drop می‌شدند. لاب به چیدمان واقع‌گرایانه اصلاح شد: R1 گیت‌وی LAN خصوصی (`10.20.0.1/24` روی bridge-lab) و مشتری `10.20.0.10/24` با مسیر از همین گیت‌وی. همچنین حذف رکورد conntrack قدیمیِ همان جریان (پس از تغییر قانون) برای تمیز بودن آزمون انجام شد. این اصلاحات در متن درس هم منعکس است.

## وضعیت لاب پس از بسته

R1: قانون masquerade فعال + مسیر استاتیک 198.51.100.0/24 (از بستهٔ قبل) + آدرس 10.20.0.1/24 روی bridge-lab. R2: loopback شبیه‌ساز بدون تغییر. CLIENT: آدرس‌های 192.0.2.120 و 10.20.0.10 + مسیر pref-src دار. پنجرهٔ WinBox CLIENT در مهمان باز و متصل است (برای بسته‌های بعدی قابل استفاده).

## باقی‌مانده

- انتشار production این بسته: **NEEDS_APPROVAL** (مستقل از PR89 و PR88)
- firewall-basics و queues-troubleshooting: بسته‌های بعدی همین صف
- GNS3_BOOT/PACKETS باز؛ ۹ سناریوی ضبط پیشنهادی با actual/approval null؛ -SEO PR27 باز؛ Issues63/75 باز
