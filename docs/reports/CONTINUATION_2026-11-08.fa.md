> **مرجع فعلی پس از PR94v2:** [گزارش نهایی خدمات/مقالات و تصمیم index](../../seo/commercial-decision-2026-11-08-v2/report.fa.md) و [CURRENT ریشه](../../HANDOFF.md) را بخوانید. Queue در PR93 synthetic پذیرفته‌شده است؛ merge/production آن هنوز تأیید نشده. متن زیر checkpoint پیشین همین روز است، نه صف اجرای فعلی.

# سابقهٔ ادامهٔ اجرایی TehNet —۸نوامبر۲۰۲۶

## بستهٔ مستندات و شواهد

**READY_FOR_REVIEW، نه تغییر production.** مبنا fresh origin/main `69243f4` است؛ branch Queue/commit865b281 و تمام شاخه‌های قبلی حفظ شدند. پیش از fetch/switch، snapshot خصوصی status/refs/diff/چهار فایل ادامه خارج Git گرفته شد. محتویات شواهد commitc33f0b3 در همین PR وارد می‌شوند؛ hash هر6PNG با production receipt تطبیق شد. تنها یک CURRENT در هرکدام از HANDOFF/PROGRESS/TASKS وجود دارد؛ checkpointهای قبلی باقی و HISTORICAL شده‌اند. راهنمای قدیمی ادامه و ابهام staging/production گزارش PR88 تصحیح شد.

## صف انتشارِ جدا از توسعه

| بسته | head دقیق فعلی | receipt تاریخی و آزمون | وضعیت8نوامبر |
|---|---|---|---|
| [PR88](https://github.com/DashSaman/TehNet/pull/88) | merged source69243f4 | [production](../evidence/2026-11-05/winbox-core/production-verification.json)،39PNG/2body،60native/16renderer/1590staging/730live | DEPLOYED_VERIFIED؛ replay ممنوع |
| [PR89 مسیریابی](https://github.com/DashSaman/TehNet/pull/89) | 3c52cea433bb82e51d7471a7ab25f6033b714c62 | [receipt](https://github.com/DashSaman/TehNet/blob/feat/static-routing-winbox-20261105/docs/evidence/2026-11-05/static-routing-winbox/staging-verification.json)،10PNG،50native/8renderer/444browser،CI42071263335 موفق | OPEN؛ VERIFIED_STAGING_NOT_DEPLOYED؛ merge/deploy NEEDS_APPROVAL |
| [PR90 NAT](https://github.com/DashSaman/TehNet/pull/90) | 9a082fffd2376a4250a07b4e476b6fdcae970fd4 | [receipt](https://github.com/DashSaman/TehNet/blob/feat/nat-winbox-20261105/docs/evidence/2026-11-05/nat-winbox/staging-verification.json)،13PNG،50native/8renderer/555browser،CI42097636011 موفق | OPEN؛ VERIFIED_STAGING_NOT_DEPLOYED؛ merge/deploy NEEDS_APPROVAL |
| [PR91 Firewall](https://github.com/DashSaman/TehNet/pull/91) | 48b9d7a9f6df9c0157458e742b8182d40277c43d | [receipt](https://github.com/DashSaman/TehNet/blob/feat/fw-winbox-20261105/docs/evidence/2026-11-06/fw-winbox/staging-verification.json)،6PNG،50native/8renderer/296browser،CI42110423284 موفق | OPEN؛ VERIFIED_STAGING_NOT_DEPLOYED؛ merge/deploy NEEDS_APPROVAL |

CI یادشده Public repository guard است؛ receiptهای5نوامبر اجرای native/staging و exact restore/0production را ثبت می‌کنند. اعداد، اجرای تازه یا شاهد برابری رقابتی نیستند. بررسی عمومی8نوامبر:11URL با200،39تصویر دو درس موجود، فرم/nonce خانه و Services، noindex حفظ‌شده؛ sectionهای تازهٔ89/90/91 هنوز غایب. هیچ فرم production ارسال نشد. هیچ ناشر قدیمی تکرار نشود.

## ادامهٔ مستقل و مرزها

1. Queue/owner67: baseline فعلی، تنظیم GUI واقعی، جهت Target upload/download، counter/اثر، Disable/Enable و recovery؛ محدودیت CHR/TCG روشن. از checkpoint865b281 فقط به‌عنوان سابقه استفاده شود؛ دستور قدیمی خالی‌کردن جدول قبل هر capture بدون تشخیص مالکیت اجرا نشود.
2. native migration/renderer/browser، داده/فایل/runtime restore دقیق، اصل تصویر/hash و callout؛ سپس commit/PR و ادامهٔ درس‌های مستقل بعدی. وضعیت staging از production جدا بماند.
3. GNS3: آخرین boot/ping نامحرز؛ وضعیت فعلی باید خوانده شود، نه create/bootstrap مجدد.9سناریو/0ضبط تازهٔ تأییدشده؛ actual timing/approval null. full8source audiovisual و admin-save gate هنوز بازند؛ PR82 دورهٔ منتشرشده نیست.
4. -SEO PR27 باز است؛ به receipt زنده تطبیق داده شود، ادغام آن در این مأموریت فرض نشود. noindex، payment/ERP، CAPTCHA واقعی، customer consent و exact CAD گیت‌های مستقل دارند؛ نتیجهٔ SEO/lead/parity ادعا نشود.
5. MyTel read-only، ticket/inquiry موجود canonical، shop در/shop،25کالای استعلامی و امنیت/rotation/history/origin حفظ شوند. هیچ ورودی میزبان، power/lock/driver/network change، تعمیر ACL گسترده، force-push یا پیام واقعی مجاز نیست.

پس از آماده‌شدن هر بسته، اولین کار مستقل قابل انجام ادامه یابد. تأیید انتشار89–91 هنوز موجود نیست و با زمان یا دستور ادامه جایگزین نمی‌شود.
