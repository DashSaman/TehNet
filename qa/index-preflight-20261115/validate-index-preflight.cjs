'use strict';
/* TN-INDEX-PREFLIGHT-20261115 — static contract validation of the PR100 index path.
 * Validates activation-manifest.json + runtime-manifest.json + runtime class +
 * policy migration + release-operator wiring, ALL read from git at the pinned PR100 head.
 * PHP files are syntax-checked with `php -l` only — never executed, no DB touched here.
 * PART B (staging readback comparison) runs only when a readback JSON path is given;
 * the readback itself is produced by staging-readback.php (READ-ONLY wp-cli). */
const { execFileSync, spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const PR100_REF = 'origin/feat/setup-reconcile-20261113';
const PHP_EXE = path.resolve(__dirname, '../../../php-runtime/php.exe');
const ROOT = path.resolve(__dirname, '../..');

function gitShow(ref, file) {
  return execFileSync('git', ['show', ref + ':' + file], { cwd: ROOT, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024 });
}
function gitRev(ref) {
  return execFileSync('git', ['rev-parse', ref], { cwd: ROOT, encoding: 'utf8' }).trim();
}

/* tiny check runner */
const checks = [];
function ck(name, pass, detail) {
  checks.push({ name, pass: !!pass, detail: detail === undefined ? null : detail });
  console.log((pass ? 'PASS ' : 'FAIL ') + name + (detail !== undefined && detail !== null ? '  ' + JSON.stringify(detail).slice(0, 160) : ''));
}
function must(name, pass, detail) { ck(name, pass, detail); if (!pass) throw new Error('HARD FAIL: ' + name); }

/* --- extractors --- */
function extractMaxPaths(classSrc) {
  const m = classSrc.match(/public const MAX_PATHS=\[(.*?)\];/s);
  if (!m) throw new Error('MAX_PATHS not found in class source');
  return [...m[1].matchAll(/'([^']+)'/g)].map(x => x[1]);
}
function extractFixedMap(migSrc) {
  const m = migSrc.match(/\$fixed=\[([^\]]+)\];/s);
  if (!m) throw new Error('$fixed not found');
  return Object.fromEntries([...m[1].matchAll(/'([^']+)'\s*=>\s*(\d+)/g)].map(x => [x[1], parseInt(x[2], 10)]));
}
function extractCreatedMap(migSrc) {
  const m = migSrc.match(/\$created=\[([^\]]+)\];/s);
  if (!m) throw new Error('$created not found');
  return Object.fromEntries([...m[1].matchAll(/'([^']+)'\s*=>\s*'([A-Za-z0-9]+)'/g)].map(x => [x[1], x[2]]));
}
const SHA_RE = /^[a-f0-9]{64}$/;

/* --- main --- */
function main(stagingReadbackPath, productionReadbackPath) {
  const startedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  const head = gitRev(PR100_REF);
  console.log('PR100 head: ' + head);

  const classSrc = gitShow(PR100_REF, 'site/plugins/tehnet-core/includes/class-index-policy.php');
  const migSrc = gitShow(PR100_REF, 'ops/migrate-index-policy.php');
  const opSrc = gitShow(PR100_REF, 'ops/release-growth-content.py');
  const activation = JSON.parse(gitShow(PR100_REF, 'seo/index-decision-2026-11-08-v2/activation-manifest.json'));
  const runtime = JSON.parse(gitShow(PR100_REF, 'seo/index-decision-2026-11-08-v2/runtime-manifest.json'));

  const maxPaths = extractMaxPaths(classSrc);
  const fixed = extractFixedMap(migSrc);
  const created = extractCreatedMap(migSrc);

  /* PART A1 — runtime class contract */
  must('class_key_matches', /public const KEY='tehnet-index-allowlist-20261108-v1';/.test(classSrc));
  must('class_option_name', /public const OPTION='tn_index_policy_20261108';/.test(classSrc));
  must('class_max_paths_is_16', maxPaths.length === 16, maxPaths.length);
  must('class_fail_closed_no_blog_public_write', !/update_option\s*\(|add_option\s*\(|delete_option\s*\(/.test(classSrc), 'class must never write options');
  must('class_fail_closed_blog_public_gate', /get_option\('blog_public'\)!=='0'/.test(classSrc));
  must('class_no_content_writes', !/wp_insert_post|wp_update_post|wp_delete_post|wp_delete_post|wp_trash_post/.test(classSrc));
  must('class_nonapproved_gets_noindex', /X-Robots-Tag: noindex, nofollow/.test(classSrc) && /\$r\['noindex'\]=true/.test(classSrc) && /'nofollow'=>true|\$r\['nofollow'\]=true/.test(classSrc));
  must('class_approved_removal_scoped', /remove_filter\('wp_robots','wp_robots_noindex'\)/.test(classSrc));

  /* PART A2 — migration PHP contract */
  must('mig_baseline_blog_public_0_required', /get_option\('blog_public'\)!=='0'/.test(migSrc));
  must('mig_core_noindex_filter_required', /has_filter\('wp_robots','wp_robots_noindex'\)===false/.test(migSrc));
  must('mig_never_updates_blog_public', !/\$set\([^)]*blog_public/.test(migSrc) && !/update_option\(['"]blog_public/.test(migSrc));
  must('mig_single_option_write_paths', (migSrc.match(/\$wpdb->update\(/g) || []).length === 1 && (migSrc.match(/\$wpdb->insert\(/g) || []).length === 1 && (migSrc.match(/\$wpdb->delete\(/g) || []).length === 1, 'writes confined to the one policy option via $set');
  must('mig_production_gate_needs_key_env', /getenv\('TN_GROWTH_AUTHORIZED_RELEASE'\)===%s|\$key/.test(migSrc) && /TN_GROWTH_AUTHORIZED_RELEASE/.test(migSrc));
  must('mig_enforces_16_targets', /!==16/.test(migSrc));
  must('mig_staging_gate_closed_isolation', /pre_wp_mail/.test(migSrc) && /woocommerce_available_payment_gateways/.test(migSrc) && /tn-guard|probe/.test(migSrc));
  must('mig_fixed_map_11', Object.keys(fixed).length === 11, Object.keys(fixed).length);
  must('mig_created_map_5', Object.keys(created).length === 5, Object.keys(created).length);

  /* PART A3 — activation manifest contract */
  must('act_schema_key_operation', activation.schema === 1 && activation.key === 'tehnet-index-allowlist-20261108-v1' && activation.operation === 'activate');
  must('act_exactly_16_targets', Array.isArray(activation.targets) && activation.targets.length === 16, activation.targets.length);
  const actPaths = activation.targets.map(t => t.path);
  must('act_paths_exactly_max_paths_set', JSON.stringify([...actPaths].sort()) === JSON.stringify([...maxPaths].sort()), 'set equality both directions enforced below');
  must('act_no_lab_paths', actPaths.every(p => !p.startsWith('/lab/')), 'RETAIN_NOINDEX pages excluded');
  must('act_unique_paths', new Set(actPaths).size === 16);
  const ids = activation.targets.filter(t => t.id !== null).map(t => t.id);
  const keys = activation.targets.filter(t => t.id === null).map(t => t.key);
  must('act_11_fixed_5_created', ids.length === 11 && keys.length === 5, { ids: ids.length, keys: keys.length });
  must('act_unique_ids', new Set(ids).size === ids.length);
  must('act_unique_keys', new Set(keys).size === keys.length);
  must('act_keys_are_A1_A4_N1', JSON.stringify([...keys].sort()) === JSON.stringify(['A1', 'A2', 'A3', 'A4', 'N1'].sort()));
  let fixedOk = true, createdOk = true;
  for (const t of activation.targets) {
    if (fixed[t.path] !== undefined) { if (t.id !== fixed[t.path]) fixedOk = false; }
    if (created[t.path] !== undefined) { if (t.key !== created[t.path] || t.id !== null) createdOk = false; }
  }
  must('act_fixed_ids_match_migration_map', fixedOk);
  must('act_created_keys_match_migration_map', createdOk);
  must('act_hash_format_valid', activation.targets.every(t => SHA_RE.test(t.body_sha256) && (t.excerpt_sha256 === undefined || SHA_RE.test(t.excerpt_sha256))));
  must('act_titles_present', activation.targets.every(t => typeof t.title === 'string' && t.title.length > 3));
  must('act_d3_still_needs_exact_owner_approval', activation.production_authorization === 'NEEDS_SEPARATE_EXACT_ALLOWLIST_OWNER_APPROVAL', activation.production_authorization);
  /* negative-private: no customer/commerce record types can be targeted — MAX_PATHS are page paths only */
  must('act_no_private_post_types', actPaths.every(p => /^\/[a-z0-9\-\/]*\/?$/.test(p)) && !actPaths.some(p => /ticket|quote|order|account|cart|checkout|my-account/.test(p)), 'allowlist is plain public pages only');

  /* PART A4 — runtime manifest contract (D2 install-off) */
  must('rt_install_off_contract', runtime.schema === 1 && runtime.key === 'tehnet-index-runtime-20261108-v1' && runtime.operation === 'install-off' && runtime.default === 'OFF' && runtime.blog_public === '0');
  must('rt_needs_owner_approval', runtime.production_authorization === 'NEEDS_SEPARATE_OWNER_APPROVAL', runtime.production_authorization);

  /* PART A5 — release operator wiring */
  must('op_has_index_scopes', opSrc.includes("INDEX_RUNTIME_SCOPE = 'tehnet-index-runtime-20261108-v1'") && opSrc.includes("INDEX_ACTIVATION_SCOPE = 'tehnet-index-allowlist-20261108-v1'"));
  must('op_authorization_env_binding', opSrc.includes("env['TN_GROWTH_AUTHORIZED_RELEASE'] = self.scope"));
  must('op_runtime_files_declared', opSrc.includes('site/plugins/tehnet-core/includes/class-index-policy.php'));

  /* PART A6 — payload bundles for the 5 created pages exist in PR100 tree */
  const bundleDir = 'content/commercial-decision-2026-11-08-v2/';
  const bundleBodies = ['network-support-contract-guide.html', 'network-project-proposal-checklist.html', 'business-server-planning-guide.html', 'server-backup-restore-acceptance.html', 'server-virtualization-tehran.html'];
  for (const b of bundleBodies) {
    let ok = false;
    try { gitShow(PR100_REF, bundleDir + b); ok = true; } catch (e) { ok = false; }
    must('bundle_exists:' + b, ok);
  }

  /* PART A7 — php -l syntax check ONLY (never executed) */
  must('php_runtime_present', fs.existsSync(PHP_EXE), 'php-runtime/php.exe (local runtime, path withheld)');
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'tn-idx-lint-'));
  for (const [name, src] of [['class-index-policy.php', classSrc], ['migrate-index-policy.php', migSrc]]) {
    const f = path.join(tmp, name);
    fs.writeFileSync(f, src);
    const r = spawnSync(PHP_EXE, ['-l', f], { encoding: 'utf8', timeout: 30000 });
    const raw = ((r.stdout || '') + (r.stderr || '')).trim();
    must('php_lint:' + name, r.status === 0 && /No syntax errors detected/.test(raw), raw.split(tmp).join('[TMP]').replace(/[A-Za-z]:\\[^\s"]+/g, '[LOCAL_PATH]').slice(0, 90));
  }
  fs.rmSync(tmp, { recursive: true, force: true });

  /* PART B — read-only readback comparisons (optional inputs) */
  const result = {
    packet: 'TN-INDEX-PREFLIGHT-20261115',
    started_utc: startedUtc,
    finished_utc: new Date().toISOString().replace(/\.\d+Z$/, 'Z'),
    pr100_ref: PR100_REF,
    pr100_head_sha: head,
    static: { checks: checks.slice(), passed: checks.filter(c => c.pass).length, failed: checks.filter(c => !c.pass).length },
    staging: { state: 'NOT_RUN' },
    production: { state: 'NOT_RUN' },
    verdict: null,
  };

  const compareReadback = (rb, label) => {
    const cmp = [];
    const home = (rb.home || '').replace(/\/$/, '');
    for (const t of activation.targets) {
      const row = (rb.targets || []).find(x => x.path === t.path);
      if (!row) { cmp.push({ path: t.path, match: false, reason: 'missing_in_readback' }); continue; }
      const reasons = [];
      if (!row.found) reasons.push('not_found');
      else {
        if (row.post_type !== 'page') reasons.push('post_type:' + row.post_type);
        if (row.post_status !== 'publish') reasons.push('post_status:' + row.post_status);
        if (row.has_password) reasons.push('password_protected');
        if (fixed[t.path] !== undefined && row.id !== fixed[t.path]) reasons.push('id_drift:' + row.id);
        if (created[t.path] !== undefined && row.growth_key !== created[t.path]) reasons.push('growth_key_drift:' + row.growth_key);
        if (row.content_sha256 !== t.body_sha256) reasons.push('body_hash_drift');
        if (t.excerpt_sha256 !== undefined ? row.excerpt_sha256 !== t.excerpt_sha256 : row.excerpt_sha256 !== 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855') reasons.push('excerpt_hash_drift');
        if (typeof row.permalink === 'string' && row.permalink !== home + t.path) reasons.push('permalink_drift');
        if (row.title !== t.title) reasons.push('title_drift');
      }
      cmp.push({ path: t.path, match: reasons.length === 0, reason: reasons.join(',') || 'ok' });
    }
    const matched = cmp.filter(c => c.match).length;
    return {
      state: 'COMPARED',
      observed_utc: rb.observed_utc,
      env: rb.env,
      home: rb.home,
      blog_public: rb.blog_public,
      wp_robots_noindex_filter: rb.wp_robots_noindex,
      runtime_class_installed: rb.runtime_class === true,
      direct_ids: rb.direct_ids || undefined,
      policy_option_state: rb.policy_option === undefined ? 'NOT_PROBED' : (rb.policy_option === null ? 'NOT_APPLIED_OFF' : 'PRESENT'),
      targets: cmp,
      matched,
      total: cmp.length,
    };
  };

  if (stagingReadbackPath) {
    const rb = JSON.parse(fs.readFileSync(stagingReadbackPath, 'utf8'));
    result.staging = compareReadback(rb, 'staging');
    result.staging.policy_option_present = rb.policy_option_present === true;
    result.staging.d2_status = rb.runtime_class === true ? 'RUNTIME_PRESENT' : 'RUNTIME_ABSENT_INSTALL_OFF_PENDING';
    ck('staging_env_is_staging', rb.env === 'staging', rb.env);
    ck('staging_blog_public_0', rb.blog_public === '0', rb.blog_public);
    ck('staging_core_noindex_filter_present', rb.wp_robots_noindex === true);
    ck('staging_policy_option_off', rb.policy_option_present !== true, 'policy not applied yet');
    ck('staging_runtime_class_state', typeof rb.runtime_class === 'boolean', String(rb.runtime_class));
    ck('staging_all_16_targets_match_manifest', result.staging.matched === 16, result.staging.matched + '/16');
  }
  if (productionReadbackPath) {
    const rb = JSON.parse(fs.readFileSync(productionReadbackPath, 'utf8'));
    result.production = compareReadback(rb, 'production');
    ck('production_env_is_production', rb.env === 'production', rb.env);
    ck('production_blog_public_0', rb.blog_public === '0', rb.blog_public);
    ck('production_core_noindex_filter_present', rb.wp_robots_noindex === true);
    const fixedIdMismatches = result.production.targets
      .filter(t => fixed[t.path] !== undefined)
      .filter(t => /id_drift|not_found|missing_in_readback/.test(t.reason));
    ck('production_all_fixed_ids_match_manifest', fixedIdMismatches.length === 0, fixedIdMismatches.length + ' fixed-path id/lookup mismatches (created A1-A4/N1 pages are D1 staging scope, absent on production is expected pre-release)');
    ck('production_id206_is_voice_network_readiness', (rb.direct_ids && rb.direct_ids['206'] && rb.direct_ids['206'].path === '/services/voice-network-readiness/') === true, JSON.stringify(rb.direct_ids && rb.direct_ids['206']));
    ck('production_id193_absent', (rb.direct_ids && rb.direct_ids['193'] && rb.direct_ids['193'].missing === true) === true, JSON.stringify(rb.direct_ids && rb.direct_ids['193']));
  }
  result.static.checks = checks.slice();
  result.static.passed = checks.filter(c => c.pass).length;
  result.static.failed = checks.filter(c => !c.pass).length;

  const anyFail = result.static.failed > 0 || (result.staging.state === 'COMPARED' && result.staging.matched !== 16);
  result.verdict = anyFail ? 'FAIL' : (result.staging.state === 'COMPARED' ? 'PREFLIGHT_OK_D3_STILL_UNAUTHORIZED' : 'STATIC_OK_STAGING_NOT_RUN');
  const outPath = path.join(__dirname, 'preflight-result.json');
  fs.writeFileSync(outPath, JSON.stringify(result, null, 1), 'utf8');
  console.log('\nTOTAL=' + checks.length + ' PASS=' + checks.filter(c => c.pass).length + ' FAIL=' + checks.filter(c => !c.pass).length);
  console.log('STAGING=' + result.staging.state + (result.staging.state === 'COMPARED' ? ' matched=' + result.staging.matched + '/16' : ''));
  console.log('PRODUCTION=' + result.production.state + (result.production.state === 'COMPARED' ? ' matched=' + result.production.matched + '/16' : ''));
  console.log('VERDICT=' + result.verdict);
  console.log('WROTE ' + outPath);
  return anyFail ? 1 : 0;
}

if (require.main === module) {
  const sArg = process.argv[2];
  const pArg = process.argv[3];
  process.exitCode = main(sArg && fs.existsSync(sArg) ? sArg : undefined, pArg && fs.existsSync(pArg) ? pArg : undefined);
}
module.exports = { extractMaxPaths, extractFixedMap, extractCreatedMap };
