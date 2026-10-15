# Operational store implementation plan

Goal: extend the existing TehNet store with safe catalog import, usable commerce and a mature ERP boundary.
Spec: `docs/requirements-store-2026-10-15.fa.txt`; architecture: `docs/architecture.md`.
Execution: direct implementation plus the single bounded GLM advice already consumed. The user's explicit instruction to act independently for routine decisions overrides additional skill approval rituals. Production publishing and real payment still require the user's explicit approval.

Global constraints: preserve live Core drift, original theme, all customer data and noindex; never copy source stock/prices into sale data; no watermark manipulation; no secret logs; no new shared-host deployment.

Review focus: interrupted import/rollback; duplicate or conflicting financial events; simultaneous last-unit purchase; fractional cable UOM; money unit ambiguity.

- [x] 1. Inspect repository, SSH/runtime/DB and actual source API; preserve evidence, compare options and record decision.
- [ ] 2. Write failing catalog tests (source identity, no copied media/reviews/price/stock, duplicate imports, conflicting technical claims); implement normalized manifest and reversible importer.
- [ ] 3. Start isolated localhost WordPress/WooCommerce and ERPNext; preserve versions and test setup. No production credential reuse.
- [ ] 4. Implement storefront module: explicit verified-sale gate, technical filters, wishlist/compare, sales-unit display and account flows; verify actual mobile pages.
- [ ] 5. Implement ERP outbox/inbox with replay/conflict protection and fail-closed unavailable dependencies; test a real ERP order/stock/GL cycle with synthetic data.
- [ ] 6. Prove concurrency, expiry/cancel, refund/return, UOM, integer IRR/IRT, settlement and role boundaries; clearly list anything still blocked.
- [ ] 7. Document in Persian with actual screenshots, backup/restore rehearsal and allowlisted deployment/rollback; commit each meaningful deliverable. Obtain explicit approval before production deployment/payment.

Task ownership: current agent owns all changed files; no concurrent code-writing agents. Existing senior-team bridge supports read-only advice, so the requested bulk GLM execution is unavailable. No provider fallback is allowed.
