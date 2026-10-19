# Automatic offline profile refresh

Automatic selected-source qualification now follows each accepted publication: [provider worker, current-profile gate and operations](PROVIDER_AUTO.md). The19October extension changes only `tools/offline_refresh.py` and `tools/offline_publication.py` in the frozen44-file producer: an owned relative `public/current` pointer switches before the existing Nginx publication transaction, restores on rollback and reconciles from the verified actual route after interruption. Old/new full manifests and the narrow watch source-hash transition are retained under [provider evidence](../evidence/PROVIDER_AUTO.md). The schedule, original canonical client/signature/freshness/install gates and all production quotas below remain unchanged.

Owner-authorized scope: keep the isolated `/software/offline/` profile fresh through actual signed qualification. No change to WordPress/theme/Core/menu,active web image,auth/Rubika or the eleven-file mirror worker. The48h client freshness rule remains enforced. This extends the [dated devtools procedure](OFFLINE_DEVTOOLS.md); original static acceptance remains historical evidence.

## Schedule and admission

`tehnet-software-offline-refresh.timer` checks every6h at00/06/12/18:20UTC with up to5min jitter,persistent across reboot. The oneshot service qualifies only when the last successful published test is at least12h old; therefore normal successful refresh intervals are12–18h. Lock conflicts defer with status75. The timer runs on the server independently of the desktop/Codex app.

The existing eleven-file worker retains its1GiB/day quota and30min schedule. **Additional offline-refresh allowance:**192MiB reserved before each attempt,max2 attempts/384MiB per UTC day; failed attempts remain charged. The ledger is fsynced including its directory before I/O; a backwards calendar day is refused. Each bounded request separately consumes a conservative size+64KiB reservation inside the attempt. This is a body/request reservation budget,not measured billing or TCP-header accounting. Rootfs acquisition is charged twice at40MiB cap,InRelease at2MiB each and every exact signed index/archive before fetch. No automatic redirects/proxies/foreign fallback or quota reset on failure.

## What must pass before publication

1. ExecStartPre verifies APT can change to its sandbox UID inside mount/network namespaces, before reserving bytes. Sufficient available RAM (>=1200MiB),owned operation locks and daily reservation are required. Current original signed24.04.5 Base/SHA sums/CD-image keyring remain pinned; Base/helper/installer trust changes are manual.
2. Three fresh InRelease files from the reviewed pinned HTTPS Arvan allocation. gpgv validates original Ubuntu signatures,all suite/origin names,date/future/expiry policies and nondecreasing Date relative to the live accepted profile. Six signed by-hash main/universe amd64 indices are fetched through caps. Native APT then reads **only file: sources in a disconnected namespace** to resolve actual candidate seed versions; no uncontrolled native APT WAN acquisition.
3. Independent builder verifies signed expanded index hashes and each selected package path/version/size/SHA256. The closure may change within<=200 packages/<=128MiB package bytes; the stricter overall request budget can refuse it before download. A number matching the old58 is not an acceptance gate.
4. A second fresh official Base root,private768MiB noswap RAM,download/recheck of all full package bytes,empty old package lists and network-isolated native installation with downloads forbidden. All exact package versions,empty dpkg audit,all8 functional tools and copyright files must pass. Corrupt/missing dependency,forged signature and newer nonseed dependency must each stop before dpkg status mutation. The evidence SHA256 must bind the exact unaccepted candidate; an old successful log cannot qualify a new profile.
5. Reverify original signatures and Date antirollback immediately before publication; mutable suites must be<=24h old at this boundary. Only then create accepted=true profile,proof,dynamic Persian guide and the unchanged helper in the four-file whitelist.
6. Persist publication intent with old snippet bytes/hash,new exact snippet hash and both code directories. Checked publication preserves the reviewed base proxy,tests Nginx,reloads and checks exact origin bytes plus all main/private acceptance routes. Any ordinary failure restores the previous snippet with checked syntax/reload. A stop/reboot during publication must reconcile actual origin/reload before any not-due decision; unexpected concurrent config edits are refused.

All payloads are on the external mirror or transient unswappable RAM; no website `.deb`,rootfs,cache or kit archive. Root/indices/archives disappear when each private mount namespace exits. Service bounds:900MiB RAM,swap0,CPU50%,96tasks,1200s total,600s per stage,2MiB per child log. The service sees `/srv/tehnet-software` as inaccessible and never opens private engine DBs. A separate operator live audit verifies the five state DB paths and private boundary; direct private DB hashing is intentionally not part of the automated sandbox.

