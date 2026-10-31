# Local bundle path normalization and private failure evidence

Status: VERIFIED_LOCAL_TOOLING. Windows18PASS/1SKIP, initial Linux CI19PASS; final Windows-only ACL followup has red/green evidence and requires fresh current-head CI before integration. No production/staging release is part of this unit. See the dated receipt for exact code/CI scope.

The first support publication package stopped locally before native execution. A bounded reproduction now contrasts a269-character lexical relative output path containing `..` with its235-character resolved destination: relative packaging fails, absolute packaging succeeds, with the same immutable source/scope. Do not replay the completed support deployment.

1. Preserve the original partial package and full reproduction trace privately. Add a failing boundary test that drives the actual Windows relative output case, then normalize a new destination before creating/writing members. Retain immutable source, new-directory and symlink safeguards.
2. Add an explicit optional private diagnostics directory for failures before release logging is initialized. Validate an existing absolute private directory outside Git/web roots, reject symlink/junction paths, require restricted POSIX permissions or a restricted Windows ACL. Keep stdout generic; raw trace and exact paths belong only in the validated private directory.
3. Verify path normalization, no adoption of existing/symlink destinations, restrictive diagnostic permissions, and that a sentinel secret in an exception appears only in the private log, never CLI stdout/stderr. Run existing operator regressions; no remote calls required.
4. Reproduce complete committed-payload bundles through relative and absolute paths after the fix and compare members/tool/runtime digests. Retain failed attempts privately; no automatic native retry or journal reset.
5. Record sanitized evidence, limits, current continuation and morning-report checkpoint; publication guard/known-value scan, small commit and ordinary CI-backed PR integration. The installed production source remains the prior qualified source; this tooling change is not a redeployment.

Next independent package: official-source research and a distinct useful expansion of the existing IP/DHCP/DNS lesson. Security gates, noindex, real commerce and MyTel freeze remain unchanged.
