#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN="$ROOT/site/plugins/tehnet-core"
MAIN="$PLUGIN/tehnet-core.php"
SETTINGS="$PLUGIN/includes/class-settings.php"
CONTENT="$PLUGIN/includes/class-content-types.php"
[[ -f "$MAIN" ]] || { echo 'FAIL: plugin main missing'; exit 1; }
[[ -f "$SETTINGS" ]] || { echo 'FAIL: settings class missing'; exit 1; }
[[ -f "$CONTENT" ]] || { echo 'FAIL: content types class missing'; exit 1; }
grep -q 'Plugin Name: TehNet Core' "$MAIN"
for key in tehnet_phone tehnet_address tehnet_youtube_url tehnet_telegram_url tehnet_instagram_url tehnet_primary_cta; do
  grep -q "$key" "$SETTINGS" || { echo "FAIL: missing setting $key"; exit 1; }
done
grep -q "current_user_can('manage_options')" "$SETTINGS"
grep -q 'sanitize_text_field' "$SETTINGS"
grep -q 'esc_url_raw' "$SETTINGS"
grep -q "register_post_type('tn_service'" "$CONTENT"
grep -q "register_post_type('tn_lab'" "$CONTENT"
grep -q "'show_in_rest' => true" "$CONTENT"
echo 'CORE_PLUGIN_CONTRACT=PASSED'
