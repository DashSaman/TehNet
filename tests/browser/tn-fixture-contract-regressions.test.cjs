'use strict';
/* TN-P2-ORIGINAL-DRIVER-SOURCE-GATE-20261118 — pure regressions per
 * MANAGER_REVIEW (comment 6969086962). Zero network/browser/RouterOS/DB effects;
 * Node built-ins only. Sections:
 *   A/B/C — source-consuming order/binding regressions + pure helper seams.
 *   D — ACTUAL-ENTRYPOINT harness: loads the real published driver source in a vm
 *       with every require (playwright / child_process / fs) replaced by in-memory
 *       stubs that RECORD all attempted effects. No duplicate callback: the exact
 *       published readBrowserMarker/adapter code paths execute. The pre-fix source
 *       is pinned to the reviewed SHA (99adf59…) and both reported P1 failures are
 *       reproduced against it, then asserted fixed against the current source. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const vm = require('node:vm');
const H = require('./tn-fixture-helpers.cjs');

const DRIVER_PATH = path.join(__dirname, 'tn-local-staging-fix2-driver.cjs');
const PREFIX_DRIVER_SHA = '99adf594146c90bc10010a2b1cadce6347e62878'; /* reviewed pre-fix source (permanent pin) */
const REPO_ROOT = path.join(__dirname, '..', '..');
const TEST_BASE = 'http://127.0.0.1:18085';

const DRIVER_SRC = fs.readFileSync(DRIVER_PATH, 'utf8');

const tests = [];
const t = (name, fn) => tests.push([name, fn]);

const COMPLETE_CONTRACT = {
  fixture_marker_name: 'tn_fixture_marker',
  fixture_marker_value: 'TN-RUN-dead-beef',
  app_endpoint: 'https://staging.example/',
  db_identity: 'tehnetux',
  source_fingerprints: { plugin: 'abc', theme: 'def' },
};
const clone = o => JSON.parse(JSON.stringify(o));

/* --- A: adapter eligibility (pure seam) --- */
t('adapterEligibility: incomplete contract (marker+fingerprint only) is ineligible', () => {
  const partial = { fixture_marker_name: 'n', cleanup_fingerprint_source: 'fp' };
  const e = H.adapterEligibility(partial, { ok: true, missing: [] });
  assert.equal(e.eligible, false);
  assert.ok(e.reasons.some(r => r.indexOf('incomplete_contract') >= 0), e.reasons.join(';'));
});
t('adapterEligibility: missing digests reject even a complete contract', () => {
  const e = H.adapterEligibility(clone(COMPLETE_CONTRACT), { ok: false, missing: ['index_runtime_manifest'] });
  assert.equal(e.eligible, false);
  assert.ok(e.reasons.some(r => r.indexOf('missing_or_invalid_digests') >= 0));
});
t('adapterEligibility: complete contract + ok digests is eligible (positive control)', () => {
  const e = H.adapterEligibility(clone(COMPLETE_CONTRACT), { ok: true, missing: [] });
  assert.equal(e.eligible, true, JSON.stringify(e.reasons));
});
t('adapterEligibility: null contract is ineligible (withdrawn/legacy default blocked)', () => {
  const e = H.adapterEligibility(null, { ok: true, missing: [] });
  assert.equal(e.eligible, false);
  assert.ok(e.reasons.some(r => r.indexOf('incomplete_contract') >= 0));
});

