# بستهٔ تصمیم مالک — فعال‌سازی indexability محدود (۱۳ نوامبر ۲۰۲۶، نسخهٔ ۳ پس از دو بازبینی Codex)

وضعیت: **WAITING_FOR_OWNER** — این سند فقط برای تصمیم شماست؛ هیچ اجرایی بدون اجازهٔ صریح انجام نمی‌شود. این نسخه اصلاح‌شدهٔ بازبینی Codex (۱۲ نوامبر) است.

## چهار مجوز جدا در PR94 (قبول یکی به بقیه تعمیم نمی‌یابد)

PR94 صریحاً «چهار تصمیم مستقل» را مستند کرده: سه گام زیر **به‌علاوهٔ merge خود PR94**. یعنی حتی بعد از موافقت با گام‌ها، ادغام شاخهٔ PR94 در main هم یک تأیید جداست.

| # | تصمیم | دامنهٔ واقعی | حالت فعلی |
|---|---|---|---|
| M0 | ادغام شاخهٔ PR94 در main | ۱۰۷ فایل: صفحات تصمیم‌یار + ماژول سیاست ایندکس + runtime فروشگاه + آزمون‌ها؛ **شامل runtime اجرایی است** | باز؛ CI آن تاریخی است (run 42503696771 برای ec7eb0a) — پیش از ادغام، CI تازهٔ head لازم است |
| D1 | انتشار صفحات تصمیم‌یار | scope `tehnet-commercial-decision-20261108-v2`: **۱۰ صفحه (۵ موجود به‌روزشده + ۵ تازه)** + **۱۵ فایل runtime** (decision-aids: CSV/print PHP) — نه body-only؛ rollback شامل فایل‌های runtime هم هست | صفحه‌ها فقط در PR94 هستند |
| D2 | نصب خاموش ماژول سیاست ایندکس | scope `tehnet-index-runtime-20261108-v1`: `class-index-policy.php` + bootstrap Core با checksum؛ **بدون option** → رفتار سایت دقیقاً مثل الان | ماژول در production نیست |
| D3 | فعال‌سازی allowlist ۱۶ URL — **فقط پس از اتمام و تأیید D1/D2 و recovery اجباری** | scope `tehnet-index-allowlist-20261108-v1`: فقط ساخت یک option دقیق (path+ID)؛ `blog_public=0` سراسری دست‌نخورده | همهٔ صفحه‌ها الان `noindex, nofollow` |

## دقیقاً چه چیزی ایندکس می‌شود؟ (۱۶ URL از activation-manifest)

۱۱ موجود: `/`، `/services/`، `/about/`، `/contact/`، `/technical-methodology/`، `/services/voice-network-readiness/`، `/services/remote-support/`، `/services/mikrotik-tehran/`، `/services/network-setup-tehran/`، `/services/network-support-tehran/`، `/services/network-tehran/` — ۵ تازهٔ D1: `/network-support-contract-guide/`، `/network-project-proposal-checklist/`، `/business-server-planning-guide/`، `/server-backup-restore-acceptance/`، `/services/server-virtualization-tehran/`.

**خارج از allowlist (noindex می‌ماند):** مسیرهای خصوصی واقعی مستند در PR94 — `cart-2`، `tn-checkout`، `tn-account`، `support`، `b2b`، shop/product، wp-admin، preview و هر query — به‌علاوهٔ exceptions کامل `index-policy.json`. هیچ تغییری در AI-crawler policy، CAPTCHA، پرداخت یا دسترسی‌ها.

## امنیت، محدودیت‌های صادقانه و بازگشت

- **شرط اجباری ورود به D1/D2/D3 (طبق بازبینی Codex):** recovery واقعاً تأییدشده شامل (الف) مقصد off-host + یک بازیابی آزمایشی کامل از آن، و (ب) rehearsal بازیابی wp-content؛ فقط backup same-host کافی نیست. backup تازه + checksum قبل از هر گام (الگوی ۱۱ نوامبر).
- **محدودیت احرازشده:** recovery آزموده‌شده same-host و DB-only است؛ بازیابی wp-content و مقصد off-host **آزمون نشده**. دیسک سرور ۸۴٪ پر. تا تعیین مقصد off-host توسط شما، اجرای D2/D3 توصیه نمی‌شود (D1 هم بهتر است بعد از آن).
- Rollback کامل هر گام: D3 = حذف option؛ D2 = بازگردانی bootstrap/class به ترتیب معکوس؛ D1 = بازیابی body **به‌همراه عنوان/چکیده‌های تغییرکرده** و بازگرداندن ۵ صفحهٔ تازه به وضعیت draft، و حذف/بازگردانی فایل‌های runtime از journal. `blog_public=0` هیچ‌وقت تغییر نمی‌کند.
- هر تعارض noindex/Disallow مؤثر در لحظهٔ انتشار → توقف و rollback محدود.
- سitemap هسته فقط همین ۱۶ URL را خواهد داشت؛ ثبت در Search Console بعد از D3 و با یک ورود شما.

## درخواست دقیق

پاسخ ممکن: «M0 فقط» / «M0+D1» / «M0+D1+D2» / «M0+D1+D2+D3» — توجه: D3 فقط بعد از اتمام و تأیید D1/D2 و تأیید recovery اجباری فعال می‌شود. یا اصلاح لیست ۱۶ URL. بدون پاسخ صریح، همه WAITING_FOR_OWNER می‌مانند و کارهای مستقل ادامه می‌یابد.
