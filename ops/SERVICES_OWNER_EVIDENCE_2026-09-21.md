# TehNet Services Owner Deployment Evidence — 2026-09-21

## Scope
Published the five approved commercial service owner pages beneath `/services/` without changing Docker/Nginx topology or enabling search indexing.

## Recovery points
- Pre-seed recovery point: `/root/tehnet-backups/20260921-005938`
- Post-seed / pre-plugin-fix recovery point: `/root/tehnet-backups/20260921-010347`
- Both backups contain validated MariaDB dump + `wp-content`, TehNet compose/env and Nginx site config.

## Production issue found during deployment
The five WordPress child pages were successfully created under the Services page, but initially returned HTTP 404.

Root-cause evidence:
- WordPress stored all five pages as published children of Services page ID 8.
- WP-CLI generated the intended `/services/<owner>/` permalinks.
- Direct origin requests and Cloudflare requests both returned the same 404, excluding edge cache/DNS as the cause.
- WordPress rewrite rules mapped `/services/<slug>/` to the empty `tn_service` CPT before hierarchical page resolution.
- There were zero `tn_service` posts in production.

Resolution:
- Disabled the unused `tn_service` pretty rewrite so ordinary page owners exclusively own `/services/*`.
- Added a regression contract preventing that rewrite collision from returning.
- Updated the older SEO contract that incorrectly required the conflicting rewrite.

## Deployment verification
- `TEHNET_FILE_DEPLOY=PASSED`
- `PORT_BINDING=127.0.0.1:18082`
- `UNRELATED_RUNTIME_TOPOLOGY=UNCHANGED`
- `BLOG_PUBLIC=0`
- Nginx configuration test passed.

## Live owner checks
Each route returned HTTP 200 both directly from the origin and publicly through Cloudflare, with exactly one H1, the expected canonical URL, and `noindex, nofollow`:
- `/services/network-tehran/`
- `/services/network-support-tehran/`
- `/services/network-setup-tehran/`
- `/services/mikrotik-tehran/`
- `/services/remote-support/`

The `/services/` hub also returned HTTP 200, exactly one H1, and linked to all five owners.

## Safety result
No unrelated container/image/port topology changed during the content seed or plugin file deployment. Search indexing remains disabled pending the explicit launch gate.
