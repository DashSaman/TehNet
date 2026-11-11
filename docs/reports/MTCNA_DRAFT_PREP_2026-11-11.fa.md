# گزارش آماده‌سازی پیش‌نویس‌های MTCNA — ۲۰۲۶-۱۱-۱۱

## دامنهٔ مأموریت
قرارداد `AGENTS.md`، `HANDOFF.md`، `PROGRESS.md` و برنامه، فهرست، رسید تاریخی، `SCREENSHOT_RUNBOOK_40.fa.md` و QA آرشیو تصاویر در `content/mtcna-saturday-20261107` خوانده شدند. این کار فقط پیش‌نویس‌های خصوصی دورهٔ TehNet زیر والد WordPress 40 را پوشش می‌دهد. روی شاخهٔ مستقل `content/mtcna-prep-20261111-wireless15-26` از checkpoint آماده‌سازی ۱۰ نوامبر ثبت شد؛ PR82 دست نخورده ماند.

## مبنای زندهٔ REST
WPVibe Free در آغاز **۰ از ۱۰۰** فراخوانی ۲۴ساعته مصرف‌شده گزارش داد؛ اتصال `tehnet.ir` برقرار بود. هیچ Usage Reset مصرف نشد. پیش از نوشتن، `GET /wp/v2/pages?status=draft&parent=40&per_page=100&context=edit` تعداد **۳۹** Draft مستقل نشان داد؛ Draft مشخص برای ۱۵ و ۲۶ وجود نداشت. مالک‌های عمومی 40 و 62–67 همه `publish` و مستقل بودند؛ هیچ‌کدام ویرایش نشدند.

## دو پیش‌نویس تازه
| جلسه | موضوع | شناسه | نتیجهٔ بازخوانی raw |
|---|---|---:|---|
| ۱۵ | Wireless Bridge، Station Bridge و آزمون شفافیت لایهٔ دو | **285** | Draft، parent 40، slug و excerpt بازخوانی؛ `content.raw` = **۷۷۵۶** نویسه، ۷ H2 و ۲۶ بلوک؛ تطبیق bytewise با متن POST اولیه جداگانه ثبت **نشده** |
| ۲۶ | WiFi Access List و Registration، Signal و بازگشت امن | **286** | Draft، parent 40، slug و excerpt بازخوانی؛ `content.raw` = **۹۰۷۰** نویسه، ۸ H2 و ۳۱ بلوک؛ **برابری bytewise محتوای خام و excerpt با POST** تأیید شد |

- جلسهٔ ۱۵: [Edit](https://tehnet.ir/wp-admin/post.php?post=285&action=edit) / [Preview](https://tehnet.ir/?page_id=285&preview=true)
- جلسهٔ ۲۶: [Edit](https://tehnet.ir/wp-admin/post.php?post=286&action=edit) / [Preview](https://tehnet.ir/?page_id=286&preview=true)
- این نشانی‌ها از پاسخ شناسهٔ واقعی REST گرفته شده‌اند. باز شدن در مرورگر واردشدهٔ مدیر و ذخیرهٔ مستقل Gutenberg هنوز آزموده نشده است.

هر دو درس محتوای متفاوت با عنوان و slug یکتا، H2 فارسی، فرمان‌های فقط‌خواندنی با برچسب «نمونه» و «انتظار»، مراحل پیشنهادی WinBox 4.5، معیار پذیرش/بازگشت، excerpt، پیشنهاد Meta Description، پیوندهای داخلی به هاب و WinBox و منابع رسمی MikroTik دارند. هیچ دستور تنظیم‌کنندهٔ خطرناک، Credential یا IP تولیدی در نمونه‌ها قرار نگرفت.

## تصاویر و صداقت فنی
در هر پیش‌نویس فقط **دیاگرام شماتیک موجود** `content/mtcna/assets/wireless-lab.webp` با alt و caption فارسی و هشدار «تصویر واقعی WinBox نیست» درج شده است. هیچ تصویر جدید تولید یا جعل نشد؛ اسکرین‌شات‌های آرشیو مخصوص درس‌های رادیویی واجد مراحل چهارگانه نیستند. **۰ تصویر واقعی در WordPress Media Library آپلود شد**؛ مسیر WPVibe upload_media در روزهای قبل با ۴۰۴ مواجه شده بود و در این اجرا تکرار نشد.

منابع رسمی بررسی‌شده:
- https://manual.mikrotik.com/docs/wireless/wifi/
- https://manual.mikrotik.com/docs/wireless/abgn/wireless-interface/
- https://manual.mikrotik.com/docs/wireless/wifi/configuring-repeater/

عکس‌های واقعی WinBox 4.5 با RouterBOARD/Radio سازگار، فرم پُرشده، Apply/OK، Registration/Bridge/Counter قبل و بعد، Undo و بازبینی فنی **همگی NOT_RUN / NOT_CAPTURED** هستند. CHR بدون رادیو راه‌حل معتبر نیست.

## موجودی نهایی
- بازخوانی مجدد فهرست `status=draft&parent=40`: **۴۱ Draft یکتا** (افزایش از ۳۹).
- REST `status=future&parent=40`: **۰**.
- برای هر یک از ۴۰ ردیف دوره Draft اسمی قابل ارجاع وجود دارد، ولی **Draft232 هنوز محتوای میراثی درس ۱ از دورهٔ ۲۴جلسه‌ای است و نمی‌توان آن را محتوای تأییدشدهٔ جلسهٔ ۲ جدید دانست.** بنابراین **۳۹ ردیف با موضوع هدف نگاشت اسمی معتبرتر دارند**، یک محتوای مستقل `02.md` همچنان فقط GitHub است؛ Draft255 میراثی خارج از نگاشت حفظ شد. هیچ ID قبلی حذف/overwrite نشد.
- READY=0، SCHEDULED=0، public write=0، RouterBOARD lab=0، media upload=0، reset usage=0.
- کیفیت آرشیو: ۱۶۰ تصویر واقعی خام، ۱۲۷ نمای متمایز، ۲۰ درس تکراری/ناقص، **۰ درس با چهار مرحلهٔ تأییدشده**.

## دلیل پایان این نوبت و اقدامات بعدی
دو درس مجازِ این نوبت تهیه و readback شدند. تکمیل استاندارد تصویری به سخت‌افزار رادیویی مستقلِ مجاز و آزمون Rollback، سنجش واقعی مدت ۱۰–۱۵ دقیقه و تأیید تخصصی نیاز دارد. پیش از هر اصلاح Draft232، باید `content.raw` و هش تازه، عدم drift، canonical owner و تطبیق با `02.md` تعیین شوند؛ ویرایش کورکورانهٔ ID قدیمی ممنوع است. سپس ذخیرهٔ Gutenberg و مسیر Preview با حساب مدیر آزمایش شود. پس از تبدیل واقعی همهٔ ۴۰ قسمت به پیش‌نویس‌های منسجم با readback و index کامل، شرط غیرفعال‌سازی اتوماسیون جداگانه بررسی شود. در وضعیت کنونی **اتوماسیون آماده‌سازی فعال می‌ماند**.

PR82 در بررسی زنده `open / mergeable=false / merged=false` بود. noindex، MyTel، فروشگاه، پرداخت، تم، کاربران، فرم‌ها، cron، شبکه، Docker، سرور مشترک RoboT و اتوماسیون مستقل انتشار بدون تغییر ماندند.
