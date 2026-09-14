# TehNet Agent Handoff

## Purpose
Continuation memory for any agent working on TehNet.

## Current state
Discovery is complete, the product direction is approved, and the first implementation foundation has been completed on `feature/tehnet-foundation`.

Read first:
1. `AGENTS.md`
2. `PROGRESS.md`
3. `docs/superpowers/specs/2026-09-14-tehnet-platform-design.md`
4. `docs/superpowers/plans/2026-09-14-tehnet-foundation.md`
5. `ROADMAP.md`
6. `TASKS.md`

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
`https://tehnet.ir/` still redirects to the WordPress installer. Theme/plugin are deployed as files but not activated because WordPress installation has not been finalized.

A separate `tunnelpannel-e2e` container appeared from another workflow while this task was in progress. TehNet work did not create, restart, stop, or modify it.

## Exact next task
After the foundation branch is integrated, create a separate implementation plan for safe WordPress bootstrap/activation and the editable Gutenberg page foundation. Do not change host port `18082`, existing Nginx routing, or unrelated project containers.

## Important unresolved choices
- WordPress admin email/credential ownership still needs a deliberate bootstrap decision before final install.
- Rial payment gateway remains intentionally undecided.
- NoPayments integration must be verified against current official provider behavior before coding.
- Current YouTube logo remains the production identity until the owner approves a redesigned preview.
