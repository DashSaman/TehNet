#!/usr/bin/env bash
# Scoped same-schema code activation; rollback never overwrites newer engine state.
set -Eeuo pipefail
umask 077
RELEASE="$(realpath "${1:?release directory required}")"
IMAGE="${2:?immutable image ID required}"
KEY_HOME="$(realpath "${3:?temporary protected decryption/encryption key home required}")"
RECIPIENT="${4:?full encryption recipient fingerprint required}"
MODE="${5:---activate}"
[[ "$RELEASE" == /opt/tehnet-software/releases/* && "$IMAGE" =~ ^sha256:[a-f0-9]{64}$ ]]
[[ "$RECIPIENT" =~ ^[A-Fa-f0-9]{40}$ || "$RECIPIENT" =~ ^[A-Fa-f0-9]{64}$ ]]
[[ "$MODE" == --activate || "$MODE" == --rehearse ]]
[[ "$(id -u)" == 0 ]]
exec 9>/run/lock/tehnet-software-engine.lock
flock -n 9 || { echo 'Another engine operation is active' >&2; exit 2; }
export PYTHONPATH="$RELEASE/host-site:$RELEASE"
export PYTHONDONTWRITEBYTECODE=1
OLD_IMAGE="$(docker inspect -f '{{.Image}}' tehnet-software)"
OLD_COMPOSE="$(docker inspect -f '{{ index .Config.Labels "com.docker.compose.project.config_files" }}' tehnet-software)"
[[ "$OLD_IMAGE" =~ ^sha256:[a-f0-9]{64}$ && -f "$OLD_COMPOSE" ]]
[[ "$OLD_COMPOSE" == /opt/tehnet-software/releases/* || "$OLD_COMPOSE" == /root/tehnet-backups/*/previous-compose.yaml ]]
[[ "$(docker port tehnet-wordpress 80/tcp)" == '127.0.0.1:18082' ]]
docker image inspect "$IMAGE" >/dev/null
TEHNET_SOFTWARE_IMAGE="$IMAGE" docker compose -p tehnet-software -f "$RELEASE/compose.engine.yaml" config --quiet
BACKUP="/root/tehnet-backups/$(date -u +%Y%m%d-%H%M%S)-software-engine-${MODE#--}"
mkdir -m 700 "$BACKUP"
SNIPPET=/etc/nginx/snippets/tehnet-software.conf
fingerprint(){ docker ps -a --no-trunc --format '{{.Names}}|{{.ID}}|{{.Image}}|{{.Ports}}' | grep -v '^tehnet-software|' | sort; }
fingerprint > "$BACKUP/containers.before"
sha256sum /etc/nginx/sites-enabled/tehnet.ir.conf > "$BACKUP/site.before"
cp "$OLD_COMPOSE" "$BACKUP/previous-compose.yaml"
cp "$SNIPPET" "$BACKUP/previous-snippet.conf"
printf '%s\n' "$OLD_IMAGE" > "$BACKUP/previous-image.txt"
printf '%s\n' "$IMAGE" > "$BACKUP/engine-image.txt"
cp -L /etc/nginx/sites-enabled/tehnet.ir.conf "$BACKUP/site.conf"
cp /opt/tehnet/compose.yaml "$BACKUP/wordpress-compose.yaml"
[[ ! -f /opt/tehnet/.env ]] || cp /opt/tehnet/.env "$BACKUP/wordpress.env"
docker exec tehnet-db sh -c 'MYSQL_PWD="$MARIADB_ROOT_PASSWORD" mariadb-dump -uroot --single-transaction --routines --triggers "$MARIADB_DATABASE"' | gzip > "$BACKUP/tehnet.sql.gz"
docker exec tehnet-wordpress tar -czf - -C /var/www/html wp-content > "$BACKUP/wp-content.tar.gz"
gzip -t "$BACKUP/tehnet.sql.gz"; tar -tzf "$BACKUP/wp-content.tar.gz" >/dev/null
START=$SECONDS; PROBE="tehnet-software-recovery-$(date -u +%Y%m%d%H%M%S)"
PROBE_CREATED=0; CHANGED=0
ready(){
 for attempt in $(seq 1 25); do
  if curl --fail --silent --show-error --max-time 3 --resolve tehnet.ir:443:127.0.0.1 https://tehnet.ir/software/readyz > "$BACKUP/ready.json" && python3 -c 'import json,sys; assert json.load(open(sys.argv[1]))["status"]=="ready"' "$BACKUP/ready.json"; then return 0; fi
  sleep 1
 done
 return 1
}
preserved(){
 fingerprint > "$BACKUP/containers.after"
 sha256sum /etc/nginx/sites-enabled/tehnet.ir.conf > "$BACKUP/site.after"
 cmp "$BACKUP/containers.before" "$BACKUP/containers.after"
 cmp "$BACKUP/site.before" "$BACKUP/site.after"
 for path in / /learn/ /services/ /shop/ /contact/ /software/; do
  curl --fail --silent --show-error --max-time 15 --resolve tehnet.ir:443:127.0.0.1 -o /dev/null "https://tehnet.ir$path"
 done
}
rollback(){
 trap - ERR INT TERM HUP EXIT
 set +e
 [[ "$PROBE_CREATED" == 0 ]] || docker rm -f "$PROBE" >/dev/null 2>&1
 if [[ "$CHANGED" != 0 ]]; then
  docker stop --time 25 tehnet-software >/dev/null 2>&1
  TEHNET_SOFTWARE_IMAGE="$OLD_IMAGE" docker compose -p tehnet-software -f "$BACKUP/previous-compose.yaml" up -d --pull never --no-build
  if [[ "$(docker inspect -f '{{.Image}}' tehnet-software)" == "$OLD_IMAGE" ]]; then
   cp "$BACKUP/previous-snippet.conf" "$SNIPPET"
   nginx -t && systemctl reload nginx
  fi
 fi
 if [[ "$(docker inspect -f '{{.Image}}' tehnet-software)" == "$OLD_IMAGE" ]] && cmp "$BACKUP/previous-snippet.conf" "$SNIPPET" && ready && preserved; then
  printf 'ROLLBACK_PASS state_preserved=true elapsed_seconds=%s backup=%s\n' "$((SECONDS-START))" "$BACKUP" | tee "$BACKUP/rollback-result.txt"
  return 0
 fi
 echo 'ROLLBACK_INCOMPLETE: preserve backups; inspect server privately' >&2
 return 1
}
failure(){ status="$1"; rollback || true; exit "$status"; }
trap 'failure $?' ERR
trap 'failure 130' INT
trap 'failure 143' TERM
trap 'failure 129' HUP
trap 'status=$?; if [[ "$status" != 0 ]]; then failure "$status"; fi' EXIT
CHANGED=1
docker stop --time 25 tehnet-software >/dev/null
python3 -m app.recovery backup --root /srv/tehnet-software --destination "$BACKUP/engine-state.gpg" --key-home "$KEY_HOME" --recipient "$RECIPIENT" --image "$IMAGE" --quiesced --compose "$RELEASE/compose.engine.yaml" --nginx-snippet "$RELEASE/deployment/nginx-engine.conf" > "$BACKUP/backup-result.json"
EXPECTED="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["cipher_sha256"])' "$BACKUP/backup-result.json")"
python3 -m app.recovery restore --bundle "$BACKUP/engine-state.gpg" --staging "$BACKUP/restored" --key-home "$KEY_HOME" --expected-sha256 "$EXPECTED" > "$BACKUP/restore-result.json"
chown -R 10001:10001 "$BACKUP/restored"
! docker container inspect "$PROBE" >/dev/null 2>&1
PROBE_CREATED=1
docker run -d --name "$PROBE" --network none --read-only --user 10001:10001 --cap-drop ALL --security-opt no-new-privileges:true --memory 256m --cpus .5 --pids-limit 64 --tmpfs /tmp:rw,nosuid,noexec,size=16m \
 -e TEHNET_SOFTWARE_DATA=/data -e TEHNET_SOFTWARE_AUTH=/auth -e TEHNET_SOFTWARE_METADATA=/metadata -e TEHNET_SOFTWARE_RESTRICTED=1 \
 -v "$BACKUP/restored/data:/data:ro" -v "$BACKUP/restored/metadata:/metadata:ro" -v "$BACKUP/restored/auth:/auth:rw" "$IMAGE" >/dev/null
