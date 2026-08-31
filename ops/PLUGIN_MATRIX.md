# TehNet Component / Plugin Ownership Matrix

**Reviewed:** 2026-08-31

The rule is one owner per concern. Do not install overlapping plugins without updating this decision record.

| Concern | Owner | Launch decision | Evidence / notes |
|---|---|---|---|
| Commerce/orders/products/download entitlements | WooCommerce | USE | WordPress.org current reviewed version: 11.0.1; maintained by Automattic; core is open source. |
| Course/LMS | Tutor LMS | USE, free first | Current reviewed version 4.0.7; 100k+ active installs; Persian translation available. Free edition supports WooCommerce monetization with manual Woo product creation/linking, which is acceptable for launch. |
| TehNet Pro membership | `tehnet-core` | CUSTOM | No generic membership plugin at launch. A designated WooCommerce product grants/extends 30-day Pro access after successful payment. This avoids a second checkout/entitlement engine and better fits Iranian gateways that may not support automatic recurring charging. |
| Google login | Nextend Social Login | USE, free first | Current reviewed version 3.1.26. Free edition supports Google/WordPress user login. WooCommerce-specific placement is a Pro feature, so launch UX will use normal WP/custom account login placement unless Pro is legitimately licensed later. Google OAuth secrets stay outside Git. |
| SEO/meta/sitemap | Yoast SEO | USE | Current reviewed version 28.2; mature canonical/meta/XML sitemap owner. TehNet SEO decisions still come from `DashSaman/-SEO`; plugin scores are not KPIs. Disable/avoid duplicate schema/meta ownership in other plugins where conflicts occur. |
| Product structured data | WooCommerce + validated targeted extensions in `tehnet-core` only if needed | USE NATIVE FIRST | Visible product price/stock/schema must agree. Do not let multiple SEO plugins emit competing Product entities. |
| Support ticketing | Fluent Support | USE | Current reviewed version 2.3.1; 10k+ active installs; Persian translation listed; ticket system is self-hosted in WordPress. |
| Object cache | Redis Object Cache | CONDITIONAL | Reviewed version 2.8.0; enable only if production baseline confirms Redis can be safely installed/run. Prefer PhpRedis. |
| Full-page cache | Nginx/Cloudflare strategy | CONDITIONAL | Do not install a second page-cache plugin by default. If FastCGI cache is used, exclude login, cart, checkout, account, admin and personalized/entitled pages. Validate before enabling. |
| Page builder | None | DO NOT ADD | Use custom TehNet theme + block editor/native templates. Avoid Elementor-style dependency/bloat unless a future requirement justifies it. |
| Security | Cloudflare + origin hardening + WP least privilege | NATIVE/OPS | No generic all-in-one security plugin initially. Add a focused plugin only for a measured gap. |
| Backups | Host-level ops scripts | OPS | DB/files/config backups live outside web root and are restore-tested. Do not rely solely on a WordPress backup plugin. |
| Iranian payment gateway | TBD real provider | BLOCKED | Do not install random gateway plugins. Select after owner supplies the actual PSP/aggregator account/provider; verify maintenance, WooCommerce compatibility and callback security before production use. |
| Paid video hosting | TBD signed/streaming provider | BLOCKED | Requirement: in-site playback without normal direct-download CTA. Do not claim DRM. Select provider after storage/bandwidth/cost requirements are confirmed. |
| SMTP/email delivery | TBD | BLOCKED | Pick provider after sender domain/mail service is known; credentials never committed. |

## Why Tutor LMS + WooCommerce

TehNet must sell both courses and physical network equipment. WooCommerce therefore remains the single commerce/order engine. Tutor LMS free can link courses to manually-created WooCommerce products, avoiding a second checkout engine. Upgrade to Tutor LMS Pro only when a real Pro-only capability is needed and licensed.

## Why custom Pro instead of a membership plugin

Launch Pro is a simple monthly access product. `tehnet-core` stores an expiry timestamp on the WordPress user. Successful payment of the configured Pro product adds 30 days from the later of `now` or the current active expiry; each order is marked after granting to prevent duplicate extension. This is deliberately small and testable.

## Installation policy

Before installing production plugins, record exact installed version in `ops/BASELINE.md` / deployment log. Lock update windows, back up first, and rerun launch-critical journeys after upgrades.
