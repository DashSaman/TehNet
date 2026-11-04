# کشف جزئیات خدمت از کاتالوگ —۴نوامبر۲۰۲۶

وضعیت: DEPLOYED_VERIFIED؛ PR80/CI41853568495 ادغام و main4002d5a با payload برابر staging منتشر شد؛ source `5e6e3e9f1e3f8f57b666fb56587b0db1129d47f4`. دو کارت سرور و شعب در همان Services8، علاوه بر درخواست مستقیم، یک پیوند توصیفی به ماژول‌های منتشرشدهٔ ID33 می‌گیرند. صفحه/فرم/backend تازه یا ویرایش Home وجود ندارد. منبع قدیمی کاتالوگ تغییر نمی‌کند؛ artifact جدید و scope فقط post_content8 با0runtime-file است.

- `/services/#server-planning` → `/services/network-setup-tehran/#server-project-brief` → فرم فعلی با `server-scoping`.
- `/services/#branch-planning` → `/services/network-setup-tehran/#branch-connectivity-brief` → فرم فعلی با `wifi-branch-scoping`.

راهنمای رسمی [Google: پیوند قابل crawl و anchor توصیفی](https://developers.google.com/search/docs/crawling-indexing/links-crawlable) در4نوامبر خوانده شد؛ این تغییر از لینک واقعی a/href و عنوان مرتبط استفاده می‌کند، بدون ساخت صفحهٔ هم‌نیت. noindex عمدی حفظ است؛ این کار ادعای indexing/rank/lead ندارد.

آزمون واحد scope ابتدا به علت Unapproved release scope قرمز شد؛ پس از ثبت،30آزمون اجرا شد:29PASS/1SKIP مربوط به symlink Windows. Node syntax موفق؛ native44 و مرورگر116 موفق؛ preflight/apply/repeat/rollback/repeat، رد Home/HTML خام/shortcode ناشناس و drift، بازیابی دقیق تمام داده/revision/fixture/runtime تأیید شد. پیش از تغییر، نبود دو پیوند در سایت زنده بازتولید شد.0تیکت تازه و0تغییر production در این qualification. [receipt و تصاویر قبل/بعد](../evidence/2026-11-04/service-discovery/native-staging.json). پذیرش باید مسیر واقعی کارت→جزئیات→context/nonce/action موجود، desktop/mobile/no-JS و بازیابی دقیق fixture/data/runtime را نشان دهد. گیت Services-only، raw HTML، shortcode ناشناس و تصاحب Home نیز در native بررسی می‌شود.

انتشار واقعی تنها post_content8، با backup تازه/checksum/drift و حفظ داده/25قلم/runtime/خانه/منو/پرداخت/noindex/CAPTCHA انجام شد. [receipt زنده](../evidence/2026-11-04/service-discovery/production-verification.json) و116بررسی مستقل مرورگر زنده،0ارسال فرم. تصاویر live کارت‌ها کنار receipt هستند. این release دوباره اجرا نشود. گام مستقل بعد: تصمیم‌یار دستی عیب‌یابی؛ انتقال دانش service-depth در -SEO#25 با CI41855380111 ادغام شد. Issues63/75 باز؛ MyTel read-only، پرداخت، CAPTCHA و همهٔ گیت‌های امنیتی حفظ‌اند.
