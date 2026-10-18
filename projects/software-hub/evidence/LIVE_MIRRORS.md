# Accepted public mirror pilot and Rubika capability — 2026-10-18

Owner authorized real trusted-mirror downloads, Rubika tests, external-only payload placement, preservation of the existing website and post-task status/test entries. Owner then confirmed there is no bot token and requested hidden setup. Base `cbedff35a5efdec3371daf16e4a968326aa9e47e`; branch `docs/melika-consolidation-2026-10-17`. [Execution record](../tasks/W5-LIVE-MIRRORS.md), [phase ledger](LIVE_MIRROR_LEDGER.md), [operator pins/source hashes](mirrors-operator-source.json).

**Accepted:** three public exact-identity files at [TehNet downloads](https://tehnet.ir/software/#downloads). The active web image remains `sha256:ab4220407e6a35a6e3d4221b44f238f12b25b1081be4b03ce8a92276a60289fa`; no web image, template, WordPress/theme/Core/menu, Nginx file or running container was replaced/restarted in this task. Operator code lives separately at `/opt/tehnet-software/operations/mirrors-20261018`. Only the public registry and bounded network-operation state changed; auth/restricted/research bytes matched before/after.

| Exact download | Provider | Bytes | Independent identity source |
|---|---|---:|---|
| alpine-minirootfs-3.24.2-x86_64.tar.gz | mirror.mobinhost.com | 3701382 | [official checksum](https://dl-cdn.alpinelinux.org/alpine/v3.24/releases/x86_64/alpine-minirootfs-3.24.2-x86_64.tar.gz.sha256) and release metadata |
| alpine-minirootfs-3.24.2-aarch64.tar.gz | mirror.mobinhost.com | 4028030 | [official checksum](https://dl-cdn.alpinelinux.org/alpine/v3.24/releases/aarch64/alpine-minirootfs-3.24.2-aarch64.tar.gz.sha256) and release metadata |
| hello_2.10-3build1_amd64.deb | mirror.arvancloud.ir | 26006 | [Ubuntu package download/checksum page](https://packages.ubuntu.com/noble/amd64/hello/download) |

All full SHA256 values are pinned in [public-downloads.json](../catalog/public-downloads.json). The rootfs files are for containers/chroots; hello is explicitly an Ubuntu installation-example package. This is not a complete offline software collection, dependency closure, installer or native APT/APK signature-chain acceptance. Existing eight online install guides still use the client's APT sources; they do not fetch those eight tools from this three-file pilot.

Provider approval is scoped to direct links to publicly offered files: [official Alpine mirror list](https://mirrors.alpinelinux.org/), [MobinHost archive invitation/location](https://mirror.mobinhost.com/alpine/), [Arvan's Linux repository offer](https://www.arvancloud.ir/en/dev/linux-repository), and [official Arch mirror country listing](https://archlinux.org/mirrors/arvancloud.ir/). These were read, not treated as instructions to reconfigure the existing website. Original Linux research is unchanged and not automatically promoted to approved routing.

| Actual gate | Result / evidence |
|---|---|
| Official identity/location research | Official release checksums/size; public download offer; actual peers' RIPE RDAP country IR. [Pinned source/identity records](mirror-identity-evidence.json), [candidate HEAD results](mirror-head-qualification.json) |
| Real staging stream verification | 3/3 full hashes/sizes, 7755418 bytes, no payload files; only two metadata databases in qualification root. [Report](mirrors-mirror-full-qualification.json) |
| Provider protocol before activation | Each: HEAD200/exact length, GET Range206/exact 16-byte Content-Range, conditional304, full stream hash, valid TLS. [Report](mirrors-provider-delivery-qualification.json) |
| Live initial publication | Atomic public SQLite replacement after all files passed. [First refresh](mirrors-live-first-refresh.json). Backup `/root/tehnet-backups/20261018-144016-public-mirrors` |
| Origin end-to-end | Live TehNet GET/HEAD307 with Range/conditional headers to exact registered destination; client full bytes match, provider HEAD/Range/conditional checks pass. Existing website/canonical/noindex/menu, APIs/assets and private denials pass. [Report](mirrors-live-origin-mirrors.json) |
| Independent Windows public TLS | Same complete checks passed for all three files, no payload persisted. [Report](live-public-mirrors.json). First attempt timed out during the own-site TLS handshake after baseline requests; one unchanged bounded rerun passed. No TLS/deadline/verification requirement was relaxed |
| Actual constrained refresh service | ExecMainStatus0; read-only system, only public metadata/ops/lock writable; auth/restricted/research inaccessible. [State](mirrors-live-state.json) |
| Shared operation lock | Holding the actual lock deferred service with exit75 and unchanged verification timestamps. After release, real service exit0 advanced all three timestamps. Timer active/enabled with 20-minute OnUnitActive trigger, not a simulated clock |
| No website payload storage | Exactly five metadata/auth/ops DB files under subsystem state; zero payload files. Root/web catalog and registry mounts stay read-only; only auth writable in web container. All existing container IDs/images/ports and both Nginx files preserved |
| Final Linux full suite | **129/129**, zero skips/failures, 27.577s, exit0; [complete log](mirrors-linux-full-tests-accepted.txt). Prior 128/128,27.319s retained as earlier checkpoint |
| Final Windows full suite | **105 passed,24 Linux/GPG-only skipped**,129 total,9.215s,exit0; [complete log](mirrors-windows-full-tests.txt) |
| Original upstream probe | 18/18,0.002s,exit0. Original 22 attributed research blobs/189734 bytes are unchanged |
| Browser | Valid-TLS live downloads page visibly shows 3 links and copyable exact hash checks in existing palette. No warning/error console entries; screenshot kept in local outputs |

The 20-minute refresh consumes about 558390096 bytes/day for this set before bounded extra checks, below the durable 1GiB/day hard cap. Failed attempts count; every file is capped at512MiB/10s. A failed full verification publishes no partial registry; eligibility expires after one hour. There is no alternate-host/foreign fallback, arbitrary public fetch/proxy or local payload cache. HTTP307 exposes its destination and does not hide infrastructure or certify tariffs. [Operations/rollback/migration prerequisites](../deployment/PUBLIC_MIRRORS.md).

RIPE returned `87.107.152.0/23` IR for MobinHost and `185.143.233.0/24` IR/ANYCAST for Arvan's actual peer. Approved peer allocations are additionally checked before registry publication. Registry country is not proof of all physical CDN locations, user-side DNS, Iranian-ISP reachability or complete-outage independence. No domestic tariff or universal availability is accepted. IranServer refused the tested connection; Pardisco timed out and IUT transport failed; none is enabled as fallback.

## Rubika — actual result and remaining owner step

[Official methods](https://rubika.ir/botapi/methods) and [models](https://rubika.ir/botapi/models/) were rechecked. Actual invalid-token `getMe` over verified TLS reached `botapi.rubika.ir`: HTTP200,26-byte JSON with non-OK status. This is unauthenticated transport evidence. The Linux PTY fixture hid both token prompts, stored a disposable public test token0600 and removed its temp directory. The installed setup wrapper refuses pipes/arguments before touching state. [Capability evidence](mirrors-rubika-capability.json).

The owner has no production token; `/root/.config/tehnet-software-rubika/token` remains absent. Hidden owner setup and bounded in-memory fixture/recheck tools are ready; the web backend stays disabled. No actual credential upload/download, URL lifetime,24/72h retention, storage quota, distribution permission, deletion/recovery or private VPN delivery is accepted. The documented50MB general File ceiling is documentation only. [Copy/paste setup and probe procedure](../deployment/RUBIKA_PILOT.md).

## Failures and review, preserved honestly

- Initial new tests failed on missing modules, then Windows read-only-descriptor fsync failed with EBADF; a writable staging descriptor fixed it and tests passed. No live state was involved.
- One focused read-only review found two P2 issues: a token path elsewhere inside Git was allowed, and case-normalized returned hostnames could disclose token text. Red regressions reproduced both; repository-ancestor rejection and case-insensitive token/private-file-ID redaction passed before deployment. No real credentials were used. No duplicate/recursive review or external coding CLI ran.
- First Linux package lacked existing TLS fixtures and had a test assuming a checkout. Full diagnostics were read; fixture packaging and an explicit synthetic Git-root test fixed these harness issues. Final full suite passed. A later invalid retention-record test exposed accidental replacement upload semantics; strict record/date validation now rejects it before any API call, and final129/129 includes its regression.
- A Windows-to-Bash text pipe introduced CRLF at the first final-test harness line; Bash rejected `set -o pipefail` before tests/mutations. Binary LF transport fixed the harness. A staged document link check initially ran before this report existed; the final full verifier is required before publication.
- The first state-report dictionary dropped one duplicate systemd TimersMonotonic property; both triggers were retrieved separately and stored as a list. The20-minute trigger was verified explicitly. MemoryPeak was unavailable; no measured peak-memory claim is made.

Private state/keys/tokens/bearer URLs are outside Git. No messages were sent to chats, no personal Rubika session/account was used and no production password was configured. Iran migration under30min, future large artifacts and native offline installation remain separate unaccepted gates.
