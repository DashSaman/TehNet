# TehNet Foundation Deployment Evidence — 2026-09-14

## Scope
Only TehNet theme/plugin files were deployed. No Docker Compose file, Nginx config, host port, database schema, or unrelated project was modified.

## Before deployment
- TehNet WordPress: `tehnet-wordpress`
- Binding: `127.0.0.1:18082 -> 80/tcp`
- DB: `tehnet-db` (`mariadb:11.4`)
- Redis: `tehnet-redis` (`redis:7.4-alpine`)
- Backup: `/root/tehnet-backups/20260914-183021`

## Deployment
- Copied `site/themes/tehnet/` into `/var/www/html/wp-content/themes/tehnet/`.
- Copied `site/plugins/tehnet-core/` into `/var/www/html/wp-content/plugins/tehnet-core/`.
- Applied `www-data:www-data` ownership only to those two deployed paths.
- Ran PHP lint inside the existing `tehnet-wordpress` container.

## Verification
- `TEHNET_FILE_DEPLOY=PASSED`
- `PORT_BINDING=127.0.0.1:18082`
- `UNRELATED_RUNTIME_TOPOLOGY=UNCHANGED`
- Deployed theme/plugin files confirmed present in container.
- Public site still returns HTTP 302 to `/wp-admin/install.php`; WordPress setup remains intentionally unfinished.

## Concurrent host activity
A container named `tunnelpannel-e2e` appeared from another workflow during this work. It was not created, restarted, stopped, inspected for mutation, or otherwise altered by the TehNet deployment.
