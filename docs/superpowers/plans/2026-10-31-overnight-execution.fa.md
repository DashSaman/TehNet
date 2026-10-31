# برنامهٔ اجرای شبانه TehNet × MyTel × SEO

> For agentic workers: execute inline with superpowers:executing-plans. Read the current task queue before each run; preserve other changes and completed work. No automatic team or external CLI delegation.

**Goal:** اجرای بیشترین کارِ مجاز و قابل‌اثبات تا۰۸:۰۰ یکشنبه۱نوامبر۲۰۲۶، به‌وقت Asia/Tehran، با اولویت مهار افشا و سپس تکمیل سایت و محتوای مستند.

**Architecture:** WordPress/WooCommerce و قالب/Core/Store موجود حفظ می‌شوند. ابزارهای فنی در MU-plugin، منطق درخواست در سیستم تیکت موجود و محتوا در بلوک‌های ویرایش‌پذیر قرار می‌گیرند. MyTel production فقط خواندنی است؛ سه مخزن و شواهد خصوصی مرزهای جدا دارند.

**Tech Stack:** PHP/WordPress، JavaScript/CSS ساده، Python، Playwright و GitHub Actions موجود؛ بدون سرویس پرداخت یا API پولی جدید.

**Spec:** `docs/requirements-autonomous-2026-10-31.md` کنترل‌کنندهٔ اولویت‌ها؛ `docs/requirements-growth-2026-10-31.md` و `docs/superpowers/specs/2026-10-31-cross-brand-growth-design.md` دامنهٔ قبلی و بستهٔ آغازشده را حفظ می‌کنند.

## قیود سراسری

- deadline هدف تحویل گزارش است، نه مجوزِ ادعای اتمام یا افت کیفیت. رتبه، ترافیک و توصیهٔ AI بدون دادهٔ واقعی ادعا نشوند.
- تا پایان triage/containment اولیه، بستهٔ تازهٔ مقالات آغاز نشود. پس از ثبت بلوکر امنیتی، کار مستقل بعدی ادامه یابد.
- force-push/تغییر تاریخچه در غیاب مالک صریحاً ممنوع است. کپی تمیز، backup، ref map، رویهٔ هماهنگی cloneها و پیش‌نویس درخواست پشتیبانی آماده شود.
- IP/credential/ایمیل خصوصی/داده مشتری/dump/گزارش خام در Git، CI و خروجی ابزار چاپ نشوند. اصل خصوصی در پوشهٔ خارج Git با ACL محدود است.
- noindex فعلی، inquiry-only بودن۲۵محصول، پرداخت/ERP بسته و URL/Title/H1/performance freeze مایتل حفظ شوند. فروشگاه در /shop بماند.
- انتشار TehNet فقط در دامنهٔ مجاز، با backup تازه و checksum، drift guard، staging، rollback و پس‌آزمون؛ تغییر Origin/DNS/SSH/firewall مشترک بدون OOB و گیت مجوز اجرا نشود.
- تصویر/مدل واقعی و مشخصات MPN حدس زده نشوند؛ نبود CAD مجاز یا هویت کالای قابل اثبات، وضعیت BLOCKED همان قلم است.
- مقالهٔ کاندیدا، پیش‌نویس، آزمون محلی، استقرار staging، انتشار زنده و نتیجهٔ جست‌وجو جدا ثبت شوند.

## وضعیت شروع و مدارک موجود

پاک‌سازی جاری با PRهای TehNet#33، MyTel#3 و -SEO#2 ادغام شد؛ محتوای origin/main هر سه با tree آزموده‌شده برابر بود.۲۷ تست محافظ، JSONها و نحو۱۷ JavaScript پاس شدند.۱۰۹ فایل خصوصی MyTel از index عمومی خارج و اصل محلی/خصوصی آن‌ها حفظ شد. رمز تاریخی با اعتبار نامعلوم و دو ایمیل خصوصی نیز حذف شدند؛ حذف متن، rotation نیست. تمرین تاریخچه در کپی جدا:۲۰۵۳ blob برای TehNet و۱۱۸۱ برای MyTel؛ مقادیر شناسایی‌شده باقی نماندند، اما remote/PR/cache/fork هنوز پاک نشده‌اند. آمار کل اسکنر، تعداد credential فعال نیست.