/* --- B: source-consuming order/binding regressions on the driver --- */
t('driver source: cleanupEvidence sshwp call comes AFTER adapter eligibility gate', () => {
  const elig = DRIVER_SRC.indexOf('adapter_eligibility');
  const ssh = DRIVER_SRC.indexOf('cleanupEvidence = JSON.parse(sshwp(');
  assert.ok(elig >= 0 && ssh > elig, 'eligibility gate must precede the first external adapter call');
});
t('driver source: incomplete contract path returns BEFORE the sshwp adapter call', () => {
  const gateIdx = DRIVER_SRC.indexOf("writeBlockedReceipt(eligibility.completeness.complete ? 'BLOCKED_MISSING_EVIDENCE' : 'BLOCKED_FIXTURE_OWNERSHIP')");
  const sshIdx = DRIVER_SRC.indexOf('cleanupEvidence = JSON.parse(sshwp(');
  assert.ok(gateIdx >= 0 && sshIdx > gateIdx, 'blocked receipt must be written before any adapter effect');
});
t('driver source: successful meta-path return binds the OBSERVED final URL (not hardcoded BASE)', () => {
  const rbStart = DRIVER_SRC.indexOf('readBrowserMarker: async');
  assert.ok(rbStart >= 0, 'readBrowserMarker not found');
  const rbEnd = DRIVER_SRC.indexOf('closeBrowser: async', rbStart);
  const seg = DRIVER_SRC.slice(rbStart, rbEnd);
  assert.ok(seg.indexOf('observedUrl') >= 0, 'observed final URL must be bound');
  assert.ok(seg.indexOf('return { home_url: observedUrl') >= 0, 'success path must return the observed URL');
  const successReturn = seg.indexOf('return { home_url: observedUrl');
  assert.ok(seg.slice(0, successReturn).indexOf("return { home_url: BASE + '/'") >= 0,
    'the non-meta early return may keep BASE (null marker => identity fails) — success path must NOT');
});
t('driver source: browser context closed in finally (synthetic resources closed on failure)', () => {
  const rbStart = DRIVER_SRC.indexOf('readBrowserMarker: async');
  const rbEnd = DRIVER_SRC.indexOf('closeBrowser: async', rbStart);
  const seg = DRIVER_SRC.slice(rbStart, rbEnd);
  assert.ok(seg.indexOf('finally') >= 0, 'context close must be in finally');
  assert.ok(seg.indexOf('ctx.close()') >= 0);
});
t('driver source: contract/BASE endpoint disagreement blocks before openBrowser', () => {
  const disagree = DRIVER_SRC.indexOf('BLOCKED_CONTRACT_ENDPOINT_MISMATCH');
  const open = DRIVER_SRC.indexOf('openBrowser: async');
  assert.ok(disagree >= 0 && disagree < open, 'endpoint disagreement block must precede openBrowser');
});
t('driver source: missing/throwing marker read surfaces as null value (journey blocks)', () => {
  const rbStart = DRIVER_SRC.indexOf('readBrowserMarker: async');
  const seg = DRIVER_SRC.slice(rbStart, rbStart + 900);
  assert.ok(seg.indexOf('markerValue = null') >= 0, 'markerValue must default null before the read');
});
t('driver source: blocked receipt reports actual adapter attempts (no blanket zero-effects claim)', () => {
  const wb = DRIVER_SRC.indexOf('function writeBlockedReceipt');
  const seg = DRIVER_SRC.slice(wb, wb + 1200);
  assert.ok(seg.indexOf('external_adapter_attempts') >= 0, 'receipt must carry the actual attempt counter');
  assert.ok(seg.indexOf('adapterAttempts') >= 0);
  assert.equal(seg.indexOf('zero effects executed'), -1, 'blanket zero-effects wording must be gone');
});

/* --- positive control: complete contract binding passes --- */
t('observedEndpointBindingOk: matching observed/contract/expected passes', () => {
  const v = H.observedEndpointBindingOk('https://staging.example/', 'https://staging.example/', 'https://staging.example/');
  assert.equal(v.ok, true, JSON.stringify(v.failed));
});
/* --- negatives: redirect/missing/throwing observed URL --- */
t('observedEndpointBindingOk: redirected synthetic endpoint fails', () => {
  const v = H.observedEndpointBindingOk('https://synthetic-redirect.example/', 'https://staging.example/', 'https://staging.example/');
  assert.equal(v.ok, false);
  assert.ok(v.failed.some(f => f.indexOf('mismatch') >= 0));
});
t('observedEndpointBindingOk: empty observed URL fails closed', () => {
  const v = H.observedEndpointBindingOk('', 'https://staging.example/', 'https://staging.example/');
  assert.equal(v.ok, false);
});
t('observedEndpointBindingOk: null observed URL fails closed', () => {
  const v = H.observedEndpointBindingOk(null, 'https://staging.example/', 'https://staging.example/');
  assert.equal(v.ok, false);
});

