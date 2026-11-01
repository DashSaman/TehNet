# P2 publication guard file coverage

Status: IN_PROGRESS. Existing owner authorization covers repository privacy fixes and local-only history preparation. No production or shared-history mutation is included.

Fresh private history checkout contains1513 tracked paths; ordinary Windows Path.exists reports only1276, while an extended-length root reports1513. Existing guard silently skips paths it cannot see. Thus its PASS alone is insufficient in that checkout; the separate Git-object known-value/path scan covered all reachable objects. The historical original scan count remains recorded.

Design: use an extended absolute path for Windows filesystem reads, preserve the original root for Git enumeration, and fail closed with sanitized path/category diagnostics for any unreadable tracked file. Report enumerated and read counts separately. Do not print OS exception text, contents or private absolute roots. Keep the existing content rules and narrowly scoped public-contact classification. Apply identical guard/test changes to all three repositories; no runtime/site file changes.

- [x] Observe missing-file, unreadable-file and actual Windows long-path regressions before the fix.
- [x] Implement minimal filesystem read and count correction; pass relevant tests and all private-value scans.
- [x] Recheck the original deep checkout with all1513 paths, preserving its prior incomplete scan receipt and exact main tree.
- [ ] Ordinary CI-backed PRs for the three repositories, with private snapshots before integration.
- [ ] Refresh private local clean-history references after normal merges; remote rewrite stays NEEDS_APPROVAL.

The initial history-preparation wrapper also captured only unittest stdout, while unittest writes its summary to stderr. It stopped before a verification receipt despite process exit0; corrected capture reran the complete tests without refiltering or overwriting the first snapshot. This is a preparation error, distinct from the newly confirmed filesystem-coverage gap.
