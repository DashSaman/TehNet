#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CPT="$ROOT/site/plugins/tehnet-core/includes/class-content-types.php"
PAGE="$ROOT/site/themes/tehnet/page.php"
FRONT="$ROOT/site/themes/tehnet/front-page.php"

[[ $(grep -c "'has_archive' => false" "$CPT") -eq 2 ]] || { echo 'FAIL: service/lab archives must be disabled'; exit 1; }
! grep -q "'rewrite' => \['slug' => 'services'" "$CPT" || { echo 'FAIL: tn_service rewrite collides with /services/* page owners'; exit 1; }
grep -q "'rewrite' => \['slug' => 'lab'" "$CPT" || { echo 'FAIL: lab single rewrite missing'; exit 1; }

[[ -f "$PAGE" ]] || { echo 'FAIL: page.php missing'; exit 1; }
[[ -f "$FRONT" ]] || { echo 'FAIL: front-page.php missing'; exit 1; }
grep -q '<h1' "$PAGE" || { echo 'FAIL: normal page template needs title H1'; exit 1; }
grep -q 'the_title' "$PAGE" || { echo 'FAIL: page template must render title'; exit 1; }
grep -q 'the_content' "$PAGE" || { echo 'FAIL: page template must render content'; exit 1; }
! grep -q '<h1' "$FRONT" || { echo 'FAIL: front-page template must not add duplicate H1'; exit 1; }
grep -q 'the_content' "$FRONT" || { echo 'FAIL: front-page template must render content'; exit 1; }

for f in "$ROOT"/content/pages/{about,contact,lab,learn,services,shop}.html; do
  ! grep -q '<h1' "$f" || { echo "FAIL: duplicate editorial H1 in ${f#$ROOT/}"; exit 1; }
done
[[ $(grep -o '<h1' "$ROOT/content/pages/home.html" | wc -l) -eq 1 ]] || { echo 'FAIL: homepage must own exactly one editorial H1'; exit 1; }

echo 'SEO_TECHNICAL_CONTRACT=PASSED'
