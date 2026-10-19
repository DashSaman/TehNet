# Finite48h offline refresh observation

Current19October16:48UTC software/provider upgrade supersedes the historical image/source summaries below:active image and34web hashes are in [current engine manifest](../evidence/active-runtime-source.json);canonical producer alias is `offline-refresh-20261018-v3` with only two tested publication-pointer modules changed/42others unchanged. [Transition evidence](../evidence/provider-auto/producer-adopted.json) preserves old/new44hash manifests and original watch window/history/budgets. Four original watcher sources remain unchanged. Do not restore the historical4645434d image or old producer hash baseline over this accepted upgrade.

The same existing finite heartbeat now also follows [provider operations](PROVIDER_AUTO.md) and [next-publication task](../tasks/W4-PROVIDER-FOLLOWUP.md). It reads `provider-auto-state/latest.json`,the current SHA generation record,retained original proofs and public accepted-source API. Only exact-current passing sources may be selectable;waiting for new qualification is safe closure. Rehash each source's actual proof and validate current-profile binding/full downloads/offline install,isolation and native scheduled event before reporting a successor accepted. Keep failed/interrupted intents and quotas;do not manually replay completed labs. No extra collector or forced canonical publication is needed for follow-up.

Latest19October15:44UTC inventory reconciliation:[verified owner-authorized TunnelPannel release transition](../evidence/watch-heartbeat-20261019-1540/baseline-transition.json). Only its exact external container fingerprint changed in the private expected inventory;all other config fields,source hashes,dates,samples/events and budgets were preserved. The software engine remains the accepted4645434d image/current34file manifest. No watcher/producer code or timer changed,no extra collector/refresh was started. Do not restore an older external-container inventory over this legitimate owner deployment. The six native samples recorded through15:19:49UTC remain healthy and the original48h window continues.

19October authorized baseline transition: [source-status release and concurrent owner change](../evidence/SOURCE_STATUS.md) supersede the initial engine image/container inventory and one main-config hash. The exact owner-added TunnelPannel container/include and the new software engine were verified; original start/deadline/history,producer44source hashes and all other protected hashes remain. Current expected identities are in private watch config and [engine manifest](../evidence/active-runtime-source.json). Native14:19scheduled sample passed after transition. Never replay initial hardcoded-image setup or restore an older baseline over these accepted owner changes.

This is a read-only observer of [automatic refresh](AUTO_REFRESH.md),not a replacement producer or website change. Task: [W4-OFFLINE-WATCH-48H](../tasks/W4-OFFLINE-WATCH-48H.md). Evidence/status: [OFFLINE_WATCH](../evidence/OFFLINE_WATCH.md). The observation remains ongoing until the actual deadline; synthetic tests never certify elapsed48h.

## Installed operation

- Immutable current watcher code: `/opt/tehnet-software/operations/offline-watch-20261019-v2`; v1 retained as historical setup code.
- Private state: `/opt/tehnet-software/operations/offline-watch-state-20261019`.
- Start:2026-10-19T13:39:28.226058Z; deadline:2026-10-21T13:39:28.226058Z (Tehran17:09:28 on21October).
- `tehnet-software-offline-watch.timer`: every30min; enabled across reboot. The existing producer timer stays on its original6h schedule and original quotas. No forced qualification/publication.
- Read only `latest.json`,`scheduled-events.json`,individual `sample-*.json`,small accepted metadata under `publications/<profile-sha>/`,and terminal `completed.json`. Config/baseline hashes and installation baseline remain private; do not publish them wholesale.

```bash
systemctl status tehnet-software-offline-watch.timer
systemctl show tehnet-software-offline-watch.service -p Result -p ExecMainStatus
cat /opt/tehnet-software/operations/offline-watch-state-20261019/latest.json
journalctl -u tehnet-software-offline-watch.service --since today --no-pager
```

Routine follow-up reads existing samples; do not repeatedly start the collector just to poll. Initialization refuses an existing config and must never reset the start/deadline/history. A normal service start preserves config. Maximum128 samples; ordinary48h collection is approximately97 samples. Small signed profiles/proofs are retained,never package/rootfs/index archives. The observer does not contact mirrors or spend the producer's download budget. Only origin-loopback HTTPS requests are made by the server observer. Independent public HTTPS is checked by the conversation follow-up.

## Checks and truthful completion

Each sample checks producer timer/service/due status; original signatures and48h client-date policy; exact candidate SHA bound to the saved native clean-install proof; published candidate identity and zero-swap/noswap lab proof; four exact public-origin bytes; existing main/private routes; frozen producer source/site/research/container fingerprints and engine image/health; zero catalog payload files in the scanned `/opt/tehnet-software` tree. `/srv/tehnet-software` is inaccessible to the unit and private DBs are not opened. Existing application build/rollback wheels remain application code.

The observer holds the existing shared lock for consistent short observation,never the long producer pipeline lock; contention produces `deferred`. Bounds:128MiB RAM,swap0,CPU20%,32tasks,90s service,command/output limits,at most128 samples. Failed checks preserve an error sample and nonzero unit result. Failed producer timestamps before the latest accepted publication are historical; failed timestamps after it are actionable. A check older7h,a publication older20h or a stalled stage triggers diagnosis. No automatic policy weakening or unbounded retry.

Completion requires real elapsed48h,a healthy last sample,at least one accepted new profile inside this window and no observation gap greater75min. Deferred lock-contention samples do not count as health observations or fill coverage gaps. Pre-window publications do not count. `completed_pass` means the sampled checks passed; it is not continuous uptime/SLA measurement. `completed_with_incidents` retains repaired failures. Missing coverage/publication/final health yields `completed_incomplete`. On terminal collection the script writes `completed.json` and stops only its watch timer. A durable unit condition prevents further sampling if the timer is activated again after reboot. Final follow-up disables the finite watch timer and pauses its own heartbeat;both the canonical producer timer and new provider-auto timer must remain enabled.

## Follow-up and repair

A current-thread heartbeat was created/verified active at2h intervals with a finite occurrence limit. It reads this runbook and server state,records meaningful new publications/errors/completion,and stays quiet for unchanged healthy observations. First scheduling attempts were rejected by the tool; only one heartbeat was actually created. Do not create duplicates. Inspect the native automation card/config before updates. Local-file/SSH follow-up requires the local computer/app to be available; server sampling continues independently ([official scheduled-task guidance](https://developers.openai.com/training/walkthroughs/scheduled-tasks)).

Before diagnosing a failure,retrieve complete original producer/observer logs and immutable code; summary errors are not substitutes. Keep tokens/passwords/private evidence out of public Git. Repair only the observed related cause; preserve main site,private authentication,signatures,TLS,date rules and budgets. Never reset quota or clock,force publication,or replace failed samples with successful ones. If a legitimate tested producer repair changes its immutable code,record old/new reviewed source identities and update only the authorized producer-hash baseline; preserve start/deadline,protected-site baseline and sample history. Unknown site changes require diagnosis,not automatic rollback of owner edits.

After each meaningful stage update task,STATUS,CHANGELOG,ledger,and root HANDOFF/PROGRESS/TASKS. Commit/push only the existing authorized review branch after tests and native ref verification; never merge main. At the deadline retrieve the terminal sample,all observed publication receipts/installation proofs and native schedule events,check public HTTPS and preserved baseline,report exact coverage/incidents/limits,then disable the observer/heartbeat. Do not conclude48h acceptance from today's setup tests.
