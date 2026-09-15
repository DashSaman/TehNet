#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_CONTAINER="tehnet-wordpress"
EXPECTED_BINDING="127.0.0.1:18082"
WPCLI_IMAGE="wordpress:cli"

fail(){ echo "ERROR: $*" >&2; exit 1; }
[[ "$(docker inspect -f '{{.State.Running}}' "$TARGET_CONTAINER" 2>/dev/null || true)" == "true" ]] || fail "$TARGET_CONTAINER is not running"
[[ "$(docker port "$TARGET_CONTAINER" 80/tcp 2>/dev/null | head -1)" == "$EXPECTED_BINDING" ]] || fail "unexpected TehNet port binding"

NETWORK="$(docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{println $k}}{{end}}' "$TARGET_CONTAINER" | sed '/^$/d' | head -1)"
[[ -n "$NETWORK" ]] || fail "TehNet Docker network not found"

docker image inspect "$WPCLI_IMAGE" >/dev/null 2>&1 || docker pull "$WPCLI_IMAGE" >/dev/null
ENV_FILE="$(mktemp /root/tehnet-secrets/wpseed-runtime.XXXXXX)"
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
wp_cli theme is-active tehnet >/dev/null || fail "TehNet theme is not active"
wp_cli plugin is-active tehnet-core >/dev/null || fail "TehNet Core plugin is not active"

ensure_page(){
  local slug="$1" title="$2" file="$3"
  [[ -f "$file" ]] || fail "missing page source: $file"
  local id
  id="$(wp_cli post list --post_type=page --name="$slug" --format=ids | awk '{print $1}')"
  if [[ -n "$id" ]]; then
    wp_cli post update "$id" --post_title="$title" --post_name="$slug" \
      --post_status=publish --post_content="$(cat "$file")" >/dev/null
  else
    id="$(wp_cli post create --post_type=page --post_title="$title" --post_name="$slug" \
      --post_status=publish --post_content="$(cat "$file")" --porcelain)"
  fi
  printf '%s' "$id"
}
HOME_ID="$(ensure_page home 'خانه' "$ROOT/content/pages/home.html")"
LEARN_ID="$(ensure_page learn 'آموزش' "$ROOT/content/pages/learn.html")"
MIKROTIK_ID="$(ensure_page mikrotik 'آموزش میکروتیک' "$ROOT/content/pages/learn-mikrotik.html")"
wp_cli post update "$MIKROTIK_ID" --post_parent="$LEARN_ID" >/dev/null
LAB_ID="$(ensure_page lab 'Lab' "$ROOT/content/pages/lab.html")"
SERVICES_ID="$(ensure_page services 'خدمات' "$ROOT/content/pages/services.html")"
SERVICE_NETWORK_TEHRAN_ID="$(ensure_page network-tehran 'خدمات شبکه تهران' "$ROOT/content/pages/service-network-tehran.html")"
wp_cli post update "$SERVICE_NETWORK_TEHRAN_ID" --post_parent="$SERVICES_ID" >/dev/null
SERVICE_NETWORK_SUPPORT_TEHRAN_ID="$(ensure_page network-support-tehran 'پشتیبانی شبکه تهران' "$ROOT/content/pages/service-network-support-tehran.html")"
wp_cli post update "$SERVICE_NETWORK_SUPPORT_TEHRAN_ID" --post_parent="$SERVICES_ID" >/dev/null
SERVICE_NETWORK_SETUP_TEHRAN_ID="$(ensure_page network-setup-tehran 'راه‌اندازی شبکه شرکت در تهران' "$ROOT/content/pages/service-network-setup-tehran.html")"
wp_cli post update "$SERVICE_NETWORK_SETUP_TEHRAN_ID" --post_parent="$SERVICES_ID" >/dev/null
SERVICE_MIKROTIK_TEHRAN_ID="$(ensure_page mikrotik-tehran 'خدمات MikroTik تهران' "$ROOT/content/pages/service-mikrotik-tehran.html")"
wp_cli post update "$SERVICE_MIKROTIK_TEHRAN_ID" --post_parent="$SERVICES_ID" >/dev/null
SERVICE_REMOTE_SUPPORT_ID="$(ensure_page remote-support 'پشتیبانی شبکه از راه دور' "$ROOT/content/pages/service-remote-support.html")"
wp_cli post update "$SERVICE_REMOTE_SUPPORT_ID" --post_parent="$SERVICES_ID" >/dev/null
SHOP_ID="$(ensure_page shop 'فروشگاه' "$ROOT/content/pages/shop.html")"
ABOUT_ID="$(ensure_page about 'درباره ما' "$ROOT/content/pages/about.html")"
CONTACT_ID="$(ensure_page contact 'تماس با ما' "$ROOT/content/pages/contact.html")"

wp_cli option update show_on_front page >/dev/null
wp_cli option update page_on_front "$HOME_ID" >/dev/null

MENU_NAME='منوی اصلی'
MENU_ID="$(wp_cli menu list --fields=term_id,name --format=csv \
  | awk -v name="$MENU_NAME" -f "$ROOT/ops/lib/wp-menu-id.awk")"
if [[ -z "$MENU_ID" ]]; then
  MENU_ID="$(wp_cli menu create "$MENU_NAME" --porcelain)"
fi

for page_id in "$HOME_ID" "$LEARN_ID" "$LAB_ID" "$SERVICES_ID" "$SHOP_ID" "$ABOUT_ID" "$CONTACT_ID"; do
  if ! wp_cli menu item list "$MENU_ID" --fields=object_id --format=csv \
      | tail -n +2 | grep -qx "$page_id"; then
    wp_cli menu item add-post "$MENU_ID" "$page_id" >/dev/null
  fi
done
wp_cli menu location assign "$MENU_ID" primary >/dev/null

fingerprint_unrelated > "$AFTER"
cmp -s "$BEFORE" "$AFTER" || { diff -u "$BEFORE" "$AFTER" >&2 || true; fail "unrelated container topology changed"; }
[[ "$(docker port "$TARGET_CONTAINER" 80/tcp 2>/dev/null | head -1)" == "$EXPECTED_BINDING" ]] || fail "TehNet port changed"

echo 'WP_FOUNDATION_SEED=PASSED'
echo "HOME_PAGE_ID=$HOME_ID"
echo "PRIMARY_MENU_ID=$MENU_ID"
echo 'UNRELATED_RUNTIME_TOPOLOGY=UNCHANGED'
