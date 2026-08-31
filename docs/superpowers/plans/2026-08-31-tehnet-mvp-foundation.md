# TehNet MVP Foundation Implementation Plan

> Implementation is task-by-task, test-first where behavior is involved. Update `PROGRESS.md` and `HANDOFF.md` after verified milestones.

**Goal:** deploy a professional sellable TehNet MVP on `91.107.138.246` using WordPress/WooCommerce and focused custom TehNet code.

**Spec:** `docs/superpowers/specs/2026-08-31-tehnet-platform-design.md`

## Task 1 — Host safety baseline

- Read-only inventory: OS, CPU/RAM/disk, ports, nginx/apache, PHP, MariaDB, Docker, `/var/www`, `/opt`, running services.
- Classify `GREENFIELD` or `COEXIST`.
- Create `/opt/tehnet/backups` mode 0700.
- Snapshot existing relevant config/web roots before mutation and store SHA-256.
- Record evidence in `ops/BASELINE.md`.

**Gate:** no package/service/web-root mutation before this passes.

## Task 2 — Runtime foundation

Files: `ops/install-wordpress.sh`, `ops/nginx/tehnet.conf`, `ops/BACKUP_RESTORE.md`.

- Installer validates required environment secrets before doing anything.
- Install only missing runtime packages.
- Create dedicated DB/user with runtime secrets.
- Install WP-CLI and WordPress under `/var/www/tehnet`.
- Set home/site URL to `https://tehnet.ir`.
- Configure Nginx apex vhost and `www` permanent redirect.
- Detect actual PHP-FPM socket on target rather than hard-coding a version.
- Run shell syntax, `nginx -t`, local Host-header HTTP tests.

## Task 3 — Custom TehNet theme

Files under `site/wp-content/themes/tehnet/`.

- RED: smoke test expects required files + four core URLs.
- GREEN: RTL responsive theme, homepage, dark/light tokens/toggle.
- Add reusable card/section/navigation patterns.
- Add archive/single templates only as needed, keeping WooCommerce compatibility.
- PHP syntax + smoke tests.

## Task 4 — TehNet core plugin

Files under `site/wp-content/plugins/tehnet-core/`.

- `tn_lab` and `tn_service` content types.
- shared topic taxonomy.
- tutorial/lab/course/product/service relationships.
- product sale mode `direct|inquiry`.
- inquiry-mode UI and request endpoint with nonce/validation/rate-control strategy.
- 30-day TehNet Pro access entitlement tied to a designated WooCommerce product and order completion.
- account display for Pro expiry.
- tests around pure entitlement/sale-mode helpers where possible plus WordPress integration smoke tests.

## Task 5 — Component ownership

Create `ops/PLUGIN_MATRIX.md` after current maintenance/license review.

Owners required: Commerce, LMS, Google Login, SEO/meta, caching, ticketing. Avoid feature overlap. Licensed components are installed only from legitimately supplied packages/licenses.

## Task 6 — Search architecture

Create:

- `seo/BUSINESS_SEARCH_BRIEF.md`
- `seo/SERP_MAP.md`
- `seo/QUERY_URL_MAP.md`
- `seo/LAUNCH_CHECKLIST.md`

Map commercial/informational/local intents to one preferred URL each. Observe live Persian SERPs and record date/context. Reject duplicate synonym/location pages.

## Task 7 — YouTube/content inventory

Create `content/YOUTUBE_REVIEW.md` and `content/CONTENT_INVENTORY.md`.

Classify videos `KEEP|REFRESH|DROP`, freshness risks, intended URL and available supporting assets. Publish only sourced/real content. Never invent products/stock/reviews/case studies.

## Task 8 — Production deploy

Only after Task 1 gate.

- deploy runtime safely according to GREENFIELD/COEXIST mode;
- activate theme/core plugin and selected components;
- create approved pages/drafts;
- configure checkout/account/support;
- configure Cloudflare/DNS items available to the owner or document exact required change if the current toolset cannot mutate Cloudflare;
- run live smoke journeys.

## Task 9 — Launch validation

Create `ops/LAUNCH_REPORT.md` and `ops/ROLLBACK.md`.

Validate DNS, HTTPS, www redirect, status, robots, canonical, sitemap, rendering, internal links, schema truthfulness, mobile, analytics, registration/login, Google login, direct checkout, inquiry product, protected downloads, paid video entitlement, course access, Pro access, service request and ticketing.

Test restore into an isolated target. Record `RELEASE=GO` only if all critical gates pass; otherwise `RELEASE=NO-GO` with failures.
