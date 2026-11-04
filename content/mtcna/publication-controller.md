# TehNet MTCNA publication controller

The owner authorized scheduled course publication on 2026-11-04. The first window is **2026-11-07 at 09:00 Asia/Tehran**, followed by one window every three days. A window is an execution opportunity, not evidence that a lesson is ready or was published.

## Sources of truth

Read current repository `AGENTS.md`, `HANDOFF.md`, `PROGRESS.md`, and the applicable release instructions first. Then read `content/mtcna/course-manifest.json`, `publication-ledger.json`, `wordpress-receipts.json`, and this file. The preparation branch is `content/mtcna-saturday-20261107`; prefer the merged main copy once that exact package has been integrated. Do not substitute an older PR 79 proposal or a different course identifier.

Brand: **TehNet / تهنت / تهران نتورک / Tehran Network**, YouTube `https://www.youtube.com/@tehran.network021`. The MTCNA written series is independent of the old recordings. Queue is not attributed to an old lesson without separately verified segment evidence.

## One execution

1. Read the real clock and current WordPress site timezone. Never publish before the applicable window or before the installment's recorded earliest date. A manual early invocation must remain read-only for public content.
2. Calculate a durable window ID as the scheduled Tehran timestamp `first_window + floor((now - first_window) / 72 hours) * 72 hours`. Before selecting a lesson, reconcile the ledger entry for that window. If it already has a successful or uncertain public write, verify/reconcile that same operation and do not advance to another lesson. Find the lowest-numbered installment without a verified publication receipt. Do not skip a blocked installment. Verify its prerequisites and live URLs. Publish at most one installment per scheduled window, including sequential retries and manual wake-ups after a missed run. A blocked window can be retried, but it may acquire only one successful lesson receipt.
3. Reconcile any prior uncertain operation from exact WordPress IDs and live content before retrying. Use a stable operation key containing course ID, lesson number and approved payload hash. Acquire the repository/project release mutex through its supported atomic compare-and-set or existing qualified locking mechanism. An ordinary read followed by an unconditional write is not a mutex. If a lock cannot be obtained, do not mutate public content. Do not silently steal an expired lock: reconcile its operation first.
4. Check the full lesson evidence. Technical/editorial review, actual RouterOS run, original readable application screenshots, installed version/date, expected-versus-observed acceptance results, rollback evidence, correct attribution, editor-save validation and the existing scoped site-release qualification must all be supported by actual records. Wi-Fi and RouterBOOT demonstrations also require appropriate physical hardware evidence. Diagrams, expected output, a downloaded image and source-document review do not satisfy runtime gates.
5. If evidence is missing, leave WordPress drafts as drafts, keep the same installment next, record BLOCKED with exact missing items and provide a brief Persian report. Do not generate screenshots or fabricate results to make a deadline.
6. For `merge_existing_owner`, fetch the owner with `context=edit`, preserve its valid content and prepare a scoped merged payload with the lesson anchor. Compare fresh content/hash and modification time against the version that was reviewed. Stop on unexplained drift. Do not replace the existing hub, its video archive or previous installments with an individual lesson body. Never set an already published owner to `future` or promote its working draft to a duplicate public URL.
7. For `publish_new_topic`, confirm the distinct intent and target slug have no existing owner. The draft ID is the intended target. Use the approved content and minimal necessary status/slug/date fields through the existing qualified release mechanism. For `merge_predecessor_owner`, resolve the exact target ID from the specified predecessor's verified receipt; absence is a blocker.
8. Preserve the existing noindex/search-launch controls and all unrelated site data, services, forms, products, payments and runtime configuration. This task does not send Telegram/email messages or change the YouTube channel.
9. Read back the exact target after a write, then verify the public URL, HTTP response, expected lesson text, images, previous/next navigation, canonical and robots directives. For an owner shared by multiple installments, the qualified merged payload must insert the manifest's unique section_anchor (or an explicitly reviewed equivalent marker) and verification must match that section plus its approved content hash; the owner's published status alone is insufficient. Record actual release time, final URL, lesson operation key and consumed window ID atomically in the release ledger. An uncertain or failed readback is not a successful release.
10. Commit the receipt and next pending installment without overwriting parallel project updates. Only increment completed count after verification. When all 24 are verified, disable this specific automation and report completion. A blocked slot does not count as a completed installment.

## Current verified boundary

This workspace has no QEMU, Docker, VirtualBox, KVM, RouterOS lab or physical radio. The initial course package therefore has **zero lab-verified or publication-ready installments**. Public articles must not be released merely because the schedule exists. The first lesson needs a real isolated CHR VM, installed-version/console evidence, NIC/isolation verification, original capture files and a tested recovery checkpoint.

WordPress core REST reads are connected. WPVibe's `upload_media` call returned plugin-missing/404 on 2026-11-04. Do not retry plugin-backed routes or install a plugin as an incidental change. The prepared diagrams use public immutable GitHub WebP URLs, with SVG sources in the repository; they are not WordPress media attachments or application screenshots. Native media migration can be done later through an authorized supported upload path.

## Official operational references

- https://make.wordpress.org/support/user-manual/posts/schedule-a-post/
- https://developer.wordpress.org/rest-api/reference/pages/
- https://developer.wordpress.org/plugins/cron/
- https://manual.mikrotik.com/docs/getting-started/installation-and-upgrade/install/chr-installation/