/* --- C1 contract completeness seam --- */
t('fixtureContractCompleteness: full contract complete=true', () => {
  const c = H.fixtureContractCompleteness(clone(COMPLETE_CONTRACT));
  assert.equal(c.complete, true);
  assert.deepEqual(c.missing, []);
});
t('fixtureContractCompleteness: each missing required field listed', () => {
  const c = H.fixtureContractCompleteness({});
  assert.equal(c.complete, false);
  assert.equal(c.missing.length, 5);
});
t('adapterEligibility consumes completeness (one variable at a time, no aliasing)', () => {
  const e1 = H.adapterEligibility(null, { ok: true });
  const e2 = H.adapterEligibility(clone(COMPLETE_CONTRACT), { ok: true });
  assert.equal(e1.eligible, false);
  assert.equal(e2.eligible, true);
});

/* =========================================================================
 * D — ACTUAL-ENTRYPOINT HARNESS (in-memory stubs; no network/browser/SSH/DB)
 * ========================================================================= */
let tmpContractSeq = 0;
function harnessContract(extra) {
  return Object.assign({
    fixture_marker_name: 'tn_fixture_marker',
    fixture_marker_value: 'TN-RUN-contract-beef',
    app_endpoint: TEST_BASE + '/',
    db_identity: 'tehnetux',
    source_fingerprints: { plugin: 'stub-plugin-fp', theme: 'stub-theme-fp' },
    browser_marker_source: 'meta:tn_fixture_marker',
    cleanup_fingerprint_source: 'tn_fixture_fingerprint_source',
  }, extra || {});
}

