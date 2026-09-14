#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
THEME="$ROOT/site/themes/tehnet"
[[ -f "$THEME/style.css" ]] || { echo 'FAIL: style.css missing'; exit 1; }
[[ -f "$THEME/theme.json" ]] || { echo 'FAIL: theme.json missing'; exit 1; }
[[ -f "$THEME/functions.php" ]] || { echo 'FAIL: functions.php missing'; exit 1; }
grep -q '^Theme Name: TehNet' "$THEME/style.css"
grep -q -- '--tn-blue' "$THEME/style.css"
grep -q -- '--tn-turquoise' "$THEME/style.css"
grep -q "add_theme_support( *'title-tag'" "$THEME/functions.php"
grep -q "add_theme_support( *'woocommerce'" "$THEME/functions.php"
grep -q "register_nav_menus" "$THEME/functions.php"
if grep -RniE 'nopayments|license[_ -]?key|telegram.*webhook|payment_gateway' "$THEME" --include='*.php' >/dev/null; then
  echo 'FAIL: business logic found in theme'; exit 1
fi
echo 'THEME_CONTRACT=PASSED'
