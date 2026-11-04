# اصلاح انتساب آموزش — بستهٔ نخست مأموریت۴نوامبر

وضعیت: **VERIFIED در native staging؛ هنوز در production منتشر نشده**. Issue75 و63 باز هستند؛ کل مأموریت و برابری رقابتی تکمیل نشده‌اند.

تغییر مشتری‌محور: هشت هویت موجود، بدون جابه‌جایی URL یا ساخت صفحهٔ تکراری، منبع نوشته و ویدیو را روشن می‌کنند. مقالهٔ Queue از قسمت ششم جدا و با عنوان «راهنمای تکمیلی مستقل» ارائه می‌شود. آرشیو نام‌های واقعی ضبط‌ها را نگه می‌دارد، توضیح حدسی هر قسمت و ادعای شش جلسه تا Queue حذف می‌شود. مطالب عمیق RouterOS/IP/routing حفظ شده‌اند. نمونهٔ عمومی فایروال که می‌توانست مسیر مدیریت را ببندد، به توضیح طراحی و فرمان‌های مشاهده تغییر کرده است.

## URLهای هدف، با وضعیت انتشار روشن

همهٔ این URLها اکنون وجود دارند؛ تصاویر «بعد» این گزارش از **staging** هستند و تا receipt تولید، نسخهٔ اصلاح‌شدهٔ production محسوب نمی‌شوند.