async function runDriverHarness(opts) {
  const cfg = {
    source: DRIVER_SRC,               /* source text to execute (fixed or pinned pre-fix) */
    contract: undefined,              /* undefined => no contract file (null path); object => temp file */
    failGitShowFor: null,             /* substring of git show command to fail (missing digest) */
    finalUrl: TEST_BASE + '/',        /* observed final URL the synthetic page reports */
    markerValue: null,                /* meta marker value the synthetic DOM reports */
    gotoThrows: false,                /* synthetic navigation throws (read failure path) */
    ...opts,
  };
  const calls = [];
  const receipts = {};
  const rec = (kind, extra) => calls.push(Object.assign({ kind }, extra || {}));

  /* execSync stub: local git reads answered in-memory; ANY docker/adapter command is
   * recorded; unexpected commands throw so an unexpected adapter call fails the test. */
  const execStub = (cmd) => {
    const c = String(cmd);
    if (/^git rev-parse\b/.test(c)) { rec('exec', { cmd: c, note: 'local git read' }); return '9'.repeat(40) + '\n'; }
    if (/^git show\b/.test(c)) {
      rec('exec', { cmd: c, note: 'local git read' });
      if (cfg.failGitShowFor && c.indexOf(cfg.failGitShowFor) >= 0) throw new Error('git show failed (harness-injected missing digest)');
      return 'stub-blob-content\n';
    }
    if (c.indexOf('docker exec') >= 0) {
      if (c.indexOf('transient delete') >= 0) { rec('exec', { cmd: c, note: 'external transient delete' }); return ''; }
      /* the wp-cli eval-file payload is base64-embedded — decode before sniffing */
      const b64 = /echo ([A-Za-z0-9+/=]+) \| base64 -d/.exec(c);
      const php = b64 ? Buffer.from(b64[1], 'base64').toString('utf8') : c;
      rec('exec', { cmd: c, php });
      if (php.indexOf('wp_count_posts') >= 0) return '{"n":0}';
      if (php.indexOf('get_post(') >= 0) return '{"missing":true}';
      if (php.indexOf('wp_get_environment_type') >= 0) {
        return JSON.stringify({ home: TEST_BASE + '/', db_name: 'tehnetux', env: 'staging', blog_public: '0',
          mail_blocked: true, http_blocked: true, cron_disabled: true, http_probe_blocked: true, payments_disabled: true });
      }
      if (php.indexOf('get_option') >= 0) {
        return JSON.stringify({ db_name: 'tehnetux', fixture_marker_name: cfg.contract.fixture_marker_name,
          fixture_marker_value: cfg.contract.fixture_marker_value, source_fingerprints: cfg.contract.source_fingerprints });
      }
      if (php.indexOf('_tn_email') >= 0) return '[]';
    } else {
      rec('exec', { cmd: c });
    }
    throw new Error('UNEXPECTED_ADAPTER_CALL: ' + c.slice(0, 120));
  };

  /* page stub: the MARKER page (first context) reports the case's final URL and
   * marker value; operation pages answer minimally and lack every other method
   * (accessing one throws, surfacing any unexpected synthetic-page dependency). */
  const makePage = (isMarkerPage, pageIndex) => {
    const base = {
      on: () => null,
      url: () => { rec('page-url', { pageIndex, isMarkerPage }); return isMarkerPage ? cfg.finalUrl : (TEST_BASE + '/'); },
      goto: async (u) => { rec('goto', { u: String(u), pageIndex, isMarkerPage }); if (cfg.gotoThrows && isMarkerPage) throw new Error('synthetic navigation failure'); return { status: () => 200 }; },
      evaluate: async () => { rec('evaluate', { pageIndex, isMarkerPage }); return isMarkerPage ? cfg.markerValue : null; },
    };
    return new Proxy(base, { get(t, p) {
      if (Object.prototype.hasOwnProperty.call(t, p)) return t[p];
      if (typeof p === 'symbol' || p === 'then') return undefined;
      throw new Error('SYNTHETIC_PAGE_NO_METHOD:' + String(p));
    } });
  };

  let ctxSeq = 0;
  const chromiumStub = { launch: async () => {
    rec('browser-launch');
    return {
      version: async () => 'SyntheticChromium/0-pure-harness',
      newContext: async () => {
        ctxSeq += 1; const idx = ctxSeq; rec('ctx-create', { idx });
        return {
          newPage: async () => { rec('page-create', { idx }); return makePage(idx === 1, idx); },
          close: async () => { rec('ctx-close', { idx }); },
        };
      },
      close: async () => { rec('browser-close'); },
    };
  } };

  const fsStub = {
    readFileSync: (p, enc) => { rec('fs-read', { p: String(p).slice(0, 160) }); return fs.readFileSync(p, enc); },
    writeFileSync: (p, content) => { rec('fs-write', { p: String(p) }); receipts[String(p)] = String(content); },
  };

  const stubRequire = (spec) => {
    if (spec === 'playwright') return { chromium: chromiumStub };
    if (spec === 'node:child_process') return { execSync: execStub };
    if (spec === 'node:fs') return fsStub;
    const resolved = (spec.charAt(0) === '.') ? path.resolve(__dirname, spec) : spec;
    return require(resolved);
  };

  /* Load the EXACT source with only its async invocation prefixed by `return`
   * (same minimal transform the reviewer used) so the wrapper can await it. */
  const opener = '(async () => {';
  assert.equal(cfg.source.split(opener).length - 1, 1, 'driver opener must be unique before the harness patch');
  const patched = cfg.source.replace(opener, 'return ' + opener);
  const runner = vm.runInThisContext(
    '(async (require, __dirname, __filename) => {\n' + patched + '\n})',
    { filename: 'tn-local-staging-fix2-driver(actual-published-source)' });

  let contractPath = null;
  if (cfg.contract) {
    contractPath = path.join(os.tmpdir(), 'tn-harness-contract-' + process.pid + '-' + (++tmpContractSeq) + '.json');
    fs.writeFileSync(contractPath, JSON.stringify(cfg.contract), 'utf8');
  }

  const prevBase = process.env.TN_BROWSER_BASE, prevContractPath = process.env.TN_FIXTURE_CONTRACT_PATH;
  const prevExit = process.exitCode;
  const origLog = console.log; const logs = [];
  console.log = (...a) => { logs.push(a.map(String).join(' ')); };
  const startedUtc = new Date().toISOString();
  let err = null;
  process.exitCode = undefined;
  try {
    process.env.TN_BROWSER_BASE = TEST_BASE;
    process.env.TN_FIXTURE_CONTRACT_PATH = contractPath || '';
    await runner(stubRequire, __dirname, DRIVER_PATH);
  } catch (e) { err = e; }
  finally {
    console.log = origLog;
    if (prevBase === undefined) delete process.env.TN_BROWSER_BASE; else process.env.TN_BROWSER_BASE = prevBase;
    if (prevContractPath === undefined) delete process.env.TN_FIXTURE_CONTRACT_PATH; else process.env.TN_FIXTURE_CONTRACT_PATH = prevContractPath;
    if (contractPath) { try { fs.unlinkSync(contractPath); } catch (e) { /* best effort */ } }
  }
  const exitCode = process.exitCode;
  process.exitCode = prevExit;

  const count = (pred) => calls.filter(pred).length;
  const execHas = (s) => count(c => c.kind === 'exec' && (c.cmd.indexOf(s) >= 0 || (typeof c.php === 'string' && c.php.indexOf(s) >= 0)));
  const stats = {
    adapterCalls: execHas('docker exec'),
    wpEvalFileAttempts: execHas('eval-file'),
    remoteTempWrites: execHas('base64 -d > /tmp/'),
    transientDeletes: execHas('transient delete'),
    dbCountCalls: execHas('wp_count_posts'),
    findOwnedCalls: execHas('_tn_email'),
    browserLaunches: count(c => c.kind === 'browser-launch'),
    markerPageUrlReads: count(c => c.kind === 'page-url' && c.isMarkerPage),
    browserCloses: count(c => c.kind === 'browser-close'),
    ctxCloses: count(c => c.kind === 'ctx-close'),
  };
  return { stats, receipts, calls, logs, err, exitCode: exitCode === undefined ? null : exitCode, startedUtc };
}

