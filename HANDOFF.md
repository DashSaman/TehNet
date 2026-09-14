# TehNet Agent Handoff

## Purpose
Continuation memory for any agent working on TehNet.

## Current state
Discovery is complete and the product direction is documented. Do not restart product discovery unless the owner changes a requirement.

Read first:
1. `AGENTS.md`
2. `PROGRESS.md`
3. `docs/superpowers/specs/2026-09-14-tehnet-platform-design.md`
4. `ROADMAP.md`
5. `TASKS.md`

## Locked architecture
TehNet is a Persian networking platform with four equal journeys:
- Learn — free tutorials in phase 1
- Lab — scripts/configs/files
- Services — Tehran on-site + nationwide remote support
- Shop — digital products plus physical networking equipment

Core stack: WordPress + WooCommerce. Use a custom theme for presentation and TehNet Core plugin for business logic. Gutenberg/custom blocks are preferred over Elementor. Routine business/content changes must be manageable through WordPress admin.

## SEO/content direction
Use `DashSaman/-SEO` as the evidence framework. Build topic hubs and intent-specific tutorials; do not auto-create thin pages for every YouTube video. Connect YouTube, site content, Lab assets, services and products through contextual internal links.

## Production observation
Server target: `91.107.138.246`.
Observed TehNet stack: WordPress + MariaDB + Redis in Docker. The public domain currently redirects to the WordPress installer, so the actual site build has not begun. Default WordPress themes/plugins are essentially untouched.

## Exact next task
Do not implement the site yet unless the owner approves the written master specification. After approval:
1. document production baseline and backup/recovery evidence under `ops/`;
2. create task-sized implementation plans;
3. begin theme/plugin foundation on a feature branch with tests and verification.

## Important unresolved implementation choices
- Rial payment gateway provider is intentionally undecided.
- NoPayments provider behavior/API/webhooks must be verified against current official documentation before coding.
- Final logo remains current YouTube identity unless the owner approves a previewed redesign.
