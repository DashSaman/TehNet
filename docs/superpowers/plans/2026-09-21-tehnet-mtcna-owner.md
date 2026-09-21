# TehNet MTCNA Owner Implementation Plan

## Goal
Publish the already-approved `/learn/mikrotik/mtcna/` owner as one substantial Persian learning-path page. Do not create one thin page per YouTube episode. Keep production intentionally non-indexable.

## Evidence / intent ruling
- Existing query universe marks `آموزش MTCNA فارسی` as a distinct guide/course intent owned by `/learn/mikrotik/mtcna/`.
- Existing YouTube map assigns seven numbered MTCNA episodes plus the GNS3 practice video to this owner.
- Fresh Persian SERP review on 2026-09-21 still shows course/learning-path pages and long-form MTCNA video courses as the dominant result type.
- Generic VPN and Linux owner pages remain deferred: current SERPs are fragmented by protocol/use case and Docker/NGINX sub-intents, so this phase does not invent those URLs.

## Architecture
- Page type: hierarchical WordPress Page.
- Parent: `/learn/mikrotik/`.
- Owner URL: `/learn/mikrotik/mtcna/`.
- H1 remains owned by `page.php`; block content must not contain `<h1>`.
- Page must remain editable Gutenberg block content.
- Include all mapped MTCNA/GNS3 videos in one ordered learning path.
- Cross-link to `/learn/mikrotik/`, `/lab/`, `/services/mikrotik-tehran/`, `/contact/`.
- Update the MikroTik hub so its MTCNA section links to the published owner.

### Task 1 — RED content/hierarchy contract
- [x] Add a failing MTCNA owner contract requiring source file, no editorial H1, all mapped video IDs, required sections/internal links and seed hierarchy.
- [x] Confirm RED.

### Task 2 — Owner content and idempotent seed
- [x] Write original Persian MTCNA path content with prerequisites, RouterOS practice flow, ordered episodes, GNS3 lab, checkpoints and next steps.
- [x] Replace the MikroTik hub's future-tense MTCNA note with a link to the published owner.
- [x] Extend seed script idempotently and set MTCNA parent to the MikroTik page.
- [x] Run MTCNA/Gutenberg/full contracts plus shell syntax; commit.

### Task 3 — Production gate
- [x] Create fresh DB/wp-content recovery point and non-TehNet runtime fingerprint.
- [x] Run only idempotent content seed + rewrite flush; no container/Nginx restart.
- [x] Verify public and origin `/learn/mikrotik/mtcna/` return 200, exactly one H1, correct canonical, `noindex,nofollow`, all mapped video IDs and internal links.
- [x] Verify MikroTik hub links the owner, `blog_public=0`, bind `127.0.0.1:18082`, and unrelated runtime unchanged.

### Task 4 — Evidence/integration
- [x] Record production evidence and recovery path.
- [x] Update PROGRESS/HANDOFF/TASKS and content maps with verified status only.
- [x] Run full suite, shell/PHP lint, live gate and secret scan.
- [ ] Merge to `main`, rerun tests/live gate, push, close plan, remove worktree/branch.
