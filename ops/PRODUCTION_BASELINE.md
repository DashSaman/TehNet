# TehNet Production Baseline

Captured: 2026-09-14

## Isolation rule
TehNet is an existing Docker Compose project. Foundation work must reuse the current stack and must not change host port bindings or restart unrelated projects.

## TehNet runtime
- Compose project: `tehnet`
- Compose file: `/opt/tehnet/compose.yaml`
- WordPress container: `tehnet-wordpress`
- WordPress image: `wordpress:php8.3-apache`
- Published binding: `127.0.0.1:18082 -> 80/tcp`
- Database container: `tehnet-db`
- Database image: `mariadb:11.4`
- Redis container: `tehnet-redis`
- Redis image: `redis:7.4-alpine`
- Docker network: `tehnet-internal`
- Volumes: `tehnet_tehnet-wp-data`, `tehnet_tehnet-db-data`, `tehnet_tehnet-redis-data`

## Reverse proxy
- Nginx site: `/etc/nginx/sites-enabled/tehnet.ir.conf`
- Public canonical host: `https://tehnet.ir`
- Nginx currently proxies only to the existing TehNet localhost binding.

## Reserved bindings observed on the host
- NetAuto web: `127.0.0.1:18080`
- MyTel WordPress: `127.0.0.1:18081`
- TehNet WordPress: `127.0.0.1:18082`
- Uptime Kuma: `127.0.0.1:3001`

Do not reuse or modify these bindings during TehNet foundation work.
