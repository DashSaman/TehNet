# Foreign VPS → Iranian server migration runbook

Status: documented procedure with a **synthetic local drill only**. Production scripts/app, Linux/container restore, real transfer, Iranian host access and end-to-end rollback are not implemented/tested here. Do not run illustrative CLI names as if they existed; W7 must implement the release commands in CONTRACTS and satisfy the gates below.

## Define the 30-minute objective honestly

Target: under 1,800 seconds from beginning the controlled write freeze on a prepared source to a healthy Iranian TehNet Software Archive service with public and protected-route checks complete. Include final state snapshot, final delta transfer, restore, validation, route cutover, smoke and the decision to accept or roll back. Record rollback time separately and total user-visible degraded time. Preseeded media/images, provisioning, initial bulk transfer and waiting for DNS propagation are preparation; report their duration separately rather than hiding them.

The existing TehNet WordPress site remains on its VPS in the initial migration model. If `/software/` keeps proxying through that foreign VPS, the service still depends on foreign access: **that mode cannot pass the Iran outage objective**. W0 must select a cutover architecture before W7 starts. Options: an Iranian HTTPS ingress for tehnet.ir that serves `/software/` locally and proxies other paths to the old WordPress origin; or a separately verified migration of the whole TehNet site. Recommended first design is the domestic ingress with owner-controlled routing and origin TLS. Outside `/software/`, WordPress may remain unavailable during an international outage; disclose that boundary. A domestic alternative download hostname is optional, does not silently replace the requested subpath, and needs separately authorized DNS/TLS design.

DNS is host-wide, not path-specific. Do not change tehnet.ir A/AAAA to a TehNet Software Archive-only host and break WordPress. Confirm the entire hostname's routing, edge/CDN and IPv6 plan; a foreign CDN/TLS/DNS dependency may defeat the outage goal. Proxying back to the VPS must preserve its Host/SNI/canonical behavior and cannot be a redirect loop. Preserve the old authoritative records/config and a direct management route before changing anything.

## Preparation — outside timer, mandatory

