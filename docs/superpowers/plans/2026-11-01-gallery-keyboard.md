# P7 native product gallery keyboard selection

Status: IN_PROGRESS_NOT_DEPLOYED. Owner's existing overnight authorization covers evidenced bounded UX corrections; no new payment/indexing or MyTel permission is inferred.

Current evidence: previous media receipts tested pointer selection and fullscreen Escape, but not keyboard selection of inline thumbnail controls. Fresh guest GET-only observation on real TN-SN-17868 found two bare thumbnail images without tabindex/role. Fullscreen Enter/Escape and focus return work. Native compare dialog Escape/focus return also work; a transient body activeElement after Tab is not treated as proof of escaped native-modal focus. A real public regression fails specifically because thumbnails are not native keyboard buttons.

Predictions: missing native control semantics prevents inline Tab/Enter/Space activation; adding a native button bridge should select the same FlexSlider frame. A global gallery failure would also break the existing pointer/fullscreen path, which currently works. The thumbnail li clips outward focus rings, so acceptance must check an inset visible ring. This is a scoped UX gap, not a full WCAG/screen-reader audit or a claim the whole gallery is keyboard inaccessible.

Design choice by implementer within authorized scope: wrap only bare FlexSlider thumbnail img children of li in native type=button controls. Keep the original img/URL/alt and plugin click handler; bridge button-origin activation to the original img click once, leaving image-origin pointer clicks untouched. Use stable Persian position labels and aria-current derived from the existing flex-active class. A gallery-local MutationObserver handles native delayed thumbnail creation/class changes; repeated enhancement must not nest controls, and multiple galleries stay independent. Do not emulate button keys on img or edit WooCommerce vendor code. Keep the fullscreen path and no-JS original markup. Product-only new script/CSS assets are independent of existing store.js. Focus ring is inset inside the clipped thumbnail. Future standard products inherit it without catalog/meta changes.

Release scope: exactly product-gallery.js, product-gallery.css and class-storefront.php; new explicit scope,13 current runtime guards and read-only data checker. No DB/content/product/photo/order/settings changes. Original metadata checker/manifests/scopes remain intact. Staging must model production metadata0.2.2 and then restore original preview0.2.0.

- [x] Read prior media/shop evidence and reproduce real public RED with GET-only browser.
- [x] Observe assets/scope RED before implementation.
- [x] Implement minimal module/style/product-only enqueue and exact three-file scope; local GREEN.
- [ ] Native read-only checker tests; component delayed/multiple/idempotence cases and immutable native staging actual gallery/browser/rollback qualification.
- [ ] Review full relevant diff, private denied-value scan, qualified commit/CI, private snapshot and ordinary integration.
- [ ] Fresh production backup/checksum/drift, scoped release and public keyboard/pointer/fullscreen/mobile/no-JS acceptance; preserve closed commerce/noindex/metadata/data/runtime.
- [ ] Record actual receipts, transfer evidence to -SEO and update handoff/queue. Final08:00Tehran report remains pending.

Source reviewed: https://www.w3.org/WAI/ARIA/apg/patterns/button/ , scoped Enter/Space, accessible name and retained focus guidance. Native button semantics are used. No accessibility certification or ranking gain is implied. Raw captures/private config/backups stay outside Git. Existing security gates and no force-push/MyTel production changes remain.
