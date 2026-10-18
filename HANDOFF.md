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

## 2026-10-18T14:26:22.503517+00:00 — live mirrors / qualification

Source qualification: official Alpine mirror index lists MobinHost in Tehran; its public archive explicitly offers files to visitors. Official Arvan Linux-repository page offers Ubuntu/Alpine downloads and Arch's official listing identifies the host as Iran. Actual valid-TLS HEAD on MobinHost Alpine minirootfs and Ubuntu hello, and Arvan Ubuntu hello, returned 200 with exact expected sizes and Accept-Ranges bytes. RIPE RDAP returned IR for actual peers 87.107.153.51 (87.107.152.0/23) and 185.143.233.132 (185.143.233.0/24, anycast). This is provider/registry country evidence, not domestic tariff, physical anycast location, Iranian-client reachability or outage acceptance. IranServer refused the tested connection; Pardisco timed out; IUT transport failed. None was enabled as fallback.

Independent Alpine official latest-releases metadata and .sha256 endpoints agree on version 3.24.2 x86_64/aarch64 minirootfs digest/size; Ubuntu's official package download page reports hello 2.10-3build1 amd64, 26006 bytes, e68cf4365b7aa9c4e2af4af6eee1710d6f967059b7b4af62786e8870d7366333. No native APK/APT installation/signature-chain acceptance is claimed. Only metadata was read; no payload was stored. Official Rubika methods page is reachable; owner confirms no token and requests hidden setup. Credential upload/download and retention cannot be accepted yet.

Operator metadata refresh tests: initial missing-module red confirmed; implementation initially exposed Windows fsync on a read-only descriptor (EBADF), complete traceback read and writable-descriptor fsync reproduction passed; staging descriptor changed to r+b. Five tests now pass (0.204s, exit 0), including real guarded fixture stream, atomic all-or-nothing publication, identity conflicts, preserved owner, no payload/staging residue and rejection of a verification peer outside reviewed public network allocations. This does not yet activate downloads or accept full Linux/sandbox/timer operation. Live active image/site/auth remain unchanged at this checkpoint.

## 2026-10-18T14:37:57.054032+00:00 — live mirrors / component-and-real-stream-tested

Linux full isolated operator/runtime suite passed 128/128, zero skips/failures, 27.319s, exit 0. Windows full run passed 104 with 24 Linux/GPG-only skips (128 total), 9.801s, exit 0; original archived probe 18/18, 0.002s. First Linux test packaging omitted TLS fixtures and one Git-path test assumed a real checkout; complete failures were read, disposable TLS fixtures included and the test made an explicit synthetic Git root. Rerun above passed; no production failure or website mutation occurred.

Actual staging qualification verified all 7755418 bytes across three exact public files in bounded-memory streams: Alpine 3.24.2 minirootfs x86_64 (3701382 bytes, 1.019s) and aarch64 (4028030 bytes, .971s) at MobinHost, GNU hello Ubuntu amd64 (26006 bytes, .634s) at Arvan. Full independent official SHA256/size match, valid TLS and approved RIPE allocation peers passed. Only public/external.sqlite and ops/network.sqlite appeared in qualification state; zero downloaded payload files. No live publication yet. Provider HEAD/Range/conditional and live sandbox/timer acceptance are next.

Rubika official bot API valid-TLS invalid-token request returned HTTP200, JSON object with non-OK status, 26 response bytes; this confirms transport/unauthenticated API reachability, not authentication or storage. Actual Linux PTY secret-setup fixture passed with no echo and mode0600, using a disposable public test token, removed with its temporary directory. Owner production token remains absent; upload/download and 24h/72h retention cannot be accepted. Twelve Rubika safety tests passed, including arbitrary/internal targets, redirects, caps, redaction, no file payload and credential-path rejection. The one focused reviewer found two P2 issues (secret elsewhere inside Git, case-normalized returned hostname disclosure); red tests reproduced both, fixes and regressions passed before packaging. Review did not operate real accounts. Backend remains disabled.

