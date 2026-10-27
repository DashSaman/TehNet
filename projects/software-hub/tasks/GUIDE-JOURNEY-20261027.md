# GUIDE-JOURNEY-20261027 — آزمون سفر کاربر راهنمای نصب آفلاین و رفع باگ نصاب

مالک: ایجنت توسعه (نوبت دوم، ۲۷ اکتبر ۲۰۲۶). شاخه: `feat/software-hub-gap-20261027`. روش: اجرای دقیق فرمان‌های خود راهنما در دو کانتینر تازهٔ `ubuntu:24.04` (ساخت با شبکه / نصب با `--network none`).

## یافتهٔ باگ (واقعی، مسدودکنندهٔ کاربر)

- مسیر: راهنمای عمومی فعلی → ساخت kit مطابق بخش ۱ (موفق، ۹۵.۸ ثانیه، ۵۳MB، ۵۸/۵۸ بسته با هش کامل) → نصب بخش ۲ در اوبونتوی خام → **شکست apt**: `Failed to fetch file:.../dists/<suite>/.../Packages` و سپس «does not have a Release file».
- ریشهٔ اصلی: مخزن `file:` داخل `$HOME` کاربر root (پوشهٔ 0700) توسط apt با کاربر سندباکس `_apt` خوانده نمی‌شود → InRelease با `Ign` رد می‌شود → fallback به `Release` (در kit نیست، طراحی درست) → خطا. امضا (gpgv دستی: VALIDSIG کلید رسمی) و تطابق هش Packages.xz با InRelease هر دو سالم بودند.
- چرا آزمون‌های موتور نمی‌دیدندش: محیط آزمون موتور مخزن را در مسیر جهان‌خوانا (`/repo`) و خارج از `$HOME` نصب می‌کند؛ همان شکاف «راهنما در محیط واقعی کاربر آزمون نشده» که در بریفینگ §6و هشدار داده بود.

## اصلاح (کمینه، حفظ همهٔ گاردها)

- افزودن گزینهٔ `-o 'APT::Sandbox::User=root'` به آرایهٔ OPTIONS نصاب (فقط زمان اجرای نصاب به‌عنوان root؛ سازگار با راهنمای «sudo را حذف کنید»).
- نصاب متنِ داخل پروفایل است و با `INSTALLER_SHA256` در `offline_kit.py` پین شده — هر دو با هم در:
  - مخزن: `profiles/noble-devtools-amd64/manifest.json` + `tools/offline_kit.py`
  - عملیاتی: seed ‏`/opt/tehnet-software/operations/offline-devtools-20261018/qualification/profiles/.../manifest.json` + ‏`offline-refresh-20261018-v3/tools/offline_kit.py`
  - پشتیبان هر ۴ فایل قبل از تغییر: `/root/tehnet-backups/pre-installer-fix-*`

## آزمون‌های واقعی این نوبت

1. بازاجرا با نصاب اصلاح‌شده در همان کانتینر بدون‌شبکه: **`OFFLINE_INSTALL_PASS: exact package versions and dpkg audit verified.`**
2. بلوک تأیید راهنما: git 2.43.0، jq→42، python→42، rsync 3.2.7، OpenSSH 9.6p1، `dpkg --audit` خالی.
3. تست‌های واحد: `tests.test_offline_refresh` ۱۰/۱۰ سبز (پین جدید)؛ `validate_profile` با نصاب جدید VALID.
4. انتشار: **اجرا اجباری نشد**؛ نسل بعدی تایمر (بعدی ~۰۶:۲۳ UTC) به‌طور خودکار پروفایل/نصاب/راهنمای هش‌دارِ جدید را با تأیید کامل منتشر می‌کند (نگاشت انتشار: کپی v3 از `tools/offline_kit.py` + پروفایل seed → publication → nginx snippet).

## محدودیت صریح

- این آزمون در کانتینر Docker با شبکهٔ قطع انجام شد، نه VM بوت‌شده — طبق بریفینگ، کاربراسپیس ≠ VM ادعا نمی‌شود؛ ثبت شد به‌عنوان «سفر کاربر در کانتینر ایزوله».
- تا انتشار نسل جدید توسط تایمر، نسل منتشرشدهٔ فعلی هنوز نصاب قدیمی دارد؛ در STATUS قید شد.

## پاک‌سازی

کانتینرهای آزمون (sh-build/sh-offline) و `/tmp/sh-kit` حذف شدند.
