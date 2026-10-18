# TehNet Agent Handoff

## Current state
**FA:** Foundation، WordPress، SEO، Learn/Services، LocalBusiness و اکنون WooCommerce catalog + physical inquiry در production پیاده‌سازی و تأیید شده‌اند؛ سایت عمداً non-indexable باقی مانده است.

**EN:** Foundation, WordPress, SEO, Learn/Services, LocalBusiness, and now the WooCommerce catalog + physical inquiry flow are implemented and verified in production. The site intentionally remains non-indexable.

## Read first
1. `AGENTS.md`
2. `PROGRESS.md`
3. `docs/superpowers/specs/2026-09-14-tehnet-platform-design.md`
4. `docs/superpowers/plans/2026-09-15-tehnet-seo-architecture.md`
5. `seo/QUERY_UNIVERSE_FA.md`
6. `seo/SERP_INTENT_MAP_FA.md`
7. `seo/INFORMATION_ARCHITECTURE_FA.md`
8. `seo/TECHNICAL_SEO_BASELINE.md`
9. `seo/YOUTUBE_INVENTORY_FA.md`
10. `seo/YOUTUBE_CONTENT_MAP_FA.md`
11. `docs/superpowers/plans/2026-09-15-tehnet-youtube-content-mapping.md`
12. `TASKS.md`

## Verified production
- Domain: `https://tehnet.ir`
- TehNet host binding: `127.0.0.1:18082`
- Active theme/plugin: `tehnet` / `tehnet-core`
- Main top-level routes return HTTP 200, one H1 each, correct canonicals and `noindex,nofollow`.
- `blog_public=0`; do not enable indexing yet.
- `/wp-sitemap.xml` currently returns 404 while non-public.
- Fresh recovery point: `/root/tehnet-backups/20260915-012653`.
- Non-TehNet runtime fingerprint remained unchanged across SEO deployment.
- `/learn/mikrotik/` is live and returned HTTP 200 with exactly one H1, correct canonical and `noindex,nofollow`.
- Current public YouTube inventory contains 33 mapped videos; no thin per-video site pages were created.
- Five Services owner URLs are live and verified: `/services/network-tehran/`, `/services/network-support-tehran/`, `/services/network-setup-tehran/`, `/services/mikrotik-tehran/`, `/services/remote-support/`.
- Each service owner returns HTTP 200 at origin and through Cloudflare, exactly one H1, correct canonical and `noindex,nofollow`.
- The legacy `tn_service` rewrite was disabled because it captured `/services/<slug>/` before hierarchical Pages; production currently has zero `tn_service` posts.
- Services-phase recovery points: `/root/tehnet-backups/20260921-005938` and `/root/tehnet-backups/20260921-010347`.
- Centralized LocalBusiness JSON-LD is live and validated on identity/service pages; recovery point `/root/tehnet-backups/20260921-011103`.
- LocalBusiness output uses current `areaServed`, E.164-style phone normalization, stable `@id`, PostalAddress and known YouTube `sameAs`; no unverified rating/hours/geo/postal code is emitted.
- `/learn/mikrotik/mtcna/` is live and verified at both origin and public edge with HTTP 200, one H1, correct canonical, `noindex,nofollow`, all eight mapped MTCNA/GNS3 videos and required internal links.
- MTCNA recovery point: `/root/tehnet-backups/20260921-011812`; non-TehNet runtime topology remained unchanged.
- `/learn/mikrotik/mtcna/` is live-verified with all mapped MTCNA/GNS3 videos; recovery point `/root/tehnet-backups/20260921-011812`.
- Current SERP evidence does not justify generic `/learn/vpn/` or `/learn/linux/` hubs yet; keep them NOT-YET until a dedicated intent-backed plan exists.
- **FA:** WooCommerce `11.1.1` فعال است؛ Shop page ID `9`، currency=`IRR`، Cart/Checkout/My Account=`0` و `bacs/cheque/cod=no`.
- **EN:** WooCommerce `11.1.1` is active; Shop page ID is `9`, currency is `IRR`, Cart/Checkout/My Account are `0`, and `bacs/cheque/cod=no`.
- **FA/EN:** `/shop/` + `/shop/mikrotik-routers/` passed public/origin route, H1, canonical and noindex gates; inquiry smoke and cleanup passed.
- **FA/EN:** Shop recovery point / نقطه بازیابی: `/root/tehnet-backups/20260921-021149`; no real/fake product remains and non-TehNet topology is unchanged.

