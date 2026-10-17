# Foreign VPS subpath — implemented preview and operating procedure

Current public preview: https://tehnet.ir/software/ . Existing WordPress remains at the root on 127.0.0.1:18082. New archive container `tehnet-software` publishes only 127.0.0.1:18083. Its database mount and root filesystem are read-only; non-root UID/GID 10001; 192 MiB / 0.5 CPU / 64 PID limits. No provider fetcher or worker exists. The separate bridge network does permit physical outbound traffic; physical egress restriction remains a W3/full-W6 gate.

## Applied route and menu boundary

The owner authorized precisely `/software/` plus one menu link. `/etc/nginx/snippets/tehnet-software.conf` is included once in the validated TehNet HTTPS server block; the HTTP redirect block is unchanged. The prefix is preserved on proxy_pass because the FastAPI application mounts `/software` itself:

```nginx
location = /software { return 308 /software/; }
location ^~ /software/ {
    proxy_pass http://127.0.0.1:18083;
    proxy_set_header Host $host;
    proxy_cache off;
    proxy_read_timeout 15s;
}
```

Every asset/form/API URL uses `/software/`; static serving exposes only `static/`. Fonts and JS are local. Research, DB, configuration and backups are outside web root. Responses have no-store/noindex. Unimplemented/private URLs fail closed. There is no accepted login/download surface. Preserve the main site's indexing restriction.

One idempotent WordPress menu addition uses existing PHP APIs, item 189 in primary menu 2. Ownership metadata permits removal of only the newly created item. Existing menu items and their order are checked. No theme, Core plugin, page content or unrelated container is redeployed.

## Copy/paste operator steps and conditions

These commands are for the authorized host operator, after a release is built and tested, not for visitors. Supply an existing, inspected release path and the exact image ID. Never use a floating tag in the actual deployment argument. Read the scripts before executing; they intentionally stop on conflicts.

First install only on a fresh host where `/software/` is absent, WordPress is verified and port 18083 is free:

```bash
bash /opt/tehnet-software/releases/RELEASE/deployment/scripts/deploy-preview.sh   /opt/tehnet-software/releases/RELEASE sha256:EXACT_64_HEX_IMAGE_ID
```

For an existing **schema-compatible read-only preview**, use the update procedure (it does not migrate state):

```bash
bash /opt/tehnet-software/releases/RELEASE/deployment/scripts/update-preview.sh   /opt/tehnet-software/releases/RELEASE sha256:EXACT_64_HEX_IMAGE_ID
```

Both create a fresh private backup of the existing TehNet DB/wp-content/config before runtime mutation, verify archive readability and compare unrelated container fingerprints. Update also snapshots the archive DB via SQLite backup API, retains the old immutable image and automatically recreates only the archive with that image on a failed gate. Do not use this procedure for a schema or writable-service upgrade: design and rehearse its state reconciliation separately.

The first installer checks WordPress page/rewrite ownership, snapshots Nginx/menu, starts only new resources, validates `nginx -t`, reloads gracefully and waits for a ready JSON response. ERR/INT/TERM cleanup preserves new data/snippet in the private backup and removes only newly owned state. Failed startup logs are saved first. Shell integration tests exercise real script flow against sandbox services, including partial startup, cancellation, reload convergence and update rollback.

## Latest verified result and rollback

[DEPLOYMENT](../evidence/DEPLOYMENT.md) records actual image, backup and release paths. Original pages `/`, `/learn/`, `/services/`, `/shop/`, `/contact/` retained HTTP 200, one H1, exact canonical and noindex in origin and independent public TLS tests. All old container IDs/images/ports remained unchanged. This is bounded regression evidence, not a load or complete website audit.

For latest preview-only rollback, retain the data and reuse the same Compose with the previous exact image saved in the private update backup's `previous-image.txt`. Run the same update script with that verified ID to take another fresh backup and revalidate readiness. Do not restore stale WordPress DB snapshots merely to reverse this isolated container update. Removing the entire feature requires the saved original Nginx config, `nginx -t`/graceful reload, owned-item-only removal and stopping only this project, followed by original-route/fingerprint checks. Never delete the sole state copy.

Downloads, Range/resume for accepted artifacts, APT trust, private login/revoke/cache bypass, load and Iranian-client acceptance remain future gates. A public preview does not close them.
