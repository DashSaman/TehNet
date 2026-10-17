# W2/W3/W5 external engine — operator runbook

This is a prepared engine release, not a production cutover. Live `/software/` stays on the previously accepted public preview until the new-state deployment/backup/rollback gate is implemented and tested. Do not run `update-preview.sh` or `deploy-preview.sh` with an engine release. Main WordPress/theme/Core/menu/ports are outside this change.

## Password setup chosen by the owner

The password is selected locally by the owner in an interactive SSH terminal; never send it in chat, Git, arguments, environment variables or a pipe. The engine uses Argon2id through pinned pwdlib, hashed opaque sessions, a one-hour lifetime, Secure/HttpOnly/SameSite=Strict cookies, same-origin CSRF checks, replay-resistant login challenges, durable global throttling (5 attempts/minute), bounded challenge/session counts and one concurrent password verifier. A shared password provides one restricted identity, not separate user roles. Global throttling can lock everyone out briefly; the local CLI can reset it.

After verifying the immutable engine image from the current build evidence is loaded on the server, run:

```sh
cd /opt/tehnet-software/releases/engine-external-20261017-r2
bash deployment/scripts/set-password.sh "$VERIFIED_ENGINE_IMAGE_ID"
```

Replace the variable with the **exact sha256 image ID** from the engine validation evidence; a preview image is ineligible because it lacks the auth CLI. The script accepts only an image ID and an interactive terminal. It mounts only `/srv/tehnet-software/auth` read/write into a disposable, nonroot, network-disabled container. It neither enables login on the current preview nor restarts any existing service. The hidden prompt requires 16–256 characters and matching confirmation; changing the password invalidates every old session. No production password is configured by the implementation/test process.

Until engine activation and owner setup are both complete, private routes remain uniformly denied and the generic login is unavailable. Once activated, visit `/software/access/` directly; there is no public VPN menu item. Logout is a CSRF-protected POST. Local administrative recovery commands are `python -m app.cli revoke-sessions` and `reset-lockout` with the auth directory mounted; they never print session tokens/passwords.

## New-state production activation gate — pending

Current `compose.yaml` and existing deployment scripts remain **preview only**. New engine production activation requires a separate tested composition with research metadata read-only, external registry partitions read-only, auth read/write, no payload volume/cache/temp spool, root read-only and explicit limits. Web process needs no upstream verification worker; run operator registration separately. Remove archive-prefix access logging and prevent private paths/tokens in error logs without changing WordPress logging. No trusted proxy client IP is assumed.

Before activation: consistent encrypted backup of research + both external registries + auth/operational state/config; independent protected decryption key; actual restore integrity/schema/credential checks; invalidate restored sessions/challenges; unknown versions fail closed. A manifest identity row alone is not sufficient validation. The unpublished CAS backup prototype was withdrawn under ADR 0002 and is not an accepted backup tool. Existing preview backups do not cover new auth/registry state.

Test archive-only activation, failure during activation, interruption, automatic fallback to the exact old image/composition, absence of two writers, and post-write reconciliation. Capture existing WordPress container IDs/images/ports plus homepage/Learn/Services/Shop/Contact fingerprints before/after; no unrelated restart. Do not claim password-protected VPN file downloads until an external private backend passes its authorization/revocation/no-spool tests. Public fixture redirects prove routing behavior, not real mirror permission or current file availability.

## Portable migration target under 30 minutes — acceptance still open

Prepare Iranian target and a provider-independent recovery copy first: identical architecture/runtime/image, consistent encrypted metadata/auth backups, securely provisioned secrets/key, canonical HTTPS hostname/certificates, `/software` routing, and verified direct domestic access to every external payload provider. Preload images and all OS/runtime dependencies. DNS TTL/provider control and usable rollback host are prerequisites. No transfer of software payloads to the website disk is allowed.

Measured drill must record separate preparation and timed cutover: stop the sole writer, final consistent metadata backup + encrypted transfer, staged restore/schema/integrity checks, session invalidation, provider connectivity/real GET+HEAD+Range+hash checks, enable target, DNS/routing convergence, public/private/no-leak and website smoke tests. Record each duration and whole cutover; target is <1,800 seconds. On failure before target writes, restore previous route/image/state. After target writes, freeze both writers and reconcile metadata/auth before rollback; never silently overwrite newer state.

The prior 1.764-second same-host preview restore measured only a 110,592-byte public catalog with a preloaded image. The current Linux engine test suite is not an Iran migration, encrypted metadata restore, WAN transfer, DNS cutover, payload retention or rollback-after-writes test. No such acceptance is claimed.
