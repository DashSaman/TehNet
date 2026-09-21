# TehNet Shop / Physical Inquiry Implementation Plan

## خلاصه فارسی

**هدف:** نصب WooCommerce به‌عنوان هسته کاتالوگ TehNet، حفظ `/shop/` به‌عنوان مسیر تجاری، ساخت Owner دسته روترهای MikroTik و تبدیل همه محصولات فیزیکی به حالت «استعلام قیمت» بدون فعال‌کردن پرداخت، checkout، قیمت ساختگی یا indexing.

**معماری:** WooCommerce مالک داده و نمایش محصول/دسته است و `tehnet-core` سیاست تجاری TehNet را اعمال می‌کند. محصول فیزیکی قابل خرید مستقیم نیست، قیمت آن «استعلام قیمت روز» نمایش داده می‌شود و فرم امن استعلام یک رکورد خصوصی `tn_inquiry` در مدیریت WordPress ایجاد می‌کند. هیچ محصول، قیمت، موجودی یا امتیاز جعلی در production seed نمی‌شود.

**محدودیت‌های اصلی:**
- CTA محصول فیزیکی: `استعلام قیمت`
- Owner دسته: `/shop/mikrotik-routers/`
- base دسته `shop` و base محصول `/product/` برای جلوگیری از collision
- Cart / Checkout / Payment در این فاز فعال نمی‌شوند
- `blog_public=0` و `noindex,nofollow` حفظ می‌شوند
- پورت `127.0.0.1:18082` و سرویس‌های غیر TehNet تغییر نمی‌کنند
- فرم استعلام برای مهمان امن است، IP خام ذخیره نمی‌شود و duplicate پنج‌دقیقه‌ای با hash کنترل می‌شود

**مراحل:**
1. Bootstrap امن و idempotent برای WooCommerce و URLهای Shop
2. سیاست Inquiry، validation و ذخیره خصوصی در Admin
3. UI فارسی/RTL و contract محتوای فروشگاه
4. Backup، deploy، smoke test production، cleanup، evidence و merge/push

> جزئیات فنی اجرایی در بخش English زیر آمده و همان منبع اجرای دقیق taskهاست.

## English implementation details

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Install WooCommerce as TehNet's catalog foundation, preserve `/shop/` as the commerce journey, publish the approved MikroTik-router category owner, and make every physical product inquiry-only with secure guest inquiry capture in WordPress admin—without enabling payment, checkout, stale prices, or indexing.

**Architecture:** WooCommerce owns product/category data and rendering. `tehnet-core` owns TehNet-specific commerce policy: non-virtual/non-downloadable products are not directly purchasable, their price is presented as inquiry-required, and a secure form creates a private `tn_inquiry` record. No real product, stock, price or availability is fabricated; production seeds only the category and infrastructure until actual inventory is supplied.

**Tech Stack:** WordPress, WooCommerce, PHP 8.3, TehNet Core plugin, Gutenberg, WP-CLI, Bash contract tests, Docker/MariaDB/Redis/Nginx/Cloudflare.

**Spec:** `docs/superpowers/specs/2026-09-14-tehnet-platform-design.md`

## Global Constraints

- Physical products are nationwide inquiry/order items; current price is confirmed manually because of market volatility.
- Physical-product CTA is `استعلام قیمت`; do not pretend a stale price is live.
- This phase does not implement the manual quote/invoice lifecycle, digital fulfillment, licensing, a rial gateway, crypto payment, cart checkout or order payment.
- Do not seed fake products, stock, prices, ratings or availability. The catalog may be structurally complete while empty.
- Existing Learn/Lab/Services ownership and URLs remain unchanged.
- Product-category owner remains `/shop/mikrotik-routers/`.
- Per current WooCommerce permalink guidance, taxonomy and product bases must be distinct. Use product-category base `shop` and keep the product base `/product/`; never set both to `shop`.
- Production remains `blog_public=0` and rendered `noindex,nofollow` until the explicit launch gate.
- TehNet remains bound to `127.0.0.1:18082`; no Nginx route, Docker project topology or unrelated service may change.
- Every production mutation gets a fresh DB/wp-content/config recovery point and before/after non-TehNet runtime fingerprint.
- TehNet Core must fail gracefully if WooCommerce is temporarily unavailable; no fatal class/function dependency at plugin load time.
- Public inquiry accepts a published WooCommerce product only. Draft/private/trash/unknown IDs are rejected.
- No raw client IP is stored for anti-duplicate logic.

