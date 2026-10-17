# TehNet Software Archive design and decision record

Status: owner authorized implementation on 2026-10-17; W0 v1 frozen. Runtime capabilities and deployment are tracked individually in STATUS. Date: 2026-10-17. Current request authorizes implementation plus the scoped software-section route and menu item; existing site routes and services must stay intact. This document carries intent into the roadmap; task owners must resolve listed gates before coding/integration.

## Purpose and acceptance

Build a credible Persian reference for Linux/developer artifacts and offline service continuity. Reuse trusted domestic mirrors; retain dependency-complete critical kits and independent recovery copies. Start at `https://tehnet.ir/software/` on the current foreign VPS; later run the TehNet Software Archive subsystem in Iran without depending on that foreign machine for core service. Existing TehNet WordPress/WooCommerce and its Learn/Lab/Services/Shop flows stay intact.

The ordinary catalog is public. VPN records, navigation, counts, APIs and payloads require server-side password authentication. A successful catalog query or migration is insufficient unless this separation survives backups, caches and direct object access.

Acceptance is staged: verified research copy; deterministic software tests; isolated staging deployment; real provider tests; clean-client offline install/run/restore; actual two-host migration and rollback. Each needs its own evidence. No numeric progress percentage substitutes for these gates.

## Current repository evidence

`DashSaman/TehNet` explicitly identifies itself as the source of tehnet.ir in its root README/AGENTS and `ops/PRODUCTION_BASELINE.md`. Base ref is `a84f46dad515c6151ef06c10dcea6e13dfde05a1`. Historical baseline: Compose project `tehnet`, WordPress `127.0.0.1:18082`, MariaDB and Redis, Nginx `/etc/nginx/sites-enabled/tehnet.ir.conf`, deployment under `/opt/tehnet/`. This is repository evidence from September, not a fresh SSH inventory. A public web fetch failed in this environment; current live state and IP were not confirmed. Never infer an origin IP from this record.

## Options and recommendation

| Option | Benefit | Cost / decision |
|---|---|---|
| Entirely inside existing WordPress/Core | Shared administration and existing user system | Couples workers, archive storage and migration to TehNet DB; not the recommended mirror engine |
| Independent TehNet Software Archive app behind one prefix | Isolated data, quotas, release and recovery; preserves original research stack | Requires explicit path/auth contract and a narrowly reviewed Nginx addition; recommended for mirror engine |
| Separate subdomain/site immediately | Simplest root paths | Does not meet the requested initial subpath; reserve for a future optional download host |

The independent engine is a **new subsystem proposal**. Root TehNet theme/Core responsibilities for existing business logic remain. Any WordPress navigation/editorial/account integration stays in TehNet Core and requires a separate change; never put mirror workers or commerce logic into the theme. There is no new checkout, payments or license entitlement system in TehNet Software Archive P0.

## Runtime and state boundaries

Carry forward the research's Python 3.12/FastAPI/Jinja2, SQLite one-writer, native gpgv/APT verification, bounded filesystem CAS and Compose edge/app/worker design. These are selected design choices, not installed dependencies. W0 approved the isolated research engine with WordPress business logic left in Core; pin versions/digests after checking actual support and vulnerabilities. No Redis/Celery/Kubernetes requirement in P0.

Dedicated project `tehnet-software`, network and private data root `/srv/software`; never reuse TehNet DB, volumes or existing container names. Candidate loopback binding `127.0.0.1:18083` is **unallocated until a fresh host check**; do not assume it is free. `/software/` is the only initial public prefix. No changes to `18082`, existing host default routes or unrelated projects. Data partitions: public catalog/CAS; private VPN catalog and objects; restricted operational audit; external secret mounts. Backups retain those classifications and encryption policy.

Schema/trust defaults from the archive remain: SHA-256 CAS, immutable original signed APT metadata, signature→index→artifact chain, seven-day by-hash retention plus live references, fail closed on expiry/tamper, null for unknown, source approval and license gates. Private access policy is an added required schema migration; unclassified imported software defaults restricted until reviewed.

## Downloads and storage

User-facing links start at `/software/download/...` or the protected equivalent and identify a registered exact digest. Remote redirects are low-bandwidth but expose their destination to the client; they do not conceal infrastructure or turn foreign bytes into domestic tariff traffic. A controlled stream/local serve keeps the visible URL but consumes server bandwidth and needs its own verification and Range tests. Never implement an arbitrary URL proxy. No claims of origin-IP secrecy from a domain name alone.

Public mirrors are allowed only after operator/permission, exact hash, freshness and policy checks. VPN payloads cannot be made private through a public mirror redirect. Keep them behind an authenticated local/internal object serve or a backend with revocable authorization on every retrieval; plain public URLs are ineligible.

Local CAS is the first dependable storage target. Rubika remains a disabled optional adapter; no official quota, retention, anonymous download, token lifetime or outage suitability has been verified here. Iranian S3/object storage and partner-host mirrors remain replaceable candidates: require exact contract, retention, egress/Range, costs, failure-domain and restore evidence. Do not treat free accounts as unlimited storage or independent backup.

## Assumptions and open gates

- `/software/` is the proposed slug; W0 must check current WordPress routes and owner preference before deployment.
- Existing foreign VPS has spare resources; not measured. Start a staging estimate of 2 vCPU and 2–4 GiB **additional** RAM only as a planning range, not a requirement proven by load tests. Budget at least metadata cap 1 GiB + CAS cap 5 GiB + images/logs/staging + an independent backup; maintain 30% free headroom. W6 measures peak RSS/CPU/disk and existing-site latency.
- Password/user management is local and works without external SSO; specific audited auth library is chosen by W0/W2 after current verification. Private route remains absent until W2 acceptance.
- Under-30-minute migration is a warm-target cutover objective with preseeded large data/images and validated secrets/TLS. It excludes server procurement and bulk first transfer; total preparation time must still be disclosed.
- Catalog ZIP/patch recovery, provider permissions, origin access, current port availability, domestic hosting, DNS/TLS control, production auth and true outage tests remain unresolved.

## Source and evidence rules

Original dated research, source links and probe results remain in [research](research/README.md). Do not silently refresh or endorse historical price/security/provider claims. Current requirements supersede old host/path instructions; preserve the original for attribution. W1 records original vs newly validated claims. No statements here certify national registration, tariff eligibility, lending or knowledge-based company qualification.