کد nonce تیکت/B2B و context محدود voice-network، ابزار۸سؤالیِ دستی و دو صفحهٔ خدمات/Lab در شاخهٔ رشد محلی وجود دارند. تست‌های قبلی PHP:۱۸ intake،۱۰ readiness،۹ ticket،۱۵ quote و۱۱ MTU پاس؛ پس از همگام‌سازی از main باید دوباره اجرا شوند. مرورگر/native و انتشار این بسته هنوز انجام نشده‌اند. snapshot خصوصی قبل از fast-forward گرفته شد؛۱۴ فایل حفظ و شاخه بدون از دست‌دادن تغییرات به main پاک‌سازی‌شده همگام شد.

## تمرکز بازبینی

۱. خروجی غیرمستقیمِ scanner/diff نباید خودِ secret را افشا کند؛ رمزِ prose در بازبینی دستی پیدا شد، لذا اتکا به یک ابزار کافی نیست.
۲. پاسخ direct-origin با TLS معتبر فقط همان مسیر/پروتکل/زمان را اثبات می‌کند؛ timeout یا آزمایش از خود سرور، اثبات حفاظت بیرونی نیست.
۳. nonce باید داخل form مالکِ ارسال باشد؛ query/POST آرایه‌ای، context نامعتبر و persistence خصوصی آزمون شوند.
۴. ابزار readiness اندازه‌گیری شبکه، score یا گواهی نیست؛ no-JS، موبایل، RTL، چند نمونه، reset و JSON محلی بدون درخواست بیرونی کار کنند.
۵. WordPress live file/body drift و clone قدیمی نباید باعث overwrite خانه، منو، محصول یا دادهٔ مشتری شود؛ هر release سریالی و allowlist داشته باشد.

## صف اجرا و آزمون هر بسته

### P0/P1 — triage، مهار جاری و پیشگیری

Files: `security/INCIDENT_RESPONSE_2026-10-31.md`, `security/EXPOSURE_REMEDIATION_MATRIX.md`, `security/PREVENTION_CONTROLS.md`, private evidence outside Git.

- [x] سه مخزن، visibility و سورس/تاریخچهٔ در دسترس بررسی اولیه شد؛ فایل جاری پاک‌سازی و CI اضافه/ادغام شد.
- [x] regression رمز prose علیه محافظ قبلی یک FAIL واقعی داشت و نسخهٔ اصلاح‌شده پاس شد.
- [x] اصل خصوصی و ACL آن را تأیید و یافته‌ها را با severity، current/history، validity و شواهد بدون مقدار ثبت کن؛ رمز قدیمی را صرف قدمت بی‌خطر ننام.
- [ ] وجود credential فعال یا دسترسی غیرمجاز را فقط با راه مجاز و شاهد معتبر ارزیابی کن. account/وابستگی نامعلوم → BLOCKED یا NEEDS_APPROVAL، بدون reset یا پیام واقعی.

### P2 — دامنهٔ GitHub و آمادگی پاک‌سازی تاریخچه

Files: security matrix, private GitHub inventory/backup/ref map, sanitized support-request draft.

- [ ] issue/comment/PR، CI log/artifact، release/attachment، fork، wiki/pages و repo عمومی مرتبط را با pagination و دامنهٔ مشاهدهٔ صریح بررسی کن؛ موارد inaccessible را skipped/unknown بنویس.
- [x] snapshot refهای بعد از ادغام را تازه کن؛ bundle قابل verify، کپی filter-repo، بررسی blobهای reachable و مقایسهٔ tree فعلیِ main قبل/بعد آماده کن.
- [x] SHA/ref drift باید عملیات را متوقف کند؛ هیچ mirror force-push یا حذف ref اجرا نشود. هماهنگی clone/rebase و محدودیت refs/pull/GitHub cache در رویه باشد.
- [ ] وضعیت این عملیات NEEDS_APPROVAL است؛ به P3/P4 ادامه بده.

