#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PAGES=(
  service-network-tehran
  service-network-support-tehran
  service-network-setup-tehran
  service-mikrotik-tehran
  service-remote-support
)

for name in "${PAGES[@]}"; do
  f="$ROOT/content/pages/$name.html"
  [[ -f "$f" ]] || { echo "FAIL: missing content/pages/$name.html"; exit 1; }
  ! grep -q '<h1' "$f" || { echo "FAIL: $name must not add editorial H1"; exit 1; }
  [[ "$(grep -o '<h2' "$f" | wc -l | tr -d ' ')" -ge 3 ]] || { echo "FAIL: $name needs at least three H2 sections"; exit 1; }
  grep -qF '[tehnet_phone]' "$f" || { echo "FAIL: $name must use central phone shortcode"; exit 1; }
  grep -q 'href="/contact/"' "$f" || { echo "FAIL: $name needs contact CTA"; exit 1; }
done

grep -q 'خدمات شبکه تهران' "$ROOT/content/pages/service-network-tehran.html"
grep -q 'حضوری' "$ROOT/content/pages/service-network-tehran.html"
grep -q 'پشتیبانی شبکه تهران' "$ROOT/content/pages/service-network-support-tehran.html"
grep -q 'عیب‌یابی' "$ROOT/content/pages/service-network-support-tehran.html"
grep -q 'راه‌اندازی شبکه' "$ROOT/content/pages/service-network-setup-tehran.html"
grep -q 'شرکت' "$ROOT/content/pages/service-network-setup-tehran.html"
grep -q 'MikroTik' "$ROOT/content/pages/service-mikrotik-tehran.html"
grep -q 'RouterOS' "$ROOT/content/pages/service-mikrotik-tehran.html"
grep -q 'سراسر ایران' "$ROOT/content/pages/service-remote-support.html"
grep -q 'از راه دور' "$ROOT/content/pages/service-remote-support.html"

echo 'SERVICE_OWNER_CONTENT_CONTRACT=PASSED'

SEED="$ROOT/ops/wp-seed-foundation.sh"
HUB="$ROOT/content/pages/services.html"
for spec in \
  "network-tehran|خدمات شبکه تهران|SERVICE_NETWORK_TEHRAN_ID" \
  "network-support-tehran|پشتیبانی شبکه تهران|SERVICE_NETWORK_SUPPORT_TEHRAN_ID" \
  "network-setup-tehran|راه‌اندازی شبکه شرکت در تهران|SERVICE_NETWORK_SETUP_TEHRAN_ID" \
  "mikrotik-tehran|خدمات MikroTik تهران|SERVICE_MIKROTIK_TEHRAN_ID" \
  "remote-support|پشتیبانی شبکه از راه دور|SERVICE_REMOTE_SUPPORT_ID"; do
  IFS='|' read -r slug title var <<< "$spec"
  grep -q "ensure_page $slug '$title'" "$SEED" || { echo "FAIL: seed missing $slug"; exit 1; }
  grep -q "$var=" "$SEED" || { echo "FAIL: seed ID missing for $slug"; exit 1; }
done
[[ "$(grep -c 'post_parent="\$SERVICES_ID"' "$SEED")" -ge 5 ]] || { echo 'FAIL: five service pages must be children of Services'; exit 1; }
for url in /services/network-tehran/ /services/network-support-tehran/ /services/network-setup-tehran/ /services/mikrotik-tehran/ /services/remote-support/; do
  grep -qF "href=\"$url\"" "$HUB" || { echo "FAIL: services hub missing $url"; exit 1; }
done
grep -qF '[tehnet_phone]' "$HUB" || { echo 'FAIL: services hub needs central phone'; exit 1; }
grep -qF '[tehnet_address]' "$HUB" || { echo 'FAIL: services hub needs central address'; exit 1; }

echo 'SERVICE_OWNER_HIERARCHY_CONTRACT=PASSED'
