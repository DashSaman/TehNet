# AGENTS.md — TehNet Execution Contract

## Mission
Build and maintain **TehNet / تهران نتورک** at `https://tehnet.ir` as a Persian networking platform for Learn + Lab + Services + Shop.

## Mandatory reading order
1. `AGENTS.md`
2. `HANDOFF.md`
3. `PROGRESS.md`
4. `docs/superpowers/specs/2026-09-14-tehnet-platform-design.md`
5. `ROADMAP.md`
6. `TASKS.md`
7. Relevant project files
8. `DashSaman/-SEO` for SEO work

Do not restart discovery unless the owner changes a locked decision.

## Locked decisions
- Brand: TehNet / تهران نتورک
- Domain: `tehnet.ir`
- Main market/language: Iran / Persian
- On-site service: Tehran only for now
- Remote Support: nationwide Iran
- Address for now: تهران، آیت‌الله کاشانی، شاهین جنوبی
- Phone for now: 021-91018746
- Platform: WordPress + WooCommerce
- Architecture: custom TehNet theme + TehNet Core plugin
- Gutenberg/custom blocks preferred over Elementor
- Free education in phase 1
- Digital products: download-only and licensed
- Physical products: inquiry/manual quote initially
- Website ticket history is canonical; Telegram two-way sync is the target
- Rial gateway is not selected yet
- Crypto target: NoPayments, after current provider documentation is verified

## Architecture rules
Theme handles presentation only: templates, RTL/layout, design tokens and block presentation.

TehNet Core plugin holds business/domain logic: content models, settings, account extensions, tickets, Telegram integration, downloads, licensing, quote flows and payment adapters.

Do not hardcode routine business content if it can be safely editable in WordPress admin. Target roughly 90% of daily edits without code changes.

## SEO/content rules
Use `DashSaman/-SEO` as the evidence-based reference. Never promise Page 1/#1, create fake city pages, mass-produce thin pages, fabricate reviews or add unsupported structured data.

Do not automatically create one thin article per YouTube video. Prefer topic hubs, strong intent-specific tutorials, original explanations, commands/config examples, useful media, Lab assets and contextual internal links.

## Service/commerce rules
On-site targeting is Tehran only until changed by the owner. Remote Support can be nationwide.

Physical products may use inquiry/quote instead of stale prices. Digital entitlements must follow verified order state. Licensed products need explicit license state and audit history.

## Integration rules
Keep payment providers behind replaceable adapters. Confirm current provider behavior before implementing integrations. Avoid duplicate event processing.

Website tickets remain the system of record. Telegram is a notification/reply channel mapped back to the same ticket history.

## Coordination
After meaningful work update `PROGRESS.md`, `HANDOFF.md` and `TASKS.md`. Put deployment evidence under `ops/` and TehNet-specific SEO evidence under `seo/`.

## Definition of done
A task is done only when implementation/checks are complete, documentation matches reality, and the next exact action is preserved in `HANDOFF.md`.

Controlling design: `docs/superpowers/specs/2026-09-14-tehnet-platform-design.md`.
