# TehNet LocalBusiness / NAP Evidence — 2026-09-21

## Scope
Added centralized, truthful LocalBusiness JSON-LD for TehNet identity and service pages without enabling indexing or changing runtime topology.

## External guidance checked
- Google Search Central LocalBusiness documentation: business `name` and physical `address` are required for LocalBusiness rich-result eligibility; telephone is recommended with country and area code.
- Schema.org: `areaServed` is the current property; deprecated `serviceArea` is not used.

## Recovery point
`/root/tehnet-backups/20260921-011103`

The recovery point contains a validated MariaDB dump, `wp-content`, TehNet compose/env and Nginx site config.

## Emitted identity
- Type: `LocalBusiness`
- Stable ID: `https://tehnet.ir/#localbusiness`
- Name: `تهران نتورک | TehNet`
- Phone: `+982191018746` (machine-readable normalization of the existing visible number)
- Address: PostalAddress, Tehran / Tehran / IR, street derived from the existing central full address
- Areas served: Tehran on-site + Iran remote
- SameAs: existing Tehran Network YouTube identity
- No fabricated opening hours, ratings, geo coordinates or postal code

## Live verification
Exactly one valid JSON-LD block was parsed and value-checked on:
- `/`
- `/about/`
- `/contact/`
- `/services/`
- all five approved `/services/*/` owner pages

`/learn/mikrotik/` correctly contains no LocalBusiness block.
Visible Contact NAP still renders the existing phone and full address from the central settings defaults.
Direct-origin Contact rendering also contains the same schema block.

## Safety / launch state
- `TEHNET_FILE_DEPLOY=PASSED`
- `PORT_BINDING=127.0.0.1:18082`
- non-TehNet container/image/port topology unchanged
- `BLOG_PUBLIC=0`
- rendered `noindex, nofollow` retained
- `nginx -t` passed
