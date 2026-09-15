# TehNet SEO & Content Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an evidence-backed Persian SEO architecture for TehNet, fix current technical SEO blockers, and leave production safely noindex until launch readiness.

**Architecture:** Query and page decisions are driven by current Persian SERP intent, business fit and the `DashSaman/-SEO` framework. Learn, Lab, Services and Shop remain distinct user journeys. Service pages target real Tehran/on-site and nationwide remote capabilities; educational content uses topic hubs and practical tutorials; shop intent uses category/product pages rather than articles.

**Tech Stack:** WordPress 7.x, TehNet custom theme/core plugin, Gutenberg, public Persian SERP research, `DashSaman/-SEO`, later Google Search Console.

**Spec:** `docs/superpowers/specs/2026-09-14-tehnet-platform-design.md`

## Global Constraints
- Primary market/language: Iran / Persian.
- No guaranteed Page 1/Top 10 claims.
- Do not fabricate Iran keyword volume or difficulty.
- Ahrefs Keyword Explorer API currently does not support country `IR`; record this limitation explicitly.
- Use dated SERP observations and classify intent/page type.
- No fake locations or scaled city doorway pages.
- Keep `blog_public=0` / meta noindex until launch gate approval.
- Do not change TehNet host port `127.0.0.1:18082` or unrelated runtime topology.
- One coherent intent cluster should have one canonical owner URL.

---
## File Structure
- `tests/seo-architecture-contract.sh` — evidence/architecture quality contract.
- `tests/seo-technical-contract.sh` — regression contract for current technical blockers.
- `seo/RESEARCH_LIMITATIONS.md` — measured source limitations and evidence policy.
- `seo/QUERY_UNIVERSE_FA.md` — prioritized Persian query clusters and decisions.
- `seo/SERP_INTENT_MAP_FA.md` — dated observations, competitors, dominant page types.
- `seo/INFORMATION_ARCHITECTURE_FA.md` — owner URLs, hubs, taxonomies and cannibalization rules.
- `seo/INTERNAL_LINKING_FA.md` — Learn/Lab/Services/Shop linking model.
- `seo/TECHNICAL_SEO_BASELINE.md` — live baseline, blockers and launch gates.
- `site/themes/tehnet/page.php` — normal page template with one page-title H1.
- `site/themes/tehnet/front-page.php` — homepage content without redundant page-title H1.
- `site/plugins/tehnet-core/includes/class-content-types.php` — service/lab single URL model without archive/page slug collisions.
- `content/pages/*.html` — starter page bodies with correct heading hierarchy.

### Task 1: SEO Research Contract and Evidence Ledger

**Files:** Create `tests/seo-architecture-contract.sh`, `seo/RESEARCH_LIMITATIONS.md`, `seo/QUERY_UNIVERSE_FA.md`, `seo/SERP_INTENT_MAP_FA.md`.

**Interfaces:** Consumes business scope, current SERP observations and `DashSaman/-SEO`; produces dated query decisions consumed by architecture/content work.

- [ ] Write the contract first; require evidence date, Ahrefs-IR limitation, intent, page type, business value, owner URL/decision and no fabricated volume/KD.
- [ ] Run it and verify RED because SEO evidence files do not exist.
- [ ] Populate research docs from current Persian SERPs for learning, services and shop clusters.
- [ ] Classify targets as `GO`, `NOT-YET`, `GO-LONG-TERM`, `LOW-PRIORITY`, or `NO-GO`.
- [ ] Run contract to GREEN and commit.
### Task 2: Information Architecture and Internal Linking

**Files:** Create `seo/INFORMATION_ARCHITECTURE_FA.md`, `seo/INTERNAL_LINKING_FA.md`.

**Interfaces:** Consumes Task 1 intent decisions; produces canonical owner URLs and linking rules used by future page creation.

- [ ] Define stable top-level journeys: `/learn/`, `/lab/`, `/services/`, `/shop/`.
- [ ] Define Learn hubs only where current SERP/business fit supports them; include MikroTik, networking fundamentals and later-stage Linux/monitoring boundaries.
- [ ] Define service owner pages for real commercial intents without district/city doorway duplication.
- [ ] Define Shop category/product intent; keep final WooCommerce category rewrite implementation separate until WooCommerce phase.
- [ ] Document query→owner-URL rules, canonical consolidation and when a new page is forbidden due to cannibalization.
- [ ] Define contextual links: Learn → Lab for assets, Learn → Services for implementation help, Services → relevant Learn proof/resources, Shop → guides/services, Lab → parent tutorial.
- [ ] Re-run architecture contract and commit.

### Task 3: Technical SEO Blocker Regression Tests

**Files:** Create `tests/seo-technical-contract.sh`; modify content type/theme/page content files.

**Interfaces:** Consumes current production evidence; produces conflict-free `/services/` and `/lab/`, single-H1 page templates and preserved noindex state.

- [ ] Write failing tests proving `tn_service` and `tn_lab` must not own archives that collide with pages.
- [ ] Require dedicated `page.php` and `front-page.php` template behavior.
- [ ] Require normal starter page bodies to avoid a second H1; homepage may own its editorial H1.
- [ ] Verify RED against current code.
- [ ] Set CPT `has_archive` false while preserving single rewrites under `/services/{slug}/` and `/lab/{slug}/`.
- [ ] Add page/front-page templates and correct starter heading hierarchy.
- [ ] Run test/PHP lint to GREEN and commit.
### Task 4: Safe Production Retest and Coordination

**Files:** Create `seo/TECHNICAL_SEO_BASELINE.md`; modify `PROGRESS.md`, `HANDOFF.md`, `TASKS.md`; mark this plan complete.

**Interfaces:** Consumes Tasks 1–3; produces verified production evidence and exact continuation state.

- [ ] Capture pre-change TehNet port/container fingerprint and fresh TehNet backup before deploying code fixes.
- [ ] Deploy only TehNet theme/core files using the existing safe deploy script; flush WordPress rewrite rules without container restarts.
- [ ] Re-seed only the existing editable top-level pages idempotently.
- [ ] Verify `/services/` and `/lab/` render the intended pages, all primary routes return 200, canonicals are correct where applicable, and each checked route has exactly one H1.
- [ ] Verify `blog_public=0` and homepage `noindex` remain in place; do not enable indexing.
- [ ] Document current core-sitemap behavior while noindex; do not treat sitemap availability as a launch PASS yet.
- [ ] Run the complete repository test suite, shell syntax checks and PHP lint.
- [ ] Update coordination files and commit verified facts only.

## Launch Boundary
This plan does **not** enable search indexing, mass-create tutorial pages, install an SEO plugin, publish fake location pages, configure WooCommerce SEO URLs, or claim keyword volumes unavailable for Iran. Those actions require their own evidence and implementation phases.

## Self-Review Gate
Before execution completion, verify every prioritized cluster has a truthful business path and an owner page type; every URL has one intent owner; every live technical claim has a command/retest; and every limitation is recorded rather than guessed.
