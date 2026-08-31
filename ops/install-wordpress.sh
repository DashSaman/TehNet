#!/usr/bin/env bash
set -euo pipefail
required=(TEHNET_DB_NAME TEHNET_DB_USER TEHNET_DB_PASSWORD TEHNET_ADMIN_USER TEHNET_ADMIN_PASSWORD TEHNET_ADMIN_EMAIL)
for key in "${required[@]}"; do
  [[ -n "${!key:-}" ]] || { echo "Missing required environment variable: $key" >&2; exit 64; }
done
[[ ${EUID:-$(id -u)} -eq 0 ]] || { echo "Run with sudo -E." >&2; exit 77; }
[[ "$TEHNET_DB_NAME" =~ ^[A-Za-z0-9_]+$ ]] || { echo "Unsafe TEHNET_DB_NAME" >&2; exit 65; }
[[ "$TEHNET_DB_USER" =~ ^[A-Za-z0-9_]+$ ]] || { echo "Unsafe TEHNET_DB_USER" >&2; exit 65; }
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq nginx mariadb-server curl ca-certificates rsync unzip php-fpm php-cli php-mysql php-curl php-gd php-mbstring php-xml php-zip php-intl
install -d -m 0755 /var/www/tehnet
install -d -m 0700 /opt/tehnet/backups
systemctl enable --now mariadb nginx
DB_PASS_ESCAPED="${TEHNET_DB_PASSWORD//\'/\'\'}"
mariadb <<SQL
CREATE DATABASE IF NOT EXISTS \`$TEHNET_DB_NAME\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '$TEHNET_DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS_ESCAPED';
ALTER USER '$TEHNET_DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS_ESCAPED';
GRANT ALL PRIVILEGES ON \`$TEHNET_DB_NAME\`.* TO '$TEHNET_DB_USER'@'localhost';
FLUSH PRIVILEGES;
SQL
if ! command -v wp >/dev/null 2>&1; then
  curl -fsSL https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar -o /usr/local/bin/wp
  chmod 0755 /usr/local/bin/wp
fi
if [[ ! -f /var/www/tehnet/wp-load.php ]]; then sudo -u www-data wp core download --path=/var/www/tehnet --locale=fa_IR; fi
if [[ ! -f /var/www/tehnet/wp-config.php ]]; then
  sudo -u www-data wp config create --path=/var/www/tehnet --dbname="$TEHNET_DB_NAME" --dbuser="$TEHNET_DB_USER" --dbpass="$TEHNET_DB_PASSWORD" --dbhost=localhost --dbcharset=utf8mb4 --skip-check
  sudo -u www-data wp config shuffle-salts --path=/var/www/tehnet
fi
if ! sudo -u www-data wp core is-installed --path=/var/www/tehnet >/dev/null 2>&1; then
  sudo -u www-data wp core install --path=/var/www/tehnet --url='https://tehnet.ir' --title='TehNet' --admin_user="$TEHNET_ADMIN_USER" --admin_password="$TEHNET_ADMIN_PASSWORD" --admin_email="$TEHNET_ADMIN_EMAIL" --skip-email
fi
sudo -u www-data wp option update home 'https://tehnet.ir' --path=/var/www/tehnet
sudo -u www-data wp option update siteurl 'https://tehnet.ir' --path=/var/www/tehnet
sudo -u www-data wp rewrite structure '/%postname%/' --hard --path=/var/www/tehnet
sudo -u www-data wp rewrite flush --hard --path=/var/www/tehnet
chown -R www-data:www-data /var/www/tehnet
find /var/www/tehnet -type d -exec chmod 0755 {} +
find /var/www/tehnet -type f -exec chmod 0644 {} +
chmod 0640 /var/www/tehnet/wp-config.php
echo "Runtime installed; Nginx vhost activation remains a separately validated step."
