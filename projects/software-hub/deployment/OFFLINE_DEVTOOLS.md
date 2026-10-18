# Dated Ubuntu devtools — qualification, publication and rollback

Scope: the separate `noble-devtools-amd64` profile, eight tools plus CA support, Ubuntu main+universe, 58 exact archives/32,139,756 bytes relative to the recorded clean Base. The previous main-only `noble-core` capability remains unaccepted. The existing eleven-download worker/pins/quotas and active image stay unchanged. User instructions: [OFFLINE_INSTALL](../OFFLINE_INSTALL.md). Acceptance: [evidence](../evidence/OFFLINE_DEVTOOLS.md).

## Trust and storage

Native APT solves against clean signed Ubuntu Base 24.04.5 amd64, not host packages. Provisioned Ubuntu archive keyring verifies InRelease; signed compressed and expanded index hashes authenticate each selected `.deb` Filename/size/SHA256. APT cache names with encoded version epochs differ from pool filenames; keep both identities. Use pinned HTTPS Arvan allocation, no proxy/redirect/fallback. No `trusted=yes`, expired/future release bypass or package downgrade. Mutable suites must be at most48h old when preparing; dates/signatures are checked again at offline install. By-hash URLs can disappear and a dated profile is deliberately not an automatic perpetually fresh repository.

Only code/small metadata/logs persist on the website. Rootfs, indices and package archives used by qualification live in private 768MiB **noswap** tmpfs, destroyed on exit. A transient cgroup limits RAM900MiB,swap0,CPU50%,64tasks,600seconds. Installation runs in an additional network/PID namespace: only lo UP, no routes, outside TCP refused; kernel-created DOWN tunnel interfaces are harmless and explicitly recorded. Host networking/swap/APT/container state is not modified. On client preparation, payloads go to the user's chosen new directory/removable disk, directly from the external mirror.

## Reproduce or refresh

This is an operator procedure, not a command to run on the production app container or an arbitrary shared server. Require Linux6.8+ explicit noswap support, root/unshare/gpgv/Ubuntu keyring, enough RAM headroom, the already-pinned Python host dependencies and current code. Abort on absent isolation or signature verification. Reserve a **new private operator directory**, copy project code there and create its `metadata/`. Keep originals/evidence from previous runs. No Ubuntu Docker image pull or host package installation is needed.

