# C0 verification — actual results

Date: 2026-10-17. Runtime: Windows 11, Python 3.12.10. Exact source ref `d77dd9db570b972e41b55a92c08716055009f994`; destination base `a84f46dad515c6151ef06c10dcea6e13dfde05a1`.

## Fresh checks

Commands below were run from repository root; full output/exit codes and UTC are in [checks.json](checks.json). The outer session used RTK proxy for complete Python unittest diagnostics.

| Check | Result |
|---|---|
| `python -m unittest discover -s projects/melika/tests -v` | 5 tests PASS, exit 0 |
| `python -m unittest discover -s projects/melika/research/upstream/Linux/tests -v` | 18 original research-probe tests PASS, exit 0; not real source/production APT tests |
| `python projects/melika/tools/verify_consolidation.py` | PASS: 22 blobs, 189,734 bytes, SHA-256 and Git blob identity; local Markdown targets valid; baseline site-code/config files unchanged; four root docs append-only |
| Python compilation of both new tools | PASS, exit 0 |
| Structured data parsing | 5 JSON files parsed; YAML parser available: True; 1 YAML files parsed |

Archived research `.gitattributes` disables newline conversion for upstream blobs so their hashes survive Windows/Linux checkout. Original source working tree was not edited; no source deletion is part of this work. Git staged whitespace/path checks and remote readback are recorded separately at publication.

## Synthetic local migration measurements

Reproduce with `python projects/melika/tools/rehearse_migration.py --payload-mib 16 --runs 3 --output <new-file-in-existing-directory>`. Each run has a fresh random 16 MiB payload plus SQLite snapshot/config, local uncompressed ZIP transfer, full file hashes/size and DB integrity/state verification. Cutover changes a synthetic pointer; rollback resolves to the existing original fixture and verifies its full state. It is not a service process restart.

| Run | Bundle bytes | Total seconds | Restore + verify seconds | Rollback + source verify seconds | Outcome |
|---|---:|---:|---:|---:|---|
| 1 | 16,822,905 | 0.324778 | 0.060722 | 0.032058 | PASS (fixture) |
| 2 | 16,822,905 | 0.235377 | 0.061487 | 0.027481 | PASS (fixture) |
| 3 | 16,822,905 | 0.226358 | 0.062467 | 0.027992 | PASS (fixture) |

Raw [strengthened drill](migration-local-v2.json) records exact UTC, phases and `production_migration_accepted: false`. The [first drill](migration-local.json) is historical and only checked the rollback pointer text. The strengthened test caught the absence of a rollback-target assertion; the tool now verifies the actual original fixture directory. Neither record measures Linux permissions, Docker, Nginx, TLS, DNS, WAN transfer, real catalog scale, authentication, foreign-to-Iran routing or actual outage recovery.

## Earlier failures and fixes

The initial five rehearsal tests failed as expected before the implementation existed; after implementation all five passed. A later stronger assertion failed because `rollback_target_exists` was not yet produced; the tool was updated to resolve/verify the existing original fixture, then all five passed again. The first measurement attempt failed because the output directory did not exist; creating the evidence directory resolved that setup issue. CLI evidence output requires a new file in an existing writable directory and refuses overwrites. These are not hidden production migration successes.

## Access and incomplete acceptance

- GitHub connection identifies DashSaman and reports admin/push permission on the public destination repository; a Git transport dry run also accepted a new branch. No force push/default-branch change is intended.
- `OFFLINE_SOFTWARE_CATALOG` is absent from the inspected source ref/history; targeted Downloads/Codex filename search found no original package. Prior chat reports a sandbox-only ZIP/patch. W1 remains blocked; its reported candidate/review/test counts were not verified.
- Current VPS SSH, Iranian target and authoritative DNS/TLS control were not supplied. Repository deployment evidence establishes the intended domain/runtime association but is historical; fresh public fetch of tehnet.ir was unavailable through the web tool.
- Docker CLI exists but daemon connection failed at `dockerDesktopLinuxEngine`. No Compose/Nginx/runtime deployment or Linux cold restore was run; no actual private VPN endpoint exists in this delivery.
- No provider upload/probe, Rubika retention/Range/permissions, clean real-client offline package installation, domestic tariff test, live migration, RTO/SLA or official certification is accepted by these checks.
- Existing application tests were not rerun: the change is isolated research/documentation and supporting local tools, and baseline website code/config is unchanged. No claim of fresh production website health is made.

## Publication gate

Final staged preflight passed: 59 paths (55 isolated files plus four append-only root notes); all 22 upstream hashes also matched the Git index; 139 local Markdown links resolved; `git diff --cached --check` exited 0; upstream newline attributes were verified unset for text conversion. No matches were found for private-key, GitHub-token, AWS access-ID or literal bearer patterns in staged text; this limited scan is not a full security audit. Source working tree remained clean and destination main still pointed to the recorded base before publication.

Before commit/push: stage only the isolated directory and the four append-only root documents, inspect the full relevant diff, validate checksums/links, run `git diff --cached --check`, scan for credentials/private artifacts and compare source/destination refs. Publish only a separate branch, verify its remote SHA/tree and preserve the existing main branch. Record final refs in the user-facing report rather than inventing a self-referential SHA here.
