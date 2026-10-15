# شواهد آزمون فروشگاه — ۱۵ اکتبر ۲۰۲۶

این نتایج مربوط به اجرای واقعی **محلی** WordPress/WooCommerce و ERPNext با داده ساختگی‌اند. نتیجه هیچ‌یک به معنای پرداخت از درگاه، تحویل پیامک، اتصال حمل واقعی یا آمادگی انتشار نیست.

| حوزه | نتیجه و شاهد |
|---|---|
| normalizer کاتالوگ و قرارداد ERP | ۲۰ unittest؛ هویت یکتا، عدم انتقال قیمت/stock، دسته رسمی، ادعای تأییدنشده، decimal دقیق و تضاد hash |
| پول و فروش | ۲۰ بررسی PHP؛ تبدیل دقیق ریال/تومان، ارقام فارسی، رد float و fractional rial، بسته‌ماندن فروش ناقص |
| واردسازی بومی | ۳۱ بررسی؛ ۲۵ محصول، تکرار بدون duplicate، حفظ ویرایش انسان، rollback کامل پیش از تغییر و trash قابل بازگشت |
| دسترسی Core | ۴ بررسی واقعی WordPress؛ مدیر و staff مجاز، مشتری غیرمجاز به اسناد خصوصی |
| نقش عملیات | ۴ نقش واقعی؛ فروش/انبار/مالی/پشتیبانی و منع دسترسی نامرتبط |
| اتصال Woo به ERP | سفارش متری واقعی، timeout ساختگی حمل شبکه، outbox پایدار، replay، لغو و عدم احیای سفارش لغوشده در retry |
| چرخه ERP | رزرو آخرین واحد هم‌زمان، انقضا، callback تکراری، اختلاف مبلغ، تحویل، مرجوعی جزئی/کامل، موجودی متری، GL و تسویه کارمزد؛ `qa/store-2026-10-15/erp-results.json` |
| تخفیف و ارسال | سفارش ۲۰۰۰ ریالی با ۱۰۰ تخفیف و ۲۰۰ ارسال؛ دو مرجوعی ۱۰۵۰ ریالی با سهم ارسال ۱۰۰، جمع دقیق ۲۱۰۰ |
| تطبیق سفارش | ۷ بررسی؛ tracking، فاکتور ERP، بازپرداخت بومی Woo، تکرار تطبیق بدون duplicate و برگشت کامل |
| مرورگر | Edge/Playwright؛ RTL، پیش‌نویس خصوصی، compare/wishlist، persistence، Escape، موبایل بدون overflow و بدون خطای JS |
| حساب مشتری | فاکتور خود، 403 برای فاکتور دیگر، رد CSRF، درخواست بررسی مرجوعی، موبایل و فرم کامل عملیات |
| بازیابی | SQL و فایل‌های Woo در DB/volume تازه؛ ERP در سایت تازه، تطبیق fingerprint نه جدول منتخب شامل مجوزها کسب‌وکار؛ `recovery-results.json` |
| regression موجود | ۱۶ قرارداد shell با LC_ALL=C و ۷ آزمون visual موجود با Python UTF-8 |

## بازاجرای آزمون‌ها

از ریشه مخزن، با runtimeهای حاضر:

```powershell
rtk proxy python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
rtk proxy docker exec tehnet-woo-stage-woo-1 php /stage/wp-cli.phar --allow-root --path=/var/www/html eval-file /tests/store-policy.php
rtk proxy docker exec tehnet-woo-stage-woo-1 php /stage/wp-cli.phar --allow-root --path=/var/www/html eval-file /tests/catalog-integration.php
rtk proxy docker exec tehnet-woo-stage-woo-1 php /stage/wp-cli.phar --allow-root --path=/var/www/html eval-file /tests/commerce-capabilities.php
rtk proxy docker exec tehnet-woo-stage-woo-1 php /stage/wp-cli.phar --allow-root --path=/var/www/html eval-file /tests/store-roles.php
rtk proxy docker exec tehnet-woo-stage-woo-1 php /stage/wp-cli.phar --allow-root --path=/var/www/html eval-file /tests/erp-bridge.php
rtk proxy docker exec tehnet-woo-stage-woo-1 php /stage/wp-cli.phar --allow-root --path=/var/www/html eval-file /tests/erp-lifecycle.php
rtk proxy python -u ops/staging/test-erp.py
```

