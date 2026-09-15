#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PAGE="$ROOT/content/pages/learn-mikrotik.html"
SEED="$ROOT/ops/wp-seed-foundation.sh"

[[ -f "$PAGE" ]] || { echo 'FAIL: learn-mikrotik page missing'; exit 1; }
! grep -q '<h1' "$PAGE" || { echo 'FAIL: Gutenberg body must not add H1'; exit 1; }
for token in 'RouterOS' 'MTCNA' 'VPN' 'Lab'; do grep -q "$token" "$PAGE" || { echo "FAIL: page missing section $token"; exit 1; }; done
for url in \
  'https://www.youtube.com/watch?v=iSNDz7xfNtg' \
  'https://www.youtube.com/watch?v=7cXU76ofkSg' \
  'https://www.youtube.com/watch?v=OgypQcQS3FA'; do
grep -qF "$url" "$PAGE" || { echo "FAIL: verified TehNet video missing: $url"; exit 1; }
done
VIDEO_COUNT="$(grep -Eo 'https://www\.youtube\.com/watch\?v=[A-Za-z0-9_-]{11}' "$PAGE" | sort -u | wc -l | tr -d ' ')"
[[ "$VIDEO_COUNT" -ge 3 ]] || { echo 'FAIL: need at least three unique TehNet videos'; exit 1; }

grep -q "ensure_page mikrotik 'آموزش میکروتیک'" "$SEED" || { echo 'FAIL: mikrotik page seed missing'; exit 1; }
grep -q 'MIKROTIK_ID=' "$SEED" || { echo 'FAIL: mikrotik page ID missing'; exit 1; }
grep -q 'post_parent.*LEARN_ID' "$SEED" || { echo 'FAIL: mikrotik page must be child of Learn'; exit 1; }

echo 'LEARN_MIKROTIK_CONTRACT=PASSED'
