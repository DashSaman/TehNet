# Verified live preview — 2026-10-17

Public URL: https://tehnet.ir/software/ . Product name: آرشیو نرم‌افزار تهران نتورک. All statements below concern the limited public preview, not the completed archive engine.

## Actual release and protected baseline

- Destination: DashSaman/TehNet, separate review branch `docs/melika-consolidation-2026-10-17`, draft PR #2. No merge to main. W0 checkpoint 49c9452; first implementation 2d42f3ad6e9d39affd3d09aa73eee9a6b89a1006. Final publication ref is read back after committing; never insert a guessed self-SHA.
- Current release: `/opt/tehnet-software/releases/ui-20261017`; image `sha256:54f507b987e5a252a6f207478ddd5bb6251c8889c1ed45657857be017e314352` (tag ui-20261017 is a convenience, deployment used the immutable ID).
- Previous preview image: `sha256:8889969aff3f9889bd8e61809424d81fc6ee3485b6223468cf150af90f4fcceb`; first-install config release `/opt/tehnet-software/releases/preview-20261017-r3` retained.
- Validated private first-install backup: `/root/tehnet-backups/20261017-141739-software-preview`. Fresh update backup: `/root/tehnet-backups/20261017-143634-software-update`. DB/wp-content/config/env and failure logs stay private on the host.
- Existing WordPress port 127.0.0.1:18082 unchanged; new service only 127.0.0.1:18083. Existing container IDs/images/ports preserved. Single owned menu item ID 189 in menu 2; previous eight menu entries and order unchanged; repeated apply created no duplicate.
- Active theme/Core/page files unchanged. Only exact new Nginx prefix include, isolated service/data and authorized menu addition were applied. Read-only root/data; non-root 10001; 192 MiB / 0.5 CPU cap. Separate bridge is not physical egress denial. No upstream fetch feature exists.

## Tests and evidence

| Check | Actual result | Scope |
|---|---|---|
| Locked image build | PASS, network none | Immutable Python base + 16 hashed wheels, self-contained local fonts/JS |
| Linux suite | 36 PASS, 0 skipped, 44.346 s | Contracts 9, preview 11, synthetic rehearsal 5, initial deploy 9, update/rollback 2 |
| Windows suite | 25 PASS, 11 Linux-only skipped | First invocation from workspace root failed module import; correct project cwd passed; not a product defect |
| Original research tests | 18 PASS | Archived probe tests only |
| PHP menu | 5 logic checks + 2 lints PASS | Isolated helper plus real idempotency/menu check |
| Origin + independent public TLS | PASS | Existing pages 200/canonical/noindex/H1, single menu link; research API 27/all routing false; private methods 404/no-store |
| Browser | PASS within described scope | Exact live dark/light colors and Vazirmatn; eight guides; actual copy/paste `curl --version`; 390 px viewport with 375/375 client/scroll widths; no console warning/error |
| Cold process restore | PASS, 1.764 s | Same Linux host, actual 110592-byte SQLite snapshot, preloaded image, network none, read-only root/data; page/API/local CSS/JS/fonts served |
| Real Iran migration | NOT_ACCEPTED | No Iran target, WAN transfer, ingress/DNS switch, private auth or post-write rollback |

Machine-readable evidence: [Linux tests](linux-tests.json), [origin](live-origin.json), [public](live-public.json), [isolation](live-isolation.json), [browser](browser-ui.json), [preview restore](preview-linux-restore.json), [source tests](research-tests-current.json), [consolidation](consolidation-current.json), [release input hashes](release-inputs.json), [development lock dry run](dev-lock.json). All 18 deployed runtime input files match the local reviewed bytes. The development lock resolved all 19 exact hashed wheels offline in a disposable Linux container; no package install command was executed on the production host OS. The browser test did not run visitor package installs or prove offline dependency closure. A single initial RSS observation (~36.72 MiB) was not a load benchmark; current resource sizing still needs representative load.

## Failures and decisions retained

Three first-install attempts failed and rolled back safely: Docker internal-network port publishing incompatibility before route/menu; Nginx guard encountered both HTTP/HTTPS server names; immediate read after graceful reload reached an old worker. Corrected separate bridge, HTTPS-only insertion guard and bounded readiness polling were each verified before successful fourth install. Private failed-attempt backup suffixes: `140917`, `141243`, `141507` on 20261017. Exact failure logs and original configurations remain private.

The subsequent UI update recreated only the archive container. Two readiness probes returned transient 502 before readiness passed; this is a short archive-only restart window, not zero downtime. Existing containers were not restarted. Sandbox tests proved previous-image recovery after a partial update; a production update rollback was not deliberately forced.

## Remaining gates

No verified downloads, providers, APT profile acceptance, protected password/session implementation, Rubika, domestic tariff or regulatory approvals. Private paths deny requests; that is not implemented login. Original OFFLINE_SOFTWARE_CATALOG remains unavailable and owner-deferred. Real under-30-minute foreign-to-Iran migration requires the prerequisites, actual hosts and measured acceptance in [MIGRATION](../deployment/MIGRATION.md).
