# W5-CATALOG-EXPANSION — useful Linux and development downloads

- State: done
- Owner: Codex integrator, direct execution; no delegated helper.
- Claimed UTC: 2026-10-18T15:07:05.920036+00:00
- Branch: docs/melika-consolidation-2026-10-17
- Base: 7828a5e8a45aa9b15114daf570be005a2d4e91be
- Owned paths: public catalog, bounded mirror operator/tests, its isolated deployment helpers/units, this task/evidence/docs and append-only root coordination notes.
- Dependencies: accepted three-file mirror pilot and unchanged active engine image (see previous live evidence).
- Constraints: no WordPress/theme/menu/container/Nginx changes; no payload file/cache/spool; public metadata only; VPN/password and Rubika remain unchanged.

## Approved bounded design and acceptance

Add eight official Ubuntu 24.04 noble-updates tool packages (Git, curl, jq, Python minimal, pip, wget, rsync, OpenSSH client) after independent exact size/hash/license checks and actual full mirror verification. Keep all three existing identities immutable. These individual packages require dependencies and are not accepted offline bundles. Use the already approved Arvan source, same CIDR/TLS/no-redirect policy. No automatic version discovery or fallback.

At 17,066,942 bytes for 11 files, 20-minute refresh would exceed the 1 GiB/day quota. Use a 30-minute timer with a 150-second service deadline, retain hard quotas, one-hour routing expiry and restricted sandbox. Enforce max12 entries plus <=80% daily planned byte/request budget (49 runs includes one extra startup). Reject an over-budget manifest before network work. Review plan against actual qualified sizes before activation.

Use a new immutable operator directory and a scoped updater for the nonempty registry. Preserve previous public metadata and unit files, hold the shared lock for mutations, retain durable network counters and unknown metadata, restore only the scoped public snapshot/units on failure. Test rollback/refusal separately before live update. No site restart.

## Verification / actual work

Initial read-only source research: all eight official package download pages returned exact hashes/sizes; official copyright documents retrieved and fingerprinted. Nothing added to production yet. Phase evidence and results will be appended here and to STATUS/CHANGELOG/root notes after each stage.

## Remaining

Implementation/activation/tests completed; exact publication ref is obtained from Git history after this record is committed. Known follow-ups: existing guide wording, offline dependency/signature acceptance, Rubika/private delivery and Iranian-host cutover. No claim of native APT signature/clean-client installation, Rubika storage, ISP tariff/outage acceptance or Iran migration.

## 2026-10-18T15:11:49.247452+00:00 — catalog expansion / component-and-provider-tested

Official independent Ubuntu noble-updates package identities/copyrights recorded for Git, curl, jq, Python 3.12 minimal, pip, wget, rsync and OpenSSH client. Copyright documents for Wget and rsync explicitly refer to GPL-3 and linking exceptions; these unstructured documents do not use the DEP5 License field. Existing three manifest entries retain identical metadata/source/URL identities. No third provider or fallback enabled.

New bounded manifest tests first failed at old five-entry cap and missing scheduled-byte check; implementation now accepts at most12 and enforces <=80% of unchanged daily byte/request quotas before network. Windows harness initially lost its environment assignment through nested shell interpolation; switched to explicit subprocess environment. A new preservation fixture initially hit the intended one-second host backoff; advanced only its synthetic clock. Focused11/11 now pass (0.384s). Complete Windows135 total:111 passed,24 Linux/GPG-only skips,9.479s. Complete isolated Linux135/135 passed,zero skips/failures,28.228s.

Actual isolated full-stream qualification verified all11 files/17,066,942 bytes with exact independent SHA256/size, valid TLS and reviewed CIDR peers. Same real metadata was restored from11 rows to its empty snapshot; network usage remained charged and no payload/staging files remained. Provider-only acceptance then passed11 full hashes plus HEAD200, exact16-byte Range206/Content-Range and conditional304. Production catalog/site/auth remained untouched during qualification. Planned49 runs/day including startup:836,280,158 bytes and539 requests, below reserved80% thresholds; 30-minute refresh,150-second service,one-hour expiry,1GiB/1000 hard daily quotas retained. Scoped updater/rollback is under focused read-only review before production activation.

## 2026-10-18T15:14:39.974271+00:00 — catalog expansion / review-regressions-and-deployment-gate

The one focused static reviewer identified two updater rollback defects before live execution: failure immediately after database replacement could leave only the old fingerprint, and restoration command errors could still print success. Both were fixed: an exclusive/fsynced candidate fingerprint receipt is recorded before publication, rollback accepts only the exact old/candidate fingerprints, and every timer/service/unit restore step explicitly checks status. Unknown concurrent metadata remains rejected. No broad or duplicate review was performed.

