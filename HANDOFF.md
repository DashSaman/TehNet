# TehNet Agent Handoff

## Current state
Foundation, WordPress bootstrap, SEO architecture, YouTube mapping and the first MikroTik Learn hub are implemented and verified in production. The site intentionally remains non-indexable.

## Read first
1. `AGENTS.md`
2. `PROGRESS.md`
3. `docs/superpowers/specs/2026-09-14-tehnet-platform-design.md`
4. `docs/superpowers/plans/2026-09-15-tehnet-seo-architecture.md`
5. `seo/QUERY_UNIVERSE_FA.md`
6. `seo/SERP_INTENT_MAP_FA.md`
7. `seo/INFORMATION_ARCHITECTURE_FA.md`
8. `seo/TECHNICAL_SEO_BASELINE.md`
9. `seo/YOUTUBE_INVENTORY_FA.md`
10. `seo/YOUTUBE_CONTENT_MAP_FA.md`
11. `docs/superpowers/plans/2026-09-15-tehnet-youtube-content-mapping.md`
12. `TASKS.md`

## Verified production
- Domain: `https://tehnet.ir`
- TehNet host binding: `127.0.0.1:18082`
- Active theme/plugin: `tehnet` / `tehnet-core`
- Main top-level routes return HTTP 200, one H1 each, correct canonicals and `noindex,nofollow`.
- `blog_public=0`; do not enable indexing yet.
- `/wp-sitemap.xml` currently returns 404 while non-public.
- Fresh recovery point: `/root/tehnet-backups/20260915-012653`.
- Non-TehNet runtime fingerprint remained unchanged across SEO deployment.
- `/learn/mikrotik/` is live and returned HTTP 200 with exactly one H1, correct canonical and `noindex,nofollow`.
- Current public YouTube inventory contains 33 mapped videos; no thin per-video site pages were created.

## SEO architecture locked
- `/learn/`, `/lab/`, `/services/`, `/shop/` are separate journeys.
- First-priority Learn owner: `/learn/mikrotik/`.
- Service owners include `/services/network-tehran/`, `/services/network-support-tehran/`, `/services/network-setup-tehran/`, `/services/mikrotik-tehran/`, `/services/remote-support/`.
- Shop intent belongs to category/product pages, not tutorials.
- No auto-generated thin pages per YouTube video and no fake district/city doorway pages.

## Important implementation facts
- `tn_service` and `tn_lab` archives are disabled to avoid collisions with `/services/` and `/lab/` pages; single rewrites remain nested beneath those slugs.
- `page.php` owns the H1 for normal pages; `front-page.php` leaves the editorial homepage H1 to page content.
- WP-CLI used here has no `wp menu get`; Persian menu discovery uses the tested `ops/lib/wp-menu-id.awk` parser.
- Current `robots.txt` only disallows `/wp-admin/`; actual prelaunch index blocking is the rendered meta robots plus `blog_public=0`.

## Exact next task
After merging this branch into `main`, create a new isolated branch/plan for **Services owner pages**. Implement the already-approved commercial owners for Tehran networking/MikroTik and nationwide Remote Support with truthful service-area claims, strong editable Gutenberg content, and no fake district/city pages. Keep all production indexing disabled.

## Safety
Do not change port `18082`, Nginx routing, Docker project topology or unrelated services. Before each production content/code deployment, capture a fresh TehNet backup and compare the non-TehNet runtime fingerprint before/after.

## Still unresolved
- Rial gateway provider.
- NoPayments official API/webhook implementation details.
- Final optional logo redesign (must be previewed before replacement).
- Search Console connection/measurement and final launch-indexing approval.
