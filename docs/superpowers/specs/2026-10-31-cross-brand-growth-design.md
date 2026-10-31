# TehNet × MyTel × SEO: execution design

User specification: `docs/requirements-growth-2026-10-31.md` (full original, 1,818 lines). User explicitly requests autonomous execution; no additional design questionnaire is required. The complete transformation is an ongoing program, not declared complete by the first release.

## Protected architecture

Keep WordPress, Gutenberg, existing Core/Store/MU plugins and Learn/Lab/Services/Shop. TehNet owns networking infrastructure and its educational/application perspective. MyTel owns commercial PBX/VoIP intents and existing frozen URLs/titles/H1s. MyTel production is read-only. No fabricated shared legal ownership, `sameAs`, stock, pricing, certifications, SLA, reviews or citation data. Preserve noindex and physical-product inquiry gates. SEO research is transferred to a separate branch in `DashSaman/-SEO`; no private MyTel metrics or customer data are copied.

## Current evidence

Fetched TehNet `origin/main` at `b5ec3da`; prior conversation branch is stale. Isolated worktree starts from that main. Store is0.7.0 in source, with working contributions that must not be rebuilt. Public/native reads on31October show25 inquiry-only products, noindex,32 published nonproduct items and five existing service pages.13 MyTel specialist routes return200 with index/follow and their own H1/canonical. Native source content/hashes are captured privately, with only sanitized summaries committed. Public form DOM proves `_wpnonce` is outside each returned support/B2B form. No real submission was made.

## Approaches considered

1. New builder/CRM or wholesale theme rebuild: rejected because it duplicates working components, increases migration risk and ignores existing editorial ownership.
2. Generate large page batches first: rejected because the service journey and existing request forms have concrete gaps, and candidate count is not publication permission.
3. Extend existing MU tools and ticket intake, improve existing service discovery, add one distinct network-readiness resource and retain evidence-backed phased backlog: chosen under the user's autonomous direction. It delivers a useful path without modifying frozen MyTel pages or inventing product assets.

## First implementation unit

- Fix nonce placement in both returned shortcode forms using WordPress's return-value mode, retaining nonce validation, throttles and existing private records.
- Allow a fixed, validated `voice-network` service context to prefill the existing ticket form; reject arbitrary/array inputs and escape output. Keep optional metadata within the existing ticket record; no email or real customer action during tests.
- Add a server-rendered, accessible network-readiness checklist to the existing technical-resource MU plugin. Eight manual questions use `unknown/ready/issue/na`. JavaScript improves summaries and produces an explicit local report; no score, network measurement, telemetry, persistence or router writes. Essential questions, instructions and referral links remain visible without JavaScript.
- Add an original Gutenberg-editable network-readiness service page covering discovery, Voice VLAN/QoS/PoE/WAN, measurements under load, privacy, change window and recovery. Link to MyTel `/services/` and `/voip-support/` only where the user needs telephony deployment. Improve existing Services/Lab discovery with bounded append-only sections; home/menu and established service URLs stay intact.

## Program artifacts

Record brand/query ownership, cross-brand link decisions including pending MyTel-side proposals, competitor scorecard with observed evidence,100+ distinct candidate topics marked by actual research state, index-launch checklist, measurement definitions and phased acceptance matrix. Candidate topics without market/SERP/source evidence remain deferred/unpublished. Current Google/Bing/OpenAI guidance is provider-scoped; a200 response or old Help Center slug is not enough to establish source identity.

## Acceptance and release

Red/green PHP tests reproduce nonce placement and service-context boundaries. Test the checklist's real mouse/keyboard/mobile/no-JS/export/reset behavior in a browser; ensure no external requests and no overflow. Native staging must confirm Gutenberg parsing, rendered forms, protected data, service/cross-domain URLs and unchanged noindex/commerce gates. Production writes require fresh full backup/checksum, exact file/body drift gates and a reversible journal; MyTel receives no production changes. Failed/skipped/transport-limited checks remain explicit. Each milestone includes source synthesis and SEO-repository handoff before being called complete.
