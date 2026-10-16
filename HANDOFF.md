# TehNet Agent Handoff

## CURRENT — universal shop template and product controls, 2026-10-16

Store0.4.0 is published through a nine-file Store-only allowlist. Live `/shop/` and every native current/future Woo product inherit responsive cards, graphic taxonomy navigation, compact expandable technical filters, SKU/category identity, toggleable compare/wishlist and gallery/details layout. Reviewed exact-MPN models inherit shared mouse/touch/zoom/auto-rotation/fullscreen/reset controls and existing documented exploded parts. Spin and approved photo overlays no longer require imported source IDs. JSON part storage now uses wp_slash to survive actual WordPress Unicode/quotation unslashing; unit stubs reproduce the real boundary.

Latest runtime map is `qa/shop-ux-2026-10-16/release.json` (22 reconciled paths,9 changed); release `/root/tehnet-releases/shop-experience-20261016-0aeb95218702`, fresh full backup `/root/tehnet-backups/20261016-190351-store-review`, SHA verified. Native before/after product bodies/all meta, home/menu8, settings/orders/commerce gates are equal. No migrations or media assignments. All25 products are inquiry-only;0 approved real GLB/spin, noindex remains. Do not replay broader old deployers or old image imports.

Read `docs/research/shop-experience-2026-10-16.fa.md`, `docs/shop-experience-operations.fa.md` and final `qa/shop-ux-2026-10-16/verification.json`. Fresh isolated native tests:27 shop and20 synthetic future-product mouse/CDP-touch/model checks; local23photo/31evidence/43metadata/11MTU plus19 synthetic renderer checks. Final production receipts have their own status/time; only a passed receipt proves its result. Four actual competitor visual samples; B&H browser403, prior120-domain survey remains limited.

Private clone `/root/tehnet-ux-preview-20261016`, internal Docker network, web172.18.0.3:80 through localhost18085 SSH; mail/HTTP/cron/payment blocked, DB tmpfs ephemeral, do not restart/reset casually. Hidden synthetic product189 is accessible within the clone/Store API and must never be copied to production. Native exact-product validation passed using this explicitly educational fixture, not real SKU CAD. Long SSH tunnel stalled; renewed with keepalive/IPQoS=none. Public browser transport defaults also failed; HTTP1-only test flags are recorded, no production Cloudflare/network settings changed. One focused native read-only mapper used; no GLM/new paid API.

PUBLIC ACCEPTANCE LIMIT: final production browser run completed12 functional assertions, then Persian-SKU navigation exceeded90s. Do not call the full27 production suite passed. Legacy live-store rerun timed out at tn-account; chained photo/remediation suites did not run; their old passed receipts retain historical dates. Current public HTTP/API/HTML proof is separate in `production/public-http.json`, through actual public Cloudflare HTTPS from managed host. Curl follows the Persian query302 to correct product200. Final verifier records `verified-with-production-browser-limit`; it is not an assertion that every attempted test passed. Next meaningful QA is the remaining public browser paths once this client route is stable; no rollback/data rewrite follows merely from this transport timeout.

## CURRENT — explicit interactive3D controls, 2026-10-16

Owner requested visible rotation/inspection. Local demo now has a prominent3D entrance, gesture guide, zoom buttons, opt-in auto-rotation/stop, fullscreen/exit and full camera reset. Direct link: `http://localhost:18084/?view=3d`. Ordinary URL still starts with real photographs; production remains unchanged. Demo-only controller `ops/visuals/cable-controls.js` uses the existing self-hosted model-viewer4.4.0. Hidden panels/background and reduced-motion changes stop auto-rotation; reduced motion disables its button. Fullscreen is offered where supported, with a fallback message on denial.

Fresh26 actual mouse/CDP-touch checks plus30 base browser and12 GLB/photo checks pass. Evidence and inspected desktop/mobile/fullscreen screenshots: `qa/product-visuals-2026-10-16/interaction/`. Mouse rotation/pan, two-finger pinch/pan, zoom projection, native turntable yaw and portrait reset were exercised. Reset must restore declarative `fieldOfView` (initially auto), request its update, await updateComplete and the asynchronous jump before recomputing bounds; using a stale live FoV made portrait reset too small. GLB and actual photo bytes are unchanged; exact-SKU/CAD limitations below remain. No GLM/new paid API or production release in this step.

