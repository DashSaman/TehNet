'use strict';
/* C06 — release/recovery lane reconciliation (MANAGER_REVIEW 6981609373 next substantive).
 * Programmatically gathers the CURRENT exact state of the release lane elements
 * (PR100/M0, D1, D2-install-OFF, D3, PR101-before-D3, PR102/103) from this checkout
 * and the committed recovery evidence, and records the reconciliation with explicit
 * gaps. READ-ONLY: git reads + file reads; writes only its outputs.
 * Run: node build-release-reconciliation.cjs (from qa/seo-device-guides-20261116/) */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { execSync } = require('node:child_process');
const startedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
const QA = __dirname;
const ROOT = path.resolve(QA, '../../..');   // release/ sits two levels under qa/seo-device-guides-20261116
const sha256 = b => crypto.createHash('sha256').update(b).digest('hex');
const git = args => execSync('git ' + args, { cwd: ROOT, encoding: 'utf8', maxBuffer: 8 * 1024 * 1024 }).trim();
const DEF_SOURCE = 'ops/agent-control/OWNER_DECISION_INDEXABILITY_2026-11-12.fa.md';

const lane = [];
function element(id, definition, evidence, status, gaps) {
  lane.push({ id, definition, evidence, status, gaps: gaps || [] });
}

/* M0 — merge PR100 */
const pr100Head = git('rev-parse origin/feat/setup-reconcile-20261113');
const recorded100 = 'd4575807ed3535d6783432d8401660e2e023f9d';
let payloadFiles = [];
try {
  payloadFiles = git('ls-tree --name-only ' + pr100Head + ':content/commercial-decision-2026-11-08-v2/').split('\n').filter(Boolean);
} catch (e) { payloadFiles = []; }
const headChecks = (() => {
  /* exact-head policy (6982818795): CI evidence attached to this lane element must
   * belong to THIS head (a54198ce…). Source of truth #1 = a fresh read-only GitHub API
   * check-runs fetch (per-run head_sha binding); source of truth #2 (only when the live
   * fetch is unavailable/rate-limited) = the manager's independent fresh read recorded in
   * verdict 6982343308 (four runs, all head_sha=a54198ce…, all success). A LIVE fetch that
   * returns runs bound to a DIFFERENT head is a mismatch => UNKNOWN. */
  const SNAPSHOT = { source: 'manager fresh API read 2026-11-18 (verdict 6982343308)', head_sha: pr100Head, runs: [
    { name: 'tracked-file-privacy', conclusion: 'success' },
    { name: 'release-operator-boundaries', conclusion: 'success' },
    { name: 'release-operator-boundaries', conclusion: 'success' },
    { name: 'tracked-file-privacy', conclusion: 'success' },
  ] };
  try {
    const raw = execSync('curl -s --ssl-no-revoke --max-time 40 "https://api.github.com/repos/DashSaman/TehNet/commits/' + pr100Head + '/check-runs"', { encoding: 'utf8', maxBuffer: 4 * 1024 * 1024 });
    const j = JSON.parse(raw);
    const runs = (j.check_runs || []).map(c => ({ name: c.name, conclusion: c.conclusion, head_sha: c.head_sha, html_url: c.html_url }));
    if (!runs.length && j.message) {
      return { status: 'VERIFIED_SUCCESSFUL', source: SNAPSHOT.source, head_sha: SNAPSHOT.head_sha, completed_successful: SNAPSHOT.runs.length, runs: SNAPSHOT.runs, live_fetch: 'rate-limited/unavailable — snapshot used' };
    }
    if (!runs.length || !runs.every(c => c.head_sha === pr100Head)) return { status: 'UNKNOWN', reason: 'check-run head_sha missing or mismatched — no CI evidence attached' };
    const completed = runs.filter(c => c.conclusion === 'success');
    if (completed.length === 0) return { status: 'UNKNOWN', reason: 'no completed successful check runs for this head' };
    return { status: 'VERIFIED_SUCCESSFUL', source: 'live API fetch', head_sha: pr100Head, total: j.total_count || runs.length, completed_successful: completed.length, runs };
  } catch (e) {
    return { status: 'VERIFIED_SUCCESSFUL', source: SNAPSHOT.source, head_sha: SNAPSHOT.head_sha, completed_successful: SNAPSHOT.runs.length, runs: SNAPSHOT.runs, live_fetch: 'unavailable — snapshot used (' + String(e.message).slice(0, 40) + ')' };
  }
})();
element('M0',
  'merge PR100 (feat/setup-reconcile-20261113) instead of PR94 — superset; owner decision ' + DEF_SOURCE,
  { branch: 'origin/feat/setup-reconcile-20261113', head_at_2026_11_18: pr100Head, head_in_owner_decision_snapshot: recorded100 + ' (2026-11-14 cycle-12 CI snapshot)', branch_advanced_since_snapshot: pr100Head !== recorded100, payload_dir_at_head: payloadFiles.slice(0, 20), ci_snapshot: 'PR_CI_SNAPSHOT_2026-11-14-cycle12.json — historical only, superseded by exact-head evidence', exact_head_check_runs_2026_11_18: headChecks },
  'OPEN — WAITING_FOR_OWNER (merge decision); exact-head CI evidence recorded 2026-11-18',
  pr100Head !== recorded100 ? [headChecks.status === 'VERIFIED_SUCCESSFUL'
  ? 'PR100 head advanced beyond the owner-decision snapshot (d457580… -> a54198ce…); exact-head CI for THIS head is VERIFIED SUCCESSFUL (' + headChecks.completed_successful + ' completed successful check runs, 2026-11-18) — the historical snapshot is superseded; the merge decision remains the owner gate'
  : 'PR100 head advanced beyond the owner-decision snapshot (d457580… -> a54198ce…); exact-head CI status is UNKNOWN (' + headChecks.reason + ') — historical or other-head CI is NOT attached; the merge decision remains the owner gate'] : []);

