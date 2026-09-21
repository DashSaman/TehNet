#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
COMMERCE="$ROOT/site/plugins/tehnet-core/includes/class-commerce.php"
INQUIRIES="$ROOT/site/plugins/tehnet-core/includes/class-inquiries.php"
CORE="$ROOT/site/plugins/tehnet-core/tehnet-core.php"
fail(){ echo "FAIL: $*"; exit 1; }

[[ -f "$COMMERCE" ]] || fail 'commerce class missing'
[[ -f "$INQUIRIES" ]] || fail 'inquiries class missing'
for hook in woocommerce_is_purchasable woocommerce_get_price_html woocommerce_loop_add_to_cart_link woocommerce_single_product_summary; do
  grep -q "$hook" "$COMMERCE" || fail "missing commerce hook: $hook"
done
grep -q "add_action('wp_head'" "$COMMERCE" || fail 'commerce archive canonical hook missing'
grep -q 'is_shop' "$COMMERCE" || fail 'shop canonical branch missing'
grep -q 'is_product_category' "$COMMERCE" || fail 'product category canonical branch missing'
grep -q 'rel=\"canonical\"' "$COMMERCE" || fail 'canonical markup missing'
for hook in admin_post_tehnet_product_inquiry admin_post_nopriv_tehnet_product_inquiry; do
  grep -q "$hook" "$INQUIRIES" || fail "missing inquiry handler: $hook"
done
grep -q 'check_admin_referer' "$INQUIRIES" || fail 'nonce validation missing'
grep -q 'tn_website' "$COMMERCE" || fail 'honeypot field missing'
grep -q 'get_transient' "$INQUIRIES" || fail 'duplicate lookup missing'
grep -q 'set_transient' "$INQUIRIES" || fail 'duplicate lock missing'
grep -q "register_post_type('tn_inquiry'" "$INQUIRIES" || fail 'private inquiry post type missing'
grep -q "'public' => false" "$INQUIRIES" || fail 'inquiry post type must be private'
! grep -Eq 'REMOTE_ADDR|CF_CONNECTING_IP|HTTP_CF_CONNECTING_IP' "$INQUIRIES" || fail 'raw/client IP must not be used for inquiry dedupe'
grep -q "class-commerce.php" "$CORE" || fail 'commerce class not loaded'
grep -q "class-inquiries.php" "$CORE" || fail 'inquiries class not loaded'
! grep -Eq 'woocommerce_available_payment_gateways|woocommerce_checkout_' "$COMMERCE" "$INQUIRIES" || fail 'payment/checkout behavior is out of scope'
echo COMMERCE_INQUIRY_CONTRACT=PASSED
