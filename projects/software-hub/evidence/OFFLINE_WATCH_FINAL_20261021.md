# Final finite48h offline watch report

Status: completed_with_incidents. The native completion record and all original samples were read after the real deadline. The 42 inventory failures and both deferred samples remain; this is not incident-free or continuous-uptime acceptance.

## Window, counts and timing

The immutable window is 2026-10-19T13:39:28.226058Z to 2026-10-21T13:39:28.226058Z: exactly48hours. First sample equals the start. Last inside-window sample: 2026-10-21T13:30:17.893938Z. The terminal healthy sample was collected at 2026-10-21T14:00:18.585601Z, 1250.359543seconds after the deadline; actual first-to-terminal span was48h20m50.359543s. The window itself was not extended or reset.

| Scope | Total | Healthy | Error | Deferred |
| --- | ---: | ---: | ---: | ---: |
| Inside fixed48h window |98|54|42|2|
| All native records, including later terminal |99|55|42|2|

Maximum adjacent sample interval: 1830.014909s. Maximum interval between nondeferred samples: 3605.521443s, below the4500s/75minute limit. Maximum interval between successful health confirmations: 63196.200659s, or17h33m16.200659s. Error samples count as observations in the native policy; they do not confirm full health. Deferred samples do not fill that gap. All61previous original sample hashes were explicitly rechecked unchanged.

## Retained incidents and periods without successful health confirmation

Every inventory error records the same strict existing-container-fingerprint mismatch. Original signature/install-binding and origin flags passed in those records, but the observer stopped at inventory before its final engine-health predicate. Each correction below changed only the exact independently verified expectation under locks/private backup after an owner-authorized deployment; no site, container, source, unit, credential or history was replaced.

| Error checks | First/last failed check UTC | Exact expectation corrected UTC | Next natural healthy UTC | Surrounding healthy-confirmation gap, seconds |
| ---: | --- | --- | --- | ---: |
|1|2026-10-19T17:19:57.191325Z / 2026-10-19T17:19:57.191325Z|2026-10-19T17:47:36.609669Z|2026-10-19T17:50:06.578938Z|3611.98419|
|34|2026-10-19T18:20:07.246921Z / 2026-10-20T10:53:19.442526Z|2026-10-20T10:54:06.620818Z|2026-10-20T11:23:22.779597Z|63196.200659|
|3|2026-10-20T11:53:28.500523Z / 2026-10-20T12:53:45.817368Z|2026-10-20T12:56:46.003656Z|2026-10-20T13:23:46.402135Z|7223.622538|
|2|2026-10-20T14:23:48.536301Z / 2026-10-20T14:54:18.551210Z|2026-10-20T14:59:19.576210Z|2026-10-20T15:24:28.533770Z|5441.112991|
|2|2026-10-20T16:24:50.944754Z / 2026-10-20T16:55:09.216198Z|2026-10-20T17:03:04.462231Z|2026-10-20T17:25:12.162603Z|5423.618558|

The nonhealthy-period objects in the JSON distinguish first-to-last failed-check spans from the larger interval between surrounding successful confirmations. Neither duration is a measured application outage.

| Deferred sample UTC | Recorded reason | Surrounding successful confirmations UTC | Gap, seconds |
| --- | --- | --- | ---: |
|2026-10-21T05:28:22.476079Z|Existing worker/publication lock held; exact holder unknown|2026-10-21T04:58:22.078378Z / 2026-10-21T05:58:27.599821Z|3605.521443|
|2026-10-21T06:28:27.801473Z|Existing worker/publication lock held; exact holder unknown|2026-10-21T05:58:27.599821Z / 2026-10-21T06:58:28.374635Z|3600.774814|

## Actual scheduled publications and exact-generation source results

Three real native published events, three distinct new accepted profile SHAs and the native healthy-observed counter of three coincide numerically; they are separate measures. A fourth SHA in samples belongs to the baseline accepted before the window. Historical signatures and date rules were rechecked at original acceptance; current generation freshness also passed at current wall time. No stale generation was reactivated.

| Run | Accepted UTC | Native published UTC | Profile SHA256 |
| --- | --- | --- | --- |
|run-20261020-002025-75be29d8|2026-10-20T00:23:53.116922+00:00|2026-10-20T00:23:55.567955+00:00|fa5c9cf4a358b255a39363a46e32547bb54aaa2882a2e6d5a827dd11fd765724|
|run-20261020-122501-3aeeac00|2026-10-20T12:28:34.875382+00:00|2026-10-20T12:28:37.346995+00:00|a07664bf5543e8e159bd96e3a49b2c91ea3977a00b29264191eae3720d6c0808|
|run-20261021-062356-9f2df70c|2026-10-21T06:27:19.581939+00:00|2026-10-21T06:27:22.108766+00:00|be34b7d12a2a77479c8846179aae95636c64b46701655fbe730605f57b7ee4f3|

