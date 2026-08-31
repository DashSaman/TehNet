# TehNet Backup / Restore

Backup scope: MariaDB, `wp-content`, `wp-config.php` in protected backup storage only, custom theme/plugin and Nginx vhost.

Before production mutation create `/opt/tehnet/backups/<timestamp>/`, dump DB with `--single-transaction`, archive content/config, copy Nginx vhost and generate SHA-256 sums. Credentials are provided at runtime and never committed.

Restore verification targets an isolated temporary database/path or staging host. Never overwrite production merely to test restoration. Record the restore command, duration, errors and resulting application checks in `ops/LAUNCH_REPORT.md`.
