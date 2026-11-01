# Issue63 — enterprise service discovery and an existing-ticket request journey

Spec: https://github.com/DashSaman/TehNet/issues/63. Base: edc4ab8.

The owner explicitly requested immediate implementation and continuous execution. Reuse the existing WordPress architecture and ticket entity; no separate CRM, duplicated quote backend, new city/service URL, or indexing/payment change. Work directly; one read-only staging-operator map was requested.

1. Capture current Home/Services and three TarazNet service journeys at desktop/mobile. Treat competitor content as self-description, not proof of capacity.
2. Add a short server-rendered service form to Services and Home using the existing `tn_ticket_submit` handler/private `tn_ticket` store. Name, email, service and problem are required; company optional. Preserve native nonce, honeypot and existing per-IP throttle. Return an expiring random receipt exposing reference/status only. Existing authorized staff see the same ticket and service context; no notification sent by intake.
3. Replace the existing Services body with editable core blocks: categorized cards, in-page navigation, six existing URL owners, three practical decision aids, geographic boundaries, workflow/quote explanation, inline form and relevant MyTel referral. The owner subsequently confirmed availability of monitoring, servers/virtualization, firewall, enterprise Wi-Fi and branch connectivity in this chat. Describe these services with scoped deliverables; vendor certifications, price, SLA and delivery guarantees remain unverified. Preserve homepage identity/hero/four journeys while improving service discovery and request access.
4. RED→GREEN contract checks; isolated native WordPress tests covering real POST/persistence/receipt/staff authorization, validation/spam/no-JS/mobile, blocked email/network/payment and exact cleanup. Screenshots before/after and editor roundtrip.
5. Extend the existing bounded operator with a separate exact catalog scope, qualify fresh backup/checksum/drift/repeat/rollback and preserved protected data. Publish only qualified/authorized scope; verify production via read-only probes. No production QA submissions. Commit bounded changes, leave Issue63 open and continue safe remaining gaps. Transfer only sanitized reusable lessons to -SEO.

Review focus: receipt privacy/cache isolation, array/unknown service rejection, shared ticket behavior, no-JS operation, capability gates and restoration of both owned page bodies and files without reverting foreign edits. Preserve MyTel production read-only, noindex, 25 inquiry-only products, closed payments, security incident gates and shared network/container layout.

## Execution ledger

- IN_PROGRESS: CP-01/CP-02 implemented locally. Before capture: Home, Services and three TarazNet URLs, desktop/mobile. Isolated native attempts exercised actual private ticket persistence and, in one attempt, both desktop/no-JS requests plus authorized staff visibility. Qualification is incomplete: navigation timeouts and a corrected staff selector prevented a full browser PASS. All attempts were restored; one fixture-owned dashboard draft needed guarded reconciliation before exact restoration. No live writes or parity claim.
- Latest local checks: 58 Python tests (one explicit host symlink-permission skip), 55 PHP contracts and three PHP syntax checks passed. These do not replace the pending full native journey, immutable release qualification or public before/after verification.


## Delivered package — actual outcome

- DEPLOYED_VERIFIED CP01/02: PR64/65, runtime/Home/Services source4aff178; native51 with two actual synthetic private requests and staff trace; exact restore; public139 plus14 TLS GETs. No production submission.
- DEPLOYED_VERIFIED first CP03/04/05 batch: PR66/sourcefd1209d; three existing content upgrades (monitoring acceptance, Wi-Fi brief, firewall matrix), native41/public41 each, body-only fresh backup/drift/repeat/hash/protected-state checks. Zero new article/URL/runtime; examples remain hypothetical.
- Published sanitized delivery evidence and reconciled coordination: PR67/CI41314181611. Central reuse: -SEO PR21/CI41314407511 merged. See the dated report/receipts for exact hashes and screenshots.
- Issue63 OPEN. Further server/virtualization/branch depth and real consented case evidence remain; GSC access actually refused subscription_required, intentional noindex is unchanged and requires separate owner approval. Neither browser counts nor the completed delivery package establish competitive parity/search gains.
