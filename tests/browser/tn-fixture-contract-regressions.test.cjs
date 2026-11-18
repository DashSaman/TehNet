'use strict';
/* TN-P2-DRIVER-REMAINING-ACCEPTANCE-20261118 — pure regressions per
 * MANAGER_REVIEW 6969817290 (supersedes the 6969086962 round; preserves its accepted
 * fixes). Zero network/browser/RouterOS/DB effects; Node built-ins only. Sections:
 *   A/B/C — source-consuming order/binding regressions + pure helper seams.
 *   D — ACTUAL-ENTRYPOINT harness: loads the real published driver source in a vm
 *       with every require replaced by in-memory stubs that RECORD all attempted
 *       effects. No duplicate callback: the exact published readBrowserMarker and
 *       adapter gating execute. The pre-fix source stays pinned to the reviewed SHA
 *       (99adf59…) for the two historical reproducers.
 * KEY ACCEPTANCE (6969817290): a complete contract + digests NEVER qualifies an
 * adapter — the default withdrawn route makes ZERO external attempts, endpoint
 * disagreement blocks BEFORE any attempt, the positive path exists ONLY through an
 * explicitly injected synthetic qualified adapter, and the observed final URL is
 * consumed FAIL-CLOSED (no BASE fallback). */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const vm = require('node:vm');
const H = require('./tn-fixture-helpers.cjs');

const DRIVER_PATH = path.join(__dirname, 'tn-local-staging-fix2-driver.cjs');
const SEAM_PATH = path.join(__dirname, 'tn-fix2-adapter-seam.cjs');
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
t('adapterEligibility: eligibility NEVER asserts adapter qualification (contract boolean cannot qualify)', () => {
  /* 6969817290 #1: eligibility is only contract-shape + digest readiness — it carries no
   * notion of a qualified adapter, so no contract field can act as one. */
  const e = H.adapterEligibility(Object.assign(clone(COMPLETE_CONTRACT), { adapter_qualified: true, qualified: true }), { ok: true, missing: [] });
  assert.equal(Object.prototype.hasOwnProperty.call(e, 'qualified'), false);
  assert.equal(JSON.stringify(e.reasons), '[]');
});

