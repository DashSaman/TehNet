# Integration contracts for independent owners

Status: planned contracts. W0 is the sole editor until frozen; changes require a versioned decision and consumer acknowledgement. Original type/function/CLI contracts remain in [API_CONTRACT](research/upstream/Linux/API_CONTRACT.md), except the documented path relocation and privacy additions here. Never treat historical public endpoints as permission to return VPN records.

## Ownership and module interfaces

`app/models.py`, `app/config.py`, `app/db.py`, `app/migrations/`, and `contracts/openapi.json` belong to W0. Model changes go through W0 before parallel work. W0 must add `visibility: public|restricted`, deny-default import policy and a safe public DTO; restrict audit/probe details separately. Separate private persistence/object roots are preferred; using one DB requires every read/count/export to enforce the same policy and an explicit review.

- W3 consumes `SourceConfig`, `Artifact`, `ProbeBudget`; produces `ValidatedTarget`, `HttpObservation`, `ProbeResult`. No public routes; no code that enables sources on discovery.
- W4 consumes W3 guarded fetches; produces `VerifiedRelease`, `MetadataBundle`, `ImportStats`, exact native-APT profile manifests and `GapDecision`. `accepted_at` requires real matching logs, never a caller-provided boolean.
- W5 owns `StorageBackend.stat`, `put_verified`, `download_target`, verified local objects, quotas and private-capable storage. Storage returns opaque object identity/internal paths, never uncontrolled URLs or user-supplied paths. W2 decides access **before** delivery.
- W2 owns `AccessContext`, authentication/session validation, `require_restricted_access(request) -> AccessContext`, `public_projection(record) -> PublicDTO|None` and private-route delivery policy. A module without a validated context cannot serve a private object. W0 freezes exact concrete typed signatures before dependent coding.
- W6 consumes these components through service entry points; public UI never receives private rows to filter in JavaScript. W6 owns app composition and scheduler wiring, and requests interface changes from their owners.
- W7 consumes a versioned release/state manifest from W6; no independent schema rewrite or migration-on-import. Unknown/newer schema fails validation and preserves old release.

## External paths (planned)

All archived root routes acquire `/melika` externally. Public API includes `/melika/v1/sources`, `/v1/artifacts`, `/v1/artifacts/{sha256}`, `/v1/gaps`, `/v1/profiles/{id}` (each relative to `/melika`), public download and Ubuntu dists/pool. These expose only reviewed public records; public counts, pagination, search, autocomplete and errors exclude restricted content. Health is process-only and ready checks need no external calls.

Private equivalents live under `/melika/private/`, including private search/API/download; login at `/melika/access/`, logout a CSRF-protected POST. No public alias for a private SHA/path, no public APT feed containing VPN data. Unauthenticated requests to known and unknown private artifacts share a consistent denial without existence/count disclosure. No permissive CORS. OpenAPI may describe generic schemas but may not embed private examples or URLs.

Default download method is GET/HEAD; admin mutations remain local CLI-only. Public unknown IDs return 404, no approved usable public copy 503, conflicting digest 409; never turn a timeout into absence. Restricted data needs authorization even when its hash is known and on HEAD/Range/conditional requests. No method or internal redirect bypass.

## Portable release contract (W6/W7)

Release layout proposal: `release.json` (commit, schema, architecture, image digests, base-path config, required runtime capabilities); `compose.yaml`; locally loadable image archives and checksum index; pinned keyrings/config; consistent `catalog.sqlite` backup; manifests and every referenced CAS object; separately provisioned secrets/session-signing material; private encrypted state backup. OS packages/runtime binaries needed for cold offline restore are part of preparation, not assumed downloadable later.

Proposed commands `preflight`, `backup`, `verify-release`, `restore --staging`, `smoke`, `cutover`, `rollback` are **not implemented**. W7 must provide real scripts under `deployment/scripts/`, specified flags and nonzero failures before the runbook is executable. They must never take arbitrary public archive uploads, overwrite active state during validation or print secret contents. [Synthetic drill](tools/rehearse_migration.py) is only a reproducible local evidence aid.
