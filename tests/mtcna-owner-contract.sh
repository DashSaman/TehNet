#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PAGE="$ROOT/content/pages/learn-mikrotik-mtcna.html"
HUB="$ROOT/content/pages/learn-mikrotik.html"
SEED="$ROOT/ops/wp-seed-foundation.sh"
fail(){ echo "FAIL: $*"; exit 1; }
[[ -f "$PAGE" ]] || fail 'MTCNA owner source missing'
! grep -qi '<h1' "$PAGE" || fail 'editorial H1 forbidden'
for id in Wbj3C0g__zw a0JMhBdNNgs hqjjvQoO7as Z5EWfUn1Ejw LO4m55Hf-do XRIMAowqdM4 I_8T6nu8JNg OgypQcQS3FA; do
  grep -q "$id" "$PAGE" || fail "mapped video missing: $id"
done
for text in 'پیش‌نیاز' 'ترتیب پیشنهادی' 'GNS3' 'چک‌پوینت' 'RouterOS'; do grep -q "$text" "$PAGE" || fail "section/content missing: $text"; done
for href in '/learn/mikrotik/' '/lab/' '/services/mikrotik-tehran/' '/contact/'; do grep -q "href=\"$href\"" "$PAGE" || fail "internal link missing: $href"; done
grep -q 'href="/learn/mikrotik/mtcna/"' "$HUB" || fail 'MikroTik hub does not link MTCNA owner'
grep -q 'MTCNA_ID=.*ensure_page mtcna' "$SEED" || fail 'MTCNA idempotent seed missing'
grep -q 'post update "$MTCNA_ID" --post_parent="$MIKROTIK_ID"' "$SEED" || fail 'MTCNA parent hierarchy missing'
echo MTCNA_OWNER_CONTRACT=PASSED
