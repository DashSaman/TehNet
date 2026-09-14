# TehNet Execution Progress

## Current phase
Foundation implemented and safely deployed as files; WordPress installation/activation and page build are the next implementation phase.

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

## Current production state
- TehNet containers remain running on the original Docker topology.
- `tehnet-db` remains healthy.
- Public `https://tehnet.ir/` still redirects to `/wp-admin/install.php`; WordPress setup has not yet been finalized.
- Theme/plugin files are present but not yet activated because WordPress installation is incomplete.
- A separate `tunnelpannel-e2e` container appeared on the host during this work from another workflow; TehNet work did not create or modify it.

## Current work
- Complete and integrate the verified foundation branch.
- Prepare the next task-sized plan for WordPress bootstrap/activation and editable page foundation.
- Prepare TehNet-specific SEO/query architecture before mass content creation.

## Next execution order
1. Integrate the verified `feature/tehnet-foundation` branch after owner choice.
2. Safely finalize WordPress installation without changing host ports.
3. Activate `tehnet` theme and `tehnet-core` plugin.
4. Build editable Gutenberg homepage/header/footer foundations.
5. Establish SEO/content architecture before mass page creation.
6. Implement Services, Shop, Account and Support in controlled phases.
7. Pass launch quality gates and begin measurement/iteration.

## Rules for all agents
- Read `AGENTS.md` and `HANDOFF.md` first.
- Do not overwrite verified work or locked product decisions silently.
- Test before marking complete.
- Keep deployment evidence in `ops/` and TehNet SEO evidence in `seo/`.
