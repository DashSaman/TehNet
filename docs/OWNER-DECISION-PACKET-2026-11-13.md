# Owner decision packet — 2026-11-13

Single reference for the decisions only you can make. Nothing here has been merged, deployed, published or un-noindexed without your explicit authorization. Production changes this cycle: **zero**.

## 1. Open PRs and recommended merge sequence

| Order | PR | Content | Conflicts | Verified state |
|---|---|---|---|---|
| 1 | #96 | Agent control + fail-closed Codex bridge | none (standalone ops scripts) | CI green; behavioral suite proven live |
| 2 | #95 | SEO research docs (90 keywords, 30 briefs, 180-day plan) | none (docs only) | CI green |
| 3 | #93 | Queue lesson (cloud lab, 12 frames) | ops scope tables only | staging VERIFIED by delivering agent |
| 4 | #89 | Static routing lesson (ID64, 10 captures) | ops scope tables | staging VERIFIED |
| 5 | #90 | NAT lesson (ID65, 13 captures) | ops scope tables | staging VERIFIED |
| 6 | #91 | Firewall lesson (ID66, 6 captures) | ops scope tables | staging VERIFIED |
| 7 | #97 | JSON-LD CollectionPage schema | none (plugin + tests) | frontend VERIFIED via tunnel |
| 8 | #99 | Buyer-oriented network-setup-tehran revision | ops scope tables | staging APPLIED, 63 native + 17 browser checks, rollback drill proven |
| 9 | #98 | UI/UX audit v3-r2 QA evidence | none (qa only) | QA_BASELINE_VERIFIED (bounded), CI green |
| 10 | #94 | Index readiness + buyer decision aids | none (mu-plugin + policy, **default-OFF**) | ready; needs its own explicit gate |

Notes:
- PRs #89/#90/#91/#93/#99 all extend `ops/release-growth-content.py` + `ops/migrate-growth-content.php` scope tables. Merging any two requires a mechanical rebase of the later one (single-line map entries). Merge them in your chosen order; rebase is per-PR and low-risk.
- Merge ≠ deploy. Every production release is a separate owner-authorized run of the scope-guarded release tool.

## 2. Release dependencies (production)

1. **Backup precondition**: fresh server backup with verified SHA256SUMS before any production apply (the release tool enforces this automatically and refuses without it).
2. **Recovery qualification**: production rollback gate requires `recovery_qualified_utc` in the private config — staging rollback drills are done; production qualification is part of your first release authorization.
3. **Content digest match**: each release refuses if production content drifted from the staging-verified baseline — drift means re-verify, not overwrite.
4. **PR #97 post-deploy check**: after deploying JSON-LD, run the committed native test once on production (read-only).

## 3. Off-host recovery — blocking decision

- Current state: backups exist **only on the server host** (2026-11-13 set verified). Restore rehearsal passed (6/6 tables, 52/52 rows) on staging.
- Risk: a host loss destroys both the site and its only backup copies.
- Needed from you: off-host destination (object storage / second host / offline media), capacity (~5.3 GB current), retention window.
- Recommend: decide this **before** the first production content release.

## 4. Indexability — unchanged, default-off preserved

- Production remains intentionally `noindex` (`blog_public=0`). No pending PR changes this.
- PR #94 ships the index policy **default-OFF** with a 16-URL allowlist; activating it, and later flipping the site index, are two separate future decisions with their own verification steps.
- GSC first-party data: PR #95 documents the access requirement; no ranking/search data was invented without it.

## 5. Decision asks

1. **Merge approvals**: which of the 10 PRs and in which order (recommend the sequence above; #96 and #95 are zero-risk starters).
2. **Off-host backup destination**: required before first production release.
3. **Production releases**: authorize individually per PR after merge; each runs check → backup → apply → verify, with journal + rollback.
4. **Index flip**: defer; nothing to decide today.
5. **Queue lesson continuation**: handoff recipe is pushed on `handoff/queue-in-progress-20261106`; say "continue queue" to resume in a future session.