آزمون‌ها fixture مستقل می‌سازند و داده واقعی را حذف نمی‌کنند. ERP سندهای submitted ساختگی را برای حسابرسی نگه می‌دارد؛ تعداد اسناد sandbox با هر اجرا افزایش می‌یابد. تست importer فقط fixtureهای خودش را trash می‌کند؛ ۲۵ پیش‌نویس اصلی باقی می‌مانند. benchmark سرعت یا آزمون بار انجام نشده است.

برای مرورگر، `PLAYWRIGHT_MODULE` را به بسته Playwright نصب‌شده معرفی کنید و scriptهای `tests/browser/` را با Node اجرا کنید؛ این دستگاه Edge موجود را استفاده می‌کند و مرورگر دیگری دانلود نشده است. رمزها از `.env` خوانده می‌شوند و در خروجی چاپ نمی‌شوند.

## خطاهایی که واقعاً کشف و اصلاح شدند

- mapping اشتباه capability در CPTها دسترسی مدیر Woo را هم مختل می‌کرد؛ capability اختصاصی متا جایگزین شد.
- مرتب‌سازی پیش‌فرض دسته Woo فیلتر meta را تغییر می‌داد؛ lookup واردسازی با meta_query و ترتیب صریح اصلاح شد.
- تنظیم‌کننده Docker برنامه custom را از apps.txt حذف می‌کرد؛ mount آن در configurator و پاک‌سازی cache محیط قدیمی اصلاح شد.
- retry رزرو پس از لغو می‌توانست سفارش را دوباره رزرو کند؛ اکنون پیش از retry وضعیت بررسی و رویداد void می‌شود.
- query عمومی سفارش شامل OrderRefund بود و پنل عملیات را fatal می‌کرد؛ type=shop_order و guard نوع اضافه شد. آزمون مرورگر اکنون حضور فرم کامل و سطرهای جدول را هم می‌سنجد.
- تغییر ساعت VM بعضی صفحات محلی را future کرده بود؛ seed فقط صفحات ساختگی محلی را با تاریخ جاری publish می‌کند.
- حساب ماشینی از generic CRUD به رکورد رزرو و رویداد حق نوشتن داشت؛ آزمون HTTP این ایراد را بازتولید کرد. اکنون نقش آن روی دو DocType فقط read است و نوشتن داخلی فقط پس از authorize و در handler کنترل‌شده انجام می‌شود. دو آزمون منفی API عمومی و چرخه مالی کامل پس از اصلاح اجرا می‌شوند.

## حدود پذیرش

خرید کامل موبایلی با **درگاه sandbox معتبر** اجرا نشده، چون ارائه‌دهنده و اعتبارنامه آن مشخص نیست. هیچ callback مرورگر یا شناسه ساختگی به‌عنوان پرداخت واقعی گزارش نمی‌شود. مالیات غیرصفر، سامانه مودیان، سفارش ترکیبی digital/physical و کالاهای سریال/بچ در مرز اتصال فعلی نیاز پیکربندی و آزمون جدا دارند و بسته می‌مانند. ERP native این حوزه‌ها را دارد، اما فعال‌بودن آن‌ها در اتصال حاضر ادعا نمی‌شود.

بازیابی، آزمون تولید نیست. اولین backup بومی ERP به خطای اعتبار زمانی گواهی MariaDB محلی خورد؛ فقط همان فرمان backup/restore محلی با MYSQL_HOME موقت و غیرفعال‌کردن بررسی گواهی اجرا شد. تنظیم TLS برنامه و production عوض نشد. اصلاح ساعت/گواهی و آزمون با TLS معتبر شرط انتشار است.
