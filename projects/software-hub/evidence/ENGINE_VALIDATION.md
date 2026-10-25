# External engine component validation — 2026-10-17

Base commit: `bc1b98ecf1579870ba0636c9d593de56a74ad7a0`. Review branch `docs/melika-consolidation-2026-10-17`. The [tested source manifest](engine-tested-source.json) records raw app/templates/static input hashes from the exact built tar bundle and canonical hashes verified against the final working tree. Normalization removes CRLF and trailing whitespace at EOF only; one trailing blank EOF was removed after the build. No executable change was made afterward.

Image: `sha256:b36c9957ad25882e2b552a4a84ec9f2aa8a7aecbb0a9e5284393d3b2c9df932f`. Staged release `/opt/tehnet-software/releases/engine-external-20261017-r2`; **not active on live site**. Build used the pinned Python base, `--network none`, no-index pip and 21 individually hashed runtime wheels. Test packages used requirements-dev.lock with hashes and offline local wheels, inside disposable tmpfs, not host Python.

| Check | Actual outcome |
|---|---|
| Linux final full suite `python -m unittest discover -s tests -v` | 98 passed, zero skips/failures, 117.536 s, exit 0; [full successful output](engine-linux-tests.txt) |
| Prior Linux validation | 95/95 + 3/3 operations passed before final canonical-target refactor; superseded by the full 98-test run above |
| Windows current full suite, separate dev venv | 98 total, 84 passed, 14 Linux-only skipped, 8.736 s, exit 0 |
| Original Linux research probe suite | 18 passed, 0.002 s, exit 0; immutable upstream not edited |
| Browser local-only fixture | Persian login; dark/light; password type=password; 390 px client/scroll widths both 390; no warning/error console entries |
| Live preservation after Linux build/tests | Existing container names/IDs/images/ports and Nginx/site snippet SHA-256 unchanged; six website routes pass HTTP smoke |

Linux command used: disposable `docker run --rm --network none --read-only --user 10001:10001 --cap-drop ALL --security-opt no-new-privileges:true --memory 384m --cpus .5 --pids-limit 64 --tmpfs /tmp:rw,exec,nosuid,size=256m`, staged tree mounted `/app:ro`, PYTHONPATH=/tmp/test-site; offline pip install then complete unittest. The first run lacked `exec` on **test-only** tmpfs, so native dependencies and fake shell tools could not execute. Complete failure was inspected and kept privately on the release. Corrected runner passed; production mounts were never changed.

Auth schema regression was demonstrated failing when credential table was missing but identity retained. Fixed schema checks reject missing tables/invalid credential state. The proposed CAS-backup restore implementation was withdrawn entirely after owner external-storage correction; neither its security nor a GPG recovery roundtrip is claimed. One focused read-only boundary review reported no concrete anonymous/revoked-session bypass in the inspected version; this is not a comprehensive security certification of the revised whole engine.

Fixtures are test-only: checked-in TLS server key is intentionally public and used only with its fixture CA; CA private key is not distributed or installed in system/production trust. No production password, Rubika token, private artifact or real provider agreement was used. Test fixture bytes were never imported into live storage.

Current live preview image remains `sha256:54f507b987e5a252a6f207478ddd5bb6251c8889c1ed45657857be017e314352`. No engine deployment, password setup, real provider activation, encrypted new-state recovery or Iran cutover occurred. [ADR 0002](../decisions/0002-external-payload-storage.md) and [operations](../deployment/ENGINE_OPERATIONS.md) define remaining gates. Component tests do not accept private external delivery, provider retention/quotas/Range, native offline install or under-30-minute migration.

Actual interactive terminal test: disposable network-disabled, read-only, UID 10001 container with the final immutable image, 192 MiB memory and separate /tmp test auth mount. Both getpass prompts accepted a public test-only password without echo; `set-password: OK` and `TERMINAL_FIXTURE_PASS_NO_PRODUCTION_STATE` observed. Test state was removed; /srv production auth was never mounted. This validates the hidden prompt/backend, not owner production setup or live login.
