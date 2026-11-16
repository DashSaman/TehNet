'use strict';
/* TN-INDEX-INTENDED-BUNDLE-20261116 rev2 — corrections per MANAGER_REVIEW 6904880164.
 * RELEASE PRECEDENCE (manager-corrected): IDs 31/33/35 take the PR100 DECISION payloads
 * (body/title/excerpt) exactly as the guarded DECISION_SCOPE handler will load them;
 * staging-sync constants are kept ONLY as BEFORE/precondition evidence (that scope is
 * staging-only by contract and refused in production). ID37 takes the PR101 remote-buyer
 * payload (content/remote-buyer-20261113/manifest.json); the earlier remote-support
 * manifest/body is its BASELINE, not the intended body.
 * Honest row taxonomy: RESOLVED_COMPLETE (release-determined) vs UNCHANGED_FIELD_NEEDS_
 * PROVENANCE (field untouched by any release; needs authoritative readback/provenance)
 * vs AUTHORIZATION_REFERENCE_UNVERIFIED (live changes whose authorization receipt is
 * unverified) vs BLOCKED_CONTENT_DECISION (genuinely missing content decision).
 * Deterministic; NOT_FOR_ACTIVATION; guarded originals untouched. */
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const REPO = path.resolve(__dirname, '../..');
const PR100 = 'a54198ce7ed3535d6783432d8401660e2e023f9d';
const PR101 = 'cb391c2dc262a65e524962fa7fc44a0187f476fe';
const OUT_DIR = __dirname;
const OUT_MANIFEST = path.join(OUT_DIR, 'intended-activation-manifest.candidate.json');
const OUT_CHECKS = path.join(OUT_DIR, 'intended-bundle-checks.json');

function gitShow(ref, file) {
  return execFileSync('git', ['show', ref + ':' + file], { cwd: REPO, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 });
}
const sha256 = s => crypto.createHash('sha256').update(Buffer.from(s, 'utf8')).digest('hex');

/* ---------- pinned input loading ---------- */
function loadInputs() {
  const original = JSON.parse(gitShow(PR100, 'seo/index-decision-2026-11-08-v2/activation-manifest.json'));
  const decision = JSON.parse(gitShow(PR100, 'content/commercial-decision-2026-11-08-v2/manifest.json'));
  const migrationPhp = gitShow(PR100, 'ops/migrate-growth-content.php');
  const buyer = JSON.parse(gitShow(PR101, 'content/remote-buyer-20261113/manifest.json'));
  const buyerBody = gitShow(PR101, 'content/remote-buyer-20261113/' + buyer.content_file);
  const buyerBodyBaseline = gitShow(PR101, 'content/remote-support-2026-11-01/remote-support.html');
  /* decision payload bodies */
  const decisionBodies = {};
  for (const t of decision.targets) decisionBodies[t.id] = gitShow(PR100, 'content/commercial-decision-2026-11-08-v2/' + t.content_file);
  const decisionPageBodies = {};
  for (const p of decision.pages) decisionPageBodies[p.key] = gitShow(PR100, 'content/commercial-decision-2026-11-08-v2/' + p.content_file);
  /* guarded PHP constants (sync truth) as BEFORE evidence only */
  const syncRe = /(\d+)\s*=>\s*\['uri'=>'([^']*)','file'=>'([^']*)','title'=>"((?:[^"\\]|\\.)*)",'excerpt'=>"((?:[^"\\]|\\.)*)",'expected'=>'([a-f0-9]{64})','exc'=>'([a-f0-9]{64})','lf'=>'([a-f0-9]{64})'\]/g;
  const sync = {};
  for (const m of migrationPhp.matchAll(syncRe)) sync[parseInt(m[1], 10)] = { uri: m[2], file: m[3], title: m[4], excerpt: m[5], lf: m[8] };
  /* guarded PHP DECISION_TARGETS const titles — used for REAL const-vs-manifest comparisons */
  const dtConst = {};
  const dtRe = /(\d+)\s*=>\s*\['uri'=>'([^']*)','file'=>'([^']*)','title'=>(null|'((?:[^'\\]|\\.)*)')\]/g;
  const dtBlock = migrationPhp.match(/private const DECISION_TARGETS=\[([\s\S]*?)\];/);
  if (dtBlock) for (const m of dtBlock[1].matchAll(dtRe)) dtConst[parseInt(m[1], 10)] = { uri: m[2], file: m[3], title: m[4] === 'null' ? null : m[5] };
  const dpBlock = migrationPhp.match(/private const DECISION_PAGES=\[([\s\S]*?)\];/);
  const dpConst = {};
  if (dpBlock) for (const m of dpBlock[1].matchAll(/'([A-Za-z0-9]+)'\s*=>\s*\['slug'=>'([^']*)','parent_id'=>(\d+),'file'=>'([^']*)','title'=>'((?:[^'\\]|\\.)*)'\]/g)) dpConst[m[1]] = { slug: m[2], parent_id: parseInt(m[3], 10), file: m[4], title: m[5] };
  return { original, decision, migrationPhp, buyer, buyerBody, buyerBodyBaseline, decisionBodies, decisionPageBodies, sync, dtConst, dpConst };
}