## Current WooCommerce guidance checked 2026-09-21

- WooCommerce current permalink documentation allows a custom product-category base and warns not to use the same base for products and product categories.
- WooCommerce currently recommends PHP 8.3+ and MariaDB 10.6+; current TehNet PHP is already 8.3, and production compatibility must be checked before plugin activation.
- References:
  - https://woocommerce.com/document/permalinks/
  - https://woocommerce.com/document/update-php-wordpress/

## File Structure

- Create `site/plugins/tehnet-core/includes/class-commerce.php` — WooCommerce policy and public inquiry-form rendering.
- Create `site/plugins/tehnet-core/includes/class-inquiries.php` — inquiry validation, persistence, duplicate protection and private admin UI.
- Modify `site/plugins/tehnet-core/tehnet-core.php` — load/register commerce classes and bump TehNet Core version.
- Modify `site/themes/tehnet/style.css` — minimal inquiry-form and inquiry-price presentation.
- Modify `content/pages/shop.html` — truthful phase-1 Shop copy and link to MikroTik router category.
- Create `ops/wp-commerce-bootstrap.sh` — guarded, idempotent WooCommerce installation/configuration/category bootstrap.
- Create `ops/commerce-live-smoke.php` — temporary hidden Woo product + inquiry persistence smoke test with guaranteed cleanup.
- Create `tests/commerce-bootstrap-contract.sh` — bootstrap/permalink/payment-surface contract.
- Create `tests/commerce-inquiry-contract.sh` — hook/security/admin/persistence contract.
- Create `tests/product-inquiry-logic.php` — executable pure-logic tests.
- Create `tests/shop-commerce-content-contract.sh` — content/owner-link contract.
- Create `ops/SHOP_INQUIRY_EVIDENCE_2026-09-21.md` during the production task.
- Modify `PROGRESS.md`, `HANDOFF.md`, `TASKS.md` only after production evidence exists.

## Review Focus

1. **Digital-product isolation:** virtual or downloadable products must not be classified as physical inquiry-only items; the helper test in Task 2 pins this behavior.
2. **Tampered product IDs/status:** inquiry processing must reject unknown, draft, private or non-product IDs; the integration smoke and static contract pin the published-product check.
3. **Iranian mobile input:** Persian digits, spaces and `+98` format must normalize to one `09xxxxxxxxx` form; landlines/short/long values must fail.
4. **Quantity abuse:** only integer quantities 1–99 are accepted; zero, negatives, decimals, text and >99 fail.
5. **Duplicate submissions:** same product + normalized mobile + quantity within five minutes must not create a second record; use a transient hash only, never raw IP.

---

### Task 1: Guarded WooCommerce Bootstrap and Shop URL Ownership

**Files:**
- Create: `tests/commerce-bootstrap-contract.sh`
- Create: `ops/wp-commerce-bootstrap.sh`
- Modify: `content/pages/shop.html`

**Interfaces:**
- Consumes: existing `tehnet-wordpress` container, existing `/shop/` page and the production guard pattern used by `ops/wp-seed-foundation.sh`.
- Produces: active WooCommerce plugin, existing Shop page assigned as Woo shop, `product_cat` owner `mikrotik-routers`, category base `shop`, product base `/product/`, IRR currency, and zero assigned cart/checkout/account pages.

- [ ] **Step 1: Write the failing bootstrap contract**

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BOOT="$ROOT/ops/wp-commerce-bootstrap.sh"
SHOP="$ROOT/content/pages/shop.html"
fail(){ echo "FAIL: $*"; exit 1; }