1. **Authority and inventory:** authorized access to both hosts and DNS/edge/TLS, current release/base ref, architecture/OS compatibility, clock sync, enough disk for active + staging + rollback + private encrypted backup, source CAS/DB sizes, bytes still to transfer. Measure sustained throughput on the actual route and estimate `remaining_bytes / measured_bytes_per_second`, adding restore/verification/startup margins. If remaining work cannot fit, preseed more or do not start.
2. **Warm target:** provision Linux/runtime/Docker/Compose and needed native APT/gpgv tooling; pin real image digests and package locks. Preload image archives and local assets so restore does not fetch GitHub/registries/CDNs. Verify same architecture or build separately in advance. Use official [image save](https://docs.docker.com/reference/cli/docker/image/save/) and [load](https://docs.docker.com/reference/cli/docker/image/load/) workflows; verify actual digests after import. Image tar archives do not include application volume data.
3. **State preparation:** pre-copy immutable public objects and encrypted private objects/manifests, preserving required metadata and by-hash references. Keep the source authoritative; no pruning or deletion propagation during migration. Do not sync a live SQLite DB file as a valid backup. Pin schema and software compatibility; use the [SQLite backup API](https://docs.python.org/3.12/library/sqlite3.html#sqlite3.Connection.backup). Freeze changes to the schema for the rehearsal/cutover window.
4. **Keys/access:** install secrets using a separate protected channel, least privilege and target file permissions. Transfer or explicitly rotate session/signing keys; document logout impact. Check backup decryption and no public private-object aliases. Prepare TLS including certificate chain/renewal and local clock; valid public HTTPS must work without weakening verification. Keep secret material off command arguments and reports.
5. **Route preparation:** lower DNS TTL in advance if DNS cutover is chosen, but do not guarantee resolver behavior from TTL alone. Pre-test domestic ingress via an explicitly targeted test client without changing global routing; verify public and private `/software/` and WordPress passthrough. Save exact A/AAAA/CNAME/edge/routing/TLS config and rollback instructions privately. Decide how old cached clients will reach the same active state; no two writers.
6. **Rehearsal gate:** run a cold restore on an isolated **Linux** target using representative DB/object sizes, then two real cross-host timed rehearsals including a rollback. Test international egress denied **inside the disposable test network only**, without cutting SSH/production networking. Check DNS, certs, image loads, all static assets, auth, local download checksums, SQLite integrity/foreign keys and no foreign control-plane requests. A local Windows fixture is insufficient.
7. **Go/no-go:** all checks pass, backup readable, public/private data separation verified, critical downloads independently recoverable, no new schema change, and measured budget fits. Rubika cannot be the only source of critical bytes. Record operator and abort point.

## Timed cutover — proposed 25-minute budget + 5-minute margin

These are budgets, **not measurements**. W7 logs wall-clock UTC and monotonic duration/exit status for every phase.

| Elapsed target | Action | Required evidence / abort |
|---|---|---|
| 0–3 min | Enter maintenance/read-only mode; pause only TehNet Software Archive worker/writer; stop new admin imports; drain in-flight writes | Source no longer mutates DB, manifests or CAS references; WordPress unaffected |
| 3–7 min | Consistent SQLite backup + final manifests/objects delta; freeze snapshot and hash manifest | Full DB integrity and referential validation; exact payload size/checksum; no raw WAL-only copy |
| 7–12 min | Transfer verified delta to target staging; decrypt private state under restricted permissions | Missing/corrupt object or insufficient disk aborts before active overwrite |
| 12–16 min | Restore into new release/data directory; validate schema, hashes, references, keyring/policy | Restore fails closed on unknown schema, bad signature/expiry or missing secret |
| 16–20 min | Start target with explicit local-only images and writes disabled; run public/private and Range smoke | No network pull/build; no VPN data before auth acceptance; no foreign dependency in domestic mode |
| 20–23 min | Switch only preapproved ingress/edge or host records; gracefully validate config | WordPress paths still work; one authoritative writer; old cached clients read-only/maintenance |
| 23–25 min | Verify from Iranian client and independent client; enable single target writer only after acceptance | `/software/` URLs, HTTPS, public catalog/download, private deny/login/logout, object hash, no unrelated drift |
| 25–30 min | Reserved for checks and decision | If not accepted by minute 25 or a critical test fails, invoke prepared rollback; never expose private data to save time |

Serving existing read-only immutable downloads during freeze may reduce disruption but is not assumed to prove zero downtime. Record actual 5xx/maintenance windows. Preserve original metadata security age; never extend signatures/expiry to make offline tests pass.

## Rollback, consistency and split-brain prevention

Keep the old TehNet Software Archive release, snapshot and route config intact; no destructive cleanup during the window. If failure occurs **before the target accepts writes**, keep target read-only, switch ingress to saved source routing, validate config/TLS and affected WordPress paths, restore source authoritative mode and restart only its worker. Verify old public/private behavior and log rollback RTO. Old DNS clients must not write to an abandoned target; route them to maintenance or the single active backend.

If target has accepted any write, **do not simply unfreeze the stale source**. Freeze target, take a new consistent backup with new CAS/manifests and audit events, transfer/validate it against source software/schema compatibility, and reconcile via documented forward recovery or supported rollback migration. The rollback objective is invalid until this post-write scenario is measured. Prefer read-only acceptance until final go decision so normal rollback needs no reverse data merge. Never run source and target workers concurrently against divergent writable catalogs.

Store secrets and user data privately; publish sanitized timings, bytes, release/image refs, schema version, test counts and result labels only. Delete old deployments/backups only after an owner-approved retention period and independent restore verification.

## Reproducible check available now

From repository root, Python 3.12+ with stdlib SQLite:

```text
python -m unittest discover -s projects/software-hub/tests -v
python projects/software-hub/tools/rehearse_migration.py --payload-mib 16 --runs 3 --output /a/new/writable/path/drill.json
```

Use a new output path in an existing writable directory; existing evidence is not overwritten. Windows also accepts a native absolute path. The script allocates its own temporary fixtures, creates a real SQLite backup, transfers a local ZIP, verifies every payload, changes a synthetic release pointer and rolls back to the original verified fixture. It never uses production paths, authenticates to a server or changes DNS. [Measured report after rollback strengthening](../evidence/migration-local-v2.json) and [validation interpretation](../evidence/VALIDATION.md) describe its actual limits. The earlier [initial drill](../evidence/migration-local.json) is retained as history and checked a pointer name without asserting that its rollback directory existed; do not use it as stronger rollback evidence.

## Acceptance report template for W7

Record date/operator, source/target country-vantage evidence, host OS/arch, application commit, image digests, schema, DB/CAS/delta bytes, measured link throughput, cold/warm state, preparation seconds, phase seconds, outage seconds, total cutover seconds, rollback seconds, commands and exit codes, public/private test results, no-foreign-egress results, WordPress regression results, remaining risks and sanitized log paths. Mark the 30-minute gate PASS only when **each** representative real-host rehearsal is under 1,800 seconds, all critical checks pass and rollback is demonstrated. Until then: `NOT_ACCEPTED`.
