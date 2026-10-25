# W2/W3/W5 external engine — operator runbook

Current web presentation release as of19October2026:`/opt/tehnet-software/releases/engine-source-status-20261019`,image `sha256:3d01499c5a3c66b625abd95f113a4d37a156f6a230c4bb283cacac3237b3d8a6`. [Source checks,recovery/rollback and deployment](../evidence/SOURCE_STATUS.md). Schema,state mounts,password CLI,producer and normal download worker are unchanged. Preserve the complete current offline Nginx aliases during code activation; never replace them with a historical base-only snippet. The existing password helper still operates on the exact current inspected image.

Current engine is active on `/software` as of 2026-10-18. [Recovery and activation evidence](../evidence/ENGINE_ACTIVATION.md) supersedes the earlier staged-only status. Owner password remains unset and private access closed until local setup; actual external private delivery/Rubika are still unaccepted. Use [RECOVERY](RECOVERY.md) for tested metadata recovery and code rollback. WordPress/theme/Core/menu/other ports are outside scope.

## Password setup chosen by the owner

The password is selected locally by the owner in an interactive SSH terminal; never send it in chat, Git, arguments, environment variables or a pipe. The engine uses Argon2id through pinned pwdlib, hashed opaque sessions, a one-hour lifetime, Secure/HttpOnly/SameSite=Strict cookies, same-origin CSRF checks, replay-resistant login challenges, durable global throttling (5 attempts/minute), bounded challenge/session counts and one concurrent password verifier. A shared password provides one restricted identity, not separate user roles. Global throttling can lock everyone out briefly; the local CLI can reset it.

After verifying the immutable engine image from the current build evidence is loaded on the server, run:

```sh
cd /opt/tehnet-software/releases/engine-active-20261018
bash deployment/scripts/set-password.sh "$(docker inspect -f '{{.Image}}' tehnet-software)"
```

The command resolves the **exact sha256 image ID** of the active engine; compare it with the activation evidence before use. A historical preview image is ineligible because it lacks the auth CLI. The script accepts only an image ID and an interactive terminal. It mounts only `/srv/tehnet-software/auth` read/write into a disposable, nonroot, network-disabled container. The active engine reads the resulting credential without a restart. The hidden prompt requires 16–256 characters and matching confirmation; changing the password invalidates every old session. No production password is configured by the implementation/test process.

Until owner setup is complete, private routes remain uniformly denied and the generic login shows the owner-setup message (503). After setup, visit `/software/access/` directly; there is no public VPN menu item. Logout is a CSRF-protected POST. Local administrative recovery commands are `python -m app.cli revoke-sessions` and `reset-lockout` with the auth directory mounted; they never print session tokens/passwords.

## New-state production activation gate — accepted for current same-schema transition

The legacy `compose.yaml` and preview deployment scripts remain preview-only and reject engine source. Current `compose.engine.yaml` plus `activate-engine.sh` have passed encrypted metadata/config staged recovery, isolated network-none restored boot, fault-injection and actual same-host rollback/final activation. The web process mounts research and external registries read-only, auth read/write, no payload volume, root read-only with explicit limits. The owned archive Nginx snippet excludes request logging, cache and disk buffering; WordPress logging/config is preserved. Routine password setup shares the engine operation lock.

Actual owner-copy decryption key, backup results, exact active/previous images and limits are documented in [RECOVERY](RECOVERY.md) and [activation evidence](../evidence/ENGINE_ACTIVATION.md). Code rollback keeps newer databases; restore never activates a volume automatically. Temporary server secret keys were removed after acceptance; future restore/deployment requires the owner to provide a temporary recovery key home. Only public recipient material remains on the server. Public/private provider and native offline-install acceptance are separate from engine activation.

## Portable migration target under 30 minutes — acceptance still open

Prepare Iranian target and a provider-independent recovery copy first: identical architecture/runtime/image, consistent encrypted metadata/auth backups, securely provisioned secrets/key, canonical HTTPS hostname/certificates, `/software` routing, and verified direct domestic access to every external payload provider. Preload images and all OS/runtime dependencies. DNS TTL/provider control and usable rollback host are prerequisites. No transfer of software payloads to the website disk is allowed.

Measured drill must record separate preparation and timed cutover: stop the sole writer, final consistent metadata backup + encrypted transfer, staged restore/schema/integrity checks, session invalidation, provider connectivity/real GET+HEAD+Range+hash checks, enable target, DNS/routing convergence, public/private/no-leak and website smoke tests. Record each duration and whole cutover; target is <1,800 seconds. On failure before target writes, restore previous route/image/state. After target writes, freeze both writers and reconcile metadata/auth before rollback; never silently overwrite newer state.

The prior 1.764-second same-host preview restore measured only a 110,592-byte public catalog with a preloaded image. The current Linux engine test suite is not an Iran migration, encrypted metadata restore, WAN transfer, DNS cutover, payload retention or rollback-after-writes test. No such acceptance is claimed.
