# TehNet portfolio visual refresh — implementation record

Goal / هدف: Apply the owner-approved Amirreza résumé palette and server/network vector to the existing TehNet WordPress presentation, and publish an independent native résumé page.

Authorization: Owner requested updating tehnet.ir with the approved résumé design, then explicitly authorized Remote Desktop Commander → SSH execution. This is a presentation deployment, not authorization to activate indexing or payments.

Reference: Amirreza_Golavar_TehNet_v1.1.html, SHA256 142e765063459ff4978430a60ce0e7490f175055c7301c9482b62784fd1c400d.

Design: dark navy #080f18, surface #101c29, cyan #79e7f7 and #33c9ee; light mode; RTL; existing site logo; conceptual SVG server rack and network nodes, without a fabricated personal portrait. Preserve Learn/Lab/Services/Shop and all existing URLs. Homepage remains Gutenberg-editable. Résumé is editable native WordPress HTML with a dedicated presentation template.

Global constraints
- No changes to tehnet-core business logic, inquiry/order data, gateways, blog_public=0, Nginx, Compose, bind ports or unrelated services.
- Omit the excluded partner brand and personal mobile from public résumé, downloadable text, VCF and metadata. The existing company office number is distinct and retained elsewhere on the business site.
- No private credentials, database dumps, private backup bytes, or font files are committed or distributed.
- Preserve live theme drift before changes; deploy only an explicit file allowlist, never replace the theme directory or delete live fonts.

Execution
- [x] Authenticated SSH read-only inspection; current live theme and homepage captured separately from older repository source.
- [x] Validated database and presentation/core backup; non-TehNet runtime fingerprint captured.
- [x] Isolated branch/worktree; all 16 existing contract tests passed at baseline.
- [x] New 7-test regression suite observed failing before implementing the refresh.
- [x] Added additive CSS/JS, preserved logo, vector graphic, accessible menu/theme/motion controls and native résumé template/content/downloads.
- [x] Regression suite, existing contracts, inquiry logic, PHP and JavaScript syntax passed locally.
- [ ] Browser preview in desktop/mobile and dark/light; actual WordPress integration verified separately after controlled deployment.
- [ ] Fresh pre-deploy backup and concurrent-edit guard; explicit-allowlist deployment and home/profile content changes only.
- [ ] Public/origin routes, H1/canonical/noindex, personal-data exclusions, live browser checks and runtime isolation verification.
- [ ] Update handoff/progress/tasks and deployment evidence with actual results.

Rulings
- Local runtime has a newer theme and additional published lessons than main. Preserve runtime presentation and untouched page content rather than reseeding the whole site.
- Replace unverified numeric homepage highlights with descriptive journey/service labels; do not invent current counts.
- Default new visitors to dark; retain saved light/dark preference.
- Existing self-hosted fonts remain in production; no font binaries added to Git.
- Browser preview is read-only DOM simulation, not proof of WordPress publishing or persistence.
- A privacy-test false positive on the word MyTel was fixed with a word-boundary telephone-scheme check; actual personal-number and VCF checks retained.
