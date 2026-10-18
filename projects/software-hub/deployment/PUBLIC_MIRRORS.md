# Bounded public catalog — operator procedure

Eleven exact downloads are active at [TehNet](https://tehnet.ir/software/#downloads): two Alpine minirootfs files at MobinHost; GNU hello plus Git, curl, jq, Python3.12-minimal, python3-pip, wget, rsync and openssh-client at Arvan. The eight tools target Ubuntu24.04 noble-updates; pip is architecture all, others amd64. [Versions, client instructions and dependency caveats](../catalog/README.md), [immutable pins](../catalog/public-downloads.json), [actual acceptance](../evidence/CATALOG_EXPANSION.md).

## Trust and placement

Source approvals remain the two original public download offerings, with exact reviewed CIDRs. Official Alpine/Ubuntu HTTPS metadata independently establishes identities; copyright links are preserved. Native APT/APK signature-chain validation and clean-client installation remain W4 gates. No automatic package discovery, version replacement, unreviewed host or alternate/foreign fallback is enabled. These are individual files, not dependency-complete offline bundles.

Mirror listings and RIPE country IR establish scoped provider/registry evidence. Arvan is ANYCAST: this does not certify every physical edge, visitor DNS, Iranian ISP reachability, domestic tariff or availability during international disconnection. Verification rejects peers outside the reviewed allocation before publication. Visitor delivery remains the provider's responsibility after the visible redirect.

The website returns no-store307 to the exact registered URL. Provider delivery handles HEAD/Range/conditionals. Full verification hashes/discards64KiB chunks without payload files. Only small SQLite metadata/auth/operations state lives on the site. All-or-nothing publication copies the public SQLite database, preserves UID/GID/mode, fsyncs and atomically replaces it after every hash passes. Other metadata rows are preserved by the refresh operator. There is no public registration/proxy endpoint.

## Active operator and limits

Current code: `/opt/tehnet-software/operations/catalog-expanded-20261018`; frozen dependencies: `/opt/tehnet-software/releases/engine-active-20261018/host-site`. The web image is unchanged. The original `/opt/tehnet-software/operations/mirrors-20261018` remains intact for previous3-file recovery and its hidden Rubika token helper; do not run its pilot installer again.

The enabled `tehnet-software-mirrors.timer` schedules every30min with <=30s jitter/15s accuracy. The service deadline is150s, memory192MiB,CPU50%, max32tasks, read-only filesystem except public metadata/ops/shared lock, and no access to auth/restricted/research state. Shared lock `/run/lock/tehnet-software-engine.lock` also covers deployment/password/backup. Contention returns75 and changes no verification stamps. Each file deadline10s/cap512MiB,1full worker,>=1s per-host spacing; hard quotas remain1000requests/1GiB/day. Every failure charges quota.

The11-file set totals17,066,942bytes/run. The old20min schedule would use1,228,819,824bytes/day and exceed quota. The new30min schedule uses819,213,216bytes/48runs; manifest planning reserves49runs including an extra startup:836,280,158bytes/539requests. Max12entries and planned <=80% byte/request quota are enforced before any network work. Another large file may exceed the reserve even below12entries. A150s service accommodates12*10s deadlines, serial spacing and publication. Measured successful11-file runs were much shorter; this is not a worst-network completion guarantee.

Failure publishes no partial registry; existing stamps expire after1h and affected downloads return503. A single missed30min run may approach expiry. No stale payload cache masks failures. Operators must review journal/quota/provider health before retrying; do not reset usage or falsify timestamps.

```sh
systemctl status tehnet-software-mirrors.timer --no-pager
systemctl show tehnet-software-mirrors.service -p Result -p ExecMainStatus
systemctl start tehnet-software-mirrors.service
```

## Scoped updater and backups

`deployment/scripts/update-public-catalog.sh` is the accepted3-to11 updater, not an arbitrary repeatable upgrade. It refuses existing metadata other than the exact original3 matching identities, requires qualified pins, active old timer, shared lock and exact active web image. It preserves public/network snapshots and old unit files under `/root/tehnet-backups/20261018-151445-catalog-expansion`. Network snapshots are evidence only: **never restore old network counters for this change**. It does not replace any website container, Nginx file, password or research/restricted database.

Before database replacement, the operator exclusively writes/fsyncs `candidate-current` containing the exact staged SQLite fingerprint. Rollback accepts only the recorded old/candidate fingerprints, so a failure immediately after replacement is recoverable while unknown concurrent metadata causes refusal. Every timer/service/unit restore operation checks exit status; failure reports `ROLLBACK_REQUIRES_OPERATOR`, not success. Sudden power loss or SIGKILL cannot run shell traps: inspect the protected transaction/receipt and reconcile before restarting the timer. Generic refresh assumes its caller holds the shared lock.

Tests include post-publication failure and restore, all eight rollback command failures, successful shell path, unknown concurrent writes, restricted-snapshot refusal and preserved budget. Disposable copies of actual live snapshots completed11→3→11 in0.020s with unchanged live registry/budget. This measured metadata rehearsal is not live rollback, whole-site recovery or Iran migration.

## Manual withdrawal / prepared-target migration

Stop only the owned timer/service; acquire the shared engine lock. Preserve a fresh current public snapshot and the current units. Compare **every** current digest,record,source,path against the accepted transaction pins; unknown/newer rows or changed identities require reconciliation. Restore the exact previous public snapshot with `tools.catalog_transaction.restore_public`, passing the freshly inspected current fingerprint. Restore the two backed-up service/timer files, check every command, daemon-reload and restart the previous timer. Keep current network/auth/restricted/research state. Reverify using the intact original3-file operator before counting old routes as available: the snapshot timestamps may have expired. Confirm actual service0, freshness, exact public3 identities, baseline/private denials and unchanged website fingerprints. Do not blindly restore a whole-site or auth backup for catalog withdrawal.

For migration preload frozen dependencies/code, public metadata and the owned units with reviewed target absolute paths/shared lock. Keep credentials separate. No provider payload needs copying to the website. Independent Iranian target connectivity, clean-client installation/auth restore and prepared-target cutover under30min remain unaccepted. [Engine recovery](RECOVERY.md) covers encrypted five-database recovery separately.
