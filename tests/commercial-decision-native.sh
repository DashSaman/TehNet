#!/usr/bin/env bash
set -euo pipefail
test "${RUNNER_ENVIRONMENT:-}" = github-hosted
test "${GITHUB_REPOSITORY:-}" = DashSaman/TehNet
stage_root="$(mktemp -d /tmp/tn-decision-native-XXXXXX)"
stage_net="tn-decision-$GITHUB_RUN_ID"
stage_db="tn-decision-db-$GITHUB_RUN_ID"
stage_cli="tn-decision-cli-$GITHUB_RUN_ID"
stage_app="tn-decision-app-$GITHUB_RUN_ID"
stage_relay_pid=""
stage_relay_launcher=""
mkdir -p "$stage_root/web"
cleanup(){ if test -n "$stage_relay_pid"; then sudo kill "$stage_relay_pid" 2>/dev/null || true; if test -n "$stage_relay_launcher"; then wait "$stage_relay_launcher" 2>/dev/null || true; fi; fi; docker rm -f -v "$stage_app" "$stage_db" "$stage_cli" >/dev/null 2>&1 || true; docker network rm "$stage_net" >/dev/null 2>&1 || true; case "$stage_root" in /tmp/tn-decision-native-*) sudo rm -rf -- "$stage_root";; esac; }
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
docker run -d --name "$stage_app" --network "$stage_net" -e TN_FIXTURE_PASSWORD="$stage_password" -v "$PWD:/src:ro" -v "$stage_root:/lab" -v "$stage_root/web:/var/www/html" --entrypoint bash wordpress:7.1.4-php8.3-apache -eu -c '
for fixture_php in /src/tests/commercial-decision-native.php /src/tests/index-decision-native.php /src/ops/migrate-growth-content.php /src/ops/migrate-index-policy.php /src/site/plugins/tehnet-core/includes/class-content-types.php /src/site/plugins/tehnet-core/includes/class-index-policy.php; do php -l "$fixture_php"; done
cp -a /usr/src/wordpress/. /var/www/html/
cp -a /src/site/. /var/www/html/wp-content/
cd /var/www/html/wp-content/plugins
php -r '"'"'$z=new ZipArchive();$z->open("/lab/woocommerce.zip");$z->extractTo(".");$z->close();'"'"'
cat > /var/www/html/wp-content/mu-plugins/tn-isolation.php <<'"'"'PHP'"'"'
<?php
add_filter("pre_wp_mail","__return_false",PHP_INT_MAX);
add_filter("pre_http_request",static function($pre,$args,$url){if($url==="https://www.google.com/recaptcha/api/siteverify"&&hash_equals(getenv("TN_FIXTURE_PASSWORD"),(string)($args["body"]["response"]??"")))return ["headers"=>[],"body"=>wp_json_encode(["success"=>true,"hostname"=>"localhost","challenge_ts"=>gmdate("c")]),"response"=>["code"=>200,"message"=>"OK"]];return new WP_Error("closed_fixture","Blocked");},PHP_INT_MAX,3);
add_filter("woocommerce_available_payment_gateways","__return_empty_array",PHP_INT_MAX);
add_filter("wp_robots",static function($r){if(file_exists(ABSPATH."wp-content/tn-fixture-conflict-flag")&&is_page(29))$r["noindex"]=true;return $r;},999);
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
php /lab/wp --allow-root --user=1 eval-file /src/tests/commercial-decision-native.php seed
php /lab/wp --allow-root plugin activate woocommerce tehnet-core tehnet-store
php /lab/wp --allow-root theme activate tehnet
php /lab/wp --allow-root --user=1 eval-file /src/tests/commercial-decision-native.php prepare
php /lab/wp --allow-root rewrite flush --hard
touch /lab/READY
exec apache2-foreground
'
for n in {1..120}; do test -f "$stage_root/READY" && break; if test "$(docker inspect -f '{{.State.Running}}' "$stage_app")" != true; then docker logs "$stage_app"; exit 1; fi; sleep 1; done
test -f "$stage_root/READY"
export TN_STAGE_APP="$stage_app" TN_STAGE_DB="$stage_db" TN_STAGE_NET="$stage_net" TN_FIXTURE_PASSWORD="$stage_password"
sudo --preserve-env=TN_STAGE_APP,TN_STAGE_DB,TN_STAGE_NET,TN_FIXTURE_PASSWORD,GITHUB_SHA,RUNNER_ENVIRONMENT,GITHUB_REPOSITORY python3 tests/commercial-decision-release.py "$stage_root" prepare
sudo --preserve-env=TN_STAGE_APP,TN_STAGE_DB,TN_STAGE_NET,TN_FIXTURE_PASSWORD,GITHUB_SHA,RUNNER_ENVIRONMENT,GITHUB_REPOSITORY python3 tests/index-decision-release.py "$stage_root" prepare
docker exec "$stage_app" php /lab/wp --allow-root --user=1 eval-file /src/tests/commercial-decision-native.php baseline-routes
sudo --preserve-env=TN_STAGE_APP,TN_STAGE_DB,TN_STAGE_NET,TN_FIXTURE_PASSWORD,GITHUB_SHA,RUNNER_ENVIRONMENT,GITHUB_REPOSITORY python3 tests/commercial-decision-release.py "$stage_root" apply
docker exec "$stage_app" php /lab/wp --allow-root --user=1 eval-file /src/tests/commercial-decision-native.php accept
stage_app_pid="$(docker inspect -f '{{.State.Pid}}' "$stage_app")"
sudo nsenter --target "$stage_app_pid" --net -- node -e 'const fs=require("node:fs"),net=require("node:net");net.createServer(c=>{const u=net.connect(80,"127.0.0.1");c.pipe(u);u.pipe(c);c.on("error",()=>u.destroy());u.on("error",()=>c.destroy());}).listen(18085,"127.0.0.1");fs.writeFileSync(process.argv[1]+"/relay.pid",String(process.pid),{mode:0o600});' "$stage_root" >"$stage_root/relay.log" 2>&1 &
stage_relay_launcher="$!"
sleep 1
stage_relay_pid="$(sudo cat "$stage_root/relay.pid")"
case "$stage_relay_pid" in ""|*[!0-9]*) exit 1;; esac
sudo --preserve-env=TN_STAGE_APP,TN_STAGE_DB,TN_STAGE_NET,TN_FIXTURE_PASSWORD,GITHUB_SHA,RUNNER_ENVIRONMENT,GITHUB_REPOSITORY python3 tests/index-decision-release.py "$stage_root" runtime
docker exec "$stage_app" php /lab/wp --allow-root --user=1 eval-file /src/tests/index-decision-native.php off
sudo nsenter --target "$stage_app_pid" --net -- env NODE_PATH="$stage_root/pw/node_modules" PLAYWRIGHT_BROWSERS_PATH="$stage_root/browsers" node tests/index-decision-browser.cjs off "$stage_root"
sudo --preserve-env=TN_STAGE_APP,TN_STAGE_DB,TN_STAGE_NET,TN_FIXTURE_PASSWORD,GITHUB_SHA,RUNNER_ENVIRONMENT,GITHUB_REPOSITORY python3 tests/index-decision-release.py "$stage_root" activate
docker exec "$stage_app" php /lab/wp --allow-root --user=1 eval-file /src/tests/index-decision-native.php active
sudo nsenter --target "$stage_app_pid" --net -- env NODE_PATH="$stage_root/pw/node_modules" PLAYWRIGHT_BROWSERS_PATH="$stage_root/browsers" node tests/index-decision-browser.cjs active "$stage_root"
sudo --preserve-env=TN_STAGE_APP,TN_STAGE_DB,TN_STAGE_NET,TN_FIXTURE_PASSWORD,GITHUB_SHA,RUNNER_ENVIRONMENT,GITHUB_REPOSITORY python3 tests/index-decision-release.py "$stage_root" rollback
docker exec "$stage_app" php /lab/wp --allow-root --user=1 eval-file /src/tests/index-decision-native.php restored
sudo nsenter --target "$stage_app_pid" --net -- env NODE_PATH="$stage_root/pw/node_modules" PLAYWRIGHT_BROWSERS_PATH="$stage_root/browsers" node tests/index-decision-browser.cjs restored "$stage_root"
sudo nsenter --target "$stage_app_pid" --net -- env NODE_PATH="$stage_root/pw/node_modules" PLAYWRIGHT_BROWSERS_PATH="$stage_root/browsers" TN_FIXTURE_PASSWORD="$stage_password" node tests/commercial-decision-browser.cjs "$stage_root"
docker exec "$stage_app" php /lab/wp --allow-root --user=1 eval-file /src/tests/commercial-decision-native.php verify-ticket
docker exec "$stage_app" php /lab/wp --allow-root --user=1 eval-file /src/tests/commercial-decision-native.php cleanup-http-state
sudo --preserve-env=TN_STAGE_APP,TN_STAGE_DB,TN_STAGE_NET,TN_FIXTURE_PASSWORD,GITHUB_SHA,RUNNER_ENVIRONMENT,GITHUB_REPOSITORY python3 tests/commercial-decision-release.py "$stage_root" rollback
docker exec "$stage_app" php /lab/wp --allow-root --user=1 eval-file /src/tests/commercial-decision-native.php rollback-accept
docker exec "$stage_app" mkdir -m 700 -p /tmp/tn-editorial-native-decision-v2/evidence
docker exec -e TN_TEST_MANIFEST=/src/content/network-setup-2026-11-01/manifest.json -e TN_TEST_MIGRATION=/src/ops/migrate-growth-content.php -e TN_TEST_DIRECTORY=/tmp/tn-editorial-native-decision-v2/evidence "$stage_app" php /lab/wp --allow-root --user=1 eval-file /src/tests/growth-network-setup-migration-native.php

docker logs "$stage_app" 2>&1 | sed -n '/TN_DECISION_NATIVE /p; /TN_INDEX_NATIVE /p'
cleanup
trap - EXIT
if docker inspect "$stage_app" >/dev/null 2>&1 || docker inspect "$stage_db" >/dev/null 2>&1 || docker inspect "$stage_cli" >/dev/null 2>&1 || docker network inspect "$stage_net" >/dev/null 2>&1 || sudo kill -0 "$stage_relay_pid" >/dev/null 2>&1 || kill -0 "$stage_relay_launcher" >/dev/null 2>&1; then echo TN_DECISION_CLEANUP_FAILED; exit 1; fi
echo TN_DECISION_CLEANUP_VERIFIED
