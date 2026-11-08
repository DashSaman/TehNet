#!/usr/bin/env bash
set -euo pipefail
test "${RUNNER_ENVIRONMENT:-}" = github-hosted
test "${GITHUB_REPOSITORY:-}" = DashSaman/TehNet
stage_root="$(mktemp -d /tmp/tn-seo-native-XXXXXX)"
stage_net="tn-seo-$GITHUB_RUN_ID"
stage_db="tn-seo-db-$GITHUB_RUN_ID"
stage_cli="tn-seo-cli-$GITHUB_RUN_ID"
cleanup(){ docker rm -f -v "$stage_db" "$stage_cli" >/dev/null 2>&1 || true; docker network rm "$stage_net" >/dev/null 2>&1 || true; case "$stage_root" in /tmp/tn-seo-native-*) rm -rf -- "$stage_root";; esac; }
trap cleanup EXIT
stage_password="$(openssl rand -hex 24)"
echo "::add-mask::$stage_password"
docker network create --internal "$stage_net" >/dev/null
docker run -d --name "$stage_db" --network "$stage_net" --network-alias db -e MARIADB_ROOT_PASSWORD="$stage_password" -e MARIADB_DATABASE=wordpress mariadb:11.4.13-noble >/dev/null
for n in {1..40}; do if docker exec "$stage_db" healthcheck.sh --connect --innodb_initialized >/dev/null 2>&1; then break; fi; sleep 1; done
docker create --name "$stage_cli" wordpress:cli-2.12.0-php8.3 >/dev/null
docker cp "$stage_cli:/usr/local/bin/wp" "$stage_root/wp"
docker run --rm --network "$stage_net" -e TN_FIXTURE_PASSWORD="$stage_password" -v "$PWD:/src:ro" -v "$stage_root:/lab" --entrypoint bash wordpress:7.1.4-php8.3-apache -eu -c '
cp -a /usr/src/wordpress/. /var/www/html/
cp -a /src/site/. /var/www/html/wp-content/
cat > /var/www/html/wp-content/mu-plugins/tn-isolation.php <<'"'"'PHP'"'"'
<?php
add_filter("pre_wp_mail","__return_false",PHP_INT_MAX);
add_filter("pre_http_request",static fn()=>new WP_Error("closed_fixture","Blocked"),PHP_INT_MAX,3);
add_filter("woocommerce_available_payment_gateways","__return_empty_array",PHP_INT_MAX);
PHP
cd /var/www/html
php /lab/wp --allow-root config create --dbname=wordpress --dbuser=root --dbpass="$TN_FIXTURE_PASSWORD" --dbhost=db --skip-check --extra-php <<'"'"'PHP'"'"'
define("WP_ENVIRONMENT_TYPE","staging");
define("DISABLE_WP_CRON",true);
define("WP_HTTP_BLOCK_EXTERNAL",true);
define("WP_POST_REVISIONS",false);
PHP
php /lab/wp --allow-root core install --url=https://example.invalid --title="Synthetic fixture" --admin_user=fixture --admin_password="$TN_FIXTURE_PASSWORD" --admin_email=fixture@example.invalid --skip-email
php /lab/wp --allow-root option update blog_public 0
php /lab/wp --allow-root plugin activate tehnet-core tehnet-store
php /lab/wp --allow-root --user=1 eval-file /src/tests/seo-readiness-native.php
'
echo "TN_SEO_CLEANUP_PENDING_TRAP"