1. Obtain the official [Ubuntu Base release](https://cdimage.ubuntu.com/ubuntu-base/releases/24.04/release/) small `SHA256SUMS` and detached `SHA256SUMS.gpg` metadata over verified HTTPS. Validate the provisioned CD-image key fingerprint `843938DF228D22F7B3742BC0D94AA3F0EFE21092`; preserve metadata and gpgv output. The scripts pin the24.04.5 archive; changing the base requires review/new baseline acceptance.
2. Capture existing container fingerprints and hashes of the owned Nginx snippet, TehNet site/compose configuration, auth/restricted DBs and immutable research as private `containers.before` and `protected.before`. Never publish their contents. Set `OPS` to this private code directory and `HOST_SITE` to the pinned dependency directory. Put `devtools-smoke.py` from this folder at `$OPS/devtools-smoke.py`.
3. Run [discover-devtools.sh](qualification/discover-devtools.sh) in a private mount namespace under the stated transient unit limits. It downloads the signed Base only into noswap RAM, verifies exact hash, runs native signed APT update, records clean baseline, exact candidate seeds, print-URIs and selected signed paragraphs/full index hashes. No packages are installed on the host.

```bash
systemd-run --no-block --unit=tehnet-offline-discovery-UNIQUE \
  --property=Type=exec --property=RuntimeMaxSec=600 \
  --property=MemoryMax=900M --property=MemorySwapMax=0 \
  --property=CPUQuota=50% --property=TasksMax=64 \
  --setenv="OPS=$OPS" --setenv="HOST_SITE=$HOST_SITE" \
  /usr/bin/unshare --mount --propagation private \
  /bin/bash "$OPS/deployment/qualification/discover-devtools.sh"
```

4. From that code directory, with its PYTHONPATH and pinned dependencies, run `python3 -m tools.build_devtools_profile "$OPS" deployment/client/offline-install.sh`. It independently validates the signatures, signed index hashes and exact package mappings; rejects tampered/stale/rolled-back signed dates; writes `metadata/profile-unaccepted.json` and signed-chain evidence. It never accepts a profile. Revisit native scope/byte bounds if the candidate closure changes; do not simply loosen assertions. Installer changes require updating the helper's exact installer hash and rerunning relevant tests.
5. Repeat the transient-unit command with a new unit name and [run-devtools-lab.sh](qualification/run-devtools-lab.sh). This repeats clean Base extraction, downloads/checks the entire kit in RAM and performs native install with no network/old lists. Corrupt/missing archive, forged signed metadata and newer installed nonseed dependency must each fail before dpkg status changes. Positive install must prove all exact versions/empty dpkg audit; [functional checks](qualification/devtools-smoke.py) exercise all8 tools and58 installed copyright files. Preserve full failed logs, then fix/retest; successful package installation alone is insufficient.
6. Require successful unit exit, `offline-install-acceptance.json`, `lab-state.json`, unchanged private fingerprints, zero swap/oom, no remaining lab mounts and exactly the five existing subsystem state DBs. Record durations/source hashes and actual result after every stage. This is a clean Base userland, not booted VM/ISO or real Iran connectivity. Only then set accepted=true in the dated public profile and bind its SHA256 into sanitized acceptance evidence.

## Public metadata publication

The four-file whitelist is exactly `index.html`, `profile.json`, `offline_kit.py`, `acceptance.json`. Stage them in a private source directory; no `.deb`, rootfs, archives, token, auth DB or arbitrary file tree. The helper validates all58 full file hashes on the client. The guide uses the existing `/software/static/style.css`, fonts and UI script; no new web image is required.

[offline_publication.py](../tools/offline_publication.py) holds the existing engine operation lock, requires the exact prior owned snippet, saves its original bytes and file hashes under a private timestamped backup, copies the four small files to an immutable public code directory, and appends four **exact** `/software/offline/` locations to the owned snippet. It runs `nginx -t` before graceful reload. No WordPress/site configuration/menu/container/service/port change. Unknown child paths fall through the existing closed app behavior. GET/HEAD only, no listing, no-store/noindex/nosniff/CSP. Post-publication check is part of the transaction when calling `publish(..., check=...)`; CLI callers must immediately run the complete live acceptance and roll back on any failure.

Linux tests inject reload and post-check failures and require exact old bytes, successful rollback syntax validation and reload. These fixtures test transaction behavior; actual live publication evidence separately records real Nginx validation/reload, public/origin checks and unchanged containers/auth/private state.

## Roll back or migrate

For the current four-location addition, hold `/run/lock/tehnet-software-engine.lock`, atomically restore **only** `nginx-software.before` from the recorded offline-guide backup to `/etc/nginx/snippets/tehnet-software.conf`, run `nginx -t`, then graceful reload and recheck main routes/software/private boundary. The public immutable code directory may remain unreachable until a separate cleanup; never remove original research or client payloads by assumption. Keep backup/source/proof paths recorded. A failed rollback reload is a failure requiring operator attention, never a success result.

For prepared-target migration, include the four public code/metadata files and their hashes in the software code bundle; restore the owned snippet's exact aliases only after those paths exist and remain readable by Nginx. They contain no software payload. Preserve the immutable active web image and normal five-DB encrypted recovery rules. Add `/software/offline/`, exact profile/helper hash checks and unknown-child404 to the target acceptance before traffic cutover. Existing prepared-target under30min migration evidence does not retroactively measure this new addendum or prove Iran/mirror availability; run and time the prepared target rehearsal again for that claim. Users' kits and mirror payloads are not migrated through the website disk. See [MIGRATION](MIGRATION.md) and [RECOVERY](RECOVERY.md).

For an update of this exact owned guide,use publish(...,previous_public=THE_EXACT_PREVIOUS_IMMUTABLE_PUBLIC_DIRECTORY) under the same engine lock. The module requires the entire prior snippet equal reviewed base+prior generated routes,backs it up,and replaces those4 guide routes with the new4; it refuses unexpected config edits. The CLI without that argument is initial-publication only. Current backup and exact public hashes are in the acceptance report.
