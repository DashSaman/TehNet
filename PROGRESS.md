# TehNet Execution Progress

## Current phase
Product architecture locked; implementation planning and production-baseline documentation are next.

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
- Product discovery and business model clarified.
- Platform approach selected over Elementor-heavy architecture.
- Admin-manageability principle locked.
- SEO/content topic-hub approach locked.
- Local/remote service scope locked.
- Commerce, account and support direction locked.
- Master design saved to `docs/superpowers/specs/2026-09-14-tehnet-platform-design.md`.
- `AGENTS.md`, `ROADMAP.md` and `TASKS.md` created for multi-agent continuity.
- Production TehNet containers were observed: WordPress, MariaDB and Redis are already running; WordPress still points publicly to its installer and the site is not configured yet.

## Current work
- Owner review of the written master specification.
- Production baseline/backup documentation.
- TehNet-specific SEO query architecture planning.
- Task-sized implementation plan preparation after spec review.

## Next execution order
1. Owner reviews the master design in the repository.
2. Record production baseline and backup/recovery evidence under `ops/`.
3. Produce implementation plan(s) from the approved specification.
4. Build TehNet theme/plugin foundation.
5. Establish SEO/content architecture before mass page creation.
6. Implement Services, Shop, Account and Support in controlled phases.
7. Pass launch quality gates and begin measurement/iteration.

## Rules for all agents
- Read `AGENTS.md` and `HANDOFF.md` first.
- Do not overwrite verified work or locked product decisions silently.
- Test before marking complete.
- Keep deployment evidence in `ops/` and TehNet SEO evidence in `seo/`.
