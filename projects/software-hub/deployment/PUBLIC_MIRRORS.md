# Public mirror pilot — operator procedure

Three exact public downloads are active at [TehNet](https://tehnet.ir/software/#downloads): Alpine 3.24.2 minirootfs for x86_64/aarch64 at MobinHost, and the GNU hello Ubuntu amd64 installation-example package at Arvan. These are individual files, not an accepted Ubuntu offline bundle or installer. The eight existing online installation guides still use the client's configured APT repositories. [Measured acceptance](../evidence/LIVE_MIRRORS.md) and [immutable public pins](../catalog/public-downloads.json) define the scope.

## Trust and placement

Operator approval is for low-volume direct links to the providers' public download offerings, not an agreement for unrestricted redistribution/storage. Independent official Alpine checksum/release metadata and Ubuntu's package page establish exact identities; provider public pages and official mirror listings establish the invitation to download. Native APK/APT signature-chain validation and clean-client installation remain separate W4 gates. No broader package tree, unsigned automatic package discovery or automatic host fallback is enabled.

The pilot's country classification uses official mirror listings plus independently queried RIPE RDAP allocations and measured TLS peers. Arvan's allocation is explicitly ANYCAST: registry country does not establish every physical edge location, user tariff, connectivity from every Iranian ISP or availability during international disconnection. `approved_cidrs` rejects a verification peer outside the individually reviewed allocations before publication; it does not control the visitor's DNS or provider after redirect. No domestic-tariff/outage guarantee is made.

Payloads stay on the provider. The website issues a no-store 307 to the exact registered URL; Range/HEAD/conditional delivery happens at that provider. The destination is visible. Verification hashes and discards 64 KiB chunks; it never creates a payload file. The root/research/registry web mounts are read-only. Registry publication temporarily creates only a small SQLite metadata copy in the private public-registry directory, preserves owner/mode and replaces that database atomically after **all** hashes pass. Readers finish their old snapshot or open the new one.

## Automatic verification

Installed operator code: `/opt/tehnet-software/operations/mirrors-20261018`. It uses the frozen active engine dependencies from `/opt/tehnet-software/releases/engine-active-20261018/host-site`; the web image is unchanged. No global dependency install is required.

`tehnet-software-mirrors.timer` invokes the tested service every 20 minutes with bounded jitter. The service has a 60-second limit, 192 MiB memory limit, read-only filesystem except public metadata/ops/operation lock, and no access to auth, restricted registry or research data. It shares `/run/lock/tehnet-software-engine.lock` with password/deploy/backup. Lock contention returns 75 without publishing; the next run retries normally. All operator metadata writers must use that lock; no public mutation route exists.

Each file has a 10-second verification deadline and a 512 MiB cap; durable quotas are 1,000 requests and 1 GiB full bytes/day. This three-file set is 7,755,418 bytes/run, about 558,390,096 bytes/day at 20-minute cadence before bounded extra checks. Failures also consume quota. An unsuccessful all-or-nothing refresh leaves existing verification stamps untouched; routing expires after one hour and returns 503. No stale-byte cache or foreign fallback masks a failure.

Read status or trigger the same sandboxed operation:

```sh
systemctl status tehnet-software-mirrors.timer --no-pager
systemctl show tehnet-software-mirrors.service -p Result -p ExecMainStatus
systemctl start tehnet-software-mirrors.service
```

Changing pins/host allocations requires fresh official identity/license/source review, isolated full verification, HEAD/Range checks and a scoped metadata transaction. Do not edit `verified_at` manually or bypass an expired result. The initial installer refuses a nonempty registry and existing unit names; it is not an updater and must not be blindly replayed.

## Backup and rollback

Initial pilot transaction: `/root/tehnet-backups/20261018-144016-public-mirrors`. It holds consistent previous public/network SQLite snapshots and protected container/site/private-state fingerprints. The initial installer has scoped failure traps; it refuses to overwrite unrecognized concurrent metadata. No live failure injection of the installer is claimed. Atomic publication/conflict/failure behavior has independent tests; the actual service and shared-lock deferral were executed.

To withdraw the pilot, stop/disable **only** its timer/service, acquire the engine operation lock, inspect current public identities against the exact transaction and preserve a fresh current snapshot. Restore only the previous public registry using an atomic same-filesystem metadata copy with its current UID/GID/mode. Preserve auth/restricted/research and current network usage counters. Unknown newer rows require reconciliation instead of a blind restore. Do not replay a whole-site or older auth backup for a public-download change. [Engine recovery](RECOVERY.md) covers the five-database encrypted backup separately.

For migration, preload pinned dependencies/code and mirror metadata, install/review these two unit files, and ensure their absolute release paths and shared lock point at the prepared target. Carry credentials separately. Provider payloads are not copied to the website. Independent target connectivity, restored auth checks and Iran cutover under 30 minutes remain unaccepted.
