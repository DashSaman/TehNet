# TehNet Execution Progress

## Current phase / فاز فعلی
- **FA:** زیرساخت WooCommerce، کاتالوگ Shop و جریان استعلام محصولات فیزیکی در production پیاده‌سازی و live-verified شده‌اند؛ سایت همچنان عمداً noindex است. فاز بعدی پیشنهادی، چرخه دستی Quote/Invoice برای همین inquiryهاست.
- **EN:** WooCommerce catalog foundations and the physical-product inquiry flow are implemented and live-verified in production while the site intentionally remains noindex. The next proposed phase is the manual Quote/Invoice lifecycle for these inquiries.

## Product decisions locked
- Brand/domain: TehNet / تهران نتورک / `https://tehnet.ir`
- Primary market/language: Iran / Persian
- On-site services: Tehran; Remote Support: nationwide Iran
- Current address: تهران، آیت‌الله کاشانی، شاهین جنوبی
- Current phone: 021-91018746
- Product model: Learn + Lab + Services + Shop
- Stack: WordPress + WooCommerce with custom TehNet theme and TehNet Core plugin
- Editing: Gutenberg/custom blocks; routine changes from WordPress admin
- Education: free in phase 1
- Physical products: inquiry/manual quote initially
- Digital products: download-only and licensed
- Support target: website tickets + two-way Telegram
- Rial gateway: intentionally undecided
- Crypto target: NoPayments after official integration verification
- SEO evidence framework: `DashSaman/-SEO`

## Completed and verified
- Product discovery, architecture spec, agent contract, roadmap and backlog.
- Safe production baseline, backup/recovery policy and isolated branch/worktree workflow.
- Persian RTL TehNet theme and `tehnet-core` settings/content-model foundation.
- WordPress installed/configured at `tehnet.ir`, locale `fa_IR`, editable Gutenberg pages/menu seeded.
- TehNet remains bound only to `127.0.0.1:18082`; unrelated services are protected by fingerprint checks.
- Persian query universe and dated SERP intent map created without fabricated Iran Volume/KD.
- Stable information architecture and internal-linking rules defined for Learn/Lab/Services/Shop.
- `/services/` and `/lab/` archive collisions removed while preserving single-item rewrites.
- Normal pages and homepage templates now enforce a single-H1 model.
- Existing top-level pages reseeded idempotently; WP-CLI Persian menu lookup regression fixed with tested CSV parser.
- Live routes `/`, `/learn/`, `/lab/`, `/services/`, `/shop/`, `/about/`, `/contact/` each returned HTTP 200 with exactly one H1 and correct canonical.
- `blog_public=0` and rendered `noindex,nofollow` remain active; indexing was not enabled.
- Core sitemap currently returns 404 while non-public; current `robots.txt` only protects `/wp-admin/`, which is documented rather than guessed.
- Fresh SEO-phase recovery point: `/root/tehnet-backups/20260915-011313`.
- Non-TehNet runtime fingerprint matched exactly before/after SEO deployment.
- Public YouTube inventory captured with 33 current videos and stable video IDs; every video is mapped exactly once to `OWNER`, `NOT-YET`, `YOUTUBE-ONLY` or `DEPRECATED`.
- Off-topic iPhone items remain YouTube-only; the explicitly old Cloudflare 1101 video is marked deprecated instead of receiving an SEO page.
- First substantial Learn owner `/learn/mikrotik/` is live, editable in Gutenberg, and includes original learning-path guidance plus verified TehNet videos.
- `/learn/mikrotik/` returned HTTP 200, exactly one H1, canonical `https://tehnet.ir/learn/mikrotik/`, and `noindex,nofollow`.
- Fresh content-phase recovery point: `/root/tehnet-backups/20260915-012653`.
- Non-TehNet runtime fingerprint remained exactly unchanged during the content seed.
- Five approved service owners are live: `/services/network-tehran/`, `/services/network-support-tehran/`, `/services/network-setup-tehran/`, `/services/mikrotik-tehran/`, `/services/remote-support/`.
- All five service owners returned HTTP 200 at origin and through Cloudflare with exactly one H1, correct canonical and `noindex,nofollow`.
- `/services/` now links to all five owner pages and remains editable in Gutenberg.
- A production 404 caused by the legacy `tn_service` rewrite collision was reproduced, covered by regression tests and fixed by disabling that unused pretty rewrite.
- Fresh recovery points: `/root/tehnet-backups/20260921-005938` and `/root/tehnet-backups/20260921-010347`.
- Non-TehNet runtime topology remained unchanged throughout the Services deployment.
- Centralized LocalBusiness JSON-LD is live on homepage, About, Contact, Services hub and all five service owners, with truthful NAP/service-area values and no fabricated ratings/hours/geo.
- LocalBusiness JSON is intentionally absent from `/learn/mikrotik/`; `BLOG_PUBLIC=0` and rendered `noindex,nofollow` remain active.
- LocalBusiness recovery point: `/root/tehnet-backups/20260921-011103`; non-TehNet topology remained unchanged.
- `/learn/mikrotik/mtcna/` is live and verified at origin/public with one H1, correct canonical, noindex/nofollow, all eight mapped MTCNA/GNS3 videos and required internal links.
- MTCNA recovery point: `/root/tehnet-backups/20260921-011812`; non-TehNet topology remained unchanged.
- Fresh SERP review supports the MTCNA owner but not generic VPN/Linux hubs yet; those remain NOT-YET rather than creating thin/cannibalizing pages.
- **FA:** WooCommerce `11.1.1` فعال است؛ `/shop/` و `/shop/mikrotik-routers/` در Public/Origin با HTTP 200، یک H1، canonical صحیح و `noindex,nofollow` تأیید شدند.
- **EN:** WooCommerce `11.1.1` is active; `/shop/` and `/shop/mikrotik-routers/` were verified at public edge and origin with HTTP 200, one H1, exact canonical and `noindex,nofollow`.
- **FA:** Cart/Checkout/My Account و تمام gatewayهای داخلی غیرفعال‌اند؛ smoke استعلام PASS شد و بعد از cleanup تعداد product و inquiry موقت صفر است.
- **EN:** Cart/Checkout/My Account and all built-in gateways are disabled; the inquiry smoke passed and cleanup left zero temporary products/inquiries.
- **FA/EN:** Shop recovery point / نقطه بازیابی فروشگاه: `/root/tehnet-backups/20260921-021149`; non-TehNet runtime topology remained unchanged.