function blockedReceiptAssertions(r, status) {
  assert.equal(r.err, null, 'driver must not crash: ' + (r.err && r.err.message));
  assert.equal(r.receipts['fix2-clean-error.json'], undefined, 'no crash receipt expected');
  const receipt = JSON.parse(r.receipts['fix2-clean-result.json']);
  assert.equal(receipt.status, status);
  assert.ok(receipt.journey, 'journey block required in receipt');
  assert.equal(receipt.journey.status, status);
  return receipt;
}

/* D1 — no contract at all: withdrawn/legacy default stays unreachable with ZERO effects */
t('harness(actual entrypoint): no contract => BLOCKED_FIXTURE_OWNERSHIP, zero external adapter/browser effects', async () => {
  const r = await runDriverHarness({ contract: undefined });
  const receipt = blockedReceiptAssertions(r, 'BLOCKED_FIXTURE_OWNERSHIP');
  assert.equal(r.stats.adapterCalls, 0, 'no external adapter call may be attempted: ' + JSON.stringify(r.stats));
  assert.equal(r.stats.remoteTempWrites, 0, 'no remote temp-file write may be attempted');
  assert.equal(r.stats.browserLaunches, 0);
  assert.equal(receipt.journey.external_adapter_attempts, 0);
  assert.equal(receipt.journey.browser_launches, 0);
  assert.ok(/blocked before openBrowser/.test(receipt.journey.note), receipt.journey.note);
  assert.equal(r.exitCode, 1);
});

/* D2 — the manager's exact P1 counterexample: incomplete contract (marker+fingerprint only) */
t('harness(actual entrypoint): incomplete contract => zero adapter calls, no remote temp write, blocked receipt', async () => {
  const r = await runDriverHarness({
    contract: { fixture_marker_name: 'n', cleanup_fingerprint_source: 'fp' },
  });
  const receipt = blockedReceiptAssertions(r, 'BLOCKED_FIXTURE_OWNERSHIP');
  assert.equal(r.stats.adapterCalls, 0, 'legacy external adapter must NOT be reached');
  assert.equal(r.stats.wpEvalFileAttempts, 0);
  assert.equal(r.stats.remoteTempWrites, 0);
  assert.equal(r.stats.browserLaunches, 0);
  assert.equal(receipt.journey.external_adapter_attempts, 0);
  const elig = receipt.checks.find(c => c.name === 'adapter_eligibility');
  assert.ok(elig && elig.pass === false, 'eligibility check recorded as failing');
  assert.equal(r.exitCode, 1);
});

/* D3 — complete contract but a missing required digest */
t('harness(actual entrypoint): missing required digest => BLOCKED_MISSING_EVIDENCE, zero adapter/browser effects', async () => {
  const r = await runDriverHarness({
    contract: harnessContract(),
    failGitShowFor: 'class-index-policy.php',
  });
  const receipt = blockedReceiptAssertions(r, 'BLOCKED_MISSING_EVIDENCE');
  assert.equal(r.stats.adapterCalls, 0);
  assert.equal(r.stats.remoteTempWrites, 0);
  assert.equal(r.stats.browserLaunches, 0);
  assert.equal(receipt.journey.external_adapter_attempts, 0);
  assert.equal(r.exitCode, 1);
});

/* D4 — contract/BASE endpoint disagreement blocks BEFORE openBrowser (one read-only
 * cleanup-evidence probe may have run; receipt reports it honestly) */
