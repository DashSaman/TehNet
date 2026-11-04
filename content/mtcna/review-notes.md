# TehNet MTCNA preparation review and evidence status

Checkpoint: 2026-11-04. Course ID: `tehnet-mtcna-routeros7-20261104`.

## Disposition

The bounded static-review findings have been resolved in the source package. The course remains a set of non-public working drafts: **zero lab-verified lessons, zero original application screenshots, zero publication-ready lessons and zero new public releases from this package**. Editor-save validation and scoped site-release qualification remain pending. Existing published course owners are separate from these working drafts.

## Recorded package

| Item | Recorded state |
|---|---|
| Written lessons | 24 substantial Markdown files across nine chapters |
| Metadata | 24 lesson metadata files |
| Text size | 29,722 whitespace-delimited words across the lesson Markdown files |
| Schematics | 14 precise diagrams, each supplied as SVG and WebP: 28 asset files |
| WordPress working drafts | 24 actual draft-creation receipts, IDs 232–255, parent 40 |
| Fresh independent WordPress readback | PASS: all 24 authenticated GET results matched raw content, draft status, slug and parent; comparison recorded 2026-11-04T16:16:11Z |
| RouterOS execution and original screenshots | Not performed / missing |
| Editor-save and scoped release qualification | Pending |

Local inventory counts and the receipt IDs/statuses were read afresh for this note. WordPress creation and independent GET comparisons are recorded in [wordpress-receipts.json](wordpress-receipts.json). The final offline build also successfully rendered all 24 actual source files. An earlier review statement about rendering 24 files before the final lesson existed was withdrawn; the successful build and readback reported here occurred after the final lesson was saved.

## Resolved findings and verification boundary

- The content reviewers' bounded static findings for lessons 01–16 and 17–24, including mismatches between lesson scenarios and their diagrams, are resolved in the source package. DHCP now explicitly uses dns-none=yes, bridge membership and NAT addresses match the text, R1/R2 commands are separated, and Wi-Fi, diagnostics and the final project have matching figures. This is a source-consistency result; it does not establish execution of commands, observed outcomes or a completed technical publication review. Final immutable URL pins are present in the exact WordPress raw-content readback.
- The draft generator checks the existing manifest before writing generated outputs. It refuses to replace progressed lesson state, changed gates, publication receipts, lab evidence, tested versions, original screenshot files or verified video-segment evidence. The omitted `video_segment_evidence` check was added and independently exercised in memory: populated evidence now raises `ValueError`. Initial draft generation remains permitted. Release history belongs in the separate [publication ledger](publication-ledger.json).
- The [publication controller](publication-controller.md) and saved automation prompt require a durable three-day window ID anchored to the first scheduled slot. A completed or uncertain write consumes that window for selection purposes until reconciled; retries cannot advance to another lesson in the same window. The controller requires a supported atomic release mutex and blocks public writes if it cannot obtain one. These are verified instructions and guard behavior, not a claim that a live release has been exercised.
- Existing owners 40 and 62–67 receive only qualified, reviewed scoped updates. A shared owner must contain the unique lesson section anchor and approved section content hash; its existing published status cannot prove a new installment was released. Working drafts must not become competing public owners. The production noindex launch gate remains applicable.
- The diagrams use immutable GitHub source URLs without invented WordPress attachment IDs. They are explanatory schematics, not screenshots, terminal output or acceptance evidence. SVG/WebP assets were committed before their URLs were inserted; all 24 draft payloads were subsequently read back exactly. Actual Gutenberg editor-save and rendered-page checks remain pending.

## Active schedule

Automation `6aeb53b439908191bfdaf9fbace0d08c` is enabled in `exact_schedule` mode. Its first nominal slot is **Saturday 2026-11-07 / 16 Aban 1405 at 09:00 Asia/Tehran**, equivalent to **05:30 UTC**, followed by one slot every three days. The status peek confirmed that it is enabled; `next_run_time` was `null`. Therefore the first slot is stated from the stored schedule, without claiming a separately confirmed next-run timestamp.

A blocked lesson stays next. There are no catch-up batches and no fixed occurrence count: the controller stops after 24 verified releases. January 15, 2027 is only the earliest final nominal slot if every lesson qualifies on time. See the [Persian publication calendar](publication-calendar.fa.md) and [saved automation](automation.json).

## Next concrete handoff

Provision an authorized, isolated CHR lab for lesson 1 with **1 GiB RAM**. Record the RouterOS and WinBox versions actually installed, interface/NIC mapping and network-isolation evidence. Establish a recovery checkpoint, execute the lesson from the documented starting state, and test recovery. Preserve original application screenshots and actual command output with expected-versus-observed results. Complete technical/editorial review, editor-save validation and the existing scoped release qualification before the controller may publish. Physical RouterBOOT and Wi-Fi evidence remain separate later requirements.

The official CHR installation reference is [MikroTik CHR installation](https://manual.mikrotik.com/docs/getting-started/installation-and-upgrade/install/chr-installation/). WordPress status/date behavior is documented in [Pages REST API](https://developer.wordpress.org/rest-api/reference/pages/) and [scheduling a post](https://make.wordpress.org/support/user-manual/posts/schedule-a-post/).

## Source review record

The preparation package is tracked in [pull request 82](https://github.com/DashSaman/TehNet/pull/82). Its repository CI is separate from the unexecuted RouterOS lab and publication qualification.
