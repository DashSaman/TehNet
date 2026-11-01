# ماتریس مهار افشا — بدون مقادیر محرمانه

Reviewed2026-11-01; initial findings retained. Severity دربارهٔ اثر واقعی/نامعلومی آن است؛ status دربارهٔ کار انجام‌شده. «حذف‌شده از فایل جاری» با «بسته‌شدن رخداد» متفاوت است.

| ID | Severity / ماهیت | Current / history | اقدام و آزمون | نتیجه / ریسک باقیمانده | گیت |
|---|---|---|---|---|---|
| SEC-01 | P2 metadata عملیاتی؛ P1 مشروط به bypass اثبات‌شده | نشانی‌های شناسایی‌شده در current پاک؛ history/PR باقی | بررسی متن/اسکن/diff، حذف فعلی و guard/CI، تمرین blob history | فایل جاری برای مقادیر شناسایی‌شده VERIFIED؛ تضمین حفاظت Origin نیست | تاریخچه NEEDS_APPROVAL، Origin UNDETERMINED |
| SEC-02 | Potential P0 credential؛ اعتبار و دسترسی عمومیِ نسخه‌های دیگر نامعلوم | رمز plaintext در مستندات تاریخیِ مخزن اکنون خصوصی پیدا شد؛ current حذف، history باقی | بازبینی دستی، regression قرمز علیه guard قبلی و پاس پس از اصلاح، بررسی prose در history | rotation انجام نشده؛ هر محل استفاده باید تعویض شود. صرف قدمت باعث کاهش ریسک نشده | BLOCKED: مسیر حساب/وابستگی/تأیید امن؛ مخزن خصوصی بماند |
| SEC-03 | P2 private operational evidence؛ حساسیتِ محتوای دقیق خصوصی |۱۰۹ backup/output از index حذف؛ اصل خصوصی محفوظ؛ history باقی | compare محتوای اصلی Git و کپی محلی/خصوصی، guard مسیرهای ممنوع | VERIFIED for current removal؛ ادعای خالی‌بودن همهٔ داده‌های مشتری در کل history وجود ندارد | history NEEDS_APPROVAL |
| SEC-04 | P2 privacy/operational metadata | مسیر رایانه و دو ایمیل خصوصیِ شناسایی‌شده current حذف | ماژول استاندارد به‌جای مسیر اختصاصی، known-value scan و JSON/JS checks | VERIFIED در دامنهٔ تست؛ اسکرین‌شات/فایل‌های خارج دامنه هنوز کنترل جدا می‌خواهند | OCR محدود VERIFIED؛ سایر رسانه/metadata خارج دامنه |
| SEC-05 | P3 documented fixture/public service ranges | کلید TLS آزمایشگاهی عمداً عمومی، schema migration و public security CIDRها حفظ شدند | reason + content digest و regression برای تغییر exception | دادهٔ عمومی/test با credential عملیاتی خلط نشده؛ fixture مجوز تولید نیست | VERIFIED for narrow exception |
| SEC-06 | Origin risk under evaluation | افشای آدرس به‌تنهایی اثبات compromise نیست | read-only native inventory و external/internal HTTPS با اعتبارسنجی TLS | مسیر بیرونی/شواهد هنوز نتیجهٔ قطعی نمی‌دهد؛ configuration و OOB خصوصی/گیت‌دار | UNDETERMINED / BLOCKED on route and OOB; NEEDS_APPROVAL for changes |
| SEC-07 | P2 retained refs/API | current/available API و snapshotها بررسی؛history/PR cache باقی | main202log؛۴repo مرتبط،۱۴release/۲asset/۵artifact/۵log و۷payload؛۳clean-copy محلی با tree برابر | no known/token match در همین دامنه؛wiki غیرقابل‌دسترسی،clone/cache پاک نشده | shared rewrite/support NEEDS_APPROVAL |

هر یافتهٔ تازه باید severity، مسیر منبعِ sanitized، اثر، روش/تاریخ، test result و remaining risk داشته باشد. مقادیر، private URL، نام مشتری یا raw patch اینجا ثبت نشوند.

## بازبینی false positive عمومی