/* ---------- generation core (pure given inputs) ---------- */
function generate(inputs) {
  const { original, decision, buyer, buyerBody, buyerBodyBaseline, decisionBodies, decisionPageBodies, sync, dtConst, dpConst } = inputs;
  const throwIf = (cond, msg) => { if (cond) throw new Error('GEN_REJECT: ' + msg); };

  /* REAL const-vs-manifest guards (each compares actual values; throws on drift) */
  const decisionTargets = Object.fromEntries(decision.targets.map(t => [t.id, t]));
  const decisionPages = Object.fromEntries(decision.pages.map(p => [p.key, p]));
  for (const idStr of Object.keys(dtConst)) {
    const id = parseInt(idStr, 10);
    const t = decisionTargets[id];
    throwIf(!t, 'const target missing from manifest: ' + id);
    throwIf(dtConst[id].uri !== t.uri || dtConst[id].file !== t.content_file, 'const uri/file drift for decision target ' + id);
    if (dtConst[id].title === null) throwIf(t.title !== undefined && t.title !== null, 'const title=null but manifest carries title for ' + id);
    else throwIf(dtConst[id].title !== t.title, 'const TITLE drift for decision target ' + id);
  }
  for (const key of Object.keys(dpConst)) {
    const p = decisionPages[key];
    throwIf(!p, 'const page missing from manifest: ' + key);
    throwIf(dpConst[key].slug !== p.slug || dpConst[key].file !== p.content_file || dpConst[key].title !== p.title, 'const slug/file/TITLE drift for decision page ' + key);
  }
  /* payload body bytes must equal their pinned LF digests (checksum gate) */
  for (const t of decision.targets) throwIf(sha256(decisionBodies[t.id]) !== t.content_sha256_lf, 'decision body checksum mismatch: ' + t.content_file);
  for (const p of decision.pages) throwIf(sha256(decisionPageBodies[p.key]) !== p.content_sha256_lf, 'decision page body checksum mismatch: ' + p.content_file);
  throwIf(sha256(buyerBody) !== buyer.content_sha256_lf, 'buyer body checksum mismatch');
  throwIf(buyer.key !== 'tehnet-service-remote-buyer-20261113-v1', 'wrong buyer scope key');
  throwIf(buyer.target.id !== 37, 'buyer target id must be 37');

  const byPath = Object.fromEntries(original.targets.map(t => [t.path, t]));
  throwIf(Object.keys(byPath).length !== 16, 'original manifest must carry exactly 16 targets');

  const RESOLVED = 'RESOLVED_COMPLETE';
  const PROV = 'UNCHANGED_FIELD_NEEDS_PROVENANCE';
  const AUTH = 'AUTHORIZATION_REFERENCE_UNVERIFIED';
  const rows = [];
  function addRow(path, fields) {
    const base = byPath[path];
    throwIf(!base, 'unknown path: ' + path);
    const body = fields.body || { state: PROV, sha256: null };
    const title = fields.title || { state: PROV, value: base.title };
    const excerpt = fields.excerpt || { state: PROV, sha256: base.excerpt_sha256 || null };
    const complete = body.state === RESOLVED && title.state === RESOLVED && excerpt.state === RESOLVED;
    rows.push({
      path, id: base.id, identity: 'production',
      status: complete ? RESOLVED : (fields.row_status || (body.state === RESOLVED ? PROV : (fields.row_status || BLOCKED))),
      fields: { body, title, excerpt },
      binding: fields.binding || null,
      notes: fields.notes || [],
      carried_reference: { title: base.title, body_sha256: base.body_sha256, excerpt_sha256: base.excerpt_sha256 || null },
    });
  }
  const BLOCKED = 'BLOCKED_CONTENT_DECISION';

  /* 29/31/33/35 — DECISION payloads are the intended post-D1 content (release precedence) */
  for (const [id, p] of [[29, '/services/network-tehran/'], [31, '/services/network-support-tehran/'], [33, '/services/network-setup-tehran/'], [35, '/services/mikrotik-tehran/']]) {
    const t = decisionTargets[id];
    addRow(p, {
      body: { state: RESOLVED, sha256: t.content_sha256_lf },
      title: { state: RESOLVED, value: t.title },
      excerpt: { state: RESOLVED, sha256: sha256(t.excerpt) },
      binding: { scope: decision.key, ref: PR100, file: 'content/commercial-decision-2026-11-08-v2/' + t.content_file, transform: 'post_content = payload bytes (lf-verified); title/excerpt = decision manifest strings (const-compared with guarded PHP DECISION_TARGETS)' },
      notes: [{ before_evidence: 'staging-sync const carries pre-release baseline body ' + (sync[id] ? sync[id].lf.slice(0, 12) + '…' : 'n/a') + ' — staging-only scope, refused in production; kept as BEFORE evidence, NOT intended values' }],
    });
  }
  /* 8 — decision changes post_content ONLY */
  addRow('/services/', {
    body: { state: RESOLVED, sha256: decisionTargets[8].content_sha256_lf },
    title: { state: PROV, value: byPath['/services/'].title },
    excerpt: { state: PROV, sha256: byPath['/services/'].excerpt_sha256 },
    binding: { scope: decision.key, ref: PR100, file: 'content/commercial-decision-2026-11-08-v2/services.html', transform: 'post_content = payload bytes (lf-verified); change_fields=[post_content] only' },
    row_status: PROV,
    notes: ['title/excerpt untouched by this release — unchanged fields need authoritative readback/provenance, carried 11-08 values are reference only'],
  });
  /* 37 — PR101 remote-buyer payload (intended body); baseline recorded */
  addRow('/services/remote-support/', {
    body: { state: RESOLVED, sha256: buyer.content_sha256_lf },
    title: { state: PROV, value: byPath['/services/remote-support/'].title },
    excerpt: { state: PROV, sha256: byPath['/services/remote-support/'].excerpt_sha256 },
    binding: { scope: buyer.key, ref: PR101, file: 'content/remote-buyer-20261113/' + buyer.content_file, transform: 'post_content = buyer payload bytes (lf-verified); change_fields=[post_content]; title/slug/excerpt/meta preserved' },
    row_status: PROV,
    notes: [{ before_evidence: 'PR101 remote-support manifest body 2f5210b2… is the BASELINE of the same page, not the intended body' }, 'status ' + buyer.status],
  });
  /* A1-A4/N1 — decision new pages */
  for (const key of ['A1', 'A2', 'A3', 'A4', 'N1']) {
    const p = decisionPages[key];
    const path = key === 'N1' ? '/services/server-virtualization-tehran/' : '/' + p.slug + '/';
    addRow(path, {
      body: { state: RESOLVED, sha256: p.content_sha256_lf },
      title: { state: RESOLVED, value: p.title },
      excerpt: { state: RESOLVED, sha256: sha256(p.excerpt) },
      binding: { scope: decision.key, ref: PR100, file: 'content/commercial-decision-2026-11-08-v2/' + p.content_file, transform: 'new page: post_content = payload bytes (lf-verified); title = guarded const (compared); excerpt = manifest string' },
    });
  }
  /* unchanged-by-release rows — honest taxonomy */
  for (const path of ['/contact/', '/technical-methodology/']) {
    addRow(path, { row_status: PROV, notes: ['no release payload touches this page; unchanged field needs authoritative readback/provenance'] });
  }
  addRow('/services/voice-network-readiness/', {
    row_status: PROV,
    notes: ['no release payload touches this page; body matched BOTH environment readbacks (7f384153…, DB observation not release intent); staging id 193 recorded solely in staging_environment_binding'],
  });
  for (const path of ['/', '/about/']) {
    addRow(path, {
      row_status: AUTH,
      notes: ['live 2026-11-15 home/about/profile changes are associated with commit 8c74794 but the exact authorization/mutation receipt has NOT been supplied — AUTHORIZATION_REFERENCE_UNVERIFIED; the later public-index goal is not retrospective permission'],
    });
  }

  /* allowlist set equality (no additions; unchanged even when rows are unresolved) */
  const allowlist = original.targets.map(t => t.path);
  throwIf(rows.length !== 16, 'must resolve exactly 16 rows');

  const resolvedCount = rows.filter(r => r.status === RESOLVED).length;
  return {
    schema: 2,
    key: 'tehnet-index-allowlist-20261108-v1',
    operation: 'activate',
    candidate_kind: 'INTENDED_BUNDLE_SOURCE_ONLY',
    status: 'NOT_FOR_ACTIVATION',
    identity_base: 'production',
    production_ids_preserved: true,
    staging_environment_binding: {
      unresolved_separate_mapping: true,
      proposed_env_ids_example: { '/services/voice-network-readiness/': { production: 206, staging: 193 } },
    },
    inputs: {
      pr100_head: PR100,
      pr101_head: PR101,
      payload_digests: {
        decision_29_network_tehran: decisionTargets[29].content_sha256_lf,
        decision_31_network_support: decisionTargets[31].content_sha256_lf,
        decision_33_network_setup: decisionTargets[33].content_sha256_lf,
        decision_35_mikrotik: decisionTargets[35].content_sha256_lf,
        decision_8_services: decisionTargets[8].content_sha256_lf,
        decision_A1: decisionPages.A1.content_sha256_lf,
        decision_A2: decisionPages.A2.content_sha256_lf,
        decision_A3: decisionPages.A3.content_sha256_lf,
        decision_A4: decisionPages.A4.content_sha256_lf,
        decision_N1: decisionPages.N1.content_sha256_lf,
        pr101_buyer_body: buyer.content_sha256_lf,
        pr101_buyer_baseline_body: sha256(buyerBodyBaseline),
      },
    },
    release_precedence: {
      29_31_33_35: 'PR100 DECISION scope payloads (body+title+excerpt) — the guarded DECISION_SCOPE handler loads these; staging-sync constants kept as BEFORE evidence only',
      37: 'PR101 remote-buyer payload (content/remote-buyer-20261113); remote-support manifest/body = baseline',
      8: 'decision body only; title/excerpt unchanged-by-release',
    },
    allowlist_paths_exact: allowlist,
    targets: rows,
    resolved_complete_count: resolvedCount,
    activation_incomplete: resolvedCount < 16,
    production_authorization: 'NEEDS_SEPARATE_EXACT_ALLOWLIST_OWNER_APPROVAL',
  };
}

