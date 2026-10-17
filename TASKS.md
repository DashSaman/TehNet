# TehNet Task Backlog

Status legend: `LOCKED`, `NEXT`, `BACKLOG`, `BLOCKED`, `DONE`.

## Product decisions
- DONE — Brand/domain: TehNet / تهران نتورک / tehnet.ir.
- DONE — Primary market: Iran, Persian-first.
- DONE — On-site services: Tehran; Remote Support: nationwide.
- DONE — Free education in phase 1.
- DONE — Physical shop starts as inquiry/manual quote.
- DONE — Digital products support download-only and licensed models.
- DONE — Full user account required.
- DONE — Ticket + Telegram two-way target.
- DONE — Gutenberg/custom blocks preferred over Elementor.

## Foundation
- DONE — Document live TehNet WordPress/Docker baseline in `ops/`.
- DONE — Define backup/recovery checklist before site implementation.
- DONE — Create feature-branch workflow and deployment validation checklist.
- DONE — Create foundation implementation plan from the approved master spec.
- DONE — Create and execute WordPress bootstrap/activation implementation plan.

## Theme / admin
- DONE — TehNet RTL theme foundation.
- DONE — Blue/turquoise/white design tokens.
- BACKLOG — Tehran visual motifs with restrained use.
- DONE — Central settings page for phone/address/social/CTA foundation.
- BACKLOG — Add centrally managed logo/media identity controls.
- DONE — Reusable Gutenberg patterns and editable homepage/top-level page foundation.
- BACKLOG — Preview optional professionalized logo variants before any logo replacement.

## Deployment safety
- DONE — Real pre-change production backup created and validated.
- DONE — Theme/plugin deployed without changing `127.0.0.1:18082`.
- DONE — Unrelated container/image/port topology verified unchanged during deploy.
- DONE — Finalize WordPress installation and activate foundation without topology changes.

## SEO / content
- DONE — TehNet query universe and dated SERP intent map.
- DONE — Topic hub architecture.
- DONE — URL/taxonomy/owner-URL plan.
- DONE — Technical SEO baseline, route/H1/canonical/noindex regression gates.
- BACKLOG — Search Console and conversion measurement.
- DONE — YouTube inventory and video→owner-URL mapping (33 current public videos).
- DONE — Internal linking map Learn/Lab/Services/Shop.
- DONE — First substantial Learn owner `/learn/mikrotik/` built and live-verified.
- DONE — LocalBusiness/NAP implementation with centralized settings.
- DONE — MTCNA owner `/learn/mikrotik/mtcna/` built and live-verified.
- DEFERRED — Generic VPN/Linux hubs pending stronger independent SERP intent; do not create thin/generic pages.
- DONE — WooCommerce catalog + physical inquiry foundation / کاتالوگ ووکامرس و استعلام محصول فیزیکی.

## Services
- DONE — Tehran service taxonomy/pages using approved owner URLs.
- DONE — Nationwide Remote Support owner page/flow foundation.
- BACKLOG — Quote/request workflow.
- BACKLOG — Service history in user dashboard.

## Commerce
- DONE — WooCommerce catalog structure / ساختار کاتالوگ WooCommerce.
- DONE — Physical-product inquiry mode / حالت استعلام قیمت محصول فیزیکی.
- NEXT — Manual quote/invoice lifecycle / چرخه دستی پیش‌فاکتور و فاکتور.
- BACKLOG — Digital download entitlement flow.
- BACKLOG — License domain model and activation/revoke/audit flow.
- BLOCKED — Rial gateway selection (owner has intentionally not selected one yet).
- DEFERRED — Verify NoPayments official integration only in the later payment-adapter phase / بررسی NoPayments در فاز پرداخت.

## Account / support
- BACKLOG — Full user dashboard.
- BACKLOG — Ticket system.
- BACKLOG — Telegram notification bridge.
- BACKLOG — Telegram reply→ticket synchronization.
- BACKLOG — Duplicate-event protection and audit log.

## Launch
- BACKLOG — Performance validation.
- BACKLOG — Security review.
- BACKLOG — Mobile/RTL validation.
- BACKLOG — SEO launch checklist/retest.
- BACKLOG — Production launch and post-launch measurement.

## Separate TehNet Software Archive research and implementation track (2026-10-17)

- REVIEW — Isolated research consolidation/design at `projects/software-hub/`; exact checks in its evidence log.
- BLOCKED — W1: recover original OFFLINE_SOFTWARE_CATALOG ZIP/patch/checksums (not in source Git history).
- NEXT (TehNet Software Archive only) — W0: freeze interfaces, private-access boundary and proposed subpath design; do not replace the existing commerce NEXT task.
- BACKLOG — W2–W7 implementation, staged deployment and real timed Iran migration/rollback; see `projects/software-hub/WORKSTREAMS.md`.

