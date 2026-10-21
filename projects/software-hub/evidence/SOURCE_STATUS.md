# Dated source checks and homepage correction —19October2026

Predecessor:f4e5711423cd19083a3b93eb9291fa83377314b4. [Task](../tasks/W1-SOURCE-STATUS.md). This corrects stale research presentation; it does not approve27download providers.

## Actual source results

[All27dated checks](../catalog/source-observations.json) used pinned public DNS,verified HTTPS,no redirects/HTTP fallback and bounded metadata bodies from the foreign VPS.

| Result | Count | Scope |
|---|---:|---|
| Signed noble-updates metadata accepted |4|ArvanCloud,LinuxMirrors.ir,Liara,Hamravesh; Ubuntu archive keyring,signature/date checks|
| HTTPS200 endpoint only |9|1Platform,Chabokan,Faraso,Myket,Pardis,Parsdev,Runflare,Shatel,Sindad; no install acceptance|
| Metadata rejected |1|MobinHost: `Stale mutable suite`; excluded from successful cards|
| Redirect not followed |2|HamDocker and Pishgaman|
| Connection not established from this vantage |11|DNS,timeout or certificate failure; not proof of global downtime|

Each complete pass permits at most40requests/5,505,024response-body bytes,4workers,64KiB endpoint bodies and512KiB signed metadata bodies. No package/rootfs/index archive is fetched or saved. Signature input exists only in `/run` during gpgv. A reporting serialization error (`datetime`) required a second bounded pass; a regression test now checks serialization. One targeted repeat diagnosed MobinHost freshness. Producer quotas were unchanged. No scheduled provider scraping was added,including Runflare.

The API preserves27public rows and disabled routing,projects only dated public fields,and excludes private rows/configuration. Checks older24hours become stale. These manual checks are separate from the existing automatic,clean-install-gated offline profile. No new provider receives unattended package-routing approval.

## Interface and verification

The homepage shows11actual external downloads,links the existing offline guide,and removes obsolete claims that downloads/offline installation have never been enabled. It displays13successful dated observations and14research/failure records in a collapsed disclosure. Each card states scope/time/foreign vantage. TehNet palette,fonts,theme,copy controls and private boundaries remain.

- [Red reproduction](source-status-red-tests.txt):the actual home test failed on the blanket badge;11other preview tests passed.
- [Final Windows](source-status-windows-final-tests.txt):176total,145passed/31Linux-specific skips,10.159s. [Six source-policy/probe tests](source-status-projection-tests.txt) cover stale/future data,public projection,bad signatures,redirect refusal and datetime serialization.
- [Full Linux](source-status/linux-tests.txt):176/176passed,28.847s. Original archived probe suite18/18passed0.003s; copied research unchanged.
- [Browser](source-status/browser-acceptance.json):13successful cards,14research cards,27dated results,11download cards,4offline links,no obsolete badge. Search and disclosure open/close passed. A checking script initially asserted the deliberately opened disclosure was closed; closing it restored the intended final state without a product change.
- [Public HTTPS](source-status/public-http.json):20checks/all4complete offline public-file hashes pass. [Main/private routes](source-status/public-main-privacy.json) and [origin](source-status/origin-acceptance.json) pass.

## Release, recovery and preservation

Current release:`/opt/tehnet-software/releases/engine-source-status-20261019`; image `sha256:3d01499c5a3c66b625abd95f113a4d37a156f6a230c4bb283cacac3237b3d8a6`. [30active file hashes](source-status/runtime.json), [current identity](active-runtime-source.json), [activation](source-status/activation-summary.json).

Built from the accepted local image with no network/package installation. Existing owner DPAPI recovery material was imported over SSH into a temporary protected GPG home,without a plaintext local export. Encrypted metadata restore,isolated network-none boot and code rollback rehearsal passed in13seconds; final activation9seconds. Timings exclude key/whole-site read-only backup preparation. Brief `/software`502occurred during restart; main routes stayed available. This is same-host acceptance,not an Iranian migration measurement. Temporary secret keys were removed and absence verified.

Complete offline Nginx aliases remained byte-identical. Only the software engine was replaced. Main WordPress/site content/config,private/research state,other containers,offline producer44frozen files/units/status/budget and mirror worker were preserved relative to pre-deployment state. [Storage audit](source-status/storage-postcheck.json):zero catalog payloads in scanned `/opt/tehnet-software` and `/srv/tehnet-software` trees. Pre-existing application build dependencies remain code.

Initial preflight rejected an unrelated new container/main-config change. Read-only investigation tied it to the owner's concurrent TunnelPannel request. The exact added container and sole added include were verified; removing that include reproduced the old main-config hash,and all prior container identities were unchanged. [Concurrent-change record](source-status/concurrent-owner-change.json). That owner change was preserved. The watch baseline records this addition plus the authorized software image/container transition,without weakening exact protected hashes or resetting time/history.

## Continuing observation

[Post-deployment watch](source-status/watch-postcheck.json):native14:19:21UTC scheduled sample healthy;4stored samples,0failures,0new in-window publications. Original19October13:39:28UTC–21October13:39:28UTC window preserved. Independent original-signature/exact-install-proof/origin/preservation checks passed. Offline profile still `433c86293ecbc675f78cef8efae426eef3612f2b22e22886b9eeb1a1e6b4cfca`,accepted06:26:39UTC; no forced publication.

Use current watch config/current engine manifest. Do not replay historical setup/activation scripts. Frozen producer source intentionally retains its old unused web main module; do not replace its44file manifest with web-only hashes. Historical one-time installation/catalog-expansion scripts pin the previous image and should refuse replay; normal30min mirror refresh remains unchanged. At the actual48h deadline report coverage/incidents/new publications and stop only the finite observer/heartbeat. Source-provider checks are dated manual observations; Iran access and continuous provider monitoring remain unaccepted.

Final repository checks:22original blobs/189734bytes and439local Markdown links verified; existing site files changed0,root coordination append-only. Scoped36staged paths,whitespace and credential-shape heuristic passed (not an exhaustive secret scan);30staged web hashes match installed/tested source and4watcher hashes are unchanged. Frozen producer manifest remains byte-identical,with only the intentional new-web versus old-producer main-module difference. Full relevant code diff reviewed. Pre-push native refs matched review predecessorf4e5711423cd19083a3b93eb9291fa83377314b4 and maina84f46dad515c6151ef06c10dcea6e13dfde05a1; publish only the existing draft review branch.
