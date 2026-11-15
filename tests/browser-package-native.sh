#!/usr/bin/env bash
# Browser-package isolated fixture + real browser journeys on the GitHub-hosted runner.
# Pattern mirror of tests/commercial-decision-native.sh (the accepted cloud-runner pattern).
set -euo pipefail
test "${RUNNER_ENVIRONMENT:-}" = github-hosted
test "${GITHUB_REPOSITORY:-}" = DashSaman/TehNet
stage_root="$(mktemp -d /tmp/tn-browser-native-XXXXXX)"
stage_net="tn-browser-$GITHUB_RUN_ID"
stage_db="tn-browser-db-$GITHUB_RUN_ID"
stage_cli="tn-browser-cli-$GITHUB_RUN_ID"
stage_app="tn-browser-app-$GITHUB_RUN_ID"
mkdir -p "$stage_root/web"
cleanup(){ docker rm -f -v "$stage_app" "$stage_db" "$stage_cli" >/dev/null 2>&1 || true; docker network rm "$stage_net" >/dev/null 2>&1 || true; case "$stage_root" in /tmp/tn-browser-native-*) sudo rm -rf -- "$stage_root";; esac; }
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
docker run -d --name "$stage_app" --network "$stage_net" -p 127.0.0.1:18085:80 -e TN_FIXTURE_PASSWORD="$stage_password" -v "$PWD:/src:ro" -v "$stage_root:/lab" -v "$stage_root/web:/var/www/html" --entrypoint bash wordpress:7.1.4-php8.3-apache -eu -c '
for fixture_php in /src/tests/browser-package-native.php /src/ops/migrate-growth-content.php; do php -l "$fixture_php"; done
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
define("WP_HOME","http://localhost:18085");
define("WP_SITEURL","http://localhost:18085");
define("WP_ENVIRONMENT_TYPE","staging");
define("TN_RECAPTCHA_ENABLED",true);
define("TN_RECAPTCHA_SITE_KEY","SIMULATED-SITE-KEY");
define("TN_RECAPTCHA_SECRET_KEY","SIMULATED-SECRET-KEY");
PHP
php /lab/wp --allow-root core install --url=http://localhost:18085 --title="Synthetic fixture" --admin_user=fixture --admin_password="$TN_FIXTURE_PASSWORD" --admin_email=fixture@example.invalid --skip-email
php /lab/wp --allow-root option update blog_public 0
php /lab/wp --allow-root plugin activate woocommerce tehnet-core tehnet-store
php /lab/wp --allow-root theme activate tehnet
php /lab/wp --allow-root --user=1 eval-file /src/tests/browser-package-native.php seed
php /lab/wp --allow-root rewrite flush --hard
touch /lab/READY
exec apache2-foreground
'
for n in {1..120}; do test -f "$stage_root/READY" && break; if test "$(docker inspect -f '{{.State.Running}}' "$stage_app")" != true; then docker logs "$stage_app"; exit 1; fi; sleep 1; done
test -f "$stage_root/READY"
export TN_STAGE_APP="$stage_app" TN_STAGE_DB="$stage_db" TN_STAGE_NET="$stage_net" TN_FIXTURE_PASSWORD="$stage_password"
stage_app_pid="$(docker inspect -f '{{.State.Pid}}' "$stage_app")"
sudo nsenter --target "$stage_app_pid" --net -- node -e 'const fs=require("node:fs"),net=require("node:net");net.createServer(c=>{const u=net.connect(80,"127.0.0.1");c.pipe(u);u.pipe(c);c.on("error",()=>u.destroy());u.on("error",()=>c.destroy());}).listen(18085,"127.0.0.1");fs.writeFileSync(process.argv[1]+"/relay.pid",String(process.pid),{mode:0o600});' "$stage_root" >"$stage_root/relay.log" 2>&1 &
sleep 1
# Bootstrap the request contexts before the immutable DB baseline.
# Wait for Apache to start (via the port mapping) — set +e for the wait phase
set +e
up=false
for n in $(seq 1 60); do
  code="$(curl --silent --max-time 5 --output /dev/null --write-out '%{http_code}' http://localhost:18085/ 2>/dev/null)"
  if test "$code" = "200"; then up=true; echo "APACHE_UP after ${n} attempts"; break; fi
  sleep 3
done
set -e
if test "$up" != "true"; then
  # Bounded diagnostic per MANAGER_REVIEW: curl from three layers, record distinctly
  echo "=== DIAGNOSTIC PROBE ==="
  # (a) inside container: direct Apache port 80
  app_code="$(docker exec "$stage_app" curl --silent --max-time 5 --output /dev/null --write-out '%{http_code}' http://127.0.0.1:80/ 2>&1)" || app_code="curl_exit_$?"
  echo "PROBE_A_container_apache80: $app_code"
  # (b) from the host: published port 18085 with verbose status
  host_code="$(curl --silent --max-time 5 --output /dev/null --write-out '%{http_code}' http://127.0.0.1:18085/ 2>&1)" || host_code="curl_exit_$?"
  echo "PROBE_B_host_published18085: $host_code"
  # (c) docker port mapping check
  port_map="$(docker port "$stage_app" 2>/dev/null || echo 'no-mapping')"
  echo "PROBE_C_docker_port_mapping: $port_map"
  # (d) container process check: is Apache actually running?
  apache_pid="$(docker exec "$stage_app" pgrep -c apache2 2>/dev/null || echo 0)"
  echo "PROBE_D_apache_process_count: $apache_pid"
  # (e) container port 80 listener
  listener="$(docker exec "$stage_app" sh -c 'ss -tlnp 2>/dev/null | grep ":80 " || echo "no-listener"')"
  echo "PROBE_E_container_port80_listener: $listener"
  echo "=== END DIAGNOSTIC ==="
  docker logs "$stage_app" 2>&1 | tail -20
  exit 1
fi
for stage_path in / /services/ /b2b/ /support/ /shop/ /wp-admin/admin-post.php; do
 stage_http="$(curl --silent --show-error --max-time 30 --output /dev/null --write-out '%{http_code}' "http://localhost:18085$stage_path")"
 case "$stage_http" in 200|301|302|400) :;; *) echo "TN_FIXTURE_BOOTSTRAP_FAILED status=$stage_http"; exit 1;; esac
done
# The real browser journeys (Cases 1-4) against the isolated fixture.
export TN_BROWSER_BASE="http://localhost:18085"
NODE_PATH="$stage_root/pw/node_modules" PLAYWRIGHT_BROWSERS_PATH="$stage_root/browsers" node tests/browser-package.cjs
echo "TN_BROWSER_PACKAGE_NATIVE_DONE"
