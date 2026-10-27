#!/usr/bin/env bash
set -uo pipefail
cd /root/tehnet-backups || exit 0
ls -dt *-store-review 2>/dev/null | tail -n +5 | xargs -r rm -rf
ls -dt *-offline-auto 2>/dev/null | tail -n +3 | xargs -r rm -rf
ls -dt *software-engine-* 2>/dev/null | tail -n +3 | xargs -r rm -rf
find /root/tehnet-backups -maxdepth 1 -name '*agent-maintenance*' -printf '%T@ %f\n' 2>/dev/null | sort -rn | tail -n +4 | awk '{print $2}' | xargs -r rm -rf
