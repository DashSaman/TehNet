# Accepted catalog expansion — 2026-10-18

The owner requested useful Linux/programming downloads from trusted mirrors, unchanged existing website, external-only payloads and recorded phase/test results. Base `7828a5e8a45aa9b15114daf570be005a2d4e91be`; existing review branch `docs/melika-consolidation-2026-10-17`. [Task](../tasks/W5-CATALOG-EXPANSION.md), [phase ledger](CATALOG_EXPANSION_LEDGER.md), [current operator procedure](../deployment/PUBLIC_MIRRORS.md).

**Accepted live:**11 exact files at [TehNet downloads](https://tehnet.ir/software/#downloads), adding8 tools below to the unchanged3 original identities. New files use the existing approved Arvan Ubuntu mirror; original2 Alpine rootfs files remain at MobinHost. Exact SHA256/size/path/source/CIDR/license/identity references are in [immutable pins](../catalog/public-downloads.json). New source claims are limited to the individual files tested, not an entire package tree.

| Added tool | Exact Ubuntu noble-updates version | Bytes |
|---|---|---:|
| Git version control | `1:2.43.0-1ubuntu7.3` | 3679758 |
| curl HTTP/TLS client | `8.5.0-2ubuntu10.15` | 226504 |
| jq JSON command line | `1.7.1-3ubuntu0.24.04.2` | 65694 |
| Python 3.12 minimal interpreter | `3.12.3-1ubuntu0.17` | 2334634 |
| Python pip package manager | `24.0+dfsg-1ubuntu1.3` | 1319940 |
| GNU Wget downloader | `1.21.4-1ubuntu4.5` | 334118 |
| rsync file synchronization | `3.2.7-1ubuntu1.5` | 442954 |
| OpenSSH client | `1:9.6p1-3ubuntu13.19` | 907922 |

All are Ubuntu24.04 amd64 except architecture-independent pip. These require dependencies and are not complete offline bundles. Python minimal is not a full development environment, and pip still needs package sources. [Client copy/paste instructions](../catalog/README.md). Official package pages/copyrights were fetched over HTTPS in memory; exact upstream identity/license references and copyright fingerprints are [recorded](catalog-expansion-official-identities.json). Wget/rsync's unstructured copyright documents explicitly refer to GPL-3 plus linking exceptions. Native APT/APK signed-index-chain and clean-client installation acceptance remain W4 work.

## Actual verification

| Gate | Observed result / evidence |
|---|---|
| Isolated full suite after review fixes | Linux137/137,zero skips/failures,28.159s,exit0. [Full log](catalog-expansion-linux-full-tests-accepted.txt) |
| Windows full suite |137 total112 passed25 Linux/GPG/shell-only skipped,11.806s,exit0. [Full log](catalog-expansion-windows-tests.txt) |
| Isolated actual mirror streams |11 exact hashes/sizes,17,066,942bytes,verified TLS/approved allocation peers,zero payload files. Full refresh then scoped restore to empty, network charges retained. [Report](catalog-expansion-catalog-full-qualification.json) |
| Provider protocol qualification |All11 full hashes,HEAD200/exact length,16-byte Range206/exact Content-Range,conditional304. [Report](catalog-expansion-provider-delivery-qualification.json) |
| Live publication |Atomic all-or-nothing11 records with prepublication recovery receipt; scoped backup `/root/tehnet-backups/20261018-151445-catalog-expansion`. [First refresh](catalog-expansion-live-first-refresh.json) |
| Origin end-to-end |All11 TehNet GET/HEAD307/no-store/exact registered URL,then all17,066,942 provider bytes/hash/size/HEAD/Range/conditional; existing routes/canonical/noindex/menu/assets,27 research rows,readiness and private denials passed. [Report](catalog-expansion-live-origin-delivery.json) |
| Independent Windows public TLS |Same complete11-file delivery and site/privacy checks passed,zero payload persistence. [Report](catalog-expansion-public-delivery.json). First attempt hit own-site TLS EOF; [complete first failure](catalog-expansion-public-delivery-first-failure.log) retained. One unchanged bounded rerun passed; no TLS/deadline weakening |
| Actual protected refresh service |Exit0;150s deadline,192MiB memory,strict read-only system,public metadata/ops/lock writable,auth/restricted/research inaccessible. Actual shared-lock deferral75 left timestamps unchanged; unlock0 advanced all11. [Live state and source hashes](catalog-expansion-live-state.json) |
| Timer and quota |Enabled/active30min OnUnitActive trigger,all repeated timer properties retained. Hard1000requests/1GiB unchanged.17,066,942bytes/run;49 planned runs836,280,158bytes/539requests,under80% limits. Max12entries and budget validation before network. One-hour routing expiry retained |
| Actual-snapshot rollback rehearsal |Disposable copies of real11/current and3/previous snapshots restored11→3→11 in0.020s; unknown concurrent edit refused,live registry/budget unchanged. [Report](catalog-expansion-live-snapshot-rollback-rehearsal.json). This is not live rollback or server migration |
| Website/state isolation |All existing container ID/image/port fingerprints,Nginx files and auth/restricted/research bytes matched before/after; active healthy/read-only image unchanged: `sha256:ab4220407e6a35a6e3d4221b44f238f12b25b1081be4b03ce8a92276a60289fa`. Every frozen runtime source hash matches local source and running container after CRLF→LF normalization |
| No website software storage |Exactly5 SQLite state files under `/srv/tehnet-software`,no payload/cache/spool. Full downloads are bounded streams discarded in RAM. No container/Nginx/WordPress restart was issued |
| Browser |Live11 cards/new tools visible in existing palette;copy-button status appears;no warning/error logs. Screenshot retained in local outputs. Native clipboard content was not independently certified by this check |

## Review and failures before acceptance

The one focused reviewer identified post-publication/pre-fingerprint recovery and false-positive rollback success defects before activation. The new receipt is exclusively created/fsynced before replacement; rollback accepts only old/candidate fingerprints. Unit/timer/service restore commands all check status. Regression tests inject a failure immediately after actual replacement and each of8 shell restoration failures; no unknown metadata or budget rollback is accepted. No broad/duplicate review or new provider access was used.

Initial component red tests found the old5-entry limit and absent schedule budget validation. A synthetic fixture initially hit its intended1s host backoff; its clock was corrected. Nested Windows shell quoting affected test/metadata harnesses only; explicit subprocess environments/files were used. Final state audit initially compared raw CRLF container bytes with the existing LF-normalized manifest; the complete hash mismatch was investigated, normalization corrected and exact source audit passed. No production source or verification rule was changed to pass these checks.

## Limits / next work

The existing WordPress/theme/Core/menu/Nginx/web image remain unchanged. Current27 research rows stay unapproved as a whole. Current online installation guides still use the client's configured repositories; one historical static sentence says archive downloads are not active. This metadata-only task leaves that frontend sentence untouched; its correction is a bounded future archive UI task, not a reason to alter the existing website during catalog publication.

Password remains for the owner to set; public listing/download/private denial checks passed and no VPN data was imported. Rubika real token remains absent and backend disabled; its original hidden setup helper remains installed. No Rubika upload/retention/restore,private external delivery,tariff/outage guarantee,clean offline install or Iranian-server cutover under30min is accepted. RIPE country IR/Arvan ANYCAST is registry evidence,not universal physical edge/ISP availability.

Adding further files requires fresh official pins/license review,real full/provider checks,reserved quota planning and a new scoped update for the now11-file registry. The initial installer and this exact3-to11 updater must not be blindly replayed. Keep current network charges and reconcile unknown metadata before any rollback. [Operations,backup and prepared-target migration prerequisites](../deployment/PUBLIC_MIRRORS.md).
