# Issue63 — enterprise service discovery and an existing-ticket request journey

Spec: https://github.com/DashSaman/TehNet/issues/63. Base: edc4ab8.

The owner explicitly requested immediate implementation and continuous execution. Reuse the existing WordPress architecture and ticket entity; no separate CRM, duplicated quote backend, new city/service URL, or indexing/payment change. Work directly; one read-only staging-operator map was requested.

1. Capture current Home/Services and three TarazNet service journeys at desktop/mobile. Treat competitor content as self-description, not proof of capacity.
2. Add a short server-rendered service form to Services and Home using the existing `tn_ticket_submit` handler/private `tn_ticket` store. Name, email, service and problem are required; company optional. Preserve native nonce, honeypot and existing per-IP throttle. Return an expiring random receipt exposing reference/status only. Existing authorized staff see the same ticket and service context; no notification sent by intake.
3. Replace the existing Services body with editable core blocks: categorized cards, in-page navigation, six existing URL owners, three practical decision aids, geographic boundaries, workflow/quote explanation, inline form and relevant MyTel referral. Unverified monitoring/server/firewall/Wi-Fi capacity is explicitly subject to scope review; no invented availability, vendor certification, price or SLA. Preserve homepage identity/hero/four journeys while improving service discovery and request access.
4. RED→GREEN contract checks; isolated native WordPress tests covering real POST/persistence/receipt/staff authorization, validation/spam/no-JS/mobile, blocked email/network/payment and exact cleanup. Screenshots before/after and editor roundtrip.
5. Extend the existing bounded operator with a separate exact catalog scope, qualify fresh backup/checksum/drift/repeat/rollback and preserved protected data. Publish only qualified/authorized scope; verify production via read-only probes. No production QA submissions. Commit bounded changes, leave Issue63 open and continue safe remaining gaps. Transfer only sanitized reusable lessons to -SEO.

Review focus: receipt privacy/cache isolation, array/unknown service rejection, shared ticket behavior, no-JS operation, capability gates and restoration of both owned page bodies and files without reverting foreign edits. Preserve MyTel production read-only, noindex, 25 inquiry-only products, closed payments, security incident gates and shared network/container layout.

## Execution ledger

- IN_PROGRESS: CP-01/CP-02. Fresh main fetched; isolated existing worktree clean and new feature branch created. Before capture running. No live writes.
