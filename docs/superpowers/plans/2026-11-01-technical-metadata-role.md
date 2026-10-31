# Bounded technical audit and hub metadata correction

Status: DEPLOYED_VERIFIED; this bounded unit is complete. Inline continuation of the owner's autonomous UX/SEO correction scope. No new question or deployment permission is inferred from time passing.

Observed: a bounded public GET crawl returned73 responses including25 product URLs; status/H1/canonical/description/JSON syntax and main links were examined. A real-browser smoke covered16 route/viewport/JS combinations. Raw responses remain outside Git. This is neither a full crawler identity/field-performance audit nor a120-site benchmark.

Design decision: the four collection routes `/learn/`, `/lab/`, `/learn/mikrotik/`, `/learn/mikrotik/mtcna/` currently receive Article solely because their visible editorial note is present. Their primary purpose is organizing resources. Remove only that Article inference; retain the note, all descriptions/social metadata and genuine lesson Article output. This is a conservative semantic correction based on content review and official structured-data relevance guidance; no Google penalty or measured ranking impact is claimed.

Alternatives considered: add CollectionPage/ItemList graphs, or suppress all WP page Articles. Both broaden this fix: the former needs an accurately maintained collection model, and the latter removes valid lesson markup because lessons are WP pages too. Choose four exact page paths; same-slug posts and other pages remain unchanged. Commercial readiness-page classification is a separate review item, not silently included.

1. Add regression assertions through the existing metadata render/model seam; observe baseline failures for the four hub contexts. Keep old unit receipts historical by accepting a separate dated output path.
2. Add the exact-path page-only exclusion, preserving external-owner and private/unpublished guards. Run all metadata tests and PHP lint.
3. Native staging, one file only: backup/checksum, identity/network/mail/payment guard, baseline digest, full protected data fingerprint; verify hubs lose only Article, lessons keep Article and all visible body/H1/title/canonical/noindex/other metadata match. Rehearse exact file rollback and repeat, preserving foreign file edits.
4. Commit immutable reviewed source after full diff/private-value guard. Use a separately bounded one-file operator, not the historical multi-file/content remediation script. Qualify its staging apply/repeat/rollback before normal protected PR/CI integration.
5. Fresh qualified production backup/checksum/drift and approved source equivalence; publish only the metadata file with atomic ownership-preserving replacement. Verify read-only native/public/browser states. Keep noindex, content, menus, products/customer data, MyTel and shared infrastructure unchanged. Record actual release separately; leave VERIFIED/BLOCKED if any gate is unavailable.

No canonical/robots/sitemap-policy change; no Cloudflare policy change or email delivery; no customer/payment action. Schema counts, HTTP200 and browser acceptance are not search or AI-citation metrics. Morning report stays interim until the agreed deadline.

Qualified c287a86: one file, zero database writes,8 native HTTP comparisons and188 real-browser checks, then exact original file rollback and unchanged protected data/runtime. Metadata/payload tampering refused.

Actual acceptance: PR41/CI41250290474; source6728ddd equals qualified payload/tool c287a86, fresh verified backup,13 valid-TLS GETs and188 read-only public-browser checks. One metadata file installed; no DB/content writes or indexing-policy change. Broader mission remains open.
