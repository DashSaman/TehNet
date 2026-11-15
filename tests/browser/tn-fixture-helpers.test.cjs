'use strict';
/* Dependency-free tests for tn-fixture-helpers.cjs — node built-ins only.
 * All external effects (SSH/DB/mail/browser) are stubbed; nothing touches the network.
 * PHP is syntax-checked with `php -l` (local runtime) — never executed. */
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const H = require('./tn-fixture-helpers.cjs');

const PHP_EXE = path.resolve(__dirname, '../../../php-runtime/php.exe');
const GOOD = 'TN-RUN-abc123-def456';
const OTHER = 'TN-RUN-abc123-def456x'; // valid marker of ANOTHER run; must never satisfy GOOD's ownership
const FIXTURE_HOME = 'http://localhost:18085/';

const tests = [];
const t = (name, fn) => tests.push([name, fn]);

/* MANAGER_REVIEW 6901713229 negative counterexamples — written FIRST, must fail before the fix */
t('NEG1 redact: actual tn_service_receipt query token must be redacted', () => {
  const checks = [{ name: 'receipt', pass: true, detail: { url: 'http://x/services/network-setup-tehran/?tn_service_receipt=SYNTHETIC_TOKEN_123' } }];
  const copy = H.serializeOutput({ run_id: 'x', checks: [] }, checks, GOOD);
  assert.ok(!JSON.stringify(copy).includes('SYNTHETIC_TOKEN_123'), 'tn_service_receipt token must not survive serialization');
  assert.ok(copy.checks[0].detail.url.includes('tn_service_receipt=[REDACTED]'));
});
t('NEG2 boundary: prefix-collision marker of ANOTHER run must be rejected (JS predicate + PHP generation)', () => {
  const collision = { id: 42, type: 'tn_ticket', email: 'acceptance-test+' + OTHER + '@example.invalid' };
  assert.equal(H.isOwnedRecord(collision, GOOD), false, 'substring containment must not own another run record');
  assert.equal(H.ownershipRejectionReason(collision, GOOD), 'email_marker_mismatch');
  const validOther = { id: 51, type: 'tn_quote', email: 'acceptance-test+' + OTHER + '@example.invalid' };
  assert.equal(H.isOwnedRecord(validOther, OTHER), true, 'the other run still owns its own record');
  const phpFind = H.buildFindOwnedPhp(GOOD);
  const phpDel = H.buildDeleteOwnedPhp(GOOD, [42]);
  for (const php of [phpFind, phpDel]) {
    assert.ok(php.includes('strpos($email,"+".$m."@")!==false'), 'PHP must use exact +marker@ boundary');
    assert.ok(!php.includes('strpos($email,$m)!==false'), 'bare substring comparison must be gone');
  }
});
t('NEG3 journey: non-throwing incomplete deletion {deleted:[],skipped:[42]} must FAIL the run', async () => {
  const s = goodEffects();
  s.effects.deleteOwnedRecords = async () => ({ deleted: [], skipped: [42] }); // wp_delete_post silently failed
  const res = await H.runJourney({
    marker: GOOD, expectedFixture: { home_url: FIXTURE_HOME }, effects: s.effects, operation: async () => 'ok',
  });
  assert.equal(res.status, 'FAILED_CLEANUP', 'incomplete cleanup must never be PASSED');
  assert.match(String(res.cleanup.error), /incomplete_deletion/);
});

/* --- marker --- */
t('marker: valid shape accepted, junk rejected', () => {
  assert.equal(H.isRunMarker(GOOD), true);
  assert.equal(H.isRunMarker('TNMARK-old'), false);
  assert.equal(H.isRunMarker(''), false);
  assert.equal(H.isRunMarker(null), false);
  assert.equal(H.isRunMarker('TN-RUN-' + 'a;b'), false);
  assert.throws(() => H.assertRunMarker('junk'), /invalid run marker/);
  const m1 = H.newRunMarker(1700000000000);
  assert.equal(H.isRunMarker(m1), true);
  assert.notEqual(m1, H.newRunMarker(1700000000000), 'two markers at same ms must differ');
});

/* --- same marker reaches ALL forms --- */
t('formEmail: identical marker for service/B2B/no-JS forms; bad marker throws', () => {
  const e = H.formEmail(GOOD);
  assert.equal(e, 'acceptance-test+TN-RUN-abc123-def456@example.invalid');
  assert.equal(H.formEmail(GOOD, 'nojs-form'), 'nojs-form+TN-RUN-abc123-def456@example.invalid');
  assert.throws(() => H.formEmail('TNMARK-old'), /invalid run marker/);
});

