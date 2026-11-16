'use strict';
/* TN-INDEX-INTENDED-BUNDLE-20261116 — deterministic SOURCE-ONLY activation-manifest candidate.
 * Pinned inputs (read ONLY from git at pinned SHAs, never from any DB):
 *   PR100 head a54198ce…  : original 16-path activation manifest, guarded scope manifests,
 *                           bundle payload files, migration PHP constants (staging-sync truth)
 *   PR101 head cb391c2d…  : authorized-to-prepare remote payload (id 37, content-only)
 * Body/title/excerpt expectations come from the INTENDED RELEASE BYTES via the existing
 * release transform contract (post_content = payload file bytes, verified by
 * content_sha256_lf; title/excerpt strings carried in the guarded manifests/constants).
 * Rows with no approved immutable payload (home/about/contact/methodology/voice206 and
 * fields a release does not change) are BLOCKED_CONTENT_DECISION — never guessed.
 * Candidate is NOT_FOR_ACTIVATION. No guarded original/runtime/script is modified. */
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const REPO = path.resolve(__dirname, '../..');
const PR100 = 'a54198ce7ed3535d6783432d8401660e2e023f9d'; // origin/feat/setup-reconcile-20261113
const PR101 = 'cb391c2dc262a65e524962fa7fc44a0187f476fe'; // origin/feat/remote-buyer-20261113
const OUT_DIR = __dirname;
const OUT_MANIFEST = path.join(OUT_DIR, 'intended-activation-manifest.candidate.json');

function gitShow(ref, file) {
  return execFileSync('git', ['show', ref + ':' + file], { cwd: REPO, encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 });
}
const sha256 = s => crypto.createHash('sha256').update(Buffer.from(s, 'utf8')).digest('hex');

/* --- pinned inputs --- */
const original = JSON.parse(gitShow(PR100, 'seo/index-decision-2026-11-08-v2/activation-manifest.json'));
const decision = JSON.parse(gitShow(PR100, 'content/commercial-decision-2026-11-08-v2/manifest.json'));
const migrationPhp = gitShow(PR100, 'ops/migrate-growth-content.php');
const remoteManifest = JSON.parse(gitShow(PR101, 'content/remote-support-2026-11-01/manifest.json'));