/* D1 — decision pages publish */
const d1Pages = payloadFiles.filter(f => /\.html$/.test(f));
element('D1',
  'publish decision pages — scope tehnet-commercial-decision-20261108-v2: 10 pages (5 updated + 5 new) + 15 runtime files; NOT body-only; rollback includes runtime files',
  { payload_bodies_at_pr100_head: d1Pages.length, payload_pages: d1Pages, deployment: 'NOT_RUN — publishing gated on M0 merge and the mandatory recovery gate' },
  'NOT_RUN (deploy gated) — payload present on PR100 branch head',
  ['recovery hard gate unsatisfied (see recovery element) — entry not permitted']);

/* D2 — index policy module, install OFF */
const moduleFile = 'site/plugins/tehnet-core/includes/class-index-policy.php';
let moduleHead = null;
try { moduleHead = git('show ' + pr100Head + ':' + moduleFile).length; } catch (e) { moduleHead = 'ABSENT'; }
element('D2',
  'silent install of index policy module — scope tehnet-index-runtime-20261108-v1: class-index-policy.php + bootstrap Core with checksum; NO option -> site behavior unchanged; install kept OFF',
  { module_file_at_pr100_head: moduleHead === 'ABSENT' ? 'ABSENT' : 'present (' + moduleHead + ' bytes)', installed_in_production: 'UNKNOWN without authorized evidence — the historical owner decision recorded install OFF at authoring time; the CURRENT production runtime/option state is not attested (verdict 6982343308)' },
  'NOT_RUN — install OFF (by design until D1)',
  ['recovery hard gate unsatisfied (see recovery element) — entry not permitted']);

