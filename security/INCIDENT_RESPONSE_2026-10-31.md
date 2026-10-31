# بررسی افشای اطلاعات — خلاصهٔ مناسب انتشار عمومی

**Observed/reviewed:2026-10-31. این گزارش پاک‌سازی کامل یا گواه نبود نفوذ نیست.** جزئیات نشانی، credential، تنظیم شبکه و دادهٔ خام در محل محدودشده با ACL خارج Git نگهداری می‌شوند. مقادیر را از diff/اسکن در chat یا گزارش عمومی بازنشر نکنید.

## دامنه و اقدام واقعی

- GitHub visibility: TehNet و -SEO عمومی، MyTel.one خصوصی؛ visibility تغییر نکرد.۳۷ مخزن قابل‌دسترسیِ مالک در inventory برگشتند؛ این عدد تعداد بررسی کامل۳۷ مخزن نیست.
- فایل‌های فعلی سه مخزن با PRهای [TehNet#33](https://github.com/DashSaman/TehNet/pull/33)، [MyTel#3](https://github.com/DashSaman/mytel.one/pull/3) و [-SEO#2](https://github.com/DashSaman/-SEO/pull/2) پاک‌سازی و ادغام شدند. tree هر origin/main با tree آزموده‌شده برابر بود. CI هر۳ موفق شد.
- نشانی عملیاتی/داخلی شناسایی‌شده، مسیر اختصاصی رایانه، دو ایمیل خصوصی و یک رمز تاریخی مرحله‌بندی‌شده حذف شدند؛۱۰۹ فایل backup/output خصوصی MyTel از index انتشار خارج شدند. اصل محلی و کپی خصوصی حفظ و با محتوای Git تطبیق داده شد؛ تفاوت CRLF checkout جدا ثبت شد. هیچ دادهٔ سایت یا مشتری برای این کار پاک نشد.
- ارزش/اعتبار رمز تاریخی هنوز نامعلوم است. آن را صرف قدیمی‌بودن بی‌خطر نمی‌نامیم. حذف متن جایگزین revoke/rotate نیست؛ مسیر حساب/وابستگی و مجوز امن لازم است. هیچ reset ایمیل، پیام مشتری یا تغییر حساب اجرا نشده و MyTel خصوصی باقی مانده است.

## بررسی خواندنیِ فراتر از فایل جاری

paginationِ issue/PR metadata، issue comment، inline review comment، release، fork، artifact و workflow run برای۳ مخزن اصلی تا پایان پاسخ API انجام شد. در این snapshot:۳۳/۳/۲ رکورد issue شامل PR،۳۳/۳/۲ PR، یک issue comment در TehNet و بدون inline comment وجود داشت.۲۴ آرشیو log در دسترس CI با محدودیت حجم باز و برای مقادیر شناسایی‌شده/الگوهای token بررسی شدند؛ هیچ match در این دامنه نبود. release، release asset، artifact و fork این۳ مخزن در زمان بررسی صفر بودند. Pages API404 و metadata has_pages=false بود؛ wiki feature برای۲ مخزن روشن است اما محتوایش هنوز بررسی جدا می‌خواهد. این نتایج شامل diffهای تاریخی PR، تصاویر/OCR و cacheهای خارج این پاسخ API نیستند.

MyTellPBX، melika و mytel-webphone به‌صورت خواندنی در کل history قابل‌دسترسی بررسی شدند:۴۹۱/۱۳۰/۲۹blob، match مقادیر شناخته‌شده و یافتهٔ Gitleaks صفر. MytellPhone هیچ ref قابل‌دسترسی نداشت. این مخازن تغییر نکردند. این دامنه، گواه نبود هر نوع اطلاعات خصوصی در تمام پروژه‌های مرتبط نیست.

## مرزهای باز

تمرین تاریخچه در کپی جدا، با bundle پشتیبان:۲۰۵۳blob برای TehNet و۱۱۸۱ برای MyTel؛ مقادیر شناسایی‌شده، مسیر شخصی و مسیرهای private evidence در خروجی تمیز باقی نماندند. این تمرین قبل از ادغام‌های جدید بود؛ snapshot/ref map پس از merge باید تازه و حفظ tree جاری دوباره تأیید شود. هیچ force-push، پاک‌سازی cache/PR/fork یا تماس با GitHub Support انجام نشده است. دستور جدید مالک، بازنویسی سابقه در غیاب او را صریحاً منع می‌کند.

بررسی خواندنی Origin با TLS verification روشن و Host/SNI صحیح آغاز شد. پاسخ بیرونیِ ظاهراً مستقیم، نشانه/گواهی متفاوت با آزمون داخلی داشت؛ بنابراین مسیر هنوز برای نتیجه‌گیری قطعی اعتبارسنجی نشده است. حفاظت یا bypass قطعی ادعا نمی‌شود. تنظیم دقیق و وابستگی سرویس‌ها خصوصی‌اند؛ OOB بازیابی تأیید نشده و شبکه/DNS/SSH/Origin تغییر نکرده است. این گیت مسدودشده، مجوز تغییر پرخطر نیست.

## اولویت بعد

۱. تکمیل wiki/رسانه‌های مرتبط و snapshot تاریخچهٔ پس از merge با procedure دقیق و حمایت از concurrency؛ وضعیت NEEDS_APPROVAL حفظ شود.
۲. تکمیل اعتبارسنجی مسیر Origin و طرح محدود/قابل‌بازگشتِ حفاظت، بدون افشای تنظیم عملیاتی و بدون تغییر مشترکِ فاقد پیش‌نیاز.
۳. ادامهٔ بستهٔ مستقل فرم/خدمات/Lab، سپس UX، محتوای مستند و SEO طبق برنامهٔ شبانه؛ امنیتِ باز در گزارش صبح بالاتر از پیشرفت محتوایی گزارش شود.

References: [GitHub removal guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)، [Cloudflare origin protection](https://developers.cloudflare.com/fundamentals/security/protect-your-origin-server/)، [AOP](https://developers.cloudflare.com/ssl/origin-configuration/authenticated-origin-pull/)، reviewed2026-10-31. این منابع، به‌ترتیب رویهٔ حذف/محدودیت نسخه‌های باقی‌مانده و گزینه‌های محافظت را توضیح می‌دهند؛ نتیجهٔ جاری سایت را اثبات نمی‌کنند.

## checkpoint تازهٔ پس از merge — v4

برای TehNet:۲۰۹۰blob و۱۹۸commit،۴۱ref؛ برای MyTel:۱۱۹۵blob و۱۶۴commit،۹ref بررسی شدند. bundleهای تازه verify و در کپی جدا restore شدند. tree فعلی main در هر دو خروجی دقیقاً برابر اصل ماند؛ guard و۹unit در checkout هر مخزن پاس شدند. مقادیر حساس شناسایی‌شده/مسیرهای شخصی در objectهای blob/commit/tag بررسی‌شده صفر؛ مسیر backup/output خصوصی MyTel صفر. این‌ها فقط تمرین محلی‌اند؛ هیچ remote ref تغییر نکرد و purge مشترک NEEDS_APPROVAL است. رسید: `qa/security-2026-10-31/history-rehearsal.json`؛ map و backup دقیق خصوصی می‌مانند و پس از تغییر refs باید تازه شوند.

v3 عمداً در gateِ برابری tree متوقف شد: فهرست مشترک، ایمیل تماسِ عمداً عمومی پروفایل TehNet را هم جایگزین می‌کرد. scope پس از بازبینی original اصلاح و تماس عمومی حفظ شد. اولین checkoutِ v4 نیز به محدودیت طول مسیر Windows خورد؛ اصلِ شکست نگه داشته شد و checkout تازه با `git -c core.longpaths=true` در همان فرمان ساخته شد، بدون تغییر تنظیم سراسری. تلاشی برای ادامه روی checkout ناقص انجام نشد.

برای wikiِ TehNet و -SEO، تلاش خواندنی `ls-remote` با exit128 و پیام repository-not-found برگشت. محتوای wiki قابل بررسی نبود؛ feature روشن را مدرک نبودن محتوا نمی‌نامیم. Pages طبق snapshot API پیشین فعال نبود. تصاویر/OCR/cache خارجی هنوز بررسی کامل نشده‌اند. بررسی تنظیم واقعی branch protection و native secret scanning نیز جدا باز است.
