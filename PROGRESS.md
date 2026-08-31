# TehNet Verified Progress

**Last update:** 2026-08-31

## Summary

| Area | State | Evidence |
|---|---|---|
| Business model | APPROVED | approved decisions in `docs/product/DECISIONS.md` |
| Architecture/spec | APPROVED/ACTIVE | `docs/superpowers/specs/2026-08-31-tehnet-platform-design.md` |
| Implementation plan | ACTIVE | `docs/superpowers/plans/2026-08-31-tehnet-mvp-foundation.md` |
| Canonical repository | ACTIVE | `DashSaman/TehNet` |
| Working branch | ACTIVE | `tehnet-bootstrap`; Draft PR #1 used as CI/review checkpoint |
| Theme | BOOTSTRAPPED + CI PASS | custom `tehnet` RTL dark/light theme, four homepage journeys |
| Core content model | BOOTSTRAPPED + CI PASS | `tn_lab`, `tn_service`, topic taxonomy and relationship metadata |
| Shop inquiry mode | IMPLEMENTED + CI PASS | direct/inquiry product meta, admin field, purchasability filter and inquiry CTA |
| TehNet Pro domain rules | IMPLEMENTED + CI PASS | pure tests cover 30-day grant/renewal/expiry behavior |
| TehNet Pro Woo integration | IMPLEMENTED + CI PASS | designated Pro product, `woocommerce_payment_complete`, duplicate-order guard, account status |
| Runtime installer | WRITTEN + CI PASS | missing-secret contract and shell syntax pass; production execution pending |
| Component ownership | REVIEWED | `ops/PLUGIN_MATRIX.md` |
| Production runtime | BLOCKED | target SentinelX host connected but inactive under Free active-host limit |
| DNS | PARTIAL | apex configured by owner; `www` still requires live record/redirect validation |
| SEO query map | NOT YET VERIFIED | live Persian SERP research/URL map pending |
| YouTube migration | NOT STARTED | channel inventory/brand extraction pending |
| Launch | NO-GO | production and full critical journeys not deployed/verified |

## TDD / CI evidence

### Baseline bootstrap

GitHub Actions passed theme PHP syntax, plugin PHP syntax, theme smoke, core smoke and installer missing-secret/syntax contract.

### Sale mode / Pro domain cycle

1. Test commit added `site/tests/domain-test.php` before implementation.
2. GitHub Actions failed specifically at `Domain behavior` while all preceding tests passed.
3. `src/domain.php` was implemented.
4. GitHub Actions then passed `Domain behavior` and all other checks.

### WooCommerce integration cycle

1. Test commit added `site/tests/integration-contract-test.php` before integration code.
2. GitHub Actions failed specifically at `WordPress integration contract`.
3. Product inquiry admin/frontend hooks and `pro-membership.php` were implemented.
4. GitHub Actions run for commit `f53e0dd44097d9df9227757ab661ced000578dfc` completed successfully across all steps.

## Product decisions already locked

- Four equal journeys: Learn / Lab / Services / Shop.
- Content priority: MikroTik/VPN → Linux/Server → Cisco → VoIP → applied AI.
- Revenue: individual sales + monthly Pro.
- Labs: free + paid + Pro-only.
- Services: priced package + quote + hourly consulting.
- Shop: direct stock + inquiry inventory.
- Login: email/password + Google.
- Support: tickets + Telegram/WhatsApp + form/email.
- Payment: Iranian provider first; provider not yet supplied.

## External blockers / required real inputs

1. Production host must be active through the authorized server-control route before Task 1 inventory/deployment.
2. Actual Iranian payment provider/account.
3. Google OAuth credentials.
4. Supplier product catalog, stock and pricing feed/process.
5. Paid-video provider/hosting decision.
6. Sender email/SMTP provider.

## Next execution order

1. Build SEO Business Search Brief + live SERP/Query→URL map.
2. Review Tehran Network YouTube channel inventory and brand cues.
3. Expand theme from homepage skeleton to hub/archive/single relationship templates.
4. Add real service/inquiry request data flow and validation.
5. When server access becomes active: baseline → backup → install runtime → deploy components → live validation.

## Release state

`RELEASE=NO-GO`

This is correct until production deployment and launch gates pass.
