# AGENTS.md — TehNet Execution Contract

This repository is the canonical source of truth for TehNet. Do not implement TehNet work in another repository.

## Product

TehNet (`tehnet.ir`) is a unified Persian networking brand with four equal primary journeys: Learn, Lab, Services and Shop.

## Mandatory working rules

1. Read `HANDOFF.md`, `PROGRESS.md`, the approved spec and active plan before changing code.
2. Work on a feature branch. Do not push unfinished implementation directly to `main`.
3. Use test-first development for application behavior. Every bug fix gets a regression test.
4. Preserve production workloads. Inventory and back up `91.107.138.246` before installing or replacing web/database services.
5. Never commit passwords, OAuth secrets, API keys, database credentials, private keys or payment credentials.
6. Update `PROGRESS.md` after every meaningful verified milestone. Record what was changed, what was tested, result, commit and remaining blocker.
7. Keep `HANDOFF.md` current enough that a fresh agent can resume without chat history.
8. SEO is designed in from the beginning. Use `DashSaman/-SEO` as the evidence/playbook reference, but keep all TehNet-specific SEO decisions and evidence in this repo under `seo/`.
9. Do not manufacture reviews, stock, prices, case studies, customer counts, credentials or location pages.
10. Do not publish thin placeholder pages merely to reach a target content count.
11. One plugin/system owns each concern. Avoid overlapping WordPress plugins and unnecessary page-builder bloat.
12. Prefer native WordPress/WooCommerce functionality before adding plugins.
13. All launch-critical changes need a reproducible verification step.
14. If production verification fails, record `NO-GO`; never declare a launch complete from deployment alone.

## Canonical architecture

- Ubuntu origin: `91.107.138.246`
- Cloudflare in front of origin
- Canonical public URL: `https://tehnet.ir`
- `www.tehnet.ir` → permanent redirect to apex
- Nginx + PHP-FPM + MariaDB + WordPress + WooCommerce
- Custom theme: `tehnet`
- Custom plugin: `tehnet-core`

## Product decisions

See `docs/product/DECISIONS.md`. Those decisions are approved unless the user explicitly changes them.

## Definition of verified

A task is verified only when its specified automated/manual checks have been run against the correct target and evidence is recorded. A file existing in Git is not proof that production works.
