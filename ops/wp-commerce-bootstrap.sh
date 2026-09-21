#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_CONTAINER="tehnet-wordpress"
EXPECTED_BINDING="127.0.0.1:18082"
WPCLI_IMAGE="wordpress:cli"

fail(){ echo "ERROR: $*" >&2; exit 1; }
[[ "$(docker inspect -f '{{.State.Running}}' "$TARGET_CONTAINER" 2>/dev/null || true)" == "true" ]] || fail "TehNet WordPress is not running"
[[ "$(docker port "$TARGET_CONTAINER" 80/tcp 2>/dev/null | head -1)" == "$EXPECTED_BINDING" ]] || fail "unexpected TehNet port binding"

NETWORK="$(docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{println $k}}{{end}}' "$TARGET_CONTAINER" | sed '/^$/d' | head -1)"
[[ -n "$NETWORK" ]] || fail "TehNet Docker network not found"
docker image inspect "$WPCLI_IMAGE" >/dev/null 2>&1 || docker pull "$WPCLI_IMAGE" >/dev/null

ENV_FILE="$(mktemp /root/tehnet-secrets/wpcommerce-runtime.XXXXXX)"
BEFORE="$(mktemp)"
AFTER="$(mktemp)"
trap 'rm -f "$ENV_FILE" "$BEFORE" "$AFTER"' EXIT
chmod 600 "$ENV_FILE"

docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' "$TARGET_CONTAINER" \
  | grep -E '^WORDPRESS_DB_(HOST|NAME|USER|PASSWORD)=|^WORDPRESS_TABLE_PREFIX=' > "$ENV_FILE"
wp_cli(){
  docker run --rm --user 33:33 --volumes-from "$TARGET_CONTAINER" \
    --network "$NETWORK" --env-file "$ENV_FILE" \
    "$WPCLI_IMAGE" --path=/var/www/html "$@"
}

fingerprint_unrelated(){
  docker ps -a --no-trunc --format '{{.Names}}|{{.ID}}|{{.Image}}|{{.Ports}}' \
    | grep -v '^tehnet-' | sort
}
fingerprint_unrelated > "$BEFORE"

wp_cli core is-installed >/dev/null || fail "WordPress is not installed"
wp_cli plugin is-installed woocommerce >/dev/null 2>&1 || wp_cli plugin install woocommerce >/dev/null
wp_cli plugin activate woocommerce >/dev/null

SHOP_ID="$(wp_cli post list --post_type=page --name=shop --format=ids | awk '{print $1}')"
[[ -n "$SHOP_ID" ]] || fail "existing /shop/ page missing"

CART_ID="$(wp_cli option get woocommerce_cart_page_id 2>/dev/null || true)"
CHECKOUT_ID="$(wp_cli option get woocommerce_checkout_page_id 2>/dev/null || true)"
ACCOUNT_ID="$(wp_cli option get woocommerce_myaccount_page_id 2>/dev/null || true)"
for page_id in "$CART_ID" "$CHECKOUT_ID" "$ACCOUNT_ID"; do
  if [[ "$page_id" =~ ^[1-9][0-9]*$ ]] && [[ "$page_id" != "$SHOP_ID" ]]; then
    wp_cli post update "$page_id" --post_status=draft >/dev/null || true
  fi
done
wp_cli option update woocommerce_shop_page_id "$SHOP_ID" >/dev/null
wp_cli option update woocommerce_currency IRR >/dev/null
wp_cli option update woocommerce_cart_page_id 0 >/dev/null
wp_cli option update woocommerce_checkout_page_id 0 >/dev/null
wp_cli option update woocommerce_myaccount_page_id 0 >/dev/null
wp_cli option update woocommerce_bacs_settings '{"enabled":"no"}' --format=json >/dev/null
wp_cli option update woocommerce_cheque_settings '{"enabled":"no"}' --format=json >/dev/null
wp_cli option update woocommerce_cod_settings '{"enabled":"no"}' --format=json >/dev/null
wp_cli option update woocommerce_permalinks '{"category_base":"shop","tag_base":"product-tag","attribute_base":"","product_base":"/product/"}' --format=json >/dev/null

CATEGORY_ID="$(wp_cli term get product_cat mikrotik-routers --by=slug --field=term_id 2>/dev/null || true)"
if [[ -z "$CATEGORY_ID" ]]; then
  CATEGORY_ID="$(wp_cli term create product_cat 'روترهای MikroTik' --slug=mikrotik-routers \
    --description='کاتالوگ روترهای MikroTik تهران نتورک؛ قیمت و موجودی تجهیزات فیزیکی فقط پس از استعلام روز تأیید می‌شود.' --porcelain)"
fi

wp_cli rewrite flush >/dev/null
fingerprint_unrelated > "$AFTER"
cmp -s "$BEFORE" "$AFTER" || { diff -u "$BEFORE" "$AFTER" >&2 || true; fail "unrelated container topology changed"; }
[[ "$(docker port "$TARGET_CONTAINER" 80/tcp 2>/dev/null | head -1)" == "$EXPECTED_BINDING" ]] || fail "TehNet port changed"

echo 'WP_COMMERCE_BOOTSTRAP=PASSED'
echo "SHOP_PAGE_ID=$SHOP_ID"
echo "MIKROTIK_CATEGORY_ID=$CATEGORY_ID"
echo 'UNRELATED_RUNTIME_TOPOLOGY=UNCHANGED'
