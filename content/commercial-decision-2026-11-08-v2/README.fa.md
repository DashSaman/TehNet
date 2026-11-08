# بستهٔ تصمیم تجاری نسخهٔ دوم — PR94
وضعیت پایه: PREPARED؛ [رسید پذیرش و وضعیت جاری](../../seo/commercial-decision-2026-11-08-v2/verification.json) مرجع qualification است؛ تا ثبت رسید cloud، پذیرش اجرایی ادعا نمی‌شود. هیچ تغییر production، ادغام یا تغییر noindex مجاز/انجام نشده است.

این بسته owner8 را فقط در بدنه، و owner29/31/33/35 را در بدنه، عنوان و excerpt تغییر می‌دهد. تغییر title/excerpt دامنهٔ صریح v2 است و به مجوز body-only نسخهٔ اول نسبت داده نمی‌شود. پنج صفحهٔ جدید از نوع page هستند: N1 فرزند Services و A1–A4 صفحات تحریریهٔ ریشه با Gutenberg و انتساب واقعی سازمان. blog69 و home5 تغییر ندارند. از ساخت post جدید، taxonomy یا سامانهٔ فرم موازی خبری نیست.

دامنهٔ انتشار canonical: `tehnet-commercial-decision-20261108-v2` از طریق همان `ops/release-growth-content.py` و `ops/migrate-growth-content.php`. manifest دقیق پنج owner و پنج صفحه را محدود می‌کند. نسخهٔ v2 جایگزین candidateهای owner8/29 نسخهٔ اول است؛ v1 سپس v2 را پشت سر هم منتشر نکنید. baseline بدنه/عنوان/excerpt مشاهده‌شدهٔ live است؛ در drift بازبینی تازه لازم است.

کاربرگ‌ها کامل و شامل فرم خالی، مثال فرضی و UNKNOWN/NOT_TESTED هستند؛ این مقادیر داخل فرم نشانهٔ صداقت داده‌اند، نه متن اصلیِ تکمیل‌نشده. A1–A4 به‌ترتیب قرارداد عملیاتی، پیشنهاد هم‌دامنه، نیازسنجی workload و شاهد بازیابی را پوشش می‌دهند. فایل‌های CSV و HTML چاپی، دارایی عمومیِ فاقد دادهٔ مشتری‌اند و exact-byte در آزمون بررسی خواهند شد. CSS فقط `.tn-decision-table` را هدف می‌گیرد.

بازگشت canonical: متن، عنوان، excerpt، meta و revision ownerهای قبلی به snapshot خصوصی برمی‌گردد؛ پنج صفحهٔ تازه draft می‌شوند، حذف قطعی نمی‌شوند. فایل‌های تازهٔ تحت مالکیت حذف و CSS قبلی با checksum برگردانده می‌شود. صفحه یا فایل دارای drift را بازنویسی نکنید. restore کامل دیتابیس فقط روی fixture آزمایش می‌شود؛ rollback محدود زنده نباید دادهٔ تازهٔ مشتری را برگرداند.

اسکن فهرست خصوصی قدیمی: NOT_RUN_OWNER_APPROVED_BRANCH_EXCEPTION فقط برای `feat/seo-readiness-20261108`. فایل/سیستم مالک خوانده نمی‌شود. اسکن الگوی اسرار روی کد تازه پیش از commit و publication_guard در cloud انجام می‌شود؛ این اسکن پاکی تاریخچه یا چرخش credential را ثابت نمی‌کند.

تأییدها جدا هستند: (۱) merge دامنهٔ نهایی PR94، (۲) انتشار محدود محتوا/دارایی با backup تازه، drift و rollback، (۳) نصب/فعال‌سازی کنترل index فقط در allowlist تأییدشده. هیچ‌کدام از حاضرشدن متن، CI، یا تأیید مصرف‌شدهٔ PR88 نتیجه نمی‌شوند. PR89–91 و PR93 مستقل‌اند؛ تغییر فایل مشترک publisher/CSS نیازمند reconciliation آخرین main است.

شکاف مسیر Lab در staging: tn_lab با rewrite عمومی lab، pageهای موجود76/188/207 را می‌پوشاند. class-content-types.php در همین scope فقط برای این سه مسیرِ دارای هویت publish تأییدشده، rule خواندنی دقیق را مقدم می‌کند. گزینهٔ ذخیره‌شدهٔ rewrite_rules، ساختار permalink و URLها تغییر نمی‌کنند؛ وجود CPT هم‌نام باعث عدم override و نیاز به reconciliation می‌شود. rollback همین فایل قبلی را برمی‌گرداند. اثر production هنوز مشاهده/منتشر نشده است.
