#!/usr/bin/env bash
set -euo pipefail
SCRIPT="$(cd "$(dirname "$0")/.." && pwd)/install-wordpress.sh"
[[ -f "$SCRIPT" ]] || { echo "FAIL: installer missing" >&2; exit 1; }
set +e
OUT="$(env -i PATH="$PATH" bash "$SCRIPT" 2>&1)"
RC=$?
set -e
[[ $RC -ne 0 ]] || { echo "FAIL: installer accepted missing secrets" >&2; exit 1; }
grep -q 'Missing required environment variable' <<<"$OUT" || { echo "FAIL: missing-env error not explicit" >&2; exit 1; }
bash -n "$SCRIPT"
echo "install-wordpress-test: PASS"
