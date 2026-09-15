# WordPress Bootstrap Evidence — 2026-09-15

## Scope
Finalized only the existing TehNet WordPress stack. No host port, Nginx route, unrelated container, unrelated network, or unrelated volume was intentionally changed.

## Recovery point
Fresh pre-bootstrap backup:
`/root/tehnet-backups/20260915-000906`

Validated artifacts:
- `tehnet.sql.gz`
- `wp-content.tar.gz`
- TehNet Compose file
- private TehNet environment file
- TehNet Nginx site configuration

## Runtime isolation
- WordPress container: `tehnet-wordpress`
- MariaDB container: `tehnet-db`
- Redis container: `tehnet-redis`
- Host binding remained: `127.0.0.1:18082->80/tcp`
- Bootstrap and seed scripts compare unrelated container topology before/after execution.
- Both executions reported `UNRELATED_RUNTIME_TOPOLOGY=UNCHANGED`.
## Verified WordPress state
- Canonical home/site URL: `https://tehnet.ir`
- Locale: `fa_IR`
- Search indexing: disabled (`blog_public=0`)
- Static front page enabled; homepage ID: `5`
- Active theme: `tehnet`
- Active core plugin: `tehnet-core`
- Primary menu ID: `2`
- Bootstrap admin user exists.
- Bootstrap credential file exists only at `/root/tehnet-secrets/wp-admin-bootstrap.env` with mode `0600`; credential values are not stored in Git or this evidence file.

## Seeded editable pages
- `home` → ID 5
- `learn` → ID 6
- `lab` → ID 7
- `services` → ID 8
- `shop` → ID 9
- `about` → ID 10
- `contact` → ID 11

All tested public routes returned HTTP 200. `/wp-admin/install.php` is no longer the homepage redirect.

## Crawl safety
Homepage contains `meta robots: noindex, nofollow` and `/robots.txt` contains `Disallow: /`. This remains intentional until SEO/content launch gates are passed.
