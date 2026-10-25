#!/usr/bin/env bash
# First installation only. Existing TehNet code/containers are never redeployed.
set -Eeuo pipefail
umask 077
RELEASE="$(realpath "${1:?release directory required}")"
IMAGE="${2:?immutable image ID required}"
[[ "$RELEASE" == /opt/tehnet-software/releases/* ]] || { echo 'Invalid release root'; exit 1; }
[[ "$IMAGE" =~ ^sha256:[a-f0-9]{64}$ ]] || { echo 'Exact image ID required'; exit 1; }
[[ ! -f "$RELEASE/app/external_storage.py" ]] || { echo 'ENGINE_RELEASE_REQUIRES_NEW_STATE_BACKUP_AND_ROLLBACK_GATE' >&2; exit 2; }
[[ "$(docker port tehnet-wordpress 80/tcp)" == '127.0.0.1:18082' ]]
! docker container inspect tehnet-software >/dev/null 2>&1 || { echo 'Already installed: use reviewed upgrade procedure'; exit 1; }
! ss -ltnH '( sport = :18083 )' | grep -q . || { echo 'Port occupied'; exit 1; }
CONF=/etc/nginx/sites-enabled/tehnet.ir.conf
SNIPPET=/etc/nginx/snippets/tehnet-software.conf
[[ ! -e "$SNIPPET" ]] || { echo 'Snippet already exists'; exit 1; }
[[ ! -e /srv/tehnet-software/data ]] || { echo 'Data path exists; refusing replacement'; exit 1; }
[[ ! -L /srv/tehnet-software && ! -L /srv/tehnet-software/data ]]
# Check WordPress ownership before reserving the prefix, not just Nginx text.
conflict_code="$(curl --silent --show-error --resolve tehnet.ir:443:127.0.0.1 -o /dev/null -w '%{http_code}' https://tehnet.ir/software/)"
[[ "$conflict_code" == 404 ]] || { echo 'software route already exists or is not safely absent'; exit 1; }
docker exec --user www-data tehnet-wordpress php -r 'require "/var/www/html/wp-load.php"; if(get_page_by_path("software") || url_to_postid(home_url("/software/"))){exit(2);} foreach((array)get_option("rewrite_rules",[]) as $rule=>$query){if(str_contains($rule,"software")){exit(2);}}'
BACKUP="/root/tehnet-backups/$(date -u +%Y%m%d-%H%M%S)-software-preview"
mkdir -m 700 "$BACKUP"
fingerprint(){ docker ps -a --no-trunc --format '{{.Names}}|{{.ID}}|{{.Image}}|{{.Ports}}' | grep -v '^tehnet-software|' | sort; }
fingerprint > "$BACKUP/containers.before"
cp -L "$CONF" "$BACKUP/nginx.conf"
cp /opt/tehnet/compose.yaml "$BACKUP/compose.yaml"
[[ ! -f /opt/tehnet/.env ]] || cp /opt/tehnet/.env "$BACKUP/.env"
docker exec tehnet-db sh -c 'MYSQL_PWD="$MARIADB_ROOT_PASSWORD" mariadb-dump -uroot --single-transaction --routines --triggers "$MARIADB_DATABASE"' | gzip > "$BACKUP/tehnet.sql.gz"
docker exec tehnet-wordpress tar -czf - -C /var/www/html wp-content > "$BACKUP/wp-content.tar.gz"
gzip -t "$BACKUP/tehnet.sql.gz"
tar -tzf "$BACKUP/wp-content.tar.gz" >/dev/null

# Every public page is checked before the new route is installed.
for path in / /learn/ /services/ /shop/ /contact/; do
  code="$(curl --fail --silent --show-error --resolve tehnet.ir:443:127.0.0.1 -o /dev/null -w '%{http_code}' "https://tehnet.ir$path")"
  [[ "$code" == 200 ]] || { echo "Baseline failed: $path"; exit 1; }
done

MENU_CREATED=0
MENU_ID=0
MENU_ATTEMPTED=0
ROUTE_EDITED=0
APP_STARTED=0
DATA_CREATED=0
SNIPPET_CREATED=0
OWNER="software-preview-$(date -u +%Y%m%d%H%M%S)"
rollback(){
  status="${1:-1}"
  trap - ERR INT TERM EXIT
  set +e
  rollback_failed=0
  if [[ "$MENU_ATTEMPTED" == 1 ]]; then docker exec --user www-data tehnet-wordpress php /tmp/tehnet-software-menu.php rollback-owner "$OWNER" || rollback_failed=1; fi
  if [[ "$ROUTE_EDITED" == 1 ]]; then cp "$BACKUP/nginx.conf" "$CONF" && nginx -t && systemctl reload nginx || rollback_failed=1; fi
  if [[ "$APP_STARTED" == 1 ]]; then
    docker logs tehnet-software > "$BACKUP/software-failure.log" 2>&1 || true
    TEHNET_SOFTWARE_IMAGE="$IMAGE" docker compose -p tehnet-software -f "$RELEASE/compose.yaml" down || rollback_failed=1
  fi
  if [[ "$SNIPPET_CREATED" == 1 && -f "$SNIPPET" ]]; then mv "$SNIPPET" "$BACKUP/failed-software-snippet.conf" || rollback_failed=1; fi
  if [[ "$DATA_CREATED" == 1 && -d /srv/tehnet-software/data ]]; then mv /srv/tehnet-software/data "$BACKUP/failed-software-data" || rollback_failed=1; fi
  if [[ "$rollback_failed" == 0 ]]; then echo "DEPLOY_FAILED_ROLLED_BACK backup=$BACKUP status=$status" >&2;
  else echo "DEPLOY_FAILED_ROLLBACK_INCOMPLETE backup=$BACKUP status=$status" >&2; fi
  exit "$status"
}
trap 'rollback $?' ERR
trap 'rollback 130' INT
trap 'rollback 143' TERM
trap 'status=$?; if [[ "$status" != 0 ]]; then rollback "$status"; fi' EXIT

DATA_CREATED=1
mkdir -p /srv/tehnet-software/data
chown 10001:10001 /srv/tehnet-software/data
chmod 700 /srv/tehnet-software/data
docker run --rm --network none -v /srv/tehnet-software/data:/data "$IMAGE" python -m app.cli init-db
docker run --rm --network none -v /srv/tehnet-software/data:/data "$IMAGE" python -m app.cli seed-public-research
TEHNET_SOFTWARE_IMAGE="$IMAGE" docker compose -p tehnet-software -f "$RELEASE/compose.yaml" config --quiet
APP_STARTED=1
TEHNET_SOFTWARE_IMAGE="$IMAGE" docker compose -p tehnet-software -f "$RELEASE/compose.yaml" up -d --pull never --no-build
for attempt in $(seq 1 20); do
  if curl --fail --silent http://127.0.0.1:18083/software/readyz > "$BACKUP/ready.json"; then break; fi
  sleep 1
done
curl --fail --silent http://127.0.0.1:18083/software/readyz >/dev/null

SNIPPET_CREATED=1
cat > "$SNIPPET" <<'NGINX'
location = /software { return 308 /software/; }
location ^~ /software/ {
    proxy_pass http://127.0.0.1:18083;
    proxy_set_header Host $host;
    proxy_cache off;
    proxy_read_timeout 15s;
}
NGINX
ROUTE_EDITED=1
python3 - "$CONF" <<'PY'
from pathlib import Path
import re
import sys
path=Path(sys.argv[1])
data=path.read_text()
marker='    server_name tehnet.ir www.tehnet.ir;'
https_block=data.split('\nserver {',1)[0]
assert https_block.count(marker)==1 and '/software' not in data
assert re.search(r'\blisten\s+(?:\[::\]:)?443\s+ssl',https_block), 'First matching server must be HTTPS'
path.write_text(data.replace(marker,marker+'\n    include /etc/nginx/snippets/tehnet-software.conf;',1))
PY
ROUTE_EDITED=1
nginx -t
systemctl reload nginx
# deployment-stage: edge-check
EDGE_READY=0
for attempt in $(seq 1 10); do
  if curl --fail --silent --show-error --resolve tehnet.ir:443:127.0.0.1 https://tehnet.ir/software/readyz > "$BACKUP/edge-ready.json" 2>> "$BACKUP/edge-errors.log"; then
    if python3 -c 'import json,sys; assert json.load(open(sys.argv[1])).get("status")=="ready"' "$BACKUP/edge-ready.json"; then EDGE_READY=1; break; fi
  fi
  sleep 1
done
[[ "$EDGE_READY" == 1 ]]

docker cp "$RELEASE/software-menu.php" tehnet-wordpress:/tmp/tehnet-software-menu.php
docker cp "$RELEASE/software-menu-lib.php" tehnet-wordpress:/tmp/software-menu-lib.php
docker exec --user www-data tehnet-wordpress php /tmp/tehnet-software-menu.php plan > "$BACKUP/menu.before.json"
MENU_ATTEMPTED=1
docker exec --user www-data tehnet-wordpress php /tmp/tehnet-software-menu.php apply "$OWNER" > "$BACKUP/menu.result.json"
MENU_ID="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["id"])' "$BACKUP/menu.result.json")"
MENU_CREATED="$(python3 -c 'import json,sys; print(int(json.load(open(sys.argv[1]))["created"]))' "$BACKUP/menu.result.json")"
docker exec --user www-data tehnet-wordpress php /tmp/tehnet-software-menu.php plan > "$BACKUP/menu.after.json"

for path in / /learn/ /services/ /shop/ /contact/ /software/; do
  curl --fail --silent --show-error --resolve tehnet.ir:443:127.0.0.1 -o /dev/null "https://tehnet.ir$path"
done
fingerprint > "$BACKUP/containers.after"
cmp "$BACKUP/containers.before" "$BACKUP/containers.after"
[[ "$(docker port tehnet-wordpress 80/tcp)" == '127.0.0.1:18082' ]]
printf '%s\n' "$IMAGE" > "$BACKUP/software-image.txt"
printf '%s\n' "$OWNER" > "$BACKUP/menu-owner.txt"
trap - ERR INT TERM EXIT
echo "SOFTWARE_PREVIEW_DEPLOY=PASS"
echo "BACKUP=$BACKUP"
cat "$BACKUP/menu.result.json"
echo 'EXISTING_CONTAINERS_AND_PORTS=UNCHANGED'