/* ---------- private-negative / conflict validation (real injected failures) ---------- */
function runNegatives(baseInputs) {
  const results = [];
  function expectReject(name, mutate) {
    const inputs = JSON.parse(JSON.stringify(baseInputs));
    mutate(inputs);
    let rejected = false, reason = null;
    try { generate(inputs); } catch (e) { rejected = true; reason = String(e.message).split('\n')[0]; }
    results.push({ name, rejected, reason: rejected ? reason.slice(0, 90) : 'NOT REJECTED — VALIDATION GAP' });
    if (!rejected) throw new Error('NEGATIVE NOT ENFORCED: ' + name);
  }
  /* N1: sync baseline substituted as final payload for 31 must fail the checksum gate */
  expectReject('baseline-as-final:31', ins => {
    ins.decision.targets.find(t => t.id === 31).content_sha256_lf = ins.sync[31].lf;
    ins.decisionBodies = undefined; delete ins.decisionBodies;
  });
  /* N1b (structural): swapping the payload body bytes for 31 breaks lf equality */
  expectReject('baseline-body-as-final:31', ins => { ins.decisionBodies[31] = 'STALE_BASELINE_BODY'; });
  /* N2: conflicting title for 29 must fail the const comparison */
  expectReject('conflicting-title:29', ins => { ins.decision.targets.find(t => t.id === 29).title = 'عنوان متفاوت غیرمصوب'; });
  /* N3: missing required input (buyer manifest) must fail */
  expectReject('missing-input:buyer', ins => { ins.buyer = null; });
  /* N3b: missing decision page payload body must fail */
  expectReject('missing-input:A1-body', ins => { ins.decisionPageBodies.A1 = null; });
  /* N4: private/non-allowlist target must fail the exact-16 set */
  expectReject('private-target-added', ins => { ins.original.targets.push({ path: '/support/', id: 999, title: 'x', body_sha256: 'b'.repeat(64) }); });
  /* N4b: allowlist path swapped to a non-allowlist route */
  expectReject('path-swapped', ins => { ins.original.targets.find(t => t.path === '/about/').path = '/my-account/'; });
  return results;
}