t('harness(actual entrypoint): contract endpoint != BASE => BLOCKED_CONTRACT_ENDPOINT_MISMATCH before openBrowser', async () => {
  const r = await runDriverHarness({ contract: harnessContract({ app_endpoint: 'http://fixture-elsewhere.invalid/' }) });
  const receipt = blockedReceiptAssertions(r, 'BLOCKED_CONTRACT_ENDPOINT_MISMATCH');
  assert.equal(r.stats.browserLaunches, 0, 'no browser may be launched');
  assert.equal(r.stats.dbCountCalls, 0, 'no operation effect');
  assert.equal(r.stats.findOwnedCalls, 0, 'no discovery effect');
  assert.equal(r.stats.transientDeletes, 0);
  assert.equal(r.stats.adapterCalls, 1, 'only the single cleanup-evidence probe');
  assert.equal(receipt.journey.external_adapter_attempts, 1, 'receipt reports the actual attempt count');
  assert.equal(r.exitCode, 1);
});

/* D5 — redirected final URL with a matching marker: identity must block, zero
 * operation/submit/discovery/delete; synthetic context closed */
t('harness(actual entrypoint): redirected final URL => BLOCKED_IDENTITY (browser_endpoint), zero operation/discovery/delete', async () => {
  const r = await runDriverHarness({
    contract: harnessContract(),
    finalUrl: 'http://redirected-target.invalid/',
    markerValue: 'TN-RUN-contract-beef',
  });
  assert.equal(r.err, null);
  const receipt = JSON.parse(r.receipts['fix2-clean-result.json']);
  assert.equal(receipt.journey.status, 'BLOCKED_IDENTITY');
  const logNames = (receipt.journey.effect_log || []).map(e => e.effect);
  assert.ok(logNames.indexOf('closeBrowser') >= 0, 'browser closed after identity failure');
  assert.equal(logNames.indexOf('findOwnedRecords'), -1, 'no discovery after identity failure');
  assert.equal(logNames.indexOf('deleteOwnedRecords'), -1, 'no delete after identity failure');
  assert.equal(r.stats.dbCountCalls, 0, 'operation (baseline counting) must not run');
  assert.equal(r.stats.findOwnedCalls, 0, 'no discovery adapter call');
  assert.equal(r.stats.browserLaunches, 1);
  assert.ok(r.stats.ctxCloses >= 1, 'marker context closed in finally');
  assert.equal(r.stats.markerPageUrlReads >= 1, true, 'the OBSERVED final URL was actually read');
  assert.equal(r.exitCode, 1);
});

/* D6 — throwing navigation: blocked identity, resources closed, zero mutation */
t('harness(actual entrypoint): throwing marker navigation => BLOCKED_IDENTITY, zero operation/discovery/delete', async () => {
  const r = await runDriverHarness({ contract: harnessContract(), gotoThrows: true, markerValue: 'TN-RUN-contract-beef' });
  assert.equal(r.err, null);
  const receipt = JSON.parse(r.receipts['fix2-clean-result.json']);
  assert.equal(receipt.journey.status, 'BLOCKED_IDENTITY');
  assert.equal(r.stats.dbCountCalls, 0);
  assert.equal(r.stats.findOwnedCalls, 0);
  assert.equal(r.stats.transientDeletes, 0);
  assert.ok(r.stats.ctxCloses >= 1, 'context closed even on the throwing path');
  assert.equal(r.stats.browserCloses, 1, 'journey closed the browser');
});

/* D7 — missing marker value: blocked identity, zero mutation */
t('harness(actual entrypoint): null marker value => BLOCKED_IDENTITY, zero operation/discovery/delete', async () => {
  const r = await runDriverHarness({ contract: harnessContract(), markerValue: null });
  assert.equal(r.err, null);
  const receipt = JSON.parse(r.receipts['fix2-clean-result.json']);
  assert.equal(receipt.journey.status, 'BLOCKED_IDENTITY');
  assert.equal(r.stats.dbCountCalls, 0);
  assert.equal(r.stats.findOwnedCalls, 0);
  assert.equal(r.stats.transientDeletes, 0);
  assert.equal(r.stats.browserLaunches, 1);
});

/* D8 — positive control: matching observed URL + matching marker => journey PASSED
 * with operation/discovery actually enabled */
