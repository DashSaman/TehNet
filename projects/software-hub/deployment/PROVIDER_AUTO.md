# Automatic exact-profile provider qualification

This extends [provider kits](PROVIDER_KITS.md). The canonical publisher still checks the original Ubuntu signatures, freshness, hashes and its own clean offline installation before publishing. A separate native worker then downloads and installs the exact published profile independently from ArvanCloud, LinuxMirrors.ir, Liara and Hamravesh. Only passing sources for that exact profile appear at `/software/offline/sources/`. See [measured evidence](../evidence/PROVIDER_AUTO.md), [task](../tasks/W4-PROVIDER-AUTO.md) and [execution ledger](../evidence/PROVIDER_AUTO_LEDGER.md).

## Publication and immediate closure

The publisher owns `/opt/tehnet-software/public/current`, a relative symlink to a real sibling publication directory containing application code and small public metadata only. It switches this pointer before changing the owned Nginx aliases. If publication fails, the previous pointer is restored after the previous route passes reload. Interrupted publication recovery reconciles the pointer from the verified actual route before a not-due decision. A crash can temporarily close provider choices; it cannot carry old acceptance into a successor.

The web container mounts the public **directory** read-only at `/offline-public`; replacing a symlink is visible without restarting the container. It also reads the small dynamic `/metadata/public/provider-qualification.json` receipt. Every request compares the exact current raw profile SHA256, canonical acceptance binding, 48-hour freshness and package count with the provider receipts. Missing, stale, failed or foreign receipts never activate choices. It rechecks profile identity before returning choices. The public projection excludes private paths, error text, credentials and operator state.

Preparation commands fetch both `profile.json` and the public projected `sources/acceptance.json`. `provider_kit.py --qualification providers.json` requires an exact matching accepted source/profile before any package I/O. Both helpers remain hash-pinned; original Ubuntu signature, date, size and complete SHA256 verification remains mandatory. A concurrent generation change makes mismatching downloads/receipts stop safely. There is no arbitrary source URL, silent fallback or persistent payload cache.

## Timer, work and budgets

New units are `tehnet-software-provider-auto.timer`, `tehnet-software-provider-auto.service` and `tehnet-software-provider-lab@.service`. The timer observes after two minutes from boot, then two minutes after the previous controller becomes inactive, with up to15seconds accuracy. It does not force a canonical refresh. Four sources run sequentially; each gets a fresh Ubuntu Base24.04.5 amd64 root verified using the pinned CD signing key and a private768MiB noswap tmpfs. All six signed indices and every package are downloaded anew. Installation runs without network, followed by eight functional tool checks, empty dpkg audit and four invalid-input/nonmutation checks.

The dispatcher is limited to128MiB,swap0,20%CPU,32tasks and5400seconds. Each independent child is limited to900MiB,swap0,50%CPU,96tasks and1200seconds. `/srv/tehnet-software` is inaccessible inside a child. Admission requires at least1200MiB currently available RAM. The child holds the existing canonical qualification lock throughout payload work, including if the dispatcher dies. The controller refuses admission while an older child remains active. Protection snapshots use current hashes of the seed's owned file list plus the software snippet and current container inventory; they do not depend on the finite48-hour watch surviving.

Before I/O each exact profile/source intent durably reserves192MiB. Maximum four source attempts per profile and eight attempts/1536MiB per nondecreasing UTC day use a **separate** ledger. All failed charges survive. Existing canonical192MiB attempt/384MiB daily and mirror1GiB ledgers/schedules remain unchanged. Request-budget charges are conservative reservations, not measured wire traffic. The payloads live on external mirrors; temporary qualification downloads exist only in noswap RAM and disappear when the lab ends. Persistent local files contain code and small operational evidence only.

## Inspect and diagnose

Run as the existing authorized server operator; commands below do not request payload downloads:

```bash
sudo systemctl status tehnet-software-provider-auto.timer --no-pager
sudo systemctl status tehnet-software-provider-auto.service --no-pager
sudo cat /opt/tehnet-software/operations/provider-auto-state/latest.json
sudo journalctl -u tehnet-software-provider-auto.service -n 80 --no-pager
curl --fail --proto '=https' https://tehnet.ir/software/offline/sources/acceptance.json
```

The state directory holds `<profile-sha256>.json`, `daily-budget.json`, `latest.json` and `runs/<profile-sha256>-<fixed-provider>/metadata/`. Each attempted source retains its original journal, exact installation proof, download observations, network budget and isolation/preservation evidence. Deferred checks record the controller outcome without consuming an attempt. Failed/interrupted sources stay inactive for that profile; they are not silently retried. Diagnose the original log before a narrowly reviewed repair. Do not reset the ledger or delete intents to force acceptance. A genuinely new canonical profile receives new intents within the daily cap.

If the dispatcher dies after reserving an intent, restart marks it interrupted and never replays it. A surviving child remains independently bounded and retains its logs; the next controller waits for it before another admission. A newer profile supersedes old activation; old records remain. The worker atomically replaces only public receipts, never the publication pointer or canonical route. Errors before publication discovery are recorded in `latest.json` and systemd journal; lock conflicts return75 without changing acceptance.

## Recovery, migration and rollback

The existing [encrypted engine recovery](RECOVERY.md) covers five authoritative SQLite databases. Derived provider receipts and the provider operations ledger are **not** added to that database bundle. Before prepared-target migration, separately copy the small `provider-auto-state` tree, immutable tested worker release, three rendered units, seed signing metadata and owned public publication directories/pointer over the authorized encrypted operator channel. Preserve original modes, exact proof bytes, intents and charged budgets; never transfer package/rootfs/index archives. Stop the old dispatcher and wait for its child to finish before transferring state, then keep one writer. The original canonical producer's state and signing prerequisites follow [automatic refresh](AUTO_REFRESH.md). Validate source hashes, actual Nginx target/pointer identity, public proof binding, resource limits and timers on the prepared target before allowing downloads to be selected.

If receipts or operational proof cannot be recovered, close provider selection rather than restore unverified acceptance. Preserve the known ledger; reconstruct derived receipts only from exact matching retained proofs and current canonical profile after review. Missing budget history is not permission to reset its quota. Do not duplicate active dispatchers across servers. Existing [migration](MIGRATION.md) prerequisites/rollback and under30minute prepared-target goal remain; this task does not measure a real Iranian cutover.

To suspend new qualification, disable only the new provider timer and wait for any active child to finish:

```bash
sudo systemctl disable --now tehnet-software-provider-auto.timer
```

Preserve the canonical refresh timer and finite watch. Suspension does not make old receipts qualify a new generation. For code rollback, use a previously tested **gate-capable** release with the same durable state, pointer and receipt contract. The historical manual-selector image predates this contract: after a new generation it must not be restored as an active selector. If no compatible release exists, close the owned source selector while preserving the canonical offline guide, then repair/redeploy. Never restore an old database over newer writes. Live acceptance requires the complete current Nginx snippet, encrypted recovery/network-none boot/code rollback rehearsal, source identities and main/private/other-container preservation checks.

The actual48-hour watcher and its start/deadline/history remain independent. Legitimate producer changes to the two pointer-transaction modules require old/new manifests and a narrow tested source-hash transition under the existing locks, without resetting observation or hiding failed events. A future naturally scheduled canonical publication remains a separate observation until it really occurs.
