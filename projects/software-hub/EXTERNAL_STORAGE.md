# External storage and mirrors — current implementation

Authoritative requirement: [ADR 0002](decisions/0002-external-payload-storage.md). No downloadable payload may be persisted on the website VPS. Only code, small metadata/auth/operational SQLite state and private configuration belong there. Research rows are not enabled download sources.

Current accepted pilot (2026-10-18): three exact public artifacts at MobinHost/Arvan, independent official full digests/sizes, real TLS/HEAD/Range/conditional and two-vantage end-to-end acceptance. [Evidence](evidence/LIVE_MIRRORS.md), [20-minute bounded operator refresh and rollback](deployment/PUBLIC_MIRRORS.md), [public-only pinned policy manifest](catalog/public-downloads.json). Only the reviewed public pilot policies are committed; private source approvals and bearer credentials still stay outside Git. The API/CLI schema and web image are unchanged. All other provider approvals remain separate gates.

## Implemented

`app/external_storage.py` provides metadata-only explicit initialization, separate visibility partitions, exact identity conflicts, 10,000-record cap per partition, safe filename/field bounds and registration by complete network SHA-256/size verification. Verification consumes 64 KiB chunks, discards them, caps a file at 512 MiB, has a total 10-second deadline and durable daily request/byte/host/circuit limits. Large ISOs or slower transfers currently fail closed; do not bypass these caps or split files without a separately tested protocol. HTTP reads never initialize/migrate registries.

Public `/software/v1/artifacts` has an explicit safe projection. GET/HEAD `/software/download/{sha256}/{filename}` returns an uncacheable 307 only for an approved, recently verified registered public target. No arbitrary URL endpoint, payload fetch on a visitor request, local object directory or upload API exists. A verification proves the bytes at its measured time; remote content can change afterward. The UI provides a copyable client-side `sha256sum --check` command. Range, resume and conditional responses happen at the provider, not on TehNet.

Private navigation/records/counts/search/URLs never enter public HTML/API/OpenAPI. Login protects the private catalog; private delivery is closed pending accepted external authorization. No public or signed bearer redirect is used as a substitute for revocation on every request. A successful password test is not private-provider acceptance.

## Register a real public mirror file

An administrator must obtain operator/redistribution approval and an independently trusted full digest/size first. A hash learned only from the same untrusted response is insufficient; native APT still needs W4 signature→index→artifact validation. Keep approval and domestic-connectivity evidence in a private source policy file outside Git; use the exact SourceConfig fields in `app/models.py`. `routing_enabled` defaults false, visibility defaults restricted; enabling requires `permission_state=approved`, `domestic_state=verified`, nonempty `approval_evidence`, HTTPS `base_url` and exact `allowed_hosts`. Discovery alone never supplies these approvals.

After setting `TEHNET_SOFTWARE_DATA`, `TEHNET_SOFTWARE_METADATA` and `TEHNET_SOFTWARE_OPS` to separate administrator-owned directories in a prepared engine environment:

```sh
python -m app.cli init-store
python -m app.cli init-network
python -m app.cli register-external \
  --source-policy /protected/approved-source.json --relative-path exact/relative/file.bin \
  --sha256 "$TRUSTED_SHA256" --size "$TRUSTED_SIZE" \
  --name "$SOFTWARE_NAME" --version "$VERSION" --architecture "$ARCH" \
  --filename file.bin --visibility public --license-approved \
  --provenance "$INDEPENDENT_TRUST_AND_LICENSE_REFERENCE"
```

Values above are operator inputs, not pre-approved software. The command must complete successfully before a row appears. Repeat registration with identical identity/policy to refresh the one-hour eligibility; a failure leaves prior verification to expire. Policy changes/conflicts require explicit administrative reconciliation; there is no automatic alternate/foreign fallback. The scoped pilot now has a sandboxed 20-minute refresh for only its three pins; there is no general upload/discovery scheduler. Every metadata writer must hold the engine operation lock. Run verification in a separately authorized worker environment if the website host must perform no upstream payload reads at all; only synchronize consistent, reviewed metadata afterward.

## Rubika and other external providers

Official documentation checked on 2026-10-17: [Rubika Bot API methods](https://rubika.ir/botapi/methods). It describes `requestSendFile` returning `upload_url`, multipart POST returning `file_id`, and `getFile` returning `download_url`. These establish an API workflow, not storage guarantees. This review did not establish permanent retention, public distribution permission, numeric quotas, download URL lifetime, Range support or outage independence. No account/token/upload/real-provider retention test was performed. `app/storage_backends/rubika.py` therefore raises a capability error and is never selected automatically.

The [owner token setup/capability tool](deployment/RUBIKA_PILOT.md) now implements hidden local setup, API identity checks, an optional 4 KiB in-memory public fixture and same-file retention recheck. Real API transport and a disposable hidden-terminal fixture passed; the owner has no token, so real account upload/download and retention are unaccepted. Future software uploads still go directly from a workstation/separate transfer worker. Record size/SHA/time/file ID privately, test immediate/actual24/72h retrieval, renewal/deletion/recovery, Range/HEAD, permission and quota. Every returned upload/download host requires a separately reviewed exact allowlist; never forward bot credentials or expose VPN objects through public bearer URLs. Real measurements and an independent recovery copy remain prerequisites.

An Iranian S3-compatible object store or contracted mirror can implement the same external-placement policy. Outside the explicitly accepted three-file public mirror pilot, no additional storage provider, price, subscription, quota or domestic classification is selected/approved by this code.