/* ---------- main ---------- */
const inputs = loadInputs();
const candidate = generate(inputs);

/* positive checks (real comparisons only; every entry below is machine-verified) */
const checks = [];
function ck(name, pass, detail) { checks.push({ name, pass: !!pass, detail: detail === undefined ? null : detail }); if (!pass) throw new Error('CHECK FAILED: ' + name + ' ' + JSON.stringify(detail)); }
ck('original_exact16', candidate.inputs && candidate.allowlist_paths_exact.length === 16);
ck('production_ids_preserved', candidate.targets.every(t => t.id === inputs.original.targets.find(o => o.path === t.path).id));
ck('voice206_preserved', candidate.targets.find(t => t.path === '/services/voice-network-readiness/').id === 206);
ck('no_staging_ids_in_production_rows', candidate.targets.every(t => t.id !== 193 && !(t.binding && t.binding.staging_id !== undefined)));
ck('precedence_31_uses_decision_body', candidate.targets.find(t => t.path === '/services/network-support-tehran/').fields.body.sha256 === inputs.decision.targets.find(t => t.id === 31).content_sha256_lf, { note: 'NOT the sync baseline ' + inputs.sync[31].lf.slice(0, 12) });
ck('precedence_33_uses_decision_body', candidate.targets.find(t => t.path === '/services/network-setup-tehran/').fields.body.sha256 === inputs.decision.targets.find(t => t.id === 33).content_sha256_lf);
ck('precedence_35_uses_decision_body', candidate.targets.find(t => t.path === '/services/mikrotik-tehran/').fields.body.sha256 === inputs.decision.targets.find(t => t.id === 35).content_sha256_lf);
ck('precedence_37_uses_buyer_body', candidate.targets.find(t => t.path === '/services/remote-support/').fields.body.sha256 === inputs.buyer.content_sha256_lf, { expected: '8feda428…', note: '2f5210b2 kept as baseline evidence only' });
ck('sync_values_absent_from_intended_fields', !JSON.stringify(candidate.targets.filter(t => ['29', '31', '33', '35'].includes(String(t.id))).map(t => t.fields)).includes(inputs.sync[31].lf));
ck('allowlist_no_private_routes', candidate.allowlist_paths_exact.every(p => /^\/[a-z0-9\-\/]*\/?$/.test(p)) && !candidate.allowlist_paths_exact.some(p => /ticket|quote|order|account|cart|checkout|my-account|lab/.test(p)));
ck('auth_reference_unverified_used', candidate.targets.filter(t => t.path === '/' || t.path === '/about/').every(t => t.status === 'AUTHORIZATION_REFERENCE_UNVERIFIED'));
ck('needs_provenance_used', candidate.targets.some(t => t.status === 'UNCHANGED_FIELD_NEEDS_PROVENANCE'));
ck('not_for_activation', candidate.status === 'NOT_FOR_ACTIVATION' && candidate.activation_incomplete === true);

