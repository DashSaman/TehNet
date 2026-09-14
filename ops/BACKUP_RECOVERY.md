# TehNet Backup and Recovery

## Production backup policy
Before any production deployment, create a timestamped backup under `/root/tehnet-backups/`. Backup bytes and secrets stay on the server and are never committed to Git.

Baseline backup created during foundation work:
`/root/tehnet-backups/20260914-183021`

It contains:
- compressed MariaDB dump (`tehnet.sql.gz`)
- compressed WordPress `wp-content` (`wp-content.tar.gz`)
- `/opt/tehnet/compose.yaml`
- private `/opt/tehnet/.env`
- TehNet Nginx site configuration

## Validation
Run before relying on a backup:

```bash
gzip -t /root/tehnet-backups/<timestamp>/tehnet.sql.gz
tar -tzf /root/tehnet-backups/<timestamp>/wp-content.tar.gz >/dev/null
```

## Recovery outline
1. Stop only the `tehnet` Compose project if restoration is actually required.
2. Restore the saved Compose/environment files to `/opt/tehnet/` with restrictive permissions.
3. Restore `wp-content` into the TehNet WordPress volume only.
4. Start only the TehNet DB and import the saved SQL dump.
5. Start the TehNet WordPress/Redis services.
6. Validate `127.0.0.1:18082`, Nginx, public HTTPS, and TehNet container health.
7. Confirm unrelated container names and published ports are unchanged.

Do not use `docker system prune --volumes` or broad container removal as a TehNet recovery step.
