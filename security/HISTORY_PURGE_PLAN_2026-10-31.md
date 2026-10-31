# رویهٔ هماهنگ پاک‌سازی تاریخچه — NEEDS_APPROVAL

این فایل فقط برنامهٔ قابل بازبینی است. هیچ force-push مجاز/اجراشده تلقی نشود. متن مالک در بخش۴ دستور جدید، اجرای خودکار آن در غیاب او را منع می‌کند.

1. پس از پایان current-tree merges، از remote تازه heads/tags/pull references و وضعیت PRها را دریافت کن. scope و مالک تغییرات را هماهنگ کن؛ repoهای نامرتبط و visibility تغییر نکنند.
2. bundle مستقل در محل خصوصی، SHA256 و `git bundle verify`، ref map و source/archive inventory بساز. قبل از purge امکان restore همان snapshot را محلی آزمایش کن.
3. در کپی جدا `git-filter-repo` با نسخه/هش ابزارِ ثبت‌شده اجرا شود: فقط مقادیر حساسِ تأییدشده، private workstation paths و مسیرهای private evidence مربوط به MyTel. public CIDR/runtime dependency عمومی یا immutable provenance را کورکورانه تغییر نده.
4. کل blobهای reachableِ خروجی برای مقادیر شناسایی‌شده و الگوهای مربوط بررسی شوند؛ tree جاری main پیش/پس باید برابر بماند یا تغییر دقیق مستقل مجدداً QA شود. guard و testها در checkout خروجی اجرا شوند. قبلی‌ها تمرین‌های محلی با snapshot قبل از ادغام‌اند؛ به‌عنوان snapshot تازه استفاده نشوند.
5. **پس از تأیید صریح مالک** remote refها را دوباره مقایسه کن؛ کوچک‌ترین drift عملیات را متوقف کند. اگر protection/approval مانع شد دور زده نشود. update فقط refهای مصوب با expected old SHA/lease باشد؛ `push --mirror` که می‌تواند refهای نامرتبط را حذف کند اجرا نشود.
6. refs/pull و cached views ممکن است باقی بمانند. پیش‌نویس sanitized درخواست GitHub Support آماده و جزئیات دقیق فقط در کانال خصوصی قرار گیرد؛ بدون مجوز تماس ارسال نشود. امکان حذف همهٔ clone/forkها در اختیار این agent نیست.
7. همکاران باید clone/rebase تمیز داشته باشند؛ merge تاریخچهٔ آلوده می‌تواند افشا را برگرداند. پس از اجرا دوباره remote refs و فایل‌های public و direct commit/PR retention بررسی شوند. اعتبار credential جدا revoke/rotate شود.

حذف متن از current تأیید شده، پاک‌سازی کپی محلی تمرین شده، بازنویسی remote/تأیید cache/fork هنوز نشده است. این بلوکر نباید اجرای امنِ مستقلِ سایت و محتوا را متوقف کند.