[[ -f "$BOOT" ]] || fail 'commerce bootstrap missing'
grep -q 'EXPECTED_BINDING="127.0.0.1:18082"' "$BOOT" || fail 'port guard missing'
grep -q 'plugin install woocommerce' "$BOOT" || fail 'WooCommerce install missing'
grep -q 'woocommerce_shop_page_id' "$BOOT" || fail 'existing Shop page not assigned'
grep -q 'woocommerce_currency' "$BOOT" || fail 'currency not configured'
grep -q 'mikrotik-routers' "$BOOT" || fail 'MikroTik router category missing'
grep -q 'category_base.*shop' "$BOOT" || fail 'category base not /shop/'
grep -q 'product_base.*product' "$BOOT" || fail 'distinct product base missing'
! grep -Eq 'product_base.*shop' "$BOOT" || fail 'product/category base collision'
for key in woocommerce_cart_page_id woocommerce_checkout_page_id woocommerce_myaccount_page_id; do
  grep -q "$key" "$BOOT" || fail "$key must be explicitly disabled for phase 1"
done
for gateway in bacs cheque cod; do grep -q "woocommerce_${gateway}_settings" "$BOOT" || fail "$gateway disable missing"; done
grep -q '/shop/mikrotik-routers/' "$SHOP" || fail 'Shop does not link category owner'
echo COMMERCE_BOOTSTRAP_CONTRACT=PASSED
```

- [ ] **Step 2: Run the contract and verify RED**

Run: `bash tests/commerce-bootstrap-contract.sh`

Expected: `FAIL: commerce bootstrap missing`

- [ ] **Step 3: Implement the guarded idempotent bootstrap**

`ops/wp-commerce-bootstrap.sh` must follow the established TehNet pattern:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_CONTAINER='tehnet-wordpress'
EXPECTED_BINDING='127.0.0.1:18082'
WPCLI_IMAGE='wordpress:cli'
fail(){ echo "ERROR: $*" >&2; exit 1; }

[[ "$(docker inspect -f '{{.State.Running}}' "$TARGET_CONTAINER" 2>/dev/null || true)" == true ]] || fail 'TehNet WordPress is not running'
[[ "$(docker port "$TARGET_CONTAINER" 80/tcp | head -1)" == "$EXPECTED_BINDING" ]] || fail 'unexpected TehNet port binding'
```

Then reuse the secure ephemeral WP-CLI env/network approach from `ops/wp-seed-foundation.sh`, fingerprint non-TehNet runtime, and execute these idempotent operations:

```bash
wp_cli core is-installed >/dev/null
wp_cli plugin is-installed woocommerce >/dev/null 2>&1 || wp_cli plugin install woocommerce >/dev/null
wp_cli plugin activate woocommerce >/dev/null
SHOP_ID="$(wp_cli post list --post_type=page --name=shop --format=ids | awk '{print $1}')"
[[ -n "$SHOP_ID" ]] || fail 'existing /shop/ page missing'
wp_cli option update woocommerce_shop_page_id "$SHOP_ID" >/dev/null
wp_cli option update woocommerce_currency IRR >/dev/null
wp_cli option update woocommerce_cart_page_id 0 >/dev/null
wp_cli option update woocommerce_checkout_page_id 0 >/dev/null
wp_cli option update woocommerce_myaccount_page_id 0 >/dev/null
wp_cli option update woocommerce_bacs_settings '{"enabled":"no"}' --format=json >/dev/null
wp_cli option update woocommerce_cheque_settings '{"enabled":"no"}' --format=json >/dev/null
wp_cli option update woocommerce_cod_settings '{"enabled":"no"}' --format=json >/dev/null
wp_cli option update woocommerce_permalinks '{"category_base":"shop","tag_base":"product-tag","attribute_base":"","product_base":"/product/"}' --format=json >/dev/null
```

If WooCommerce created cart/checkout/account pages before their option IDs are reset, capture their IDs first and move only those Woo-created pages to `draft`; do not delete them.

Create the category only if absent:

```bash
CATEGORY_ID="$(wp_cli term get product_cat mikrotik-routers --by=slug --field=term_id 2>/dev/null || true)"
if [[ -z "$CATEGORY_ID" ]]; then
  CATEGORY_ID="$(wp_cli term create product_cat 'روترهای MikroTik' --slug=mikrotik-routers \
    --description='کاتالوگ روترهای MikroTik تهران نتورک؛ قیمت و موجودی تجهیزات فیزیکی فقط پس از استعلام روز تأیید می‌شود.' --porcelain)"
fi
wp_cli rewrite flush >/dev/null
```

Finish by comparing the non-TehNet fingerprint and re-checking port `18082`.

- [ ] **Step 4: Replace Shop copy with truthful phase-1 commerce copy**

`content/pages/shop.html` must state that physical equipment uses daily inquiry, does not display a pretend live price, and link to `/shop/mikrotik-routers/`. Do not claim stock or shipping time. Keep the page Gutenberg-editable and do not add an editorial `<h1>`.

- [ ] **Step 5: Run Task 1 verification**

Run:

```bash
bash tests/commerce-bootstrap-contract.sh
bash -n ops/wp-commerce-bootstrap.sh
bash tests/gutenberg-foundation-contract.sh
git diff --check
```

Expected: all pass.

- [ ] **Step 6: Commit**

```bash
git add tests/commerce-bootstrap-contract.sh ops/wp-commerce-bootstrap.sh content/pages/shop.html
git commit -m 'feat: add guarded WooCommerce catalog bootstrap'
```

---

### Task 2: Physical Inquiry Policy, Validation and Private Persistence

**Files:**
- Create: `site/plugins/tehnet-core/includes/class-commerce.php`
- Create: `site/plugins/tehnet-core/includes/class-inquiries.php`
- Modify: `site/plugins/tehnet-core/tehnet-core.php`
- Create: `tests/product-inquiry-logic.php`
- Create: `tests/commerce-inquiry-contract.sh`

**Interfaces:**
- Consumes: WooCommerce `WC_Product` behavior when available.
- Produces: `TehNet_Core_Commerce::is_physical_inquiry_product($product): bool`, public inquiry form hooks, `TehNet_Core_Inquiries::normalize_mobile(string): string`, `TehNet_Core_Inquiries::normalize_quantity(mixed): int`, `TehNet_Core_Inquiries::process_request(array, int): int|WP_Error`, private `tn_inquiry` records.

- [ ] **Step 1: Write executable RED logic tests**

`tests/product-inquiry-logic.php`:

```php
<?php
define('ABSPATH', __DIR__ . '/');
require __DIR__ . '/../site/plugins/tehnet-core/includes/class-commerce.php';
require __DIR__ . '/../site/plugins/tehnet-core/includes/class-inquiries.php';

final class Fake_Product {
    public function __construct(private bool $virtual, private bool $downloadable) {}
    public function is_virtual(): bool { return $this->virtual; }
    public function is_downloadable(): bool { return $this->downloadable; }
}

$assert = static function (bool $ok, string $message): void {
    if (! $ok) { fwrite(STDERR, "FAIL: $message\n"); exit(1); }
};
$assert(TehNet_Core_Commerce::is_physical_inquiry_product(new Fake_Product(false, false)), 'physical product must be inquiry-only');
$assert(! TehNet_Core_Commerce::is_physical_inquiry_product(new Fake_Product(true, false)), 'virtual product must stay outside physical inquiry');
$assert(! TehNet_Core_Commerce::is_physical_inquiry_product(new Fake_Product(false, true)), 'downloadable product must stay outside physical inquiry');
$assert(TehNet_Core_Inquiries::normalize_mobile('۰۹۱۲ ۳۴۵ ۶۷۸۹') === '09123456789', 'Persian mobile normalization');
$assert(TehNet_Core_Inquiries::normalize_mobile('+98 912 345 6789') === '09123456789', '+98 mobile normalization');
$assert(TehNet_Core_Inquiries::normalize_mobile('02191018746') === '', 'landline must not pass mobile validation');
$assert(TehNet_Core_Inquiries::normalize_quantity('1') === 1, 'quantity 1');
$assert(TehNet_Core_Inquiries::normalize_quantity('99') === 99, 'quantity 99');
foreach (['0', '-1', '1.5', '100', 'abc'] as $bad) {
    $assert(TehNet_Core_Inquiries::normalize_quantity($bad) === 0, "invalid quantity $bad");
}
echo "PRODUCT_INQUIRY_LOGIC=PASSED\n";
```

