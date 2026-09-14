# TehNet Platform Design — 2026-09-14

## Status
Approved product direction; implementation has not started from this specification yet.

## Product identity
- Brand: **TehNet / تهران نتورک**
- Domain: **https://tehnet.ir**
- Primary market: **Iran**
- Primary language: **Persian**
- Physical/local service area: **Tehran**
- Remote support: **nationwide across Iran**
- Current physical address for public/local use: **تهران، آیت‌الله کاشانی، شاهین جنوبی**
- Current public phone: **021-91018746**
- YouTube reference: **https://www.youtube.com/@tehran.network021**
- SEO operating reference: **DashSaman/-SEO**

## Product model
TehNet is a networking business platform with four first-class journeys:
1. **Learn** — free Persian networking education, mainly supported by YouTube.
2. **Lab** — scripts, configurations, diagrams, templates and downloadable technical assets.
3. **Services** — on-site networking services in Tehran plus nationwide remote support.
4. **Shop** — digital products plus physical networking equipment.

The site must feel like a professional networking authority first, not a generic WooCommerce store.

## Locked business decisions
- Tutorials are free in phase 1.
- Most educational videos will also live on YouTube.
- Public education must remain indexable and must not require login.
- Registration is encouraged for downloads, user history and account services.
- The user account must be full-featured from the first serious release.
- Support must exist both as website tickets and Telegram.
- Ticket/Telegram communication is intended to be two-way synchronized.
- Digital products can be either download-only or licensed.
- Licensed products may later support device/domain activation limits, expiration, renewal, revoke and validation logs.
- Physical products are nationwide inquiry/order items; current price is normally confirmed manually because of market volatility.
- A customer can request price, receive an invoice, pay and have goods sourced/shipped, including direct sourcing from Lalezar.
- Digital products should support automatic payment and fulfillment.
- Rial payment provider is intentionally not locked yet.
- Cryptocurrency payment target is **NoPayments**, with automatic invoice/payment confirmation as the desired behavior; exact API/webhook capabilities must be verified before implementation.
- Paid courses are out of scope for phase 1, but architecture must not block adding them later.

## Recommended stack
### Core
- WordPress
- WooCommerce
- MariaDB
- Redis
- Nginx/Cloudflare edge already in production topology

### Custom layer
Use a **custom TehNet theme** plus a **TehNet Core plugin**.

**Theme responsibilities:**
- presentation
- templates
- layout
- typography
- design tokens
- Gutenberg block presentation

**TehNet Core plugin responsibilities:**
- custom post types/taxonomies
- account extensions
- support/ticket domain logic
- Telegram integration
- digital delivery
- licensing
- inquiry workflow
- payment adapters
- site-wide settings
- structured data helpers specific to TehNet entities

Business logic must not be hardcoded into the theme. A future redesign must not break tickets, purchases, downloads, licenses or account history.

## Admin-editability principle
Daily site management must not require editing PHP or asking an AI to rewrite the project.

Use native WordPress/Gutenberg management wherever possible. Build reusable TehNet blocks/settings for:
- Hero sections
- service cards
- topic hubs
- YouTube/video sections
- product grids
- FAQ sections
- CTA sections
- testimonials/case evidence
- related tutorials
- related services/products
- Lab/download cards
- contact blocks

Create centralized editable settings for:
- logo
- colors/design tokens
- phone
- address
- Telegram/Instagram/YouTube links
- footer copy
- service CTAs
- LocalBusiness identity fields
- payment provider settings
- NoPayments settings
- Telegram bot settings
- support routing settings

Target: **about 90% of routine content/business edits should be possible from WordPress admin without code changes.**

## Information architecture
### Primary navigation
- آموزش
- لاب / فایل‌ها
- خدمات شبکه
- فروشگاه
- پشتیبانی
- درباره ما
- تماس با ما
- حساب کاربری

