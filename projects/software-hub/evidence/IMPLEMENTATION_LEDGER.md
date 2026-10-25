# Implementation ledger — TehNet Software Archive

Owner request (2026-10-17): finalize W0, begin implementation using existing research, preserve current site, add a menu link and record every task/test. Owner correction: this is a section of TehNet, not a separate Melika brand. Use «آرشیو نرم‌افزار تهران نتورک», `/software/`, and `projects/software-hub/`. Original source repository names/attribution and raw historical evidence remain unchanged.

## Pre-flight decisions

- W0→W2/W3/W4/W5/W6: shared models, visibility, schema and base-path contracts must be frozen before consumers. W0 owns these files; one implementer in this request.
- W0→W6: preview can publish the reviewed mirror-research registry with all routing disabled; it cannot expose VPN data or claim download/offline acceptance. Restricted routes fail closed until W2 is actually implemented.
- W6→menu: owner explicitly authorized the single TehNet navigation addition. Use WordPress menu APIs, preserve every existing item/location and make the update idempotent/reversible. No theme replacement or general reseed.
- W6→host: existing authorized SSH profile reached the actual TehNet host and confirmed 127.0.0.1:18082 plus its Nginx config. Candidate 18083 currently has no listener. Deploy only a separate bounded service and exact `/software` prefix; capture full backup and before/after unrelated-service fingerprints.
- Ruling: current request authorizes this implementation and scoped route/menu deployment; do not ask again for the already specified design. W7 real migration, provider activation and W2 private access remain separate gates. Cost if wrong: a bounded route/service/menu rollback; no existing website code or data schema changes are permitted.
- WPVibe plugin-backed menu command returned 404 because its optional plugin is absent. Do not retry plugin-backed tools or install anything; use the existing authorized SSH/WP-CLI path.

## Tasks

W0 claimed by current Codex implementer; base e61227712311d77baef4694f88d2b934ab90ec43. Exact owned paths: app/models.py, config.py, db.py, migrations/, contracts/, tests/test_contracts.py and task/status documents. W6-preview follows after W0 acceptance; it does not close full W6 or W2.

W0 complete: nine tests PASS / exit 0. Typed v1 contract and schema frozen; test fixtures explicitly close SQLite handles for Windows cleanup. Next W6-preview; no W2/private/provider acceptance.

W6-preview software ready: 30/30 Linux tests PASS; 23/23 local runnable checks PASS; 18 original probe checks PASS; PHP menu logic 5 checks PASS and two PHP lint checks PASS. Browser rendering/search verified. Initial Linux suite fixture omitted the rehearsal tool mount (5 expected setup failures); reran with full read-only validation tree and all 30 passed.

Ruling: before deployment, nullable unknown source base_url takes precedence over contradictory original NOT NULL SQL. Corrected the initial migration before any deployed state existed; replaced broad INSERT OR IGNORE with ID-conflict-only handling. Cost if wrong: future source imports fail visibly instead of silently discarding records.

Final review: one independent focused reviewer, three Important deployment findings. Added actual-flow sandbox tests for preexisting route, partial startup, post-data/snippet/reload/menu failures and SIGTERM; each failed against original behavior and passed after the single fix pass. No reportable minors deferred. Not assessed by reviewer: production host/edge behavior; live validation remains required.

Initial live attempt: readiness failed with curl status 7 before Nginx/menu mutations. The real rollback removed only the new container/network and preserved its fresh data under the validated private backup; existing site remained intact. An isolated probe confirmed this Docker host suppresses published ports for internal networks (`8000/tcp: null`) while Uvicorn itself runs. Ruling: preview uses its own bridge network and loopback published port; it performs no upstream fetches and enables no providers. Physical outbound filtering and outage acceptance remain unimplemented W3/full-W6/W7 gates. Cost if wrong: a future fetch feature could reach outside; it must not be enabled before its policy tests. Offline unit/image builds still run with network none. Preserve failure logs before removing newly owned containers.

Second live attempt: the Nginx guard correctly aborted on two server_name declarations (HTTPS and HTTP redirect), then restored original config and removed newly owned resources. Added an explicit positive sandbox test matching both virtual servers; it failed against the original guard. The guard now validates the first HTTPS block and inserts only there, preserving the HTTP redirect block. This is a host-config compatibility fix, not permission to rewrite additional routes.

Third first-install attempt: origin readiness immediately after graceful reload saw the prior worker's 404. A bounded JSON-ready poll regression test failed first, then passed. Fourth first-install succeeded with backup 20261017-141739-software-preview, image 8889969a..., menu item 189. Existing fingerprints and original menu order preserved; repeat menu apply created no duplicate.

Owner's styling/easy-install request: measured current theme colors and copied its unmodified local Vazirmatn fonts with full OFL attribution. Added self-only JS for shared tn-theme preference and clipboard, eight online apt install/check guides, explicit prerequisites and offline-unaccepted text. Two new preview tests went RED then GREEN. Browser clipboard read adapter returned empty while UI reported success; verified actual clipboard by pasting into the page search input instead, which produced exact curl --version. Restored input/theme after test. Mobile 390px viewport: client/scroll width375; no horizontal overflow. Console warning/error list empty.

Latest Linux suite 36/36 passes in 44.346s; two actual-script update tests cover successful isolated replacement and partial-start rollback with real SQLite snapshot. Full Windows invocation initially used wrong cwd and could not import app; correct project cwd passed 25 with 11 Linux-only skips. No product change was needed for that command error.

UI release ui-20261017 built offline and updated only the archive container after fresh backup 20261017-143634-software-update; immutable image 54f507b987e5a252a6f207478ddd5bb6251c8889c1ed45657857be017e314352. Two transient archive 502 probes during replacement, then ready; no previous container restarted. Existing Nginx config compared byte-for-byte unchanged by update.

Same-host Linux cold-process restore of actual 110592-byte catalog, preloaded exact image, non-root/read-only/network-none container: 1.764134360 seconds including snapshot. All 27 source rows, public page, local CSS/JS/fonts ready. This is not image import, WAN/ingress/Iran/private/post-write rollback acceptance. W7 stays NOT_ACCEPTED. Active attribution links accidentally renamed to DashSaman/software during prior branding pass were corrected to actual DashSaman/melika; immutable blob/hash inventory was never changed.

Integrator reconciled current STATUS/CHANGELOG/task/root notes. Historical entries remain dated observations; current deployment report supersedes interim pending statements. Final remote ref readback is required after commit/push; no main merge.

Developer copy/paste setup now includes a venv, exact runtime + test lock and explained run/test commands; all 19 hashed wheels resolve in an offline disposable-container dry run. Added Bash LF checkout policy and ignored local .venv. Runtime-input comparison verifies all 18 deployed release inputs equal local bytes. Added reusable same-host restore and origin/public smoke tools; public reports contain no private backup bytes. Final source-attribution check additionally verifies the research entry links to the manifest's original repository.
