#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SHOP="$ROOT/content/pages/shop.html"
STYLE="$ROOT/site/themes/tehnet/style.css"
fail(){ echo "FAIL: $*"; exit 1; }

grep -q '/shop/mikrotik-routers/' "$SHOP" || fail 'MikroTik category owner link missing'
grep -q 'استعلام قیمت' "$SHOP" || fail 'physical inquiry CTA/copy missing'
! grep -Eq 'موجود است|ارسال فوری|قیمت ثابت|تضمین موجودی' "$SHOP" || fail 'unverified commerce claim in Shop copy'
grep -q '.tn-inquiry-form' "$STYLE" || fail 'inquiry form style missing'
grep -q '.tn-inquiry-price' "$STYLE" || fail 'inquiry price style missing'
grep -q '.tn-inquiry-honeypot' "$STYLE" || fail 'honeypot style missing'
! grep -A4 '.tn-inquiry-honeypot' "$STYLE" | grep -q 'display:[[:space:]]*none' || fail 'honeypot must stay keyboard/bot-detectable'
echo SHOP_COMMERCE_CONTENT_CONTRACT=PASSED
