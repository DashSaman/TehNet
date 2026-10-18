#!/usr/bin/env bash
# One metadata writer, shared with engine deployment, backup and password setup.
set -Eeuo pipefail
umask 077
OPS=/opt/tehnet-software/operations/catalog-expanded-20261018
BASE=/opt/tehnet-software/releases/engine-active-20261018
exec 9>/run/lock/tehnet-software-engine.lock
flock -n 9 || { echo 'Engine operation in progress; refresh deferred.'; exit 75; }
export PYTHONPATH="$BASE/host-site:$OPS"
export PYTHONDONTWRITEBYTECODE=1
cd "$OPS"
exec python3 -m tools.mirror_operations --manifest "$OPS/catalog/public-downloads.json" \
  --public-root /srv/tehnet-software/metadata/public --ops-root /srv/tehnet-software/ops
