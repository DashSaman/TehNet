# P8 service-page metadata role — bounded correction

Status: IN_PROGRESS_NOT_DEPLOYED. Existing approved overnight scope; no new URL/body or indexability change.

Fresh default-TLS read-only probe of 17 public routes found Article on setup, MikroTik, remote support and manual VoIP readiness service pages. Support and the service hubs currently have none. Existing attributed lessons correctly have Article. The visible source note is attribution, not proof of article intent. Google requires structured data representative of primary content; this is a role correction, not a measured ranking issue or manual action.

Diagnosis predictions: (1) rendering the real metadata module with a marked services page will reproduce the symptom; (2) a cache-only cause would not reproduce in the isolated module; (3) an unrelated plugin cannot account for that module's own Article node. First add the regression and observe RED; preserve its exact result.

Design: exclude WordPress pages whose URI is exactly services or starts services/. Retain note, description, Open Graph, genuine lessons and posts even with a matching slug, and existing collection exclusions. Avoid broad substring or all-page exclusions. Publish only metadata v0.2.2 through a new explicit immutable metadata-service-role scope: one owned file, seven runtime guards, a read-only native state checker. Keep the old qualification manifest and checker intact. No database writes or new Service/Review/Offer promises.

- [x] Confirm public baseline and local RED; add exact operator scope test.
- [x] Implement minimal role predicate and new bounded release scope; GREEN PHP/operator and native checker tests.
- [ ] Rehearse immutable current-production baseline in isolated native staging, with fresh backup/checksum/tamper/apply/repeat, desktop/mobile/no-JS acceptance and exact rollback/restoration of original preview.
- [ ] Full relevant diff, publication guard, qualified commit/CI, private snapshot and ordinary integration.
- [ ] Fresh production backup/drift guard, scoped apply and GET-only public acceptance; preserve all protected data/runtime/container state.
- [ ] Publish sanitized actual receipts and transfer the role lesson to -SEO; update overnight log/handoff. Do not claim SEO gain.

Official sources reviewed: https://developers.google.com/search/docs/appearance/structured-data/sd-policies and https://developers.google.com/search/docs/appearance/structured-data/article . Source support is page-role accuracy only; no GSC/rich-result/manual-action/rank test is implied. Service hub ID29 rewrite is deferred because parent /services already owns service selection; avoid duplicate intent.

Security gates remain: rotation UNKNOWN; remote history/cache/fork purge NEEDS_APPROVAL and refmap stale after ordinary merges; origin UNDETERMINED. No force-push, shared network/DNS/SSH change or MyTel production write. TehNet noindex and closed commerce/customer data remain protected. Shared staging writers serial under the existing OS lock. Morning report remains LIVE_NOT_FINAL until the bounded deadline.