## CURRENT — real-photo-first local preview, 2026-10-16

Owner requested real/natural imagery and inspiration from public 3D model sites while reviewing localhost18084. `ops/build-exploded-demo.py` now builds two unchanged, checksummed public-domain real Cat7 reference photographs, visible source/credit/download, explicit photo/model switch and improved original PBR cable geometry. These are independent educational photographs, not TehNet SKU images or a360 sequence; normalized geometry is not exact product CAD or a reconstruction of either photo. Source-catalog photographic origin and exact model identity remain unverified. No production runtime/content/settings changed in this step.

Read `docs/research/product-visuals-2026-10-16.fa.md` and `content/media/educational-cable-reference/provenance.json`. Sketchfab PolyCab public poster was visually inspected; its full interactive model failed to render and no geometry/textures or reuse license were obtained. Do not imply otherwise. New demo has woven filament geometry, foil surface variation, four coloured pairs/striped white insulation, capped curved sweeps, studio lighting, bounds-based framing and unchanged shared production renderer. No real micron/material claims.

Fresh checks:30 browser +12 independent GLB/photo checks; evidence and inspected screenshots in `qa/product-visuals-2026-10-16/`. Build with `rtk proxy python ops/build-exploded-demo.py --out ../../outputs/tehnet-parts-demo`, serve only that output directory on127.0.0.1:18084. Next exact action for live catalogue remains evidence-backed same-MPN photographic/CAD matching; do not assign this generic demo to an actual SKU. Prior live SEO/commerce/media release facts below remain current. No GLM/new paid API or production deployment occurred here.

## CURRENT — remediation and exploded-parts capability published, 2026-10-16

Supersedes historical audit/prepared/connection-blocked notes below. Read `seo/SITE_REMEDIATION_2026-10-16.fa.md`, `seo/remediation-2026-10-16/verification.json`, release receipts and `docs/site-remediation-operations.fa.md`.55 native published items/12 terms;75 crawl records,70 unique successful pages, each with exactly one description/OG image/H1/canonical and deliberate noindex.25 unique product bodies/titles. Homepage body,8-link menu,all product metadata,orders and commercial gates preserved by native before/after fingerprints. Metadata is deployed, not merely prepared. Sample Page2 is draft; new methodology187 and MTU188 are public; Woo109/110 titles repaired.

Store0.3.0 now has staff-reviewed native GLB, MPN/source/license/SHA checks, named animation/node validation, per-part material/measurement/source documentation, explode/assemble/slider/part selection and camera framing.30 media policy contracts,19 synthetic browser checks,11 educational cable demo checks; fresh25 production remediation checks plus14 shop and18 photo checks. No live product has an approved model, complete spin or parts document. The original parametric educational demo is explicitly not product CAD and has no real micron values. Build with `ops/build-exploded-demo.py --out PATH`; serve the result over localhost HTTP. Do not publish it as a real SKU or infer material/dimensions from a photograph.

Latest allowlist file receipt is `seo/remediation-2026-10-16/release-followup.json`; original content journal/full backup remain private at server paths in receipts. Directory permission and light-footer failures were diagnosed, fixed and publicly retested. New directories must be0755/www-data; private backup/release directories stay0700. Do not replay older import/fingerprint rollback or original full-site deployers over this release. Preserve noindex until separate owner launch approval; candidate paths are prepared only. GSC/Ahrefs plan limitations, exact-stock identity/CAD licensing and real ERP/payment prerequisites remain open. No external messages/posts, real orders/payments/router changes or AI endorsement measurements were made.

## READ FIRST — whole-site SEO/AI/product-view audit, 2026-10-16

Read `seo/SITE_AUDIT_2026-10-16.fa.md` and `seo/audit-2026-10-16/verification.json`. This task audited, documented and tested; it made no production content/settings/index/WAF/payment changes or external posts. Native inventory:54 published posts/pages/products,12 terms. Crawl:74 requests,73 final200 responses,69 unique successful pages; all69 noindex deliberately,68 lack descriptions, all69 lack OG data. Metadata MU-plugin remains absent on server; existing prepared source passes33 tests but excludes product/post/archive and has no OG image. Installing it alone will not close the audit.