Each publication passed its original three Ubuntu signature/date chains, exact native candidate/install binding, canonical lab isolation/preservation and four retained public-file hash bindings. The current four public files were independently fetched over valid HTTPS and match, allowing only the previously documented single known edge beacon normalization for HTML. Original install proof bytes were rehashed and retained privately.

| Generation, accepted UTC | Arvan | LinuxMirrors | Liara | Hamravesh |
| --- | --- | --- | --- | --- |
|2026-10-20T00:23:53.116922+00:00|pass 2026-10-20T00:28:04.916933+00:00|pass 2026-10-20T00:39:10.993725+00:00|pass 2026-10-20T00:42:32.362800+00:00|pass 2026-10-20T00:45:42.955487+00:00|
|2026-10-20T12:28:34.875382+00:00|pass 2026-10-20T12:32:31.730708+00:00|pass 2026-10-20T12:43:43.868553+00:00|pass 2026-10-20T12:46:56.833940+00:00|failed 2026-10-20T12:50:13.363693+00:00|
|2026-10-21T06:27:19.581939+00:00|pass 2026-10-21T06:32:02.757323+00:00|failed 2026-10-21T06:32:34.282345+00:00|pass 2026-10-21T06:35:46.193947+00:00|pass 2026-10-21T06:39:00.870408+00:00|

Ten passing source proofs were rehashed from their original bytes and bound to the exact generation. Each has58packages plus six complete-hash indices, eight functional tools, four invalid-input/nonmutation cases, disconnected installation and full noswap/swap0/noOOM/preservation evidence. Current selectable sources are Arvan, Liara and Hamravesh for the exact latest SHA. LinuxMirrors is inactive. API and page expose no old-generation passing choice.

The20October midday Hamravesh failure remains: internal installation exited0, but its final environment-preservation assertion failed during a separate authorized deployment; full acceptance was absent and partial results were never promoted. Its new-generation21October pass is a distinct charged attempt, not a replay of the old failed intent.

The21October LinuxMirrors lab exited1 at06:32:34UTC in the original HTTP status/encoding guard. The original log does not retain the exact status/header, so redirect, non200status and nonidentityencoding cannot be distinguished retrospectively. Four network-free fixtures reproduced that same guard error with302,404,503and200/gzip responses, all before writing a payload file. No upstream cause was invented, no guard weakened and no failed intent repeated.

Provider reservations remain:19October4attempts/768MiB;20October8/1536MiB;21October4/768MiB, including both failures and the pre-window baseline generation. These are durable reservations, not measured wire traffic. The current and historical intents remain. The eight scheduled in-window published/not_due outcomes are enumerated in JSON. The later21October18:20check was outside the window and correctly not_due; it is not another publication.

## Fresh verification and limits

Current-time source/protected-container checks and160runtime hashes pass.23independent public HTTPS checks cover current metadata/code/proof/selector and existing main/private routes.23targeted local tests pass using the existing project environment; the initial global interpreter had16passes and one module import error because pwdlib was absent. No dependency was installed or production code changed. The initial historical-proof revalidation hit current-time metadata staleness; historical date checks were then correctly evaluated at recorded acceptance while the unmodified current-time live freshness gate passed separately. These local verification conditions are not extra native watch failures.

The final native classification is reproduced independently: deadline reached, terminal sample healthy, at least one accepted publication inside the window and no nondeferred gap over75minutes; retained failures select completed_with_incidents and native limitations are empty. This does not establish continuous uptime/SLA, booted-VM installation, Iranian cutover/reachability/tariffs or the missing original OFFLINE_SOFTWARE_CATALOG. The full error/deferred periods above remain material coverage caveats.

Payloads remain on external sources; existing independent labs used only transient private noswapRAM. Main site/theme/content, other services, VPN password/private data and Rubika token were not modified. Original22research blobs/attribution remain. Original logs, snapshots, server paths and internal IDs are retained privately and are not part of this public export.

## Retirement and references

The native finite timer is already inactive after completion. After this report is registered, disable only that finite timer and delete the existing automation-4; confirm offline-refresh and provider-auto stay enabled/active. Record the actual retirement receipt separately. No new window, schedule or follow-up will be created.

