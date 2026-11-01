# ماتریس مهار افشا — بدون مقادیر محرمانه

Reviewed2026-10-31. Severity دربارهٔ اثر واقعی/نامعلومی آن است؛ status دربارهٔ کار انجام‌شده. «حذف‌شده از فایل جاری» با «بسته‌شدن رخداد» متفاوت است.

| ID | Severity / ماهیت | Current / history | اقدام و آزمون | نتیجه / ریسک باقیمانده | گیت |
|---|---|---|---|---|---|
| SEC-01 | P2 metadata عملیاتی؛ P1 مشروط به bypass اثبات‌شده | نشانی‌های شناسایی‌شده در current پاک؛ history/PR باقی | بررسی متن/اسکن/diff، حذف فعلی و guard/CI، تمرین blob history | فایل جاری برای مقادیر شناسایی‌شده VERIFIED؛ تضمین حفاظت Origin نیست | تاریخچه NEEDS_APPROVAL، Origin IN_PROGRESS |
| SEC-02 | Potential P0 credential؛ اعتبار و دسترسی عمومیِ نسخه‌های دیگر نامعلوم | رمز plaintext در مستندات تاریخیِ مخزن اکنون خصوصی پیدا شد؛ current حذف، history باقی | بازبینی دستی، regression قرمز علیه guard قبلی و پاس پس از اصلاح، بررسی prose در history | rotation انجام نشده؛ هر محل استفاده باید تعویض شود. صرف قدمت باعث کاهش ریسک نشده | BLOCKED: مسیر حساب/وابستگی/تأیید امن؛ مخزن خصوصی بماند |
| SEC-03 | P2 private operational evidence؛ حساسیتِ محتوای دقیق خصوصی |۱۰۹ backup/output از index حذف؛ اصل خصوصی محفوظ؛ history باقی | compare محتوای اصلی Git و کپی محلی/خصوصی، guard مسیرهای ممنوع | VERIFIED for current removal؛ ادعای خالی‌بودن همهٔ داده‌های مشتری در کل history وجود ندارد | history NEEDS_APPROVAL |
| SEC-04 | P2 privacy/operational metadata | مسیر رایانه و دو ایمیل خصوصیِ شناسایی‌شده current حذف | ماژول استاندارد به‌جای مسیر اختصاصی، known-value scan و JSON/JS checks | VERIFIED در دامنهٔ تست؛ اسکرین‌شات/فایل‌های خارج دامنه هنوز کنترل جدا می‌خواهند | بررسی رسانه READY |
| SEC-05 | P3 documented fixture/public service ranges | کلید TLS آزمایشگاهی عمداً عمومی، schema migration و public security CIDRها حفظ شدند | reason + content digest و regression برای تغییر exception | دادهٔ عمومی/test با credential عملیاتی خلط نشده؛ fixture مجوز تولید نیست | VERIFIED for narrow exception |
| SEC-06 | Origin risk under evaluation | افشای آدرس به‌تنهایی اثبات compromise نیست | read-only native inventory و external/internal HTTPS با اعتبارسنجی TLS | مسیر بیرونی/شواهد هنوز نتیجهٔ قطعی نمی‌دهد؛ configuration و OOB خصوصی/گیت‌دار | IN_PROGRESS / NEEDS_APPROVAL for risky changes |
| SEC-07 | Retained GitHub references | metadata/comment/log review انجام شد؛ patch/cache/wiki/media دامنهٔ جدا | pagination کامل و۲۴ log200، artifact/release/fork snapshot صفر؛ related reachable history بررسی شد | no match فقط در دامنهٔ نوشته‌شده؛ تاریخچهٔ اصلی/PR cache پاک نشده | follow-up READY؛ rewrite NEEDS_APPROVAL |

هر یافتهٔ تازه باید severity، مسیر منبعِ sanitized، اثر، روش/تاریخ، test result و remaining risk داشته باشد. مقادیر، private URL، نام مشتری یا raw patch اینجا ثبت نشوند.

## بازبینی false positive عمومی

اسکن unionِ همهٔ مقادیر شناخته‌شده،۸ match در۴ فایلِ پروفایل/رزومه/vCard و سازندهٔ آن‌ها یافت. بازبینی متن نشان داد یک ایمیل در این محل‌ها عمداً راه ارتباط حرفه‌ای عمومی است؛ P3 در همین زمینه. آن را صرف حضور در فهرستِ زمینهٔ ثبت‌نام خصوصیِ MyTel، از کارت تماس عمومی حذف نکردیم. مقدار و context حساب در گزارش تکرار نمی‌شود؛ deny-list خصوصیِ TehNet برای این طبقه‌بندی scope شده و سایر مقادیر شناسایی‌شده همچنان بررسی می‌شوند. این استثنا مجوز درج credential یا ایمیل خصوصی تازه نیست.

SEC-08 — P2 publication-enforcement gap: the two public main branches now require the observed app-bound privacy check/PR/up-to-date branch, including administrators;0 approving reviews required. API readback and unchanged-ref receipt: `qa/security-2026-10-31/main-protection.json`. Private repository configuration remains UNKNOWN on403. This does not close SEC-02/SEC-06/history/media gates.

SEC-09 — P2 publication coverage gap, CURRENT tooling: deep Windows paths made the old guard silently skip237 of1513 tracked files in a private checkout. Actual RED12:9PASS/2FAIL/1ERROR; corrected Windows12PASS and1513/1513 unchanged-checkout scan. Unreadable tracked files now fail with sanitized diagnostics. Repository CI/merge pending; no active leak or incident closure inferred. Known-value Git-object scan, history, rotation and origin gates stay separate. Receipt: `qa/security-2026-10-31/publication-file-coverage.json`.
