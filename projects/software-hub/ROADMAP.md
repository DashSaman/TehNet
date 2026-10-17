# TehNet Software Archive implementation roadmap

> Current owner override (2026-10-17): no downloadable payloads on the website VPS. [ADR 0002](decisions/0002-external-payload-storage.md) supersedes historical local-CAS requirements. The engine keeps metadata only, redirects approved public downloads externally, and refuses private redirects. W2/W3/external-W5 code is staged; production activation, external private delivery, provider and migration acceptance remain separate gates. See [external storage](EXTERNAL_STORAGE.md) and [engine operations](deployment/ENGINE_OPERATIONS.md).

**Goal:** consolidate research and build an independently operable offline-continuity service under TehNet without disrupting its current site.

**Architecture:** a proposed isolated mirror engine under `/software/`, preserving the WordPress/Core boundary, with local state, verified artifacts and explicit restricted access.

**Tech stack:** selected research stack Python 3.12/FastAPI/Jinja2, SQLite single writer, native APT/gpgv, external payload placement, Nginx/Compose; lock actual supported versions during implementation.

**Spec:** [DESIGN](DESIGN.md), [CONTRACTS](CONTRACTS.md), [security](SECURITY_PRIVACY.md), [migration](deployment/MIGRATION.md). W0 v1 is implemented and frozen; the public read-only preview is implemented. Remaining capabilities await their individual gates. Use the environment's appropriate implementation/testing skills when implementing; do not bypass the owner's limit on delegation or scope.

## Global constraints

Public normal sections; password protection for VPN on the server; no secrets/private payloads in public Git. Preserve source attribution and trust labels. Never change `18082`, WordPress/Core behavior, existing index status or unrelated containers as part of TehNet Software Archive work. No provider enabled by discovery, Rubika disabled, no arbitrary URL proxy, no foreign fallback in domestic-only mode. Do not claim a profile, provider, migration or official certification passed without its own evidence.

## Review focus

Prefix loss/login redirect escapes (W6); private data leaking through public API/cache/direct Range (W2); database restored while referenced objects missing (W5/W7); two writers after rollback (W7); domestic frontend still dependent on foreign ingress/DNS/token service (W7). Each owner must include these cases in its tests, not just a happy path.

## Phase 0 — consolidation (this delivery)

- [x] Identify `DashSaman/TehNet` using repository/domain/deployment evidence and verify connector write permission.
- [x] Copy all existing Linux Git blobs with origin/hash inventory; preserve originals and original instructions as historical data.
- [x] Record missing OFFLINE_SOFTWARE_CATALOG without inventing it.
- [x] Write entry guide, architecture, privacy, workstreams, mandatory task logging and portable migration design.
- [x] Run fresh checks and prepare the separate review branch. Publication is confirmed only by remote ref readback in the delivery report; no merge or deployment is implied.

## Phase 1 — contracts and recovered knowledge (W0/W1)

- [x] W0 resolves app boundary vs TehNet Core, base path, route ownership and auth/data models; publishes versioned typed contracts and release/state schema, plus baseline tests.
- [ ] W1 imports and audits the missing package when supplied; indexes every recovered file, reconciles counts/claims, preserves sources and private classification.
- [ ] Content owner selects a modest public P0 subset and one native Ubuntu profile. VPN candidates stay restricted; broad 200+ candidate lists do not imply deployment readiness.

**Exit:** frozen interfaces and accepted design; W1 can remain explicitly blocked while public engineering uses existing Linux research. No false declaration of complete research consolidation.

## Phase 2 — independently tested engine (W2/W3/W5 parallel, then W4/W6)

- [x] W2 component implements local password/session authorization, public projections and leakage tests. Owner-operated setup and production activation remain open.
- [x] W3 component implements bounded DNS-pinned full-stream verification/probe/source policy and real local TLS fixtures. Real provider activation remains open.
- [x] W5 first component implements external metadata registry, no-disk full hashing, public redirects and refusal of private redirects; Rubika stub remains disabled.
- [ ] W5/W6/W7 implement an accepted external private backend, workstation/transfer-worker direct upload, encrypted metadata/auth backup+restore and new-state activation/rollback. No website payload cache/CAS is permitted.
- [ ] W4 verifies original APT metadata/index/artifact chain and native dependency closure; unknown availability stays unknown; no fabricated production hashes.
- [ ] W6 wires app/UI/worker with one writer, local Persian assets, prefix-safe URLs and source approval CLI; checks the full feature/integration suite.

