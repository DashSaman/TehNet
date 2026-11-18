# Release gates (standing)

1. Explicit owner authorization per release; mission continuation is NOT authorization.
2. Fresh verified backup + restore evidence before production writes.
3. Staging qualification with external HTTP/mail/cron/payment blocked; exact artifact equality.
4. publication_guard + private deny-value scan PASS before every commit/push.
5. Independent live browser acceptance after deploy; rollback exercised or evidenced.
6. Protected state preserved: customer data, 25-item inquiry catalog, payment/ERP limits,
   CAPTCHA, theme/cron/runtime; MyTel production read-only.
7. noindex intentional state may only change through the PR94-scoped release with its
   documented allowlist (max 16 URLs) and four independent release decisions respected.
