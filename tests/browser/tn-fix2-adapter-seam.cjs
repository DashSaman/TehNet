'use strict';
/* TN-P2-DRIVER-REMAINING-ACCEPTANCE-20261118 — EXPLICIT adapter seam (MANAGER_REVIEW 6969817290 #1).
 * DEFAULT STATE: DISABLED. The withdrawn legacy SSH/container route is NOT implicitly attempted:
 * a complete contract + valid digests do NOT qualify any adapter by themselves, and no
 * contract-supplied boolean can. The ONLY way an adapter becomes reachable is an explicitly
 * injected QUALIFIED adapter module at this exact path (pure tests inject a synthetic eligible
 * adapter through this seam; a real route would require a separately reviewed+qualified adapter
 * module AND the still-separate synthetic-environment/access gates). Nothing here probes,
 * reconnects or qualifies any old fixture. */
module.exports = {
  qualified: false,
  reason: 'no_qualified_adapter_configured_default_withdrawn_route',
};