اسکن unionِ همهٔ مقادیر شناخته‌شده،۸ match در۴ فایلِ پروفایل/رزومه/vCard و سازندهٔ آن‌ها یافت. بازبینی متن نشان داد یک ایمیل در این محل‌ها عمداً راه ارتباط حرفه‌ای عمومی است؛ P3 در همین زمینه. آن را صرف حضور در فهرستِ زمینهٔ ثبت‌نام خصوصیِ MyTel، از کارت تماس عمومی حذف نکردیم. مقدار و context حساب در گزارش تکرار نمی‌شود؛ deny-list خصوصیِ TehNet برای این طبقه‌بندی scope شده و سایر مقادیر شناسایی‌شده همچنان بررسی می‌شوند. این استثنا مجوز درج credential یا ایمیل خصوصی تازه نیست.

SEC-08 — P2 publication-enforcement gap: the two public main branches now require the observed app-bound privacy check/PR/up-to-date branch, including administrators;0 approving reviews required. API readback and unchanged-ref receipt: `qa/security-2026-10-31/main-protection.json`. Private repository configuration remains UNKNOWN on403. This does not close SEC-02/SEC-06/history/media gates.

SEC-09 — P2 publication coverage gap, CURRENT tooling: deep Windows paths made the old guard silently skip237 of1513 tracked files in a private checkout. Actual RED12:9PASS/2FAIL/1ERROR; corrected Windows12PASS and1513/1513 unchanged-checkout scan. Unreadable tracked files now fail with sanitized diagnostics. Merged TehNet#60/MyTel#5/-SEO#19 with actual CI12(11PASS/1SKIP Linux), full file counts1515/52/68; no active leak or incident closure inferred. Known-value Git-object scan, history, rotation and origin gates stay separate. Receipt: `qa/security-2026-10-31/publication-file-coverage.json`.

## وضعیت مستقل هر دامنه —2026-11-01

| دامنه | Current | History / external retention | Rotation / Origin | Owner approval |
|---|---|---|---|---|
| مقادیر شناسایی‌شده | current removal VERIFIED با PR33/3/2 و guard/CI | local clean snapshots VERIFIED؛ remote purge NOT_DONE | credential UNKNOWN/NOT_ROTATED | مسیر حساب/وابستگی و اقدام امن لازم؛ reset حدسی ممنوع |
| refs و cache | سه snapshot با sourceهای صریح؛refs69/12/30،backup restore/main-tree/۱۲Windows/guard کامل | normal merge بعدی map را تاریخی می‌کند؛PR/cache/fork/old clones باقی | مستقل از اعتبار credential | NEEDS_APPROVAL؛هیچ force-push یا ارسال Support در غیاب مالک |
| Origin مشترک | current direct route هنوز UNDETERMINED | افشای تاریخی آدرس با حذف prose مهار کامل نمی‌شود | OOB/مسیر معتبر/rollback prerequisites تأیید نشده | network/DNS/SSH/Origin mutation انجام نشده؛نیازمند پیش‌نیاز و مجوز |
| فایل و رسانه | guard اصلاح‌شده همهٔ trackedها را می‌خواند یا FAIL؛۱۲Windows PASS،Linux۱۱PASS/۱SKIP | OCR تاریخی محدود و Git-object scan جدا؛عدم وجود هر secret تضمین نشده | حساب/دستگاه/شبکه تست نشده | exception تازه بدون طبقه‌بندی و دلیل پذیرفته نیست |
| سطح GitHub مرتبط | هفت core metadata200؛API اصلی/چهار مرتبط و payloadها در دامنهٔ رسید VERIFIED | wikiهای غیرقابل‌دسترسی و cache/clone خارج اثبات حذف هستند | no active-credential claim | فقط read-only audit و normal PR merges؛هیچ حذف artifact/release یا shared rewrite |

رسیدها: `qa/security-2026-10-31/history-ref-refresh-2026-11-01.json`، `main-api-refresh-2026-11-01.json`، `publication-file-coverage.json`، `related-payload-candidate-layers.json` و `repository-core-metadata.json`. API اصلی178 آرشیو200 جدید +24 قبلی =202run فهرست‌شده؛چهار repo مرتبط5log200 جدا دارند. هفت payload با545عضو آرشیو برای۹مقدار/الگوی token و سپس قواعد publication/Gitleaks بررسی شدند؛candidate و archive exclusion صفر. این نتیجه bounded است، نه گواه نبود هر اطلاعات خصوصی ناشناخته. exact map/مقادیر/raw payload و backup فقط خصوصی‌اند. خطاهای آماده‌سازی و محدودیت‌ها در incident و رسیدها حفظ شده‌اند.
