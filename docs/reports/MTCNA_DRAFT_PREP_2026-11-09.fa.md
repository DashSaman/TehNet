# گزارش آماده‌سازی خصوصی MTCNA — ۹ نوامبر ۲۰۲۶

**نتیجه: ۳۷ Draft وردپرس برای والد ۴۰، شامل ۳۶ درس نگاشت‌شده و یک Draft میراثی ID255؛ ۴ درس فقط GitHub؛ ۰ future؛ ۰ انتشار.**

## مسیر بررسی و منابع

- بر اساس AGENTS.md، HANDOFF.md، PROGRESS.md، ROADMAP.md، TASKS.md و طرح پلتفرم، به‌علاوهٔ `content/mtcna/microcourse-drafts/PREVIEW_INDEX.fa.md`، برنامهٔ ۴۰جلسه‌ای، receipt تاریخی و `SCREENSHOT_RUNBOOK_40.fa.md` در `content/mtcna-saturday-20261107`.
- کنترل QA واقعی موجود: ۱۶۰ تصویر اصلی از WinBox4.5/CHR7.25.1 با ۱۲۷ نمای متفاوت و ۲۰ درس دارای تکرار/نقص؛ صفر درس با شواهد کامل چهارگانه. هیچ QEMU جدید یا تماس با RoboT انجام نشد.
- سهمیهٔ WPVibe در ابتدای بررسی **۲۷/۱۰۰** و پس از عملیات **۳۳/۱۰۰** بود، بنابراین محدودیت روزانه مانع کار نبود. Usage Reset مصرف نشد.
- موجودی قبل از عملیات، از core WordPress REST با `parent=40&status=draft&per_page=100&context=edit`، **۳۵ Draft** بود. اولین پنج ID: ۲۸۰، ۲۷۸، ۲۷۶، ۲۷۵، ۲۷۲.

## دو صفحهٔ جدید — فقط Draft

| درس | عنوان مستقل | شناسهٔ REST | کنترل خام | لینک ویرایش / پیش‌نمایش |
|---:|---|---:|---|---|
| ۲۸ | PCQ، Classifier و تقسیم پهنای باند در RouterOS7 | ۲۸۱ | وجود raw=۸٬۳۳۳ نویسه؛ H2×۷، کد×۲، لینک دو تصویر حقیقی و شماتیک، status/parent/excerpt تأیید؛ برابری SHA-256 payload جداگانه ثبت نشده | [Editor](https://tehnet.ir/wp-admin/post.php?post=281&action=edit) / [Preview](https://tehnet.ir/?page_id=281&preview=true) |
| ۳۰ | PPP Profile، Secret و Pool در RouterOS7 | ۲۸۲ | raw=۹٬۰۰۵ نویسه؛ **برابری کامل رشتهٔ raw با payload ارسالی**، title/slug/parent/status/excerpt و تصاویر تأیید | [Editor](https://tehnet.ir/wp-admin/post.php?post=282&action=edit) / [Preview](https://tehnet.ir/?page_id=282&preview=true) |

هر دو صفحه Persian Gutenberg، H2 کاربردی، نمونهٔ Command مستقل با برچسب انتظار و NOT_RUN، Topology، Rollback پیشنهادیِ آزموده‌نشده، منابع رسمی، پیوندهای داخلی و excerpt دارند. توضیح متا فقط در کامنت پیشنهادیِ محتوا قرار دارد؛ ثبت در فیلد اختصاصی افزونهٔ SEO ادعا نشده است. تصاویر با alt فارسی و caption شامل WinBox Linux 4.5 / RouterOS 7.25.1 / تاریخ ۲۰۲۶-۱۱-۰۴ لینک شده‌اند. دو تصویر واقعیِ خام هر درس به نتیجهٔ Apply و تغییر Counter تعبیر نشده‌اند و عکس شماتیک نیز به‌صراحت نمودار نام دارد.

همچنین صفحهٔ [درس ۲۳، ID280](https://tehnet.ir/wp-admin/post.php?post=280&action=edit) که در اجرای ۸ نوامبر raw-empty نامشخص داشت، از مسیر GET فهرستیِ `context=edit` دارای raw=۹٬۳۰۳ نویسه و H2های آموزشی بازخوانی شد. **این کار ثبت صحت وجود بدنه است، نه بازسازی هش اولیه.** در این اجرا ID280 تغییر نکرد.

## شکست‌های ثبت‌شده و حدود

- GET منفرد `/wp/v2/pages/280` به‌صورت `{}` و GET غیرپدر با `include=280` به‌صورت `[]` پاسخ داد؛ اما GET فهرست با `parent=40&status=draft&context=edit` بدنهٔ raw واقعی را بازگرداند. به همین دلیل برای کنترل از فهرست احراز‌هویت‌شده استفاده شد، نه قضاوت بر مبنای `{}`.
- فقط **یک تلاش** برای بارگذاری فایل آرشیوی درس ۲۸ از URL GitHub به Media Library شد: `upload_media` پاسخ 404 برای مسیر افزونهٔ WPVibe داد. افزونه نصب/تغییر داده نشد؛ تلاش مجدد نشد؛ **صفر Media Attachment جدید تأییدشده**. تصاویر فعلاً external embedded از GitHub هستند و رندر گرافیکی محرمانهٔ پیش‌نمایش در wp-admin آزموده نشده است.
- فایل‌های WinBox در لاب قبلی اصلی و واقعی‌اند، اما QA اثبات گام‌های آموزشی، کارکرد PCQ یا PPP، سرعت، Apply، Counter یا Rollback نیستند. WinBox4.5 و RouterOS7.25.1 مربوط به تاریخ ثبت عکس‌اند، نه ادعای اجرای تازه.
- مستندات help.mikrotik.com در بررسی ۹ نوامبر پیام «سایت آرشیوی» نشان می‌دهند؛ لینک مرجع تازه `https://manual.mikrotik.com/docs/introduction/` در متن آمده است.
- هیچ تغییر عمومی، Scheduled، کاربر، noindex، فروشگاه، MyTel، قالب، پرداخت، Cron، Docker، شبکه، credential یا فایل سرور اجرا نشد.

## پایان‌سنجی و گام بعد

GET دوبارهٔ وردپرس برای والد ۴۰: **۳۷ Draft، ۰ future**. درس‌های فقط GitHub: **۱۵، ۲۶، ۳۲، ۴۰**. یک Draft میراثی ID255 جدا برای تعیین مالک باقی است و با حذف/بازنویسی تصحیح نشده است. موضوعات ۲۸ و ۳۰ باید از نظر هم‌پوشانی با Draftهای قدیمی ۲۵۱/۲۵۲ بازبینی شوند، بدون اینکه محتوای قبلی دستکاری شود؛ تکرار با مالکان منتشرشدهٔ ۴۰ و ۶۲–۶۷ نباید به URL منتشرشدهٔ تازه تبدیل شود. PR82 همچنان `open` و `mergeable=false` مشاهده شد. تغییرات فقط در شاخهٔ مستقل `content/mtcna-prep-20261109-restverified-28-30` ثبت شدند.

**هیچ درس READY یا SCHEDULED نیست**: چهار مرحلهٔ معتبر از لاب مجاز، عکس با Apply واقعی و Counter، آزمون برگشت، تست زمان و نتیجه، بازبینی فنی، Gutenberg UI save و گیت مالکیت canonical همگی در انتظارند. تا تکمیل واقعی ۴۰ Draft و فهرست preview، اتوماسیون آماده‌سازی نباید غیرفعال شود؛ اتوماسیون انتشار مستقل دست‌نخورده است.
