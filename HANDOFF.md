# TehNet Agent Handoff

## Purpose
Continuation memory for any agent working on TehNet.

## Current state
Product architecture, safe production foundation, WordPress bootstrap and editable Gutenberg page foundation are complete and verified.

Read first:
1. `AGENTS.md`
2. `PROGRESS.md`
3. `docs/superpowers/specs/2026-09-14-tehnet-platform-design.md`
4. `docs/superpowers/plans/2026-09-14-tehnet-foundation.md`
5. `docs/superpowers/plans/2026-09-15-tehnet-wordpress-bootstrap.md`
6. `ROADMAP.md`
7. `TASKS.md`

## Locked architecture
TehNet is a Persian networking platform with Learn + Lab + Services + Shop. Core stack is WordPress + WooCommerce. The custom theme is presentation-only; `tehnet-core` owns business settings/domain logic. Gutenberg/custom blocks are preferred over Elementor.

## Verified foundation
- Production baseline: `ops/PRODUCTION_BASELINE.md`
- Backup/recovery: `ops/BACKUP_RECOVERY.md`
- Existing TehNet binding remains `127.0.0.1:18082`.
- Theme implemented under `site/themes/tehnet/`.
- Core plugin implemented under `site/plugins/tehnet-core/`.
- Theme/plugin files were copied into the existing WordPress volume without changing Docker/Nginx topology.
- Contract tests and PHP lint passed.

## Production state
- `https://tehnet.ir/` is installed and returns HTTP 200.
- Theme `tehnet` and plugin `tehnet-core` are active.
- Binding remains `127.0.0.1:18082`; no TehNet execution changed unrelated container topology.
- Locale: `fa_IR`; static homepage and primary menu are configured.
- Top-level editable pages are seeded: home, learn, lab, services, shop, about, contact.
- Site is intentionally blocked from indexing (`blog_public=0`, meta noindex/nofollow, robots disallow) until SEO launch gates are passed.
- Evidence: `ops/WORDPRESS_BOOTSTRAP_EVIDENCE.md`.
- Fresh recovery point: `/root/tehnet-backups/20260915-000906`.
- Bootstrap credentials remain only in `/root/tehnet-secrets/wp-admin-bootstrap.env` mode 0600; do not copy values into Git or handoff files.

## Exact next task
Integrate `feature/wp-bootstrap`, then create a separate isolated branch/plan for Phase 2 SEO/content architecture. Build the Persian query universe from live SERP evidence before freezing topic hubs or mass-creating pages. Keep indexing disabled and do not change host port `18082`, Nginx routing, or unrelated project containers.

## Important unresolved choices
- Owner should later rotate/confirm the bootstrap WordPress admin email/password from the WordPress account; this is not a launch blocker while access is controlled.
- Rial payment gateway remains intentionally undecided.
- NoPayments integration must be verified against current official provider behavior before coding.
- Current YouTube logo remains the production identity until the owner approves a redesigned preview.