## 2026-10-18T14:41:55.938139+00:00 — live mirrors / active-public-metadata

Real provider qualification passed all three complete SHA256/size streams plus HEAD200, exact 16-byte Range206/Content-Range and conditional304 at the two approved hosts. Scoped installer then activated all three public metadata records without changing or restarting any container, Nginx configuration or WordPress. Backup: /root/tehnet-backups/20261018-144016-public-mirrors (consistent previous public registry and network metadata, private baseline fingerprints). Active engine image remains sha256:ab4220407e6a35a6e3d4221b44f238f12b25b1081be4b03ce8a92276a60289fa. All-container ID/image/port fingerprints and research/auth/restricted DB bytes plus both Nginx files matched before/after. Current five-DB recovery validator passed.

Actual protected systemd refresh service completed successfully before its 20-minute timer was enabled. It shares the engine operation lock, updates only public metadata/ops, keeps a read-only filesystem elsewhere and cannot access auth/restricted/research state. Full failed verification does not publish a partial registry; prior eligibility expires after one hour. Routine 7755418-byte refresh every20min is about558390096 bytes/day before bounded extra checks, within the 1GiB daily hard cap. Failed or repeated operator requests still consume quota; no payload cache, automatic foreign fallback or arbitrary URL registration. Only public pilot pins are committed; no private source policy/token/link is published.

Origin and independent client end-to-end redirect/full-byte checks are now running; they are not yet counted at this checkpoint. Timer/lock/final filesystem/browser checks and final publication remain. Rubika transport/hidden prompt fixture passed, but owner real token is absent; no actual upload/download, retention or website Rubika backend is accepted.

## 2026-10-18T14:54:25.234198+00:00 — live mirrors / accepted

Accepted scoped delivery: three live public files at https://tehnet.ir/software/#downloads, full trusted independent SHA256/size, TLS and provider HEAD200/Range206/conditional304. Both actual origin and independent Windows public-client paths verified TehNet GET/HEAD307 to the exact registered targets, then all real bytes without payload persistence. Baseline website/canonical/noindex/menu/assets/API checks and private denials passed; browser shows three real links and copyable hashes, no warning/error console entries. First Windows end-to-end attempt had an own-site TLS handshake timeout; a single unchanged bounded rerun passed. No verification/TLS/deadline weakening.

Actual sandboxed service passed; while the shared engine lock was held it returned75 and changed no verification stamps, then returned0 and advanced all three after unlock. Timer is enabled/active; both Monotonic properties were retrieved and the20-minute OnUnitActive trigger explicitly verified. All container fingerprints (including archive), both Nginx files and auth/restricted/research bytes preserved. Exactly five subsystem SQLite files, zero software payload files, no container or Nginx restart. Source audit matches all10 operator files to the deployed bytes and keeps the existing immutable web image/source unchanged (sha256:ab4220407e6a35a6e3d4221b44f238f12b25b1081be4b03ce8a92276a60289fa, healthy/read-only).

Final full Linux rerun:129/129,zero skips/failures,27.577s,exit0. Final Windows:129 total,105 passed,24 Linux/GPG-only skips,9.215s,exit0. Original probe18/18,0.002s. Secret-setup wrapper bash syntax and pipe refusal passed without creating a production token. A new red regression caught invalid/empty retention-record fallback to a new upload; strict record/date validation fixed it before final full tests. Initial final-test Bash pipe received CRLF and stopped at set before tests/mutations; binary LF transport fixed only the harness. The completed report resolved the intermediate missing-document link; source-copy verifier passed22 blobs/189734 bytes,273 Markdown links,existing website source files changed0,root coordination notes append-only.