- [ ] **Step 2: Write the RED structural/security contract**

`tests/commerce-inquiry-contract.sh` must require:

```bash
grep -q "woocommerce_is_purchasable" "$COMMERCE"
grep -q "woocommerce_get_price_html" "$COMMERCE"
grep -q "woocommerce_loop_add_to_cart_link" "$COMMERCE"
grep -q "woocommerce_single_product_summary" "$COMMERCE"
grep -q "admin_post_tehnet_product_inquiry" "$INQUIRIES"
grep -q "admin_post_nopriv_tehnet_product_inquiry" "$INQUIRIES"
grep -q "check_admin_referer" "$INQUIRIES"
grep -q "tn_website" "$COMMERCE"
grep -q "get_transient" "$INQUIRIES"
grep -q "set_transient" "$INQUIRIES"
grep -q "tn_inquiry" "$INQUIRIES"
grep -q "'public' => false" "$INQUIRIES"
! grep -Eq "REMOTE_ADDR|CF_CONNECTING_IP|HTTP_CF_CONNECTING_IP" "$INQUIRIES" || fail 'raw/client IP must not be used for inquiry dedupe'
```

It must also require both classes to be loaded/registered from `tehnet-core.php`, and reject any newly added payment-gateway or checkout hook.

- [ ] **Step 3: Run both tests and verify RED**

Run:

```bash
php tests/product-inquiry-logic.php
bash tests/commerce-inquiry-contract.sh
```

Expected: fail because the classes do not yet exist.

- [ ] **Step 4: Implement `TehNet_Core_Commerce`**

The class registers Woo hooks only; it must not fatal when WooCommerce is absent.

```php
final class TehNet_Core_Commerce {
    public function register(): void {
        add_filter('woocommerce_is_purchasable', [$this, 'filter_purchasable'], 20, 2);
        add_filter('woocommerce_get_price_html', [$this, 'filter_price_html'], 20, 2);
        add_filter('woocommerce_loop_add_to_cart_link', [$this, 'filter_loop_cta'], 20, 3);
        add_action('woocommerce_single_product_summary', [$this, 'render_inquiry_form'], 31);
        add_action('woocommerce_before_single_product', [$this, 'render_result_notice'], 5);
    }

    public static function is_physical_inquiry_product($product): bool {
        return is_object($product)
            && method_exists($product, 'is_virtual')
            && method_exists($product, 'is_downloadable')
            && ! $product->is_virtual()
            && ! $product->is_downloadable();
    }
}
```

For inquiry-only products:
- `woocommerce_is_purchasable` returns `false`.
- Price HTML becomes `استعلام قیمت روز` and does not expose numeric/stale price.
- Loop CTA links to the product detail page with label `استعلام قیمت`.
- Single-product form includes product ID, name, mobile, optional email, quantity 1–99, optional notes, nonce, and hidden honeypot `tn_website`.
- The form posts to `admin-post.php` action `tehnet_product_inquiry`.
- Success/error notices come only from fixed result codes, never raw query text.

- [ ] **Step 5: Implement `TehNet_Core_Inquiries`**

Register private admin records:

```php
register_post_type('tn_inquiry', [
    'labels' => ['name' => __('استعلام‌ها', 'tehnet-core'), 'singular_name' => __('استعلام', 'tehnet-core')],
    'public' => false,
    'publicly_queryable' => false,
    'show_ui' => true,
    'show_in_rest' => false,
    'show_in_menu' => class_exists('WooCommerce') ? 'woocommerce' : true,
    'supports' => ['title'],
    'map_meta_cap' => true,
    'capabilities' => [
        'edit_post' => 'manage_woocommerce', 'read_post' => 'manage_woocommerce', 'delete_post' => 'manage_woocommerce',
        'edit_posts' => 'manage_woocommerce', 'edit_others_posts' => 'manage_woocommerce',
        'publish_posts' => 'manage_woocommerce', 'read_private_posts' => 'manage_woocommerce',
        'create_posts' => 'do_not_allow',
    ],
]);
```

