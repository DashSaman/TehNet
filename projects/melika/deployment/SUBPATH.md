# Initial subpath deployment — design, not applied

Target: `https://tehnet.ir/melika/` on the owner's current foreign VPS. Existing WordPress stays at its root and `127.0.0.1:18082`. No existing PHP, content, deployment scripts or host routing were changed by this delivery.

## Prerequisites and stop conditions

W0/W6 must freshly inspect the host via authorized access: container/port/network inventory, Nginx includes, TLS/edge/CDN, disk/RAM and WordPress route conflicts. Repository evidence is historical. Candidate `18083` is not reserved until verified free. Confirm no existing `/melika` page/rewrite/static alias. Record root homepage, services/shop/learn response status/canonical/noindex and non-TehNet fingerprints before deployment. Preserve the repository's `blog_public=0` launch restriction.

Create the existing required TehNet backup under `/root/tehnet-backups/` and a Melika release/data backup separately; keep secrets out of Git. Test archive/DB readability. Do not stop existing services to inspect or install Melika. Production routing is a later narrowly reviewed deployment action.

## Routing proposal

Run only the Melika project with loopback edge access; network/volumes/secrets are separate. Foreign-stage routing may look like the following **unapplied example**, inserted only inside the identified TehNet HTTPS server block after review (not in a new default server). The current repository prohibits ad hoc Nginx changes; this addition requires its scoped deployment gate.

```nginx
# Candidate only: confirm port, route ownership, TLS and current config first.
location = /melika { return 308 /melika/; }
location ^~ /melika/ {
    proxy_pass http://127.0.0.1:18083/;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Prefix /melika;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_cache off;
}
```

Here the URI on `proxy_pass` strips the matched prefix. Configure application root_path/base-path `/melika` explicitly; trust proxy metadata only from the known loopback proxy. Do not assume `X-Forwarded-Prefix` configures the framework by itself. Match slash behavior and redirects at both proxy layers. Use [official Nginx proxy_pass semantics](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass) when implementing; this configuration was not parsed/tested locally because no Nginx runtime was available.

Generate every HTML asset, form action, API URL, login redirect, cookie path, OpenAPI server, download URL and APT base URL with this prefix. Local assets only, no external fonts/CDN login scripts. Preserve safe HTTPS canonical host; do not trust arbitrary Host/forwarded headers. Any redirect return_to must be a validated local path.

Configure only `/melika/` on the CDN to respect no-store/auth bypass and private paths. Do not change the entire site's cache policy. Never expose `research/`, `evidence/`, `.env`, data, SQLite, backups or private storage as static files. No automatic WordPress menu changes in this phase; any link/admin facade is a separate TehNet Core/content change.

## Required staging and live checks

- `/melika` redirects once to HTTPS `/melika/`; public page/assets/API/health/download and their query/pagination paths work without escaping prefix.
- Unknown `/melika/*` is handled by Melika; `/`, `/learn/`, `/services/`, `/shop/`, `/wp-admin/` still reach WordPress with previous canonical/noindex behavior.
- All private GET/HEAD/Range/cache/direct-object tests in SECURITY_PRIVACY pass through the actual edge and origin.
- Local public download checksum/size and Range/resume agree; a remote 302 reveals its destination and no private URL enters logs/caches.
- APT client uses `https://tehnet.ir/melika/ubuntu` explicitly. Do not rewrite existing root `/ubuntu` or external URLs. Keep profile acceptance false without real clean-client evidence.
- `nginx -t` succeeds before a graceful reload; only the TehNet scoped include changes. Record byte-level before/after config diff and unrelated runtime fingerprint. On failure restore previous include, validate and reload; stop only the new Melika project if necessary.

No production SSH access or live host inventory was available in this session. All bullets remain deployment acceptance tasks, not results.
