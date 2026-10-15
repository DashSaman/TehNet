# TehNet Execution Progress

## Active store mission — 2026-10-15
وضعیت نسخه محلی: اتصال ERP و عملیات Woo، نقش‌ها، فاکتور و درخواست مرجوعی پیاده‌سازی و آزموده شده‌اند. docs/acceptance-matrix-fa.md، docs/testing.md و docs/user-guide-fa.md مبنای ادامه‌اند. همه ۲۵ قلم draft و بدون قیمت/موجودی واقعی‌اند. شاخه audit/store-readiness-20261015 از visual واقعی شروع شده؛ main و production تغییر نکرده‌اند. زرین‌پال انتخاب و پروتکل sandbox واقعی آزموده شد؛ آداپتور آزمایشی با 49 بررسی mock آماده ولی خاموش است. docs/payment-sandbox-fa.md شواهد و محدودیت Docker را ثبت می‌کند. هدف بعدی آزمون native gateway→ERP و checkout موبایل پس از رفع دسترسی Docker، مدارک و قیمت/stock واقعی، مالیات و credential تولید، سپس release دارای backup/restore تولید و تأیید صریح مالک است. ثبت یا ادعای پرداخت واقعی مجاز نیست.



## Current phase / فاز فعلی — 2026-10-13
- **FA:** بازطراحی TehNet 0.5.1 و رزومه مستقل امیررضا منتشر شده‌اند. ممیزی زنده و انتقال درس‌های SEO/AEO/GEO مایتل ثبت شد. اصلاح متادیتای تازه با ۳۳ آزمون واحد آماده است، اما به علت بی‌پاسخ‌بودن اتصال ریموت هنوز منتشر نشده است.
- **EN:** Visual release LIVE; SEO follow-up PREPARED / UNIT-TESTED / NOT DEPLOYED. Read `seo/SEO_AI_READINESS_2026-10-13.md` and `qa/SEARCH_METADATA_TESTS_2026-10-13.md`. Noindex remains intentional. Restore the management connection and finish guarded integration/live checks before claiming this follow-up complete.

## Product decisions locked
- Brand/domain: TehNet / تهران نتورک / `https://tehnet.ir`
- Primary market/language: Iran, Persian-first.
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

## Completed and verified — historical phase evidence
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
- Active theme: `tehnet` 0.5.1; live WPVibe reports TehNet Core 0.3.1 and WooCommerce 11.1.1.
- Static editable homepage, primary navigation and profile page ID 80 are live.
- Canonical host is `https://tehnet.ir`.
- Search indexing remains deliberately disabled until launch gates pass.
- No secret values are stored in Git.
- New `site/mu-plugins/tehnet-search-metadata.php` is repository-prepared only; no production installation is claimed.

## Next execution order
1. Restore remote management, inspect runtime metadata ownership, deploy the tested metadata allowlist after backup, and perform live retest.
2. Resolve prelaunch content and accessible-name findings; verify metadata coverage on lesson/term routes without changing stable URLs.
3. Design and implement the manual Quote/Invoice lifecycle for physical inquiries / طراحی و پیاده‌سازی چرخه دستی پیش‌فاکتور و فاکتور.
4. Implement account/support/ticket flows and Telegram bridge in separate tested branches.
5. Implement digital delivery/licensing and payment adapters only after provider requirements are verified.
6. Revisit VPN/Linux owner hubs only with independent intent evidence and substantial content.
7. Complete launch technical/content/measurement gates and obtain explicit indexing approval before enabling indexing.

## Rules for all agents
Read `AGENTS.md` and `HANDOFF.md` first, preserve locked decisions and verified work, use evidence before SEO claims, keep indexing disabled until an explicit launch gate, and never change unrelated project ports/containers during TehNet work. Report each phase boundary to the owner and distinguish prepared, deployed and live-verified results.

## 2026-10-13 — Portfolio-derived visual refresh / بازطراحی ظاهری

**FA:** بازطراحی قالب 0.5.1 و رزومه مستقل امیررضا روی سایت زنده منتشر شدند. نتیجه و محدودیت‌ها در `ops/VISUAL_REFRESH_2026-10-13.md` ثبت شده‌اند. محتوای سایر برگه‌ها، تنظیمات پرداخت و noindex تغییر نکردند. باگ قدیمی عنوان H1 و canonical بلاگ نیز اصلاح شد.

**EN:** Preserved live theme drift first, then deployed the approved navy/cyan design and conceptual network SVG through a guarded file allowlist. Native profile page ID 80; live browser and public route/download checks passed. Source branch: `feat/portfolio-visual-20261013`, retained for review rather than automatically merging main. No unrelated runtime, core-plugin, font or service-restart changes on the TehNet host.

## 2026-10-13 — SEO/AEO/GEO continuation / ادامه اصولی سئو

- Read `DashSaman/-SEO` methodology and MyTel's dated authority/AI execution evidence; reused URL stability, entity ownership, source-quality content and real before/after verification, not private data or ranking claims.
- Fresh homepage mobile lab audit: Performance 93, Accessibility 100, Best Practices 100, SEO 61; LCP 2.7 s, CLS 0.02, TBT 110 ms. No CrUX field data. Missing home description is an open defect; noindex is deliberate; accessible-name mismatch remains to diagnose.
- Created bounded page descriptions/Open Graph/ProfilePage module; 33 isolated PHP checks PASS and syntax PASS. Test stubs are not WordPress integration proof.
- Published-page REST read confirmed raw excerpts empty, Sample Page still published and prelaunch Learn wording. No silent content deletion or indexing change.
- Remote Desktop Commander connection timed out on multiple read-only checks. WPVibe reads work. GSC Wizard subscription expired; no upgrade or measurements claimed.
- Evidence and exact deployment gate: `seo/SEO_AI_READINESS_2026-10-13.md`, `qa/SEARCH_METADATA_TESTS_2026-10-13.md`.
