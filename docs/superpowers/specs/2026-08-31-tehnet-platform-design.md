# TehNet Platform Design

**Date:** 2026-08-31  
**Domain:** `tehnet.ir`  
**Production origin:** `91.107.138.246`  
**Canonical SEO reference:** `DashSaman/-SEO`

## Product model

TehNet is a Persian networking platform with four equal primary journeys:

- **Learn:** free tutorials and paid courses.
- **Lab:** configs, scripts, diagrams, backups and hands-on assets.
- **Services:** remote/on-site networking work, packages, custom quotes and hourly consulting.
- **Shop:** networking equipment with direct-purchase and inquiry inventory.

The differentiator is not four separate mini-sites. Content and commerce are connected through useful relationships:

`YouTube / Search → Tutorial → Lab → Course / Pro → Product → Service`

## Initial editorial priority

`MikroTik/VPN → Linux/Server → Cisco → VoIP → practical AI for Networking/IT`

AI content is implementation-focused, not generic AI news.

## UX and brand

TehNet is the primary brand. The UI is RTL-first, responsive and supports dark/light modes. Dark is the visual anchor. The visual system should modernize recognizable cues from the Tehran Network YouTube identity once channel assets are reviewed. Do not fabricate endorsements, user counts or project claims.

## Core public architecture

- `/` — home
- `/learn/` — Academy hub
- `/tutorials/` — free tutorial hub
- `/labs/` — lab/file hub
- `/services/` — service hub
- `/shop/` — equipment store
- `/pro/` — monthly Pro offer/status entry
- `/account/` — account
- `/support/` — support entry
- `/about/`
- `/contact/`

Topic groups: MikroTik/VPN, Linux/Servers, Cisco/Routing/Switching, VoIP/Call Center, AI for Network/IT.

## Services

Service pages must state real scope, who they fit, process/deliverables, remote/on-site availability, pricing model when feasible, evidence, limitations, FAQs and a clear CTA. Initial intended service pages: MikroTik configuration, network support, VPN/tunneling, Linux/server, VoIP/call center, virtualization, firewall/security and hourly consulting.

Remote service is available across Iran. On-site is Tehran and nearby cities by arrangement. Never create fake-office or keyword-swapped city doorway pages.

## Shop

Architecture: `Home → Department → Category → Subcategory → Product`.

Product pages combine real specs/price/availability/warranty with selection guidance, relevant tutorials/labs and optional configuration service. Two sale modes exist:

- `direct`: normal WooCommerce purchase.
- `inquiry`: no direct add-to-cart; user requests price/availability.

## Commerce / digital access

WooCommerce owns orders, checkout and downloadable entitlements. Downloadable products use expiry/download limits. TehNet Pro is monthly access; initial implementation may be a 30-day renewable access entitlement purchased through WooCommerce when automatic recurring billing is not supported by the chosen Iranian gateway.

Paid video must be presented inside the site through a provider/streaming design that does not present an ordinary direct-download link. This is access control/deterrence, not a false DRM guarantee.

## Authentication and support

Launch login: email/password + Google OAuth. Google credentials remain external secrets.

Support launch channels: account tickets, Telegram/WhatsApp quick contact and contact form/email. Live chat is deferred.

## SEO requirements

TehNet uses the evidence-based workflow from `DashSaman/-SEO`:

`Business → Market/SERP → Feasibility → Query/Intent map → Architecture → Technical → Brief → Content → On-page → Entity/Trust → Structured Data → Internal Links → Authority → AI Search → Launch → Validation → Measurement → Iteration`

Key constraints:

- one preferred URL per coherent stable intent;
- no synonym/location page factories;
- finite crawlable architecture;
- canonical policy before publishing at scale;
- truthful structured data matching visible content;
- category/product/service pages must serve real user intent;
- technical SEO is a launch gate, not an afterthought;
- success ties to qualified traffic, leads and revenue, not plugin scores.

## Technical architecture

- Ubuntu origin `91.107.138.246`
- Cloudflare edge/DNS
- Nginx
- PHP-FPM
- MariaDB
- WordPress
- WooCommerce
- selected LMS after maintenance/license review
- custom `tehnet` theme
- focused `tehnet-core` plugin

Avoid overlapping plugins/page builders. Prefer native WP/WooCommerce behavior and focused custom code for TehNet differentiators.

## DNS/canonical

Preferred URL: `https://tehnet.ir`.

Root A is currently configured by the owner to `91.107.138.246` behind Cloudflare. `www` must also resolve, then permanently redirect to apex. The origin configuration is not considered complete until live DNS/HTTP validation passes.

## MVP scope

Professional/sellable first release with the core hubs, account/checkout, support entry, commerce, course/lab/service/product models and real launch content. Working content targets are 3 courses, 10 useful tutorials, 5 labs, ~20 real products and core service pages, but content stays draft rather than publishing placeholders.

## Operations/security

- inventory host before mutation;
- preserve existing workloads;
- pre-change backup and checksum;
- least-privilege DB credentials;
- secrets never in Git;
- backup/restore procedure and restore test;
- controlled updates;
- hardened admin/edge rate limiting where compatible;
- explicit GO/NO-GO launch report.

## MVP acceptance

1. Responsive/dark-light four-journey homepage works.
2. User can register/login and complete an eligible purchase.
3. Entitled digital content is not exposed to anonymous users.
4. Service lead/support entry works.
5. Shop supports direct and inquiry products.
6. Priority pages pass technical SEO checks.
7. Analytics/search measurement hooks are present.
8. HTTPS/canonical redirect policy is live.
9. Backup and tested rollback path exist.