### 2026-10-17 — Software archive W0

Owner renamed this section to TehNet Software Archive (/software/, projects/software-hub). W0 v1 concrete contracts/schema/read-only state and SQLite backup passed 9 tests. Work continues with a public preview and scoped menu integration; existing site code/config is unchanged at this checkpoint. Private access/provider/download/migration gates remain open.

### 2026-10-17 — Software archive preview live (supersedes earlier archive-only status)

Owner authorized current-research implementation, the exact /software/ route and one menu option. W0 is done. Public preview is live at https://tehnet.ir/software/ under Tehran Network branding; matched actual site colors/font and added eight explained online install/check copy controls. Original WordPress/theme/Core/page files and existing container IDs/images/ports preserved; old eight menu items retain order, one item 189 added. Indexing remains disabled.

Verification: Linux 36 pass/no skips; Windows 25 pass/11 Linux-only skips; original research 18 pass; menu helper 5 checks/two lints; origin/public/browser and source-hash checks in projects/software-hub/evidence/DEPLOYMENT.md. Fresh private whole-site backup and archive DB snapshot preceded archive-only update. Read current projects/software-hub/STATUS.md before acting; earlier 'not deployed' entries describe historical checkpoints.

Exact next archive work: W2/W3/W5 against frozen W0; then signed/dependency-complete W4 acceptance and full W6. Private routes are closed, not authenticated; downloads/providers/Rubika disabled. W1 original catalog is owner-deferred while existing research continues. Same-host Linux preview restore passed in 1.764 seconds with preloaded image; real Iranian migration under 30 minutes remains NOT_ACCEPTED. Existing commerce priorities above remain independent.

## 2026-10-17T15:11:01.365417+00:00 — W2 checkpoint

W2 component implemented: Argon2id (pwdlib), opaque hashed server-side sessions, CSRF/origin checks, bounded form parsing and one password verification at a time; expiry/logout/revoke/password-change invalidation; durable five-attempt/minute global login throttle and bounded challenges/sessions. Generic private access UI and hidden-terminal-only local password CLI; no public VPN navigation/data, no default password. Original research catalog schema 001 unchanged; auth has its own explicitly initialized versioned SQLite state. Same-origin WordPress is still in the shared browser trust boundary; this is not separate-user account management.

Tests: `python -m unittest discover -s tests -v`, project cwd, separate development venv: 57 total, 46 passed, 11 Linux-shell-only skipped, exit 0, 4.595 seconds. Includes 21 new auth/route/CLI checks. Initial tests failed before modules/config existed. Earlier preview assertion that all /access requests are unimplemented was updated: GET access is now implemented but returns 503 until local password setup; private/download deny tests remain. Linux image/authenticated file serving/encrypted backup/live acceptance remain pending. No production site change at this checkpoint. Runtime auth dependency wheels downloaded from PyPI, not installed in the host OS; development venv creation first hit transient temp-disk space failure, diagnosed from complete ensurepip trace and completed without ensurepip using the existing pip to target that isolated venv.

## 2026-10-17T15:23:15.618724+00:00 — W3 checkpoint

W3 component implemented: allowlisted HTTPS-only canonical targets; reject credentials/nonstandard ports/queries/ambiguous traversal and any private/mixed/multicast/reserved DNS answers. Numeric peer is pinned without re-resolving the hostname; original Host/SNI and chain/hostname verification retained. Proxy environment is ignored, automatic redirects disabled. Durable request/full-byte budgets, global/per-host leases, one full-download worker, host interval, retry-after and failure circuit survive restart. DNS workers and full wall-clock transport deadline are bounded; samples never count as full verification, failed/oversized/hash-mismatched/HTML/encoded bodies never publish, and existing destinations are not overwritten.

Actual W3 checks: 26 passed across test_netguard (6), test_network_budget (6), test_http_client (8), test_tls (6); each command `python -m unittest discover -s tests -p <module>.py -v`, separate dev venv, exit 0. Real loopback TLS tests verify numeric connection, Host/SNI, untrusted/wrong-host certificate rejection, complete exact-byte verification and interruption of trickled headers before 2.5 seconds with a one-second budget. A clearly documented test-only transport maps the approved public fixture name to the ephemeral loopback TLS server; production validator never permits loopback. Committed server key/CA are disposable test material, not production trust. No production source/provider enabled or fetched.

Implementation test failures retained: Windows rejects negative Unix timestamps in the early fake clock cleanup range; use timezone-aware datetime subtraction instead. HTTPConnection has no context-manager protocol; tests now use closing(). Windows read-only file attributes blocked removal of a staged hardlink; immutable POSIX modes apply on Linux, Windows tests do not certify Linux permissions. Full Linux image, storage wiring, provider acceptance and live checks remain pending. No production change at this checkpoint.

