# TehNet Software Archive change log

Append dated entries; do not erase prior limits when a later phase passes.

## 2026-10-17 — C0 research consolidation and design

Predecessor destination commit: `a84f46dad515c6151ef06c10dcea6e13dfde05a1`.

Copied all 22 tracked Linux files from `DashSaman/software` ref `d77dd9db570b972e41b55a92c08716055009f994` as exact Git blob bytes into an isolated research archive; added per-file hashes and attribution. Original research was not removed. Recorded unavailable OFFLINE_SOFTWARE_CATALOG instead of synthesizing it.

Added Persian entry guide, architecture/contract/privacy design, phased roadmap, independently owned workstreams, task update contract, subpath deployment design and prepared-target migration/rollback runbook. Added a stdlib-only synthetic local SQLite/bundle/cutover/rollback rehearsal and safety tests; its measurements remain explicitly separate from runtime/network acceptance. Minimal root documentation pointers preserve existing TehNet priorities.

Actual fresh check results and environment limits are in `evidence/VALIDATION.md`; current source has no application deployment, protected VPN implementation, Rubika acceptance or real Iranian migration test. Publication refs must be read back from GitHub; this entry does not invent its own commit SHA.

## 2026-10-17 — W0 v1 and TehNet naming

Owner clarified that this is TehNet's software archive. Moved active project to projects/software-hub and chose /software/. Preserved original source names/hashes and historical logs for attribution. Implemented concrete visibility/source/artifact/release contracts, versioned deny-default SQLite schema, checked initialization, read-only state access and WAL-safe snapshot. Nine W0 tests pass. Public preview is next; source routing/private data/real migration remain unaccepted.
