# Operational store implementation plan

Goal: extend the existing TehNet store with safe catalog import, usable commerce and a mature ERP boundary.
Spec: `docs/requirements-store-2026-10-15.fa.txt`; architecture: `docs/architecture.md`.
Execution: direct implementation plus the single bounded GLM advice already consumed. The user's explicit instruction to act independently for routine decisions overrides additional skill approval rituals. Production publishing and real payment still require the user's explicit approval.

Global constraints: preserve live Core drift, original theme, all customer data and noindex; never copy source stock/prices into sale data; no watermark manipulation; no secret logs; no new shared-host deployment.

Review focus: interrupted import/rollback; duplicate or conflicting financial events; simultaneous last-unit purchase; fractional cable UOM; money unit ambiguity.

- [x] 1. Inspect repository, SSH/runtime/DB and actual source API; preserve evidence, compare options and record decision.
- [x] 2. Write failing catalog tests; implement the complete 25-item draft manifest and reversible importer. Exact-model technical review remains gated by external evidence.
- [x] 3. Run isolated localhost WordPress/WooCommerce and ERPNext; preserve versions and test setup without production credential reuse.
- [x] 4. Implement sale gate, technical filters, wishlist/compare, sales-unit and account flows; verify actual mobile pages.
- [x] 5. Implement outbox/inbox, replay/conflict protection and unavailable-dependency handling; test real local ERP stock/GL with synthetic data.
- [x] 6. Prove concurrency, expiry/cancel, partial/full returns including discounts/shipping, IRR/IRT, settlement and role boundaries; list blocked scenarios in docs/testing.md.
- [x] 7. Persian guide with actual screenshots, local backup/restore and deployment/rollback plan. Stage commits preserve implementation and evidence.
- [ ] 8. External release gates: verified own catalog/stock/prices, provider sandbox credentials, complete mobile checkout, company/tax configuration, production capacity/TLS/worker/backup rehearsal and explicit deployment/payment approval. See docs/acceptance-matrix-fa.md.

Task ownership: current agent owns all changed files; no concurrent code-writing agents. Existing senior-team bridge supports read-only advice, so the requested bulk GLM execution is unavailable. No provider fallback is allowed.