/* --- ownership predicate --- */
t('ownership: exact owned record accepted', () => {
  const rec = { id: 42, type: 'tn_ticket', email: 'acceptance-test+' + GOOD + '@example.invalid' };
  assert.equal(H.ownershipRejectionReason(rec, GOOD), null);
  assert.equal(H.isOwnedRecord(rec, GOOD), true);
  const rec2 = { id: 7, type: 'tn_quote', email_has_marker: true }; // PHP-side exact strpos evidence
  assert.equal(H.isOwnedRecord(rec2, GOOD), true);
});
t('ownership: unowned sentinels rejected with reasons', () => {
  const mk = (email, extra) => Object.assign({ id: 9, type: 'tn_ticket' }, extra, email !== undefined ? { email } : {});
  assert.equal(H.ownershipRejectionReason(mk('acceptance-test+TN-RUN-othermarker-x1@example.invalid'), GOOD), 'email_marker_mismatch');
  assert.equal(H.ownershipRejectionReason(mk('acceptance-test@example.invalid'), GOOD), 'email_marker_mismatch');
  assert.equal(H.ownershipRejectionReason(mk(undefined, { email_has_marker: false }), GOOD), 'email_marker_mismatch');
  assert.equal(H.ownershipRejectionReason(mk(undefined), GOOD), 'email_marker_mismatch'); // no evidence at all
  assert.equal(H.ownershipRejectionReason({ id: 9, type: 'tn_page', email: 'x+' + GOOD + '@e.invalid' }, GOOD), 'disallowed_type');
  assert.equal(H.ownershipRejectionReason({ id: '9', type: 'tn_ticket', email: GOOD }, GOOD), 'bad_id');
  assert.equal(H.ownershipRejectionReason(null, GOOD), 'not_object');
  assert.equal(H.isOwnedRecord(mk('acceptance-test+TN-RUN-othermarker-x1@example.invalid'), GOOD), false);
});

/* --- preflight verdict: fail closed --- */
const PERFECT = {
  env: 'staging', blog_public: '0', home: FIXTURE_HOME, mail_blocked: true, http_blocked: true,
  cron_disabled: true, http_probe_blocked: true, payments_disabled: true,
};
const KEY_TO_CHECK = {
  env: 'env_staging', blog_public: 'blog_public_0', home: 'fixture_identity',
  mail_blocked: 'mail_block_confirmed', http_blocked: 'http_block_confirmed', cron_disabled: 'cron_disabled',
  http_probe_blocked: 'http_probe_blocked', payments_disabled: 'payments_disabled',
};
t('preflight: perfect probes pass', () => {
  const v = H.evaluatePreflight(PERFECT, { home_url: FIXTURE_HOME });
  assert.equal(v.ok, true);
  assert.deepEqual(v.failed, []);
  assert.equal(v.checks.length, 8);
});
t('preflight: any false/missing evidence fails (fail closed)', () => {
  for (const key of Object.keys(PERFECT)) {
    const broken = Object.assign({}, PERFECT);
    delete broken[key];
    const v = H.evaluatePreflight(broken, { home_url: FIXTURE_HOME });
    assert.equal(v.ok, false, 'missing ' + key + ' must fail');
    assert.deepEqual(v.failed, [KEY_TO_CHECK[key]]);
  }
  const vNull = H.evaluatePreflight(null, { home_url: FIXTURE_HOME });
  assert.equal(vNull.ok, false);
  assert.equal(vNull.failed.length, 8);
});
t('preflight: fixture identity — a DIFFERENT staging with identical flags must be rejected', () => {
  const impostor = Object.assign({}, PERFECT, { home: 'http://localhost:19999/' });
  const v = H.evaluatePreflight(impostor, { home_url: FIXTURE_HOME });
  assert.equal(v.ok, false);
  assert.deepEqual(v.failed, ['fixture_identity']);
  assert.equal(H.evaluatePreflight(PERFECT, { home_url: FIXTURE_HOME }).ok, true);
  const vNoExpected = H.evaluatePreflight(PERFECT, null);
  assert.equal(vNoExpected.ok, false, 'preflight without an expected fixture identity is insufficient');
});
t('preflight: payments probe with leftover sentinel (non-zero) fails', () => {
  const v = H.evaluatePreflight(Object.assign({}, PERFECT, { payments_disabled: false }));
  assert.equal(v.ok, false);
  assert.ok(v.failed.includes('payments_disabled'));
});
t('preflight: assertPreflight throws listing failed names', () => {
  const v = H.evaluatePreflight(Object.assign({}, PERFECT, { mail_blocked: false, blog_public: '1' }), { home_url: FIXTURE_HOME });
  assert.throws(() => H.assertPreflight(v), e => {
    assert.equal(e.name, 'PreflightBlocked');
    assert.deepEqual(e.failed.sort(), ['blog_public_0', 'mail_block_confirmed']);
    return true;
  });
  assert.equal(H.assertPreflight(H.evaluatePreflight(PERFECT, { home_url: FIXTURE_HOME })).ok, true);
});

