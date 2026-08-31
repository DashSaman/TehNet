# TehNet Search Launch Checklist

This is a TehNet-specific execution checklist used with the broader `DashSaman/-SEO` launch and technical-audit playbooks.

## Pre-index gates

- [ ] `https://tehnet.ir` resolves and serves intended production.
- [ ] `www.tehnet.ir` resolves and 301 redirects to the exact apex path.
- [ ] HTTP → HTTPS policy is consistent behind Cloudflare/origin.
- [ ] No staging host/content is indexable.
- [ ] WordPress Settings URLs both use canonical apex HTTPS.
- [ ] Permalink structure is stable before bulk publishing.
- [ ] Critical pages return 200; retired URLs use correct 301/404/410 behavior.
- [ ] robots rules do not block required rendering assets.
- [ ] XML sitemap contains preferred indexable URLs only.
- [ ] canonical tags match preferred entity URLs.
- [ ] account/cart/checkout/private ticket/search/facet states are noindex/control-crawl as designed.
- [ ] no accidental tag/date/author archive index bloat.

## Content/intent gates

- [ ] each priority URL has a unique documented intent in `QUERY_URL_MAP.md`.
- [ ] generic MikroTik learning intent has one owner, not duplicate hubs.
- [ ] service pages contain real scope/process/deliverables/availability/CTA.
- [ ] location claims are real; no doorway city pages.
- [ ] products contain real price/availability state and fulfilment/warranty facts when known.
- [ ] no fake reviews/ratings/customer counts/case studies.
- [ ] old YouTube content is checked for current RouterOS/tool-version accuracy.
- [ ] AI-assisted content has human/factual QA and is materially useful.

## Structured data

- [ ] Organization/WebSite identity uses consistent visible facts.
- [ ] Product markup matches visible product price/availability/reviews exactly.
- [ ] Course markup, if used, matches real visible course facts and current search-engine support requirements.
- [ ] Breadcrumb markup matches visible hierarchy.
- [ ] no invented AggregateRating/Review schema.
- [ ] validate rendered JSON-LD, not merely plugin settings.

## Internal discovery

- [ ] all priority pages reachable by crawlable links.
- [ ] no orphan course/lab/service/product.
- [ ] tutorials link contextually to commercial assets.
- [ ] category/hub pages link to priority children.
- [ ] links resolve directly to final status-200 URL where possible.

## Performance/mobile

- [ ] mobile navigation and four homepage journeys usable.
- [ ] hero/product media sized/optimized; no unnecessary autoplay video.
- [ ] checkout/account excluded from unsafe full-page caching.
- [ ] JS theme toggle does not hide primary content from initial HTML.
- [ ] measure CWV after real deployment; do not claim pass from lab score alone.

## Measurement

- [ ] Search Console property verified.
- [ ] sitemap submitted after validation.
- [ ] analytics records key commerce/service conversions without collecting unnecessary sensitive data.
- [ ] baseline date recorded.
- [ ] branded/non-branded and cluster performance can be separated.
- [ ] change log links deployments/content updates to later performance analysis.

## Release decision

Search launch remains `NO-GO` if a Critical issue exists in availability, HTTPS, status, crawl/index, canonical, rendering, checkout/entitlement, measurement, or truthful commerce data.