Verified predecessor: 350dff9698233c485751d0d262ab625d605d8f39. Authorized branch: docs/melika-consolidation-2026-10-17; main remains unmerged. Final publication refs are recorded by the closing receipt and chat. [Sanitized machine-readable report](OFFLINE_WATCH_FINAL_20261021.json).

## Every retained sample, timestamp and outcome

The last row is the later terminal sample; the other98rows are inside the original window. These are sanitized outcomes, not raw observer snapshots.

| # | Checked UTC | Scope | Result |
| ---: | --- | --- | --- |
|1|2026-10-19T13:39:28.226058Z|inside48h|healthy|
|2|2026-10-19T13:39:34.380720Z|inside48h|healthy|
|3|2026-10-19T13:49:21.802980Z|inside48h|healthy|
|4|2026-10-19T14:19:21.796941Z|inside48h|healthy|
|5|2026-10-19T14:49:48.452924Z|inside48h|healthy|
|6|2026-10-19T15:19:49.023985Z|inside48h|healthy|
|7|2026-10-19T15:49:50.844724Z|inside48h|healthy|
|8|2026-10-19T16:19:54.190397Z|inside48h|healthy|
|9|2026-10-19T16:49:54.594748Z|inside48h|healthy|
|10|2026-10-19T17:19:57.191325Z|inside48h|error / container_inventory_changed|
|11|2026-10-19T17:50:06.578938Z|inside48h|healthy|
|12|2026-10-19T18:20:07.246921Z|inside48h|error / container_inventory_changed|
|13|2026-10-19T18:50:18.580008Z|inside48h|error / container_inventory_changed|
|14|2026-10-19T19:20:25.122739Z|inside48h|error / container_inventory_changed|
|15|2026-10-19T19:50:26.464657Z|inside48h|error / container_inventory_changed|
|16|2026-10-19T20:20:27.115777Z|inside48h|error / container_inventory_changed|
|17|2026-10-19T20:50:29.944756Z|inside48h|error / container_inventory_changed|
|18|2026-10-19T21:20:31.427859Z|inside48h|error / container_inventory_changed|
|19|2026-10-19T21:50:31.538601Z|inside48h|error / container_inventory_changed|
|20|2026-10-19T22:20:36.599845Z|inside48h|error / container_inventory_changed|
|21|2026-10-19T22:50:38.016894Z|inside48h|error / container_inventory_changed|
|22|2026-10-19T23:20:39.412805Z|inside48h|error / container_inventory_changed|
|23|2026-10-19T23:50:43.819401Z|inside48h|error / container_inventory_changed|
|24|2026-10-20T00:20:44.222422Z|inside48h|error / container_inventory_changed|
|25|2026-10-20T00:50:45.203401Z|inside48h|error / container_inventory_changed|
|26|2026-10-20T01:20:45.945410Z|inside48h|error / container_inventory_changed|
|27|2026-10-20T01:50:46.527960Z|inside48h|error / container_inventory_changed|
|28|2026-10-20T02:20:48.598814Z|inside48h|error / container_inventory_changed|
|29|2026-10-20T02:50:52.707164Z|inside48h|error / container_inventory_changed|
|30|2026-10-20T03:20:54.757978Z|inside48h|error / container_inventory_changed|
|31|2026-10-20T03:51:18.463661Z|inside48h|error / container_inventory_changed|
|32|2026-10-20T04:21:22.471857Z|inside48h|error / container_inventory_changed|
|33|2026-10-20T04:51:25.367358Z|inside48h|error / container_inventory_changed|
|34|2026-10-20T05:21:27.838212Z|inside48h|error / container_inventory_changed|
|35|2026-10-20T05:51:28.828470Z|inside48h|error / container_inventory_changed|
|36|2026-10-20T06:21:30.935311Z|inside48h|error / container_inventory_changed|
|37|2026-10-20T06:51:33.086173Z|inside48h|error / container_inventory_changed|
|38|2026-10-20T07:21:48.617476Z|inside48h|error / container_inventory_changed|
|39|2026-10-20T07:52:08.527730Z|inside48h|error / container_inventory_changed|
|40|2026-10-20T08:22:18.616062Z|inside48h|error / container_inventory_changed|
|41|2026-10-20T08:52:26.178846Z|inside48h|error / container_inventory_changed|
|42|2026-10-20T09:22:48.531881Z|inside48h|error / container_inventory_changed|
|43|2026-10-20T09:53:13.623884Z|inside48h|error / container_inventory_changed|
|44|2026-10-20T10:23:18.517841Z|inside48h|error / container_inventory_changed|
|45|2026-10-20T10:53:19.442526Z|inside48h|error / container_inventory_changed|
|46|2026-10-20T11:23:22.779597Z|inside48h|healthy|
|47|2026-10-20T11:53:28.500523Z|inside48h|error / container_inventory_changed|
|48|2026-10-20T12:23:28.540361Z|inside48h|error / container_inventory_changed|
|49|2026-10-20T12:53:45.817368Z|inside48h|error / container_inventory_changed|
|50|2026-10-20T13:23:46.402135Z|inside48h|healthy|
|51|2026-10-20T13:53:47.420779Z|inside48h|healthy|
|52|2026-10-20T14:23:48.536301Z|inside48h|error / container_inventory_changed|
|53|2026-10-20T14:54:18.551210Z|inside48h|error / container_inventory_changed|
|54|2026-10-20T15:24:28.533770Z|inside48h|healthy|
|55|2026-10-20T15:54:48.544045Z|inside48h|healthy|
|56|2026-10-20T16:24:50.944754Z|inside48h|error / container_inventory_changed|
|57|2026-10-20T16:55:09.216198Z|inside48h|error / container_inventory_changed|
|58|2026-10-20T17:25:12.162603Z|inside48h|healthy|
|59|2026-10-20T17:55:38.555635Z|inside48h|healthy|
|60|2026-10-20T18:25:45.956899Z|inside48h|healthy|
|61|2026-10-20T18:55:48.535859Z|inside48h|healthy|
|62|2026-10-20T19:26:00.216171Z|inside48h|healthy|
|63|2026-10-20T19:56:28.467196Z|inside48h|healthy|
|64|2026-10-20T20:26:31.650018Z|inside48h|healthy|
|65|2026-10-20T20:56:32.476423Z|inside48h|healthy|
|66|2026-10-20T21:26:37.987561Z|inside48h|healthy|
|67|2026-10-20T21:56:38.228772Z|inside48h|healthy|
|68|2026-10-20T22:26:48.541017Z|inside48h|healthy|
|69|2026-10-20T22:57:05.002525Z|inside48h|healthy|
|70|2026-10-20T23:27:05.127852Z|inside48h|healthy|
|71|2026-10-20T23:57:13.762394Z|inside48h|healthy|
|72|2026-10-21T00:27:15.226131Z|inside48h|healthy|
|73|2026-10-21T00:57:21.956610Z|inside48h|healthy|
|74|2026-10-21T01:27:32.770989Z|inside48h|healthy|
|75|2026-10-21T01:57:33.066256Z|inside48h|healthy|
|76|2026-10-21T02:27:46.096388Z|inside48h|healthy|
|77|2026-10-21T02:57:48.656989Z|inside48h|healthy|
|78|2026-10-21T03:27:56.982041Z|inside48h|healthy|
|79|2026-10-21T03:58:18.461716Z|inside48h|healthy|
|80|2026-10-21T04:28:19.118107Z|inside48h|healthy|
|81|2026-10-21T04:58:22.078378Z|inside48h|healthy|
|82|2026-10-21T05:28:22.476079Z|inside48h|deferred / existing_worker_publication_lock_held|
|83|2026-10-21T05:58:27.599821Z|inside48h|healthy|
|84|2026-10-21T06:28:27.801473Z|inside48h|deferred / existing_worker_publication_lock_held|
|85|2026-10-21T06:58:28.374635Z|inside48h|healthy|
|86|2026-10-21T07:28:28.470753Z|inside48h|healthy|
|87|2026-10-21T07:58:30.855980Z|inside48h|healthy|
|88|2026-10-21T08:28:36.397788Z|inside48h|healthy|
|89|2026-10-21T08:58:37.747216Z|inside48h|healthy|
|90|2026-10-21T09:28:40.371321Z|inside48h|healthy|
|91|2026-10-21T09:58:48.532359Z|inside48h|healthy|
|92|2026-10-21T10:29:06.526151Z|inside48h|healthy|
|93|2026-10-21T10:59:08.583638Z|inside48h|healthy|
|94|2026-10-21T11:29:12.438296Z|inside48h|healthy|
|95|2026-10-21T11:59:17.192566Z|inside48h|healthy|
|96|2026-10-21T12:29:28.539725Z|inside48h|healthy|
|97|2026-10-21T12:59:48.514324Z|inside48h|healthy|
|98|2026-10-21T13:30:17.893938Z|inside48h|healthy|
|99|2026-10-21T14:00:18.585601Z|later terminal|healthy|