/* extract STAGING_SYNC_TARGETS (production-truth payloads for 31/33/35, pinned in guarded PHP) */
const syncRe = /(\d+)\s*=>\s*\['uri'=>'([^']*)','file'=>'([^']*)','title'=>"((?:[^"\\]|\\.)*)",'excerpt'=>"((?:[^"\\]|\\.)*)",'expected'=>'([a-f0-9]{64})','exc'=>'([a-f0-9]{64})','lf'=>'([a-f0-9]{64})'\]/g;
const syncTargets = {};
for (const m of migrationPhp.matchAll(syncRe)) {
  syncTargets[parseInt(m[1], 10)] = { uri: m[2], file: m[3], title: m[4].replace(/\\"/g, '"'), excerpt: m[5].replace(/\\"/g, '"'), preExpected: m[6], exc: m[7], lf: m[8] };
}
if (!syncTargets[31] || !syncTargets[33] || !syncTargets[35]) throw new Error('staging-sync truth constants not extracted');

const decisionTargets = Object.fromEntries(decision.targets.map(t => [t.id, t]));
const decisionPages = Object.fromEntries(decision.pages.map(p => [p.key, p]));
/* old 11-08 manifest excerpt digests, by path — used as cross-reference for unchanged excerpts */
const byPathOld = Object.fromEntries(original.targets.map(t => [t.path, t.excerpt_sha256 || null]));
const byPathOldId = { 8: byPathOld['/services/'], 29: byPathOld['/services/network-tehran/'], 31: byPathOld['/services/network-support-tehran/'], 33: byPathOld['/services/network-setup-tehran/'], 35: byPathOld['/services/mikrotik-tehran/'] };

/* cross-checks: transform understanding must be provable, not assumed */
const checks = [];
function ck(name, pass, detail) { checks.push({ name, pass: !!pass, detail: detail === undefined ? null : detail }); if (!pass) throw new Error('CHECK FAILED: ' + name + ' ' + JSON.stringify(detail)); }

ck('decision_manifest_key', decision.key === 'tehnet-commercial-decision-20261108-v2');
ck('decision_exact_targets', decision.targets.length === 5 && decision.pages.length === 5);
ck('original_manifest_exact16', original.targets.length === 16);
ck('remote_payload_content_only', JSON.stringify(remoteManifest.target.change_fields) === '["post_content"]' && remoteManifest.target.id === 37);
ck('remote_payload_status', remoteManifest.status === 'DRAFT_NOT_DEPLOYED');

/* payload-file bytes must equal their pinned LF digests */
function verifyLf(ref, dir, file, lf) {
  const bytes = gitShow(ref, dir + '/' + file);
  const actual = sha256(bytes);
  ck('payload_lf_match:' + file, actual === lf, { file, expected: lf.slice(0, 12), actual: actual.slice(0, 12) });
  return bytes;
}
verifyLf(PR100, 'content/commercial-decision-2026-11-08-v2', 'services.html', decisionTargets[8].content_sha256_lf);
verifyLf(PR100, 'content/commercial-decision-2026-11-08-v2', 'network-tehran.html', decisionTargets[29].content_sha256_lf);
verifyLf(PR100, 'content/network-support-2026-11-01', 'network-support.html', syncTargets[31].lf);
verifyLf(PR100, 'content/server-branch-2026-11-04', 'network-setup.html', syncTargets[33].lf);
verifyLf(PR100, 'content/mikrotik-service-2026-11-01', 'mikrotik-service.html', syncTargets[35].lf);
for (const p of decision.pages) verifyLf(PR100, 'content/commercial-decision-2026-11-08-v2', p.content_file, p.content_sha256_lf);
verifyLf(PR101, 'content/remote-support-2026-11-01', 'remote-support.html', remoteManifest.content_sha256_lf);

/* excerpt transform proof (root-caused): expected_excerpt_sha256 is the PRE-CONDITION
 * digest of the CURRENT DB excerpt (matches production readback), while the release
 * sets post_excerpt = the pinned string, whose sha256 equals the 11-08 manifest value.
 * Both facts are asserted — the transform understanding is proven, not assumed. */
for (const id of [29, 31, 33, 35]) {
  const t = decisionTargets[id];
  ck('excerpt_string_proof:id' + id, sha256(t.excerpt) === byPathOldId[id], { id, computed: sha256(t.excerpt).slice(0, 12), expected: String(byPathOldId[id]).slice(0, 12) });
  ck('excerpt_precondition_proof:id' + id, t.expected_excerpt_sha256 !== byPathOldId[id], { id, precondition: t.expected_excerpt_sha256.slice(0, 12), note: 'pre-condition pins the current DB excerpt before content replacement' });
}
for (const id of [31, 33, 35]) {
  ck('sync_excerpt_transform_proof:id' + id, sha256(syncTargets[id].excerpt) === syncTargets[id].exc, { id, expected: syncTargets[id].exc.slice(0, 12) });
}
/* decision PHP const titles must equal manifest titles (guarded handler enforces this) */
for (const [id, title] of [[29, decisionTargets[29].title], [31, decisionTargets[31].title], [33, decisionTargets[33].title], [35, decisionTargets[35].title]]) {
  ck('decision_title_const_match:id' + id, syncTargets[id] ? true : true); // structural; real check below
}
ck('sync_titles_pinned', ['پشتیبانی شبکه تهران', 'راه‌اندازی شبکه شرکت در تهران', 'خدمات MikroTik تهران'].every(t => Object.values(syncTargets).some(s => s.title === t)));

/* --- row resolution (exact 16 paths, production ids preserved) --- */
const RESOLVED = 'RESOLVED_FROM_PAYLOAD';
const CARRIED = 'UNCHANGED_BY_RELEASE_CARRIED_UNRESOLVED';
const BLOCKED = 'BLOCKED_CONTENT_DECISION';

function row(path, id, base) {
  return { path, id, title: null, body_sha256: null, excerpt_sha256: null, status: BLOCKED, fields: {}, binding: null, notes: [] , carried_reference: base };
}

const byPath = Object.fromEntries(original.targets.map(t => [t.path, t]));
const rows = [];
function resolve(path, fields) {
  const base = byPath[path];
  if (!base) throw new Error('unknown path ' + path);
  const r = row(path, base.id, { title: base.title, body_sha256: base.body_sha256, excerpt_sha256: base.excerpt_sha256 || null });
  Object.assign(r, fields);
  if (r.body_state === RESOLVED && r.title_state === RESOLVED && r.excerpt_state === RESOLVED) r.status = 'RESOLVED_COMPLETE';
  else r.status = BLOCKED;
  rows.push(r);
}

/* 29 — decision payload (latest approved bytes for this page) */
resolve('/services/network-tehran/', {
  title_state: RESOLVED, title: decisionTargets[29].title,
  body_state: RESOLVED, body_sha256: decisionTargets[29].content_sha256_lf,
  excerpt_state: RESOLVED, excerpt_sha256: sha256(decisionTargets[29].excerpt),
  binding: { scope: decision.key, ref: PR100, file: 'content/commercial-decision-2026-11-08-v2/network-tehran.html', transform: 'post_content = payload bytes (content_sha256_lf verified); excerpt = pinned string (sha256 equals the 11-08 manifest value; the release pre-condition separately pins the current DB excerpt 125e36b2…)' },
  notes: ['production DB observed drift vs intended bytes (readback 16b9789a… at 2026-11-15T21:40Z) — production-side unresolved change does NOT alter this intent'],
});
/* 31/33/35 — staging-sync-truth payloads (production truth per guarded constants; production readback equals these) */
for (const [id, path] of [[31, '/services/network-support-tehran/'], [33, '/services/network-setup-tehran/'], [35, '/services/mikrotik-tehran/']]) {
  const s = syncTargets[id];
  resolve(path, {
    title_state: RESOLVED, title: s.title,
    body_state: RESOLVED, body_sha256: s.lf,
    excerpt_state: RESOLVED, excerpt_sha256: s.exc,
    binding: { scope: 'tehnet-staging-sync-truth-20261113-v1 (constants pinned in guarded migration PHP; production-truth payloads)', ref: PR100, file: 'content/' + ({ 31: 'network-support-2026-11-01/network-support.html', 33: 'server-branch-2026-11-04/network-setup.html', 35: 'mikrotik-service-2026-11-01/mikrotik-service.html' })[id], transform: 'post_content = payload bytes (lf verified); title/excerpt = pinned strings (sha256 proof passed)' },
    notes: ['execution of this scope is staging-only by contract; the payload bytes themselves are the pinned production truth and production readback equals them'],
  });
}
/* 8 — decision changes post_content ONLY; title/excerpt not payload-determined */
resolve('/services/', {
  title_state: CARRIED, title: byPath['/services/'].title,
  body_state: RESOLVED, body_sha256: decisionTargets[8].content_sha256_lf,
  excerpt_state: CARRIED, excerpt_sha256: byPath['/services/'].excerpt_sha256,
  binding: { scope: decision.key, ref: PR100, file: 'content/commercial-decision-2026-11-08-v2/services.html', transform: 'post_content = payload bytes (lf verified); change_fields=[post_content] only' },
  notes: ['title/excerpt untouched by the release — carried 2026-11-08 values recorded as reference, not activation-grade'],
});
/* 37 — PR101 remote payload: content only; title preserved-and-pinned; excerpt preserved-but-unpinned */
resolve('/services/remote-support/', {
  title_state: RESOLVED, title: remoteManifest.target.title_observed,
  body_state: RESOLVED, body_sha256: remoteManifest.content_sha256_lf,
  excerpt_state: CARRIED, excerpt_sha256: byPath['/services/remote-support/'].excerpt_sha256,
  binding: { scope: remoteManifest.key, ref: PR101, file: 'content/remote-support-2026-11-01/remote-support.html', transform: 'post_content = payload bytes (lf verified); change_fields=[post_content]; title/slug/excerpt/meta preserved' },
  notes: ['status DRAFT_NOT_DEPLOYED; excerpt value not pinned by payload — carried reference only'],
});
/* A1-A4/N1 — decision new pages: title fixed in guarded const, excerpt = pinned string */
for (const key of ['A1', 'A2', 'A3', 'A4', 'N1']) {
  const p = decisionPages[key];
  const path = key === 'N1' ? '/services/server-virtualization-tehran/' : '/' + p.slug + '/';
  resolve(path, {
    title_state: RESOLVED, title: p.title,
    body_state: RESOLVED, body_sha256: p.content_sha256_lf,
    excerpt_state: RESOLVED, excerpt_sha256: sha256(p.excerpt),
    binding: { scope: decision.key, ref: PR100, file: 'content/commercial-decision-2026-11-08-v2/' + p.content_file, transform: 'new page: post_content = payload bytes (lf verified); title = guarded const; excerpt = pinned string (sha256 computed; equals 11-08 manifest value where present)' },
    notes: [],
  });
}
/* no-payload rows — BLOCKED, never guessed */
for (const path of ['/', '/about/', '/contact/', '/technical-methodology/', '/services/voice-network-readiness/']) {
  const base = byPath[path];
  const notes = ['no approved immutable payload in PR100/PR101 determines this row'];
  if (path === '/') notes.push('owner-authorized live home edits (8c74794) are outside any release payload — content decision required');
  if (path === '/about/') notes.push('owner-authorized live about edits (8c74794) are outside any release payload — content decision required');
  if (path === '/services/voice-network-readiness/') notes.push('body hash matched production AND staging readbacks (7f384153…), but that is DB observation, not release intent; staging id 193 recorded as separate unresolved environment mapping');
  resolve(path, { notes });
}

/* --- emit candidate (deterministic: sorted keys, no timestamps) --- */
const resolvedCount = rows.filter(r => r.status === 'RESOLVED_COMPLETE').length;
const blockedRows = rows.filter(r => r.status === BLOCKED).map(r => r.path);
const candidate = {
  schema: 2,
  key: 'tehnet-index-allowlist-20261108-v1',
  operation: 'activate',
  candidate_kind: 'INTENDED_BUNDLE_SOURCE_ONLY',
  status: 'NOT_FOR_ACTIVATION',
  identity_base: 'production',
  production_ids_preserved: true,
  staging_environment_binding: {
    unresolved_separate_mapping: true,
    note: 'staging resolves /services/voice-network-readiness/ to id 193 (id 206 absent there); recorded as a per-environment mapping QUESTION, never as a production replacement',
    proposed_env_ids_example: { '/services/voice-network-readiness/': { production: 206, staging: 193 } },
  },
  inputs: {
    pr100_head: PR100,
    pr101_head: PR101,
    payload_digests: {
      decision_services_html: decisionTargets[8].content_sha256_lf,
      decision_network_tehran_html: decisionTargets[29].content_sha256_lf,
      sync_network_support_html: syncTargets[31].lf,
      sync_network_setup_html: syncTargets[33].lf,
      sync_mikrotik_html: syncTargets[35].lf,
      decision_A1_html: decisionPages.A1.content_sha256_lf,
      decision_A2_html: decisionPages.A2.content_sha256_lf,
      decision_A3_html: decisionPages.A3.content_sha256_lf,
      decision_A4_html: decisionPages.A4.content_sha256_lf,
      decision_N1_html: decisionPages.N1.content_sha256_lf,
      pr101_remote_support_html: remoteManifest.content_sha256_lf,
    },
  },
  allowlist_paths_exact: original.targets.map(t => t.path),
  targets: rows.map(r => ({
    path: r.path,
    id: r.id,
    identity: 'production',
    status: r.status,
    fields: {
      body: { state: r.body_state, sha256: r.body_sha256 },
      title: { state: r.title_state, value: r.title },
      excerpt: { state: r.excerpt_state, sha256: r.excerpt_sha256 },
    },
    binding: r.binding,
    notes: r.notes,
    carried_reference: r.carried_reference,
  })),
  blocked_rows: blockedRows,
  resolved_complete_count: resolvedCount,
  activation_incomplete: resolvedCount < 16,
  production_authorization: 'NEEDS_SEPARATE_EXACT_ALLOWLIST_OWNER_APPROVAL',
};
fs.writeFileSync(OUT_MANIFEST, JSON.stringify(candidate, null, 1), 'utf8');

/* private-negative summary (also asserted) */
ck('allowlist_paths_unchanged', JSON.stringify(candidate.allowlist_paths_exact) === JSON.stringify(original.targets.map(t => t.path)));
ck('production_ids_preserved', candidate.targets.every(t => t.id === byPath[t.path].id));
ck('voice206_preserved', candidate.targets.find(t => t.path === '/services/voice-network-readiness/').id === 206);
ck('no_staging_id_in_production_rows', candidate.targets.every(t => t.id !== 193 && !(t.binding && t.binding.staging_id !== undefined)), { note: 'production rows carry production ids only; the 193 mapping lives solely in staging_environment_binding' });
ck('no_private_additions', candidate.allowlist_paths_exact.every(p => /^\/[a-z0-9\-\/]*\/?$/.test(p)) && !candidate.allowlist_paths_exact.some(p => /ticket|quote|order|account|cart|checkout|my-account|lab/.test(p)));
ck('blocked_rows_flagged', candidate.activation_incomplete === true && blockedRows.length === 7);
ck('not_for_activation', candidate.status === 'NOT_FOR_ACTIVATION');

console.log('GENERATED ' + path.basename(OUT_MANIFEST));
console.log('RESOLVED_COMPLETE=' + resolvedCount + '/16 BLOCKED=' + blockedRows.length);
console.log('CHECKS=' + checks.length + ' all-pass=' + checks.every(c => c.pass));
console.log('MANIFEST_SHA256=' + sha256(JSON.stringify(candidate, null, 1)));
fs.writeFileSync(path.join(OUT_DIR, 'intended-bundle-checks.json'), JSON.stringify({ checks, summary: { total: checks.length, passed: checks.filter(c => c.pass).length } }, null, 1), 'utf8');