### Learn / SEO topic hubs
Initial topical families should be validated against real Persian SERPs before final URLs are frozen, but expected hubs include:
- MikroTik
- Routing
- VPN
- Firewall / Security
- Linux Server
- Network Administration
- VoIP where relevant
- Monitoring / Automation where relevant

Do not create one thin page per YouTube video by default. Use a **topic-cluster model**:
- one strong hub per major topic
- substantial tutorial pages for distinct search intents
- merge near-duplicate videos into one stronger page where appropriate
- embed relevant YouTube video(s)
- add original explanation, commands, diagrams/screenshots, FAQs and downloadable resources
- link contextually to related tutorials, Lab assets, services and products

## YouTube strategy
YouTube and tehnet.ir must reinforce each other rather than duplicate each other.

For important videos/pages:
- embed the video
- provide unique Persian article content rather than transcript dumping
- include commands/config snippets and troubleshooting notes
- provide relevant downloadable files where useful
- link from article to related services/products only when contextually relevant
- add appropriate video metadata/structured data where supported and truthful
- create internal links between topic hubs and supporting tutorials

The existing YouTube logo/visual identity is the baseline. Any redesigned logo must be previewed and explicitly approved before replacing the current identity.

## Services model
### Local
Physical/on-site service focus: **Tehran only** for now.

Do not generate fake city/location pages outside the actual service area.

Potential service categories:
- MikroTik installation/configuration
- routing/VPN/firewall configuration
- network troubleshooting
- office/network setup
- server/Linux/network administration
- remote diagnostics
- maintenance/support packages

### Remote
Remote Support is available nationwide in Iran.

Service pages should clearly separate:
- on-site Tehran eligibility
- remote nationwide eligibility
- what is included
- prerequisites
- response/contact method
- request/quote CTA

## Ecommerce model
### Physical products
Examples: cable, connectors, routers and networking equipment.

Phase-1 behavior:
- indexable product/catalog pages
- useful specifications and compatibility information
- price may be hidden or shown as inquiry-required
- CTA: استعلام قیمت / تماس
- request captured in account/admin
- manual quote/invoice
- payment confirmation
- sourcing/shipping nationwide

Avoid pretending stale prices are live prices.

### Digital products
Types:
1. Download-only
2. Licensed

Desired digital flow:
- product page
- payment
- automatic order confirmation when provider confirms payment
- account entitlement
- secure download and/or license issuance
- download/order history in account

## Payment architecture
Use a provider-adapter approach.

### Rial
Do not couple business logic to a single Iranian gateway. The provider can be selected later.

### Cryptocurrency
Target provider: **NoPayments**.
Desired behavior:
- create invoice
- store provider transaction/invoice reference
- receive verified status update/webhook or equivalent
- enforce idempotent payment confirmation
- mark WooCommerce order paid exactly once
- unlock digital entitlement automatically
- keep auditable payment event history

Before coding, verify current official NoPayments API, authentication, webhook signing, supported assets/networks, expiration semantics and reconciliation behavior.

## User account
The TehNet account area should eventually expose:
- profile
- orders
- physical quote requests
- digital purchases
- downloads
- licenses and activations
- support tickets
- ticket status/history
- purchased/completed services
- user-specific files
- notifications/preferences where useful

Future paid course history can be added without changing the account architecture.

## Support architecture
The website ticket is the system of record.

Required behavior:
- user creates ticket in site account
- support receives site/admin notification
- Telegram notification is sent to configured support/admin destination
- Telegram-side reply can be associated with the original ticket
- reply is stored back into the website ticket history
- website reply can also trigger Telegram notification
- all sync actions need stable ticket/message identifiers and duplicate protection

Do not make Telegram the only copy of support history.

## Visual direction
Primary palette:
- blue
- turquoise/cyan
- white

