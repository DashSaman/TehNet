#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INV="$ROOT/seo/YOUTUBE_INVENTORY_FA.md"
MAP="$ROOT/seo/YOUTUBE_CONTENT_MAP_FA.md"

[[ -f "$INV" ]] || { echo 'FAIL: YouTube inventory missing'; exit 1; }
grep -q '2026-09-15' "$INV" || { echo 'FAIL: inventory date missing'; exit 1; }
grep -q 'UCXPPSGbWavP2fMXEOh9iZ1Q' "$INV" || { echo 'FAIL: channel ID missing'; exit 1; }
grep -q 'Inventory count: 33' "$INV" || { echo 'FAIL: current inventory count not recorded'; exit 1; }
TOTAL="$(grep -Eo 'youtube\.com/watch\?v=[A-Za-z0-9_-]{11}' "$INV" | wc -l | tr -d ' ')"
UNIQUE="$(grep -Eo 'youtube\.com/watch\?v=[A-Za-z0-9_-]{11}' "$INV" | sort -u | wc -l | tr -d ' ')"
[[ "$TOTAL" -ge 33 ]] || { echo "FAIL: expected at least 33 videos, got $TOTAL"; exit 1; }
[[ "$TOTAL" == "$UNIQUE" ]] || { echo 'FAIL: duplicate video IDs in inventory'; exit 1; }

echo 'YOUTUBE_INVENTORY_CONTRACT=PASSED'
