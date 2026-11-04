# TehNet MTCNA Scheduled Release Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this bounded content and scheduling package. The user explicitly authorized execution; do not restart design discovery.

**Goal:** Prepare 24 editable Persian course drafts under the existing Learn hub and establish the first release window on 2026-11-07 at 09:00 Asia/Tehran, with one subsequent eligible installment every three days.

**Architecture:** Preserve existing published canonical pages. Keep authored lessons and release evidence in this repository, create private WordPress working drafts, and let a single scheduled publisher select only the next evidence-qualified lesson. Existing canonical pages receive reviewed scoped updates, never a change to future status that removes them from public view.

**Tech Stack:** WordPress REST API, native Gutenberg blocks, GitHub, Python standard library, ChatGPT Automations.

**Spec:** docs/superpowers/specs/2026-11-04-mtcna-illustrated-course-design.md; accepted user clarification and execution request dated 2026-11-04.

## Global Constraints

- Approved identity: TehNet / تهنت / تهران نتورک / Tehran Network; YouTube @tehran.network021.
- Course: 24 coverage units in nine chapters, one release per three-day window.
- First window: 2026-11-07T09:00:00+03:30, equivalent to 2026-11-07T05:30:00Z.
- The user authorized preparation and scheduled publication. Existing site qualification controls and noindex remain applicable.
- Preserve already published pages 40, 62, 63, 64, 65, 66 and 67 until a qualified scoped update is executed.
- No unverified video attribution; Queue is independent written material.
- Real RouterOS lab evidence and original screenshots are unavailable in this session. Every affected lesson remains NOT_READY, NOT_RUN and MISSING; diagrams do not satisfy screenshots.
- Hardware-dependent Wi-Fi and RouterBOOT require corresponding physical evidence.
- Do not overwrite parallel work. This package starts from remote main 4002d5a15266bbb1c3aeefc41c7a366c7e4e33bc in an isolated content workspace and separate branch.

## Review Focus

- A blocked lesson must stay next in order; later lessons must not overtake it and missed windows must not cause a catch-up batch.
- Published canonical pages must never be made future or replaced by a competing public working-draft URL.
- Duplicate automation runs and uncertain WordPress creates must be reconciled from IDs, slugs, content hashes and live state before retrying.
- Any live editorial drift must stop an overwrite; preserve valid existing content and prepare a fresh reviewed merge.
- A scheduled check is not proof of publication. Read back the actual WordPress status/content and record a public URL after a successful release.

## Task 1: Normalize and complete the course package

- [x] Snapshot existing independent lesson drafts and schematics without modifying their original workspace.
- [x] Normalize the approved brand, metadata, version labels and official-source references.
- [x] Complete missing final project and ensure all 24 lessons have substantial content and evidence requirements.
- [x] Build valid editable Gutenberg content, with editable code blocks and meaningful diagram captions; final RTL/LTR presentation remains part of editor-save qualification.
- [x] Verify numbering, chapter coverage, block structure, canonical ownership and explicit NOT_READY states.

## Task 2: Save private WordPress drafts

- [x] Look up course working drafts by deterministic slug before creating anything.
- [x] Create one draft under hub 40; read back its content and status before proceeding.
- [x] Create remaining drafts sequentially, recording returned IDs, links, content hashes and status.
- [x] Read back the complete set and confirm all remain draft; preserve existing public owners.

## Task 3: Activate one scheduled release controller

- [x] Confirm there is no existing active course publisher.
- [x] Create an exact Asia/Tehran automation with DTSTART 20261107T090000 and a three-day interval.
- [x] Instruct it to read the repository manifest, gates, prerequisites and publication ledger; release at most one ready lesson through the existing qualified process and verify actual publication.
- [x] Keep blocked lessons queued, report the concrete blocker, never manufacture evidence and stop the automation after all 24 successful releases.
- [x] Record the actual automation ID, returned schedule and next run.

## Task 4: Reconcile and hand off

- [x] Save course sources, WordPress receipts, schedule and honest readiness counts in an isolated GitHub pull request.
- [x] Prepend a scoped checkpoint to HANDOFF.md, PROGRESS.md and TASKS.md without erasing parallel checkpoints.
- [x] Run a fresh independent review of the content/scheduling boundary and resolve material findings.
- [x] Report completed work and the remaining lab/screenshot dependency without claiming the course has been published.

## Rulings

The inherited scratch material used TehranTurk after a typo. The current conversation explicitly approved Tehran Network, matching remote AGENTS.md, the platform design and the existing WordPress site name. Only this approved spelling is retained.

The schedule has no fixed occurrence count because a blocked window is not a successful lesson release. The controller pauses itself after 24 verified releases. January 15, 2027 is the earliest last slot if every lesson is ready on time.

A separate branch is used because the previous draft PR and scratch source may still be owned by another active session. Its proposal remains linked as prior work.

## Verified preparation checkpoint

All 24 sources and metadata files rendered successfully. WordPress IDs 232–255 were independently read back with exact raw-content, slug, parent and draft-status matches on 2026-11-04. Fourteen immutable technical schematics cover all 24 lessons. The saved active automation prompt and schedule match its remote readback; next_run_time is null and is not invented. Source and payload hashes match every receipt. Runtime/lab, original screenshots, editor-save and release qualification remain pending; zero installments are publish-ready.

Source preparation pull request: https://github.com/DashSaman/TehNet/pull/82 . The repository CI status is recorded on that PR; it does not qualify RouterOS runtime results.
