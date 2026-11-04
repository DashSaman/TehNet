# کشف جزئیات خدمت از کاتالوگ —۴نوامبر۲۰۲۶

وضعیت: SOURCE_READY_NOT_DEPLOYED. دو کارت سرور و شعب در همان Services8، علاوه بر درخواست مستقیم، یک پیوند توصیفی به ماژول‌های منتشرشدهٔ ID33 می‌گیرند. صفحه/فرم/backend تازه یا ویرایش Home وجود ندارد. منبع قدیمی کاتالوگ تغییر نمی‌کند؛ artifact جدید و scope فقط post_content8 با0runtime-file است.

- `/services/#server-planning` → `/services/network-setup-tehran/#server-project-brief` → فرم فعلی با `server-scoping`.
- `/services/#branch-planning` → `/services/network-setup-tehran/#branch-connectivity-brief` → فرم فعلی با `wifi-branch-scoping`.

راهنمای رسمی [Google: پیوند قابل crawl و anchor توصیفی](https://developers.google.com/search/docs/crawling-indexing/links-crawlable) در4نوامبر خوانده شد؛ این تغییر از لینک واقعی a/href و عنوان مرتبط استفاده می‌کند، بدون ساخت صفحهٔ هم‌نیت. noindex عمدی حفظ است؛ این کار ادعای indexing/rank/lead ندارد.

آزمون واحد scope ابتدا به علت Unapproved release scope قرمز شد؛ پس از ثبت،30آزمون اجرا شد:29PASS/1SKIP مربوط به symlink Windows. Node syntax موفق؛ native و مرورگر این بسته هنوز NOT_RUN. پذیرش باید مسیر واقعی کارت→جزئیات→context/nonce/action موجود، desktop/mobile/no-JS و بازیابی دقیق fixture/data/runtime را نشان دهد. گیت Services-only، raw HTML، shortcode ناشناس و تصاحب Home نیز در native بررسی می‌شود.

گام بعد: native qualification، PR/CI و فقط در دامنهٔ مجاز با backup/checksum/drift/rollback؛ تا receipt، منتشرشده محسوب نشود. Issues63/75 باز؛ MyTel read-only، پرداخت، CAPTCHA و همهٔ گیت‌های امنیتی حفظ‌اند.
