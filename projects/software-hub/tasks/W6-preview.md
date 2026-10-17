# W6-preview — public preview, isolated deployment and easy installation guides

- State: done, limited to preview acceptance. Full W6 remains open.
- Owner: current Codex implementer/integrator; no shared-file concurrent owner.
- Base: 49c9452; first implementation checkpoint 2d42f3ad6e9d39affd3d09aa73eee9a6b89a1006.
- Scope: public app/CLI/catalog projections, templates/static/fonts, locked runtime/Compose, scoped deploy/update scripts, one WordPress menu helper and their tests; integrator status/changelog/root updates.
- Dependencies: W0 v1. W2/W3/W4/W5 are deliberately not bypassed to claim full acceptance.

Implemented the Persian read-only preview at https://tehnet.ir/software/ with search, 27 attributed research rows, empty artifact results, plan-only Ubuntu profile and explicit capabilities. Added one owned menu item, ID 189 in primary menu 2. Original eight items and existing container identities/images/ports are unchanged. No theme/Core/content file was deployed.

Latest owner request: preserve existing colors and provide copy/paste installation with explanations. Measured the actual theme tokens and reused its dark/light palette, self-hosted Vazirmatn and `tn-theme` preference. Added eight explained Ubuntu 24.04 online apt guides with install/check copy controls, prerequisites and honest offline status. Browser tests verified both palettes, mobile width 390 (client/scroll width 375), exact `curl --version` copy/paste and no console warnings/errors. These are guide/UI checks, not clean-client install acceptance. Font OFL attribution is included.

Actual checks: 36/36 tests pass in the exact Linux runtime image, no skips (9 contracts, 11 preview, 5 synthetic rehearsal, 9 first-deploy fault/positive tests, 2 update/rollback tests). Windows: 25 passed, 11 Linux-only skipped. Original 18 probe tests pass separately. PHP menu helper: 5 logic checks, both files lint. Build with network none and 16 hashed wheels succeeds. See evidence/DEPLOYMENT.md and machine-readable reports for current results.

One focused reviewer identified three Important deployment risks; regression tests first failed then passed after route-conflict/partial-start/rollback cleanup fixes. Real initial deploy also discovered host internal-network publishing behavior, two HTTP/HTTPS server_name blocks and graceful-reload convergence; all were recorded and corrected. Three failed first-install attempts rolled back; fourth succeeded. Latest update used a fresh validated whole-site backup, touched only the archive container and retained previous image. Two transient archive 502 responses occurred while it restarted; WordPress containers were not restarted.

Final image: sha256:54f507b987e5a252a6f207478ddd5bb6251c8889c1ed45657857be017e314352. Config/release: /opt/tehnet-software/releases/ui-20261017. Backup: /root/tehnet-backups/20261017-143634-software-update. Private backup bytes/secrets are not in Git. Public/origin tests recheck the main pages, source counts, noindex, local assets and deny responses.

Next: W2/W3/W5, then W4 and full W6. No provider enabled, no real download/authentication/Rubika, no Iranian migration acceptance. The same-host cold-process restore with a preloaded image took 1.764 seconds for a 110592-byte DB; it is not a WAN/cutover result. Integrator reconciled STATUS, CHANGELOG and root coordination documents for this task.

Developer instructions include a separate hashed test dependency lock (19 combined wheels resolved offline in a disposable-container dry run), venv and copy/paste run/test steps. All 18 deployed runtime input hashes match local bytes. Bash scripts retain LF on Windows checkout; local .venv is ignored. New evidence and tools remain in this project's ownership boundary.
