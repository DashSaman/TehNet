# پیشگیری از تکرار افشا

Reviewed2026-10-31. این کنترل‌ها فعال‌اند، ولی گواه جامع امنیت نیستند.

- `tools/publication_guard.py` + `.publication-policy.json`: فایل خصوصی، credential format، URL userinfo، مسیر شخصی، نشانی در اسناد عملیاتی و password در prose؛ diagnostic فقط دسته/مسیر/خط است.
-۹ regression در هر مخزن، از جمله عدم نمایش مقدار، malformed/known values، exception محدودشده به digest محتوای LF-normalized و prose-password؛۲۷ تست و CI در PRهای ادغام‌شده موفق بودند.
- `.github/workflows/publication-guard.yml`: checkout pin‌شده، permissions فقط contents:read و persist-credentials=false؛ guard و unit روی push/PR اجرا می‌شوند.
- `.gitignore` فایل‌های credential/DB/private evidence را exclude می‌کند؛ schema source استثنای مشخص دارد. ignore تاریخچه را حذف نمی‌کند. MyTel backup/output خصوصی دوباره tracked نشود.
- مقادیر دقیق و scanner/raw/native/log/backup در محل خارج Git با inheritance حذف‌شده و دسترسی owner/System/Administrators نگهداری می‌شوند؛ سیاست اجرای سراسری سیستم تغییر نکرد. مسیر این محل در گزارش عمومی چاپ نشود.
- اسکن Gitleaks با redaction، بررسی دستیِ diff و تشخیص اختصاصی IP/host کنار هم لازم‌اند. شمار یافتهٔ scanner تعداد credential فعال نیست؛ رمز prose را بازبینی دستی یافت.
- credential در env/secret manager یا تنظیم خصوصیِ موجود تأمین شود؛ مقدار واقعی در command/tool output/PR body نرود. جایگزین dummy برای وابستگی تولید و سپس ادعای سالم‌بودن ممنوع است.

## وضعیت آغاز بررسی — checkpoint پایین‌تر آن را به‌روز می‌کند

در آغاز، وضعیت GitHub native secret scanning/push protection و branch protection از تنظیمات واقعی تأیید نشده بود؛ نتیجهٔ بعدی در checkpoint زیر آمده است. نصب hook اشتراکی یا تغییر core.hooksPath انجام نشده. OOB/شبکه، rotation حساب و purge تاریخچه همچنان گیت‌های جدا هستند. هرگونه exception تازه باید منبع و دلیل داشته باشد، نه ignore گسترده برای سبزشدن اسکن.

## Mandatory publication checks —2026-10-31

**OBSERVED:** Actual API review found native secret scanning/push protection enabled on the two public repositories, while main had no protection and the accessible ruleset list was empty. A passing workflow alone was therefore not mandatory publication enforcement. The private repository's protection API returned403 and security fields were absent: its state remains UNKNOWN, not “disabled”; no subscription, visibility or policy change was attempted there.

After verifying the successful `tracked-file-privacy` job and its actual GitHub Actions app, main protection was configured on the two public repositories. Readback200 confirmed: pull request required, that app-bound check required, branch up-to-date required, administrator enforcement on, force-push/deletion off. Required approving-review count is0 to avoid claiming independent review or locking a sole-owner workflow. Main commit IDs remained unchanged. Prior settings and a drift-guarded rollback procedure are private.

The first PUT returned422 because both `contexts` and `checks` were supplied to a mutually exclusive schema. Full error was reviewed; fresh preflight confirmed no policy change, and the corrected checks-only request/readback succeeded. This was validation failure, not an authorization or automatic-approval rejection; no access control was bypassed.

**FACT-OFFICIAL:** GitHub provides separate settings for required checks, their app, administrator enforcement and pull-request reviews. Use the actual observed check identity and reconcile existing policies before replacing them. [Official branch-protection API](https://docs.github.com/en/rest/branches/branch-protection#update-branch-protection), reviewed2026-10-31.

**LIMIT:** This makes the bounded guard mandatory in the configured workflow. It does not prove no leak, prevent an owner from later changing policy, purge retained history, rotate credentials or validate Origin protection. Known-value/manual/media audits remain separate. This configuration step changed no production infrastructure and rewrote no shared Git history.