### P3 — ریسک Origin و حفاظت قابل‌اثبات

Files: private service/network read-only inventory, public sanitized matrix, scoped protection proposal/test.

- [ ] منابع رسمی Cloudflare مربوط به protect-origin و AOP را بخوان؛ DNS-only سرویس عمومی و اشتراک میزبان را با سیاست وب تفکیک کن.
- [ ] یک probe مجاز خواندنی از مسیر بیرونی، با pin اتصال و Host/SNI درست و TLS verification روشن اجرا کن؛ فقط نتیجهٔ redacted/Boolean منتشر شود.
- [ ] firewall/Nginx/AOP و وابستگی‌ها را بخوان؛ وضعیت OOB/rollback/مجوز را مشخص کن. بدون پیش‌نیاز، تغییر شبکهٔ مشترک اجرا نشود و پیشنهاد دقیق آماده شود.

### P4/P5 — مسیر خدمات، فرم و ابزار آمادگی شبکه

Files: `site/plugins/tehnet-store/includes/class-{tickets,quotes}.php`, `site/mu-plugins/tehnet-technical-resources*`, `tests/service-intake-contract.php`, `tests/network-readiness-unit.php`, browser test, `content/growth-2026-10-31/*`, new dated QA/release receipt.

- [x] تست‌های PHP مربوط را با mbstringِ runtime موجود اجرا و نتیجهٔ واقعی ذخیره کن؛ برای فقط کمبود extension کد را تغییر نده.
- [x] browser contract برای unknown/ready/issue/na، چند نمونه، export measured:false، reset/focus، no-JS و موبایل۳۷۵px بنویس؛ نبود/شکست واقعی را قبل از اصلاح ثبت کن.
- [x] clone داخلیِ موجود را با identity و mail/HTTP/cron/payment guard بررسی کن؛ DB tmpfs آن را restart/reset نکن. فقط فایل‌های allowlist و محتوای همین بسته با backup خصوصی تغییر کنند.
- [x] parse/serialize بلوک‌ها، parent/slug، یک H1، canonical/noindex، CTA و nonce در FormData و POST context را با مشتری synthetic در clone بررسی کن.
- [x] full-page desktop/mobile و گوتنبرگ واقعی:۵۶بلوک معتبر، unsaved edit/reset، cleanup کاربر/قفل و برابری دادهٔ قبلی؛ production drift gate خواندنی۶فایلی پاس شد. `docs/editor-release-acceptance-2026-10-31.fa.md` و رسیدها مرجع‌اند.
- [x] backup تازه با checksum و restore جدا:۱۰٬۰۱۶فایل/۴۷جدول و native boot، cleanup و invariants پاس؛ WordPress/SQL فقط، نه Origin/OOB.
- [x] migration محدود با journal، apply/repeat/rollback و دو اتصال مستقل/retention cap:۳۷ native PASS؛۱۳fixture cleanup، اصل posts/meta برابر.
- [x] release سریالیِ محدود پس از backup/checksum/drift/rollback و گیت مجاز: PR34/main ac506f1؛۸public HTTP و۲۵public browser پاس. receipt انتشار مرجع است؛ تکرار نشود.

### P6/P7 — مالکیت intent، خدمات و محتوا

Files: brand ownership, keyword/page map, cross-brand link spec, candidate portfolio, original service/article/Lab sources, central source ledger.

- [x] موجودی۱۰۰کار/۲۰خوشه با owner/مقصد/source/priority/limit/state ثبت و۲۰کنترل پاس؛ VERIFIED_INVENTORY_ONLY، تحقیق بازار/فرمان و انتشار همهٔ موضوع‌ها تکمیل نیست.
- [x] نگاشت۱۳intent تجاری موجود MyTel و۶intent TehNet ثبت شد؛ MyTel freeze حفظ، reverse-link فقط پیشنهاد در سند TehNet و بدون live write. editorial/external بودن صریح است.
- [ ] پشتیبانی/راه‌اندازی موجود را اول بهبود بده؛ امنیت، سرور/مجازی‌سازی و مانیتورینگ فقط در حد خدمتِ قابل ارائه با دامنه و deliverable صادقانه تکمیل شوند.
- [ ] مقالات در batch کوچک: intent و منابع رسمی → اصل توضیح/سناریو/دیاگرام → صحت commands/نسخه/محدودیت → لینک/metadata/CTA → مرور → staging → انتشار مجاز. دادهٔ نامطمئن در draft بماند.
- [ ] بدون deep review واقعیِ۱۲۰ فروشگاه یا CAD دقیق۲۵کالا، چنین تکمیلی ادعا نشود؛ هر سطح benchmark و مدرک مدل/مجوز مشخص باشد.