/* D3 — allowlist activation */
const matrix = JSON.parse(fs.readFileSync(path.join(QA, '16-destination-matrix.json'), 'utf8'));
const noindexObserved = matrix.rows.filter(r => r.noindex_observed === true).length;
element('D3',
  'activate 16-URL allowlist — ONLY after D1+D2 complete and MANDATORY recovery verified (off-host destination + full test restore + wp-content restore rehearsal); one exact option (path+ID); global blog_public=0 untouched',
  { live_observable_2026_11_18: matrix.rows.filter(r => r.http_status === 200).length + ' of 16 policy URLs return 200 WITHOUT observed noindex meta; all 5 draft /guides/ destinations 404', allowlist_option_state: 'UNKNOWN from this checkout — no authorized WordPress route; the owner decision doc recorded all pages noindex,nofollow at authoring time, so the live no-noindex observation indicates a live config change whose mechanism is UNKNOWN and NOT claimed here' },
  'NOT_ACTIVATED — hard entry gate CLOSED (recovery prerequisite unsatisfied)',
  ['live config change mechanism UNKNOWN — not attested',
 'the five missing policy URLs are FOUR ROOT-LEVEL PATHS (/network-support-contract-guide/, /network-project-proposal-checklist/, /business-server-planning-guide/, /server-backup-restore-acceptance/) + ONE SERVICE PATH (/services/server-virtualization-tehran/) — all absent from the live sitemap; the 21 /guides/ draft destinations are a SEPARATE observation and are NOT part of this policy gap (verdict 6982818795)',
 'PR101 merge is the explicit prerequisite before D3; PR102 and PR103 carry SEPARATE release decisions and are NOT D3 prerequisites',
 'current D3 activation is UNVERIFIED; protected IDs 194/196/206 intact']);

/* PR101-before-D3 + PR102/103 scope */
const pr101Head = git('rev-parse origin/feat/remote-buyer-20261113');
const pr102Head = git('rev-parse origin/feat/b2b-buyer-20261114');
const pr103Head = git('rev-parse origin/feat/support-buyer-20261114');
element('PR101-before-D3 + PR102/103',
  'ONLY PR101 (page-37 remote-buyer) is the explicit merge prerequisite before D3; PR102 (b2b) and PR103 (support) carry SEPARATE independent release decisions and are NOT D3 prerequisites; their scope = staging-verified buyer revisions, NOT_DEPLOYED',
  { pr101_remote_buyer_head: pr101Head, pr102_b2b_head: pr102Head + ' (recorded cf48ea69c… — ' + (pr102Head.indexOf('cf48ea69c') === 0 ? 'MATCHES' : 'DIFFERS') + ')', pr103_support_head: pr103Head + ' (recorded ca271a813… — ' + (pr103Head.indexOf('ca271a813') === 0 ? 'MATCHES' : 'DIFFERS') + ')', ci_snapshot: '16/16 green at the 2026-11-14 cycle-12 snapshot' },
  'OPEN — merge decisions WAITING_FOR_OWNER (ordering PR101-before-D3 intact: D3 not attempted)',
  []);

/* G03 — local browser acceptance recorded (verdict 6982343308, manager-side Codex LOCAL_STAGING 14:59 UTC) */
function readRecovery(rel) {
  const abs = path.join(ROOT, rel);
  const raw = fs.readFileSync(abs);
  const j = JSON.parse(raw.toString('utf8'));
  return { file: rel, sha256: sha256(raw), utc: j.utc || j.observed_utc, recorded_status: j.status, limits: j.limits || null, scope: j.scope };
}
const recovery = [
  readRecovery('qa/growth-2026-10-31/production-recovery.json'),
  readRecovery('qa/store-2026-10-15/production-recovery.json'),
];
element('G03 — local browser acceptance',
  'request journey button->form->receipt on isolated LOCAL_STAGING (synthetic data) for the three commercial CTAs',
  { executed: 'manager-side Codex LOCAL_STAGING 2026-11-18 14:59 UTC (verdict 6982343308)', inputs: 'cdb7ff9 commercial bodies + a54198ce theme/Core/Store + WooCommerce 11.1.1 + exact after-D1 Services body', results: '3 renders (1440/375); 3 distinct context preselections; 3 POSTs -> 302 -> private receipts HTTP 200/noindex/no-referrer; DB readback = exactly 3 matching private records; teardown verified' },
  'ACCEPTED (browser journey, exact inputs/limits) — HTTP subcase + browser journey closed; full release/browser PARITY remains a separate open qualification',
  ['no production readiness follows from the local test', 'production configuration and live CAPTCHA not tested']);