- [آرشیو MTCNA](https://tehnet.ir/learn/mikrotik/mtcna/) — ID40.
- [RouterOS/Winbox](https://tehnet.ir/learn/mikrotik/mtcna/routeros-winbox/) — ID62؛ title/body/excerpt.
- [IP/DHCP/DNS](https://tehnet.ir/learn/mikrotik/mtcna/ip-dhcp-dns/) — ID63.
- [Static Routing](https://tehnet.ir/learn/mikrotik/mtcna/static-routing/) — ID64.
- [NAT](https://tehnet.ir/learn/mikrotik/mtcna/nat-masquerade/) — ID65.
- [Firewall](https://tehnet.ir/learn/mikrotik/mtcna/firewall-basics/) — ID66.
- [Queue و عیب‌یابی](https://tehnet.ir/learn/mikrotik/mtcna/queues-troubleshooting/) — ID67؛ title/body/excerpt.
- [راهنمای انتخاب منبع](https://tehnet.ir/mtcna-learning-path/) — ID70، نوع واقعی post.

## شواهد اجرا

منبع qualifyشده: `c2373f16fd1cc3113e01a36f32d241eda2d01ee2`، پس از commit محتوایی `92ffc18`. دادهٔ عمومی قابل بررسی: [receipt پاک‌سازی‌شده](../evidence/2026-11-04/native-staging.json).

| بررسی واقعاً اجراشده | نتیجه |
|---|---|
| تطبیق خواندنی baseline production |23فایل مدیریت‌شده بدون drift؛ noindex فعال،25محصول، ERP و پرداخت بسته |
| unittest گیت محتوایی |5موفق؛ تزریق مجدد لینک ویدیو، حذف برچسب و VERIFIED بدون شاهد رد می‌شوند |
| unittest مرزهای release |28آزمون؛27موفق و1skipped برای symlink در Windows؛ native جایگزین این محدودیت تلقی نمی‌شود |
| PHP lint و parsing/KSES/registered blocks در WordPress واقعی | موفق در preflight بسته |
| native migration |42بررسی موفق:8رکورد،0صفحهٔ جدید، meta/revision محفوظ، repeat و rollback با instance تازه، رد drift و hook ناخواسته |
| مرورگر native |536بررسی موفق؛1440/375 برای همه،768 برای hub/Queue،320 بدون JS، تم روشن/تیره در حالت JS |
| مشاهدهٔ مرورگر |HTTP200، یک H1، canonical ثابت، noindex، برچسب منبع، حذف لینک منتسب و schema ویدیوی ساختگی، بدون overflow/خطای صفحه |
| cleanup | posts/meta/users/revisions و تمام فایل‌های fixture دقیقاً بازیابی؛ همهٔ runtimeهای قبلی بدون تغییر |
| ارسال فرم / production mutation |0 /0؛ این بسته آزمون درخواست خدمات جدید محسوب نمی‌شود |

### شکست‌هایی که رفع شدند

پوشهٔ قدیمی diagnostics با ACL سخت‌گیرانه سازگار نبود و مسیر طولانی Windows نیز پیش از شروع staging مشکل ساخت؛ پوشهٔ خصوصی تازه و کوتاه، بدون کاهش کنترل دسترسی ساخته شد. فرض وجود همهٔ فایل‌های نسخهٔ جدید در preview قدیمی اصلاح شد و فایل‌های fixture موقت به‌صورت هش‌دار اضافه/بازیابی شدند.

در native، متادیتای post70 برخلاف دامنه تغییر می‌کرد: هستهٔ WordPress هنگام update، `_pingme` و `_encloseme` را می‌ساخت. مطابق [کد مرجع رسمی WordPress](https://developer.wordpress.org/reference/functions/_publish_post_hook/)، مهاجرت فقط در همان فرایند CLI هوک انتشار را موقتاً کنار می‌گذارد و در finally به priority قبلی برمی‌گرداند. meta/cron و بازگشت هوک اکنون آزموده‌اند؛ برابری داده‌ها برای آسان‌شدن آزمون حذف نشده است. اجراهای ناموفق **FAILED_RESTORED** ثبت و journalهای آن‌ها نگهداری شدند.

## قبل / بعد واقعی

قبل: نسخهٔ عمومی production، مرورگر خواندنی بدون حساب. بعد: همان URL در fixture محتوایی native؛ قالب/منوی fixture ممکن است از snapshot قدیمی‌تر باشد و این تصاویر بازطراحی منو را اثبات نمی‌کنند.

| Queue، موبایل375 | پس از اصلاح در staging |
|---|---|
| [تصویر قبل](../evidence/2026-11-04/before-67-375-dark.png) | [تصویر بعد](../evidence/2026-11-04/after-67-375-dark.png) |

| آرشیو، دسکتاپ1440 | پس از اصلاح در staging |
|---|---|
| [تصویر قبل](../evidence/2026-11-04/before-40-1440-dark.png) | [تصویر بعد](../evidence/2026-11-04/after-40-1440-dark.png) |

## باقی‌مانده و گیت‌ها

هفت زیرنویس خودکار دریافت و بخش‌های منتخب بررسی شدند؛ **تماشای کامل صدا/تصویر8منبع انجام نشده** و هیچ ضبط VERIFIED نیست. قسمت5.5 زیرنویس قابل دریافت ندارد. نظر مدرس دربارهٔ تدریس‌نشدن درس تفصیلی Queue با اشارهٔ کوتاه زیرنویس قسمت6 تفکیک شده است. [ماتریس دقیق](../../seo/MTCNA_VIDEO_CONTENT_VERIFICATION_2026-11-04.fa.md) گیت بازبینی و ویراستاری را نگه می‌دارد.

گیت مخزن/CI مانع انتساب تأییدنشده در بسته می‌شود؛ هوک ذخیرهٔ همهٔ ویرایش‌های دستی admin هنوز پیاده نشده است. production پس از PR/CI، تطبیق payload با بستهٔ qualifyشده، backup تازه/checksum، drift guard و rollback انجام می‌شود. noindex، MyTel مستقل، پرداخت، CAPTCHA و گیت‌های امنیت مشترک تغییری نکرده‌اند.

قدم مستقل بعد: عمق خدمات سرور و اتصال شعب در URLهای مالک موجود، براساس [مقایسهٔ هفت دامنه](COMPETITIVE_LEADERSHIP_AUDIT_2026-11-04.fa.md)، بدون ایجاد سامانهٔ درخواست جدید. نتایج فنی این گزارش، شاهد رتبه، traffic، conversion یا commercial parity نیستند.