t('harness(actual entrypoint): matching observed URL + marker => PASSED, operation/discovery enabled', async () => {
  const r = await runDriverHarness({ contract: harnessContract(), markerValue: 'TN-RUN-contract-beef' });
  assert.equal(r.err, null);
  assert.equal(r.receipts['fix2-clean-error.json'], undefined);
  const receipt = JSON.parse(r.receipts['fix2-clean-result.json']);
  assert.equal(receipt.journey.status, 'PASSED', 'journey must pass on the matching control');
  assert.equal(r.stats.browserLaunches, 1);
  assert.ok(r.stats.dbCountCalls >= 2, 'operation ran (baseline + final counts)');
  assert.ok(r.stats.findOwnedCalls >= 1, 'discovery ran');
  const logNames = (receipt.journey.effect_log || []).map(e => e.effect);
  for (const k of ['preflightProbes', 'openBrowser', 'readBrowserMarker', 'closeBrowser', 'findOwnedRecords']) {
    assert.ok(logNames.indexOf(k) >= 0, 'effect log must include ' + k + ': ' + JSON.stringify(logNames));
  }
  assert.equal(receipt.journey.operation_error, null);
});

/* D9 — REPRODUCER of manager P1 #1 against the PINNED pre-fix source (99adf59…):
 * the incomplete contract reached the legacy external adapter (remote temp write)
 * before any completeness gate, and the receipt still claimed "zero effects". */
t('reproducer(pinned 99adf59 source): incomplete contract reached legacy adapter with a remote temp write + dishonest receipt', async () => {
  const prefix = require('node:child_process').execSync(
    'git show ' + PREFIX_DRIVER_SHA + ':tests/browser/tn-local-staging-fix2-driver.cjs',
    { encoding: 'utf8', maxBuffer: 8 * 1024 * 1024, cwd: REPO_ROOT });
  const r = await runDriverHarness({
    source: prefix,
    contract: { fixture_marker_name: 'n', cleanup_fingerprint_source: 'fp' },
  });
  assert.equal(r.err, null);
  const receipt = JSON.parse(r.receipts['fix2-clean-result.json']);
  assert.equal(receipt.status, 'BLOCKED_FIXTURE_OWNERSHIP');
  assert.ok(r.stats.adapterCalls >= 1, 'pre-fix: the external adapter WAS reached');
  assert.ok(r.stats.remoteTempWrites >= 1, 'pre-fix: a remote temp-file write WAS requested');
  assert.ok(r.stats.browserLaunches === 0);
  assert.equal(receipt.journey.note.indexOf('zero effects executed'), 0, 'pre-fix receipt claimed zero effects despite the adapter call');
});

/* D10 — REPRODUCER of manager P1 #2 against the PINNED pre-fix source: the marker
 * adapter manufactured endpoint evidence (hardcoded BASE, page.url() never read),
 * so a redirected final URL still PASSED with operation/discovery enabled. */
t('reproducer(pinned 99adf59 source): redirected final URL still PASSED (observed URL never read)', async () => {
  const prefix = require('node:child_process').execSync(
    'git show ' + PREFIX_DRIVER_SHA + ':tests/browser/tn-local-staging-fix2-driver.cjs',
    { encoding: 'utf8', maxBuffer: 8 * 1024 * 1024, cwd: REPO_ROOT });
  const r = await runDriverHarness({
    source: prefix,
    contract: harnessContract(),
    finalUrl: 'http://redirected-target.invalid/',
    markerValue: 'TN-RUN-contract-beef',
  });
  assert.equal(r.err, null);
  const receipt = JSON.parse(r.receipts['fix2-clean-result.json']);
  assert.equal(receipt.journey.status, 'PASSED', 'pre-fix: redirect with matching marker must reproduce the false PASSED');
  assert.equal(r.stats.markerPageUrlReads, 0, 'pre-fix: page.url() was never called');
  assert.ok(r.stats.browserLaunches >= 1);
  assert.ok(r.stats.dbCountCalls >= 2, 'pre-fix: operation ran on the redirected target');
  assert.ok(r.stats.findOwnedCalls >= 1, 'pre-fix: discovery ran');
});

let fail = 0;
(async () => {
  for (const [name, fn] of tests) {
    try { await fn(); console.log('PASS ' + name); }
    catch (e) { fail++; console.log('FAIL ' + name + '\n  ' + String(e && e.message || e).split('\n').join('\n  ')); }
  }
  console.log('\nTOTAL=' + tests.length + ' PASS=' + (tests.length - fail) + ' FAIL=' + fail);
  process.exitCode = fail ? 1 : 0;
})();
