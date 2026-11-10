# MTCNA — گزارش پیش‌نویس‌های ۳۲ و ۴۰ — ۲۰۲۶-۱۱-۱۰ (تهران)

## مرز و پیش‌نیاز
خواندن AGENTS/HANDOFF/PROGRESS، برنامهٔ ۴۰ قسمتی، PREVIEW_INDEX، receipt تاریخی، SCREENSHOT_RUNBOOK_40 و quality-report پیش از نوشتن؛ بررسی زندهٔ WordPress `parent=40&status=draft` و صفحات publish موجود 40/62–67، و وضعیت PR82. شاخهٔ PR82 تغییر نکرد و mergeable=false باقی بود. پیش از ایجاد صفحات موجودی ۳۷ Draft، ۰ Future و دو هدف ۳۲/۴۰ بدون Draft بود.

WPVibe Free در ابتدای اجرا ۲۲/۱۰۰ مصرف و ۷۸ فراخوانی باقی داشت؛ هیچ reset استفاده نشد. اتصال Core WordPress REST برای create/readback کار کرد ولی WPVibe plugin route برای Media upload به HTTP 404 خورد؛ تکرار یا نصب افزونه انجام نشد.

## عملیات WordPress و بازخوانی مستقل

| جلسه | ID | slug | hash SHA-256 برای `content.raw` از GET فهرست `context=edit` | نتیجه |
|---|---:|---|---|---|
| ۳۲ | ۲۸۳ | `mtcna-micro-32-pptp-sstp-security-routeros7` | `c56d8073560aa1134a2c5ca4b6888df8749937bad0047b915c960c91187bc80d` | ۷۰۴۸ نویسه؛ بازخوانی موفق، `draft`، والد۴۰، ۷ تیتر H2، ۲۱ بلوک، ۳ تصویر، excerpt؛ مقایسهٔ bytewise با POST اولیه در ابزار ثبت نشد |
| ۴۰ | ۲۸۴ | `mtcna-micro-40-final-self-assessment-routeros7` | `56f0abfa51ac66e3d5e2963ae7d6e5c69b31fcd65c662cd86ef8715d8043b658` | ۶۹۵۳ نویسه؛ برابری bytewise content.raw با POST تأیید، `draft`، والد۴۰، ۷ تیتر H2، ۲۰ بلوک، ۲ تصویر، excerpt |

- جلسهٔ ۳۲ — [Edit](https://tehnet.ir/wp-admin/post.php?post=283&action=edit) و [Preview](https://tehnet.ir/?page_id=283&preview=true)
- جلسهٔ ۴۰ — [Edit](https://tehnet.ir/wp-admin/post.php?post=284&action=edit) و [Preview](https://tehnet.ir/?page_id=284&preview=true)
- این لینک‌ها از IDهای REST ساخته شده‌اند، نه تست مرورگر لاگین‌شده یا تأیید Gutenberg Editor Save.

## کنترل محتوای تصویری

تصاویر با استفاده از GitHub fetch_file(base64) باز و بصری بررسی شدند، ولی فایل جدیدی تولید نشده و لاب دوباره اجرا نشد.

- [۳۲ — 02-panel.png](https://github.com/DashSaman/TehNet/blob/content/mtcna-saturday-20261107/content/mtcna/screenshots/real-lab/2026-11-04/winbox40/lesson-32/02-panel.png): پنجرهٔ PPP Interface و جدول خالی؛ نتیجهٔ اتصال نیست.
- [۳۲ — 03-form-or-readonly.png](https://github.com/DashSaman/TehNet/blob/content/mtcna-saturday-20261107/content/mtcna/screenshots/real-lab/2026-11-04/winbox40/lesson-32/03-form-or-readonly.png): منوی New باز شده، انواع PPTP/SSTP Client نمایش داده شده؛ این تصویر فرم پرشده نیست. فریم 04 آرشیو، تکرار فریم 03 است؛ استفاده نشد.
- [۴۰ — 02-panel.png](https://github.com/DashSaman/TehNet/blob/content/mtcna-saturday-20261107/content/mtcna/screenshots/real-lab/2026-11-04/winbox40/lesson-40/02-panel.png): System Resources با نسخهٔ CHR RouterOS 7.25.1 و WinBox 4.5. پنجرهٔ Terminal در پس‌زمینه Login دارد؛ این تصویر شاهد آزمون عملی پایان دوره نیست. فریم 03 فقط Focus جابه‌جا شده؛ استفاده نشد.
- تصاویر شماتیک مجزا و صریحاً توضیح داده شده‌اند؛ هیچ شات WinBox بازسازی، جعل یا بازتولید نشد.
- تصاویر از `raw.githubusercontent.com` در Gutenberg ارجاع شده‌اند؛ WP Media Library upload=**۰**. Alt فارسی و caption با تاریخ ۲۰۲۶-۱۱-۰۴/WinBox 4.5/CHR 7.25.1 در متن هستند.

## موجودی نهایی و محدودیت‌ها

REST فهرست با والد ۴۰: **۳۹ Draft** (افزایش از ۳۷)، **۰ Future**، **۳۸ نگاشت اسمی** به ۴۰ قسمت به‌اضافهٔ Draft میراثی **۲۵۵**. ردیف‌های فاقد WordPress Draft: **۱۵،۲۶** (سخت‌افزار Wireless). علاوه بر آن، منبع جدید `02.md` هنوز فقط در GitHub است؛ Draft232 متعلق به قسمت۱ طرح ۲۴ قسمتی است و هنوز بازپایه‌سازی آن به قسمت۲ تأیید نشده است.

مالک‌های منتشرشدهٔ ۴۰ و ۶۲ تا ۶۷ خوانده و بدون تغییر مانده‌اند؛ جلسه۴۰ یک آزمون مستقل و غیررسمی است، نه تکثیر متن هاب.

**۰ درس Ready، ۰ Scheduled/Future، ۰ انتشار، ۰ لاب جدید/rollback آزموده، ۰ رسانهٔ WordPress.** تصاویر ۱۶۰تایی آرشیو برای ۲۰ درس دارای مراحل تکراری‌اند و برای هیچ‌کدام چهار گامِ کامل با Apply و recovery تأیید نشده‌اند. WiFi/RouterBOOT به سخت‌افزار سازگار نیاز دارند. برای دو درسِ تازه نیز بازبینی تخصصی، اندازه‌گیری مدت، تصاویر گام۳/۴ واقعاً اجراشده، آزمون بازیابی، Gutenberg editor-save و release gates باز هستند.

## راه بعدی
- در نوبت بعد اول سهمیه را بررسی کنید؛ سپس برای ۱۵ و ۲۶ فقط با تمایز روشن بین نوشتهٔ مقدماتی و آزمون واقعی سخت‌افزار اقدام کنید.
- تفاوت متن مستقل درس۲ با legacy Draft232 را قبل از هر ویرایش، با fresh raw/hash و تعیین canonical owner حل کنید؛ overwrite خودکار ممنوع.
- PR82، noindex، سایت MyTel، فروشگاه، پرداخت، کاربران، فرم، تم، cron و سرور RoboT دست‌نخورده بمانند. کنترل نشر مستقل است.

**این گزارش فقط وضعیت مستند آماده‌سازی Draft را بیان می‌کند؛ نه تأیید علمی، نه انتشار و نه زمان‌بندی عمومی.**
