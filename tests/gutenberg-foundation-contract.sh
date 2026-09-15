#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PATTERNS="$ROOT/site/themes/tehnet/inc/block-patterns.php"
SEED="$ROOT/ops/wp-seed-foundation.sh"
HOME="$ROOT/content/pages/home.html"
SETTINGS="$ROOT/site/plugins/tehnet-core/includes/class-settings.php"

for f in "$PATTERNS" "$SEED" "$HOME"; do
  [[ -f "$f" ]] || { echo "FAIL: missing ${f#$ROOT/}"; exit 1; }
done

grep -q "register_block_pattern_category('tehnet'" "$PATTERNS"
grep -q "tehnet/hero" "$PATTERNS"
grep -q "tehnet/journeys" "$PATTERNS"
grep -q "tehnet/contact-cta" "$PATTERNS"
grep -q "inc/block-patterns.php" "$ROOT/site/themes/tehnet/functions.php"

grep -q '<!-- wp:group' "$HOME"
grep -q '<!-- wp:columns' "$HOME"
grep -q 'تهران نتورک' "$HOME"

for slug in home learn lab services shop about contact; do grep -q "$slug" "$SEED"; done
grep -q 'post list.*--post_type=page.*--name=' "$SEED"
grep -q 'show_on_front' "$SEED"
grep -q 'page_on_front' "$SEED"
grep -q 'menu location assign' "$SEED"
grep -q "add_shortcode('tehnet_phone'" "$SETTINGS"
grep -q "add_shortcode('tehnet_address'" "$SETTINGS"

if grep -nE 'docker compose (down|up|restart)|docker restart|systemctl restart nginx' "$SEED" >/dev/null; then
  echo 'FAIL: seed script may mutate runtime topology'; exit 1
fi

echo 'GUTENBERG_FOUNDATION_CONTRACT=PASSED'