The pipeline has its own `/run/lock/tehnet-software-offline-refresh.lock`; it holds the shared engine lock only for startup reconciliation and publication. Long qualification leaves the existing download worker free; publication reacquires the shared lock and refuses an intervening snippet change. Live acceptance allows the owner to have configured the private password,while still requiring unauthenticated private404/no-store. It neither reads nor sets that password. The system service defaults to root for the isolated chroot laboratory; the redundant User=root line is intentionally omitted after a measured host-specific CAP_SETUID/NoNewPrivileges failure. NoNewPrivileges and all other protection remain enabled; the preflight catches regressions.

## State, retention and failure inspection

Runtime code: `/opt/tehnet-software/operations/offline-refresh-20261018`.
Private state: `/opt/tehnet-software/operations/offline-refresh-state` (`status.json`,`daily-budget.json`,owned run subdirectories).
Each stage writes timestamp/result/run identity plus full bounded logs and evidence. The last published profile remains active on signature,transport,budget,resource,install or publication failure. Once its actual signed metadata becomes too old,client preparation intentionally refuses; no new system can guarantee safe fresh downloads during a prolonged external-source outage.

Retain at most12 generated operator runs (plus one in progress),protecting the active/current run; three automatic rollback backups and the public releases referenced by those backups/active release are retained. Only exact auto-owned name patterns/markers and validated whitelisted public metadata are eligible for pruning. Manual releases/backups,source research,engine DBs and daily ledger are never removed by retention. Keep external long-term evidence separately if required; retention is not an unlimited audit archive.

```bash
systemctl status tehnet-software-offline-refresh.timer
systemctl show tehnet-software-offline-refresh.service -p Result -p ExecMainStatus
journalctl -u tehnet-software-offline-refresh.service --since today --no-pager
cat /opt/tehnet-software/operations/offline-refresh-state/status.json
```

The owner may manually start a due check with `systemctl start tehnet-software-offline-refresh.service`; it still honors due-time/budget/lock. Do not delete/reset the ledger to retry. Inspect the failing run before repair. `--force` is an operator qualification option that bypasses only age,never quotas or acceptance gates. Separate explicitly recorded development qualification states are not the unattended production ledger.

## Disable, recover or migrate

Disable the timer before operator maintenance: `systemctl disable --now tehnet-software-offline-refresh.timer`. If the service is running,stopping it must retain its pending intent; next startup reconciles before a new attempt. Never restore daily counters from a backup. To revert a completed guide publication,use the recorded automatic backup's `nginx-software.before` under the existing engine lock,validate/reload and check main/private plus guide origin. Retain referenced public code directories. Do not restore engine/auth DBs for a guide-only rollback.

For an Iranian prepared target,copy the immutable runtime code,pinned host dependencies,Base signature/small seed metadata,current four public code/metadata files,owned snippet and private operational state. Preserve single-writer and budget accounting,validate current keyring/noswap support/resources and run actual qualification before enabling its timer. No package payload transfer through website storage is involved. A new under30min migration measurement is not implied by enabling this timer.

The current small operational backup is `/root/tehnet-backups/20261018-175541-offline-auto-operations`:10 files plus its hash manifest. Its restore round-trip checks code/metadata identity only; it never starts a second writer or overwrites a live ledger. Retain access0700 and copy it only to an operator-controlled location. For actual recovery,disable the old timer first,verify the manifest and immutable code hashes,restore the public files/unit configuration in their reviewed paths,and reconcile pending publication before enabling the target timer. Transfer the latest quiesced live ledger for migration; a stale backup counter must never replace a newer live counter. Guide-only rollback restores only the reviewed owned snippet under lock,then syntax/reload/main/private/origin checks. Keep old public directories until rollback acceptance succeeds. Full auth/database recovery still follows [RECOVERY](RECOVERY.md),not this small-state copy.

Read [automatic refresh acceptance](../evidence/AUTO_REFRESH.md) and the [stage ledger](../evidence/AUTO_REFRESH_LEDGER.md) for real execution/results. This document describes the contract; only recorded completed tests and installed/enabled unit evidence establish actual acceptance.