## 2026-10-17T16:11:32.508653+00:00 — W5 checkpoint

Owner override applied before deployment: software payloads are external only (ADR 0002). Website runtime contains no local CAS, payload import, fetch-to-file, disk spool or payload backup code. Local code/small metadata/auth/operational DBs remain separate. The unpublished local-CAS prototype was withdrawn; original 22 research blobs and deployed preview data were not removed or changed.

W5 component: separate public/restricted ExternalRegistry SQLite metadata, safe exact digest/name identities, explicit license/provenance/classification/source approval, bounded no-disk full SHA-256+size verification, one-hour public redirect eligibility and fail-closed expiry. Public GET/HEAD redirects only registered approved public targets, with no-store/no-referrer. Private catalog requires live auth; private download is deliberately 503 after auth until a private external provider is accepted; anonymous known/unknown/method/Range/conditional paths uniformly deny. No public VPN navigation/rows/policy URLs. Rubika official upload/getFile workflow was checked, but no actual account/token/upload, retention/quota/Range/permission/domestic acceptance occurred; adapter remains disabled. External upload worker/scheduler and real approved artifact catalog remain pending.

Actual verification: locked offline Linux image build passed (21 hashed runtime wheels; separate locked test dependencies), then 95 tests passed, no skips, 118.113 s, network none/root read-only/nonroot/cap-drop/384 MiB/0.5 CPU. Three added Linux operational guards passed separately (0.011 s): old preview install/update refuse engine releases before Docker, password wrapper rejects pipe without echoing input. Current Windows suite: 98 total, 84 passed/14 Linux-only skipped, 8.708 s, exit 0. Original archived probe: 18/18 passed, exit 0. Browser local fixture: correct Persian login, existing dark/light palette and masked password input, mobile 390 px client/scroll both 390, no console warnings/errors; production credential not used. Screenshots are local outputs only. Auth schema-completeness regression was observed failing before fix, then passed; incomplete credential state now fails closed.

Linux test runner first failed because Docker's read-only tmpfs defaulted noexec, preventing fixture scripts/native libraries from running. Full original error log was inspected; only disposable test tmpfs was changed to explicit exec. No production mount/security change. First failure log retained privately on staged release; no success claim based on that failed run.

Staged release: /opt/tehnet-software/releases/engine-external-20261017, tested image sha256:c60ee70b474d82e409d6ab133ee8567106f354cbb880b82c4dcac58276ea471c. No engine live activation and no production password/source/artifact provisioned. Existing containers' names/IDs/images/ports and Nginx config+software snippet hashes matched before/after; live image remains sha256:54f507b987e5a252a6f207478ddd5bb6251c8889c1ed45657857be017e314352. Homepage/Learn/Services/Shop/Contact/software HTTP smoke passed. No WordPress/menu/Nginx change or unrelated restart in this work package.

Remaining deployment gates are explicit: encrypted consistent new metadata/auth backup and verified restore; new-state archive-only composition/activation/rollback including post-write reconciliation; archive-prefix private-log exclusion; owner-operated password setup; accepted external private backend, direct external upload worker and real provider measurements. Existing preview recovery scripts do not cover new auth state and now refuse engine releases. Under-30-minute Iran migration is NOT_ACCEPTED. W2/W3 component implementation is review-ready; W5 is partial and W6/W7 new-state acceptance remains open. See EXTERNAL_STORAGE.md, deployment/ENGINE_OPERATIONS.md and evidence/ENGINE_VALIDATION.md.

## 2026-10-17T16:24:44.175378+00:00 — final W2/W3/external-W5 verification

Final external-engine checkpoint: canonical URL syntax is now a separate function from real DNS/pinned transport; there is no production fixture resolver. Full final Linux suite passed 98/98, no skips/failures, 117.536 seconds, exit 0, final image sha256:b36c9957ad25882e2b552a4a84ec9f2aa8a7aecbb0a9e5284393d3b2c9df932f, stage /opt/tehnet-software/releases/engine-external-20261017-r2. Windows final 98 total/84 passed/14 Linux-only skips, 8.736 s, exit 0. Actual hidden getpass terminal flow passed in a disposable 192 MiB network-disabled container using test-only credentials, with no echo and no production auth mount. Live container/config preservation and six-route smoke passed. Original research 22 blobs/189734 bytes unchanged and 200 Markdown links verified. The earlier 95+3 Linux figures/image in historical checkpoints are superseded; new-state recovery/live activation, private external provider, Rubika and Iran migration remain unaccepted. No real software payload, production password or provider was provisioned. All work stays on the review branch; no main merge.