Fresh failure-injection regressions execute a real publish-then-error and restore its exact previous metadata; Linux executes the actual rollback shell function with each of eight external steps failing, requires nonzero/no false PASS, and also tests the successful path. Fresh full Linux137/137 passed,zero skips/failures,28.159s; Windows137 total112 passed25 Linux/GPG/shell-only skipped,11.806s. Bash syntax and systemd-analyze verify passed. Original real provider qualification remains valid because pins/client/runtime are unchanged; new updater/operators are isolated from the active three-file pilot. Production activation is now the next scoped operation; no existing web source/container/Nginx/auth/Rubika change is authorized or required.

## 2026-10-18T15:16:33.645063+00:00 — catalog expansion / live-expanded

Scoped live updater activated11 public records at /software without changing/restarting Docker/Nginx/WordPress. The exact original3 metadata identities were checked before writing; previous public/network SQLite snapshots and exact unit files retained at /root/tehnet-backups/20261018-151445-catalog-expansion. Public registry published atomically after all complete hashes, with prepublication recovery receipt. Protected container/site/auth/restricted/research baselines matched after activation; current five-database recovery validator passed. Only public metadata/network counters and the owned mirror service/timer changed.

Actual new sandboxed service returned0. Timer uses30-minute cadence; service deadline150s for at most12 bounded10-second files plus serial host spacing. Hard1GiB/1000 daily quotas unchanged. Existing hidden Rubika helper remains at its original operator path; owner token/password not created. Origin/independent-client end-to-end and final filesystem/source/browser checks are running and not yet counted at this checkpoint.

## 2026-10-18T15:22:13.197426+00:00 — catalog expansion / accepted-live-delivery-and-recovery

Accepted live11 files including8 useful Ubuntu24.04 Linux/development tools. Origin and independent Windows public TLS each verified all17,066,942 bytes/full hashes/sizes,GET/HEAD307 exact no-store redirects,providerHEAD200/Range206/conditional304 and existing website/private denial checks. First independent attempt had own-site TLS EOF; complete failure retained,one unchanged bounded rerun passed. Browser displays new cards in existing palette,no warning/error logs; screenshot saved. Existing guide copy contains one historical not-active sentence,tracked as separate frontend wording work; no template/web-image change in this metadata-only task.

Actual production-snapshot metadata rehearsal11→3→11 passed0.020s with concurrent-edit refusal and unchanged live registry/budget. Actual shared lock75 preserved11 stamps,unlocked service0 advancedall11. Timer active/enabled30min;service150s/192MiB/strict sandbox. Current exact fiveDB state,no software payload/cache/spool. All container fingerprints,Nginx/auth/restricted/research bytes and unchanged active image/runtime source hashes verified. Audit harness initially missed CRLF normalization; corrected to existing manifest contract and passed,without runtime edits. Linux137/137,Windows112pass25platformskips;fresh source-copy/link/staged-ref verification and original probe run next. No Rubika/password/VPN/offline-Iran acceptance change. Current backup /root/tehnet-backups/20261018-151445-catalog-expansion. Publish existing review branch only; no merge to main. Full task/evidence and current copy/paste/operator docs updated.

## Final verification commands / integration

| Actual command | Environment | Exit/result |
|---|---|---|
| `python3 -m unittest discover -s tests -v` | Isolated Linux operator + frozen dependencies |0;137/137,28.159s |
| `python -m unittest discover -s tests -v` | Windows pinned development environment |0;112pass25platformskips,11.806s |
| `python3 -m tools.verify_mirror_delivery --providers-only` | Actual foreign VPS / exact11 pins |0;all full bytes/hash,HEAD/Range/conditional |
| `python3 -m tools.verify_mirror_delivery --origin` | Own origin with valid hostname TLS |0;site/private baseline +11 complete deliveries |
| `python -m tools.verify_mirror_delivery` | Independent Windows public TLS |First1/TLS EOF preserved;unchanged rerun0/all11 deliveries |
| `bash -n deployment/scripts/update-public-catalog.sh` and `systemd-analyze verify` owned units | Linux |0 |
| `python tools/verify_consolidation.py` | Local exact provenance/links/isolation |0;22 blobs189734bytes297 links |
| `python -m unittest discover -s research/upstream/Linux/tests -v` | Original preserved research probe |0;18/18,0.002s |

All phase records integrated into STATUS/CHANGELOG and append-only root PROGRESS/HANDOFF/TASKS. No original research or existing website source removed/edited. Source/deployed/runtime identity checks,actual lock/sandbox/timer and metadata-snapshot round trip are in the linked evidence. [Current accepted report](../evidence/CATALOG_EXPANSION.md). Next exact action: publish the existing separate review branch,verify remote refs/main and preserve DraftPR2; no merge. Follow-up source expansion requires a new11-file scoped transaction,not replay of the3-to11 updater.

Final staged gate passed:36 paths,whitespace clean,no credential-pattern matches (heuristic),all8 staged operator file hashes equal deployed bytes,client example bash syntax0. Final provenance/link rerun:22 blobs189734bytes297 links,website source changes0. No runtime change after accepted checks.
