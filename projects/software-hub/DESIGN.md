# TehNet Software Archive design and decision record

> Current owner override (2026-10-17): no downloadable payloads on the website VPS. [ADR 0002](decisions/0002-external-payload-storage.md) supersedes historical local-CAS requirements. The engine keeps metadata only, redirects approved public downloads externally, and refuses private redirects. W2/W3/external-W5 engine is active after accepted same-host recovery/code rollback (2026-10-18); owner password setup, external private delivery, provider and Iran migration acceptance remain separate gates. See [external storage](EXTERNAL_STORAGE.md) and [engine operations](deployment/ENGINE_OPERATIONS.md).

Status: owner authorized implementation on 2026-10-17; W0 v1 frozen. Runtime capabilities and deployment are tracked individually in STATUS. Date: 2026-10-17. Current request authorizes implementation plus the scoped software-section route and menu item; existing site routes and services must stay intact. This document carries intent into the roadmap; task owners must resolve listed gates before coding/integration.

## Purpose and acceptance

Build a credible Persian reference for Linux/developer artifacts and offline service continuity. Reuse trusted domestic mirrors; retain dependency-complete critical kits and independent recovery copies. Start at `https://tehnet.ir/software/` on the current foreign VPS; later run the TehNet Software Archive subsystem in Iran without depending on that foreign machine for core service. Existing TehNet WordPress/WooCommerce and its Learn/Lab/Services/Shop flows stay intact.

The ordinary catalog is public. VPN records, navigation, counts, APIs and payloads require server-side password authentication. A successful catalog query or migration is insufficient unless this separation survives backups, caches and direct object access.

Acceptance is staged: verified research copy; deterministic software tests; isolated staging deployment; real provider tests; clean-client offline install/run/restore; actual two-host migration and rollback. Each needs its own evidence. No numeric progress percentage substitutes for these gates.

## Current repository evidence

`DashSaman/TehNet` identifies itself as the source of tehnet.ir in root README/AGENTS and `ops/PRODUCTION_BASELINE.md`. Main base is `a84f46dad515c6151ef06c10dcea6e13dfde05a1`. Historical baseline and current scoped validation agree: WordPress `127.0.0.1:18082`, MariaDB/Redis and Nginx `/etc/nginx/sites-enabled/tehnet.ir.conf`, existing deployment `/opt/tehnet/`. The engine is active on loopback `18083` behind `/software/`; [activation evidence](evidence/ENGINE_ACTIVATION.md) records current image, real encrypted recovery/code rollback and preserved website fingerprints. [Preview deployment](evidence/DEPLOYMENT.md) and [staged validation](evidence/ENGINE_VALIDATION.md) remain historical evidence. Do not infer a secret origin IP from domain/repository data.

## Options and recommendation

| Option | Benefit | Cost / decision |
|---|---|---|
| Entirely inside existing WordPress/Core | Shared administration and existing user system | Couples workers, archive storage and migration to TehNet DB; not the recommended mirror engine |
| Independent TehNet Software Archive app behind one prefix | Isolated data, quotas, release and recovery; preserves original research stack | Requires explicit path/auth contract and a narrowly reviewed Nginx addition; recommended for mirror engine |
| Separate subdomain/site immediately | Simplest root paths | Does not meet the requested initial subpath; reserve for a future optional download host |

The independent engine is now deployed as a scoped subsystem. Root TehNet theme/Core responsibilities for existing business logic remain. Any further WordPress navigation/editorial/account integration stays in TehNet Core and requires a separate change; never put mirror workers or commerce logic into the theme. There is no new checkout, payments or license entitlement system in TehNet Software Archive P0.

## Runtime and state boundaries

Carry forward the research's Python 3.12/FastAPI/Jinja2, SQLite one-writer, native gpgv/APT verification, external payload storage and Compose edge/app/worker design. Pinned installed runtime dependencies are recorded in requirements.lock and the corresponding staged/live image evidence; APT acceptance remains planned. W0 approved the isolated research engine with WordPress business logic left in Core; pin versions/digests after checking actual support and vulnerabilities. No Redis/Celery/Kubernetes requirement in P0.

