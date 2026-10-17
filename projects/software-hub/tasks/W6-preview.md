# W6-preview — public research interface and scoped first deployment

- State: in_progress (software checks complete, live deployment pending)
- Owner: current implementer/integrator
- Base: 49c9452 (W0 contract/naming checkpoint)
- Scope: app/main.py, app/cli.py, catalog public projections, templates/static, locked Linux runtime, first-install deployment script, new WordPress menu scripts and tests. Full W6, W2 and W7 are not closed by this preview.

Implemented public Persian interface/search, 27 explicitly research-only source rows, safe public API, health/readiness capabilities and plan-only Ubuntu profile. No verified download, worker/upstream fetch, provider activation, private auth or public upload. All restricted/unimplemented routes deny requests. No active theme/Core/content changes.

Verification: 23 local software/rehearsal tests pass; all 30 tests pass in exact locked Linux image (9 contracts, 9 preview, 5 earlier rehearsal, 7 deployment failure injections). Original 18 probe tests also pass. PHP menu helper passed 5 logic checks and both PHP files lint. Local browser rendered the Persian interface and Ubuntu search returned seven matching source rows. Offline image build used 16 exact hashed wheels with `--network none` and immutable Python base digest.

One focused independent review found 3 Important deployment risks (WordPress route conflict, partial Compose start cleanup, failure/cancellation cleanup). Seven real-flow sandbox failure tests were strengthened until each went RED, then all passed after fixes. Newly created data/snippet are preserved in the private backup on rollback; original website config/menu/container identities are restored/preserved. No second reviewer or recursive delegation was used.

Ruling: original SQL required sources.base_url NOT NULL while its YAML and W0 model permit unknown/null. Initial public seeding silently inserted zero rows under INSERT OR IGNORE. Before first deployment, align schema with documented nullable unknown and use ON CONFLICT(id) DO NOTHING so unrelated constraints cannot be swallowed. Public source count/reseed tests went RED→GREEN. No deployed migration was edited.

Next exact action: first-install script creates/validates full TehNet backup, verifies original /software absence, starts only the new bounded service, adds exact Nginx prefix and one owned menu item, checks original routes/ports/container IDs. Record actual live outcome before changing this task to review/done. W1 remains owner-deferred; W2/W3/W4/W5/full-W6/W7 remain planned.