for attempt in $(seq 1 20); do
 if docker exec "$PROBE" python -c 'import urllib.request,json; r=json.load(urllib.request.urlopen("http://127.0.0.1:8000/software/readyz",timeout=2)); assert r["status"]=="ready"' >/dev/null 2>&1; then break; fi
 [[ "$attempt" != 20 ]]; sleep 1
done
docker rm -f "$PROBE" >/dev/null; PROBE_CREATED=0
printf 'RECOVERY_PASS elapsed_seconds=%s\n' "$((SECONDS-START))" > "$BACKUP/recovery-result.txt"
cp "$RELEASE/deployment/nginx-engine.conf" "$SNIPPET"
nginx -t; systemctl reload nginx
TEHNET_SOFTWARE_IMAGE="$IMAGE" docker compose -p tehnet-software -f "$RELEASE/compose.engine.yaml" up -d --pull never --no-build
ready
[[ "$(docker inspect -f '{{.Image}}' tehnet-software)" == "$IMAGE" ]]
[[ "$(curl --silent --max-time 10 --resolve tehnet.ir:443:127.0.0.1 -o /dev/null -w '%{http_code}' https://tehnet.ir/software/private/known)" == 404 ]]
CODE="$(curl --silent --max-time 10 --resolve tehnet.ir:443:127.0.0.1 -o /dev/null -w '%{http_code}' https://tehnet.ir/software/access/)"
[[ "$CODE" == 200 || "$CODE" == 503 ]]
preserved
if [[ "$MODE" == --rehearse ]]; then
 if rollback; then echo "ENGINE_REHEARSAL_PASS backup=$BACKUP"; else exit 1; fi
else
 trap - ERR INT TERM HUP EXIT
 printf 'ENGINE_ACTIVE_PASS elapsed_seconds=%s image=%s backup=%s\n' "$((SECONDS-START))" "$IMAGE" "$BACKUP" | tee "$BACKUP/activation-result.txt"
fi
