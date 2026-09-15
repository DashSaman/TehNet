# TehNet Execution Progress

## Current phase
YouTube/content mapping and the first Learn owner `/learn/mikrotik/` are implemented and live-verified while production remains intentionally noindex. Next phase is building the approved Tehran/Remote service owner pages.

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

## Current production state
- Active theme: `tehnet`; active plugin: `tehnet-core`.
- Static editable homepage and primary navigation are live.
- Canonical host is `https://tehnet.ir`.
- Search indexing remains deliberately disabled until launch gates pass.
- No secret values are stored in Git.

## Next execution order
1. Merge verified `feature/content-mapping` into `main` and retest.
2. Build the approved Tehran/Remote service owner pages from the current SERP intent map.
3. Add LocalBusiness/NAP output from centralized settings where technically appropriate.
4. Continue MTCNA/VPN/Linux content only through separate intent-backed plans; do not mass-create video pages.
5. Implement Shop/catalog, account/support and payment phases in separate tested branches.
6. Complete launch technical/content/measurement gates before enabling indexing.

## Rules for all agents
Read `AGENTS.md` and `HANDOFF.md` first, preserve locked decisions and verified work, use evidence before SEO claims, keep indexing disabled until an explicit launch gate, and never change unrelated project ports/containers during TehNet work.
