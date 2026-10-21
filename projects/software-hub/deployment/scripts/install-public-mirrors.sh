#!/usr/bin/env bash
# Scoped metadata/service installation. Never restarts Docker, Nginx or WordPress.
set -Eeuo pipefail
umask 077
[[ "$(id -u)" == 0 ]]
OPS=/opt/tehnet-software/operations/mirrors-20261018
BASE=/opt/tehnet-software/releases/engine-active-20261018
export PYTHONPATH="$BASE/host-site:$OPS" PYTHONDONTWRITEBYTECODE=1
cd "$OPS"
[[ -f mirror-full-qualification.json && -f provider-delivery-qualification.json ]]
[[ ! -e /etc/systemd/system/tehnet-software-mirrors.service && ! -e /etc/systemd/system/tehnet-software-mirrors.timer ]]
[[ "$(docker inspect -f '{{.Image}}' tehnet-software)" == sha256:ab4220407e6a35a6e3d4221b44f238f12b25b1081be4b03ce8a92276a60289fa ]]
exec 9>/run/lock/tehnet-software-engine.lock
flock -n 9 || { echo 'Engine operation active; installation deferred.'; exit 75; }
BACKUP=/root/tehnet-backups/"$(date -u +%Y%m%d-%H%M%S)-public-mirrors"
mkdir -m 700 "$BACKUP"
export MIRROR_INSTALL_BACKUP="$BACKUP"
fingerprint(){ docker ps -a --no-trunc --format '{{.Names}}|{{.ID}}|{{.Image}}|{{.Ports}}' | sort; }
fingerprint > "$BACKUP/containers.before"
sha256sum /etc/nginx/sites-enabled/tehnet.ir.conf /etc/nginx/snippets/tehnet-software.conf /srv/tehnet-software/data/catalog.sqlite /srv/tehnet-software/auth/auth.sqlite /srv/tehnet-software/metadata/restricted/external.sqlite > "$BACKUP/unchanged.before"
python3 - <<'PY'
from pathlib import Path
from contextlib import closing
import os,sqlite3,json
p=Path(os.environ['MIRROR_INSTALL_BACKUP'])
for original,name in [('/srv/tehnet-software/metadata/public/external.sqlite','previous-public.sqlite'),('/srv/tehnet-software/ops/network.sqlite','previous-network.sqlite')]:
 with closing(sqlite3.connect(Path(original).as_uri()+'?mode=ro',uri=True)) as source,closing(sqlite3.connect(p/name)) as target:source.backup(target)
 (p/name).chmod(0o600)
with closing(sqlite3.connect(p/'previous-public.sqlite')) as db:
 assert db.execute('SELECT COUNT(*) FROM external').fetchone()==(0,),'Initial pilot installer requires empty registry; later updates need a separate transaction'
for name in ['mirror-full-qualification.json','provider-delivery-qualification.json']:
 v=json.loads(Path(name).read_text())
 if name.startswith('provider'):assert len(v['items'])==3 and all(x['full_hash_verified'] and x['head']==200 and x['range']==206 for x in v['items'])
 else:assert v['updated']==3 and v['payload_files_written']==0
PY
CHANGED=0;UNITS=0
rollback(){
 trap - ERR INT TERM HUP EXIT
 set +e
 if [[ "$UNITS" == 1 ]]; then
  systemctl disable --now tehnet-software-mirrors.timer >/dev/null 2>&1
  systemctl stop tehnet-software-mirrors.service
 fi
 flock -w 20 9 || { echo 'ROLLBACK_REQUIRES_OPERATOR: operation lock busy' >&2; return 1; }
 if [[ "$CHANGED" == 1 ]]; then
  python3 - <<'PY'
from pathlib import Path
import os,sqlite3,json,shutil
from contextlib import closing
p=Path(os.environ['MIRROR_INSTALL_BACKUP']);current=Path('/srv/tehnet-software/metadata/public/external.sqlite')
expected={e['artifact']['sha256'] for e in json.loads(Path('catalog/public-downloads.json').read_text())['entries']}
with closing(sqlite3.connect(current.as_uri()+'?mode=ro',uri=True)) as db:
 assert {x[0] for x in db.execute('SELECT sha256 FROM external')}<=expected,'Concurrent unknown metadata; stop and reconcile, do not overwrite'
owner=current.stat();target=current.parent/'.rollback-metadata.sqlite'
assert not target.exists()
shutil.copyfile(p/'previous-public.sqlite',target);target.chmod(0o600);os.chown(target,owner.st_uid,owner.st_gid);os.replace(target,current)
PY
  [[ $? == 0 ]] || { echo 'ROLLBACK_REQUIRES_OPERATOR: newer metadata preserved' >&2; return 1; }
 fi
 echo "PUBLIC_METADATA_ROLLBACK_PASS backup=$BACKUP"
}
failure(){ status="$1"; rollback || true; exit "$status"; }
trap 'failure $?' ERR
trap 'failure 130' INT
trap 'failure 143' TERM
trap 'failure 129' HUP
trap 'status=$?; if [[ "$status" != 0 ]]; then failure "$status"; fi' EXIT
CHANGED=1
python3 -m tools.mirror_operations --manifest catalog/public-downloads.json --public-root /srv/tehnet-software/metadata/public --ops-root /srv/tehnet-software/ops > "$BACKUP/first-refresh.json"
UNITS=1
install -m 644 deployment/systemd/tehnet-software-mirrors.service /etc/systemd/system/tehnet-software-mirrors.service
install -m 644 deployment/systemd/tehnet-software-mirrors.timer /etc/systemd/system/tehnet-software-mirrors.timer
systemctl daemon-reload
flock -u 9
# Actual constrained service must pass before enabling its periodic timer.
systemctl start tehnet-software-mirrors.service
[[ "$(systemctl show -p ExecMainStatus --value tehnet-software-mirrors.service)" == 0 ]]
flock -w 20 9
python3 -m app.recovery validate --root /srv/tehnet-software > "$BACKUP/state-validated.json"
curl --fail --silent --show-error --max-time 10 --resolve tehnet.ir:443:127.0.0.1 https://tehnet.ir/software/readyz | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="ready" and d["capabilities"]["downloads"] is True and d["capabilities"]["rubika"] is False'
fingerprint > "$BACKUP/containers.after"
sha256sum /etc/nginx/sites-enabled/tehnet.ir.conf /etc/nginx/snippets/tehnet-software.conf /srv/tehnet-software/data/catalog.sqlite /srv/tehnet-software/auth/auth.sqlite /srv/tehnet-software/metadata/restricted/external.sqlite > "$BACKUP/unchanged.after"
cmp "$BACKUP/containers.before" "$BACKUP/containers.after"
cmp "$BACKUP/unchanged.before" "$BACKUP/unchanged.after"
systemctl enable --now tehnet-software-mirrors.timer
[[ "$(systemctl is-active tehnet-software-mirrors.timer)" == active ]]
trap - ERR INT TERM HUP EXIT
printf 'PUBLIC_MIRRORS_ACTIVE files=3 payload_disk_files=0 container_restarts=0 backup=%s\n' "$BACKUP" | tee "$BACKUP/result.txt"
cp "$BACKUP/first-refresh.json" "$OPS/live-first-refresh.json"
printf '%s\n' "$BACKUP" > "$OPS/live-backup-path.txt"
