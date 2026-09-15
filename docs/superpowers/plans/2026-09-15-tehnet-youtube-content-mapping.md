# TehNet YouTube Content Mapping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans task-by-task. Track steps with checkbox syntax.

**Goal:** Inventory the full public TehNet YouTube channel, map each video to the approved SEO architecture, and publish the first substantial `/learn/mikrotik/` owner page without enabling indexing.

**Architecture:** YouTube is evidence/distribution, while the website owns canonical long-form topic pages. Videos do not automatically create URLs. The first website owner is the MikroTik Learn hub because current SERPs and TehNet's video library both support it.

**Tech Stack:** WordPress/Gutenberg, TehNet theme/core, YouTube public channel data, Bash contracts, WP-CLI.

**Spec:** `docs/superpowers/specs/2026-09-14-tehnet-platform-design.md`

## Global Constraints
- Persian/Iran first.
- Keep `blog_public=0` and `noindex,nofollow` throughout this plan.
- Do not create one thin page per video.
- Preserve `127.0.0.1:18082`; no unrelated Docker/Nginx changes.
- Do not invent upload dates or video content not supported by title/metadata.
- Deprecated videos remain marked deprecated rather than promoted.
- Off-topic videos may remain YouTube-only with no website owner.

---
## File Structure
- `tests/youtube-content-contract.sh` — inventory/mapping quality contract.
- `seo/YOUTUBE_INVENTORY_FA.md` — all current public videos and stable IDs.
- `seo/YOUTUBE_CONTENT_MAP_FA.md` — cluster, disposition and owner URL.
- `tests/learn-mikrotik-contract.sh` — first Learn owner page contract.
- `content/pages/learn-mikrotik.html` — substantial Gutenberg body for the MikroTik hub.
- `ops/wp-seed-foundation.sh` — idempotent child-page seed under `/learn/`.
- Coordination files — progress/handoff/backlog after live verification.

### Task 1: Public YouTube Inventory

**Files:** Create `tests/youtube-content-contract.sh`, `seo/YOUTUBE_INVENTORY_FA.md`.

**Interfaces:** Consumes public channel metadata; produces stable video IDs/titles consumed by mapping and page content.

- [ ] Write a failing contract requiring the current channel ID, observation date, explicit inventory count, unique 11-character video IDs and at least 33 entries.
- [ ] Run it and confirm RED because the inventory doc is absent.
- [ ] Generate the inventory from the public channel/videos listing; record only observed title, ID, URL, duration/view count when available, and no fabricated dates.
- [ ] Run the contract to GREEN and commit.

### Task 2: Video → Owner URL Mapping

**Files:** Create `seo/YOUTUBE_CONTENT_MAP_FA.md`; extend `tests/youtube-content-contract.sh`.

**Interfaces:** Consumes the full inventory plus `seo/INFORMATION_ARCHITECTURE_FA.md`; produces canonical owner decisions used by site content.

- [ ] Extend the contract first to require `Cluster`, `Disposition`, `Owner URL` and coverage of every inventory ID.
- [ ] Verify RED.
- [ ] Map MikroTik/MTCNA/VPN videos to existing or future approved owners; map Linux/monitoring to future hubs; mark off-topic iPhone items as `YOUTUBE-ONLY`; mark superseded material as `DEPRECATED`.
- [ ] Ensure no mapping invents a page outside the approved architecture without a documented `NOT-YET` decision.
- [ ] Run GREEN and commit.

### Task 3: Publish the First Learn Owner

**Files:** Create `tests/learn-mikrotik-contract.sh`, `content/pages/learn-mikrotik.html`; modify `ops/wp-seed-foundation.sh`.

**Interfaces:** Consumes Task 2 mapping; produces editable WordPress child page `/learn/mikrotik/` under the existing Learn parent.

- [ ] Write a failing contract requiring no editorial H1, original Persian sections, at least three verified TehNet YouTube video URLs, and idempotent child-page seeding beneath `LEARN_ID`.
- [ ] Verify RED.
- [ ] Build a substantial Persian MikroTik hub: orientation, RouterOS path, MTCNA path, VPN/security learning path, lab/practice guidance and selected video embeds/links.
- [ ] Keep the body free of unsupported ranking/marketing claims and do not link to unpublished owner pages.
- [ ] Seed/update the page with `post_parent=$LEARN_ID` so the canonical path is `/learn/mikrotik/`.
- [ ] Run contract, shell syntax and relevant repository tests to GREEN; commit.

### Task 4: Safe Production Verification and Coordination

**Files:** Modify `PROGRESS.md`, `HANDOFF.md`, `TASKS.md`; update this plan with completion evidence.

**Interfaces:** Consumes Tasks 1–3; produces live evidence and exact next-step state.

- [ ] Capture a fresh TehNet recovery point and pre-change non-TehNet runtime fingerprint.
- [ ] Run the idempotent seed only; do not restart TehNet or unrelated containers.
- [ ] Flush WordPress rewrite rules using the existing ephemeral WP-CLI pattern.
- [ ] Verify `/learn/mikrotik/` returns 200, exactly one H1, correct canonical and `noindex,nofollow`.
- [ ] Re-verify the existing primary routes and `blog_public=0`.
- [ ] Confirm non-TehNet runtime fingerprint is byte-for-byte unchanged and port remains `127.0.0.1:18082`.
- [ ] Run all repository contracts, shell syntax checks and PHP lint.
- [ ] Update coordination files with verified facts only, close plan checkboxes and commit.

## Completion Boundary
This plan does not create individual MTCNA lesson pages, VPN tutorial pages, Services landing pages, WooCommerce products, VideoObject schema or enable indexing. Those require separate plans after this owner-page foundation is verified.

## Self-Review Gate
Every inventoried ID must appear exactly once in the mapping; website URLs must be justified by approved intent; the MikroTik hub must add original value beyond video titles; production remains noindex and isolated from unrelated services.
