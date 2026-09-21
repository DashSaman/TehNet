#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SETTINGS="$ROOT/site/plugins/tehnet-core/includes/class-settings.php"
SCHEMA="$ROOT/site/plugins/tehnet-core/includes/class-schema.php"
MAIN="$ROOT/site/plugins/tehnet-core/tehnet-core.php"
fail(){ echo "FAIL: $*"; exit 1; }

[[ -f "$SCHEMA" ]] || fail 'class-schema.php missing'
grep -q 'public static function defaults' "$SETTINGS" || fail 'central defaults API missing'
grep -q 'public static function value' "$SETTINGS" || fail 'central option value API missing'
for key in tehnet_business_name tehnet_address_locality tehnet_address_region tehnet_address_country tehnet_onsite_area tehnet_remote_area; do
  grep -q "$key" "$SETTINGS" || fail "missing central setting $key"
done
grep -q 'youtube.com/@tehran.network021' "$SETTINGS" || fail 'known YouTube identity default missing'
grep -q "class-schema.php" "$MAIN" || fail 'schema class not loaded by core'
grep -q 'new TehNet_Core_Schema' "$MAIN" || fail 'schema class not registered by core'
grep -q "add_action('wp_head'" "$SCHEMA" || fail 'schema renderer not attached to wp_head'
! grep -q 'serviceArea' "$SCHEMA" || fail 'deprecated serviceArea must not be used'
! grep -Eq 'aggregateRating|openingHoursSpecification|GeoCoordinates' "$SCHEMA" || fail 'unverified rating/hours/geo must not be emitted'
echo LOCALBUSINESS_SETTINGS_CONTRACT=PASSED

# Renderer contract: one stable LocalBusiness entity, truthful NAP and current Schema.org fields.
grep -q "'@type' => 'LocalBusiness'" "$SCHEMA" || fail 'LocalBusiness type missing'
grep -q "'@type' => 'PostalAddress'" "$SCHEMA" || fail 'PostalAddress missing'
grep -q "'@id'" "$SCHEMA" || fail 'stable LocalBusiness @id missing'
grep -q "'areaServed'" "$SCHEMA" || fail 'areaServed missing'
grep -q "'sameAs'" "$SCHEMA" || fail 'sameAs identity links missing'
grep -q 'normalize_phone' "$SCHEMA" || fail 'phone normalization missing'
grep -q "'+98'" "$SCHEMA" || fail 'Iran phone normalization missing'
grep -q 'street_address' "$SCHEMA" || fail 'street derivation helper missing'
grep -q 'wp_json_encode' "$SCHEMA" || fail 'JSON-LD must use wp_json_encode'
grep -q 'JSON_UNESCAPED_UNICODE' "$SCHEMA" || fail 'Persian JSON must stay readable'
grep -q 'JSON_UNESCAPED_SLASHES' "$SCHEMA" || fail 'schema URLs should not be escaped'
grep -q 'is_front_page' "$SCHEMA" || fail 'homepage targeting missing'
grep -q "is_page(\['about', 'contact', 'services'\])" "$SCHEMA" || fail 'identity page targeting missing'
grep -q 'get_page_by_path' "$SCHEMA" || fail 'Services child targeting missing'
grep -q 'required' "$SCHEMA" || fail 'required-field completeness guard missing'
echo LOCALBUSINESS_RENDERER_CONTRACT=PASSED
