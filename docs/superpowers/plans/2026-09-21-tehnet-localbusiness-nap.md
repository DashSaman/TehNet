# TehNet LocalBusiness / NAP Implementation Plan

> Execution target: `feature/localbusiness-nap` from verified `main`.

## Goal
Add truthful, centralized LocalBusiness structured data for TehNet without inventing opening hours, ratings, geo coordinates, postal codes or unsupported claims. Keep production non-indexable until the explicit launch gate.

## Current external guidance checked 2026-09-21
- Google Search Central LocalBusiness: `name` and physical `address` are required for LocalBusiness rich-result eligibility; telephone is recommended and should include country/area code.
- Google says LocalBusiness data may be placed on pages that contain business information; it does not need to be duplicated indiscriminately across the whole site.
- Schema.org marks `serviceArea` as superseded; use `areaServed`.

References:
- https://developers.google.com/search/docs/appearance/structured-data/local-business
- https://developers.google.com/search/docs/appearance/structured-data/organization
- https://schema.org/LocalBusiness
- https://schema.org/areaServed

## Architecture ruling
- Business identity remains owned by TehNet Core settings, not the theme.
- Add one TehNet Core schema class; presentation theme remains schema-agnostic.
- Use a stable `@id` of `https://tehnet.ir/#localbusiness`.
- Render on homepage, About, Contact, Services hub and direct Services child pages only.
- Do not emit LocalBusiness on unrelated Learn/Lab/Shop pages at this phase.
- Use `LocalBusiness`, not a guessed narrower subtype.
- Keep visible NAP and schema values driven by the same settings/defaults.
- Normalize the existing Iranian phone number to E.164-style `+98...` only for machine-readable output.
- Use Tehran for on-site area and Iran for nationwide remote area through editable settings and `areaServed`.
- Omit empty optional properties rather than fabricate values.

### Task 1: Contract and centralized identity settings
- [x] Add failing `tests/localbusiness-schema-contract.sh` first.
- [x] Contract requires centralized business name/locality/region/country/on-site/remote settings and a schema renderer loaded by TehNet Core.
- [x] Contract rejects deprecated `serviceArea` and invented rating/geo/opening-hours fields.
- [x] Confirm RED.
- [x] Refactor settings defaults into one reusable source while preserving existing shortcodes and sanitization.
- [x] Add truthful defaults for business identity/service areas and the known YouTube identity URL.
- [x] Re-run core/settings contracts and new contract to GREEN; commit.

### Task 2: LocalBusiness JSON-LD renderer
- [x] Implement `class-schema.php` with conditional page targeting, PostalAddress, normalized telephone, stable `@id`, URL, `sameAs`, and `areaServed`.
- [x] Derive streetAddress from the existing full display address without duplicating a second street-address source of truth.
- [x] Output with `wp_json_encode` and unescaped Unicode/slashes.
- [x] Keep output absent when required identity/address fields are incomplete.
- [x] Run PHP lint and full repository suite; commit.

### Task 3: Safe production deployment and live validation
- [x] Create a fresh TehNet DB/wp-content recovery point and fingerprint non-TehNet runtime.
- [x] Deploy only TehNet theme/plugin files through the existing guarded deploy script; no container/Nginx restart.
- [x] Validate JSON-LD syntax and exact values on homepage, Contact, About, Services hub and all five service owners.
- [x] Verify no LocalBusiness script on `/learn/mikrotik/`.
- [x] Verify `blog_public=0`, rendered `noindex,nofollow`, port `127.0.0.1:18082`, Nginx config and unrelated runtime unchanged.

### Task 4: Evidence, coordination and integration
- [x] Record live evidence and recovery path in `ops/`.
- [x] Update `PROGRESS.md`, `HANDOFF.md`, `TASKS.md` with verified facts only.
- [x] Run all contracts, shell syntax/PHP lint, live JSON parse and secret-value diff scan.
- [x] Commit, merge to `main`, rerun suite/live gate, push and clean up the worktree/branch.
