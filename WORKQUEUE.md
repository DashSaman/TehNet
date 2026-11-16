# WORKQUEUE — TN-TEHNET-SEARCH-LEARNING-REVENUE-V2

> وضعیت‌ها: READY / IN_PROGRESS / REVIEW_REQUEST / NEEDS_CHANGES / DONE / BLOCKED
> فقط با تغییر واقعی state را به‌روزرسان؛ برای polling بی‌تغییر کامیت یا comment نساز.

---

| id | priority | dependencies | status | acceptance | artifact | full_sha | receipt | blocker | next_action |
|---|---|---|---|---|---|---|---|---|---|
| P0-poe-scenario | P0 | — | DONE | port/PSU consistent | ca307ae | ca307ae7321735ba | validation-receipt.json rev5 | — | — |
| P0-crs354-ram | P0 | — | DONE | 128MB official | 6251514 | — | — | — | — |
| P0-builder-gate | P0 | — | DONE | router-only in router guide | a3543b5 | — | — | — | — |
| P0-afterd1-patches | P0 | — | DONE | hash guard + after-D1 bodies | 0189ff2 | — | — | — | — |
| P1-discovery-matrix | P1 | P0 | READY | 16 URLs HTTP/canonical/robots/sitemap documented | qa/seo-device-guides-20261116/discovery-matrix.csv | — | — | NOT_RUN: no authorized non-local HTTP env | next authorized env run |
| P1-topic-map | P1 | P0 | READY | 3 clusters × intent/audience/target/gap/source/service | MASTERPLAN.md | — | — | — | — |
| P1-internal-links | P1 | P1-topic-map | READY | source→target→anchor applied in candidate pages | page-edits/*.proposed.html | — | — | NOT_RUN: requires build | next authorized run |
| P2-driver-integration | P2 | fixture-ownership | BLOCKED | app/DB disposable + ownership verified pre-effects | — | — | — | fixture ownership unverified; no disposable cloud env | await manager acceptance |
| P3-service-pages | P3 | P0 | READY | 3 pages title/H1/direct-answer/deliverables/limits/CTA | content/seo-device-guides-20261116/page-edits/ | — | — | — | — |
| P3-articles-complete | P3 | P0 | READY | router+switch articles intent/selection/limits/upgrade | content/seo-device-guides-20261116/articles/ | — | — | — | — |
| P4-educational-backlog | P4 | P3 | READY | M1-M6 + S1-S6 learning units | — | — | — | — | — |
| P5-distribution | P5 | P3 | READY | LinkedIn×3 + Gamma×20 + Reddit≤3 + Zenodo protocol | — | — | — | DRAFT_ONLY | — |
| P5-favicon-live | P5 | P0 | NOT_RUN | verify rendered head output | site/themes/tehnet/assets/img/ | — | — | NOT_RUN: no authorized env for live-site check | owner action via wp-admin |
