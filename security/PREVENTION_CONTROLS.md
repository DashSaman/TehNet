# پیشگیری از تکرار افشا

Reviewed2026-10-31. این کنترل‌ها فعال‌اند، ولی گواه جامع امنیت نیستند.

- `tools/publication_guard.py` + `.publication-policy.json`: فایل خصوصی، credential format، URL userinfo، مسیر شخصی، نشانی در اسناد عملیاتی و password در prose؛ diagnostic فقط دسته/مسیر/خط است.
-۹ regression در هر مخزن، از جمله عدم نمایش مقدار، malformed/known values، exception محدودشده به digest محتوای LF-normalized و prose-password؛۲۷ تست و CI در PRهای ادغام‌شده موفق بودند.
- `.github/workflows/publication-guard.yml`: checkout pin‌شده، permissions فقط contents:read و persist-credentials=false؛ guard و unit روی push/PR اجرا می‌شوند.
- `.gitignore` فایل‌های credential/DB/private evidence را exclude می‌کند؛ schema source استثنای مشخص دارد. ignore تاریخچه را حذف نمی‌کند. MyTel backup/output خصوصی دوباره tracked نشود.
- مقادیر دقیق و scanner/raw/native/log/backup در محل خارج Git با inheritance حذف‌شده و دسترسی owner/System/Administrators نگهداری می‌شوند؛ سیاست اجرای سراسری سیستم تغییر نکرد. مسیر این محل در گزارش عمومی چاپ نشود.
- اسکن Gitleaks با redaction، بررسی دستیِ diff و تشخیص اختصاصی IP/host کنار هم لازم‌اند. شمار یافتهٔ scanner تعداد credential فعال نیست؛ رمز prose را بازبینی دستی یافت.
- credential در env/secret manager یا تنظیم خصوصیِ موجود تأمین شود؛ مقدار واقعی در command/tool output/PR body نرود. جایگزین dummy برای وابستگی تولید و سپس ادعای سالم‌بودن ممنوع است.

## موارد آماده/نیازمند تکمیل

وضعیت GitHub native secret scanning/push protection هنوز از تنظیمات واقعی حساب برای هر repo تأیید نشده؛ supported/enabled فرض نشود. نصب hook اشتراکی یا تغییر core.hooksPath انجام نشده؛ CI موجود نقطهٔ کنترل اجباری در اجرای workflow است، ولی branch protection و الزام آن نیازمند بررسی تنظیمات واقعی‌اند. OOB/شبکه، rotation حساب و purge تاریخچه گیت‌های جدا هستند. هرگونه exception تازه باید منبع و دلیل داشته باشد، نه ignore گسترده برای سبزشدن اسکن.
