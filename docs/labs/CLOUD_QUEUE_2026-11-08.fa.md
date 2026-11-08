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

وضعیت فعلی: **VERIFIED_SYNTHETIC_CLOUD_STAGING_NOT_DEPLOYED**. لاب واقعی و آزمون native/مرورگر/rollback روی fixture ساختگی پذیرفته شده‌اند؛ Queue/owner67 هنوز در production منتشر نشده است. PR89–91 همچنان جداگانه NEEDS_APPROVAL هستند. noindex، payment و سایر گیت‌ها حفظ‌اند.

## منابع فنی

- [Queues رسمی](https://manual.mikrotik.com/docs/firewall-and-quality-of-service/queues/) و [CLI simple](https://manual.mikrotik.com/docs/cli-reference/queue/simple/)، بازبینی۸نوامبر: مستند فعلی برچسب7.26 دارد؛ لاب روی7.25.1 جداگانه آزموده می‌شود. قاعدهٔ جهت با src/dst نسبت به Target و مشاهدهٔ واقعی بررسی شود؛ متن قدیمیِ جهت‌ها کورکورانه کپی نشود.
- [WinBox رسمی](https://mikrotik.com/download/winbox):4.5؛ screenshot باید همان UI واقعی باشد، نه تصویر تولیدی یا مدل مفهومی.

## نتایج واقعی و عیب‌های باقی‌مانده

- [run42478920807](https://github.com/DashSaman/TehNet/actions/runs/42478920807): دو آزمون prompt واقعاً RED شدند؛ دو مورد دیگر پاس بودند. انتخاب آخرین prompt کامل در `prompt_state.py` اصلاح شد و هر4آزمون در اجراهای بعدی پاس شدند.
- [run42479176225](https://github.com/DashSaman/TehNet/actions/runs/42479176225)، source815b2ca: بعد از اصلاح Enter تکی، ورود هر3CHR و نسخه/هویت/5از5ping داخلی/Queue خالی/نبود FastTrack واقعاً پذیرفته شد؛ مرحلهٔ یافتن پنجرهٔ WinBox شکست خورد،0capture و همهٔ فرایندها متوقف شدند. این پذیرش شبکه است، نه GUI/Queue.
- [run42479599995](https://github.com/DashSaman/TehNet/actions/runs/42479599995)، sourced5e74ba: ورود سه دستگاه پاس، ولی5ping اولیه نپذیرفت؛ دادهٔ دقیق شمارش در آن نسخه صادر نشده و علت قطعی نیست. این شکست حذف یا موفق شمرده نمی‌شود. نسخهٔ بعد warm-up جدا برای adjacency و ثبت تعداد واقعی آزمون مستقل دارد؛ نتیجه هنوز در انتظار اجراست.
- هیچ body سایت، تصویر production یا فایل محلی تغییر نکرده است. تأیید انتشار تصاویر ساختگی به معنی مجوز merge/deploy PR93 یا PR89–91 نیست.

## پذیرش واقعی کامل لاب

[run42483186544](https://github.com/DashSaman/TehNet/actions/runs/42483186544)، source4d5c3ba: ساخت از GUI، Target و64k/128k، شمارنده‌ها، Disable/Enable، حذف محدود،5/5ping پایانی و حفظ مدیریت پذیرفته شد؛ هر12PNG واقعی بازبینی بصری و hash مستقل تطبیق شد. [receipt کامل](../evidence/2026-11-08/cloud-queue/lab-verification.json) همان خروجی runner را با وضعیت اولیهٔ آن حفظ می‌کند و review را جدا ثبت می‌کند. تمام فرایندهای همان run متوقف شدند.0تغییر production و0ویدیوی تازه.

آزمون‌های8واحد پاس‌اند؛ قالب واقعی `64k/128k` در [run42481806376](https://github.com/DashSaman/TehNet/actions/runs/42481806376) یک RED واقعی داشت و اکنون با معنای64000/128000 پذیرفته می‌شود؛ سقف معکوس/صفر/خراب رد می‌شود.

تلاش نرخ جداگانه: بدون PTY مقدار قابل parse نداد؛ با PTY timeout شد؛ as-value نرخ عددی معتبر نداد. علت قطعی BTest ثابت نشده؛ **receive-rate/throughput NOT_QUALIFIED**. با مبدأ صریح، baseline هر دو سمت20/20 شد. آزمایش100ms با صف، missing reply نشان داد ولی Dropped=0/0 بود؛ این دو به هم نسبت داده نمی‌شوند. آزمایش کم‌بار250ms در run42482843251، با صف فعال20/20 و RTT حدود2ms داشت و assertion انتظار اثر شکست خورد؛ این شاهد مخالف پنهان یا موفقیت نرخ شمرده نمی‌شود. پذیرش نهایی، بار یکسان100ms قبل/فعال/غیرفعال/دوباره‌فعال را مقایسه می‌کند؛ RTT فقط میانگین پاسخ‌های رسیده است. همهٔ countها/افت‌ها در receipt اصلی آمده‌اند.

در workflow اولیه، synchronize کل diffِ PR را دوباره ارزیابی می‌کرد و حتی docs می‌توانست job را cancel کند. دو workflow اکنون push-triggered و محدود به شاخه و مسیرهای اجرایی‌اند؛ README و گزارش‌ها لاب را تکرار نمی‌کنند. تغییر فایل اجرایی همچنان می‌تواند job هم‌نام قبلی را cancel کند؛ بدون receipt پذیرش، canceled را موفق نشمارید. نسخهٔ۱۲عکس ذخیره‌شده فقط به run/source معرفی‌شده تعلق دارد و rerun جای hash این مجموعه را نمی‌گیرد.

[بستهٔ راهنما](../../content/queue-winbox-cloud-2026-11-08/README.fa.md)، [سناریوی هدف۶دقیقه‌ای](../../content/video-production/2026-11-08/09-simple-queue-cloud.fa.md) و scope محدود در همان operator/migrator موجود آماده و در fixture ساختگی آزموده‌اند؛ ضبط تازه۰ و زمان واقعی/تأیید ویدیو null است. وضعیت merge/deploy همچنان NEEDS_APPROVAL پس از qualification؛ انتشار تصاویر در Git همان انتشار روی سایت نیست.


## پذیرش نهایی WordPress و WooCommerce
[run42489095686](https://github.com/DashSaman/TehNet/actions/runs/42489095686)، source683830a2696e471eff7e6969083465b68111a728: native۵۲/renderer۸/before۴/after۵۱۸، exact-boundary۵،۱۳فایل/repeat۰ و rollback تکرارپذیر پاس شدند. [رسید اصلی و review جدا](../evidence/2026-11-08/cloud-queue/native-staging.json) و [گزارش تحویل](../reports/QUEUE_CLOUD_2026-11-08.fa.md) مرجع‌اند.

Runtime fixture: WP7.1.4/PHP8.3.36/MariaDB11.4.13، Playwright1.56.1؛ WooCommerce11.2.1/Core0.3.1/Store0.7.0 فعال. چهار probe خروجی HTTP/mail/payment/cron را بسته تأیید کردند. schema/دادهٔ واقعی سایت منتقل نشد؛۲۵محصول fixture صریحاً ساختگی و draft هستند، نه موجودی/قیمت منبع. ERP/sandbox خاموش‌اند. [مشاهدهٔ read-only و sanitized سایت](../evidence/2026-11-08/cloud-queue/production-runtime-observation.json) فقط نسخهٔ افزونه/قالب را احراز کرد؛ WP/PHP/DB production نامعلوم و تطابق کامل runtime نامحرز است.

fixture بدون Woo قبلاً پاس بود و با سایت یکسان شمرده نشد. اولین تلاش با Woo در [42488843981](https://github.com/DashSaman/TehNet/actions/runs/42488843981) به IDهای fixture برخورد کرد؛ شرط exact-owner حفظ و ترتیب ساخت fixture پیش از activation اصلاح شد. در مرحلهٔ قبلی هم API option-value یک‌بار integer و بار دیگر string داد؛ snapshot persisted row جای مقایسهٔ نوع API را گرفت و کنترل‌ها حذف نشدند. Apache داخل app آماده ولی published host-loopback بسته بود؛ browser در namespace همان app با relay خصوصی loopback اجرا شد و Docker internal باقی ماند.

همهٔ۵تصویر frontend با hash مستقل بازبینی و ذخیره شدند؛ همگی فقط fixture ساختگی‌اند. canonical rollback ردیف‌های fixture، گزینه‌های محافظت‌شده و درخت فایل/پوشهٔ آزمون را برگرداند؛ backup checksum پاس، SQL disaster-recovery کامل اجرا نشده است. تمام relay/container/network همان job حذف شدند؛۰ارسال فرم/تغییر production/دسترسی محلی.

[درس قابل انتقال -SEO](../../seo/lessons/2026-11-08-cloud-queue-evidence.fa.md) فقط برای بازبینی آماده است، نه ادغام مرکزی یا شاهد رتبه/ترافیک/AI citation. PR93 و PR89–91 همچنان به گیت جداگانهٔ merge/production نیاز دارند.