## SEO architecture locked
- `/learn/`, `/lab/`, `/services/`, `/shop/` are separate journeys.
- First-priority Learn owner: `/learn/mikrotik/`.
- Service owners include `/services/network-tehran/`, `/services/network-support-tehran/`, `/services/network-setup-tehran/`, `/services/mikrotik-tehran/`, `/services/remote-support/`.
- Shop intent belongs to category/product pages, not tutorials.
- No auto-generated thin pages per YouTube video and no fake district/city doorway pages.

## Important implementation facts
- `tn_service` and `tn_lab` archives are disabled. The unused `tn_service` pretty rewrite is also disabled because it collided with `/services/*` Page owners; the Lab rewrite remains nested under `/lab/`.
- `page.php` owns the H1 for normal pages; `front-page.php` leaves the editorial homepage H1 to page content.
- WP-CLI used here has no `wp menu get`; Persian menu discovery uses the tested `ops/lib/wp-menu-id.awk` parser.
- Current `robots.txt` only disallows `/wp-admin/`; actual prelaunch index blocking is the rendered meta robots plus `blog_public=0`.

## Exact next task
**FA:** برای **Manual Quote/Invoice lifecycle** یک branch/plan ایزوله جدید بساز؛ inquiryهای موجود را به وضعیت‌های قابل‌پیگیری و پیش‌فاکتور/فاکتور دستی وصل کن، بدون فعال‌کردن payment یا indexing.

**EN:** Create a new isolated branch/plan for the **manual Quote/Invoice lifecycle**; connect existing inquiries to trackable quote/invoice states without enabling payment or indexing.

## Safety
Do not change port `18082`, Nginx routing, Docker project topology or unrelated services. Before each production content/code deployment, capture a fresh TehNet backup and compare the non-TehNet runtime fingerprint before/after.

## Still unresolved
- Rial gateway provider.
- NoPayments official API/webhook implementation details.
- Final optional logo redesign (must be previewed before replacement).
- Search Console connection/measurement and final launch-indexing approval.

## Separate workstream: TehNet Software Archive (2026-10-17)

Read `projects/software-hub/README.md`, `AGENTS.md` and `STATUS.md`. Consolidation/design is isolated from the existing Quote/Invoice priority. Next TehNet Software Archive actions: acquire original OFFLINE_SOFTWARE_CATALOG ZIP/patch and checksums, then freeze W0 contracts for the proposed `/software/` subsystem. Public catalog/private VPN separation, initial foreign-VPS subpath and measured prepared-target migration to Iran are requirements, not live features. No production access/deployment or real migration acceptance occurred in this delivery.

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

## 2026-10-18T13:48:56.689733+00:00 — engine activation / implementation

Implemented versioned metadata/config encrypted backup and new-directory-only restore. Initial red test failed on missing recovery module; after implementation Windows contract checks passed (2 passed, 4 real-GPG checks then skipped; Linux acceptance pending). Strict manifest/path/size/member allowlist, actual SQLite schema/integrity/semantic checks, trusted ciphertext digest, AES256 GPG decryption+MDC statuses, session/lease invalidation, exclusive backup output and no payload archive. One focused read-only reviewer found no concrete issue in assigned recovery code; it did not execute tests. Deployment implements scoped code rollback retaining newer state and privacy-safe snippet rollback order; actual shell/crypto tests pending. Owner password not generated/configured and live site still unchanged.

Owner-key protection: native PowerShell script execution was disabled locally. No execution-policy or authentication settings were changed; the same operation uses native Windows DPAPI via Python ctypes and a current-owner/SYSTEM-only directory ACL. No key bytes enter Git/output. Server key preparation and protected independent copy are not yet accepted at this checkpoint.

