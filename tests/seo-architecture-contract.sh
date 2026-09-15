#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LIMITS="$ROOT/seo/RESEARCH_LIMITATIONS.md"
QUERIES="$ROOT/seo/QUERY_UNIVERSE_FA.md"
SERP="$ROOT/seo/SERP_INTENT_MAP_FA.md"
IA="$ROOT/seo/INFORMATION_ARCHITECTURE_FA.md"
LINKS="$ROOT/seo/INTERNAL_LINKING_FA.md"

for f in "$LIMITS" "$QUERIES" "$SERP"; do
  [[ -f "$f" ]] || { echo "FAIL: missing ${f#$ROOT/}"; exit 1; }
done

grep -q '2026-09-15' "$SERP"
grep -q 'Ahrefs' "$LIMITS"
grep -Eq 'IR.*(پشتیبانی|support|ندارد|does not support)' "$LIMITS"
grep -q 'Volume' "$LIMITS"
grep -q 'KD' "$LIMITS"

for token in 'Intent' 'Page Type' 'Business Value' 'Owner URL' 'Decision'; do grep -q "$token" "$QUERIES" || { echo "FAIL: query universe missing $token"; exit 1; }; done
for decision in 'GO' 'NOT-YET' 'GO-LONG-TERM' 'LOW-PRIORITY'; do grep -q "$decision" "$QUERIES" || { echo "FAIL: missing decision $decision"; exit 1; }; done

if grep -Eiq 'Iran (Volume|KD):[[:space:]]*[0-9]|حجم جستجوی ایران[[:space:]]*:[[:space:]]*[0-9]' "$QUERIES" "$SERP"; then
  echo 'FAIL: fabricated Iran keyword metrics detected'; exit 1
fi

for f in "$IA" "$LINKS"; do [[ -f "$f" ]] || { echo "FAIL: missing ${f#$ROOT/}"; exit 1; }; done
for route in '/learn/' '/lab/' '/services/' '/shop/'; do grep -q "$route" "$IA" || { echo "FAIL: IA missing $route"; exit 1; }; done
grep -q 'Cannibalization' "$IA" || { echo 'FAIL: IA missing Cannibalization rule'; exit 1; }
for edge in 'Learn → Lab' 'Learn → Services' 'Services → Learn' 'Shop →' 'Lab →'; do grep -q "$edge" "$LINKS" || { echo "FAIL: linking map missing $edge"; exit 1; }; done

echo 'SEO_ARCHITECTURE_RESEARCH_CONTRACT=PASSED'