/* --- generated PHP: real PHP comparison, no JS syntax, no env vars, no newest-single --- */
t('probe PHP: no wp_mail() send call; sentinel gateway array; isolation mirrors repo guard', () => {
  const php = H.buildPreflightProbePhp();
  assert.ok(!/\bwp_mail\s*\(/.test(php), 'must not attempt a mail send');
  assert.ok(php.includes('apply_filters("pre_wp_mail"'), 'mail block evidenced by installed filter');
  assert.ok(php.includes('tn-guard-sentinel'), 'gateway probe starts NON-empty');
  assert.ok(php.includes('woocommerce_available_payment_gateways'));
});
t('find PHP: exact +marker@ boundary, marker embedded, no includes/env/newest-single', () => {
  const php = H.buildFindOwnedPhp(GOOD);
  assert.ok(php.includes("'TN-RUN-abc123-def456'"));
  assert.ok(php.includes('strpos($email,"+".$m."@")!==false'), 'exact boundary comparison (real PHP)');
  assert.ok(!php.includes('strpos($email,$m)!==false'), 'no bare substring comparison');
  assert.ok(!php.includes('.includes('), 'no JS syntax');
  assert.ok(!php.includes('process.env'), 'no env var dependency');
  assert.ok(!php.includes('$_ENV'));
  assert.ok(!/"posts_per_page"=>1/.test(php), 'no newest-single-record selection');
  assert.ok(php.includes('email_has_marker'));
});
t('delete PHP: exact boundary, wp_delete_post result checked, sanitized id list, skips non-owned', () => {
  const php = H.buildDeleteOwnedPhp(GOOD, [5, 9]);
  assert.ok(php.includes('strpos($email,"+".$m."@")!==false'));
  assert.ok(!php.includes('strpos($email,$m)!==false'));
  assert.ok(php.includes('$res=wp_delete_post($id,true);') && php.includes('if($res!==false&&$res!==null){$deleted[]='), 'actual delete result checked');
  assert.ok(php.includes('"failed"=>$failed'), 'failed deletions reported');
  assert.ok(!php.includes('.includes('));
  assert.ok(!php.includes('process.env'));
  assert.ok(php.includes('array(5,9)'));
  assert.ok(php.includes('$skipped'));
  assert.throws(() => H.buildDeleteOwnedPhp(GOOD, [-1]), /positive integers/);
  assert.throws(() => H.buildDeleteOwnedPhp(GOOD, [NaN]), /positive integers/);
  assert.throws(() => H.buildDeleteOwnedPhp('junk', [5]), /invalid run marker/);
});
t('phpSingleQuoted escaping round-trips quote and backslash', () => {
  assert.equal(H.phpSingleQuoted("a'b\\c"), "'a\\'b\\\\c'");
  assert.throws(() => H.phpSingleQuoted(''), /non-empty/);
  assert.throws(() => H.phpSingleQuoted('x\ny'), /control\/newline/);
});

/* --- PHP syntax check via php -l (NO execution) --- */
t('php -l: all three generated files are syntactically valid (lint only, never run)', () => {
  assert.ok(fs.existsSync(PHP_EXE), 'local php runtime must exist: ' + PHP_EXE);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'tn-php-lint-'));
  const files = {
    'probe.php': H.buildPreflightProbePhp(),
    'find.php': H.buildFindOwnedPhp(GOOD),
    'delete.php': H.buildDeleteOwnedPhp(GOOD, [5, 9]),
  };
  for (const [name, php] of Object.entries(files)) {
    const f = path.join(dir, name);
    fs.writeFileSync(f, php);
    const r = spawnSync(PHP_EXE, ['-l', f], { encoding: 'utf8', timeout: 30000 });
    assert.equal(r.status, 0, name + ' lint failed: ' + (r.stdout || '') + (r.stderr || ''));
    assert.ok(/No syntax errors detected/.test((r.stdout || '') + (r.stderr || '')), name);
  }
  fs.rmSync(dir, { recursive: true, force: true });
});

