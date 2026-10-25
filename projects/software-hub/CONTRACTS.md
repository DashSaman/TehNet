# Integration contracts for independent owners

> Current owner override (2026-10-17): no downloadable payloads on the website VPS. [ADR 0002](decisions/0002-external-payload-storage.md) supersedes historical local-CAS requirements. The engine keeps metadata only, redirects approved public downloads externally, and refuses private redirects. W2/W3/external-W5 engine is active after accepted same-host recovery/code rollback (2026-10-18); owner password setup, external private delivery, provider and Iran migration acceptance remain separate gates. See [external storage](EXTERNAL_STORAGE.md) and [engine operations](deployment/ENGINE_OPERATIONS.md).

Status: W0 v1 frozen; concrete models/schema and evidence in [contracts/README](contracts/README.md). W0 remains the sole contract owner; changes require a versioned decision and consumer acknowledgement. Original type/function/CLI contracts remain in [API_CONTRACT](research/upstream/Linux/API_CONTRACT.md), except the documented path relocation and privacy additions here. Never treat historical public endpoints as permission to return VPN records.

## Ownership and module interfaces

`app/models.py`, `app/config.py`, `app/db.py`, `app/migrations/`, and `contracts/openapi.json` belong to W0. Model changes go through W0 before parallel work. W0 must add `visibility: public|restricted`, deny-default import policy and a safe public DTO; restrict audit/probe details separately. Separate private persistence/object roots are preferred; using one DB requires every read/count/export to enforce the same policy and an explicit review.

- W3 consumes `SourceConfig`, `Artifact`, `ProbeBudget`; produces `ValidatedTarget`, `HttpObservation`, `ProbeResult`. No public routes; no code that enables sources on discovery.
- W4 consumes W3 guarded fetches; produces `VerifiedRelease`, `MetadataBundle`, `ImportStats`, exact native-APT profile manifests and `GapDecision`. `accepted_at` requires real matching logs, never a caller-provided boolean.
- W5 owns the metadata-only `ExternalRegistry.register_verified`, `artifact`, `list_artifacts`, `download_target`, bounded verification and private-capable external adapters. Storage returns opaque object identity/internal paths, never uncontrolled URLs or user-supplied paths. W2 decides access **before** delivery.
- W2 owns `AccessContext`, authentication/session validation, `require_restricted_access(request) -> AccessContext`, `public_projection(record) -> PublicDTO|None` and private-route delivery policy. A module without a validated context cannot serve a private object. W0 freezes exact concrete typed signatures before dependent coding.
- W6 consumes these components through service entry points; public UI never receives private rows to filter in JavaScript. W6 owns app composition and scheduler wiring, and requests interface changes from their owners.
- W7 consumes a versioned release/state manifest from W6; no independent schema rewrite or migration-on-import. Unknown/newer schema fails validation and preserves old release.

## External paths (v1 contract; capabilities individually gated)

All archived root routes acquire `/software` externally. Public API includes `/software/v1/sources`, `/v1/artifacts`, `/v1/artifacts/{sha256}`, `/v1/gaps`, `/v1/profiles/{id}` (each relative to `/software`), public download and Ubuntu dists/pool. These expose only reviewed public records; public counts, pagination, search, autocomplete and errors exclude restricted content. Health is process-only and ready checks need no external calls.

Private equivalents live under `/software/private/`, including private search/API/download; login at `/software/access/`, logout a CSRF-protected POST. No public alias for a private SHA/path, no public APT feed containing VPN data. Unauthenticated requests to known and unknown private artifacts share a consistent denial without existence/count disclosure. No permissive CORS. OpenAPI may describe generic schemas but may not embed private examples or URLs.

Default download method is GET/HEAD; admin mutations remain local CLI-only. Public unknown IDs return 404, no approved usable public copy 503, conflicting digest 409; never turn a timeout into absence. Restricted data needs authorization even when its hash is known and on HEAD/Range/conditional requests. No method or internal redirect bypass.

## Portable release contract (W6/W7)

Release layout proposal: `release.json` (commit, schema, architecture, image digests, base-path config, required runtime capabilities); `compose.yaml`; locally loadable image archives and checksum index; pinned keyrings/config; consistent `catalog.sqlite` backup; manifests and every referenced external provider object identity (payloads remain external); separately provisioned secrets/session-signing material; private encrypted state backup. OS packages/runtime binaries needed for cold offline restore are part of preparation, not assumed downloadable later.

The generic Iran cutover CLI names `preflight`, `backup`, `verify-release`, `restore --staging`, `smoke`, `cutover`, `rollback` remain proposals, not executable commands. The separate implemented `python3 -m app.recovery` validate/backup/staging-restore interface and `deployment/scripts/activate-engine.sh` are accepted for the current same-schema, same-host transition; see [RECOVERY](deployment/RECOVERY.md). W7 must supply and test the remaining cross-host cutover interface before that runbook is executable. No interface may accept arbitrary public archive uploads, overwrite active state during validation or print secret contents. [Synthetic drill](tools/rehearse_migration.py) is only a reproducible local evidence aid.

## Versioned engine interface update 1.1 — ADR 0002

Integrator acknowledges W2/W3/W5/W6 consumers: original schema 001 and frozen v1 ReleaseManifest retain their preview-only meaning. New auth and external registry databases have separate explicit schema version/identity checks. Do not label an engine/auth/registry release as a v1 preview release. Encrypted engine backup format 1 now covers all five databases, two optional engine configuration files and an immutable image identity with strict hashes/schema checks; same-host restore and code rollback passed. A comprehensive Iran cross-host release/cutover contract remains a W7 gate. The checked OpenAPI snapshot includes only public artifact DTOs and registered public download paths. No private examples or external policy fields are exported.

`Settings.metadata_dir` / `TEHNET_SOFTWARE_METADATA` names external **metadata**, never payload storage. `ExternalRegistry.register_verified(source, relative_path, artifact, guarded_client, license_approved, provenance)` is administrator-only and writes one metadata row only after `GuardedClient.verify_remote` hashes/discards the entire stream. `download_target` returns a registered URL for public records whose verification is at most one hour old; restricted records always raise StoreRejected. Private query methods validate a live AccessContext before reading. Future private delivery must change this contract through the integrator and provide its own no-spool/authorization evidence.

Current same-host acceptance: [engine activation](evidence/ENGINE_ACTIVATION.md) and [recovery](deployment/RECOVERY.md). Frozen v1 preview manifest retains its historical meaning; the implemented encrypted engine backup has its own format 1 and strict image/state contract. Generic future Iran cutover commands remain proposals unless explicitly implemented.
