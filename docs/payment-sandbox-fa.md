# پرداخت آزمایشی: زرین‌پال v4

وضعیت: آداپتور آزمایشی خاموش به صورت پیش‌فرض؛ **آماده فروش واقعی اعلام نمی‌شود**. محیط production در خود آداپتور رد می‌شود و هیچ نشانی درگاه واقعی یا تابع استرداد بانکی ندارد.

## انتخاب و مقایسه

| گزینه | شاهد واقعی این مرحله | تصمیم |
|---|---|---|
| زرین‌پال v4 | راهنمای رسمی request/verify و sandbox؛ درخواست واقعی، بازگشت مرورگر و verify اجرا شد | انتخاب برای آزمایش اتصال |
| افزونه رسمی Woo زرین‌پال 5.1.1 | بسته رسمی دانلود و کد مرتبط خوانده شد؛ HPOS/Blocks و sandbox در کد وجود دارند | بدون اصلاح و آزمون بیشتر برای ثبت ERP/پرداخت واقعی فعال نشد |
| NextPay | صفحه رسمی API/REST قابل خواندن بود؛ سندباکس قابل اجرا در صفحه بررسی‌شده تأیید نشد | گزینه جایگزین؛ مقایسه هزینه/قرارداد بدون اطلاعات واقعی انجام نشد |
| IDPay و pay.ir | بازیابی مستندات رسمی در این اجرا موفق نبود | قابلیت/هزینه/دسترسی آن‌ها حدس زده نشد |

