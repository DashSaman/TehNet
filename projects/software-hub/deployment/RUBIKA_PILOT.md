# Rubika — owner setup and measured capability boundaries

Current result: official documentation and API transport were checked; the invalid-token request reached the valid-TLS API and received a non-OK JSON response. The actual Linux hidden-prompt fixture passed without echo and with a 0600 token file. **No production token exists, no real upload/download or retention test passed, and the website backend remains disabled.** [Evidence](../evidence/mirrors-rubika-capability.json).

## Choose the token locally

Create a dedicated bot using [Rubika's official instructions](https://rubika.ir/botapi/). Keep the token out of chat, command arguments, environment variables, Git, screenshots and public output. In an interactive administrator SSH terminal, copy:

```sh
bash /opt/tehnet-software/operations/mirrors-20261018/deployment/scripts/set-rubika-token.sh
```

The helper requests the token and confirmation with hidden prompts, stores it atomically under `/root/.config/tehnet-software-rubika/token` with owner-only access, then runs an authenticated `getMe` check. It prints only a fixed result; no bot identity/token is printed. A rejected API check leaves the owner's protected token file for correction; rerun setup to replace it. The token never enters the web container and this operation does not enable Rubika on the website. The existing VPN password is a separate credential and is not changed.

## Bounded public fixture test

Use only a dedicated test bot. The [official API](https://rubika.ir/botapi/methods) documents `requestSendFile` → multipart upload → `getFile`. The [file-type model](https://rubika.ir/botapi/models/#filetypeenum) currently documents a 50 MB general File ceiling; this is documentation, not measured storage capacity, quota or retention. The probe generates only a 4 KiB public text fixture in memory. No chat/message send occurs and no user/VPN/software file is read or staged on the website disk.

Prepare the local operator runtime:

```sh
cd /opt/tehnet-software/operations/mirrors-20261018
export PYTHONPATH=/opt/tehnet-software/releases/engine-active-20261018/host-site:$PWD
export PYTHONDONTWRITEBYTECODE=1
python3 -m tools.rubika_probe check
python3 -m tools.rubika_probe roundtrip
```

The first roundtrip discovers only the upload hostname and stops before contacting an unapproved host. Review it using official provider evidence, public DNS and TLS; do not approve wildcards or an arbitrary returned hostname. Repeat with `--upload-host APPROVED_UPLOAD_HOST`; after upload, an unknown download host also stops for review. Only then supply `--download-host APPROVED_DOWNLOAD_HOST`. These uppercase names are placeholders, not approved hosts. Token/private IDs/bearer URLs are redacted; hostile hostname normalization cannot expose their case-folded form. Every actual connection rejects private/mixed DNS, pins the numeric peer while checking TLS/SNI, ignores proxy environment, refuses redirects/credentials/nonstandard ports, and has fixed response/time caps.

The optional upload is self-created public test data and may remain at the provider: the checked documentation did not establish a file-delete endpoint or permanence. Keep the returned `fixture-record.json` privately beside the token. The report's full-hash result, `head_verified` and `range_verified` are separate checks; a false field is not provider acceptance. Returned URLs are never registered as public or VPN downloads.

## Real retention and recovery gates

After actual 24 and 72 hours, manually repeat `python3 -m tools.rubika_probe recheck` with the same approved download host. It reuses the private file ID, requests a fresh URL and checks the same bytes without a new upload. Malformed/missing/future-dated fixture records fail closed. Record actual creation/check times; advancing a test clock cannot prove provider retention. No follow-up scheduler was created.

Before any real storage adapter is enabled, measure anonymous versus authorized access, HEAD/Range, expiry/renewal, quota/errors, deletion/recovery, official distribution permission, domestic connectivity and an independent recovery copy. An accessible bearer URL cannot protect VPN files or provide revocation on every request. Future software uploads come directly from the workstation/separate transfer worker to accepted external storage; the website continues to hold only metadata.
