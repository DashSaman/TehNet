# TehNet Technical SEO Baseline

**Verification date:** 2026-09-15  
**Environment:** production `https://tehnet.ir` behind existing Nginx/Cloudflare path  
**Host binding preserved:** `127.0.0.1:18082`

## Recovery point
Fresh pre-change backup: `/root/tehnet-backups/20260915-011313`

Validated server-side only:
- MariaDB dump gzip integrity passed.
- WordPress `wp-content` tar archive integrity passed.
- Compose/environment/Nginx TehNet configuration captured where applicable.
- Backup secrets/bytes are not committed to Git.

## Route verification
After deploying only the TehNet theme/core files, reseeding existing pages idempotently and flushing rewrite rules:

| Route | HTTP | H1 count | Canonical | Robots |
|---|---:|---:|---|---|
| `/` | 200 | 1 | `https://tehnet.ir/` | `noindex, nofollow` |
| `/learn/` | 200 | 1 | `https://tehnet.ir/learn/` | `noindex, nofollow` |
| `/lab/` | 200 | 1 | `https://tehnet.ir/lab/` | `noindex, nofollow` |
| `/services/` | 200 | 1 | `https://tehnet.ir/services/` | `noindex, nofollow` |
| `/shop/` | 200 | 1 | `https://tehnet.ir/shop/` | `noindex, nofollow` |
| `/about/` | 200 | 1 | `https://tehnet.ir/about/` | `noindex, nofollow` |
| `/contact/` | 200 | 1 | `https://tehnet.ir/contact/` | `noindex, nofollow` |

## Current indexing state
- WordPress option `blog_public=0` is verified.
- Rendered primary routes include `noindex, nofollow`; indexing must remain disabled until launch approval.
- Current `robots.txt` does **not** globally disallow the site; measured output only disallows `/wp-admin/` and allows `admin-ajax.php`.
- WordPress core `/wp-sitemap.xml` currently returns HTTP 404 while the site is non-public. This is recorded as expected current behavior, not a launch PASS.

## Collision/H1 fixes
- `tn_service` and `tn_lab` no longer expose archives that compete with the real `/services/` and `/lab/` pages.
- Single CPT rewrites remain under `/services/{slug}/` and `/lab/{slug}/`.
- Normal pages use `page.php`, where the WordPress page title is the single H1.
- `front-page.php` does not inject another H1; the homepage body owns its editorial H1.
- Seed content for normal pages starts below H1 level.

## Runtime isolation evidence
Before and after fingerprint SHA for every non-TehNet container/image/port entry:
`154ffc0ec067945dac95ef75b3725f5b2a0acb674396b90ac34009bb13e91096`

The fingerprints matched exactly. No unrelated runtime topology changed. No TehNet host port, Nginx route or container restart was used for this SEO fix.

## Launch gates still open
Indexing must not be enabled merely because these checks pass. Remaining gates include content readiness, Search Console/measurement, structured-data decisions, performance/security/mobile review, sitemap/index validation after public indexing is intentionally enabled, and final crawl/retest.