## 2026-10-18T13:55:12.567519+00:00 — engine activation / recovery-tested

Linux GPG 2.4.4 recovery suite now passes 8/8 tests (1.775 s, exit 0): actual encrypted roundtrip and credential preservation, restored session invalidation, corrupt ciphertext, plaintext OpenPGP --store packets, independently trusted ciphertext digest, exclusive output/writer-freeze, strict manifests and actual schema completeness. Windows contract parser tests also passed, with real-GPG tests correctly skipped there. The first Linux roundtrip failed closed: GPG chose AES256-OCB (DECRYPTION_INFO 0 9 2), while the initial parser required legacy MDC mode. Complete test-only diagnostic was read; official GnuPG DETAILS/manual confirmed AEAD/MDC status semantics and obsolete --force-mdc. Parser now accepts only AES256 with verified MDC or OCB, DECRYPTION_OKAY+GOODMDC+exit0, and trusted ciphertext hash. No TLS/decryption integrity check was disabled. References: https://github.com/gpg/gnupg/blob/master/doc/DETAILS and https://gnupg.org/documentation/manuals/gnupg24/gpg.1.html.

Initial isolated dependency install failed because the container's UID 10001 could not write the new root-owned release/host-site directory; complete pip failure was inspected. Installation reran as root only inside a network-disabled/read-only disposable container writing that new dependency directory; no host-global installation or production permission change. Independent owner key copy passed transferred SHA256 and native CurrentUser DPAPI roundtrip under owner/SYSTEM-only Windows ACL; raw local key export was removed after verification. No production password was generated/configured. Deployment shell tests are still pending at this checkpoint; live preview unchanged.

## 2026-10-18T13:59:22.917177+00:00 — engine activation / deployment-tested

Final Linux full suite passed 111/111, zero skips/failures, 27.552 seconds, exit 0. Includes 8 recovery/real-GPG tests and 5 actual-shell isolated deployment scenarios: success, rehearsal rollback, partial replacement failure, backup failure, SIGTERM; new state writes retained and other website configuration unchanged in fixtures. Both shell scripts passed bash -n. New runtime rebuilt offline from locked dependencies. All five actual production metadata databases were explicitly initialized/validated; no password was set. Current production remains the previous preview until the next live rehearsal.

Independent owner recovery key was roundtrip-verified under Windows CurrentUser DPAPI and restrictive owner/SYSTEM ACL, then privately exported once and reimported into a fresh server GPG home whose fingerprint matched the public recipient. Temporary plaintext exports were removed from both endpoints after successful import; original server bootstrap key and temporary imported key still await cleanup after live acceptance. Failed first key transfer tried to use a directory whose creation followed the pending test run; after the test completed, transfer/import succeeded. No secret bytes were printed or committed. Real same-host encrypted recovery/rollback and final activation remain the next gate, not yet claimed.

## 2026-10-18T14:00:40.168413+00:00 — engine activation / real-recovery-and-rollback

Actual authorized same-host production-prefix rehearsal passed. Fresh whole-site backup plus encrypted five-DB/config backup were created privately at /root/tehnet-backups/20261018-135929-software-engine-rehearse. Using the recovery key freshly imported from the independently protected owner copy, ciphertext digest/GPG integrity/schema/semantics were validated and restored into a separate staging directory. The restored state booted in a nonroot read-only container with network none; original archive container was stopped, avoiding a second active auth writer. New engine was then served through /software and returned to the exact previous preview image/composition/snippet. ROLLBACK_PASS state_preserved=true elapsed_seconds=12; byte hashes of all five active databases matched before/after. Other containers' IDs/images/ports, main Nginx site file, and six website routes passed preservation checks. The software prefix briefly returned 502 during each archive container replacement; no zero-downtime claim. No owner password, real external source or payload was provisioned. Final activation is next; real Iran migration remains NOT_ACCEPTED.

## 2026-10-18T14:02:10.726350+00:00 — engine activation / active

