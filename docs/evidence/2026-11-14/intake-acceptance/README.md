# Integrated request-acceptance — isolated staging (2026-11-14)

State under test: PR100 decision package APPLIED + PR101/102/103 revisions in
their verified form (publisher state as staged). Environment: tehnet-ux-preview
(WordPress isolated, external HTTP/mail/cron closed, noindex intact).

## What was exercised (intake-accept.json — 26 checks, PASS)
1. **Service journey** (the real CTA path from the reconciled page 33):
   /services/?tn_service_context=server-scoping → nonce → POST admin-post →
   302 /support/?tn_ticket=sent&tn_service_receipt=<token> → private tn_ticket
   with _tn_request_kind=service + customer thread + receipt transient.
2. **B2B quote**: /b2b/ form → POST with real catalog product (id 85, qty 2) →
   302 b2b/?tn_quote=sent → private tn_quote with items a:1:{...85...}, state=received.
3. **Support ticket**: /support/ form → POST → private tn_ticket (plain).
4. **Negatives**: bad nonce 403; honeypot-filled 400; unknown service context 400;
   invalid email 400; invalid quote qty 400. Missing-nonce lifetime note: real
   expiry (~12-24h tick) not simulatable in-session; the invalid-nonce path
   exercises the same check_admin_referer failure branch.
5. **Rate limit**: 5 ticket-bucket attempts accepted, 6th → 429. Discovered
   behaviour (documented for ops): throttle counts ATTEMPTS reaching it,
   including rejected ones — validation negatives consume slots.
6. **Cleanup**: created records deleted by ID (incl. 3 earlier orphans);
   counts restored to baseline (tickets 0, quotes 0); receipt + throttle
   transients cleared.

## Forms rendering (curl-level = no-JS by construction)
All three forms render with hidden nonce + honeypot + action/submit on
/services/ (context preselected), /b2b/ (product selects), /support/.
No-JS: forms are plain HTML POST — the curl POSTs contain no JavaScript.
Visual RTL/mobile screenshots for each page exist in the per-PR evidence
(docs/evidence/2026-11-13/{remote-buyer,b2b-buyer...}/ + 2026-11-13/seo-jsonld).
A fresh browser screenshot pass was attempted; the executor host's browser
process wedged after earlier runs (honest note) — non-blocking because the
per-PR visual evidence already covers the same pages/viewports.

## Limitations (honest)
- CAPTCHA: staging has no tn_recaptcha_enabled option → verify() returns ok
  (fail-open by design when disabled); the real Google challenge path is NOT
  exercised (same framing as PR94's fixture). Production CAPTCHA configuration
  was not inspected (credentials out of scope).
- Real email delivery, cron, payments: closed/blocked on staging by design.
- One driver defect found+fixed during the run: urlencode needed doseq=True
  for PHP array fields (tn_item_product[]) — without it items arrive as a
  stringified "['85']" and validate rejects (400) — test-side, not site-side.
- Throttle state is per-IP+bucket with 1h window; tests cleared their own
  throttle transients between phases (own test state) to stay deterministic.
