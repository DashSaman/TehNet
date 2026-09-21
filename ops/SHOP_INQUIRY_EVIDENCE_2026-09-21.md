# TehNet Shop / Physical Inquiry Evidence — 2026-09-21

## فارسی

### محدوده اجرا
- WooCommerce به‌عنوان هسته کاتالوگ TehNet نصب و فعال شد.
- محصولات فیزیکی در این فاز فقط با CTA «استعلام قیمت» کار می‌کنند؛ خرید مستقیم، Checkout و Payment فعال نیست.
- دسته مالک روترهای MikroTik روی `/shop/mikrotik-routers/` ایجاد شد.
- هیچ محصول، قیمت، موجودی، امتیاز یا زمان ارسال ساختگی در production ایجاد نشده است.

### Recovery point و سازگاری
- Backup: `/root/tehnet-backups/20260921-021149`
- WordPress: `7.1.1`
- PHP: `8.3.32`
- MariaDB: `11.4.12-MariaDB-ubu2404`
- WooCommerce: `11.1.1`
- DB، `wp-content`، compose، env و Nginx قبل از deploy ذخیره و archiveها اعتبارسنجی شدند.

### تنظیمات فروشگاه
- Shop page ID: `9`; Currency: `IRR`.
- Cart / Checkout / My Account IDs: `0 / 0 / 0`.
- Built-in gateways: `bacs=no`, `cheque=no`, `cod=no`.
- Product category base: `shop`; Product base: `/product/`.
- MikroTik category term ID: `17`.
- تعداد محصولات واقعی بعد از bootstrap و بعد از smoke: `0`.

### Live SEO / Route gate
- `/shop/`: Public + Origin = HTTP 200، دقیقاً یک H1، canonical صحیح `https://tehnet.ir/shop/` و `noindex,nofollow`.
- `/shop/mikrotik-routers/`: Public + Origin = HTTP 200، دقیقاً یک H1، canonical صحیح `https://tehnet.ir/shop/mikrotik-routers/` و `noindex,nofollow`.
- Shop زنده لینک دسته MikroTik و متن «استعلام قیمت» را نمایش می‌دهد.
- اولین live gate نشان داد archiveهای Woo canonical ندارند؛ regression test ابتدا RED شد، سپس canonical مخصوص Shop/product-category در `tehnet-core` اضافه و هر دو مسیر دوباره PASS شدند.

### Inquiry smoke test
- یک محصول فیزیکی hidden با SKU تصادفی `TEHNET-SMOKE-*` فقط برای smoke ساخته شد.
- ثبت خصوصی `tn_inquiry`، نرمال‌سازی موبایل/تعداد، metadata و duplicate protection تست شد.
- درخواست تکراری همان محصول/موبایل/تعداد با `WP_Error duplicate` رد شد.
- محصول virtual به‌درستی از policy استعلام فیزیکی خارج ماند.
- `COMMERCE_LIVE_SMOKE=PASSED`.
- Cleanup: `SMOKE_PRODUCTS_LEFT=0` و `SMOKE_INQUIRIES_LEFT=0`.

### ایزولیشن و وضعیت Launch
- `blog_public=0` و `noindex,nofollow` حفظ شد.
- TehNet فقط روی `127.0.0.1:18082` bind است.
- `nginx -t` PASS شد.
- fingerprint کانتینر/image/port سرویس‌های غیر TehNet قبل و بعد byte-for-byte یکسان بود.
- هیچ container یا Nginx restart انجام نشد.

## English

### Scope
- WooCommerce was installed and activated as TehNet's catalog foundation.
- Physical products are inquiry-only; direct purchase, checkout and payment are not enabled in this phase.
- The MikroTik router owner category is live at `/shop/mikrotik-routers/`.
- No fabricated product, price, stock, rating or shipping-time data was seeded.

### Recovery point / compatibility
- Backup: `/root/tehnet-backups/20260921-021149`
- WordPress `7.1.1`; PHP `8.3.32`; MariaDB `11.4.12-MariaDB-ubu2404`; WooCommerce `11.1.1`.
- Database, `wp-content`, compose, env and Nginx configuration were captured and validated before deployment.

### Store configuration
- Shop page ID `9`; currency `IRR`.
- Cart / Checkout / My Account page IDs: `0 / 0 / 0`.
- Built-in gateways: `bacs=no`, `cheque=no`, `cod=no`; no enabled gateway was found.
- Product-category base `shop`; product base `/product/`; MikroTik term ID `17`.
- Real product count remained `0` after bootstrap and smoke cleanup.

### Live route / SEO gate
- `/shop/` and `/shop/mikrotik-routers/` both returned Public + Origin HTTP 200, exactly one H1, exact canonical and `noindex,nofollow`.
- The live Shop contains the MikroTik category link and inquiry copy.
- Initial live verification exposed missing Woo archive canonicals. A RED regression contract was added, archive canonical output was implemented, and both routes passed after redeployment.

### Inquiry smoke / isolation
- A temporary hidden `TEHNET-SMOKE-*` physical product verified private inquiry persistence, normalization, metadata, duplicate rejection and virtual-product exclusion.
- `COMMERCE_LIVE_SMOKE=PASSED`; cleanup left `0` smoke products and `0` smoke inquiries.
- `blog_public=0`, binding `127.0.0.1:18082` and valid Nginx configuration were preserved.
- The non-TehNet runtime fingerprint matched byte-for-byte before and after deployment; no container or Nginx restart was performed.
