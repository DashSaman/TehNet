#!/usr/bin/env bash
# Authorized TehNet-only presentation deployment. No restarts or routing changes.
set -Eeuo pipefail
umask 077
ROOT=/root/tehnet-visual-release-20261013
LIVE=/var/lib/docker/volumes/tehnet_tehnet-wp-data/_data/wp-content/themes/tehnet
REPO=/root/TehNet
BASE=8a6cada
cd "$ROOT"
exec 9>/root/tehnet-backups/.visual-deploy.lock
flock -n 9 || { echo 'Another visual deploy is running'; exit 1; }
files=(header.php footer.php functions.php style.css page-portfolio.php assets/css/visual-refresh.css assets/js/visual-refresh.js assets/img/network-art.svg assets/profile/Amirreza-Golavar-Resume.txt assets/profile/Amirreza-Golavar.vcf)
existing=(header.php footer.php functions.php style.css)
for f in "${existing[@]}"; do
  git -C "$REPO" show "$BASE:site/themes/tehnet/$f" | cmp -s - "$LIVE/$f" || { echo "Concurrent live change: $f"; exit 1; }
done
for f in "${files[@]:4}"; do
  test ! -e "$LIVE/$f" || { echo "New target already exists: $f"; exit 1; }
done
for f in "${files[@]}"; do test -s "$ROOT/site/themes/tehnet/$f"; done
b=/root/tehnet-backups/$(date -u +%Y%m%d-%H%M%S)-visual-release
mkdir -p "$b/files"
printf '%s\n' "$b" > /root/tehnet-backups/latest-visual-release-path
for f in "${existing[@]}"; do cp -p "$LIVE/$f" "$b/files/$f"; done
docker ps --no-trunc --format '{{.Names}}|{{.ID}}|{{.Image}}|{{.Ports}}' | grep -v '^tehnet-' | sort > "$b/non-tehnet-before.txt"
find "$LIVE/assets/fonts" -type f -exec sha256sum {} + | sort > "$b/fonts-before.txt"
find /var/lib/docker/volumes/tehnet_tehnet-wp-data/_data/wp-content/plugins/tehnet-core -type f -exec sha256sum {} + | sort > "$b/core-before.txt"
docker exec tehnet-db sh -c 'exec mariadb-dump --single-transaction -uroot -p"${MARIADB_ROOT_PASSWORD:-$MYSQL_ROOT_PASSWORD}" "${MARIADB_DATABASE:-$MYSQL_DATABASE}"' | gzip > "$b/tehnet.sql.gz"
gzip -t "$b/tehnet.sql.gz"
test "$(stat -c%s "$b/tehnet.sql.gz")" -gt 1000
tar -czf "$b/theme.tar.gz" -C "$LIVE" .
tar -tzf "$b/theme.tar.gz" > /dev/null
docker cp "$ROOT" tehnet-wordpress:/tmp/tehnet-visual-release
for f in header.php footer.php functions.php page-portfolio.php; do docker exec tehnet-wordpress php -l "/tmp/tehnet-visual-release/site/themes/tehnet/$f"; done
docker exec tehnet-wordpress php /tmp/tehnet-visual-release/ops/visual/apply-content.php prepare
docker cp tehnet-wordpress:/tmp/tehnet-visual-release/state-before.json "$b/state-before.json"
rollback() {
  status=$?; trap - ERR; set +e
  echo 'Deployment verification failed; restoring only changed presentation and target content.'
  for f in "${existing[@]}"; do cp -p "$b/files/$f" "$LIVE/$f"; done
  docker exec tehnet-wordpress php /tmp/tehnet-visual-release/ops/visual/apply-content.php rollback
  mkdir -p "$b/introduced-files"
  for f in "${files[@]:4}"; do
    if test -f "$LIVE/$f"; then mkdir -p "$b/introduced-files/$(dirname "$f")"; mv "$LIVE/$f" "$b/introduced-files/$f"; fi
  done
  echo "ROLLBACK_BACKUP=$b"; exit "$status"
}
trap rollback ERR
for f in "${files[@]}"; do
  install -D -m 0644 -o 33 -g 33 "$ROOT/site/themes/tehnet/$f" "$LIVE/$f.visual-new"
  mv "$LIVE/$f.visual-new" "$LIVE/$f"
done
docker exec tehnet-wordpress php /tmp/tehnet-visual-release/ops/visual/apply-content.php apply
for route in / /amirreza-golavar/ /learn/ /services/ /shop/; do
  code=$(curl -sS -o "$b/origin-$(echo "$route" | tr / _).html" -w '%{http_code}' -H 'Host: tehnet.ir' -H 'X-Forwarded-Proto: https' "http://127.0.0.1:18082$route")
  echo "ORIGIN $route $code"; test "$code" = 200
done
docker ps --no-trunc --format '{{.Names}}|{{.ID}}|{{.Image}}|{{.Ports}}' | grep -v '^tehnet-' | sort > "$b/non-tehnet-after.txt"
find "$LIVE/assets/fonts" -type f -exec sha256sum {} + | sort > "$b/fonts-after.txt"
find /var/lib/docker/volumes/tehnet_tehnet-wp-data/_data/wp-content/plugins/tehnet-core -type f -exec sha256sum {} + | sort > "$b/core-after.txt"
cmp "$b/non-tehnet-before.txt" "$b/non-tehnet-after.txt"
cmp "$b/fonts-before.txt" "$b/fonts-after.txt"
cmp "$b/core-before.txt" "$b/core-after.txt"
docker cp tehnet-wordpress:/tmp/tehnet-visual-release/created-profile-id "$b/created-profile-id"
trap - ERR
echo "DEPLOYMENT=PASS BACKUP=$b"
echo 'UNRELATED_RUNTIME_CORE_AND_FONTS=UNCHANGED'
