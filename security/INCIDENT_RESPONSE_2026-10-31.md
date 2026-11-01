# بررسی افشای اطلاعات — خلاصهٔ مناسب انتشار عمومی

## CURRENT SECURITY CHECKPOINT — 2026-11-01

P2 tooling correction is merged: [TehNet#60](https://github.com/DashSaman/TehNet/pull/60), [MyTel#5](https://github.com/DashSaman/mytel.one/pull/5), [-SEO#19](https://github.com/DashSaman/-SEO/pull/19). Actual CI in each repository ran12 privacy cases:11 passed/1 Windows-only skip on Linux. Windows locally passed12/12 in each. TehNet's25 release-boundary cases also passed. Full current-file read counts:1515/52/68. The earlier deep-checkout1276/1513 PASS was incomplete; the corrected unchanged checkout read1513/1513. This corrects publication coverage, not a confirmed new leak or incident closure.

Fresh isolated local cleanup snapshots preserve current main trees for TehNet e4b5ae5, MyTel15e3813 and -SEO fba6419. All reachable blob/commit/tag objects were checked for the nine identified values and personal-path pattern; classified public contact remains preserved. Snapshot refs69/12/30; changed local refs69/12/25. Backup bundles were verified/restored and all three clean checkouts passed12 Windows tests and complete-file guards. Exact maps and backups stay private. Subsequent normal merges invalidate freshness; shared refs were never rewritten.

Four related public repositories were checked beyond the three primary ones. MyTellPBX changed one existing ref and added two: incremental28blob/2commit/2tag known-value scan and a full current reachable-history Gitleaks run found no candidates. The other three advertised ref maps matched earlier audited mirrors; unchanged object scans were not repeated. Complete related API pagination found14 releases,2 release assets,5 artifacts and5 workflow runs; issue/PR/comment/fork counts were0. Five200 CI archives were scanned. Seven actual payload archives (two release assets/five artifacts),545 archive file members and31,550,723 expanded bytes were inspected without extraction or execution, with no identified-value/token candidates and no archive exclusions. This is bounded detection, not arbitrary-secret proof or media/decompilation/account validation.

All four related wiki queries were inaccessible (exit128); absence of content is not inferred. Pages API404 and metadata snapshots are recorded separately. Artifact download preparation first returned415 with the release-asset Accept header; the documented artifact header succeeded. A depth-limit bug marked plain leaf files as limited; identical cached payload hashes were reinspected with limits only on actual nested archives. Original diagnostics remain private and were not counted as successful scans. [Official artifact API](https://docs.github.com/en/rest/actions/artifacts#download-an-artifact), reviewed2026-11-01.

P0/P1 credential validity/rotation remains UNKNOWN/NOT_ROTATED. P2 shared-history/PR/cache/fork purge and support submission remain NEEDS_APPROVAL; no force-push or support message. P3 origin remains UNDETERMINED with OOB prerequisites unverified; no network/DNS/SSH/account mutation. Current removal, local cleanup, rotation and origin are separate statuses. Main-repository API/new-CI-log refresh completed separately; see the following dated follow-up. Receipt: `qa/security-2026-10-31/history-ref-refresh-2026-11-01.json`.

## HISTORICAL INITIAL CHECKPOINT —2026-10-31

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

## Main API/log follow-up —2026-11-01

Main-repository API/new-log follow-up is now VERIFIED in its stated snapshot: TehNet60 PR/133runs, MyTel5PR/9runs and -SEO19PR/60runs. Complete pagination and178 newly inspected200 CI archives plus24 previously inspected archives cover all202 listed runs, without size/invalid-archive exclusions; known-value/token candidates0. Related repositories add5 separately scanned CI archives. These are run/archive counts, not distinct findings or proof of no undiscovered secret. The additional MyTel wiki query was inaccessible; content absence is not inferred. Raw captures stay private. Receipt: `qa/security-2026-10-31/main-api-refresh-2026-11-01.json`. Later report/documentation runs are beyond this timestamped snapshot and still require ordinary publication CI/guard checks.

## Additional bounded evidence layers —2026-11-01

Cached identical-hash payloads were checked with the current publication rules and default redacted Gitleaks stdin in an isolated private working directory:7payloads/545archive file members, no candidate or archive exclusion. Nine known values/token patterns remain separate from arbitrary-secret absence or credential validity. Core metadata for all7 explicitly named repositories was read/scanned with200, no known/token occurrence, no visibility change. Receipts: `qa/security-2026-10-31/related-payload-candidate-layers.json` and `repository-core-metadata.json`. No archive members were unpacked to their member paths or executed; the additional Gitleaks phase retained decoded member content in one private scanner stream. No account reset or release/artifact deletion occurred.
