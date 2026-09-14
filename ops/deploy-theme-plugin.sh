#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTAINER="tehnet-wordpress"
EXPECTED_PORT="127.0.0.1:18082"
THEME_SRC="$ROOT/site/themes/tehnet"
PLUGIN_SRC="$ROOT/site/plugins/tehnet-core"

fail(){ echo "ERROR: $*" >&2; exit 1; }
command -v docker >/dev/null 2>&1 || fail "docker is required"
[[ -d "$THEME_SRC" ]] || fail "theme source missing"
[[ -d "$PLUGIN_SRC" ]] || fail "plugin source missing"
[[ "$(docker inspect -f '{{.State.Running}}' "$CONTAINER" 2>/dev/null || true)" == "true" ]] || fail "$CONTAINER is not running"

PUBLISHED="$(docker port "$CONTAINER" 80/tcp 2>/dev/null | head -1)"
[[ "$PUBLISHED" == "$EXPECTED_PORT" ]] || fail "unexpected TehNet port binding: $PUBLISHED"

LATEST_BACKUP="$(find /root/tehnet-backups -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | tail -1)"
[[ -n "$LATEST_BACKUP" ]] || fail "no TehNet backup found"
[[ -s "$LATEST_BACKUP/tehnet.sql.gz" ]] || fail "latest DB backup missing"
[[ -s "$LATEST_BACKUP/wp-content.tar.gz" ]] || fail "latest wp-content backup missing"

BEFORE="$(mktemp)"
AFTER="$(mktemp)"
trap 'rm -f "$BEFORE" "$AFTER"' EXIT

docker ps -a --format '{{.Names}}|{{.Image}}|{{.Ports}}' | sort > "$BEFORE"

docker exec "$CONTAINER" mkdir -p \
  /var/www/html/wp-content/themes/tehnet \
  /var/www/html/wp-content/plugins/tehnet-core

docker cp "$THEME_SRC/." "$CONTAINER:/var/www/html/wp-content/themes/tehnet/"
docker cp "$PLUGIN_SRC/." "$CONTAINER:/var/www/html/wp-content/plugins/tehnet-core/"

docker exec "$CONTAINER" chown -R www-data:www-data \
  /var/www/html/wp-content/themes/tehnet \
  /var/www/html/wp-content/plugins/tehnet-core

docker exec "$CONTAINER" sh -lc \
  "find /var/www/html/wp-content/themes/tehnet /var/www/html/wp-content/plugins/tehnet-core -name '*.php' -print0 | xargs -0 -n1 php -l >/dev/null"

docker ps -a --format '{{.Names}}|{{.Image}}|{{.Ports}}' | sort > "$AFTER"
if ! cmp -s "$BEFORE" "$AFTER"; then
  echo 'Container/image/port inventory changed during TehNet file deployment:' >&2
  diff -u "$BEFORE" "$AFTER" >&2 || true
  exit 1
fi

PUBLISHED_AFTER="$(docker port "$CONTAINER" 80/tcp 2>/dev/null | head -1)"
[[ "$PUBLISHED_AFTER" == "$EXPECTED_PORT" ]] || fail "TehNet port changed after deploy"

HTTP_CODE="$(curl -ksS -o /dev/null -w '%{http_code}' -H 'Host: tehnet.ir' https://127.0.0.1/ || true)"
[[ "$HTTP_CODE" =~ ^(200|301|302)$ ]] || fail "unexpected local HTTPS response: $HTTP_CODE"

echo "TEHNET_FILE_DEPLOY=PASSED"
echo "PORT_BINDING=$PUBLISHED_AFTER"
echo "UNRELATED_RUNTIME_TOPOLOGY=UNCHANGED"
