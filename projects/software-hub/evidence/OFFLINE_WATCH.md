# 48h observation — setup accepted,real window ongoing

Predecessor `cdb01c02b4e1e1af77c4c2aa6dcde9bbae20dfbf`; [task](../tasks/W4-OFFLINE-WATCH-48H.md), [operation](../deployment/OFFLINE_WATCH.md), [stage ledger](OFFLINE_WATCH_LEDGER.md).

Window **2026-10-19T13:39:28.226058Z through2026-10-21T13:39:28.226058Z**. The latter is21October17:09:28 Tehran. Initial state is `observing`,not48h complete. [Activation](watch-activation.json), [latest captured sample](watch-start/latest.json).

## Already observed scheduled successor

After the prior manual activation,the native refresh service started2026-10-19T06:23:20Z and published at06:26:39.147044Z (Tehran09:56). The new profile SHA256 is `433c86293ecbc675f78cef8efae426eef3612f2b22e22886b9eeb1a1e6b4cfca`. Stage events show signed discovery,independent builder,clean offline install,qualified and checked publication. Later12:20:53UTC timer check returned `not_due`; timer enabled/active,result0,today one192MiB reservation. [Sanitized native events](watch-start/pre-window-scheduled-events.json), [installed acceptance](watch-start/publication/offline-install-acceptance.json), [lab isolation](watch-start/publication/lab-state.json), [publication receipt](watch-start/publication/publication.json), [current signed profile](watch-start/publication/profile.json).

This real scheduled successor predates the fresh monitoring window and is **not** counted as its required in-window new publication. The old failure timestamp18October17:39 precedes the new successful acceptance and is not a fresh failure. No producer repair was justified by initial evidence; no forced refresh/quota reset or signature relaxation.

## Setup validation

- Policy TDD:4 initial expected assertion failures/1 partial-window pass; implementation5/5 passed. Tests reject early completion,old-only publication,coverage gaps,clock reversal and lost repaired incidents. Exact final Linux suite [168/168 passed29.130s](watch-v1-linux-tests.txt). [Windows](watch-windows-full-tests.txt):137passed/31Linux-specific skips,10.221s.
- Exact hardened-unit QA [sample](watch-start/qa-latest.json) healthy; it uses separate QA state and does not count as real48h coverage.
- Real initial and normal watch service executions produced2 healthy samples. Deadline/config remained byte-identical; producer unit files,daily budget and owned Nginx snippet remained byte-identical. [Activation](watch-activation.json), [tested/installed watcher hashes](watch-runtime.json).
- Server collector validates signatures and exact installed-candidate binding,main/private origin routes,producer/site/research/container preservation and no catalog payloads in the scanned tree. It fetches no package payloads and cannot open private engine DBs. Finite bounds,history and outcome classifications are described in the runbook.
- One current-thread2h heartbeat created and verified active. Two rejected schedule forms created no automation; the successful form has a finite occurrence limit and explicit deadline/stop instructions. Do not equate its creation with observed future runs. Server sampling is independent of desktop availability.

[Independent public HTTPS](watch-public-http.json):20 checks and all4 complete public hashes pass; [main/private checks](watch-public-main-privacy.json) pass. [Server audit](watch-final-live-state.json) verifies original5stateDB paths,unchanged site/auth/restricted/research/container/runtime/operator fingerprints,original11-file30min timer and no catalog payloads in scanned software trees/no laboratory mounts. The110 old hash-locked application build/rollback wheels20523643bytes remain unchanged. [Follow-up setup](watch-followup.json) exports no personal automation/thread identifier. Provenance/link check:22 blobs/189734bytes and400 links passed before final README links; final link count is recorded in task/ledger.

Future half-hour samples,scheduled successor inside the window,incident repair if needed,and real48h terminal coverage remain pending. No host reboot,bootedVM,Iran access,outage independence or new migration measurement is claimed.

## Observer-only correction before terminal acceptance

Self-review found deferred lock samples were incorrectly filling health-coverage gaps. A new test with healthy endpoints and95deferred samples reproduced false `completed_pass`; the corrected computation uses only actual nondeferred observations. [Final Linux169/169,27.889s](watch-v2-linux-tests.txt); final Windows138passed/31Linux-specific skips9.899s; six policy tests pass. This was a synthetic observer accounting defect,not a producer failure or an actual lost48h observation.

Exact hardened v2 QA passed; [live upgrade](watch-upgrade-v2.json) preserved the original entire config,start/deadline and both previous sample hashes. It produced the third healthy real sample and changed only the watcher service/code. Producer units,budget and owned snippet remained unchanged. [Current four installed/tested hashes](watch-runtime.json); [v1 identity](watch-runtime-v1.json) remains historical. No window reset or forced refresh. Current phase remains `observing`; no in-window successor is claimed yet.