/* --- B: source-consuming order/binding regressions on the driver --- */
t('driver source: eligibility gate precedes endpoint gate precedes adapter qualification precedes first adapter use', () => {
  const elig = DRIVER_SRC.indexOf('adapter_eligibility');
  const disagree = DRIVER_SRC.indexOf('BLOCKED_CONTRACT_ENDPOINT_MISMATCH');
  const qual = DRIVER_SRC.indexOf('BLOCKED_NO_QUALIFIED_ADAPTER');
  const firstUse = DRIVER_SRC.indexOf('aCleanupEvidence(FIXTURE_CONTRACT)');
  assert.ok(elig >= 0 && elig < disagree, 'eligibility must precede the endpoint gate');
  assert.ok(disagree >= 0 && disagree < qual, 'endpoint gate must precede adapter qualification');
  assert.ok(qual >= 0 && qual < firstUse, 'adapter qualification must precede the first adapter use');
});
t('driver source: ineligible path returns BEFORE the adapter seam is loaded', () => {
  const gateIdx = DRIVER_SRC.indexOf("writeBlockedReceipt(eligibility.completeness.complete ? 'BLOCKED_MISSING_EVIDENCE' : 'BLOCKED_FIXTURE_OWNERSHIP')");
  const loadIdx = DRIVER_SRC.indexOf('function loadAdapter');
  const callIdx = DRIVER_SRC.indexOf('const adapter = loadAdapter()');
  assert.ok(gateIdx >= 0 && loadIdx >= 0 && callIdx > loadIdx);
  assert.ok(gateIdx < callIdx, 'ineligible path must return before any adapter load/use');
});
t('driver source: NO legacy adapter route remains (no SSH/docker/wp-cli command material)', () => {
  assert.equal(DRIVER_SRC.indexOf('ssh netauto-main'), -1, 'ssh target constant must be gone');
  assert.equal(DRIVER_SRC.indexOf('docker exec'), -1, 'docker command material must be gone');
  assert.equal(DRIVER_SRC.indexOf('wp-cli.phar'), -1, 'wp-cli command material must be gone');
  assert.equal(DRIVER_SRC.indexOf('function sshwp'), -1, 'implicit sshwp adapter must be gone');
});
t('driver source: successful meta-path return binds the OBSERVED final URL with NO BASE fallback', () => {
  const rbStart = DRIVER_SRC.indexOf('readBrowserMarker: async');
  assert.ok(rbStart >= 0, 'readBrowserMarker not found');
  const rbEnd = DRIVER_SRC.indexOf('closeBrowser: async', rbStart);
  const seg = DRIVER_SRC.slice(rbStart, rbEnd);
  assert.ok(seg.indexOf('observedUrl') >= 0, 'observed final URL must be bound');
  assert.ok(seg.indexOf('return { home_url: observedUrl') >= 0, 'success path must return the observed URL');
  assert.equal(seg.indexOf('observedUrl ||'), -1, 'the BASE fallback must be gone (6969817290 #2)');
  assert.ok(seg.indexOf("home_url: null") >= 0, 'missing/empty observed URL must yield null home_url (fail closed)');
});
t('driver source: browser context closed in finally (synthetic resources closed on failure)', () => {
  const rbStart = DRIVER_SRC.indexOf('readBrowserMarker: async');
  const rbEnd = DRIVER_SRC.indexOf('closeBrowser: async', rbStart);
  const seg = DRIVER_SRC.slice(rbStart, rbEnd);
  assert.ok(seg.indexOf('finally') >= 0, 'context close must be in finally');
  assert.ok(seg.indexOf('ctx.close()') >= 0);
});
t('driver source: contract/BASE endpoint disagreement blocks before openBrowser AND before the adapter seam load', () => {
  const disagree = DRIVER_SRC.indexOf('BLOCKED_CONTRACT_ENDPOINT_MISMATCH');
  const loadIdx = DRIVER_SRC.indexOf('const adapter = loadAdapter()');
  const open = DRIVER_SRC.indexOf('openBrowser: async');
  assert.ok(disagree >= 0 && disagree < loadIdx, 'endpoint disagreement must block before the adapter seam is even loaded');
  assert.ok(disagree < open, 'endpoint disagreement block must precede openBrowser');
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
/* Explicitly injected synthetic QUALIFIED adapter — the ONLY positive path
 * (MANAGER_REVIEW 6969817290 #1). Pure in-memory; records every invocation into the
 * supplied sink array (merged into harness stats). */
function syntheticQualifiedAdapter(sink, contract, opts) {
  opts = opts || {};
  const rec = (kind, extra) => { sink.push(Object.assign({ kind }, extra || {})); };
  const findQueue = Array.isArray(opts.findOwnedQueue) ? opts.findOwnedQueue.slice() : null;
  return {
    qualified: true,
    reason: 'synthetic-injected-for-positive-control',
    cleanupEvidence: (c) => { rec('adapter-cleanupEvidence'); return {
      db_name: c.db_identity, fixture_marker_name: c.fixture_marker_name,
      fixture_marker_value: c.fixture_marker_value, source_fingerprints: c.source_fingerprints }; },
    preflightProbes: () => { rec('adapter-preflightProbes'); return {
      home: TEST_BASE + '/', db_name: 'tehnetux', env: 'staging', blog_public: '0',
      mail_blocked: true, http_blocked: true, cron_disabled: true,
      http_probe_blocked: true, payments_disabled: true }; },
    findOwned: () => { rec('adapter-findOwned'); return (findQueue && findQueue.length) ? findQueue.shift() : []; },
    deleteOwned: () => { rec('adapter-deleteOwned'); return opts.deleteOwnedResult || { deleted: [], failed: [], skipped: [] }; },
    countRecords: () => { rec('adapter-countRecords'); return 0; },
    recordDetail: () => { rec('adapter-recordDetail'); return opts.recordDetailResult || { missing: true }; },
    clearReceiptTransients: (tokens) => {
      rec('adapter-clearReceiptTransients', { tokensCount: Array.isArray(tokens) ? tokens.length : -1 });
      return { cleared: tokens.length * 2, requested: tokens.length };
    },
  };
}
/* Rich synthetic OPERATION page (only for the token-capture control): executes the
 * c1 keyboard flow far enough to capture a receipt token into private memory, then
 * fails late (waitForSelector) so the control proves scoped cleanup runs after a
 * later operation failure. Pure in-memory; the driver's real logic consumes it. */
function makeRichOperationPage(rec) {
  const TOKEN = 'feedface1234';
  let evalCount = 0, urlCount = 0;
  const page = {
    on: (ev, handler) => { rec('rich-page-on', { ev });
      if (ev === 'response') handler({
        status: () => 302,
        headers: () => ({ location: TEST_BASE + '/services/network-setup-tehran/?tn_ticket=sent&tn_service_receipt=' + TOKEN }),
        request: () => ({ method: () => 'POST' }),
      });
      return null;
    },
    url: () => { urlCount++; rec('page-url', { rich: true });
      return urlCount === 1
        ? (TEST_BASE + '/services/network-setup-tehran/?tn_service_context=server-scoping')
        : (TEST_BASE + '/services/network-setup-tehran/?tn_ticket=sent&tn_service_receipt=' + TOKEN); },
    goto: async () => ({ status: () => 200 }),
    evaluate: async () => { evalCount++;
      if (evalCount === 1) return { tag: 'A', href: TEST_BASE + '/services/network-setup-tehran/?tn_service_context=server-scoping' };
      if (evalCount === 2) return 'server-scoping';
      return '\u062f\u0631\u062e\u0648\u0627\u0633\u062a \u0634\u0645\u0627 \u062b\u0628\u062a \u0634\u062f TN-777'; },
    keyboard: { press: async () => {}, type: async () => {} },
    locator: () => ({ first: () => ({ focus: async () => {} }) }),
    waitForNavigation: async () => {},
    waitForSelector: async () => { throw new Error('synthetic receipt-selector failure after token capture'); },
  };
  return new Proxy(page, { get(t, p) {
    if (Object.prototype.hasOwnProperty.call(t, p)) return t[p];
    if (typeof p === 'symbol' || p === 'then') return undefined;
    throw new Error('RICH_PAGE_NO_METHOD:' + String(p));
  } });
}
async function runDriverHarness(opts) {
  const cfg = {
    source: DRIVER_SRC,               /* source text to execute (fixed or pinned pre-fix) */
    contract: undefined,              /* undefined => no contract file (null path); object => temp file */
    adapter: undefined,               /* undefined => the REAL seam module (disabled default); object => injected */
    extraCalls: null,                 /* sink array from an injected adapter, merged into stats */
    failGitShowFor: null,             /* substring of git show command to fail (missing digest) */
    legacyAdapterCommands: false,     /* true ONLY for pinned pre-fix reproducers (old source ssh's directly) */
    finalUrl: TEST_BASE + '/',        /* observed final URL the synthetic marker page reports */
    markerValue: null,                /* meta marker value the synthetic DOM reports */
    gotoThrows: false,                /* synthetic navigation throws (read failure path) */
    urlThrows: false,                 /* synthetic page.url() throws (observed-URL failure path) */
    richCtxIndex: null,              /* operation-context index served by the rich synthetic page (token-capture control) */
    ...opts,
  };
  const calls = [];
  const receipts = {};
  const rec = (kind, extra) => calls.push(Object.assign({ kind }, extra || {}));

  /* execSync stub: local git reads answered in-memory. From the FIXED source, docker/ssh
   * commands are IMPOSSIBLE (the implicit adapter is gone) — any such command throws and
   * fails the test. The legacy sniffing answers ONLY for the pinned pre-fix reproducers. */
  const execStub = (cmd) => {
    const c = String(cmd);
    if (/^git rev-parse\b/.test(c)) { rec('exec', { cmd: c, note: 'local git read' }); return '9'.repeat(40) + '\n'; }
    if (/^git show\b/.test(c)) {
      rec('exec', { cmd: c, note: 'local git read' });
      if (cfg.failGitShowFor && c.indexOf(cfg.failGitShowFor) >= 0) throw new Error('git show failed (harness-injected missing digest)');
      return 'stub-blob-content\n';
    }
    /* decode the base64-embedded wp-cli payload BEFORE recording, so the recorded
     * exec carries the decoded php for content-level assertions */
    const b64 = /echo ([A-Za-z0-9+/=]+) \| base64 -d/.exec(c);
    const php = b64 ? Buffer.from(b64[1], 'base64').toString('utf8') : null;
    rec('exec', { cmd: c, php: php || undefined, note: php ? 'external adapter attempt (decoded payload bound)' : 'external command attempt' });
    if (!cfg.legacyAdapterCommands) {
      throw new Error('UNEXPECTED_EXTERNAL_COMMAND_FROM_FIXED_SOURCE: ' + c.slice(0, 120));
    }
    /* legacy answering ONLY for the pinned pre-fix source (its own implicit sshwp) */
    if (c.indexOf('docker exec') >= 0) {
      if (c.indexOf('transient delete') >= 0) return '';
      const body = php || c;
      if (body.indexOf('wp_count_posts') >= 0) return '{"n":0}';
      if (body.indexOf('get_post(') >= 0) return '{"missing":true}';
      if (body.indexOf('wp_get_environment_type') >= 0) {
        return JSON.stringify({ home: TEST_BASE + '/', db_name: 'tehnetux', env: 'staging', blog_public: '0',
          mail_blocked: true, http_blocked: true, cron_disabled: true, http_probe_blocked: true, payments_disabled: true });
      }
      if (body.indexOf('get_option') >= 0) {
        return JSON.stringify({ db_name: 'tehnetux', fixture_marker_name: cfg.contract.fixture_marker_name,
          fixture_marker_value: cfg.contract.fixture_marker_value, source_fingerprints: cfg.contract.source_fingerprints });
      }
      if (body.indexOf('_tn_email') >= 0) return '[]';
    }
    throw new Error('UNEXPECTED_ADAPTER_CALL: ' + c.slice(0, 120));
  };

  /* page stub: the MARKER page (first context) reports the case's final URL and
   * marker value; operation pages answer minimally and lack every other method
   * (accessing one throws, surfacing any unexpected synthetic-page dependency). */
  const makePage = (isMarkerPage, pageIndex) => {
    if (cfg.richCtxIndex === pageIndex) return makeRichOperationPage((k, x) => calls.push(Object.assign({ kind: k }, x || {})));
    const base = {
      on: () => null,
      url: () => {
        rec('page-url', { pageIndex, isMarkerPage });
        if (cfg.urlThrows && isMarkerPage) throw new Error('synthetic page.url() failure');
        return isMarkerPage ? cfg.finalUrl : (TEST_BASE + '/');
      },
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
    /* adapter seam: injected ONLY when the case supplies one; otherwise the REAL
     * module loads (disabled default = withdrawn route). */
    if (resolved === SEAM_PATH && cfg.adapter) return cfg.adapter;
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

  const allCalls = calls.concat(Array.isArray(cfg.extraCalls) ? cfg.extraCalls : []);
  const count = (pred) => allCalls.filter(pred).length;
  const execHas = (s) => count(c => c.kind === 'exec' && (c.cmd.indexOf(s) >= 0 || (typeof c.php === 'string' && c.php.indexOf(s) >= 0)));
  const adapterMethodCalls = count(c => c.kind.indexOf('adapter-') === 0);
  const stats = {
    adapterMethodCalls,
    adapterCalls: execHas('docker exec'),
    legacyDiscoveryCalls: execHas('_tn_email'),
    remoteTempWrites: execHas('base64 -d > /tmp/'),
    transientDeletes: execHas('transient delete'),
    operationCountCalls: count(c => c.kind === 'adapter-countRecords'),
    discoveryCalls: count(c => c.kind === 'adapter-findOwned'),
    deleteCalls: count(c => c.kind === 'adapter-deleteOwned'),
    transientClearCalls: count(c => c.kind === 'adapter-clearReceiptTransients'),
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
  assert.equal(r.stats.adapterMethodCalls, 0, 'no adapter invocation may occur');
  assert.equal(r.stats.adapterCalls, 0);
  assert.equal(r.stats.remoteTempWrites, 0);
  assert.equal(r.stats.browserLaunches, 0);
  assert.equal(receipt.journey.external_adapter_attempts, 0);
  assert.equal(receipt.journey.browser_launches, 0);
  assert.ok(/blocked before openBrowser/.test(receipt.journey.note), receipt.journey.note);
  assert.equal(r.exitCode, 1);
});

/* D2 — the historical P1 counterexample: incomplete contract (marker+fingerprint only) */
t('harness(actual entrypoint): incomplete contract => zero adapter calls, no remote temp write, blocked receipt', async () => {
  const r = await runDriverHarness({
    contract: { fixture_marker_name: 'n', cleanup_fingerprint_source: 'fp' },
  });
  const receipt = blockedReceiptAssertions(r, 'BLOCKED_FIXTURE_OWNERSHIP');
  assert.equal(r.stats.adapterMethodCalls, 0);
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
  assert.equal(r.stats.adapterMethodCalls, 0);
  assert.equal(r.stats.remoteTempWrites, 0);
  assert.equal(r.stats.browserLaunches, 0);
  assert.equal(receipt.journey.external_adapter_attempts, 0);
  assert.equal(r.exitCode, 1);
});

/* D4 (6969817290 #1) — contract/BASE endpoint disagreement blocks with ZERO external
 * attempts (previously one cleanup-evidence upload preceded the block) */
t('harness(actual entrypoint): contract endpoint != BASE => BLOCKED_CONTRACT_ENDPOINT_MISMATCH with ZERO external attempts', async () => {
  const r = await runDriverHarness({ contract: harnessContract({ app_endpoint: 'http://fixture-elsewhere.invalid/' }) });
  const receipt = blockedReceiptAssertions(r, 'BLOCKED_CONTRACT_ENDPOINT_MISMATCH');
  assert.equal(r.stats.adapterMethodCalls, 0, 'no adapter invocation before the block');
  assert.equal(r.stats.adapterCalls, 0, 'no legacy adapter call');
  assert.equal(r.stats.remoteTempWrites, 0, 'no remote temp write');
  assert.equal(r.stats.browserLaunches, 0, 'no browser launch');
  assert.equal(receipt.journey.external_adapter_attempts, 0, 'receipt reports zero attempts');
  assert.equal(r.exitCode, 1);
});

/* D4b (6969817290 #1) — COMPLETE contract + valid digests + matching endpoint, but NO
 * injected adapter: the default withdrawn route makes ZERO external attempts */
t('harness(actual entrypoint): complete-but-unqualified contract => BLOCKED_NO_QUALIFIED_ADAPTER, zero adapter/upload/browser effects', async () => {
  const r = await runDriverHarness({ contract: harnessContract() });
  const receipt = blockedReceiptAssertions(r, 'BLOCKED_NO_QUALIFIED_ADAPTER');
  assert.equal(r.stats.adapterMethodCalls, 0, 'no adapter method may run without an injected qualified adapter');
  assert.equal(r.stats.adapterCalls, 0);
  assert.equal(r.stats.remoteTempWrites, 0, 'no remote temp write attempted');
  assert.equal(r.stats.browserLaunches, 0);
  assert.equal(r.stats.discoveryCalls, 0);
  assert.equal(r.stats.deleteCalls, 0);
  assert.equal(r.stats.transientClearCalls, 0, 'no transient deletion adapter call on the unqualified route');
  assert.equal(receipt.journey.external_adapter_attempts, 0);
  assert.ok(receipt.adapter_qualification, 'qualification state recorded in receipt');
  assert.equal(receipt.adapter_qualification.qualified, false);
  assert.ok(/withdrawn/.test(receipt.adapter_qualification.reason), receipt.adapter_qualification.reason);
  const elig = receipt.checks.find(c => c.name === 'adapter_eligibility');
  assert.ok(elig && elig.pass === true, 'eligibility passed — qualification is what blocked');
  assert.equal(r.exitCode, 1);
});

/* D5 — redirected final URL with a matching marker (injected adapter): identity must
 * block, zero operation/discovery/delete; synthetic resources closed */
t('harness(actual entrypoint): redirected final URL => BLOCKED_IDENTITY (browser_endpoint), zero operation/discovery/delete', async () => {
  const contract = harnessContract();
  const aCalls = [];
  const r = await runDriverHarness({
    contract,
    adapter: syntheticQualifiedAdapter(aCalls, contract),
    extraCalls: aCalls,
    finalUrl: 'http://redirected-target.invalid/',
    markerValue: 'TN-RUN-contract-beef',
  });
  assertIdentityBlocked(r);
});

/* D5b — EMPTY observed URL with a correct marker must NOT fall back to BASE */
t('harness(actual entrypoint): empty observed URL => BLOCKED_IDENTITY (no BASE fallback), zero operation/discovery/delete', async () => {
  const contract = harnessContract();
  const aCalls = [];
  const r = await runDriverHarness({
    contract,
    adapter: syntheticQualifiedAdapter(aCalls, contract),
    extraCalls: aCalls,
    finalUrl: '',
    markerValue: 'TN-RUN-contract-beef',
  });
  assertIdentityBlocked(r);
});

/* D5c — NULL observed URL with a correct marker must NOT fall back to BASE */
t('harness(actual entrypoint): null observed URL => BLOCKED_IDENTITY (no BASE fallback), zero operation/discovery/delete', async () => {
  const contract = harnessContract();
  const aCalls = [];
  const r = await runDriverHarness({
    contract,
    adapter: syntheticQualifiedAdapter(aCalls, contract),
    extraCalls: aCalls,
    finalUrl: null,
    markerValue: 'TN-RUN-contract-beef',
  });
  assertIdentityBlocked(r);
});

/* D5d — THROWING page.url(): read failure surfaces as blocked identity */
t('harness(actual entrypoint): throwing page.url() => BLOCKED_IDENTITY, zero operation/discovery/delete, context closed', async () => {
  const contract = harnessContract();
  const aCalls = [];
  const r = await runDriverHarness({
    contract,
    adapter: syntheticQualifiedAdapter(aCalls, contract),
    extraCalls: aCalls,
    urlThrows: true,
    markerValue: 'TN-RUN-contract-beef',
  });
  assertIdentityBlocked(r);
});

/* D6 — throwing navigation: blocked identity, resources closed, zero mutation */
t('harness(actual entrypoint): throwing marker navigation => BLOCKED_IDENTITY, zero operation/discovery/delete', async () => {
  const contract = harnessContract();
  const aCalls = [];
  const r = await runDriverHarness({
    contract,
    adapter: syntheticQualifiedAdapter(aCalls, contract),
    extraCalls: aCalls,
    gotoThrows: true,
    markerValue: 'TN-RUN-contract-beef',
  });
  assertIdentityBlocked(r);
});

/* D7 — missing (null) marker value: blocked identity, zero mutation */
t('harness(actual entrypoint): null marker value => BLOCKED_IDENTITY, zero operation/discovery/delete', async () => {
  const contract = harnessContract();
  const aCalls = [];
  const r = await runDriverHarness({
    contract,
    adapter: syntheticQualifiedAdapter(aCalls, contract),
    extraCalls: aCalls,
    markerValue: null,
  });
  assertIdentityBlocked(r);
});

/* D7b — MISSING marker attribute (undefined from the DOM query): blocked identity */
t('harness(actual entrypoint): missing (undefined) marker value => BLOCKED_IDENTITY, zero operation/discovery/delete', async () => {
  const contract = harnessContract();
  const aCalls = [];
  const r = await runDriverHarness({
    contract,
    adapter: syntheticQualifiedAdapter(aCalls, contract),
    extraCalls: aCalls,
    markerValue: undefined,
  });
  assertIdentityBlocked(r);
});

/* D7c — MISMATCHED marker value (another fixture's marker): blocked identity */
t('harness(actual entrypoint): mismatched marker value => BLOCKED_IDENTITY, zero operation/discovery/delete', async () => {
  const contract = harnessContract();
  const aCalls = [];
  const r = await runDriverHarness({
    contract,
    adapter: syntheticQualifiedAdapter(aCalls, contract),
    extraCalls: aCalls,
    markerValue: 'TN-RUN-some-other-marker',
  });
  assertIdentityBlocked(r);
});

/* D8 — positive control: explicitly injected synthetic qualified adapter + matching
 * observed URL + matching marker => journey PASSED with operation/discovery enabled */
t('harness(actual entrypoint): injected qualified adapter + matching URL/marker => PASSED, operation/discovery enabled', async () => {
  const contract = harnessContract();
  const aCalls = [];
  const r = await runDriverHarness({
    contract,
    adapter: syntheticQualifiedAdapter(aCalls, contract),
    extraCalls: aCalls,
    markerValue: 'TN-RUN-contract-beef',
  });
  assert.equal(r.err, null);
  assert.equal(r.receipts['fix2-clean-error.json'], undefined);
  const receipt = JSON.parse(r.receipts['fix2-clean-result.json']);
  assert.equal(receipt.journey.status, 'PASSED', 'journey must pass on the matching control');
  assert.equal(r.stats.browserLaunches, 1);
  assert.ok(r.stats.operationCountCalls >= 2, 'operation ran (baseline + final counts through the injected adapter)');
  assert.ok(r.stats.discoveryCalls >= 1, 'discovery ran through the injected adapter');
  assert.equal(r.stats.transientClearCalls, 0, 'empty-token no-call: PASSED path with zero captured tokens must NOT invoke the transient deletion adapter (6970814289)');
  const logNames = (receipt.journey.effect_log || []).map(e => e.effect);
  for (const k of ['preflightProbes', 'openBrowser', 'readBrowserMarker', 'closeBrowser', 'findOwnedRecords']) {
    assert.ok(logNames.indexOf(k) >= 0, 'effect log must include ' + k + ': ' + JSON.stringify(logNames));
  }
  assert.equal(receipt.journey.operation_error, null);
});

/* D9 — REPRODUCER of the historical P1 #1 against the PINNED pre-fix source (99adf59…):
 * the incomplete contract reached the legacy external adapter (remote temp write)
 * before any completeness gate, and the receipt still claimed "zero effects". */
t('reproducer(pinned 99adf59 source): incomplete contract reached legacy adapter with a remote temp write + dishonest receipt', async () => {
  const prefix = require('node:child_process').execSync(
    'git show ' + PREFIX_DRIVER_SHA + ':tests/browser/tn-local-staging-fix2-driver.cjs',
    { encoding: 'utf8', maxBuffer: 8 * 1024 * 1024, cwd: REPO_ROOT });
  const r = await runDriverHarness({
    source: prefix,
    contract: { fixture_marker_name: 'n', cleanup_fingerprint_source: 'fp' },
    legacyAdapterCommands: true,
  });
  assert.equal(r.err, null);
  const receipt = JSON.parse(r.receipts['fix2-clean-result.json']);
  assert.equal(receipt.status, 'BLOCKED_FIXTURE_OWNERSHIP');
  assert.ok(r.stats.adapterCalls >= 1, 'pre-fix: the external adapter WAS reached');
  assert.ok(r.stats.remoteTempWrites >= 1, 'pre-fix: a remote temp-file write WAS requested');
  assert.ok(r.stats.browserLaunches === 0);
  assert.equal(receipt.journey.note.indexOf('zero effects executed'), 0, 'pre-fix receipt claimed zero effects despite the adapter call');
});

/* D10 — REPRODUCER of the historical P1 #2 against the PINNED pre-fix source: the marker
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
    legacyAdapterCommands: true,
  });
  assert.equal(r.err, null);
  const receipt = JSON.parse(r.receipts['fix2-clean-result.json']);
  assert.equal(receipt.journey.status, 'PASSED', 'pre-fix: redirect with matching marker must reproduce the false PASSED');
  assert.equal(r.stats.markerPageUrlReads, 0, 'pre-fix: page.url() was never called');
  assert.ok(r.stats.browserLaunches >= 1);
  assert.ok(r.stats.adapterCalls >= 2, 'pre-fix: legacy adapter calls ran on the redirected target');
  assert.ok(r.stats.legacyDiscoveryCalls >= 1, 'pre-fix: discovery ran');
});

/* helper for the identity-blocked cases */
function assertIdentityBlocked(r) {
  assert.equal(r.err, null);
  assert.equal(r.receipts['fix2-clean-error.json'], undefined);
  const receipt = JSON.parse(r.receipts['fix2-clean-result.json']);
  assert.equal(receipt.journey.status, 'BLOCKED_IDENTITY', 'expected BLOCKED_IDENTITY, got ' + receipt.journey.status);
  const logNames = (receipt.journey.effect_log || []).map(e => e.effect);
  assert.ok(logNames.indexOf('closeBrowser') >= 0, 'browser closed after identity failure');
  assert.equal(logNames.indexOf('findOwnedRecords'), -1, 'no discovery after identity failure');
  assert.equal(logNames.indexOf('deleteOwnedRecords'), -1, 'no delete after identity failure');
  assert.equal(r.stats.operationCountCalls, 0, 'operation (baseline counting) must not run');
  assert.equal(r.stats.discoveryCalls, 0, 'no discovery adapter call');
  assert.equal(r.stats.deleteCalls, 0, 'no deleteOwned adapter call');
  assert.equal(r.stats.transientClearCalls, 0, 'no clearReceiptTransients adapter call on rejected identity (6970814289)');
  assert.equal(r.stats.browserLaunches, 1);
  assert.ok(r.stats.ctxCloses >= 1, 'marker context closed in finally');
  assert.equal(r.stats.browserCloses, 1, 'journey closed the browser');
  assert.equal(r.exitCode, 1);
}

/* D11 — positive owned-token cleanup control (6970814289): a receipt token IS captured,
 * a later operation step fails, and the scoped transient cleanup STILL runs through the
 * adapter with the NONEMPTY token list (not gated on overall PASSED); token stays redacted. */
t('harness(actual entrypoint): captured owned token + later operation failure => transient cleanup STILL runs with nonempty tokens; token redacted', async () => {
  const contract = harnessContract();
  const aCalls = [];
  const r = await runDriverHarness({
    contract,
    adapter: syntheticQualifiedAdapter(aCalls, contract, {
      findOwnedQueue: [[{ id: 777, type: 'tn_ticket', email_has_marker: true }], []],
      deleteOwnedResult: { deleted: [777], failed: [], skipped: [] },
      recordDetailResult: { id: 777, status: 'private', kind: 'service' },
    }),
    extraCalls: aCalls,
    richCtxIndex: 2,
    markerValue: 'TN-RUN-contract-beef',
  });
  assert.equal(r.err, null);
  assert.equal(r.receipts['fix2-clean-error.json'], undefined);
  const receiptText = r.receipts['fix2-clean-result.json'];
  const receipt = JSON.parse(receiptText);
  assert.equal(receipt.journey.status, 'PASSED', 'journey completes; the failure is inside the operation case ledger');
  const c1err = receipt.checks.find(c => c.name === 'c1_error');
  assert.ok(c1err && c1err.pass === false, 'later operation failure recorded');
  assert.equal(receipt.owned_tokens_captured, 1, 'exactly one receipt token captured');
  const clearCall = aCalls.find(c => c.kind === 'adapter-clearReceiptTransients');
  assert.ok(clearCall, 'transient deletion adapter invoked for the NONEMPTY token list');
  assert.equal(clearCall.tokensCount, 1, 'the adapter received the nonempty token list');
  assert.equal(r.stats.transientClearCalls, 1);
  assert.ok(r.stats.deleteCalls >= 1, 'journey owned-record cleanup ran');
  assert.equal(receiptText.indexOf('feedface1234'), -1, 'token value redacted from the published receipt');
  assert.equal(r.exitCode, 1);
  assert.equal(r.stats.browserCloses, 1);
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
