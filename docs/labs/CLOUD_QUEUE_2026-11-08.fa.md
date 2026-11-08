# لاب Queue ابری — ۸ نوامبر ۲۰۲۶

## دامنه و محل اجرا

شاخه `lab/cloud-queue-20261108` و [PR93](https://github.com/DashSaman/TehNet/pull/93) فقط لاب/شواهد تازه را آماده می‌کنند. هیچ اجرای محلی، مرورگر متصل، SSH به production، انتشار سایت، merge خدمات یا تغییر MyTel مجاز نیست.

انتخاب: GitHub-hosted `ubuntu-24.04` استاندارد در همین مخزن عمومی. [مستندات runner](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job) اجرای استاندارد مخزن عمومی را رایگان و هر job را VM تازه معرفی می‌کند. از larger/self-hosted runner، cache و artifact upload استفاده نمی‌شود؛ [logs و summary در سهمیه artifact حساب نمی‌شوند](https://docs.github.com/en/billing/concepts/product-billing/github-actions). این نتیجه برای همین گزینه است، نه تضمین رایگان‌بودن هر خدمت ابری.

## کنترل‌ها

- `contents: read`، checkout بدون persist-credentials، timeout25دقیقه؛ هر فرایند در finally بسته می‌شود.
- فایل/رمز/دیسک/backup محلی یا production منتقل نمی‌شود. مهمان‌ها کاملاً تازه، با credential تصادفی و پنهان‌شده در log هستند؛ این کار چرخش credential تاریخی نیست.
- CHR فقط TCG/نمایشگر خاموش، NIC مدیریت restrict=on و listenهای loopback، لینک‌های داده socket داخلی. WinBox/Xvfb فقط در VM میزبان GitHub اجرا می‌شود؛ Xvfb روی TCP گوش نمی‌دهد.
- RouterOS7.25.1 و WinBox4.5 با hash نسخهٔ پذیرفته‌شده pin می‌شوند؛ نسخهٔ واقعی QEMU از runner خوانده می‌شود.
- bootstrap [run42478063766](https://github.com/DashSaman/TehNet/actions/runs/42478063766) واقعاً موفق شد؛ guard مربوط نیز موفق است. این پذیرش نصب پیش‌نیاز است، نه آموزش Queue.

## استثنای مشخص اسکن

مالک صریحاً برای همین شاخه تأیید کرد فهرست denied-value قدیمی روی سیستم ممنوع‌الوصول خوانده/منتقل نشود؛ اسکن آن **NOT_RUN** است. اسکن الگوی اسرار روی source تازه و publication_guard ابری جایگزین محدود این شاخه است. private main/history/rotation/origin یا شاخه‌های دیگر تأیید نمی‌شوند؛ از این استثنا برای افشای مقدار قدیمی استفاده نشود.

## تصاویر و صداقت شواهد

نسخهٔ اولیهٔ export پیکسل به لاگ عمومی در auto-review رد شد؛ علت نبود تأیید صریح همان مقصد بود. نسخهٔ نخستِ پذیرفته‌شده فقط metadata تصویر (نام، اندازه، hash) صادر می‌کرد و پیکسل‌ها در پایان job حذف می‌شدند. سپس مالک صریحاً انتشار فقط تصاویر تازهٔ همین لاب ساختگی در لاگ عمومی PR93 و PNG در همین مخزن را تأیید کرد. export تازه فقط همین دامنه را دارد؛ هیچ عکس محلی/رمز/دادهٔ مشتری یا production مجاز نیست. پیش از پذیرش عکس، UI واقعاً بازبینی شود.

سه CHR تازه قرار است مسیر رفت/برگشت را بدون NAT روی آدرس‌های مستنداتی RFC5737 بسازند. baseline واقعی، Target و جهت‌ها، Max Limit، counter/اثر، Disable/Enable، برگشت و حفظ مدیریت باید واقعاً پذیرفته شوند. افزایش counter به‌تنهایی اثبات نرخ یا ظرفیت شبکه مشتری نیست.

وضعیت فعلی: **BOOTSTRAP_VERIFIED؛ ACTUAL_LAB_PROBE_IN_PROGRESS**. Queue/owner67 هنوز staging-qualified یا منتشرشده نیست. PR89–91 همچنان جداگانه NEEDS_APPROVAL هستند. noindex، payment و سایر گیت‌ها حفظ‌اند.

## منابع فنی

- [Queues رسمی](https://manual.mikrotik.com/docs/firewall-and-quality-of-service/queues/) و [CLI simple](https://manual.mikrotik.com/docs/cli-reference/queue/simple/)، بازبینی۸نوامبر: مستند فعلی برچسب7.26 دارد؛ لاب روی7.25.1 جداگانه آزموده می‌شود. قاعدهٔ جهت با src/dst نسبت به Target و مشاهدهٔ واقعی بررسی شود؛ متن قدیمیِ جهت‌ها کورکورانه کپی نشود.
- [WinBox رسمی](https://mikrotik.com/download/winbox):4.5؛ screenshot باید همان UI واقعی باشد، نه تصویر تولیدی یا مدل مفهومی.

## نتایج واقعی و عیب‌های باقی‌مانده

- [run42478920807](https://github.com/DashSaman/TehNet/actions/runs/42478920807): دو آزمون prompt واقعاً RED شدند؛ دو مورد دیگر پاس بودند. انتخاب آخرین prompt کامل در `prompt_state.py` اصلاح شد و هر4آزمون در اجراهای بعدی پاس شدند.
- [run42479176225](https://github.com/DashSaman/TehNet/actions/runs/42479176225)، source815b2ca: بعد از اصلاح Enter تکی، ورود هر3CHR و نسخه/هویت/5از5ping داخلی/Queue خالی/نبود FastTrack واقعاً پذیرفته شد؛ مرحلهٔ یافتن پنجرهٔ WinBox شکست خورد،0capture و همهٔ فرایندها متوقف شدند. این پذیرش شبکه است، نه GUI/Queue.
- [run42479599995](https://github.com/DashSaman/TehNet/actions/runs/42479599995)، sourced5e74ba: ورود سه دستگاه پاس، ولی5ping اولیه نپذیرفت؛ دادهٔ دقیق شمارش در آن نسخه صادر نشده و علت قطعی نیست. این شکست حذف یا موفق شمرده نمی‌شود. نسخهٔ بعد warm-up جدا برای adjacency و ثبت تعداد واقعی آزمون مستقل دارد؛ نتیجه هنوز در انتظار اجراست.
- هیچ body سایت، تصویر production یا فایل محلی تغییر نکرده است. تأیید انتشار تصاویر ساختگی به معنی مجوز merge/deploy PR93 یا PR89–91 نیست.
