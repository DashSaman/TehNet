#!/usr/bin/env bash
# One scoped update for the accepted nonempty pilot; no website/container restart.
set -Eeuo pipefail
umask 077
[[ "$(id -u)" == 0 && $# == 0 ]]
OPS=/opt/tehnet-software/operations/catalog-expanded-20261018
BASE=/opt/tehnet-software/releases/engine-active-20261018
export PYTHONPATH="$BASE/host-site:$OPS" PYTHONDONTWRITEBYTECODE=1
cd "$OPS"
[[ -f provider-delivery-qualification.json && -f linux-full-tests-accepted.txt ]]
[[ "$(docker inspect -f '{{.Image}}' tehnet-software)" == sha256:ab4220407e6a35a6e3d4221b44f238f12b25b1081be4b03ce8a92276a60289fa ]]
systemctl is-active --quiet tehnet-software-mirrors.timer
systemctl is-enabled --quiet tehnet-software-mirrors.timer
exec 9>/run/lock/tehnet-software-engine.lock
flock -n 9 || exit 75
BACKUP=/root/tehnet-backups/"$(date -u +%Y%m%d-%H%M%S)-catalog-expansion"
mkdir -m 700 "$BACKUP"
export CATALOG_BACKUP="$BACKUP"
fingerprint(){ docker ps -a --no-trunc --format '{{.Names}}|{{.ID}}|{{.Image}}|{{.Ports}}' | sort; }
fingerprint > "$BACKUP/containers.before"
sha256sum /etc/nginx/sites-enabled/tehnet.ir.conf /etc/nginx/snippets/tehnet-software.conf /srv/tehnet-software/data/catalog.sqlite /srv/tehnet-software/auth/auth.sqlite /srv/tehnet-software/metadata/restricted/external.sqlite > "$BACKUP/unchanged.before"
cp /etc/systemd/system/tehnet-software-mirrors.{service,timer} "$BACKUP/"
python3 - <<'PY'
import json,os
from pathlib import Path
from tools.mirror_operations import load_manifest,refresh_plan
from tools.catalog_transaction import snapshot,fingerprint
from app.external_storage import ExternalRegistry
entries=load_manifest(Path('catalog/public-downloads.json'));pins={e['artifact']['sha256']:e for e in entries}
qualification=json.loads(Path('provider-delivery-qualification.json').read_text())
assert {x['sha256'] for x in qualification['items']}==set(pins)
assert all(x['full_hash_verified'] and x['head']==200 and x['range']==206 for x in qualification['items'])
store=ExternalRegistry(Path('/srv/tehnet-software/metadata/public'),visibility='public')
with store.connection() as db:
 rows=db.execute('SELECT sha256,record_json,source_json,relative_path FROM external').fetchall()
 assert len(rows)==3,'Updater only accepts original three-file pilot; reconcile newer catalog separately'
 for digest,record,source,path in rows:
  assert digest in pins and json.loads(record)==pins[digest]['artifact'] and json.loads(source)==pins[digest]['source'] and path==pins[digest]['relative_path'],'Existing identity differs'
backup=Path(os.environ['CATALOG_BACKUP'])
snapshot(store.database,backup/'previous-public.sqlite')
snapshot(Path('/srv/tehnet-software/ops/network.sqlite'),backup/'previous-network.sqlite')
(backup/'expected-current').write_text(fingerprint(store.database))
(backup/'budget-plan.json').write_text(json.dumps(refresh_plan(entries),indent=2)+'\n')
PY
rollback(){
 trap - ERR INT TERM HUP EXIT
 set +e
 systemctl stop tehnet-software-mirrors.timer || { echo 'ROLLBACK_REQUIRES_OPERATOR: timer stop failed' >&2; return 1; }
 systemctl stop tehnet-software-mirrors.service || { echo 'ROLLBACK_REQUIRES_OPERATOR: service stop failed' >&2; return 1; }
 flock -w 20 9 || { echo 'ROLLBACK_REQUIRES_OPERATOR: operation lock busy' >&2; return 1; }
 python3 - <<'PY'
import os
from pathlib import Path
from tools.catalog_transaction import restore_public
backup=Path(os.environ['CATALOG_BACKUP'])
expected=[(backup/'expected-current').read_text().strip()]
if (backup/'candidate-current').exists():expected.append((backup/'candidate-current').read_text().strip())
restore_public(Path('/srv/tehnet-software/metadata/public/external.sqlite'),backup/'previous-public.sqlite',expected)
PY
 [[ $? == 0 ]] || { echo 'ROLLBACK_REQUIRES_OPERATOR: concurrent metadata preserved; timer remains stopped' >&2; return 1; }
 install -m 644 "$BACKUP/tehnet-software-mirrors.service" /etc/systemd/system/tehnet-software-mirrors.service || { echo 'ROLLBACK_REQUIRES_OPERATOR: service unit restore failed' >&2; return 1; }
 install -m 644 "$BACKUP/tehnet-software-mirrors.timer" /etc/systemd/system/tehnet-software-mirrors.timer || { echo 'ROLLBACK_REQUIRES_OPERATOR: timer unit restore failed' >&2; return 1; }
 systemctl daemon-reload || { echo 'ROLLBACK_REQUIRES_OPERATOR: unit reload failed' >&2; return 1; }
 systemctl start tehnet-software-mirrors.timer || { echo 'ROLLBACK_REQUIRES_OPERATOR: timer start failed' >&2; return 1; }
 echo "SCOPED_CATALOG_ROLLBACK_PASS backup=$BACKUP"
}
failure(){ status="$1"; rollback || true; exit "$status"; }
trap 'failure $?' ERR
trap 'failure 130' INT
trap 'failure 143' TERM
trap 'failure 129' HUP
trap 'status=$?; if [[ "$status" != 0 ]]; then failure "$status"; fi' EXIT
systemctl stop tehnet-software-mirrors.timer
systemctl stop tehnet-software-mirrors.service
python3 -m tools.mirror_operations --manifest catalog/public-downloads.json --public-root /srv/tehnet-software/metadata/public --ops-root /srv/tehnet-software/ops --publication-receipt "$BACKUP/candidate-current" > "$BACKUP/first-refresh.json"
install -m 644 deployment/systemd/tehnet-software-mirrors.service /etc/systemd/system/tehnet-software-mirrors.service
install -m 644 deployment/systemd/tehnet-software-mirrors.timer /etc/systemd/system/tehnet-software-mirrors.timer
systemctl daemon-reload
python3 -m app.recovery validate --root /srv/tehnet-software > "$BACKUP/state-validated.json"
fingerprint > "$BACKUP/containers.after"
sha256sum /etc/nginx/sites-enabled/tehnet.ir.conf /etc/nginx/snippets/tehnet-software.conf /srv/tehnet-software/data/catalog.sqlite /srv/tehnet-software/auth/auth.sqlite /srv/tehnet-software/metadata/restricted/external.sqlite > "$BACKUP/unchanged.after"
cmp "$BACKUP/containers.before" "$BACKUP/containers.after"
cmp "$BACKUP/unchanged.before" "$BACKUP/unchanged.after"
systemctl start tehnet-software-mirrors.timer
systemctl is-active --quiet tehnet-software-mirrors.timer
trap - ERR INT TERM HUP EXIT
printf 'CATALOG_EXPANDED files=11 payload_disk_files=0 container_restarts=0 backup=%s\n' "$BACKUP" | tee "$BACKUP/result.txt"
cp "$BACKUP/first-refresh.json" "$OPS/live-first-refresh.json"
printf '%s\n' "$BACKUP" > "$OPS/live-backup-path.txt"
