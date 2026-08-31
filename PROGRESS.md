# TehNet Verified Progress

**Last update:** 2026-08-31

## Summary

| Area | State | Evidence |
|---|---|---|
| Business model | APPROVED | 20-question design session captured in `docs/product/DECISIONS.md` |
| Architecture/spec | IN PROGRESS | `docs/superpowers/specs/2026-08-31-tehnet-platform-design.md` |
| Implementation plan | IN PROGRESS | `docs/superpowers/plans/2026-08-31-tehnet-mvp-foundation.md` |
| Repository | ACTIVE | `DashSaman/TehNet`, branch `tehnet-bootstrap` |
| Theme | BOOTSTRAPPED | custom `tehnet` theme files + smoke test |
| Core plugin | BOOTSTRAPPED | custom `tehnet-core` plugin files + smoke test |
| Production runtime | BLOCKED | target SentinelX host connected but inactive under Free active-host limit |
| DNS | PARTIAL | apex configured; `www` record still needs confirmation/configuration |
| SEO query map | NOT YET VERIFIED | live Iran-specific SERP provider limitation noted; web SERP research still required |
| Content migration | NOT STARTED | YouTube inventory review pending |
| Launch | NO-GO | production not yet deployed/validated |

## Completed decisions

- Four equal homepage journeys: Learn / Lab / Services / Shop.
- Primary audiences: professionals, companies, beginners, equipment buyers.
- Initial content order: MikroTik/VPN → Linux/Server → Cisco → VoIP → practical AI for Network/IT.
- Dark/light UI with visual continuity from Tehran Network YouTube identity.
- Course price strategy initially focused on accessible + specialist tiers, roughly 300k–3m toman.
- TehNet Pro: monthly access model.
- Labs: free + paid + Pro-only.
- Services: priced packages + custom quote + hourly consulting.
- Service area: remote across Iran; on-site Tehran and nearby cities by arrangement.
- Shop: direct stock + inquiry inventory.
- Authentication: email/password + Google.
- Payment: Iranian gateway first, future-provider-ready architecture.
- Support: account tickets + Telegram/WhatsApp + form/email; live chat deferred.
- Paid files: expiry/limited delivery; paid videos in-site without ordinary download link.
- YouTube archive: review and refresh, not blind import.

## Blockers requiring external data/access

1. Activate target host in SentinelX or provide another authorized execution route.
2. Real Iranian payment gateway/provider credentials are not yet available.
3. Google OAuth client credentials are not yet available.
4. Real equipment catalog/stock/price source from supplier is not yet available.
5. Paid-video hosting/signing provider is not yet selected.

## Release state

`RELEASE=NO-GO`

Reason: production runtime and critical user journeys have not been deployed and verified.
