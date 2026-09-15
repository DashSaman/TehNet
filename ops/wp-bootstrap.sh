#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

TARGET_CONTAINER="tehnet-wordpress"
EXPECTED_BINDING="127.0.0.1:18082"
SECRETS_DIR="/root/tehnet-secrets"
SECRET_FILE="$SECRETS_DIR/wp-admin-bootstrap.env"
WPCLI_IMAGE="wordpress:cli"
SITE_URL="https://tehnet.ir"
SITE_TITLE="تهران نتورک | TehNet"
ADMIN_USER="tehnetmgr"
ADMIN_EMAIL="admin@tehnet.ir"

fail(){ echo "ERROR: $*" >&2; exit 1; }
command -v docker >/dev/null 2>&1 || fail "docker is required"
command -v openssl >/dev/null 2>&1 || fail "openssl is required"
[[ "$(docker inspect -f '{{.State.Running}}' "$TARGET_CONTAINER" 2>/dev/null || true)" == "true" ]] || fail "$TARGET_CONTAINER is not running"

BINDING="$(docker port "$TARGET_CONTAINER" 80/tcp 2>/dev/null | head -1)"
[[ "$BINDING" == "$EXPECTED_BINDING" ]] || fail "unexpected TehNet binding: $BINDING"

NETWORK="$(docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{println $k}}{{end}}' "$TARGET_CONTAINER" | sed '/^$/d' | head -1)"
[[ -n "$NETWORK" ]] || fail "TehNet Docker network not found"

mkdir -p "$SECRETS_DIR"
chmod 700 "$SECRETS_DIR"
RUNTIME_ENV="$(mktemp "$SECRETS_DIR/wpcli-runtime.XXXXXX")"
CLI_ENV="$(mktemp "$SECRETS_DIR/wpcli-combined.XXXXXX")"
BEFORE="$(mktemp)"
AFTER="$(mktemp)"
trap 'rm -f "$RUNTIME_ENV" "$CLI_ENV" "$BEFORE" "$AFTER"' EXIT
chmod 600 "$RUNTIME_ENV" "$CLI_ENV"

docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' "$TARGET_CONTAINER" \
  | grep -E '^WORDPRESS_DB_(HOST|NAME|USER|PASSWORD)=|^WORDPRESS_TABLE_PREFIX=' > "$RUNTIME_ENV"
[[ "$(grep -c '^WORDPRESS_DB_' "$RUNTIME_ENV")" -ge 4 ]] || fail "WordPress DB environment is incomplete"

fingerprint_unrelated(){
  docker ps -a --no-trunc --format '{{.Names}}|{{.ID}}|{{.Image}}|{{.Ports}}' \
    | grep -v '^tehnet-' | sort
}
fingerprint_unrelated > "$BEFORE"

if ! docker image inspect "$WPCLI_IMAGE" >/dev/null 2>&1; then
  docker pull "$WPCLI_IMAGE" >/dev/null
fi

wp_cli(){
  docker run --rm --user 33:33 --volumes-from "$TARGET_CONTAINER" \
    --network "$NETWORK" --env-file "$RUNTIME_ENV" \
    "$WPCLI_IMAGE" --path=/var/www/html "$@"
}
if ! wp_cli core is-installed >/dev/null 2>&1; then
  if [[ ! -f "$SECRET_FILE" ]]; then
    PASSWORD="$(openssl rand -hex 24)"
    cat > "$SECRET_FILE" <<EOF
WP_ADMIN_USER=$ADMIN_USER
WP_ADMIN_EMAIL=$ADMIN_EMAIL
WP_ADMIN_PASSWORD=$PASSWORD
EOF
    chmod 600 "$SECRET_FILE"
  fi

  cat "$RUNTIME_ENV" "$SECRET_FILE" > "$CLI_ENV"
  chmod 600 "$CLI_ENV"

  docker run --rm --user 33:33 --volumes-from "$TARGET_CONTAINER" \
    --network "$NETWORK" --env-file "$CLI_ENV" --entrypoint sh \
    "$WPCLI_IMAGE" -lc 'wp --path=/var/www/html core install \
      --url="https://tehnet.ir" \
      --title="تهران نتورک | TehNet" \
      --admin_user="$WP_ADMIN_USER" \
      --admin_password="$WP_ADMIN_PASSWORD" \
      --admin_email="$WP_ADMIN_EMAIL" \
      --skip-email'
fi

wp_cli option update home "$SITE_URL" >/dev/null
wp_cli option update siteurl "$SITE_URL" >/dev/null
wp_cli option update blogname "$SITE_TITLE" >/dev/null
wp_cli option update blogdescription 'آموزش، خدمات و تجهیزات شبکه' >/dev/null
wp_cli option update timezone_string 'Asia/Tehran' >/dev/null
wp_cli option update blog_public 0 >/dev/null
if ! wp_cli language core is-installed fa_IR >/dev/null 2>&1; then
  if ! wp_cli language core install fa_IR >/dev/null 2>&1; then
    echo 'WARN: fa_IR language pack could not be installed; continuing with current core language.' >&2
  fi
fi
if wp_cli language core is-installed fa_IR >/dev/null 2>&1; then
  wp_cli language core activate fa_IR >/dev/null
fi

wp_cli rewrite structure '/%postname%/' --hard >/dev/null
wp_cli theme activate tehnet >/dev/null
wp_cli plugin activate tehnet-core >/dev/null
wp_cli rewrite flush --hard >/dev/null

wp_cli core is-installed >/dev/null
wp_cli theme is-active tehnet >/dev/null
wp_cli plugin is-active tehnet-core >/dev/null
[[ "$(wp_cli option get blog_public | tr -d '\r')" == "0" ]] || fail "blog_public is not 0"
[[ "$(wp_cli option get home | tr -d '\r')" == "$SITE_URL" ]] || fail "home URL mismatch"
[[ "$(wp_cli option get siteurl | tr -d '\r')" == "$SITE_URL" ]] || fail "siteurl mismatch"

fingerprint_unrelated > "$AFTER"
if ! cmp -s "$BEFORE" "$AFTER"; then
  echo 'ERROR: unrelated container topology changed during WordPress bootstrap:' >&2
  diff -u "$BEFORE" "$AFTER" >&2 || true
  exit 1
fi

[[ "$(docker port "$TARGET_CONTAINER" 80/tcp 2>/dev/null | head -1)" == "$EXPECTED_BINDING" ]] || fail "TehNet port changed"

echo 'WP_BOOTSTRAP=PASSED'
echo "PORT_BINDING=$EXPECTED_BINDING"
echo "ADMIN_SECRET_FILE=$SECRET_FILE"
echo 'BLOG_PUBLIC=0'
echo 'UNRELATED_RUNTIME_TOPOLOGY=UNCHANGED'
