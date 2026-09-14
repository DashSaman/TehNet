#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASELINE="$ROOT/ops/PRODUCTION_BASELINE.md"
RECOVERY="$ROOT/ops/BACKUP_RECOVERY.md"
[[ -f "$BASELINE" ]] || { echo 'FAIL: baseline missing'; exit 1; }
[[ -f "$RECOVERY" ]] || { echo 'FAIL: recovery doc missing'; exit 1; }
grep -q '127.0.0.1:18082' "$BASELINE"
grep -q 'tehnet-wordpress' "$BASELINE"
grep -q 'tehnet-db' "$BASELINE"
grep -q 'tehnet-redis' "$BASELINE"
grep -q '/opt/tehnet/compose.yaml' "$BASELINE"
grep -q '/etc/nginx/sites-enabled/tehnet.ir.conf' "$BASELINE"
grep -q '/root/tehnet-backups/' "$RECOVERY"
echo 'PRODUCTION_ISOLATION_CONTRACT=PASSED'