All25 products share one182-character stored body;6 pairs share titles. Zero registered/reviewed spin sequences; current viewer's16 contracts and synthetic spin UI pass, not evidence of real3D. Home/product mobile Lighthouse performance98/95, SEO61/61; no field CrUX. Seven rendered templates show no overflow. GSC payment_required and Ahrefs AI Insufficient plan; rankings/citations/backlinks remain unmeasured. Community searches/contributions are research only; no messages sent. Original MyTel and local -SEO SOP read as dated sources; no private backups copied.

Next exact implementation action: plan/extend one metadata owner across approved templates with editable descriptions and verified OG images, preserve noindex and stable URLs, then validate/backup/allowlist-deploy under the applicable authorization. Separately verify physical MPNs and collect one real360 pilot. Correct the Safe Mode absolute claim against official docs; improve Learn/Lab and methodology. Do not fabricate Product offers/reviews, models, external endorsements or AI recommendation metrics. Full findings A01–A14 and acceptance criteria are in the report. Existing commerce/backup/media state below is unchanged.

## READ FIRST — catalogue cleanup live, 2026-10-16

Current source branch is `feat/store-payment-sandbox-20261015`; older sections below are history. `/shop/` has25 public inquiry products with30 image references. Owner explicitly authorized removal of their Saieed retailer lettering:15 cleaned lossless assets replaced references on11 products,14 skipped. Original assets and attachments remain. Built-in imagegen reconstructed only masked backgrounds; original RGB outside reviewed masks was restored and independently reproduced from committed transparent patches. Manufacturer labels/details remain; exact manufacturer-model matching and photographic origin are still unverified. Real360 remains0 products.

Native release receipt `tn_photo_cleanup_5918db794d83f97e`; fresh backup `/root/tehnet-backups/20261016-150644-store-review` checksums passed. Repeat apply changed0/skipped25; business fields, order count, homepage and theme snapshot unchanged. Evidence: `qa/store-2026-10-16/cleanup-apply.json`, `cleanup-pixel-verification.json`, `photo-verification.json`, `live-photos-browser.json` and `qa/store-2026-10-15/live-browser.json`. Run `python ops/release-catalog-photos.py rollback --cleanup` only if this media release needs reverting; it refuses later human edits and retains both versions. Do not run the older source-photo importer over the cleanup release.

Next exact action for commerce: obtain verified physical model/stock/price data and same-item real360 frames before claiming them. Production ERP/payment remain disabled. Local Docker WSL bootstrap fails `0xc00000fd`; do not reset or wipe it. Full Woo/ERP sandbox proof from15 October is historical, independent PHP/pixel and read-only production browser checks are current. Keep main Learn/Services, menu, noindex and unrelated services intact. See `PROJECT_STATUS.md` for the current overall state.

## Active store mission — 2026-10-15
وضعیت نسخه محلی: اتصال ERP و عملیات Woo، نقش‌ها، فاکتور و درخواست مرجوعی پیاده‌سازی و آزموده شده‌اند. docs/acceptance-matrix-fa.md، docs/testing.md و docs/user-guide-fa.md مبنای ادامه‌اند. همه ۲۵ قلم draft و بدون قیمت/موجودی واقعی‌اند. شاخه audit/store-readiness-20261015 از visual واقعی شروع شده؛ main و production تغییر نکرده‌اند. زرین‌پال انتخاب و پروتکل sandbox واقعی آزموده شد؛ آداپتور آزمایشی با 49 بررسی mock آماده ولی خاموش است. docs/payment-sandbox-fa.md شواهد و محدودیت Docker را ثبت می‌کند. هدف بعدی آزمون native gateway→ERP و checkout موبایل پس از رفع دسترسی Docker، مدارک و قیمت/stock واقعی، مالیات و credential تولید، سپس release دارای backup/restore تولید و تأیید صریح مالک است. ثبت یا ادعای پرداخت واقعی مجاز نیست.



## READ FIRST — current continuation, 2026-10-13