Style:
- modern technical/networking
- clean, fast and professional
- Persian-first typography and RTL
- subtle Tehran identity elements
- possible references to Tehran skyline, Milad Tower, Azadi Tower or urban geometry
- avoid decorative clutter that harms readability or speed

The current YouTube brand/logo is acceptable as the starting point. Any professionalized logo variant must be previewed before adoption.

## SEO operating model
`DashSaman/-SEO` is the reference framework. TehNet-specific decisions/evidence belong in this repository.

No agent may promise Page 1 or #1 rankings. The goal is to maximize competitiveness through verified technical, content, entity, authority and measurement work.

### Technical baseline
- one canonical HTTPS host: `https://tehnet.ir`
- `www` permanently redirects to apex
- clean crawlable server-rendered WordPress output
- XML sitemaps
- robots controls
- correct canonicals
- intentional index/noindex rules for account/cart/checkout/filter/archive surfaces
- breadcrumbs
- structured data only where truthful and supported
- image/video optimization
- strong Core Web Vitals targets
- minimal plugin/theme bloat

### Content/search architecture
- Persian keyword/query universe built from actual SERP observation and tools
- intent mapped before page creation
- topic hubs + supporting tutorials
- service pages for genuine Tehran/local and nationwide remote intents
- ecommerce/category/product pages based on real catalog demand
- internal links across Learn → Lab → Service → Shop where useful
- FAQ only where real user questions exist
- no doorway/location-spam pages
- no scaled thin AI content

### Local SEO
Use consistent TehNet NAP data across site and eligible external profiles:
- TehNet / تهران نتورک
- تهران، آیت‌الله کاشانی، شاهین جنوبی
- 021-91018746

Use LocalBusiness/Organization markup only with accurate fields. Update all occurrences centrally when address/phone changes.

### Entity/social reinforcement
Connect the site clearly to legitimate brand channels:
- YouTube
- Instagram
- Telegram

Use consistent naming, descriptions, logo and contact identity.

### Measurement
Launch is not SEO completion. Set up and use:
- Google Search Console
- analytics/conversion measurement
- server/log monitoring where useful
- indexed-page/canonical checks
- query/page performance tracking
- lead, quote, ticket, download and purchase conversions

## Performance principles
- no Elementor dependency by default
- prefer Gutenberg and custom blocks
- avoid plugin duplication
- use Redis intentionally, not as a substitute for bad architecture
- optimize images and fonts
- keep JavaScript limited to real interaction needs
- measure before/after performance for meaningful changes

## Security and operations
- secrets never committed to Git
- use environment/config separation
- least privilege for integration credentials
- verify webhook signatures where provider supports them
- idempotency for payment and Telegram sync events
- backups before destructive production changes
- staging/feature branch workflow before production
- document deployment evidence in `ops/`

## Production state observed before implementation
As of 2026-09-14, the server already has TehNet containers for WordPress, MariaDB and Redis. WordPress is not yet fully installed/configured publicly and the domain redirects to the WordPress installer. Default themes/plugins are effectively untouched. This makes the current deployment suitable for a clean implementation baseline.

## Explicit non-goals for phase 1
- paid LMS/course system
- English/international site
- on-site services outside Tehran
- real-time physical inventory/price engine
- mass city/location landing pages
- Elementor-first page building
- hard-coding editable business content into theme PHP

## Success criteria for the first production release
- TehNet identity and RTL design are coherent
- admin can edit routine site content/settings without code
- Learn/Lab/Services/Shop journeys are functional
- physical product inquiry flow works
- digital product entitlement/download flow works
- user account history is useful
- ticket system works and Telegram sync has verified behavior
- SEO technical launch gates pass with evidence
- Search Console/measurement is connected
- no Critical/High launch blocker remains undocumented

## Implementation gate
This document is the product/architecture specification. Agents must not invent conflicting architecture. Before implementation begins, convert this specification into task-sized implementation plans and validate provider-specific assumptions (especially NoPayments and Telegram integration details) against current official documentation.