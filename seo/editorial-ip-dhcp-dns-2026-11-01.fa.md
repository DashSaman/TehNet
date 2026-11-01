# درس موجود IP/DHCP/DNS — تحقیق و پذیرش پیش‌نویس

وضعیت: VERIFIED_NATIVE_DRAFT_NOT_DEPLOYED؛۱نوامبر۲۰۲۶. این فایل انتشار زنده نیست.

مقصد همان ID63 و [URL موجود](https://tehnet.ir/learn/mikrotik/mtcna/ip-dhcp-dns/) با عنوان/والد/متادیتای قبلی است. پنج کار TN-T001 تاTN-T005 در خوشهٔ C01 به یک درس نگاشت می‌شوند؛ پنج مقاله یا URL جدید ساخته نشده است. تقاضا/رتبه/ترافیک/AI citation اندازه‌گیری نشده و پرتفوی تاریخی۱۰۰کاندیدا تغییر شمارندهٔ انتشار نمی‌کند.

شکاف متن اصلی با native GET خواندنی تأیید شد: فقط یک recipe کوچک، مرز نامشخص DNS پاسخ‌گو، استنباط قطعی از دو ping متفاوت، و نبود تصمیم prefix/route، مرحلهٔ lease، reservation/manual-IP و شواهد تعارض. متن جدید همان مقصد را با شکل آموزشی، تصمیم مرحله‌ای، fragment غیرفعال لاب، خواندن وضعیت و پرسش کنترل‌شدهٔ DNS، برگهٔ پذیرش و CTA مرتبط پشتیبانی/میکروتیک کامل می‌کند. ویدیوی قبلی a0JMhBdNNgs به‌شکل لینک حفظ شد؛ محتوا/فرمان‌های ویدیو یا نتایج لاب تأیید نشده‌اند.

[دفتر منابع](editorial-ip-dhcp-dns-2026-11-01.sources.json) شامل۹منبع اولیه با scope/نسخه/حد است: چهاربخش MikroTik، سه Microsoft و دوRFC. انتخابگر مستندات7.26 بود، نه نسخهٔ دستگاه یا توصیهٔ ارتقا. فرمان‌های RouterOS و Windows شبکه اجرا نشده‌اند؛ طرح RFC5737 مستندسازی است و باید در لاب مجاز با طرح خصوصیِ منسجم جایگزین شود. دستورهای تغییر پیکربندی، نمونهٔ مفهومی وdisabled هستند؛ سرویس DNS پاسخ‌گو یا WAN/firewall خودکار فعال نمی‌شود.

پذیرش واقعی در [رسید draft](../qa/growth-2026-10-31/ip-dhcp-dns-draft-and-migration.json):۵۷بلوک ثبت‌شده/parse-serialize/kses،۲۱browser1440/375/no-JS و edit/reset بدون save پاس؛ موبایل دیده شد، دسکتاپ خودکار است.۱۵GET پیوند باTLS معتبر همگی200. تمام posts/meta/users، قفل و کاربر موقت به fingerprint قبل بازگشتند. scope مستقل ID63 دارای۳۷native assertion و۳۷regression خدمات قبلی است؛ نویسندهٔ هم‌زمان/foreign edit/meta hook/retention/identity/path/field/baseline/repeat/rollback بررسی شدند.۲۰unit Windows:۱۹PASS/۱SKIP به‌دلیل مجوزsymlink؛ CI جدید باید شاخهٔ POSIX را نیز اجرا کند. صفر runtime install، هشت digest محافظت‌شده ازجملهmetadata0.2.1.

NEXT: source immutable را commit و bundle کن؛ rehearsal check/apply/repeat/HTTP/rollback/repeat با baseline فعلی metadata و restore دقیق fixture، سپس PR/CI، backup تازه/checksum/drift و انتشار محدود همین body در صورت پذیرش. native acceptance را با آزمایش RouterOS یا رشد سئو یکی نگیرید. noindex/پرداخت/MyTel freeze و گیت‌های credential/history/Origin پابرجا هستند.