Normalization rules:
- translate Persian and Arabic digits to ASCII;
- remove whitespace/dashes/parentheses;
- `+989xxxxxxxxx`, `00989xxxxxxxxx`, `989xxxxxxxxx`, and `09xxxxxxxxx` normalize to `09xxxxxxxxx`;
- any other shape returns empty string;
- quantity is an integer 1–99 or returns `0`.

HTTP handler sequence:
1. `check_admin_referer('tehnet_product_inquiry', 'tn_inquiry_nonce')`.
2. Honeypot must be empty.
3. Product ID must resolve with `wc_get_product()` and underlying post status must be `publish`.
4. Product must satisfy `TehNet_Core_Commerce::is_physical_inquiry_product()`.
5. Name non-empty; normalized mobile valid; quantity valid; email optional but valid if provided.
6. Duplicate key is `hash('sha256', product_id . '|' . mobile . '|' . quantity)`; if its transient exists, redirect with fixed `duplicate` result. Never include an IP address.
7. Create one private `tn_inquiry`, store `_tn_product_id`, `_tn_product_name`, `_tn_quantity`, `_tn_customer_name`, `_tn_mobile`, `_tn_email`, `_tn_notes`, `_tn_user_id`, `_tn_status=new`.
8. Set duplicate transient for `5 * MINUTE_IN_SECONDS` only after successful creation.
9. Redirect back to the canonical product permalink with fixed success/error code and `#tehnet-inquiry`.

Expose `process_request(array $request, int $user_id = 0): int|WP_Error` for the production smoke test. The HTTP wrapper owns nonce/honeypot/redirect; `process_request()` owns product + field + duplicate + persistence validation.

Add read-only admin columns for product, customer, mobile, quantity, status and date. Do not implement quote/invoice actions in this phase.

- [ ] **Step 6: Wire TehNet Core without a hard Woo load dependency**

In `tehnet-core.php`:

```php
require_once TEHNET_CORE_DIR . 'includes/class-commerce.php';
require_once TEHNET_CORE_DIR . 'includes/class-inquiries.php';

function tehnet_core_boot(): void {
    (new TehNet_Core_Settings())->register();
    (new TehNet_Core_Content_Types())->register();
    (new TehNet_Core_Schema())->register();
    (new TehNet_Core_Inquiries())->register();
    if (class_exists('WooCommerce')) {
        (new TehNet_Core_Commerce())->register();
    }
}
```

Bump plugin header and `TEHNET_CORE_VERSION` from `0.1.0` to `0.2.0`.

- [ ] **Step 7: Run Task 2 verification**

Run:

```bash
php tests/product-inquiry-logic.php
bash tests/commerce-inquiry-contract.sh
find site/plugins/tehnet-core -name '*.php' -print0 | xargs -0 -n1 php -l
for t in tests/*.sh; do bash "$t"; done
git diff --check
```

Expected: all pass.

- [ ] **Step 8: Commit**

```bash
git add site/plugins/tehnet-core tests/product-inquiry-logic.php tests/commerce-inquiry-contract.sh
git commit -m 'feat: add physical product inquiry workflow'
```

---

### Task 3: Inquiry UI and Shop Content Contract

**Files:**
- Modify: `site/themes/tehnet/style.css`
- Modify: `content/pages/shop.html`
- Create: `tests/shop-commerce-content-contract.sh`

**Interfaces:**
- Consumes: form classes/IDs emitted by Task 2 and category owner created by Task 1.
- Produces: usable RTL inquiry form and truthful Shop/category navigation with no fabricated product claims.

- [ ] **Step 1: Write RED content/UI contract**

Require:

```bash
grep -q '/shop/mikrotik-routers/' "$SHOP"
grep -q 'استعلام قیمت' "$SHOP"
! grep -Eq 'موجود است|ارسال فوری|قیمت ثابت|تضمین موجودی' "$SHOP" || fail 'unverified commerce claim in Shop copy'
grep -q '.tn-inquiry-form' "$STYLE"
grep -q '.tn-inquiry-price' "$STYLE"
grep -q '.tn-inquiry-honeypot' "$STYLE"
```

- [ ] **Step 2: Run and verify RED**

Run: `bash tests/shop-commerce-content-contract.sh`

Expected: fail on missing inquiry CSS.

- [ ] **Step 3: Add minimal RTL-safe presentation**

Style only TehNet-owned form elements; do not globally restyle WooCommerce internals. Include:

```css
.tn-inquiry-form { display: grid; gap: 1rem; margin-top: 1.5rem; }
.tn-inquiry-form label { display: grid; gap: .4rem; font-weight: 700; }
.tn-inquiry-form input,
.tn-inquiry-form textarea { width: 100%; }
.tn-inquiry-price { font-weight: 800; }
.tn-inquiry-honeypot { position: absolute !important; left: -9999px !important; }
```

Preserve keyboard accessibility; do not use `display:none` on the honeypot field.

- [ ] **Step 4: Run Task 3 verification and commit**

Run:

```bash
bash tests/shop-commerce-content-contract.sh
bash tests/theme-contract.sh
git diff --check
```

Commit:

```bash
git add site/themes/tehnet/style.css content/pages/shop.html tests/shop-commerce-content-contract.sh
git commit -m 'style: add physical inquiry shop experience'
```

---

### Task 4: Safe Production Install, Smoke Test, Evidence and Integration

**Files:**
- Create: `ops/commerce-live-smoke.php`
- Create after verification: `ops/SHOP_INQUIRY_EVIDENCE_2026-09-21.md`
- Modify after verification: `PROGRESS.md`
- Modify after verification: `HANDOFF.md`
- Modify after verification: `TASKS.md`
- Modify this plan only to check completed boxes after evidence exists.

**Interfaces:**
- Consumes: Tasks 1–3 and the existing guarded TehNet deployment scripts.
- Produces: WooCommerce active in production, category owner live, inquiry backend proven with a temporary hidden fixture, no real/fake catalog items left behind, and a recoverable documented production state.

- [ ] **Step 1: Write the production smoke script before deployment**

`ops/commerce-live-smoke.php` runs under WP-CLI and must use `try/finally` cleanup. It creates a random temporary simple physical WooCommerce product with `catalog_visibility=hidden`, no price and a unique `TEHNET-SMOKE-*` SKU, sets it published only for the duration of the smoke, then:

```php
$product = new WC_Product_Simple();
$product->set_name('TEHNET INTERNAL COMMERCE SMOKE');
$product->set_status('publish');
$product->set_catalog_visibility('hidden');
$product->set_virtual(false);
$product->set_downloadable(false);
$product->set_sku('TEHNET-SMOKE-' . wp_generate_password(10, false, false));
$product_id = $product->save();

$service = new TehNet_Core_Inquiries();
$inquiry_id = $service->process_request([
    'product_id' => $product_id,
    'name' => 'TehNet Smoke',
    'mobile' => '09120000000',
    'quantity' => '2',
    'email' => '',
    'notes' => 'internal production smoke',
], 0);
```

Assertions:
- result is a valid inquiry post ID;
- post type is `tn_inquiry` and status is private;
- stored product ID/mobile/quantity match expected canonical values;
- the second identical request returns duplicate `WP_Error` and creates no second inquiry;
- a virtual fake product returns `false` from physical-inquiry policy;
- `finally` deletes the temporary inquiry, temporary product and duplicate transient.

The script prints `COMMERCE_LIVE_SMOKE=PASSED` only after cleanup succeeds.

- [ ] **Step 2: Run final branch gate before production mutation**

Run:

```bash
for t in tests/*.sh; do bash "$t"; done
php tests/product-inquiry-logic.php
bash -n ops/wp-commerce-bootstrap.sh
find site/themes/tehnet site/plugins/tehnet-core -name '*.php' -print0 | xargs -0 -n1 php -l
git diff --check
```

Expected: all pass.

- [ ] **Step 3: Capture fresh recovery point and environment compatibility facts**

Create `/root/tehnet-backups/<UTC timestamp>/` containing:
- compressed MariaDB dump;
- compressed `wp-content`;
- `/opt/tehnet/compose.yaml`;
- `/opt/tehnet/.env` mode 0600;
- `/etc/nginx/sites-available/tehnet.ir.conf`;
- `unrelated-before.txt` fingerprint.

Validate gzip/tar before changing production. Record, but do not commit, secrets.

Check and record:

```bash
wp_cli core version
# PHP version from WordPress runtime
# MariaDB version from tehnet-db
```

Abort rather than force-install if the current WooCommerce package declares incompatible requirements.

- [ ] **Step 4: Deploy TehNet code, then bootstrap WooCommerce**

Run in this order:

```bash
bash ops/deploy-theme-plugin.sh
bash ops/wp-commerce-bootstrap.sh
bash ops/wp-seed-foundation.sh
```

No container or Nginx restart is allowed.

- [ ] **Step 5: Run live route/config gates**

Verify public and direct origin:

```text
https://tehnet.ir/shop/                     -> 200, exactly one H1, canonical, noindex,nofollow
https://tehnet.ir/shop/mikrotik-routers/    -> 200, exactly one H1, canonical, noindex,nofollow
```

Also verify:
- WooCommerce is active and record its installed version.
- `woocommerce_shop_page_id` is the existing Shop page.
- `woocommerce_cart_page_id=0`, `woocommerce_checkout_page_id=0`, `woocommerce_myaccount_page_id=0`.
- built-in `bacs`, `cheque`, `cod` are not enabled; no other installed gateway is enabled.
- `woocommerce_currency=IRR`.
- `woocommerce_permalinks.category_base=shop` and `product_base=/product/`.
- `blog_public=0`.
- port is still `127.0.0.1:18082`.
- `nginx -t` passes.
- category term exists and no real/fake product was seeded by the bootstrap.

- [ ] **Step 6: Run temporary production inquiry smoke and prove cleanup**

Run `ops/commerce-live-smoke.php` with the same secure WP-CLI wrapper used elsewhere.

Expected: `COMMERCE_LIVE_SMOKE=PASSED`.

Afterwards verify there is no product with SKU prefix `TEHNET-SMOKE-` and no inquiry with customer name `TehNet Smoke`.

- [ ] **Step 7: Verify runtime isolation**

Capture `unrelated-after.txt` with the exact same container/image/port command and compare byte-for-byte with `unrelated-before.txt`. Re-check TehNet port. Expected: unchanged.

- [ ] **Step 8: Record evidence and coordination files**

`ops/SHOP_INQUIRY_EVIDENCE_2026-09-21.md` must record:
- backup path;
- installed WooCommerce version and compatibility facts;
- exact Shop/category live-gate results;
- inquiry smoke result + cleanup proof;
- no enabled payment gateways/cart/checkout/account surfaces;
- `BLOG_PUBLIC=0` and rendered noindex;
- unchanged port/Nginx/unrelated runtime;
- statement that no actual products/prices/stock were fabricated.

Update `PROGRESS.md`, `HANDOFF.md`, and `TASKS.md` from verified facts only. Mark WooCommerce catalog structure + physical inquiry DONE. Keep manual quote/invoice, digital entitlement, licensing and payments as separate future phases.

- [ ] **Step 9: Final branch verification**

Run the entire test/lint suite again, repeat the two live route gates, run a secret-value diff scan against the branch base, and confirm the branch is clean after the evidence commit.

- [ ] **Step 10: Integration**

After explicit integration authorization, merge the feature branch to `main`, rerun the repository suite and live Shop/category gates from `main`, push `main`, confirm local/remote SHAs match, remove the worktree/feature branch, and mark this final checkbox complete.