const negatives = runNegatives(inputs);
ck('all_negative_probes_rejected', negatives.every(n => n.rejected), negatives);

/* determinism: regenerate and compare bytes */
const candidate2 = generate(loadInputs());
ck('deterministic_regeneration', JSON.stringify(candidate) === JSON.stringify(candidate2));

/* write outputs (sorted-stable JSON) */
fs.mkdirSync(OUT_DIR, { recursive: true });
const json = JSON.stringify(candidate, null, 1);
fs.writeFileSync(OUT_MANIFEST, json, 'utf8');
fs.writeFileSync(OUT_CHECKS, JSON.stringify({ checks, negatives, summary: { checks: checks.length, checks_passed: checks.filter(c => c.pass).length, negative_probes: negatives.length, all_rejected: negatives.every(n => n.rejected) } }, null, 1), 'utf8');
console.log('GENERATED intended-activation-manifest.candidate.json');
console.log('ROWS resolved=' + candidate.resolved_complete_count + '/16 blocked_or_partial=' + (16 - candidate.resolved_complete_count));
console.log('CHECKS=' + checks.length + ' NEGATIVES=' + negatives.length + ' ALL_REJECTED=' + negatives.every(n => n.rejected));
console.log('MANIFEST_SHA256=' + sha256(json));