Rubika: real valid-TLS invalid-token getMe returned a non-OK JSON response, actual hidden-terminal public-fixture setup passed0600/no echo, and13 safety tests passed. Owner real token remains absent; hidden setup/check helper installed. Actual credential upload/download,24/72h retention, quotas/permissions/deletion/recovery and VPN external delivery remain NOT_ACCEPTED, backend disabled. No chat/message send, personal session, production password change or scheduled Rubika follow-up. Future owner step: run the installed hidden-token helper; provider approval/retention needs its own subsequent actual evidence. Iran under30-minute migration and native offline installation also remain unaccepted. Exact current pins, backup /root/tehnet-backups/20261018-144016-public-mirrors and procedures are in PUBLIC_MIRRORS/RUBIKA_PILOT and evidence/LIVE_MIRRORS. Publish only existing review branch; predecessor cbedff35a5efdec3371daf16e4a968326aa9e47e, no main merge.

## 2026-10-18T15:07:05.920036+00:00 — catalog expansion / claimed-and-researched

Claimed W5-CATALOG-EXPANSION at predecessor 7828a5e8a45aa9b15114daf570be005a2d4e91be. Eight current official Ubuntu package identities/licenses researched; only metadata read. Planned 11-file total 17,066,942 bytes; 20-minute cadence would exceed existing quota, so bounded 30-minute schedule and pre-network budget checks are required before activation. Existing website/image/password/Rubika unchanged; actual mirror and rollback tests pending.

## 2026-10-18T15:11:49.247452+00:00 — catalog expansion / component-and-provider-tested

Official independent Ubuntu noble-updates package identities/copyrights recorded for Git, curl, jq, Python 3.12 minimal, pip, wget, rsync and OpenSSH client. Copyright documents for Wget and rsync explicitly refer to GPL-3 and linking exceptions; these unstructured documents do not use the DEP5 License field. Existing three manifest entries retain identical metadata/source/URL identities. No third provider or fallback enabled.

New bounded manifest tests first failed at old five-entry cap and missing scheduled-byte check; implementation now accepts at most12 and enforces <=80% of unchanged daily byte/request quotas before network. Windows harness initially lost its environment assignment through nested shell interpolation; switched to explicit subprocess environment. A new preservation fixture initially hit the intended one-second host backoff; advanced only its synthetic clock. Focused11/11 now pass (0.384s). Complete Windows135 total:111 passed,24 Linux/GPG-only skips,9.479s. Complete isolated Linux135/135 passed,zero skips/failures,28.228s.

Actual isolated full-stream qualification verified all11 files/17,066,942 bytes with exact independent SHA256/size, valid TLS and reviewed CIDR peers. Same real metadata was restored from11 rows to its empty snapshot; network usage remained charged and no payload/staging files remained. Provider-only acceptance then passed11 full hashes plus HEAD200, exact16-byte Range206/Content-Range and conditional304. Production catalog/site/auth remained untouched during qualification. Planned49 runs/day including startup:836,280,158 bytes and539 requests, below reserved80% thresholds; 30-minute refresh,150-second service,one-hour expiry,1GiB/1000 hard daily quotas retained. Scoped updater/rollback is under focused read-only review before production activation.

## 2026-10-18T15:14:39.974271+00:00 — catalog expansion / review-regressions-and-deployment-gate

The one focused static reviewer identified two updater rollback defects before live execution: failure immediately after database replacement could leave only the old fingerprint, and restoration command errors could still print success. Both were fixed: an exclusive/fsynced candidate fingerprint receipt is recorded before publication, rollback accepts only the exact old/candidate fingerprints, and every timer/service/unit restore step explicitly checks status. Unknown concurrent metadata remains rejected. No broad or duplicate review was performed.

Fresh failure-injection regressions execute a real publish-then-error and restore its exact previous metadata; Linux executes the actual rollback shell function with each of eight external steps failing, requires nonzero/no false PASS, and also tests the successful path. Fresh full Linux137/137 passed,zero skips/failures,28.159s; Windows137 total112 passed25 Linux/GPG/shell-only skipped,11.806s. Bash syntax and systemd-analyze verify passed. Original real provider qualification remains valid because pins/client/runtime are unchanged; new updater/operators are isolated from the active three-file pilot. Production activation is now the next scoped operation; no existing web source/container/Nginx/auth/Rubika change is authorized or required.

