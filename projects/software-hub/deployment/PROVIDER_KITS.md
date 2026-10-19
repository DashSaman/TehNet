# Explicit external provider kits

The `/software/offline/sources/` page offers a dated, tested **Ubuntu24.04 amd64 devtools kit** from accepted sources. It is separate from the frozen default profile producer and its six-hour timer. It does not approve a whole mirror, domestic tariffs or reachability during an Iranian outage. See [actual qualification results](../evidence/PROVIDER_KITS.md) and [task](../tasks/W4-PROVIDER-KITS.md).

## User preparation and offline install

On an Internet-connected Ubuntu24.04 amd64 workstation, open the source selector, choose one accepted source and copy its preparation command. Python3,curl,gpgv and the Ubuntu archive keyring must already be installed; follow the [full prerequisites](../OFFLINE_INSTALL.md). The command creates a new private working directory, downloads the canonical helper and provider wrapper from TehNet, checks both full SHA256 values, then fetches current accepted profile metadata. It prepares the kit directly from the chosen external mirror.

Each selected provider supplies all six signed by-hash package indices and every package archive. Original Ubuntu signatures, signed index hashes, package identities and full archive hashes are verified by the existing `offline_kit.py`. Liara has separate Ubuntu and Ubuntu-security paths. There is no cross-provider fallback. DNS must remain public and within reviewed address pins; HTTPS verifies the hostname and the actual pinned peer. Redirects, alternate origins and arbitrary URL input are refused.

Transfer the **whole** generated `kit` directory to the disconnected Ubuntu24.04 amd64 target. Read its package/version list and the prerequisite guide, then run `sudo bash ./install.sh` from inside the directory. Existing incompatible/newer installed dependencies cause a stop. Do not place the kit on the website VPS. The website serves application code and small proof/profile metadata only; it never proxies or caches these package payloads.

The client checks the currently accepted profile again at preparation time. A dated provider installation receipt applies to the exact tested profile. A later profile's fresh signatures and full hashes are checked during preparation, but its installation from each alternative provider has not automatically been retested. The canonical publisher continues to require its own clean installation before publication. Extended mirror outage or changed IP pins can stop preparation safely.

## Acceptance and reproducibility

`catalog/provider-qualification.json` holds small accepted receipts; `app/provider_kit.py:QUALIFIED_SOURCES` must contain exactly those accepted IDs. The page projects only known public IDs with matching profile identity,complete download count,all8tools,clean installation and all4negative checks. It never exposes private catalog/configuration. The public JSON is an engineering receipt,not a new cryptographic signature; the actual Ubuntu signature chain is independently rechecked by the client.

Operator requalification reuses `tools/provider_lab.py` around the existing `deployment/qualification/run-devtools-lab.sh`; it preserves its clean signed Base root,network-disconnected install,full hash checks,corrupt/missing archive,forged signed metadata and newer dependency rejection. Run sources sequentially,each with a fresh root and no downloaded-file reuse. Review the fixed source/IP/suite mapping first. Reserve a finite attempt allowance **before** network I/O in an independent ledger; failed attempts stay charged. Never reset or borrow the production refresh ledger.

The recorded run used a private768MiB `noswap` tmpfs,900MiB cgroup memory limit,`MemorySwapMax=0`,50%CPU,96tasks and a finite unit deadline. The website's `/srv/tehnet-software` was inaccessible to each lab. Only small metadata/logs were written persistently. Host swap usage is a separate measurement; it is not claimed to be zero. The original three fast transports retain the canonical30second request bound. LinuxMirrors uses a size-aware absolute30–300second bound with10second socket idle timeout; its timeout abort shuts down the socket without closing buffered readers concurrently. Full size/hash/HTTPS checks remain mandatory.

Before adding a receipt, validate it with `tools.offline_refresh.validate_acceptance`,rehash the exact original proof,check64complete downloads,58packages/eight tools/fournegative cases,empty `dpkg --audit`,noswap/cgroup and protected-file/container preservation. Preserve failed attempts beside successful reruns. The run-specific service/controller/ledger is finite manual qualification,not a new recurring automatic publisher.

## Deploy, preserve and roll back

Deploy only the software engine after fresh Windows and pinned-dependency Linux tests and the existing encrypted state recovery,network-none restored boot and same-schema code rollback rehearsal. Preserve the complete live Nginx software snippet,including all exact canonical offline aliases; the new selector/wrapper are served through the existing app prefix,requiring no new main-site route. Do not alter WordPress,VPN credentials/private catalogs,Rubika,other containers,the canonical producer source or its timers/budget.

Use the existing [engine operations](ENGINE_OPERATIONS.md) and [backup recovery](RECOVERY.md) procedures. Under the watch lock,verify the old baseline and change only the owned engine image/container fingerprint after successful activation; preserve original48h start/deadline/history and all protected/source hashes. On failure,roll back the software image with the saved complete snippet while retaining newer operational state; do not restore an old live database over newer writes. The accepted deployment evidence records actual timings,images and postchecks.

For future migration,use [the prepared-target migration procedure](MIGRATION.md). These extra provider choices add only code and small receipts; no payload disk or bulk transfer step is introduced. The under30minute target remains conditional on the documented prerequisites and measured rehearsal,not a newly measured Iranian cutover in this task.
