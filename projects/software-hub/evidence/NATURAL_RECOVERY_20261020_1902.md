# Natural recovery after the latest inventory correction

The four independently collected samples below passed after the preceding exact inventory-expectation correction. Each has an empty error list, preserved-source/container checks and a matching successful native service run. No manual sample was started.

| Natural sample, UTC | Result |
| --- | --- |
| 2026-10-20T17:25:12.162603Z | healthy |
| 2026-10-20T17:55:38.555635Z | healthy |
| 2026-10-20T18:25:45.956899Z | healthy |
| 2026-10-20T18:55:48.535859Z | healthy |

Totals are 61 samples: 19 healthy, 42 retained failures and zero deferred. All 57 earlier original sample files were rehashed and remain byte-for-byte unchanged. There are still two actual accepted publication events and two publications observed by healthy samples. Recovery does not erase the preceding failures or prove continuous uptime. The current maximum observation interval is 1830.014909 seconds; it is a sampling interval, not a measure of the earlier unconfirmed-health periods.

The native refresh run at 18:22:24 UTC returned not_due and completed successfully. It retained the previous accepted version; no new publication occurred. The next displayed timer occurrence, 21 October 00:21:41 UTC, precedes the current minimum eligibility time of 00:28:34 UTC. Another not_due before that threshold is expected; the schedule and freshness rules were not changed.

The three original signature chains, canonical install binding, 160 runtime hashes and three original passing-source proof bindings were rechecked. Three independent public HTTPS checks confirm the exact current profile, original proof hashes and selector. Arvan, LinuxMirrors and Liara remain active for that exact version. Hamravesh retains its historical failed preservation result and remains inactive, with no complete lab acceptance. All four current intents and today's eight charged attempts/1536 MiB remain; none was replayed or reset.

No website, container, source, configuration, unit, authentication, provider result or timer was changed in this follow-up. Payloads remain external; existing independent labs use only transient private noswap RAM. All three native timers are enabled and active. The original deadline remains 21 October 13:39:28.226058 UTC (17:09:28 Tehran). The final 48h observation is still ongoing and its completion record is absent.

[Sanitized summary](NATURAL_RECOVERY_20261020_1902.json). [Preceding incident and narrow correction](WATCH_FOLLOWUP_20261020_1657.md). Original journals, snapshots and operational metadata remain private and were not exported.

Local publication-gate check initially rejected Windows CRLF line endings in the preceding report working copy. The index and committed blob were unchanged, and normalized working content matched exactly; the older original receipt still matched byte-for-byte. Corrected only that local comparison and reran the full gate. This was a local verification-helper error, not an additional native monitoring failure; no historical file or server state was altered. A subsequent local whitespace check caught two malformed not_due labels introduced during helper creation; only those labels were corrected before full re-verification.
