#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BOOT="$ROOT/ops/wp-bootstrap.sh"
[[ -f "$BOOT" ]] || { echo 'FAIL: bootstrap script missing'; exit 1; }

grep -q 'tehnet-wordpress' "$BOOT"
grep -q '127.0.0.1:18082' "$BOOT"
grep -q '/root/tehnet-secrets' "$BOOT"
grep -q 'chmod 600' "$BOOT"
grep -q 'blog_public.*0' "$BOOT"
grep -q 'https://tehnet.ir' "$BOOT"
grep -q 'Asia/Tehran' "$BOOT"
grep -q 'tehnet-core' "$BOOT"
grep -q 'theme activate tehnet' "$BOOT"
grep -q 'site switch-language fa_IR' "$BOOT"
grep -q 'CURRENT_LANG=' "$BOOT"
grep -q 'if ! wp_cli theme is-active tehnet' "$BOOT"
grep -q 'if ! wp_cli plugin is-active tehnet-core' "$BOOT"
if grep -q 'language core activate' "$BOOT"; then
  echo 'FAIL: deprecated language activation command present'; exit 1
fi
if grep -q -- '--hard' "$BOOT"; then
  echo 'FAIL: unnecessary hard rewrite flush present'; exit 1
fi

if grep -nE 'docker compose (down|up|restart)|docker restart|systemctl restart nginx|nginx -s' "$BOOT" >/dev/null; then
  echo 'FAIL: bootstrap may mutate runtime topology'; exit 1
fi

echo 'WP_BOOTSTRAP_CONTRACT=PASSED'
