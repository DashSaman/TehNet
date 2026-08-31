# TehNet Handoff

**Updated:** 2026-08-31

## Canonical source

Repository: `DashSaman/TehNet`  
Active branch: `tehnet-bootstrap`  
Draft PR: #1 (CI/review checkpoint, not a launch claim)

`DashSaman/-SEO` is an external SEO operating-system reference only. TehNet-specific work stays here.

## Current verified state

- Product strategy and 20-question decisions captured.
- Spec and execution plan exist in `docs/superpowers/`.
- Custom RTL dark/light `tehnet` theme exists with four equal homepage journeys.
- `tehnet-core` contains Lab/Service content types and content relationship metadata.
- WooCommerce product sale mode supports `direct` and `inquiry`; inquiry products become non-purchasable and show price/availability CTA.
- TehNet Pro is implemented as a configured WooCommerce product granting 30 days of user access on `woocommerce_payment_complete`, extending active expiry and guarding against duplicate grant for the same order.
- CI verifies PHP syntax, theme/core smoke, pure domain rules, integration contract and installer missing-secret behavior.
- Latest verified integration commit: `f53e0dd44097d9df9227757ab661ced000578dfc`, CI success.
- Component ownership is recorded in `ops/PLUGIN_MATRIX.md`.

## Production blocker

Target origin: `91.107.138.246`.

SentinelX host `host_pvworker_138246_20260831` is connected/healthy but inactive because the Free plan allows one active host while five are connected. Do not disconnect unrelated hosts without explicit user instruction. Production has therefore NOT been inventoried or mutated by this branch.

## DNS context

Owner-provided Cloudflare screenshot showed apex `tehnet.ir` proxied A → `91.107.138.246`; Cloudflare recommended adding a `www` record. Canonical policy is `https://tehnet.ir`, with `www` permanently redirected after it resolves.

## Next work safe without production access

1. `seo/BUSINESS_SEARCH_BRIEF.md`, `SERP_MAP.md`, `QUERY_URL_MAP.md`.
2. YouTube `KEEP|REFRESH|DROP` inventory and brand/visual evidence.
3. Service/inquiry request model and UI.
4. Theme hub/single templates and relationship components.
5. Content inventory/draft map.

## Next work once server becomes active

Run Task 1 exactly: read-only inventory → GREENFIELD/COEXIST classification → backup/checksum. Only then execute runtime installer and Nginx deployment. Detect the real PHP-FPM socket; never replace an existing vhost/service blindly.

## Release

`NO-GO` until production + critical journeys + SEO/backup validation pass.
