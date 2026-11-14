#!/usr/bin/env bash
set -euo pipefail
test "${RUNNER_ENVIRONMENT:-}" = github-hosted
test "${GITHUB_REPOSITORY:-}" = DashSaman/TehNet
stage_root="$(mktemp -d /tmp/tn-seo-native-XXXXXX)"
stage_net="tn-seo-$GITHUB_RUN_ID"
stage_db="tn-seo-db-$GITHUB_RUN_ID"
stage_cli="tn-seo-cli-$GITHUB_RUN_ID"
stage_app="tn-seo-app-$GITHUB_RUN_ID"
stage_relay_pid=""
cleanup(){ if test -n "$stage_relay_pid"; then sudo kill "$stage_relay_pid" 2>/dev/null || true; fi; docker rm -f -v "$stage_app" "$stage_db" "$stage_cli" >/dev/null 2>&1 || true; docker network rm "$stage_net" >/dev/null 2>&1 || true; case "$stage_root" in /tmp/tn-seo-native-*) rm -rf -- "$stage_root";; esac; }
trap cleanup EXIT
stage_password="$(openssl rand -hex 24)"
echo "::add-mask::$stage_password"
curl --fail --location --proto '=https' --tlsv1.2 --max-time 120 --output "$stage_root/woocommerce.zip" https://github.com/woocommerce/woocommerce/releases/download/11.2.1/woocommerce.zip
echo "3066f85e46d1c1f6451296da0300b459963b504fd0d2f75869701ee744833aaf  $stage_root/woocommerce.zip" | sha256sum --check --status
npm install --prefix "$stage_root/pw" --ignore-scripts --no-audit --no-fund playwright@1.56.1 >/dev/null
PLAYWRIGHT_BROWSERS_PATH="$stage_root/browsers" node "$stage_root/pw/node_modules/playwright/cli.js" install --with-deps chromium >/dev/null
docker network create --internal "$stage_net" >/dev/null
docker run -d --name "$stage_db" --network "$stage_net" --network-alias db -e MARIADB_ROOT_PASSWORD="$stage_password" -e MARIADB_DATABASE=wordpress mariadb:11.4.13-noble >/dev/null
for n in {1..40}; do if docker exec "$stage_db" healthcheck.sh --connect --innodb_initialized >/dev/null 2>&1; then break; fi; sleep 1; done
docker create --name "$stage_cli" wordpress:cli-2.12.0-php8.3 >/dev/null
docker cp "$stage_cli:/usr/local/bin/wp" "$stage_root/wp"
docker run -d --name "$stage_app" --network "$stage_net" -e TN_FIXTURE_PASSWORD="$stage_password" -v "$PWD:/src:ro" -v "$stage_root:/lab" --entrypoint bash wordpress:7.1.4-php8.3-apache -eu -c '
cp -a /usr/src/wordpress/. /var/www/html/
cp -a /src/site/. /var/www/html/wp-content/
cd /var/www/html/wp-content/plugins
php -r '"'"'$z=new ZipArchive();$z->open("/lab/woocommerce.zip");$z->extractTo(".");$z->close();'"'"'
cat > /var/www/html/wp-content/mu-plugins/tn-isolation.php <<'"'"'PHP'"'"'
<?php
add_filter("pre_wp_mail","__return_false",PHP_INT_MAX);
add_filter("pre_http_request",static function($pre,$args,$url){if($url==="https://www.google.com/recaptcha/api/siteverify"&&hash_equals(getenv("TN_FIXTURE_PASSWORD"),(string)($args["body"]["response"]??"")))return ["headers"=>[],"body"=>wp_json_encode(["success"=>true,"hostname"=>"localhost","challenge_ts"=>gmdate("c")]),"response"=>["code"=>200,"message"=>"OK"]];return new WP_Error("closed_fixture","Blocked");},PHP_INT_MAX,3);
add_filter("woocommerce_available_payment_gateways","__return_empty_array",PHP_INT_MAX);
PHP
cd /var/www/html
php /lab/wp --allow-root config create --dbname=wordpress --dbuser=root --dbpass="$TN_FIXTURE_PASSWORD" --dbhost=db --skip-check --extra-php <<'"'"'PHP'"'"'
define("WP_ENVIRONMENT_TYPE","staging");
define("DISABLE_WP_CRON",true);
define("WP_HTTP_BLOCK_EXTERNAL",true);
define("WP_POST_REVISIONS",false);
define("WP_HOME","http://localhost:18085");
define("WP_SITEURL","http://localhost:18085");
PHP
php /lab/wp --allow-root core install --url=http://localhost:18085 --title="Synthetic fixture" --admin_user=fixture --admin_password="$TN_FIXTURE_PASSWORD" --admin_email=fixture@example.invalid --skip-email
php /lab/wp --allow-root option update blog_public 0
php /lab/wp --allow-root --user=1 eval-file /src/tests/seo-readiness-full.php seed
php /lab/wp --allow-root plugin activate woocommerce tehnet-core tehnet-store
php /lab/wp --allow-root theme activate tehnet
php /lab/wp --allow-root --user=1 eval-file /src/tests/seo-readiness-native.php
php /lab/wp --allow-root --user=1 eval-file /src/tests/seo-readiness-full.php apply
php /lab/wp --allow-root rewrite flush --hard
touch /lab/READY
exec apache2-foreground
'
for n in {1..120}; do test -f "$stage_root/READY" && break; if test "$(docker inspect -f '{{.State.Running}}' "$stage_app")" != true; then docker logs "$stage_app"; exit 1; fi; sleep 1; done
test -f "$stage_root/READY"
stage_app_pid="$(docker inspect -f '{{.State.Pid}}' "$stage_app")"
sudo nsenter --target "$stage_app_pid" --net -- node -e 'const net=require("node:net");net.createServer(c=>{const u=net.connect(80,"127.0.0.1");c.pipe(u);u.pipe(c);c.on("error",()=>u.destroy());u.on("error",()=>c.destroy());}).listen(18085,"127.0.0.1");' >"$stage_root/relay.log" 2>&1 &
stage_relay_pid="$!"
sleep 1
sudo nsenter --target "$stage_app_pid" --net -- env NODE_PATH="$stage_root/pw/node_modules" PLAYWRIGHT_BROWSERS_PATH="$stage_root/browsers" TN_FIXTURE_PASSWORD="$stage_password" node tests/seo-readiness-full-browser.cjs "$stage_root"
docker exec "$stage_app" php /lab/wp --allow-root --user=1 eval-file /src/tests/seo-readiness-full.php verify
docker exec "$stage_app" php /lab/wp --allow-root --user=1 eval-file /src/tests/seo-readiness-full.php diagnostic
docker logs "$stage_app" 2>&1 | sed -n '/TN_SEO_NATIVE /p'
cleanup
trap - EXIT
if docker inspect "$stage_app" >/dev/null 2>&1 || docker inspect "$stage_db" >/dev/null 2>&1 || docker network inspect "$stage_net" >/dev/null 2>&1; then echo TN_P94_CLEANUP_FAILED; exit 1; fi
echo TN_P94_CLEANUP_VERIFIED
