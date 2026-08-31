# TehNet Handoff

**Updated:** 2026-08-31

## Current goal

Build the first professional, sellable TehNet MVP on `tehnet.ir` / `91.107.138.246`.

## Canonical repository

`DashSaman/TehNet`

All TehNet work belongs here. `DashSaman/-SEO` is reference-only for SEO/AEO/GEO/search operating practices.

## Active branch

`tehnet-bootstrap`

## Current implementation state

- Product/architecture design approved after 20 questions.
- Dedicated repository initialized.
- WordPress deployment foundation, custom theme skeleton and custom core plugin are being moved into this repository.
- DNS screenshot supplied by user showed apex `tehnet.ir` A record pointing to `91.107.138.246` through Cloudflare; Cloudflare warned that `www` had no record.
- Preferred canonical is apex `https://tehnet.ir`; `www` must resolve and 301 to apex.

## Production access blocker

SentinelX sees the target host as:

`host_pvworker_138246_20260831` (`91.107.138.246` context from the project)

The host is connected and healthy but currently inactive because the connected SentinelX account is on a Free plan allowing only one active host while five are connected. Do not disconnect unrelated production hosts without explicit instruction. Until this is resolved, continue repository implementation/testing that does not require production mutation.

## Next executable work

1. Finish repository bootstrap and CI.
2. Complete TehNet core plugin behavior: inquiry products, 30-day Pro access product, relationship UI/API.
3. Complete theme templates for hubs and content relationships.
4. Build TehNet SEO business/search brief and query→URL map from live SERPs.
5. Review existing Tehran Network YouTube inventory and brand visuals.
6. Once target host is active: run read-only production inventory, classify GREENFIELD/COEXIST, back up, install runtime, deploy theme/plugin, then validate.

## Do not guess

Production package versions, existing ports/services, PHP-FPM socket, existing web roots, payment-gateway credentials, Google OAuth credentials and real product inventory must be discovered or supplied before production configuration is finalized.
