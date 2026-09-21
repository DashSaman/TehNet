# TehNet MTCNA Owner Evidence — 2026-09-21

## Scope
Published the approved `/learn/mikrotik/mtcna/` learning-path owner as one substantial page rather than thin per-video pages.

## Intent decision
Fresh Persian SERP review continued to show MTCNA as a distinct course/learning-path intent. Generic VPN remained fragmented across protocol/use-case results, while Linux results clustered around narrower Docker/NGINX/server topics; those generic hubs remain NOT-YET.

## Recovery point
`/root/tehnet-backups/20260921-011812`

## Production verification
- Idempotent WordPress seed passed and unrelated runtime topology stayed unchanged.
- Public and direct-origin `/learn/mikrotik/mtcna/` returned HTTP 200.
- Exactly one H1 and correct canonical.
- `noindex,nofollow` remains rendered and `blog_public=0`.
- All seven mapped MTCNA episodes plus the GNS3 lab video are present.
- Required internal links and the MikroTik-hub backlink are present.
- TehNet binding remains `127.0.0.1:18082`; Nginx config test passed.