Dedicated project `tehnet-software`, network and private metadata/auth root `/srv/tehnet-software`; never reuse TehNet DB, volumes or existing container names. Loopback `127.0.0.1:18083` is already allocated to the accepted archive preview; do not run a second listener there or assume it is available for another task. `/software/` is the only initial public prefix. No changes to `18082`, existing host default routes or unrelated projects. Data partitions: public external metadata; private VPN external metadata; separate auth state; restricted operational audit; external secret mounts. Payloads stay at external providers. Backups retain those classifications and encryption policy.

Trust defaults carried into the current external design: exact SHA-256 identities, immutable original signed APT metadata, signature→index→artifact chain, seven-day by-hash retention plus live references, fail closed on expiry/tamper, null for unknown, source approval and license gates. Private access policy is an added required schema migration; unclassified imported software defaults restricted until reviewed.

## Downloads and storage

User-facing links start at `/software/download/...` or the protected equivalent and identify a registered exact digest. Remote redirects are low-bandwidth but expose their destination to the client; they do not conceal infrastructure or turn foreign bytes into domestic tariff traffic. A future authenticated external stream could keep the visible URL but consumes server bandwidth and requires its own verification, Range and no-disk-spool tests. Never implement an arbitrary URL proxy. No claims of origin-IP secrecy from a domain name alone.

Public mirrors are allowed only after operator/permission, exact hash, freshness and policy checks. VPN payloads cannot be made private through a public mirror redirect. Keep them behind an authenticated external stream with no website disk spool or a backend with revocable authorization on every retrieval; plain public URLs are ineligible.

Website local CAS is prohibited by the current owner instruction; existing mirrors and accepted external storage hold payloads. Rubika remains a disabled optional adapter; no official quota, retention, anonymous download, token lifetime or outage suitability has been verified here. Iranian S3/object storage and partner-host mirrors remain replaceable candidates: require exact contract, retention, egress/Range, costs, failure-domain and restore evidence. Do not treat free accounts as unlimited storage or independent backup.

## Assumptions and open gates

- `/software/` was accepted and deployed with one owned menu item; retain its route ownership and existing WordPress paths.
- Existing foreign VPS has spare resources; not measured. Start a staging estimate of 2 vCPU and 2–4 GiB **additional** RAM only as a planning range, not a requirement proven by load tests. Budget at least metadata cap 1 GiB + images/bounded logs (no software payload staging/cache) + an independent backup; maintain 30% free headroom. W6 measures peak RSS/CPU/disk and existing-site latency.
- Password management uses pinned pwdlib/Argon2id and local opaque sessions without external SSO. Component tests and same-host recovery/deployment passed; owner password setup remains intentional and pending.
- Under-30-minute migration is a warm-target cutover objective with preloaded images/metadata and validated secrets/TLS/provider connectivity. It excludes server procurement and bulk first transfer; total preparation time must still be disclosed.
- Catalog ZIP/patch recovery, provider permissions, domestic hosting, target DNS/TLS control, owner-provisioned production login and true outage tests remain unresolved. Encrypted five-database recovery is accepted on the current host only.

## Source and evidence rules

Original dated research, source links and probe results remain in [research](research/README.md). Do not silently refresh or endorse historical price/security/provider claims. Current requirements supersede old host/path instructions; preserve the original for attribution. W1 records original vs newly validated claims. No statements here certify national registration, tariff eligibility, lending or knowledge-based company qualification.

Current same-host acceptance: [engine activation](evidence/ENGINE_ACTIVATION.md) and [recovery](deployment/RECOVERY.md). Frozen v1 preview manifest retains its historical meaning; the implemented encrypted engine backup has its own format 1 and strict image/state contract. Generic future Iran cutover commands remain proposals unless explicitly implemented.
