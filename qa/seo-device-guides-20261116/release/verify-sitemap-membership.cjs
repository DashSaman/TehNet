'use strict';
/* TN-G04-SITEMAP-MEMBERSHIP-CHECK-20261118 — executable local cross-check binding the
 * 16 policy rows to the ACTUAL wp-sitemap XML loc values. READ-ONLY: fetches the live
 * wp-sitemap.xml and its child files, parses the loc set, and asserts
 *   1. per-row: recorded live_sitemap_membership == XML truth (normalized full URL);
 *   2. draft candidates ⊆ (live 200 ∧ sitemap member) and none of the 404 rows
 *      appears in the draft candidate list;
 *   3. summary counts agree (11 live / 5 dead / total loc entries as recorded).
 * Writes only its own receipt. Run: node verify-sitemap-membership.cjs (from qa/seo-device-guides-20261116/) */
const fs = require('node:fs');
const path = require('node:path');
const https = require('node:https');
const startedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
const QA = __dirname;
const matrix = JSON.parse(fs.readFileSync(path.join(QA, '16-destination-matrix.json'), 'utf8'));

function get(url) {
  return new Promise(resolve => {
    const req = https.get(url, { timeout: 20000, headers: { 'User-Agent': 'TehNetReleaseReadinessCheck/1.0 (read-only status check)' } }, res => {
      let sz = 0; const ch = [];
      res.on('data', c => { sz += c.length; if (sz > 800000) req.destroy(); ch.push(c); });
      res.on('end', () => resolve({ status: res.statusCode, text: Buffer.concat(ch).toString('utf8') }));
      res.on('error', e => resolve({ status: 0, text: '', error: String(e).slice(0, 60) }));
    });
    req.on('timeout', () => { req.destroy(); resolve({ status: 0, text: '', error: 'timeout' }); });
    req.on('error', e => resolve({ status: 0, text: '', error: String(e).slice(0, 60) }));
  });
}

(async () => {
  const checks = [];
  let failures = 0;
  const idx = await get('https://tehnet.ir/wp-sitemap.xml');
  checks.push({ check: 'wp_sitemap_reachable', pass: idx.status === 200, detail: 'status=' + idx.status });
  if (idx.status !== 200) { failures++; }
  const children = (idx.text.match(/<loc>([^<]+)<\/loc>/g) || []).map(x => x.replace(/<\/?loc>/g, '')).filter(u => /sitemap/i.test(u));
  const locs = new Set();
  const perChild = [];
  for (const c of children) {
    const r = await get(c);
    const urls = (r.text.match(/<loc>([^<]+)<\/loc>/g) || []).map(x => x.replace(/<\/?loc>/g, '')).filter(u => !/\.xml/i.test(u));
    urls.forEach(u => locs.add(u));
    perChild.push({ url: c, url_count: urls.length });
  }
  checks.push({ check: 'sitemap_child_files_parsed', pass: children.length > 0, detail: children.length + ' children, ' + locs.size + ' total loc entries' });
  checks.push({ check: 'total_loc_entries_matches_matrix_record', pass: locs.size === matrix.sitemap_observed.total_loc_entries, detail: 'xml=' + locs.size + ' matrix=' + matrix.sitemap_observed.total_loc_entries });
  if (locs.size !== matrix.sitemap_observed.total_loc_entries) failures++;

  /* membership truth per row */
  for (const row of matrix.rows) {
    const truth = locs.has(row.full_url) || locs.has(row.full_url + '/');
    const ok = truth === row.live_sitemap_membership;
    checks.push({ check: 'membership_row:' + row.path, pass: ok, detail: 'xml_truth=' + truth + ' recorded=' + row.live_sitemap_membership });
    if (!ok) failures++;
  }
  /* draft candidate list containment */
  const liveMemberPaths = new Set(matrix.rows.filter(r => r.http_status === 200 && r.live_sitemap_membership === true).map(r => r.full_url));
  const cands = matrix.draft_review_scope.candidate_urls;
  const candsAllLiveMembers = cands.every(u => liveMemberPaths.has(u));
  checks.push({ check: 'draft_candidates_subset_of_live_members', pass: candsAllLiveMembers, detail: cands.length + ' candidates, all live+member=' + candsAllLiveMembers });
  if (!candsAllLiveMembers) failures++;
  const deadPaths = new Set(matrix.rows.filter(r => r.http_status === 404).map(r => r.full_url));
  const noDeadInCandidates = cands.every(u => !deadPaths.has(u));
  checks.push({ check: 'draft_candidates_exclude_dead_rows', pass: noDeadInCandidates, detail: '5 dead rows excluded from candidates=' + noDeadInCandidates });
  if (!noDeadInCandidates) failures++;
  /* summary agreement */
  const live = matrix.rows.filter(r => r.http_status === 200).length;
  const dead = matrix.rows.filter(r => r.http_status === 404).length;
  const summaryOk = matrix.membership_summary.live_and_in_sitemap === 11 && matrix.membership_summary.dead_and_absent === 5 && live === 11 && dead === 5 && matrix.rows.length === 16;
  checks.push({ check: 'policy16_summary_agreement', pass: summaryOk, detail: 'live=' + live + ' dead=' + dead + ' rows=' + matrix.rows.length + ' (16-URL contract preserved)' });
  if (!summaryOk) failures++;

  const ok = failures === 0;
  const finishedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  const receipt = {
    packet: 'TN-G04-SITEMAP-MEMBERSHIP-CHECK-20261118',
    command: 'node verify-sitemap-membership.cjs',
    cwd: 'qa/seo-device-guides-20261116/',
    started_utc: startedUtc, finished_utc: finishedUtc,
    exit: ok ? 0 : 1,
    failures,
    checks,
    mode: 'LOCAL_TEST — read-only public GETs + XML loc parsing; writes only this receipt; no sitemap mutation/submission',
    not_run: ['WordPress apply', 'production deployment', 'browser rendering', 'sitemap submission'],
  };
  fs.writeFileSync(path.join(QA, 'sitemap-membership-check-receipt.json'), JSON.stringify(receipt, null, 1));
  for (const c of checks) console.log((c.pass ? 'OK  ' : 'FAIL') + ' ' + c.check + (c.pass ? '' : ' — ' + c.detail));
  console.log('SITEMAP-CHECK=' + (ok ? 'PASS' : 'FAIL') + ' failures=' + failures + ' | exit=' + receipt.exit);
  process.exitCode = ok ? 0 : 1;
})();