**FA:** بازطراحی TehNet 0.5.1 و رزومه برگه 80 منتشر شده‌اند. اصلاح جدید متادیتای سئو فقط در ریپو آماده و با ۳۳ آزمون واحد تأیید شده؛ **هنوز روی سایت نصب نشده است**. این دو وضعیت را یکی ندان. کاربر خواسته در پایان هر مرحله گزارش کوتاه در چت و گزارش ماندگار در ریپو ثبت شود.

**EN:** Resume from this branch, not older main. Read `seo/SEO_AI_READINESS_2026-10-13.md` and `qa/SEARCH_METADATA_TESTS_2026-10-13.md`. The new `site/mu-plugins/tehnet-search-metadata.php` is PREPARED / UNIT-TESTED / NOT DEPLOYED. The current blocker is Remote Desktop Commander: RoboT lists online but ping/list_sessions/commands time out. Public website and authenticated WPVibe reads still work. GSC Wizard also returned payment_required; no upgrade was authorized.

Exact next action: restore the authorized management connection, inspect real MU-plugin/metadata ownership and live Core drift, take a fresh targeted backup, deploy only the new metadata file after actual-container lint, then verify live output. Do not overwrite the whole Core plugin: runtime reports 0.3.1 while its repository bootstrap header is older. Do not rerun the previous one-shot visual builders/deployer.

Fresh audit: homepage mobile lab Performance 93, Accessibility 100 (with a label-content-name-mismatch finding), Best Practices 100, SEO 61. Homepage description missing; noindex intentional. No field CrUX data. Published Sample Page ID 2 and prelaunch Learn wording remain launch-review items; nothing was silently deleted or made indexable.

Keep `blog_public=0`, noindex/nofollow, payments, existing customer data and unrelated services unchanged. Public résumé excludes the designated partner brand and personal mobile; business office contact is a separate identity. Never publish credentials, private backup bytes, customer data or font files. Prepared metadata source/test commits: `ef5ac64`, `b8845ff`; test evidence: `cad908a`.

## Earlier foundation state
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

## Earlier product backlog — after the current SEO continuation
**FA:** برای **Manual Quote/Invoice lifecycle** یک branch/plan ایزوله جدید بساز؛ inquiryهای موجود را به وضعیت‌های قابل‌پیگیری و پیش‌فاکتور/فاکتور دستی وصل کن، بدون فعال‌کردن payment یا indexing.

**EN:** Create a new isolated branch/plan for the **manual Quote/Invoice lifecycle**; connect existing inquiries to trackable quote/invoice states without enabling payment or indexing.

## Safety
Do not change port `18082`, Nginx routing, Docker project topology or unrelated services. Before each production content/code deployment, capture a fresh TehNet backup and compare the non-TehNet runtime fingerprint before/after.

## Still unresolved
- Rial gateway provider.
- NoPayments official API/webhook implementation details.
- Final optional logo redesign (must be previewed before replacement).
- Search Console connection/measurement and final launch-indexing approval.

## Latest live checkpoint — 2026-10-13 / بازطراحی منتشرشده

**FA:** قالب TehNet 0.5.1 با رنگ‌بندی سرمه‌ای/فیروزه‌ای و گرافیک شبکه رزومه تأییدشده روی سایت زنده منتشر شد. رزومه امیررضا در `/amirreza-golavar/` (برگه 80) فعال است. شماره شخصی و برند مستثناشده در خروجی عمومی نیستند. آموزش، لاب، خدمات، فروشگاه، داده‌های قبلی، تنظیمات پرداخت و noindex حفظ شدند.

**EN:** Production visual refresh is deployed. Source checkpoint is `feat/portfolio-visual-20261013`; main has not been auto-merged. Read `ops/VISUAL_REFRESH_2026-10-13.md`, `qa/live-browser-report.json` and `qa/public-verification.json` before continuing. Preserve existing production fonts and logo. The pre-existing blog archive H1/canonical defect was corrected.

Next: review/integrate this branch without overwriting the newer live presentation. Keep its worktree. The earlier manual Quote/Invoice, account/support and indexing-launch tasks remain separate and unfinished. No service restarts, port/routing changes or TehNet Core changes were made.
