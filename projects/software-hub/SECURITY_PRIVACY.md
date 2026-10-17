# Public catalog and password-protected VPN section

Status: required design and acceptance checklist; no live authentication was implemented in this consolidation. Existing public research references are not secret; private runtime configuration, subscriber data, credentials and access links are.

## Boundary that must hold

Ordinary software, education and approved mirror metadata are public. VPN listings, their navigation/category names where sensitive, private search results/counts, detail records, source maps, downloads and backups are restricted. An unclassified import defaults restricted, then a human/content owner reviews classification. Never ship private content in HTML, JSON hydration, static JS, RSS, sitemap, public source maps, public Git, frontend build artifacts or public object buckets.

Use an audited server-side password/session implementation, salted password hashes (no reversible or plaintext storage), local administrator provisioning, rate limits and safe login failure messages. Credentials travel only over valid TLS. Secure/HttpOnly/SameSite session cookies scoped to `/software`, CSRF defenses on login/logout/admin changes, session rotation, expiry, revocation and lockout recovery are required. Avoid new crypto/auth protocol design. No third-party login or license server is essential for local outage access.

Private responses and denial/login responses use `Cache-Control: private, no-store`; authenticated requests bypass edge/CDN/shared caches. Set noindex for private paths but recognize robots.txt and noindex are not authorization. Public HTML and APIs must not reveal restricted counts through pagination or errors. Do not leak IDs in analytics/referrers; redact Authorization/Cookie/passwords/temporary URL queries and client identifiers in public logs. Keep detailed logs locally under retention/ACL rules.

Every API and delivery method enforces access on the server: direct hash/path access, GET/HEAD, Range/If-Range, conditional 304, encoded traversal, case/trailing-slash alternatives and storage redirects. Local Nginx objects use an `internal` location outside web root; private data has no public alias. Authentication occurs before X-Accel-Redirect. Public third-party URLs cannot satisfy restricted delivery. Short-lived signed tokens alone are bearer access; do not log them or confuse an unrevocable public URL with password protection.

## Data and backup policy

Never commit production VPN client lists, subscriber database, connection profiles, keys, bot tokens, OTP/session files, private download URLs, passwords or real identifying logs. This public Git repository is **not** a confidential vault, even if the future website has a login page. Store private backup data encrypted, with keys provisioned separately, restricted destination permissions and a tested restore. Record only sanitized report metadata/hashes publicly; review hash/filename sensitivity before publishing.

Migration must carry access policy and password hashes securely, rotate/invalidate sessions at cutover unless keys are securely transferred, and test logout/old-cookie invalidation. Private section remains disabled on a new target until its authorization and direct-object tests pass. Do not expose it temporarily to meet a migration timer.

## W2 acceptance matrix (all unexecuted for the real app)

| Input / condition | Required behavior |
|---|---|
| Anonymous public browser | Ordinary catalog available; no VPN rows/links/counts in response source or APIs |
| Anonymous direct known private hash vs random hash | Consistent denial; no payload or existence signal |
| Valid password then logout / expired or revoked session | Authorized view works; later GET/HEAD/Range/conditional requests denied |
| Public search/export/feed/sitemap/OpenAPI | No restricted records, URLs, examples or counts |
| CDN first authorized then anonymous request | No cached restricted bytes delivered |
| Internal file URL, symlink, encoded traversal, alternate path | Rejected by app and edge; no object-store bypass |
| Login burst / cross-origin state change | Bounded rate and CSRF rejection with sanitized logs |
| Restore on fresh host and session-policy change | Private section fails closed until checks pass; old sessions obey chosen invalidation policy |

W2 owns this matrix and records actual commands, output, fixtures and limitations in its task log. A test against a mock login page or filesystem fixture is not evidence for the future deployed app.

## Integrity and fetch policy carried forward

Read the immutable research security/API contract: approved sources only, validated and pinned DNS/TLS, no arbitrary fetch proxy, quarantine mismatches, signed APT metadata with freshness and by-hash retention, license/permission records, and no foreign fallback in DOMESTIC_ONLY. A VPN running domestically does not create an international route during complete upstream disconnection. Report local use and external connectivity separately.
