# Search metadata — test evidence and deployment gate

Date: 2026-10-13.

## Status
**PREPARED AND UNIT-TESTED — NOT DEPLOYED.** This applies only to the new metadata MU-plugin. The earlier visual release TehNet 0.5.1 is already deployed; do not confuse the two stages.

Source: `site/mu-plugins/tehnet-search-metadata.php`.
Test: `tests/search-metadata-test.php`.

Test environment: PHP 8.4.24 in the assistant's isolated container. WordPress functions are explicit test stubs; no real database, WordPress runtime or production connection is exercised by this suite.

Initial RED: running the test before creating the module returned exit 1 with `FAIL: metadata module is missing (expected initial RED)`.

Final GREEN: `php tests/search-metadata-test.php` returned **CHECKS=33 FAILURES=0**, exit 0. `php -l site/mu-plugins/tehnet-search-metadata.php` reported no syntax errors. The suite was rerun after writing the final source.

## Exact tested bytes

| File | SHA256 | Git blob SHA |
|---|---|---|
| Module | `5ae28138870402180922fd868f02596209fcb39db6e70ce7b2ebc2c84db0413c` | `468ce76d700952e6f6a2b48b6627f93f24edaa72` |
| Test | `25bb399bdb5a9deea013ef68d618c4a6650fd7c556d74fea631d9e850b9b6b69` | `39da2615176715430d4d0d3eced66782cb01db36` |

## Successful checks

```text
PASS homepage description exactly once
PASS homepage description is meaningful Persian
PASS title canonical robots owners untouched
PASS no organization or fabricated rich-result types
PASS no outgoing script or tracking
PASS Open Graph URL and locale
PASS manual excerpt takes priority
PASS HTML and attributes escaped
PASS Unicode truncation remains valid and bounded
PASS invalid UTF8 safely omitted
PASS skip admin
PASS skip feed
PASS skip 404
PASS skip search
PASS skip preview
PASS skip unpublished object
PASS skip password protected even with cookie
PASS no interference with product metadata
PASS null queried object safely ignored
PASS external SEO owner wins
PASS no guessed description for unknown empty page
PASS future pages work with explicit excerpt
PASS sample page is not promoted
PASS blog pagination Open Graph matches page URL
PASS full route keyed not leaf slug
PASS existing profile description not duplicated
PASS valid ProfilePage and Person
PASS stable profile identity
PASS no private telephone or brand social impersonation
PASS profile description available without legacy theme callback
PASS renamed page does not get false Person schema
PASS render does not write state
PASS registered only front-end head hook
CHECKS=33 FAILURES=0
```

## Implementation boundaries

- One removable MU-plugin; no replacement of the deployed theme or Core plugin.
- Exact route fallbacks for established page intents; stored editorial excerpts take priority on normal pages.
- Unknown pages with no explicit excerpt deliberately receive no generated metadata. Lesson descriptions and future pages still need editorial excerpts; this is not a claim of site-wide completeness.
- No attempt to turn arbitrary SVG/menu/code text into a description.
- Existing résumé description remains owned by its theme callback; this module does not print a duplicate.
- Known full SEO plugins take precedence; unrecognized metadata owners must be checked manually or integrated via the documented external-owner filter.
- Minimal ProfilePage/Person only on the existing résumé route/template with matching visible names. No telephone, invented credentials, ratings, statistics, employer assertions or business socials presented as personal sameAs.
- Does not emit title/canonical/robots, change options, enable indexing, submit URLs, call external services or modify customer data.
- Open Graph image and provider-specific measurement are not implemented here.

## Deployment prerequisites — still open

1. Restore the authorized Remote Desktop Commander management connection. The site's public HTTPS and WPVibe read access work; the repeated error is `Timeout - no response from device` on RoboT, not a proven website outage.
2. Read the real MU-plugin directory and all current metadata owners. If the target file or another owner exists, inspect and reconcile it; never overwrite blindly.
3. Take a fresh restricted backup and record current theme/Core/protected settings and unrelated-service fingerprints. Do not copy backup bytes or secrets into Git.
4. Lint the module using the actual WordPress container's PHP version, then use an explicit one-file deployment allowlist. Target: `wp-content/mu-plugins/tehnet-search-metadata.php`. Preserve existing MU-plugins.
5. Verify public and origin output: homepage, profile, established hubs/services, blog pagination and unsupported/private contexts. One description where this module owns it; no duplicate on profile; unchanged title/canonical/intentional noindex; valid consistent JSON-LD.
6. Verify output escaping and privacy again against the real saved HTML. Existing business-office contact on business pages is separate from the excluded personal mobile.
7. On regression, remove/restore only this newly introduced file, not a full database or theme rollback over newer data. No service restart is part of the plan.
8. Record integration/live results and update coordination docs before claiming deployment complete.

## Fresh content-read observations

WPVibe REST read of published pages on 2026-10-13 showed empty raw excerpts, default Sample Page ID 2 still published, and prelaunch wording in Learn ID 6. These are launch-review items. They were not silently deleted, rewritten, or made indexable in this continuation.

## Separate measurement limitation

GSC Wizard refused list_sites with `payment_required`; no property/GA4/AI-report data was obtained, no subscription changed. Current mobile lab audit and its limitations are in `seo/SEO_AI_READINESS_2026-10-13.md`.
