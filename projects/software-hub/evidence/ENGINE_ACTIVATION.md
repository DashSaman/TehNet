# Engine activation and recovery acceptance — 2026-10-18

Owner authorized real backup/restore/code rollback and activation on `/software` while preserving WordPress, external-only payloads and owner password setup. Base `e35ce964d7a9a25b496cafa1ede52d4b168a5bc5`; review branch `docs/melika-consolidation-2026-10-17`. Source manifest: [active runtime](active-runtime-source.json). Original research/migration 001 are unchanged.

**Active:** `https://tehnet.ir/software/`, image `sha256:ab4220407e6a35a6e3d4221b44f238f12b25b1081be4b03ce8a92276a60289fa`, release `/opt/tehnet-software/releases/engine-active-20261018`. Password remains **unset**; generic access returns 503 and private methods deny 404 until the owner configures it. No production password was generated, demonstrated or transmitted. Public research stays available; no real external software/provider or private file delivery is accepted by activation.

| Gate / command | Actual result |
|---|---|
| Locked offline image build | PASS; pinned runtime/test wheels; host dependencies isolated under release/host-site, not installed globally |
| Linux full `python3 -m unittest discover -s tests -v` | 111 passed, zero skips/failures, 27.552 s, exit 0; [complete output](activation-engine-full-tests.txt) |
| Real GPG recovery tests | 8 passed, 1.775 s; [output](activation-recovery-tests-v2.txt) |
| Actual shell fault flow with isolated fake services | 5 passed, 6.996 s; [output](activation-activation-tests.txt): backup failure, partial new-container failure, TERM, rehearsal and success; newer state write retained |
| Windows full suite | 111 total, 87 passed, 24 Linux/GPG-only skipped, 13.354 s, exit 0 |
| Original upstream probe | 18 passed, 0.002 s, exit 0 |
| Real same-host prefix rehearsal | PASS, 12 s after preparation; encrypted state/config restore + network-none cold boot + new image + exact prior image/composition/snippet rollback; [log](activation-live-rehearse.log) |
| Final activation | PASS, 8 s after preparation; [log](activation-live-activate.log) |
| Database consistency | All five active DB byte hashes equal before/after rehearsal and final activation; code rollback did not restore stale DBs |
| Existing website | Other container names/IDs/images/ports and main Nginx site hash preserved; six routes/canonical/noindex/menu-link checks pass; only archive container and owned snippet changed |
| Origin and independent public TLS | 19 checks each; [origin](activation-engine-origin-verification.json), [public](engine-public-verification.json) |
| Live container/state | Healthy, read-only root and research/metadata mounts, auth-only writable persistence, exactly five DB files, zero software payload files; [state](activation-activation-state.json) |
| Browser | Valid-TLS live access page visibly requires owner setup; TehNet colors, no browser warning/error log entries; screenshot kept in local outputs |

Private transaction locations: rehearsal `/root/tehnet-backups/20261018-135929-software-engine-rehearse`; activation `/root/tehnet-backups/20261018-140051-software-engine-activate`. Each includes a fresh protected whole-site backup, encrypted engine state/config, trusted ciphertext hash result, staged verified state and exact previous image/composition/snippet. Engine ciphertext is 215529 bytes; its independent owner-machine copy matches the trusted hash. Key/ciphertext/private DB bytes are excluded from Git and public outputs.

The owner recovery key is protected by CurrentUser DPAPI with owner/SYSTEM-only ACL outside the Git repository. It was privately exported once and imported into a fresh server GPG home, matching the independent public fingerprint, for actual recovery. Temporary raw exports were removed. After off-server ciphertext/hash verification, both server bootstrap/import secret keys and agents were removed and empty private-key directories verified; only the permanent public recipient remains. Recovery now needs the owner-controlled key/profile, not a secret left on the VPS. [Procedure and limits](../deployment/RECOVERY.md).

Observed failures were resolved before activation: initial isolated pip target was unwritable under UID10001 (rerun as root only in a disposable read-only/network-disabled installer targeting new release/host-site); GPG2.4.4 emitted AES256-OCB rather than legacy-only MDC status (strict authenticated status parser corrected using official documentation, regression included); the first private export transfer preceded its destination directory (retried after preparation). Full diagnostic logs remain privately on the staged release; no failed run was counted as acceptance. A single focused static recovery review reported no concrete finding and did not run tests.

Archive requests briefly returned 502 during container replacement; no zero-downtime claim. Timings exclude initial installation/key/whole-site backup preparation. This is same-host metadata recovery/code rollback, **not** Iran/WAN/DNS migration, provider retention/Range/permission acceptance, APT offline installation or accepted external private downloads. No two active auth writers; restored boot used a separate state copy. Real Iran migration under 30 minutes remains NOT_ACCEPTED. Future cross-host post-write reconciliation and disaster recovery on a separate Iranian machine remain separate gates.

Evidence publication: Compose progress-line trailing spaces were removed from the two sanitized transaction logs after the staged whitespace check detected them; log text/results are unchanged. Latest Windows full rerun: 111 total, 87 passed, 24 Linux/GPG-only skipped, 9.056 s, exit 0. Final source-copy verifier checked 237 Markdown links.