**Exit:** deterministic software acceptance, secure private boundary, reproducible offline-startable release. Keep `apt_profile_accepted=false` until real clean-client tests.

## Phase 3 — foreign VPS staging/subpath (W6 + integrator)

- [x] Fresh host/port/route inventory and validated scoped backup for the public preview.
- [x] Public preview and one menu item deployed; actual site colors and eight online copy/paste guides verified.
- [ ] Complete full engine/privacy/download/load acceptance; preview evidence does not close full W6.
- [ ] Deploy the isolated new project only after topology/config review; run actual Nginx, route, WordPress/noindex, public/private and load checks.
- [ ] Measure CPU/RSS/disk/egress, latency and current-site impact; set quotas from evidence. Record exact service and image refs.
- [ ] Provider agreements, actual full hashes, storage retention and real Iranian-client tests documented separately.

**Exit:** service staging/live acceptance only for the features actually exercised; current WordPress unchanged; rollback evidence saved. Foreign VPS success is not domestic outage acceptance.

## Phase 4 — portable migration qualification (W7)

- [ ] Implement real release/preflight/snapshot/restore/smoke/cutover/rollback scripts and cold Linux restore from preloaded artifacts.
- [ ] Warm an Iranian target, preseed media/images, select hostname/ingress plan preserving WordPress and removing foreign dependencies for TehNet Software Archive.
- [ ] Complete two representative measured cross-host drills and rollback, plus post-write rollback/split-brain safety tests.
- [ ] Measure complete timed window under 1,800 seconds with prerequisites disclosed; test domestic mode with isolated foreign egress denial.
- [ ] Perform the owner-authorized cutover, retain old state and independently verified backups for the approved retention period.

**Exit:** only measured and reproducible real-host evidence accepts the migration target. Today's synthetic local timings cannot close this phase.

## Phase 5 — content and storage expansion

After W1: prioritize the documented offline kits by Iranian operational value, dependency closure, disk budget and failure domains. Give separate install/run/restore evidence per exact version/arch. Explore Git bundles plus releases/LFS/submodules, Python wheelhouse, OCI/Skopeo, OpenWrt and other ecosystems with protocol-specific tools; a generic 302 does not implement every registry. Compare reuse options from original research before building replacements.

Evaluate Iranian S3/partner hosts and optional official Rubika bot pilot only after contract/retention/Range/anonymous access/full-hash/independent restore gates. Measure 24/72-hour retention in actual elapsed time. Keep at least one critical copy independent of the chosen provider. Update costs from current official sources when procurement is requested; historical estimates are not current quotes.

## Phase 6 — differentiated service and support applications

Offer optional organization-local readiness assessment that runs with consent and exports dependency inventories without credentials or customer databases. Build service-weighted, dependency-complete storage planning and compare it with simple popularity/size/LRU baselines; report measured recovery coverage, not invented improvements. Provide machine-readable install/run/restore reports with artifact provenance and security-data age. Consider standard signed update frameworks after threat/operational review.

For tariff registration, national-project support, loans and knowledge-based-company assessment, create separate evidence packs: measured domestic data paths/IP ownership, operating entity and rights, R&D records, benchmark baseline/results, actual offline installations/customer pilots, budget and support model. Verify current official eligibility/processes at application time. None of these approvals, rates or loans is acquired or guaranteed by this roadmap; forwarding a URL is not proof of domestic billing.

## Task execution and handoff

Use [WORKSTREAMS](WORKSTREAMS.md) for exact owners, paths, dependencies and acceptance. Claim one task before editing, write a task-specific plan/test cycle, run checks, record actual results and next action. Integrator serializes shared docs and root coordination updates. A task without its task log and changelog/status reconciliation cannot be merged as done.