## Current production state
- Active theme: `tehnet`; active plugins: `tehnet-core` + WooCommerce `11.1.1`.
- Static editable homepage and primary navigation are live.
- Canonical host is `https://tehnet.ir`.
- Search indexing remains deliberately disabled until launch gates pass.
- No secret values are stored in Git.

## Next execution order
1. Design and implement the manual Quote/Invoice lifecycle for physical inquiries / طراحی و پیاده‌سازی چرخه دستی پیش‌فاکتور و فاکتور.
2. Implement account/support/ticket flows and Telegram bridge in separate tested branches.
3. Implement digital delivery/licensing and payment adapters only after provider requirements are verified.
4. Revisit VPN/Linux owner hubs only with independent intent evidence and substantial content.
5. Complete launch technical/content/measurement gates before enabling indexing.

## Rules for all agents
Read `AGENTS.md` and `HANDOFF.md` first, preserve locked decisions and verified work, use evidence before SEO claims, keep indexing disabled until an explicit launch gate, and never change unrelated project ports/containers during TehNet work.

## 2026-10-17 — Isolated TehNet Software Archive research/design handoff

Added `projects/software-hub/` with 22 provenance-traced Linux research copies, entry guide, roadmap, privacy/agent/task contracts and migration design with a synthetic local rehearsal. OFFLINE_SOFTWARE_CATALOG is missing from inspected source history and awaits its original ZIP/patch. No WordPress/theme/plugin/content/ops/runtime configuration was changed or deployed. Fresh checks and precise limits: `projects/software-hub/evidence/VALIDATION.md`. Existing production statements above are historical and were not revalidated by this work.

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
