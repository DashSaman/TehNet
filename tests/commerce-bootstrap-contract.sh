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
for gateway in bacs cheque cod; do
  grep -q "woocommerce_${gateway}_settings" "$BOOT" || fail "$gateway disable missing"
done
grep -q '/shop/mikrotik-routers/' "$SHOP" || fail 'Shop does not link category owner'
echo COMMERCE_BOOTSTRAP_CONTRACT=PASSED
