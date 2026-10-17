#!/usr/bin/env bash
# Preview-only, no schema migration. Replace only the archive container.
set -Eeuo pipefail
umask 077
RELEASE="$(realpath "${1:?release directory required}")"
IMAGE="${2:?immutable image ID required}"
[[ "$RELEASE" == /opt/tehnet-software/releases/* ]]
[[ "$IMAGE" =~ ^sha256:[a-f0-9]{64}$ ]]
OLD_IMAGE="$(docker inspect -f '{{.Image}}' tehnet-software)"
[[ "$OLD_IMAGE" =~ ^sha256:[a-f0-9]{64}$ ]]
[[ "$(docker port tehnet-wordpress 80/tcp)" == '127.0.0.1:18082' ]]
BACKUP="/root/tehnet-backups/$(date -u +%Y%m%d-%H%M%S)-software-update"
mkdir -m 700 "$BACKUP"
fingerprint(){ docker ps -a --no-trunc --format '{{.Names}}|{{.ID}}|{{.Image}}|{{.Ports}}' | grep -v '^tehnet-software|' | sort; }
fingerprint > "$BACKUP/containers.before"
cp -L /etc/nginx/sites-enabled/tehnet.ir.conf "$BACKUP/nginx.conf"
cp /opt/tehnet/compose.yaml "$BACKUP/wordpress-compose.yaml"
cp "$RELEASE/compose.yaml" "$BACKUP/software-compose.yaml"
[[ ! -f /opt/tehnet/.env ]] || cp /opt/tehnet/.env "$BACKUP/.env"
docker exec tehnet-db sh -c 'MYSQL_PWD="$MARIADB_ROOT_PASSWORD" mariadb-dump -uroot --single-transaction --routines --triggers "$MARIADB_DATABASE"' | gzip > "$BACKUP/tehnet.sql.gz"
docker exec tehnet-wordpress tar -czf - -C /var/www/html wp-content > "$BACKUP/wp-content.tar.gz"
gzip -t "$BACKUP/tehnet.sql.gz"
tar -tzf "$BACKUP/wp-content.tar.gz" >/dev/null
# Current preview has no writers; still use SQLite's consistent backup API.
python3 - "$BACKUP/software.sqlite" <<'PY'
import sqlite3,sys
from contextlib import closing
with closing(sqlite3.connect('file:/srv/tehnet-software/data/catalog.sqlite?mode=ro',uri=True)) as source:
    with closing(sqlite3.connect(sys.argv[1])) as target:
        source.backup(target)
        assert target.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
PY
printf '%s\n' "$OLD_IMAGE" > "$BACKUP/previous-image.txt"
printf '%s\n' "$IMAGE" > "$BACKUP/new-image.txt"
ready(){
  for attempt in $(seq 1 20); do
    if curl --fail --silent --show-error --resolve tehnet.ir:443:127.0.0.1 https://tehnet.ir/software/readyz > "$BACKUP/ready.json"; then
      if python3 -c 'import json,sys; assert json.load(open(sys.argv[1])).get("status")=="ready"' "$BACKUP/ready.json"; then return 0; fi
    fi
    sleep 1
  done
  return 1
}
rollback(){
  status="${1:-1}"
  trap - ERR INT TERM EXIT
  set +e
  docker logs tehnet-software > "$BACKUP/software-failure.log" 2>&1
  if TEHNET_SOFTWARE_IMAGE="$OLD_IMAGE" docker compose -p tehnet-software -f "$RELEASE/compose.yaml" up -d --pull never --no-build && ready; then
    echo "UPDATE_FAILED_ROLLED_BACK backup=$BACKUP" >&2
  else echo "UPDATE_FAILED_ROLLBACK_INCOMPLETE backup=$BACKUP" >&2; fi
  exit "$status"
}
TEHNET_SOFTWARE_IMAGE="$IMAGE" docker compose -p tehnet-software -f "$RELEASE/compose.yaml" config --quiet
ready
trap 'rollback $?' ERR
trap 'rollback 130' INT
trap 'rollback 143' TERM
trap 'status=$?; if [[ "$status" != 0 ]]; then rollback "$status"; fi' EXIT
TEHNET_SOFTWARE_IMAGE="$IMAGE" docker compose -p tehnet-software -f "$RELEASE/compose.yaml" up -d --pull never --no-build
ready
for path in / /learn/ /services/ /shop/ /contact/ /software/; do
  curl --fail --silent --show-error --resolve tehnet.ir:443:127.0.0.1 -o /dev/null "https://tehnet.ir$path"
done
fingerprint > "$BACKUP/containers.after"
cmp "$BACKUP/containers.before" "$BACKUP/containers.after"
cmp "$BACKUP/nginx.conf" /etc/nginx/sites-enabled/tehnet.ir.conf
[[ "$(docker inspect -f '{{.Image}}' tehnet-software)" == "$IMAGE" ]]
trap - ERR INT TERM EXIT
echo "SOFTWARE_PREVIEW_UPDATE=PASS BACKUP=$BACKUP IMAGE=$IMAGE"