Authorized final /software engine activation passed in 8 seconds after preparation/fresh whole-site backup. Exact active image: sha256:ab4220407e6a35a6e3d4221b44f238f12b25b1081be4b03ce8a92276a60289fa. Release /opt/tehnet-software/releases/engine-active-20261018. Private backup /root/tehnet-backups/20261018-140051-software-engine-activate includes encrypted engine state/config and successful staged recovery/isolated boot. All five active DB byte hashes matched before/after. Only tehnet-software was recreated; other container identities/images/ports and main Nginx site configuration matched. The archive snippet alone changed to disable access/error request logging, disk buffering and caching. WordPress routes passed origin HTTP smoke. The archive prefix briefly returned 502 during replacement; no zero-downtime claim. Owner password remains unset; private routes deny and no real software/provider is activated. Independent public TLS verification, off-server ciphertext copy and removal of temporary server secret keys are in progress, not yet accepted at this checkpoint.

## 2026-10-18T14:16:08.239621+00:00 — engine activation / accepted

Scoped task accepted: engine remains healthy at https://tehnet.ir/software/ on immutable image sha256:ab4220407e6a35a6e3d4221b44f238f12b25b1081be4b03ce8a92276a60289fa, release /opt/tehnet-software/releases/engine-active-20261018. Real encrypted recovery/isolated boot/exact previous-code rollback passed in 12 seconds; final activation passed in 8 seconds after preparation. All five live DB bytes and other website container/config fingerprints were preserved. Zero software payload files; root/research/external registry mounts read-only, auth-only writable persistence. Owner password remains deliberately unset; private paths fail closed. No production password or real provider was provisioned.

Final checks: Linux full suite 111/111, zero skipped/failed (27.552 s); real GPG recovery 8/8 and actual shell fault flow 5/5. Windows full rerun: 111 total, 87 passed, 24 Linux/GPG-only skipped, 9.056 s, exit 0. Original research tests 18/18. Origin and independent valid-TLS public checks passed 19 each; browser shows owner-setup message without console warnings/errors. Final immutable runtime source hashes match recorded tested inputs; 22 original blobs/189734 bytes unchanged, 234 Markdown links valid, existing website source files changed 0, root coordination notes append-only; diff whitespace check exit 0. Current image healthy/read-only confirmed again over SSH.

Independent owner ciphertext copy (215529 bytes) matches trusted separately kept SHA256. CurrentUser DPAPI recovery key is outside Git under owner/SYSTEM-only ACL; actual recovery used its separately imported temporary key. Bootstrap/import server secret keys and agents were removed and key files verified absent; only public recipient persists. Owner Windows account/profile is required to recover the DPAPI-protected key for future restore; do not assume DPAPI copy alone is portable. No automatic scheduled backup was requested or created.

Documentation now points to current active evidence; staged/preview reports remain historical. Real Iran/WAN/DNS migration under 30 minutes, authenticated external private delivery, Rubika/provider permission/retention and APT offline installation remain NOT_ACCEPTED. Same-host timings exclude initial installation/key/whole-site backup preparation; archive briefly returned 502 during replacement. Post-write cross-host reconciliation and power-loss recovery are separate documented limitations. Branch publication only, no main merge; predecessor/base e35ce964d7a9a25b496cafa1ede52d4b168a5bc5.

## 2026-10-18T14:17:40.845387+00:00 — engine activation / publication-verified

Final publication gate: read-only SSH audit confirmed the exact healthy/read-only active image and equality of every app/templates/static file hash inside the running container with active-runtime-source.json and local source. Independently kept ciphertext hash matches; server temporary secret-key directories are empty and public recipient exists. Final public TLS rerun passed 19 checks. Staged whitespace check initially detected only Compose progress-line trailing spaces in the new evidence logs; sanitized copies were trimmed without changing text/results, and the complete staged check then passed (exit 0). Original private logs remain untouched. Source-copy/link verifier passed 22 blobs, 189734 bytes, 237 links, no existing website source changes and append-only root notes. No runtime changed after accepted Linux tests/activation. Ready to commit/push only the existing review branch; main remains outside scope.
