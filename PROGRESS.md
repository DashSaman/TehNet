# TehNet Execution Progress

## Current phase
WordPress bootstrap and editable Gutenberg foundation are verified in production; SEO/content architecture is next.

## Product decisions locked
- Brand: TehNet / تهران نتورک
- Domain: https://tehnet.ir
- Primary market/language: Iran / Persian
- On-site service area: Tehran
- Remote Support: nationwide Iran
- Current public address: تهران، آیت‌الله کاشانی، شاهین جنوبی
- Current public phone: 021-91018746
- Model: Learn + Lab + Services + Shop
- Stack: WordPress + WooCommerce with custom TehNet theme and TehNet Core plugin
- Editing model: Gutenberg/custom blocks; routine changes managed from WordPress admin
- Education: free in phase 1; paid courses may come later
- Physical products: inquiry/manual quote because of price volatility
- Digital products: download-only and licensed
- Support: website tickets + two-way Telegram target
- Rial payment provider: not selected yet
- Crypto integration target: NoPayments, pending current provider verification
- SEO source of truth: DashSaman/-SEO

## Completed
- Product discovery, business model and master design approved.
- Multi-agent contract, roadmap and task backlog created.
- Production TehNet Docker/Nginx baseline documented without exposing secrets.
- Timestamped production backup created and archive integrity validated.
- Isolated worktree/feature branch workflow established.
- Foundation implementation plan created.
- Lightweight Persian RTL TehNet theme implemented with blue/turquoise/white design tokens.
- TehNet Core plugin implemented with editable phone/address/social/CTA settings.
- Public REST-enabled `tn_service` and `tn_lab` content models implemented.
- Theme and plugin files deployed into the existing `tehnet-wordpress` volume.
- Deployment verified `127.0.0.1:18082` unchanged and unrelated container/image/port topology unchanged during deployment.
- All foundation Bash contracts and PHP lint checks pass.
- WordPress finalized at `https://tehnet.ir` with locale `fa_IR`; installer redirect removed.
- TehNet theme and `tehnet-core` activated without changing `127.0.0.1:18082`.
- Editable Gutenberg homepage/top-level pages and primary menu seeded idempotently.
- Site intentionally remains `noindex,nofollow` with `robots.txt` disallow until launch gates pass.
- Fresh pre-bootstrap recovery point: `/root/tehnet-backups/20260915-000906`.

## Current production state
- `https://tehnet.ir/` returns HTTP 200 and no longer redirects to the installer.
- TehNet binding remains `127.0.0.1:18082`; DB and Redis topology are unchanged.
- Active theme: `tehnet`; active core plugin: `tehnet-core`.
- Locale is `fa_IR`; homepage is a static editable Gutenberg page.
- Seeded routes `/learn/`, `/lab/`, `/services/`, `/shop/`, `/about/`, `/contact/` all returned HTTP 200 during verification.
- Search indexing is deliberately disabled until SEO/content launch readiness.
- Bootstrap credential values are stored only in root-only `/root/tehnet-secrets/wp-admin-bootstrap.env` (mode 0600), never in Git.

## Current work
- Integrate the verified WordPress bootstrap branch.
- Start Phase 2: Persian query universe, SERP intent map, topic hubs and URL/taxonomy architecture.
- Inventory YouTube content after the SEO hub model is frozen.

## Next execution order
1. Integrate verified `feature/wp-bootstrap` into `main`.
2. Build TehNet Persian query universe and validate live SERP intent.
3. Freeze topic hubs, URL/taxonomy and internal-link architecture.
4. Implement technical SEO baseline while the site remains noindex.
5. Inventory/map YouTube content into approved hubs.
6. Implement Services, Shop, Account and Support in controlled phases.
7. Pass launch quality gates before enabling indexing.

## Rules for all agents
- Read `AGENTS.md` and `HANDOFF.md` first.
- Do not overwrite verified work or locked product decisions silently.
- Test before marking complete.
- Keep deployment evidence in `ops/` and TehNet SEO evidence in `seo/`.
