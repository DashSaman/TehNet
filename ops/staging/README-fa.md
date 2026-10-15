# محیط محلی فروشگاه

این پوشه فقط برای localhost و داده ساختگی است؛ الگوی نصب روی سرور مشترک فعلی نیست. Docker Desktop باید روشن باشد. محیط آزمایش‌شده WordPress 7.1.3، WooCommerce 11.1.1، PHP 8.3، ERPNext 16.51.0 و Frappe 16.52.0 است. تصویر WordPress برچسب متغیر دارد؛ در انتشار، digest و سازگاری با نسخه واقعی تولید باید قفل شوند.

از ریشه مخزن اجرا کنید؛ روی این دستگاه پیشوند `rtk proxy` را برای فرمان‌ها نگه دارید:

```powershell
rtk proxy python ops/staging/prepare-local.py
rtk proxy python ops/staging/fetch-fonts.py
rtk proxy docker compose -p tehnet-erp-stage --env-file ops/staging/.env -f ops/staging/erp.compose.yml -f ops/staging/erp-app.compose.yml up -d
rtk proxy docker compose -p tehnet-woo-stage --env-file ops/staging/.env -f ops/staging/woo.compose.yml up -d
```

وابستگی‌های WP-CLI و Woo با SHA256 ثبت‌شده کنترل می‌شوند. رمزها فقط در `.env` نادیده‌گرفته‌شده ساخته می‌شوند. فایل فونت OFL نیز فقط در `.local/fonts` می‌ماند. پوشه `.local`، dumpها، رمزها و فونت باینری را commit نکنید.

راه‌اندازی اولیه WordPress باید با URL `http://localhost:18083`، حساب محلی `tehnet-stage` و رمز خصوصی همین محیط انجام شود؛ رمز را در فرمان قابل نمایش یا log قرار ندهید. WP-CLI در `/stage/wp-cli.phar` و بسته Woo در `/stage/woocommerce.zip` در دسترس است. سپس افزونه‌های `woocommerce`، `tehnet-core` و `tehnet-store` و قالب `tehnet` را فعال کنید. `WC_Install::create_pages()`، ارز IRR، کشور IR، HPOS، ساختار `/%postname%/`، زبان fa_IR و `blog_public=0` تنظیم شوند. BACS/COD/cheque خاموش بمانند.

```powershell
rtk proxy docker exec tehnet-woo-stage-woo-1 php /stage/wp-cli.phar --allow-root --path=/var/www/html eval-file /local-seed.php
rtk proxy docker exec tehnet-woo-stage-woo-1 php /stage/wp-cli.phar --allow-root --path=/var/www/html tehnet catalog import /catalog/saieedshabake-2026-10-15.json --apply
```

ERP یک سایت `frontend` می‌سازد. در setup wizard فقط شرکت ساختگی **TehNet Sandbox** با اختصار TNS، کشور Iran، ارز IRR و سال مالی 2026-03-21 تا 2027-03-20 بسازید. سپس `bench --site frontend install-app tehnet_erp` و `bench --site frontend execute tehnet_erp.sandbox.setup` را داخل backend اجرا کنید. این seed به سایت و متغیر محیطی محلی محدود است؛ داده آن موجودی واقعی تهران نتورک نیست. `sandbox.credentials` فقط برای گرفتن مستقیم و خصوصی API key/secret حساب ماشینی است؛ خروجی آن را در ترمینال چت چاپ نکنید. مقدارها در `.env` محلی با نام ERP_API_KEY/ERP_API_SECRET قرار می‌گیرند و سرویس Woo دوباره ایجاد می‌شود تا env را بگیرد.

تنظیم‌کننده ERP اکنون خود برنامه اتصال را mount می‌کند تا restart آن را از `sites/apps.txt` حذف نکند. پس از اصلاح یک محیط قدیمی، `bench --site frontend clear-cache` لازم است. اجرای setup موجود را روی اطلاعات واقعی یا شرکت دیگری تکرار نکنید.

## مشاهده و آزمون

- فروشگاه: `http://localhost:18083/shop/?tn_preview=1`؛ پیش‌نویس‌ها فقط با ورود مدیر در local دیده می‌شوند.
- عملیات: `http://localhost:18083/wp-admin/admin.php?page=tn-store`.
- ERP: `http://localhost:18084`؛ منوهای انگلیسی این نسخه هنوز ترجمه کامل فارسی ندارند.
- حساب مشتری: `http://localhost:18083/my-account/`؛ fixture را فقط با seed-account.php و wrapper خصوصی بسازید.
- حمل‌ونقل، پرداخت و اعلان واقعی خاموش‌اند. local-safety.php ایمیل را متوقف می‌کند و موفقیت تحویل گزارش نمی‌کند.

فرمان‌های آزمون و حدود شواهد در `docs/testing.md` ثبت شده‌اند. سرویس‌ها و volumeها را برای ادامه حفظ کنید؛ `down -v`، prune عمومی یا حذف پایگاه‌های قبلی لازم نیست.

## تنظیم اتصال در انتشار

مقدارهای سروری `TEHNET_ERP_URL`، `TEHNET_ERP_SITE`، `TEHNET_ERP_API_KEY`، `TEHNET_ERP_API_SECRET` و `TEHNET_ERP_STORE_ID` لازم‌اند. URL در production فقط HTTPS است. `TEHNET_VERIFIED_GATEWAYS` باید فقط نام adapterهای واقعاً آزموده‌شده سمت سرور را داشته باشد. `TEHNET_ERP_RESERVATIONS_ENABLED=true` به‌تنهایی خرید را فعال نمی‌کند. اعتبارنامه درگاه یا ERP را در فرم محصول، مرورگر یا Git قرار ندهید.
