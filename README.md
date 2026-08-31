# TehNet

TehNet (`tehnet.ir`) is a Persian networking platform combining four equal business journeys:

- **Learn** — free tutorials and paid courses
- **Lab** — scripts, configs, diagrams and hands-on labs
- **Services** — remote/on-site networking services and consulting
- **Shop** — networking equipment with direct purchase and inquiry flows

## Status

This repository is the canonical source of truth for all TehNet product, implementation, operations, SEO and deployment work.

Development starts on feature branches and is merged to `main` only after verification.

## Production target

- Domain: `tehnet.ir`
- Origin server: `91.107.138.246`
- CDN/DNS: Cloudflare
- Canonical host: `https://tehnet.ir`
- `www.tehnet.ir` must permanently redirect to the apex host.

## SEO reference

The evidence-based SEO operating system in `DashSaman/-SEO` is treated as an external reference. TehNet-specific query maps, audits, decisions and evidence live in this repository.

## Repository map

- `docs/` — product/design/architecture/implementation specs
- `ops/` — installation, deployment, backup, recovery and production evidence
- `site/` — custom WordPress theme/plugins and tests
- `seo/` — TehNet-specific SEO research, query maps and launch gates
- `content/` — content inventory and YouTube migration records
- `AGENTS.md` — execution contract for AI/engineering agents
- `HANDOFF.md` — current continuation state
- `PROGRESS.md` — verified work completed and remaining

See `PROGRESS.md` and `HANDOFF.md` for the live project state.
