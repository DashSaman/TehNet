#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEPLOY="$ROOT/ops/deploy-theme-plugin.sh"
[[ -f "$DEPLOY" ]] || { echo 'FAIL: deploy script missing'; exit 1; }
grep -q 'tehnet-wordpress' "$DEPLOY"
grep -q 'site/themes/tehnet' "$DEPLOY"
grep -q 'site/plugins/tehnet-core' "$DEPLOY"
grep -q 'docker cp' "$DEPLOY"
grep -q '127.0.0.1:18082' "$DEPLOY"
if grep -nE 'docker compose (down|up)|nginx -s|systemctl restart nginx|/opt/tehnet/compose.yaml.*>' "$DEPLOY" >/dev/null; then
  echo 'FAIL: deploy script may mutate runtime topology'; exit 1
fi
echo 'DEPLOY_CONTRACT=PASSED'
