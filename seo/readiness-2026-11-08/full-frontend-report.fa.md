# PR94 — آزمون کامل frontend و مسیر درخواست
Reviewed:2026-11-08. **VERIFIED_FULL_FRONTEND_AND_SYNTHETIC_TICKET_NOT_DEPLOYED**. [run42492885346](https://github.com/DashSaman/TehNet/actions/runs/42492885346)، source0f3040118afed1d8e10f31606b9ad0f0f5f858ec: **۳۲۷full-frontend،۳۳native،۴unit،۵negativeHTTP،۱تیکتprivate واقعیِ fixture و حذف همان رکورد**؛ persisted option restoration و cleanup app/DB/network پاس؛ relaystopدرخواست شد ولی exitآن مستقلاً ثبت نشد. [رسید کامل و labelها](full-frontend-verification.json). همهٔ اجراها روی GitHub-hosted Ubuntu، WordPress/DB ساختگی و Docker internal network بودند. برای آزمون ابری هیچ سیستم/فایل/مرورگر محلی یا داده production به کار نرفت. تشخیص production جداگانه با SSH موجود و فرمان خواندنی پس از تصریح مالک بود؛ پیکربندی همان اتصال خوانده شد، چیزی در سیستم محلی تغییر نکرد و secret به cloud/Git منتقل نشد. مالک فقط آزمون خودکار را انتخاب کرد؛۰اسکرین‌شات ساخته/منتشر/بازبینی شد.

## حدود دقیق پذیرش
قالب واقعی TehNet، CSS/JS و فونت‌های همان سورس از HTTP وردپرس سرو شدند؛ harness setContent و CSS اصلاحی کنار گذاشته شد. دو بدنهٔ کاندید8/29 با۷صفحهٔ عمومی منبعِ fixture، منو و چند صفحهٔ placeholder ساختگی استفاده شدند. خانه/فروشگاه/منو یا دادهٔ production کپی دیتابیس نشده‌اند؛ این fixture شاهد یکسانی کامل runtime production یا آمادگی انتشار نیست.

Google CAPTCHA در fixture روشن است. آزمایش مثبت فقط transport پاسخ siteverify را در MUfixture ایزوله با token تازهٔ تصادفی شبیه‌سازی می‌کند؛ WordPress handler، nonce، validation، parser/hostname/time verification و ذخیرهٔ تیکت واقعی‌اند. این **تست چالش واقعی Google، کلید live، دسترسی به Google، تحویل ایمیل یا SLA نیست**. outbound HTTP/mail/payment/cron بسته‌اند و هیچ bypass روی production نصب نشد.

بدنه29→کلیک واقعی CTA→services با context عمومی→فرم و nonce داخل FormData→ثبت از admin-post موجود→تیکت private/open با context و thread→رسید دارای شماره پیگیری بدون ایمیل/پیام خصوصی، با X-Robots-Tag و no-referrer→احراز دیتابیس→حذف فقط رکورد/رسید ساختگی آزموده می‌شود. negativeها:nonce403،context400،honeypot400،CAPTCHAخالی400 و provider-error503. شمار رکوردها بعد از این خطاها و یک موفقیت باید دقیقاً۱باشد؛ پس از cleanup۰.

روشن/تیرهٔ واقعی با localStorage و toggle، موبایل‌منوی واقعی، عرض۱۴۴۰/۷۶۸/۳۷۵/۳۲۰، فونت/CSS200، no-overflow/RTL/H1/canonical/noindex، deep-link و نبود uncaught JS error آزموده می‌شوند. حالت no-JS در markupفعلی روشن است؛ dark/no-JS قابلیت موجود نیست و PASSساختگی برای آن ثبت نمی‌شود. no-JS مسیر تماس جایگزین CAPTCHA را دارد.

## منبع noindex
[یادداشت provenance](noindex-provenance.fa.md) بین مشاهدهٔ production، source رسمی WordPress و بازتولید fixture فرق می‌گذارد. فرضیهٔ قوی blog_public=0 با publicmeta و sitemap404 سازگار است؛ ولی خواندن قطعی این option در production به علت نبود routesافزونه WPVibe و exposeنشدن در REST انجام نشد. نصب/کدگذاری روی live یا تغییر دسترسی صورت نگرفت. ابزار readonly جدید فقط برای مسیر موجود و مجاز server WP-CLI آماده است و روی production اجرا نشده. پس از تصریح تازهٔ مالک برای SSH، این مانع رفع شد: get_option واقعی production برابر0، callbackwp_robots_noindex ثبت و core sitemapfalse احراز شدند؛ [provenance به‌روز](noindex-provenance.fa.md) مرجع است. noindex تغییر نکرد.

تغییر blog_public فقط در fixture انجام و با مقایسهٔ ردیف persistedِ option_value/autoload برگشت دقیق آن احراز می‌شود. noindex زنده و تمام گیت‌های انتشار دست‌نخورده‌اند.

## موارد قبلی که پنهان نشدند
اجرای9054539/run42492583771 مسیر واقعی و۳۱۹assertion داشت، اما dark صرفاً از colorScheme تنظیم شده بود؛ قالب واقعی localStorageمی‌خواهد و بدونJSmarkupروشن دارد. آن اجرا اثبات تمام حالت‌های تیره شمرده نشد. diagnosticهم با مقایسهٔ strict نوع API بازگشت0را false ثبت کرد؛ ادعای restoreکامل از آن نشد. نسخهٔ بعد حالت واقعی را assert و به جای سست‌کردن کنترل، row persisted را مقایسه و در صورت اختلاف fail می‌کند.

## گیت‌های باقی‌مانده
نه merge و نه انتشار/noindexبرداری مجاز نشده است. scope ناشرcanonical، backup/checksum/drift/rollback تولید، احراز runtime/live producer و مجوز جدا پیش از انتشار لازم‌اند. تستUI/ثبتتیکتساختگی معیار service delivery، rank،conversion،AI citation یا parity نیست. MyTel read-only و برندPBX، inquiry-only،payment/CAPTCHA وhistory/rotation/origin حفظ‌اند. PR88 replayنشود؛۸۹–۹۱/۹۳و۹۴گیت جدا دارند.

## محدودیت سازگاری runtime
WordPressزنده7.1.4/PHP8.3.32/theme0.5.1 مستقیماً خوانده شدند؛ fixturePHP8.3.36 دارد. این اختلاف patch ثبت است؛ تطابق کامل runtime،تحویل سرویس واقعی، manualvisualreview و چالش واقعیGoogle ادعا نمی‌شوند. مالک فقط آزمون خودکار و عدم انتشار تصویر را انتخاب کرد.