## 2026-10-18T15:16:33.645063+00:00 — catalog expansion / live-expanded

Scoped live updater activated11 public records at /software without changing/restarting Docker/Nginx/WordPress. The exact original3 metadata identities were checked before writing; previous public/network SQLite snapshots and exact unit files retained at /root/tehnet-backups/20261018-151445-catalog-expansion. Public registry published atomically after all complete hashes, with prepublication recovery receipt. Protected container/site/auth/restricted/research baselines matched after activation; current five-database recovery validator passed. Only public metadata/network counters and the owned mirror service/timer changed.

Actual new sandboxed service returned0. Timer uses30-minute cadence; service deadline150s for at most12 bounded10-second files plus serial host spacing. Hard1GiB/1000 daily quotas unchanged. Existing hidden Rubika helper remains at its original operator path; owner token/password not created. Origin/independent-client end-to-end and final filesystem/source/browser checks are running and not yet counted at this checkpoint.

## 2026-10-18T15:22:13.197426+00:00 — catalog expansion / accepted-live-delivery-and-recovery

Accepted live11 files including8 useful Ubuntu24.04 Linux/development tools. Origin and independent Windows public TLS each verified all17,066,942 bytes/full hashes/sizes,GET/HEAD307 exact no-store redirects,providerHEAD200/Range206/conditional304 and existing website/private denial checks. First independent attempt had own-site TLS EOF; complete failure retained,one unchanged bounded rerun passed. Browser displays new cards in existing palette,no warning/error logs; screenshot saved. Existing guide copy contains one historical not-active sentence,tracked as separate frontend wording work; no template/web-image change in this metadata-only task.

Actual production-snapshot metadata rehearsal11→3→11 passed0.020s with concurrent-edit refusal and unchanged live registry/budget. Actual shared lock75 preserved11 stamps,unlocked service0 advancedall11. Timer active/enabled30min;service150s/192MiB/strict sandbox. Current exact fiveDB state,no software payload/cache/spool. All container fingerprints,Nginx/auth/restricted/research bytes and unchanged active image/runtime source hashes verified. Audit harness initially missed CRLF normalization; corrected to existing manifest contract and passed,without runtime edits. Linux137/137,Windows112pass25platformskips;fresh source-copy/link/staged-ref verification and original probe run next. No Rubika/password/VPN/offline-Iran acceptance change. Current backup /root/tehnet-backups/20261018-151445-catalog-expansion. Publish existing review branch only; no merge to main. Full task/evidence and current copy/paste/operator docs updated.

## 2026-10-18T15:23:35.449372+00:00 — catalog expansion / final-publication-gate

Final publication gate: source-copy/link/isolation verifier passed22 exact attributed blobs/189734bytes/296 local Markdown links,unchanged original3 pins,existing website source changes0 and append-only root notes. Original upstream probe18/18,0.002s,exit0. Full relevant implementation diff reviewed against the accepted deployed source hashes; new task/status/changelog/rollback/client instructions and known limits reconciled. Final staged whitespace/credential/path check and exact remote branch/main comparison precede publication completion. Predecessor7828a5e8a45aa9b15114daf570be005a2d4e91be; use Git history for this commit ref,not a self-referential hash.

## 2026-10-18T15:25:19.682290+00:00 — catalog expansion / staged-gate-passed

Final staged gate passed36 scoped paths,whitespace clean,no credential heuristic matches,all8 staged operator hashes equal deployed bytes,and client copy/paste example bash syntax0 (installation not executed). Final link/provenance rerun passed22 blobs189734bytes297 links,existing website source changes0. No runtime changed after accepted checks. Commit/push existing review branch and verify remote refs; preserve DraftPR2 and main.
