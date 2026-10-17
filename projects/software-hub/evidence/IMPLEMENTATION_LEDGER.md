# Implementation ledger — TehNet Software Archive

Owner request (2026-10-17): finalize W0, begin implementation using existing research, preserve current site, add a menu link and record every task/test. Owner correction: this is a section of TehNet, not a separate Melika brand. Use «آرشیو نرم‌افزار تهران نتورک», `/software/`, and `projects/software-hub/`. Original source repository names/attribution and raw historical evidence remain unchanged.

## Pre-flight decisions

- W0→W2/W3/W4/W5/W6: shared models, visibility, schema and base-path contracts must be frozen before consumers. W0 owns these files; one implementer in this request.
- W0→W6: preview can publish the reviewed mirror-research registry with all routing disabled; it cannot expose VPN data or claim download/offline acceptance. Restricted routes fail closed until W2 is actually implemented.
- W6→menu: owner explicitly authorized the single TehNet navigation addition. Use WordPress menu APIs, preserve every existing item/location and make the update idempotent/reversible. No theme replacement or general reseed.
- W6→host: existing authorized SSH profile reached the actual TehNet host and confirmed 127.0.0.1:18082 plus its Nginx config. Candidate 18083 currently has no listener. Deploy only a separate bounded service and exact `/software` prefix; capture full backup and before/after unrelated-service fingerprints.
- Ruling: current request authorizes this implementation and scoped route/menu deployment; do not ask again for the already specified design. W7 real migration, provider activation and W2 private access remain separate gates. Cost if wrong: a bounded route/service/menu rollback; no existing website code or data schema changes are permitted.
- WPVibe plugin-backed menu command returned 404 because its optional plugin is absent. Do not retry plugin-backed tools or install anything; use the existing authorized SSH/WP-CLI path.

## Tasks

W0 claimed by current Codex implementer; base e61227712311d77baef4694f88d2b934ab90ec43. Exact owned paths: app/models.py, config.py, db.py, migrations/, contracts/, tests/test_contracts.py and task/status documents. W6-preview follows after W0 acceptance; it does not close full W6 or W2.

W0 complete: nine tests PASS / exit 0. Typed v1 contract and schema frozen; test fixtures explicitly close SQLite handles for Windows cleanup. Next W6-preview; no W2/private/provider acceptance.
