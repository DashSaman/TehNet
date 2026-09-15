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