### P8/P9 — SEO فنی، AI Search و انتقال دانش

Files: dated technical/AI baseline, source ledger, index-launch checklist, competitor scorecard; `-SEO` topic/source/handoff/progress/dashboard.

- [ ] Google/Bing/OpenAI/Schema منابع معتبر جاری داشته باشند؛ URL دارای redirect به مطلب نامرتبط، منبع تأییدشده نیست.
- [ ] status/redirect/canonical/robots/sitemap/headings/meta/schema/mobile/link graph و crawler/CDN access را با روش و حدودش بررسی کن؛ robots policy جای واقعی‌بودن crawler نیست.
- [ ] noindex عمدی را حفظ و چک‌لیست launch آماده کن. دادهٔ Search Console/Ahrefs فقط اگر دسترسی واقعی جواب داد؛ خطای plan/access شفاف بماند.
- [ ] تجربهٔ هر milestone با date/evidence/limits بدون metrics خصوصی و نشانی/credential به -SEO برگردد؛ درصد baseline عمومی بدون محاسبه عوض نشود.

### P10 — QA، commit و گزارش صبح

- [ ] بعد از هر بسته: آزمون مناسب، diff کامل مرتبط با redaction، guard/known-value scan، commit کوچک، remote-ref verification، progress/handoff و انتخاب بستهٔ بعد.
- [ ] نزدیک۰۷:۳۰ از شروع feature بزرگ خودداری کن؛ QA و reconcile باقی‌مانده را تمام کن.
- [ ] `docs/reports/MORNING_HANDOFF_2026-11-01.fa.md` با بخش‌های امنیت، توسعه، محتوا/SEO، تست exact، GitHub، انتقال SEO و next actions تهیه شود. skipped و local/staging/live جدا باشند.
- [ ] در۰۸:۰۰، نتیجهٔ واقعی و گیت‌های باز گزارش شوند؛ باقی‌مانده با status روشن تحویل شود، نه ادعای «همه‌چیز تمام».

## cadence و بازهٔ هدف

Heartbeat موجود `automation-2` هر نیم‌ساعت در همین گفتگو تا۰۸:۰۰ ادامه می‌دهد. اگر سیستم/برنامه یا runner در دسترس نباشد، تداوم تضمین نیست؛ checkpoint دیسک مرجع بازیابی است. هم‌زمانی تغییر/انتشار ممنوع و نوبت فعال ادامه می‌یابد. این cadence محدود و مورد درخواست مالک است؛ cron یا سرویس دائمی ساخته نشده است.

تا۲۳:۰۰: P0–P3 و شروع بستهٔ فرم/ابزار؛۲۳–۰۱: staging و اصلاح UX؛۰۱–۰۴: خدمات/محتوای مستند و نقشهٔ موضوعات؛۰۴–۰۶: سئو/رقابت/انتقال دانش؛۰۶–۰۷:۳۰: regression و releaseهای واجد گیت؛۰۷:۳۰–۰۸:۰۰: گزارش. اگر امنیت طول بکشد، این بازه‌ها با ثبت علت جابه‌جا شوند و کیفیت/گیت‌ها حذف نشوند.

Checkpoint clarification: completed boxes refer to the scoped results in the progress log. Remote purge/credential/Origin acceptance remains open; OCR has bounded completed evidence. PHP/component/native-preview/editor acceptance is not a production deployment. Check the latest progress entry before repeating a dated task.
