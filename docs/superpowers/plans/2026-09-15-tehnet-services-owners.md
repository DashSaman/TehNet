# TehNet Services Owner Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans task-by-task. Track steps with checkbox syntax.

**Goal:** Publish the five evidence-approved commercial service owner pages under `/services/` with truthful Tehran/remote scope, editable Gutenberg content, and safe production verification.

**Architecture:** Service intent is owned by hierarchical WordPress pages beneath the existing `/services/` hub. This keeps routine editing in WordPress admin and avoids creating duplicate CPT/archive owners. NAP values are rendered from centralized TehNet settings rather than hardcoded across pages.

**Tech Stack:** WordPress/Gutenberg, TehNet theme/core, WP-CLI seed scripts, Bash contracts.

**Spec:** `docs/superpowers/specs/2026-09-14-tehnet-platform-design.md`

## Global Constraints
- On-site claims: Tehran only.
- Remote Support: nationwide Iran.
- No fake neighborhoods/cities, testimonials, prices, guarantees or certifications.
- Keep `blog_public=0` and rendered `noindex,nofollow` throughout this phase.
- Preserve `127.0.0.1:18082`; do not alter Nginx/Docker topology or unrelated services.
- Routine service copy, CTA and NAP must remain editable from WordPress/admin settings.
- Each commercial intent has one canonical owner URL.

---
## Owner URLs
- `/services/network-tehran/` — خدمات شبکه تهران
- `/services/network-support-tehran/` — پشتیبانی شبکه تهران
- `/services/network-setup-tehran/` — راه‌اندازی شبکه شرکت در تهران
- `/services/mikrotik-tehran/` — خدمات MikroTik تهران
- `/services/remote-support/` — پشتیبانی شبکه از راه دور در سراسر ایران

### Task 1: Service Content Contract and Owner Pages

**Files:** Create `tests/service-owner-contract.sh` and five `content/pages/service-*.html` files.

**Interfaces:** Consumes `seo/SERP_INTENT_MAP_FA.md` and `seo/INFORMATION_ARCHITECTURE_FA.md`; produces substantial Gutenberg bodies for the approved owner URLs.

- [x] Write the failing contract first: require all five page bodies, no editorial H1, truthful Tehran/remote language, central phone shortcode, contact CTA, and distinct intent-specific sections.
- [x] Run it and confirm RED.
- [x] Write original Persian service copy for each owner. Use specific scope/process/troubleshooting language but no invented claims or prices.
- [x] Re-run contract to GREEN and commit.

### Task 2: Idempotent Hierarchical Seeding and Services Hub

**Files:** Modify `ops/wp-seed-foundation.sh`, `content/pages/services.html`, and the Task 1 contract.

**Interfaces:** Consumes the existing `SERVICES_ID`; produces five child pages under the real Services page and discoverable links from the hub.

- [x] Extend contract first to require stable IDs and `post_parent="$SERVICES_ID"` for all five pages plus hub links to all approved URLs.
- [x] Verify RED.
- [x] Seed/update each page idempotently and assign `SERVICES_ID` as parent; do not add all service pages to the primary navigation.
- [x] Update `/services/` body with concise cards/links and centrally managed phone/address details.
- [x] Run service contract, Gutenberg contract and shell syntax to GREEN; commit.

### Task 3: Safe Production Deployment and Live SEO Checks

**Files:** No new runtime topology; update evidence/coordination only after checks.

- [x] Create a fresh TehNet DB/wp-content recovery point and capture non-TehNet runtime fingerprint.
- [x] Run only the idempotent content seed and WordPress rewrite flush; no container/Nginx restarts.
- [x] Verify all five service URLs return 200, exactly one H1, correct canonical and `noindex,nofollow`.
- [x] Verify `/services/` links to all five owners and still returns one H1.
- [x] Verify `blog_public=0`, TehNet bind `127.0.0.1:18082`, and non-TehNet fingerprint unchanged.

### Task 4: Coordination and Integration Readiness

**Files:** Modify `PROGRESS.md`, `HANDOFF.md`, `TASKS.md`; close this plan with evidence.

- [x] Run every repository contract, shell syntax check and PHP lint.
- [x] Update coordination files with verified production facts and fresh backup path.
- [x] Close plan checkboxes and commit.
- [ ] Merge to `main`, rerun the full suite on `main`, push, and clean up the worktree/branch.

## Completion Boundary
This plan does not create district-level pages, quote/ticket workflows, WooCommerce products, Google Business Profile changes, or LocalBusiness JSON-LD. Structured data is deferred until complete identity/address fields and a dedicated validation plan are available.

## Self-Review Gate
Each owner page must answer a distinct commercial intent, clearly distinguish Tehran on-site from nationwide remote service, use centralized contact values, remain editable through Gutenberg, and avoid unsupported marketing claims.