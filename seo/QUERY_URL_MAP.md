# TehNet Query → Intent → Preferred URL Map

**Version:** 0.1  
**Date:** 2026-08-31

This map prevents cannibalization. A URL owns an intent cluster, not every spelling variant. Final course/product slugs may follow the selected LMS/WooCommerce permalink configuration but must remain stable after launch.

## Core / brand

| Preferred URL | Primary job/intent | Query examples | Index? | Business CTA |
|---|---|---|---|---|
| `/` | understand TehNet + choose journey | ته نت، تهران نتورک | YES | Learn / Lab / Services / Shop |
| `/about/` | entity/trust | درباره TehNet، تهران نتورک | YES | contact / view expertise |
| `/contact/` | contact / inquiry | تماس TehNet | YES | submit contact/inquiry |

## Learn hubs

| Preferred URL | Intent owner | Examples | Index rule |
|---|---|---|---|
| `/learn/` | networking academy overview / roadmap choice | آموزش شبکه، مسیر یادگیری شبکه | YES when substantive |
| `/learn/mikrotik/` | generic MikroTik learning + roadmap | آموزش میکروتیک، دوره های میکروتیک، یادگیری میکروتیک | YES priority |
| `/learn/linux/` | Linux/server learning roadmap | آموزش لینوکس سرور، لینوکس برای ادمین شبکه | YES when substantive |
| `/learn/cisco/` | Cisco learning roadmap | آموزش سیسکو، مسیر CCNA | YES when substantive |
| `/learn/voip/` | VoIP/call-center learning roadmap | آموزش ویپ، ایزابل، VoIP | YES when substantive |
| `/learn/ai-networking/` | applied AI-for-networking roadmap | هوش مصنوعی برای شبکه، AI برای ادمین شبکه | EXPERIMENTAL; index only with real assets |

Do **not** make generic duplicate pages such as `/tutorials/mikrotik/` targeting the same generic intent. `/tutorials/` is a browse hub, while `/learn/mikrotik/` owns the search/roadmap intent.

## Tutorials

Base: `/tutorials/`.

Individual pages use `/tutorials/<problem-or-task>/` and target one real user task, e.g.:

- `/tutorials/mikrotik-dual-wan-failover/`
- `/tutorials/mikrotik-load-balancing/`
- `/tutorials/mikrotik-vpn-troubleshooting/`
- `/tutorials/linux-server-network-troubleshooting/`

Rules:

- do not create one page per synonym;
- current-version assumptions are visible;
- include commands/config/output only when tested/sourced;
- link to relevant Lab/course/service/product relationships.

## Courses

Preferred conceptual base: `/courses/<course-slug>/` unless Tutor LMS production routing requires another stable base.

Initial priority candidates (publish only with real curriculum/video/entitlement):

- MikroTik foundations / MTCNA-aligned practical course;
- practical MikroTik VPN/Tunnel or real-world scenarios;
- Linux/server networking foundation or another source-backed course actually available.

Do not pre-create empty “3 courses” purely to hit a quota.

## Labs

| Preferred URL | Intent |
|---|---|
| `/labs/` | browse/understand TehNet Labs |
| `/labs/<scenario>/` | exact downloadable/practical scenario |

Examples: dual-WAN, firewall baseline, VPN/tunnel, monitoring/log analysis. Lab topic/filter URLs are noindex by default unless a specific filter proves a distinct useful search intent and has substantive landing content.

## Services

| Preferred URL | Intent cluster | Examples |
|---|---|---|
| `/services/` | overview/choose service | خدمات شبکه TehNet |
| `/services/network-support/` | generic ongoing support | پشتیبانی شبکه، نگهداری شبکه |
| `/services/mikrotik/` | MikroTik commercial service | خدمات میکروتیک، کانفیگ میکروتیک |
| `/services/vpn/` | VPN/tunneling implementation | راه اندازی VPN، تونل شبکه |
| `/services/linux-server/` | Linux/server implementation/support | خدمات لینوکس، پشتیبانی سرور لینوکس |
| `/services/voip/` | VoIP/call center | راه اندازی ویپ، ایزابل |
| `/services/firewall-security/` | network firewall/security hardening | امنیت شبکه، فایروال شبکه |
| `/services/virtualization/` | virtualization | VMware/ESXi/virtualization service |
| `/services/hourly-consulting/` | paid expert time | مشاوره شبکه ساعتی |

Location rule: no `/tehran/`, `/karaj/`, etc. keyword-swapped service doorway factory. State truthful service areas on the relevant service/contact pages. A future real office/location can receive a location page when evidence exists.

## Shop

Use WooCommerce's final permalink policy consistently. Conceptual ownership:

| Page class | Intent |
|---|---|
| `/shop/` | store/departments |
| MikroTik product category | خرید/قیمت تجهیزات میکروتیک generic |
| Cisco product category | خرید تجهیزات سیسکو generic |
| Wi-Fi/access-point category | category commercial intent |
| exact product page | model/SKU price/spec/availability |
| comparison/buying guide | decision intent when unique evidence exists |

A model page must not exist unless the product/sourcing facts are real. An inquiry-only product may be indexed if its identity/specs are real and availability messaging is truthful.

## Pro / account / utility

| URL | Index policy |
|---|---|
| `/pro/` | YES; explain real benefits/pricing/renewal clearly |
| `/account/` | NOINDEX |
| cart/checkout/order endpoints | NOINDEX |
| `/support/` | typically YES for public support entry; private ticket views NOINDEX/authenticated |
| internal search/filter/facet parameter pages | NOINDEX/control crawl as appropriate |

## Internal link graph

- Home → all four commercial hubs.
- Learn topic hub → courses + strongest tutorials + labs.
- Tutorial → relevant lab/course/service/product only.
- Lab → prerequisite tutorial + related course.
- Service → proof/tutorial/case resource + contact/quote.
- Product → category + selection guide/tutorial + optional configuration service.
- Course → supporting labs/tutorials; avoid irrelevant product spam.

## Canonical rules

- preferred scheme/host: `https://tehnet.ir`;
- `www` permanently redirects to apex;
- one canonical URL per product/content entity;
- tracking parameters canonicalize to preferred clean URL where applicable;
- do not canonicalize genuinely different products/services to a generic hub merely to hide duplication;
- out-of-stock product lifecycle follows ecommerce policy (temporary unavailable page can remain; permanently gone uses genuine equivalent redirect or 404/410 as appropriate).
