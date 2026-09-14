# TehNet Roadmap

## Phase 0 — Foundation and safety
- Validate current TehNet Docker/WordPress/MariaDB/Redis baseline.
- Capture backup/recovery procedure.
- Establish branch/deploy/test workflow.
- Finish WordPress installation only after configuration baseline is documented.

## Phase 1 — Platform foundation
- Build custom TehNet theme with Persian RTL, blue/turquoise/white design system and subtle Tehran visual identity.
- Build TehNet Core plugin skeleton.
- Add centralized business settings: phone, address, social links, logo, CTA and LocalBusiness identity.
- Add reusable Gutenberg blocks for Hero, services, tutorials, video, products, FAQ, CTA, Lab/download and contact sections.
- Keep business logic out of the theme.

## Phase 2 — Content architecture and SEO baseline
- Build Persian query universe using `DashSaman/-SEO` methodology.
- Validate real SERP intent before freezing URLs.
- Define topic hubs such as MikroTik, Routing, VPN, Firewall/Security, Linux Server and Network Administration.
- Define internal-link model across Learn → Lab → Services → Shop.
- Configure canonical host, sitemaps, robots, index rules, breadcrumbs and supported structured data.
- Connect Search Console and conversion measurement.

## Phase 3 — Learn + YouTube
- Inventory current YouTube channel content.
- Map videos to topic hubs/search intents.
- Create substantial tutorial pages only where intent is distinct.
- Embed relevant videos and add original Persian explanations, commands, troubleshooting and related files.
- Avoid transcript-dump/thin pages.

## Phase 4 — Services
- Build Tehran on-site service pages.
- Build nationwide Remote Support pages/flows.
- Add quote/request forms and account history.
- Keep service-area claims accurate; no fake city pages.

## Phase 5 — Shop and digital products
- Configure WooCommerce catalog.
- Physical products: specs + inquiry/price request + manual quote/invoice flow.
- Digital products: download-only and licensed product types.
- Add account entitlement/download history.
- Add license lifecycle foundation: issue, activation limit, expiration, renewal/revoke and logs.

## Phase 6 — Payments
- Implement provider-adapter architecture.
- Select rial gateway later without changing core commerce logic.
- Verify current NoPayments documentation and implement automated crypto invoice/status flow if supported as required.
- Make order confirmation idempotent and auditable.

## Phase 7 — Account and support
- Full user dashboard: profile, orders, quotes, downloads, licenses, tickets, services and user files.
- Site ticket system as canonical support record.
- Telegram notifications plus two-way reply synchronization.
- Stable mapping IDs and duplicate-event protection.

## Phase 8 — Launch quality gate
- Performance/Core Web Vitals review.
- Security and access review.
- Technical SEO launch checklist from `DashSaman/-SEO`.
- Validate analytics/Search Console/conversions.
- Verify mobile/RTL/admin editability.
- Launch only when Critical/High blockers are resolved or explicitly documented.

## Future phases
- Paid courses/LMS.
- Membership/TehNet Pro if business case is proven.
- Additional payment providers.
- English/international expansion only after Persian/Iran product is mature.
