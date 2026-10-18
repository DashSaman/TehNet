# Accepted engine recovery and code rollback — 2026-10-18

Scope: TehNet software engine only. External software payloads remain external. No WordPress/theme/Core/database restore or unrelated container restart is part of an engine recovery. [Activation evidence](../evidence/ENGINE_ACTIVATION.md) distinguishes tests, real same-host rehearsal and foreign-to-Iran acceptance.

## State and trust

`app.recovery` implements explicit `validate`, `backup` and **staging-only** `restore`. Format 1 permits exactly five SQLite files and optionally the two engine configuration files: research catalog, public/restricted external registries, auth and operational budget. No uploads, arbitrary archive paths or software payload members. Each member is capped at 64 MiB, total 256 MiB. Schema 001 is immutable; new versions require new validators before deployment. SQLite integrity/FK checks, actual table/index definitions, migration identity and semantic/auth checks are required, not only an identity row.

Stop the archive writer and prevent concurrent admin imports before a multi-database backup. Use the engine operation lock for deployment, password setup, backup and any future metadata worker. The current web process writes only auth; registries/research are mounted read-only and there is no scheduler. Do not copy live DB files or declare cross-database consistency while writers run. The backup uses SQLite's consistent backup API into a private temporary metadata directory, then encrypts the bounded tar stream. Destination must be new and outside active state.

Encryption uses recipient-pinned GPG AES256 with authenticated MDC or OCB. Restore requires **independently trusted ciphertext SHA-256** as well as successful GPG decryption/integrity status. A SHA inside an untrusted downloaded archive does not establish sender trust. Keep the emitted `backup-result.json` with the protected owner copy, separate from any untrusted storage. Unknown members, duplicate JSON/members, plaintext `gpg --store` packets, modified ciphertext, unsupported schemas and existing restore targets fail closed. No active file is overwritten. Restored sessions, login challenges/throttle and live worker leases are invalidated before a verified marker is written.

GPG 2.4.4 on the measured host selected OCB. Its documented DECRYPTION_INFO reports AEAD separately from MDC; the initial legacy-only parser failed closed and was corrected using [upstream DETAILS](https://github.com/gpg/gnupg/blob/master/doc/DETAILS) and the [official GPG manual](https://gnupg.org/documentation/manuals/gnupg24/gpg.1.html). No integrity-ignore option is used. A public encryption key alone cannot authenticate an arbitrary sender; the independently kept ciphertext hash remains mandatory.

## Keys outside the server

The production server retains only its public recipient keyring at `/root/.config/tehnet-software-backup/public-keyring` and fingerprint in `recipient.txt`. Bootstrap and owner-import secret keys/exports were removed after measured recovery and owner-copy verification. Deployment restore therefore requires the owner to provision the recovery key temporarily into a separate 0700 GPG home. Never pass private bytes/passwords through arguments, environment variables, Git or chat.

The owner-machine recovery folder and encrypted backup copy are outside the Git repository and public outputs, protected by owner/SYSTEM-only ACL. The secret export is protected with native **Windows CurrentUser DPAPI**; decryption requires that Windows account/profile. A private export was actually recovered from DPAPI and imported into a fresh server keyring for the successful rehearsal. Temporary plaintext exports were removed. For another target, use that owner profile to export privately, transfer over the authorized secure channel, verify the fingerprint against the independent recipient record, import into a temporary protected GPG home and remove the export. Remove the temporary secret key/agent after acceptance. Back up the owner recovery/profile material securely; copying the DPAPI file alone to an unrelated account is not a portable key export.

## Restore to a new staging directory

Use the matching immutable release/runtime and its isolated, pinned dependency directory. Replace variables with verified protected paths; the destination must not exist and must be outside `/srv/tehnet-software`:

```sh
export PYTHONPATH="$RELEASE/host-site:$RELEASE"
export PYTHONDONTWRITEBYTECODE=1
python3 -m app.recovery restore \
  --bundle "$ENCRYPTED_BACKUP" --expected-sha256 "$INDEPENDENT_CIPHER_SHA256" \
  --key-home "$TEMPORARY_OWNER_GPG_HOME" --staging "$NEW_PRIVATE_STAGING"
```

Only `RESTORE_VERIFIED.json` with successful image/schema/semantic checks is eligible for an isolated boot. `RESTORE_REJECTED` means never activate the directory. The CLI does not switch active volumes. A later volume cutover requires freezing the sole writer and taking a fresh snapshot; do not restore an older backup over newer auth or metadata. Session invalidation intentionally logs out old sessions.

## Scoped activation and automatic rollback

`deployment/scripts/activate-engine.sh RELEASE IMMUTABLE_IMAGE TEMPORARY_GPG_HOME RECIPIENT_FINGERPRINT --rehearse|--activate` is implemented and tested. It acquires the operation lock, validates loaded image/composition/route ownership, captures exact previous image/composition/snippet and other-container/site fingerprints, creates a fresh private whole-site backup, stops only the archive, and backs up/restores its metadata. The restored copy must boot with network none before replacement. The live root and catalog mounts stay read-only; auth is the only writable persistent web mount. No payload volume is present. Only the `/software` snippet changes: no access/error request logging, caching or request/response disk buffering; body size is bounded. Main Nginx site and WordPress logs/routes remain unchanged.

On error, TERM/INT/HUP, only the archive code/composition and owned snippet roll back. The script checks the exact previous image and preserved website before reporting success. Newer engine databases remain in place; **code rollback never restores a stale state backup**. Privacy logging exclusions remain until the old image is in place. `--rehearse` deliberately activates and then returns to the exact previous image. Deployment interruption with SIGKILL/power loss cannot run a trap: retain the transaction backup and follow the saved previous-image/composition/snippet records under the same operation lock, checking current state before resuming. Never run both versions as writers.

For emergency code rollback, identify the exact accepted transaction backup, stop only `tehnet-software`, launch its saved `previous-compose.yaml` with the saved immutable `previous-image.txt`, verify the image, then restore **only** `previous-snippet.conf`, validate/reload Nginx and run website/private-route checks. Keep all five current databases; if the old code cannot validate their schema, stop and use forward recovery instead of forcing old software onto new state. The measured current transition has identical schema 1 and the previous preview simply ignores new auth/registry files.

Measured real same-host rehearsal: 12 seconds, including encrypted staged recovery/isolated boot/new activation/return to previous code. Final activation: 8 seconds after fresh whole-site preparation. Five database byte hashes matched before/after both operations. Brief `/software` 502 responses occurred while its container restarted; no zero-downtime guarantee. These timings exclude provisioning/key preparation/whole-site backup work and do not accept a real Iranian-host migration, WAN/DNS cutover, external provider retention or post-write cross-host reconciliation.