/* --- output serialization: real checks array + token redaction --- */
t('serializeOutput: binds the ACTUAL checks array and redacts marker + receipt tokens', () => {
  const marker = GOOD;
  const checks = [{ name: 'c1_ok', pass: true, detail: { url: 'http://x/b2b/?tn_token=SECRET123&ok=1' } }];
  const out = {
    run_id: 'TN-FIX2-x', run_marker: marker, checks: [],
    cleanup: { deleted: [42], skipped_unowned: [], note: 'marker=' + marker },
  };
  const copy = H.serializeOutput(out, checks, marker);
  assert.equal(copy.checks.length, 1, 'actual checks array must be bound');
  assert.equal(copy.checks[0].name, 'c1_ok');
  assert.equal(copy.checks[0].pass, true);
  assert.ok(!JSON.stringify(copy).includes(marker), 'marker must not survive serialization');
  assert.ok(copy.run_marker === '[REDACTED]');
  assert.ok(copy.cleanup.note.includes('[REDACTED]'));
  assert.ok(!JSON.stringify(copy).includes('SECRET123'), 'token values must be redacted');
  assert.ok(copy.checks[0].detail.url.includes('tn_token=[REDACTED]'));
  assert.deepEqual(out.checks, [], 'original output object untouched');
});

/* --- journey orchestration with stubbed effects --- */
function goodEffects() {
  const calls = [];
  const owned = { id: 42, type: 'tn_ticket', email: 'acceptance-test+' + GOOD + '@example.invalid' };
  const sentinelA = { id: 51, type: 'tn_quote', email: 'acceptance-test+' + OTHER + '@example.invalid' };
  const sentinelB = { id: 52, type: 'tn_ticket', email: 'acceptance-test@example.invalid' };
  let reads = 0;
  return {
    calls, owned, sentinelA, sentinelB,
    effects: {
      preflightProbes: async () => Object.assign({}, PERFECT),
      openBrowser: async () => { calls.push('openBrowser'); return { closed: false }; },
      closeBrowser: async b => { calls.push('closeBrowser'); b.closed = true; },
      findOwnedRecords: async marker => {
        reads++;
        calls.push('findOwnedRecords#' + reads + ':' + marker);
        return reads === 1 ? [owned, sentinelA, sentinelB] : [sentinelA, sentinelB]; // owned gone after delete
      },
      submitForm: async payload => {
        calls.push('submitForm');
        return payload;
      },
      deleteOwnedRecords: async (ids, marker) => {
        calls.push('deleteOwnedRecords:' + ids.join('|') + ':' + marker);
        return { deleted: ids.slice(), skipped: [], failed: [] };
      },
    },
  };
}
t('journey: bad preflight aborts BEFORE browser/submit/DB effects', async () => {
  const calls = [];
  const res = await H.runJourney({
    marker: GOOD, expectedFixture: { home_url: FIXTURE_HOME },
    effects: {
      preflightProbes: async () => Object.assign({}, PERFECT, { mail_blocked: false }),
      openBrowser: async () => { calls.push('openBrowser'); throw new Error('MUST NOT OPEN'); },
      closeBrowser: async () => { calls.push('closeBrowser'); throw new Error('MUST NOT CLOSE'); },
      findOwnedRecords: async () => { calls.push('findOwnedRecords'); throw new Error('MUST NOT READ'); },
      deleteOwnedRecords: async () => { calls.push('deleteOwnedRecords'); throw new Error('MUST NOT DELETE'); },
      submitForm: async () => { calls.push('submitForm'); throw new Error('MUST NOT SUBMIT'); },
    },
    operation: async ctx => { await ctx.submitForm({ email: H.formEmail(GOOD) }); },
  });
  assert.equal(res.status, 'ABORTED_PREFLIGHT');
  assert.ok(res.verdict.failed.includes('mail_block_confirmed'));
  assert.deepEqual(calls, [], 'no browser/submit/DB effect may run');
  assert.deepEqual(res.effectLog, [{ effect: 'preflightProbes' }], 'only the read-only probe ran');
});
t('journey: separate fixture with IDENTICAL flags but different endpoint is aborted', async () => {
  const calls = [];
  const res = await H.runJourney({
    marker: GOOD, expectedFixture: { home_url: FIXTURE_HOME },
    effects: {
      preflightProbes: async () => Object.assign({}, PERFECT, { home: 'http://localhost:19999/' }),
      openBrowser: async () => { calls.push('openBrowser'); throw new Error('MUST NOT OPEN'); },
      closeBrowser: async () => {}, findOwnedRecords: async () => [], deleteOwnedRecords: async () => ({}),
    },
    operation: async () => {},
  });
  assert.equal(res.status, 'ABORTED_PREFLIGHT');
  assert.deepEqual(res.verdict.failed, ['fixture_identity']);
  assert.deepEqual(calls, []);
});
t('journey: missing expectedFixture is rejected (fail closed)', async () => {
  const s = goodEffects();
  const res = await H.runJourney({ marker: GOOD, effects: s.effects, operation: async () => {} });
  assert.equal(res.status, 'ABORTED_BAD_SPEC');
  assert.deepEqual(s.calls, [], 'no effects may run without an expected fixture identity');
});
t('journey: bad marker aborts before ANY effect', async () => {
  const res = await H.runJourney({
    marker: 'TNMARK-old', expectedFixture: { home_url: FIXTURE_HOME },
    effects: {
      preflightProbes: async () => PERFECT, openBrowser: async () => ({}),
      closeBrowser: async () => {}, findOwnedRecords: async () => [], deleteOwnedRecords: async () => ({}),
    },
    operation: async () => {},
  });
  assert.equal(res.status, 'ABORTED_BAD_MARKER');
  assert.deepEqual(res.effectLog, []);
});
t('journey: happy path — owned only deleted, sentinels preserved, browser closed', async () => {
  const s = goodEffects();
  const res = await H.runJourney({
    marker: GOOD, expectedFixture: { home_url: FIXTURE_HOME }, effects: s.effects,
    operation: async ctx => {
      const payload = await ctx.submitForm({ email: H.formEmail(GOOD), form: 'tn-service-request' });
      return { payload };
    },
  });
  assert.equal(res.status, 'PASSED');
  assert.ok(s.calls.includes('submitForm'));
  assert.deepEqual(res.cleanup.deleted, [42]);
  assert.equal(res.cleanup.requested, 1);
  assert.equal(res.cleanup.error, null, 'post-read must confirm owned records are gone');
  assert.deepEqual(res.cleanup.skipped_unowned.map(x => x.id), [51, 52]);
  assert.ok(res.cleanup.skipped_unowned.every(x => x.reason === 'email_marker_mismatch'));
  assert.ok(s.calls.includes('closeBrowser'), 'browser closed');
  assert.ok(s.calls.includes('findOwnedRecords#1:' + GOOD), 'pre-delete discovery');
  assert.ok(s.calls.includes('findOwnedRecords#2:' + GOOD), 'post-delete verification read');
  assert.ok(s.calls.includes('deleteOwnedRecords:42:' + GOOD), 'delete effect receives ONLY the owned id + marker');
  assert.ok(!s.calls.some(c => c.startsWith('deleteOwnedRecords:42|51')), 'sentinel ids never passed to delete');
});
t('journey: post-read finding owned records still present must FAIL cleanup', async () => {
  const s = goodEffects();
  let reads = 0;
  s.effects.findOwnedRecords = async () => { reads++; return [s.owned, s.sentinelA]; }; // owned ALWAYS found
  const res = await H.runJourney({ marker: GOOD, expectedFixture: { home_url: FIXTURE_HOME }, effects: s.effects, operation: async () => 'ok' });
  assert.equal(res.status, 'FAILED_CLEANUP');
  assert.match(String(res.cleanup.error), /owned_still_present:42/);
});
t('journey: post-read returning {malformed:true} must FAIL cleanup (never fall through to PASSED)', async () => {
  const s = goodEffects();
  let reads = 0;
  s.effects.findOwnedRecords = async () => { reads++; return reads === 1 ? [s.owned] : { malformed: true }; };
  const res = await H.runJourney({ marker: GOOD, expectedFixture: { home_url: FIXTURE_HOME }, effects: s.effects, operation: async () => 'ok' });
  assert.equal(res.status, 'FAILED_CLEANUP');
  assert.match(String(res.cleanup.error), /^post_read_non_array$/);
});
t('journey: post-read returning null must FAIL cleanup', async () => {
  const s = goodEffects();
  let reads = 0;
  s.effects.findOwnedRecords = async () => { reads++; return reads === 1 ? [s.owned] : null; };
  const res = await H.runJourney({ marker: GOOD, expectedFixture: { home_url: FIXTURE_HOME }, effects: s.effects, operation: async () => 'ok' });
  assert.equal(res.status, 'FAILED_CLEANUP');
  assert.match(String(res.cleanup.error), /^post_read_non_array$/);
});
t('journey: non-array discovery must FAIL cleanup (not silently pass)', async () => {
  const s = goodEffects();
  s.effects.findOwnedRecords = async () => ({ notAnArray: true });
  const res = await H.runJourney({ marker: GOOD, expectedFixture: { home_url: FIXTURE_HOME }, effects: s.effects, operation: async () => 'ok' });
  assert.equal(res.status, 'FAILED_CLEANUP');
  assert.match(String(res.cleanup.error), /non_array_discovery/);
});
t('journey: extra deletion beyond requested owned ids must FAIL cleanup', async () => {
  const s = goodEffects();
  s.effects.deleteOwnedRecords = async () => ({ deleted: [42, 77], skipped: [], failed: [] });
  const res = await H.runJourney({ marker: GOOD, expectedFixture: { home_url: FIXTURE_HOME }, effects: s.effects, operation: async () => 'ok' });
  assert.equal(res.status, 'FAILED_CLEANUP');
  assert.match(String(res.cleanup.error), /extra_deletion:77/);
});
t('journey: thrown operation still closes browser + owned-only cleanup', async () => {
  const s = goodEffects();
  const res = await H.runJourney({
    marker: GOOD, expectedFixture: { home_url: FIXTURE_HOME }, effects: s.effects,
    operation: async ctx => {
      await ctx.submitForm({ email: H.formEmail(GOOD) });
      throw new Error('forced operation error');
    },
  });
  assert.equal(res.status, 'FAILED_OPERATION');
  assert.equal(res.operationError, 'forced operation error');
  assert.ok(s.calls.includes('closeBrowser'), 'browser closed despite throw');
  assert.deepEqual(res.cleanup.deleted, [42], 'owned cleanup still ran');
  assert.deepEqual(res.cleanup.skipped_unowned.map(x => x.id), [51, 52], 'sentinels preserved');
});
t('journey: cleanup failure produces FAILED result (not silent success)', async () => {
  const s = goodEffects();
  s.effects.deleteOwnedRecords = async () => { throw new Error('delete failed'); };
  const res = await H.runJourney({ marker: GOOD, expectedFixture: { home_url: FIXTURE_HOME }, effects: s.effects, operation: async () => 'ok' });
  assert.equal(res.status, 'FAILED_CLEANUP');
  assert.match(String(res.cleanup.error), /^delete_failed:delete failed$/);
  assert.ok(s.calls.includes('closeBrowser'));
});
t('journey: closeBrowser failure also produces FAILED_CLEANUP; cleanup still runs', async () => {
  const s = goodEffects();
  s.effects.closeBrowser = async () => { throw new Error('close failed'); };
  const res = await H.runJourney({ marker: GOOD, expectedFixture: { home_url: FIXTURE_HOME }, effects: s.effects, operation: async () => 'ok' });
  assert.equal(res.status, 'FAILED_CLEANUP');
  assert.equal(res.closeError, 'close failed');
  assert.deepEqual(res.cleanup.deleted, [42]);
});

/* --- runner --- */
(async () => {
  let fail = 0;
  for (const [name, fn] of tests) {
    try { await fn(); console.log('PASS ' + name); }
    catch (e) { fail++; console.log('FAIL ' + name + '\n  ' + String(e && e.message || e).split('\n').join('\n  ')); }
  }
  console.log('\nTOTAL=' + tests.length + ' PASS=' + (tests.length - fail) + ' FAIL=' + fail);
  process.exitCode = fail ? 1 : 0;
})();