منابع: [اتصال زرین‌پال](https://www.zarinpal.com/docs/paymentGateway/connectToGateway)، [sandbox رسمی](https://www.zarinpal.com/docs/paymentGateway/sandBox)، [افزونه رسمی در WordPress](https://wordpress.org/plugins/zarinpal-woocommerce-payment-gateway/)، [API رسمی NextPay](https://nextpay.org/nx/docs)، [Woo Gateway API](https://developer.woocommerce.com/docs/features/payments/payment-gateway-api/)، [Woo Blocks API](https://developer.woocommerce.com/docs/block-development/extensible-blocks/cart-and-checkout-blocks/checkout-payment-methods/payment-method-integration/).

بسته بررسی‌شده: `zarinpal-woocommerce-payment-gateway.5.1.1.zip`، SHA256:
`82eede70a9c3e1fd1f49c401560ee29b0fa3b20e39c8a4b5faf6b59ca27821ad`.

دو ملاحظه مشخص در فایل `class-wc-gateway-zarinpal.php` همین بسته: helper پاسخ 101 را برمی‌گرداند، ولی شاخه callback در خطوط 452–463 فقط 100 را موفق می‌داند؛ مسیر refund در خط 496 مبلغ را بدون توجه به currency در 10 ضرب می‌کند. برای فروشگاه IRR و ثبت مالی idempotent، این رفتارها نیازمند اصلاح و آزمون‌اند. این بررسی محدود، ممیزی جامع افزونه یا اثبات سوءاستفاده نیست. افزونه رسمی نصب/فعال نشده و فایل‌های آن دستکاری یا وارد مخزن نشده‌اند.

## رفتار آداپتور آزمایشی

- سرور فقط `https://sandbox.zarinpal.com` را با TLS، timeout محدود و بدون دنبال‌کردن redirect فراخوانی می‌کند. authority باید دقیقاً 36 کاراکتر و با S شروع شود.
- مبلغ مثبت و صحیح IRR از سفارش خوانده و قبل از درخواست ماندگار می‌شود. قیمت از callback یا مرورگر گرفته نمی‌شود.
- هر سفارش فقط یک تلاش دارد؛ timeout درخواست به حالت unknown می‌رود و تراکنش تازه خودکار نمی‌سازد. authority قبلی فقط با رزرو تازه ERP دوباره استفاده می‌شود.
- callback به سفارش، authority، مبلغ، merchant آزمایشی و token تصادفی 256 بیتی متصل است. Status=OK به تنهایی معتبر نیست؛ verify سمت سرور و ref_id لازم است. کدهای 100 و 101 هر دو قابل بازیابی‌اند.
- receipt پیش از payment_complete ذخیره و به یک سفارش محدود می‌شود. قفل سفارش از دو اجرای هم‌زمان جلوگیری می‌کند. وضعیت و مبلغ پس از پاسخ شبکه از data store بومی Woo دوباره خوانده می‌شوند.
- پرداخت پس از لغو، اختلاف مبلغ، رسید متعارض یا ERP خارج دسترس روی hold/تطبیق می‌ماند. callback NOK به تنهایی رزرو را لغو نمی‌کند؛ انقضای معتبر ERP موجودی را آزاد می‌کند.
- فقط محصولات فیزیکیِ جداگانه با متای `_tn_sandbox_fixture=yes` پذیرفته می‌شوند. اقلام واقعی کاتالوگ را با این برچسب علامت نزنید. هر ۲۵ قلم اصلی همچنان draft و بدون داده فروش تأییدشده‌اند.
- ثبت کلاسیک و Blocks پیاده شده است؛ اطلاعات کارت یا tokenization جمع نمی‌شود و refund بانکی وجود ندارد. **خرید کامل native و موبایل این آداپتور هنوز تأیید نشده است.**

## شواهد تازه

`qa/store-2026-10-15/zarinpal-request.json` و `zarinpal-provider-probe-fresh.json`:
درخواست مبلغ 11000 IRR، کلیک پرداخت ساختگی روی صفحه واقعی sandbox و بازگشت localhost؛ verify مبلغ 11001 با HTTP 401 و code=-50 رد شد؛ مبلغ 11000 کد 100 گرفت و تکرار آن کد 101 با همان ref_id داد. این آزمایش مستقلِ پروتکل است؛ هیچ سفارش Woo یا سند ERP از این probe ساخته نشد و هیچ پول واقعی منتقل نشد. UUID آزمایشی عمومی است و credential پذیرنده واقعی نیست. PAN، card hash و اطلاعات شخصی در شواهد نگهداری نمی‌شود.

`payment-verification.json`: 20 assertion پروتکل و 29 assertion ماشین وضعیت با PHP 8.3.35 و HTTP/Woo/ERP ساختگی؛ lint هر 10 فایل PHP افزونه و syntax JavaScript. حذف پشتیبانی 101 در کپی موقت عمداً آزمون را شکست؛ کد اصلی تغییر نکرد و سبز ماند. تست تکرار callback، جعل token/authority، تغییر هم‌زمان مبلغ، لغو حین verify، timeout، رسید مشترک دو سفارش، بازیابی ERP و رد production پوشش داده شده است. این‌ها تست native Woo نیستند.

`erp-results.json`: هر 20 سناریوی HTTP موتور واقعی ERP محلی دوباره گذشت، با انبار و رسید ساختگی مستقل از درگاه. Store API عمومی Woo نیز HTTP 200 و payment_methods خالی داد؛ نشانه فعال‌نبودن فروش/درگاه است، نه آزمون موفق خرید.

در محیط فعلی `docker ps` به named pipe دسترسی ندارد؛ اجازه شبکه این محدودیت را برطرف نکرد. راه‌اندازی مجدد کانتینر، WP-CLI و آزمون اتصال یکپارچه جدید اجرا نشد. Edge مستقل نیز با محدودیت محیط راه نیفتاد؛ بازگشت صفحه sandbox در مرورگر داخلی Codex بررسی شد. نتایج native Woo/مرورگر مرحله قبلی در `local-verification.json` حفظ شده‌اند و نتیجه تازه این آداپتور معرفی نمی‌شوند.

## ادامه آزمون یکپارچه، پس از رفع محدودیت Docker

فقط در محیط محلیِ فعلی با ERP شرکت TNS و اقلام TN-SANDBOX، overlay زیر را **آگاهانه** اعمال کنید؛ در این اجرا اعمال نشده است:

```sh
docker compose -p tehnet-woo-stage --env-file ops/staging/.env -f ops/staging/woo.compose.yml -f ops/staging/payment-sandbox.compose.yml up -d --pull never --no-deps woo
```

سپس در Woo → تنظیمات → پرداخت‌ها، «زرین‌پال — فقط آزمایش» را فعال کنید. محصول جدا با نام صریح «آزمون ساختگی، تحویلی ندارد» بسازید، به TN-SANDBOX-CABLE/Meter در ERP آزمایشی نگاشت کنید، minimum و واحد متر را مشخص و snapshot را تازه کنید. فقط همین محصول ساختگی باید `_tn_sandbox_fixture=yes` داشته باشد؛ این متا با WP-CLI برای ID مشخص همان محصول تنظیم می‌شود. نرخ حمل و آدرس نیز داده ساختگی باشند؛ ارسال ایمیل محلی از قبل مسدود است.

خرید از cart تا Blocks checkout و بازگشت موبایل، ثبت یکتای Sales Invoice/Payment Entry در شرکت آزمایشی، تغییر هم‌زمان وضعیت سفارش و تطبیق hold را native آزمایش کنید. تا آن زمان این معیار پذیرش باز است. آداپتور به‌هیچ‌وجه برای شرکت واقعی ERP، محیط production یا پرداخت واقعی تنظیم نشود.

آزمون قابل اجرا بدون Docker:

```sh
python ops/staging/verify-payment.py --php /path/to/php
python ops/staging/probe-zarinpal.py request --output qa/store-2026-10-15/zarinpal-request.json
# فقط پرداخت ساختگی sandbox را در مرورگر انجام دهید؛ سپس S_AUTHORITY خروجی را جایگزین کنید.
python ops/staging/probe-zarinpal.py verify S_AUTHORITY --output qa/store-2026-10-15/zarinpal-provider-probe-fresh.json
```

بازیابی: گزینه درگاه را خاموش و overlay را حذف کنید و base compose را با همان volume بالا بیاورید. رسید، outbox و attempt را حذف نکنید. برای lock مانده ابتدا پایان اجرای قبلی و وضعیت ERP/درگاه را اثبات کنید؛ قفل را خودکار منقضی نکنید. حالت unknown یا receipt روی hold فقط پس از تطبیق بررسی شود. راه‌اندازی واقعی همچنان تابع backup/restore تولید، تنظیمات معتبر و تأیید صریح مالک است.


## به‌روزرسانی انتشار آنلاین — ۱۵ اکتبر ۲۰۲۶

مطالب محدودیت Docker/عدم استقرار در بخش‌های قبلی، گزارش مراحل پیشین‌اند. وضعیت فعلی: کاتالوگ استعلام عمومی https://tehnet.ir/shop/ و پنل https://tehnet.ir/wp-admin/admin.php?page=tn-store منتشر شده‌اند. ERP و پرداخت واقعی تولید غیرفعال‌اند. صفحه اصلی و theme و سرویس‌های دیگر حفظ شدند.

پشتیبان کامل خصوصی `/root/tehnet-backups/20261015-184219-store-review` شامل SQL، کل WordPress، config/env و Nginx است. همان تولید در DB/volume محلی جدید بازیابی، همه فایل‌ها و ۹ جدول تطبیق و HTTP 200 تأیید شد؛ mail و HTTP خروجی clone بسته است. `production-recovery.json` شاهد است.

انتشار allowlist با `deploy-store-review.py`، import صریح WP CLI مجاز با SHA256 و dry-run پیش‌فرض، سپس انتشار استعلام با `publish-inquiry-catalog.php` انجام شد. import عادی production هنوز بسته است و environment تغییر نکرده. rerun تولید صفر create و ۲۵ skip داد. `ensure-store-pages.php` نگاشت صفحات native منتشرشده را با حفظ draftهای قدیمی درست کرد. `deploy-store-media.py` فایل‌های رسانه/مهر را با backup و guard drift منتشر کرد. جزئیات `production-release.json` و `production-media-release.json`.

برای rollback، افزونه Store را غیرفعال و فقط فایل‌های allowlist از checkpoint مربوط برگردانید. SQL را کورکورانه به عقب نبرید؛ داده/صفحه/audit جدید یا ویرایش انسانی باید تطبیق شود. گزینه coming-soon، متن قبلی shop و وضعیت/عنوان کالای جدید در option `tn_public_inquiry_release_20261015` محفوظ‌اند. صفحه اصلی در این مهاجرت‌ها هدف نبوده است.

آزمون مرورگر تولید در `live-browser.json`: منوی اصلی → shop عمومی، ۲۵ کالای غیرقابل خرید، مقایسه مهمان، تصاویر اختصاصی، چرخش شماتیک، موبایل بدون overflow و HTTP 200 صفحات. Store API خود Woo مقدار قیمت unset را به رشته صفر serialize می‌کند؛ `is_purchasable=false` و `price_html=استعلام` و قیمت ذخیره‌شده خالی است؛ این پیشنهاد فروش رایگان نیست.

خرید native رسمی sandbox محلی با سفارش ۲۵۲ / ۳۵۰۰ ریال و فاکتور ERP و callback تکراری گذشت (`native-payment.json`). هیچ وجه واقعی جابه‌جا نشد. تصویرسازی و مدل گروه کالا دقیق نیستند و با برچسب شماتیک عرضه می‌شوند؛ عکس واقعی/GLB معتبر همچنان وابستگی باز است.
