# TehNet Agent Handoff

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