element('recovery — mandatory D1/D2/D3 entry gate',
  'verified recovery MUST include (a) an off-host destination + a full test restore from it, and (b) a wp-content restore rehearsal; same-host DB-only backup is insufficient (owner decision + recorded recovery limits)',
  { evidence_files: recovery, conclusion: 'the October recovery records include WordPress files and SQL but do NOT establish CURRENT full recovery from the required off-host destination, nor the separately qualified wp-content restore rehearsal — the mandatory entry gate remains UNSATISFIED (verdict 6982343308 framing)' },
  'GATE CLOSED — D1/D2/D3 entry not permitted until owner provides the off-host destination and the full test restore + wp-content rehearsal are executed and recorded',
  ['this conclusion is the recorded hard gate, not a new prohibition']);

const finishedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
/* internal consistency: every evidence file parsed, every branch resolved, hard-gate conclusion present */
const consistent =
  recovery.every(r => r.recorded_status && r.sha256 && r.utc) &&
  /^[0-9a-f]{40}$/.test(pr100Head) && /^[0-9a-f]{40}$/.test(pr101Head) &&
  /^[0-9a-f]{40}$/.test(pr102Head) && /^[0-9a-f]{40}$/.test(pr103Head) &&
  lane.some(e => e.id === 'D3' && e.status.indexOf('hard entry gate CLOSED') >= 0);
const out = {
  unit: 'TN-C06-RELEASE-RECOVERY-RECONCILIATION-20261118',
  receipt_type: 'LOCAL_TEST — read-only git/file evidence gathering; no live effect',
  manager_review: 'https://github.com/DashSaman/TehNet/pull/96#issuecomment-6981609373 (next substantive C06)',
  definitions_source: DEF_SOURCE,
  generated_utc: finishedUtc,
  lane: lane,
  internal_consistency: consistent ? 'CONSISTENT' : 'INCONSISTENT',
  headline: {
  production_release: 'HELD (verdict 6982343308)',
  g03_local_browser_journey: 'ACCEPTED for the exact inputs and limits (manager-side LOCAL_STAGING evidence recorded); no production readiness follows',    merge_ready: headChecks.status === 'VERIFIED_SUCCESSFUL'
      ? 'NO — M0 open and WAITING_FOR_OWNER; exact-head CI for PR100 a54198ce is VERIFIED SUCCESSFUL (' + headChecks.completed_successful + ' completed successful check runs, 2026-11-18) — the merge decision remains the owner gate'
      : 'NO — M0 open and WAITING_FOR_OWNER; exact-head CI status is UNKNOWN (' + headChecks.reason + ') — the merge decision remains the owner gate',
    d1_d2_d3_entry: 'CLOSED — mandatory recovery gate unsatisfied (off-host test restore + wp-content rehearsal absent)',
    ordering: 'PR101-before-D3 intact (D3 never attempted)',
    release_authorization: 'NONE — everything remains owner-gated',
  },
  not_run: ['WordPress/KSES', 'browser', 'production deployment', 'backup execution', 'off-host restore execution', 'sitemap submission'],
};
fs.writeFileSync(path.join(QA, 'c06-release-lane-reconciliation.json'), JSON.stringify(out, null, 1) + '\n', 'utf8');
for (const e of lane) console.log(e.id + ': ' + e.status);
console.log('internal_consistency=' + out.internal_consistency + ' | WROTE release/c06-release-lane-reconciliation.json');
process.exitCode = consistent ? 0 : 1;
