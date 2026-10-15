#!/usr/bin/env bash
# Full, private TehNet-only checkpoint. Does not stop or modify any running service.
set -euo pipefail
umask 077
test "$(id -u)" = 0
test "$(docker port tehnet-wordpress 80/tcp)" = '127.0.0.1:18082'
BASE=/root/tehnet-backups
mkdir -p "$BASE"
BACKUP="$BASE/$(date -u +%Y%m%d-%H%M%S)-store-review"
mkdir -m 700 "$BACKUP"
docker ps --format '{{.Names}}' | sort > "$BACKUP/containers.txt"
python3 - "$BACKUP" <<'PY'
import subprocess,json,hashlib,sys,pathlib
names=subprocess.check_output(['docker','ps','--format','{{.Names}}'],text=True).splitlines()
names=sorted(n for n in names if not n.startswith('tehnet-'))
objects=json.loads(subprocess.check_output(['docker','inspect',*names]))
data=[{'name':x['Name'],'id':x['Id'],'image':x['Image'],'started_at':x['State']['StartedAt'],'ports':x['HostConfig']['PortBindings']} for x in objects]
pathlib.Path(sys.argv[1],'unrelated-runtime.json').write_text(json.dumps(data,sort_keys=True,indent=2))
PY
docker exec tehnet-wordpress tar -czf - -C /var/www/html . > "$BACKUP/wordpress-files.tar.gz"
docker exec tehnet-db sh -c 'exec mariadb-dump -uroot -p"$MARIADB_ROOT_PASSWORD" --single-transaction --quick --skip-lock-tables --routines --triggers "$MARIADB_DATABASE"' | gzip -1 > "$BACKUP/tehnet.sql.gz"
cp -p /opt/tehnet/compose.yaml "$BACKUP/compose.yaml"
cp -p /opt/tehnet/.env "$BACKUP/compose.env"
if test -f /root/tehnet-secrets/wp-admin-bootstrap.env; then cp -p /root/tehnet-secrets/wp-admin-bootstrap.env "$BACKUP/wp-admin-bootstrap.env"; fi
tar -czf "$BACKUP/nginx-config.tar.gz" -C /etc nginx
docker exec tehnet-wordpress sh -c 'find wp-content/themes/tehnet wp-content/plugins/tehnet-core -type f -exec sha256sum {} +' > "$BACKUP/live-code-sha256.txt"
gzip -t "$BACKUP/tehnet.sql.gz"
tar -tzf "$BACKUP/wordpress-files.tar.gz" >/dev/null
tar -tzf "$BACKUP/nginx-config.tar.gz" >/dev/null
(cd "$BACKUP" && sha256sum wordpress-files.tar.gz tehnet.sql.gz compose.yaml compose.env nginx-config.tar.gz > SHA256SUMS && sha256sum -c SHA256SUMS >/dev/null)
chmod -R go-rwx "$BACKUP"
printf 'BACKUP_READY=%s\n' "$BACKUP"
du -h "$BACKUP/wordpress-files.tar.gz" "$BACKUP/tehnet.sql.gz"
