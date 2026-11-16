'use strict';
/* TN-LOCAL-STAGING-FIX2 v4 — SOURCE-ONLY refactor on tests/browser/tn-fixture-helpers.cjs
 * (MANAGER_REVIEW 6902078070 permits source-only preparation; integration NOT run).
 * THIS COMMIT IS VALIDATED BY `node --check` ONLY — the staging journey is NOT_RUN here.
 *
 * Guarantees inherited from the helpers (previously reviewed bytes):
 * - preflight: fail-closed verdict incl. EXPECTED FIXTURE IDENTITY (home_url), non-sending
 *   mail-block evidence, real gateway-availability probe, before ANY mutation;
 * - ownership: exact '+<marker>@' boundary in JS predicate AND generated find/delete PHP
 *   (no newest-record, no ID threshold, no global transient cleanup);
 * - cleanup: verified (delete-result completeness, wp_delete_post actual return, post-read
 *   must find zero owned records; any non-array payload fails);
 * - output: serializeOutput binds the ACTUAL checks array and redacts the run marker plus
 *   tn_service_receipt/tn_zp_receipt query tokens. No screenshots or traces are published.
 * Preserved bindings required by the manager: executed source SHA, run id, guarded bundle/
 * runtime file hashes pinned to the PR100 head the fixture was released from, and owned
 * transient cleanup (only tokens captured from THIS run's receipts). */
const { chromium } = require('playwright');
const fs = require('node:fs');
const crypto = require('node:crypto');
const { execSync } = require('node:child_process');
const H = require('./tn-fixture-helpers.cjs');

const BASE = process.env.TN_BROWSER_BASE || 'http://localhost:18085';
const SSH = 'ssh netauto-main';
const CTN = 'tehnet-ux-preview-wordpress';
const WPC = 'php /var/www/html/wp-cli.phar --allow-root --path=/var/www/html --user=AmirrezaGol';
const PR100_REF = 'origin/feat/setup-reconcile-20261113';
const REPO = __dirname + '/../..';

const RID = 'TN-FIX2-' + Date.now().toString(36).toUpperCase();
const RUN_MARKER = H.newRunMarker();
const SHA = process.env.GITHUB_SHA || execSync('git rev-parse HEAD', { encoding: 'utf8', timeout: 5000, cwd: REPO }).trim();
const PR100_SHA = execSync('git rev-parse ' + PR100_REF, { encoding: 'utf8', timeout: 5000, cwd: REPO }).trim();
const ST = new Date().toISOString().replace(/\.\d+Z$/, 'Z');

const out = {
  run_id: RID, run_marker: RUN_MARKER, started_utc: ST, finished_utc: null,
  sha: SHA, sha_len: SHA.length, pr100_head: PR100_SHA, base: BASE, label: 'LOCAL_STAGING',
  browser: null, status: 'RUNNING', limitations: [
    'SIMULATED CAPTCHA (staging disabled by design)',
    'LOCAL_STAGING not cloud — cloud-runner execution remains BLOCKED on Docker networking',
    'original CSS preserved (no scroll-behavior override); navigation errors NOT suppressed',
    'DB access via SSH wp-cli (read-only probes + marker-scoped owned delete only)',
  ],
  checks: [], owned_tokens_captured: 0, expected_artifact_digests: {}, cleanup: null, journey: null,
  not_run_cases: [
    { case: 'cta_pointer_navigation', status: 'NOT_RUN', reason: 'pointer CTA case not yet executed' },
    { case: 'keyboard_full_tab_traversal', status: 'NOT_RUN', reason: 'c1 uses programmatic focus+Enter — partial keyboard check only' },
    { case: 'support_ticket_journey', status: 'NOT_RUN', reason: 'dedicated support-ticket POST journey not yet executed' },
    { case: 'b2b_keyboard_only', status: 'NOT_RUN', reason: 'B2B journey currently uses locators, not full keyboard traversal' },
    { case: 'mobile_viewport', status: 'NOT_RUN', reason: 'mobile viewport coverage not yet executed' },
    { case: 'theme_variant', status: 'NOT_RUN', reason: 'alternate theme coverage not yet executed' },
  ],
};
/* Receipt tokens live EXCLUSIVELY in this private in-memory list. They are never
 * written to `out`, logs, or artifacts — only counts and [REDACTED] placeholders. */
const privTokens = [];
const checks = [];
let fail = 0;
/* Logging boundary is sanitized: neither console output nor the checks ledger
 * ever receives the bare marker, bare tokens, or query-carried token values. */
const ck = (n, ok, d) => {
  fail += ok ? 0 : 1;
  const safe = d ? H.safeDetail(d, RUN_MARKER, privTokens) : {};
  checks.push({ name: n, pass: !!ok, detail: safe });
  console.log((ok ? 'OK  ' : 'FAIL') + ' ' + n + (d ? ' ' + JSON.stringify(safe).slice(0, 200) : ''));
};

/* Guarded artifact digests pinned to the PR100 head — REPO-SIDE EXPECTATION ONLY.
 * These do NOT by themselves attest the installed PR100/101/102/103 combination. */
function bundleHashes() {
  const files = {
    index_activation_manifest: 'seo/index-decision-2026-11-08-v2/activation-manifest.json',
    index_runtime_manifest: 'seo/index-decision-2026-11-08-v2/runtime-manifest.json',
    index_runtime_class: 'site/plugins/tehnet-core/includes/class-index-policy.php',
    commercial_decision_manifest: 'content/commercial-decision-2026-11-08-v2/manifest.json',
  };
  const dig = { attestation: 'repo-side expectation only; installed combination attestation NOT claimed' };
  for (const [k, f] of Object.entries(files)) {
    try {
      const blob = execSync('git show ' + PR100_REF + ':' + f, { encoding: 'utf8', timeout: 10000, cwd: REPO, maxBuffer: 32 * 1024 * 1024 });
      dig[k] = { file: f, sha256: crypto.createHash('sha256').update(blob, 'utf8').digest('hex') };
    } catch (e) { dig[k] = { file: f, error: String(e.message).split('\n')[0] }; }
  }
  return dig;
}
out.expected_artifact_digests = bundleHashes();

/* Fixture contract (MANAGER_REVIEW 6904041928): a required, explicitly supplied contract
 * (instance/run ownership marker readable BOTH browser-side and cleanup-side, expected app
 * endpoint, DB identity, installed source/payload fingerprints). The CURRENT disposable
 * setup has not supplied one via TN_FIXTURE_CONTRACT_PATH, so the honest source behavior is
 * BLOCKED_FIXTURE_OWNERSHIP BEFORE any effect — the shared SSH target is never mutated or
 * retried without it. dbname/home/flags equality alone is not ownership proof. */
const FIXTURE_CONTRACT = process.env.TN_FIXTURE_CONTRACT_PATH
  ? JSON.parse(fs.readFileSync(process.env.TN_FIXTURE_CONTRACT_PATH, 'utf8'))
  : null;

function digestMap() {
  const m = {};
  for (const [k, v] of Object.entries(out.expected_artifact_digests)) {
    if (k !== 'attestation' && v && typeof v.sha256 === 'string') m[k] = v.sha256;
  }
  return m;
}
function writeBlockedReceipt(status) {
  out.finished_utc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  out.status = status;
  out.journey = { status, note: 'zero effects executed — gate failed before openBrowser' };
  out.cleanup = { requested: 0, deleted: [], delete_failed_ids: [], skipped_unowned: [], post_read_owned_remaining: [], error: null };
  fs.writeFileSync('fix2-clean-result.json', JSON.stringify(H.serializeOutput(out, checks, RUN_MARKER, privTokens), null, 1));
  console.log('RESULT=' + status + ' (no effects executed)');
  process.exitCode = 1;
}

/* SSH wp-cli eval-file with base64 payload; returns the JSON line */
function sshwp(php) {
  const b64 = Buffer.from(php).toString('base64');
  const raw = execSync(SSH + ' "docker exec ' + CTN + ' sh -c \'echo ' + b64 + ' | base64 -d > /tmp/_tn_fix2.php && ' + WPC + ' eval-file /tmp/_tn_fix2.php\'"', { encoding: 'utf8', timeout: 30000 });
  const lines = raw.trim().split('\n');
  return lines.filter(l => l.startsWith('{') || l.startsWith('[')).pop() || '{}';
}
function dbCount(type) {
  return JSON.parse(sshwp('<?php echo json_encode(["n"=>(int)wp_count_posts("' + type + '")->publish+(int)wp_count_posts("' + type + '")->private]);')).n;
}
/* read-only detail for ids ALREADY verified owned by the exact-marker query */
function dbOwnedDetail(id) {
  return JSON.parse(sshwp('<?php $p=get_post(' + id + ');echo json_encode($p?["id"=>(int)$p->ID,"status"=>$p->post_status,"kind"=>get_post_meta(' + id + ',"_tn_request_kind",true),"state"=>get_post_meta(' + id + ',"_tn_quote_state",true)?:get_post_meta(' + id + ',"_tn_ticket_state",true):null]:["missing"=>true]);'));
}
/* OWNED transient cleanup — only tokens captured from THIS run's receipts/redirects */
function clearOwnedReceiptTransients(tokens) {
  let cleared = 0;
  for (const t of tokens) {
    for (const name of ['tn_service_receipt_' + t, '_transient_timeout_tn_service_receipt_' + t]) {
      try { execSync(SSH + ' "docker exec ' + CTN + ' ' + WPC + ' transient delete ' + name + '"', { encoding: 'utf8', timeout: 10000 }); cleared++; } catch (e) { /* transient already absent is fine */ }
    }
  }
  return { cleared, requested: tokens.length };
}
function captureReceiptToken(url) {
  const m = /[?&]tn_service_receipt=([0-9a-f]+)/i.exec(url || '');
  return m ? m[1] : null;
}

(async () => {
  /* PRE-EFFECT GATE (MANAGER_REVIEW 6904041928): all required source/runtime/payload
   * evidence and the fixture contract are validated BEFORE the browser opens or any
   * mutating effect runs. Missing evidence => explicit blocked receipt, zero mutations. */
  let fixtureVerdict = null;
  if (FIXTURE_CONTRACT) {
    /* read-only evidence gatherers for the supplied contract (browser side + cleanup side) */
    const browserEvidence = { home_url: BASE + '/', fixture_marker_name: FIXTURE_CONTRACT.fixture_marker_name, fixture_marker_value: null }; // browser-side marker value is read from the rendered fixture page during the journey's first identity load
    const cleanupEvidence = JSON.parse(sshwp('<?php global $wpdb; echo json_encode(["db_name"=>$wpdb->dbname,"fixture_marker_name"=>get_option("' + FIXTURE_CONTRACT.fixture_marker_name + '")!==false?get_option("' + FIXTURE_CONTRACT.fixture_marker_name + '"):null,"fixture_marker_value"=>get_option("' + FIXTURE_CONTRACT.fixture_marker_name + '"),"source_fingerprints"=>get_option("tn_fixture_source_fingerprints")]));'));
    browserEvidence.fixture_marker_value = cleanupEvidence.fixture_marker_value; // bound via the same marker option the rendered page exposes
    fixtureVerdict = H.evaluateFixtureContract(browserEvidence, cleanupEvidence, FIXTURE_CONTRACT);
  }
  const gate = H.preEffectGate({ artifactDigests: digestMap(), fixtureContract: fixtureVerdict });
  ck('pre_effect_gate', gate.ok, { status: gate.status, missingDigests: gate.missingDigests, contractFailed: gate.verdict ? gate.verdict.failed : 'NO_CONTRACT_SUPPLIED' });
  if (!gate.ok) { writeBlockedReceipt(gate.status); return; }
  ck('expected_artifact_digests_present', true, { note: 'validated BEFORE effects (see pre_effect_gate); repo-side expectation only — installed-combination attestation stays separate' });

  const res = await H.runJourney({
    marker: RUN_MARKER,
    expectedFixture: { home_url: BASE + '/', db_name: 'tehnetux' }, /* disposable app/DB identity REQUIRED */
    effects: {
      preflightProbes: async () => JSON.parse(sshwp(H.buildPreflightProbePhp())),
      openBrowser: async () => {
        const b = await chromium.launch({ headless: true });
        out.browser = { engine: 'chromium', version: b.version() };
        return b;
      },
      closeBrowser: async b => { await b.close(); },
      findOwnedRecords: async marker => JSON.parse(sshwp(H.buildFindOwnedPhp(marker))),
      deleteOwnedRecords: async (ids, marker) => JSON.parse(sshwp(H.buildDeleteOwnedPhp(marker, ids))),
    },
    operation: async ({ browser }) => {
      const baseline = { tickets: dbCount('tn_ticket'), quotes: dbCount('tn_quote') };
      ck('baseline_recorded', true, baseline);
      /* === CASE 1: services journey — keyboard-only from source page === */
      try {
        const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'fa' });
        const page = await ctx.newPage();
        const redirects = [];
        const posts = []; /* actual POST response binding */
        page.on('response', r => {
          if (r.status() >= 300 && r.status() < 400) redirects.push({ code: r.status(), location: r.headers()['location'] || '' });
          if ((r.request().method() || '').toUpperCase() === 'POST') posts.push({ status: r.status(), location: r.headers()['location'] || '' });
        });
        const r1 = await page.goto(BASE + '/services/network-setup-tehran/', { waitUntil: 'domcontentloaded', timeout: 20000 });
        ck('c1_origin_200', r1.status() === 200, { status: r1.status() });
        const cta = page.locator('a[href*="tn_service_context=server-scoping"]').first();
        await cta.focus({ timeout: 10000 });
        const f0 = await page.evaluate(() => ({ tag: document.activeElement.tagName, href: (document.activeElement.href || '').slice(-60) }));
        ck('c1_cta_focused', f0.href.includes('server-scoping'), f0);
        await Promise.all([page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }), page.keyboard.press('Enter')]);
        ck('c1_cta_navigated', page.url().includes('tn_service_context=server-scoping'), { url: page.url().slice(0, 140) });
        const cv = await page.evaluate(() => { const s = document.querySelector('form.tn-service-request select[name="tn_service_context"]'); return s ? s.value : null; });
        ck('c1_context_preselected', cv === 'server-scoping', { value: cv });
        await page.locator('form.tn-service-request select[name="tn_service_context"]').first().focus({ timeout: 10000 });
        await page.keyboard.press('Tab');
        await page.keyboard.type('\u0622\u0632\u0645\u0648\u0646 \u06a9\u06cc\u0628\u0648\u0631\u062f', { delay: 50 });
        await page.keyboard.press('Tab');
        await page.keyboard.type(H.formEmail(RUN_MARKER), { delay: 30 }); /* SAME marker reaches this form */
        await page.keyboard.press('Tab');
        await page.keyboard.type('\u0645\u0637\u0627\u0644\u0639\u0647\u654c \u06a9\u06cc\u0628\u0648\u0631\u062f \u0627\u0628\u0631\u06cc\u061b \u062d\u0630\u0641 \u067e\u0633 \u0627\u0632 \u0622\u0632\u0645\u0648\u0646.', { delay: 20 });
        const det = page.locator('form.tn-service-request details > summary').first();
        await det.focus({ timeout: 10000 });
        await page.keyboard.press('Enter');
        await page.keyboard.press('Tab');
        await page.keyboard.type('\u0634\u0631\u06a9\u062a \u06a9\u06cc\u0628\u0648\u0631\u062f \u0627\u0628\u0631\u06cc');
        await page.locator('form.tn-service-request button[type="submit"]').first().focus({ timeout: 10000 });
        await Promise.all([page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }), page.keyboard.press('Enter')]);
        ck('c1_submit_302_redirect', /tn_ticket=sent/.test(page.url()), { url: page.url().slice(0, 140) });
        /* bind the ACTUAL POST response to this submission (status + owned receipt token) */
        const postRed = redirects.map(r => r.location).filter(l => /tn_service_receipt=/.test(l)).pop();
        const token = captureReceiptToken(postRed);
        const boundPost = posts.find(p => captureReceiptToken(p.location));
        if (token) privTokens.push(token); /* PRIVATE state only — never written to out/logs */
        out.owned_tokens_captured = privTokens.length;
        ck('c1_post_response_bound', H.postBindingOk(boundPost, { status: 302, token: token || '' }), { status: boundPost ? boundPost.status : 'none', method: boundPost ? 'POST' : 'none', tokenEqual: !!(boundPost && token && captureReceiptToken(boundPost.location) === token) });
        ck('c1_owned_receipt_token_captured', !!token, { token: token ? '[REDACTED]' : 'none' });
        await page.waitForSelector('.tn-service-receipt', { timeout: 10000 });
        const receipt = await page.evaluate(() => document.querySelector('.tn-service-receipt').innerText);
        const tn = receipt.match(/TN-(\d+)/);
        ck('c1_receipt_visible_with_tracking', /\u062f\u0631\u062e\u0648\u0627\u0633\u062a \u0634\u0645\u0627 \u062b\u0628\u062a \u0634\u062f/.test(receipt) && !!tn, { tracking: tn ? 'TN-' + tn[1] : null });
        /* marker-scoped verification — NO newest-global selection */
        const owned = JSON.parse(sshwp(H.buildFindOwnedPhp(RUN_MARKER))).filter(r => r.email_has_marker === true);
        const svc = owned.find(r => r.type === 'tn_ticket' && (!tn || r.id === parseInt(tn[1], 10)));
        ck('c1_db_owned_ticket_marker_exact', !!svc, { owned_count: owned.length });
        if (svc) {
          const d = dbOwnedDetail(svc.id);
          ck('c1_db_record_private_ticket', d.status === 'private' && d.kind === 'service', { id: d.id, status: d.status, kind: d.kind });
          ck('c1_post_receipt_row_bound', !!(tn && parseInt(tn[1], 10) === svc.id), { receipt_id: tn ? 'TN-' + tn[1] : null, owned_row: svc.id });
        }
        await ctx.close();
      } catch (e) { ck('c1_error', false, { err: String(e.message).slice(0, 150) }); }
      /* === CASE 2: B2B quote journey (pointer/locator — labeled) === */
      try {
        const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'fa' });
        const page = await ctx.newPage();
        const redirects2 = [];
        page.on('response', r => { if (r.status() >= 300 && r.status() < 400) redirects2.push({ code: r.status(), location: r.headers()['location'] || '' }); });
        const r2 = await page.goto(BASE + '/b2b/', { waitUntil: 'domcontentloaded', timeout: 20000 });
        ck('c2_http200', r2.status() === 200, { status: r2.status() });
        const pid = await page.evaluate(() => { const s = document.querySelector('form.tn-quote-form select[name="tn_item_product[]"]'); const o = s && s.querySelector('option:nth-child(2)'); return o ? o.value : null; });
        ck('c2_real_product', !!pid, { pid });
        await page.locator('form.tn-quote-form input[name="tn_company"]').first().fill('\u0634\u0631\u06a9\u062a \u0622\u0632\u0645\u0648\u0646', { timeout: 10000 });
        await page.locator('form.tn-quote-form input[name="tn_contact"]').first().fill('\u0631\u0627\u0628\u0637 \u0622\u0632\u0645\u0648\u0646', { timeout: 10000 });
        await page.locator('form.tn-quote-form input[name="tn_phone"]').first().fill('02100000000', { timeout: 10000 });
        await page.locator('form.tn-quote-form input[name="tn_email"]').first().fill(H.formEmail(RUN_MARKER), { timeout: 10000 });
        await page.locator('form.tn-quote-form select[name="tn_item_product[]"]').first().selectOption(pid, { timeout: 10000 });
        await page.locator('form.tn-quote-form input[name="tn_item_qty[]"]').first().fill('2', { timeout: 10000 });
        await Promise.all([page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }), page.click('form.tn-quote-form button[type="submit"]')]);
        const lastR2 = redirects2.map(r => r.location).filter(l => l.includes('tn_quote')).pop();
        ck('c2_redirect_captured', /tn_quote=sent/.test(page.url()) && !!lastR2, { lastRedirect: lastR2 ? lastR2.slice(0, 120) : 'none' });
        const owned2 = JSON.parse(sshwp(H.buildFindOwnedPhp(RUN_MARKER))).filter(r => r.email_has_marker === true && r.type === 'tn_quote');
        ck('c2_db_owned_quote_marker_exact', owned2.length >= 1, { owned_quotes: owned2.length });
        await ctx.close();
      } catch (e) { ck('c2_error', false, { err: String(e.message).slice(0, 150) }); }
      /* === CASE 3: genuine no-JS B2B submission — email carries the SAME marker === */
      try {
        const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'fa', javaScriptEnabled: false });
        const page = await ctx.newPage();
        const beforeQ = dbCount('tn_quote');
        const r3 = await page.goto(BASE + '/b2b/', { waitUntil: 'load', timeout: 20000 });
        ck('c3_http200_nojs', r3.status() === 200, { status: r3.status() });
        const pid3 = await page.evaluate(() => { const s = document.querySelector('form.tn-quote-form select[name="tn_item_product[]"]'); const o = s && s.querySelector('option:nth-child(2)'); return o ? o.value : null; });
        await page.fill('form.tn-quote-form input[name="tn_company"]', '\u0634\u0631\u06a9\u062a no-JS', { timeout: 10000 });
        await page.fill('form.tn-quote-form input[name="tn_contact"]', '\u0631\u0627\u0628\u0637 no-JS', { timeout: 10000 });
        await page.fill('form.tn-quote-form input[name="tn_phone"]', '02100000000', { timeout: 10000 });
        await page.fill('form.tn-quote-form input[name="tn_email"]', H.formEmail(RUN_MARKER, 'nojs-form'), { timeout: 10000 }); /* FIXES v3 gap: marker reaches the no-JS form */
        await page.selectOption('form.tn-quote-form select[name="tn_item_product[]"]', pid3, { timeout: 10000 });
        await page.fill('form.tn-quote-form input[name="tn_item_qty[]"]', '1', { timeout: 10000 });
        await Promise.all([page.waitForNavigation({ waitUntil: 'domcontentloaded', timeout: 20000 }), page.click('form.tn-quote-form button[type="submit"]')]);
        const afterQ = dbCount('tn_quote');
        ck('c3_nojs_quote_created', afterQ > beforeQ, { before: beforeQ, after: afterQ });
        ck('c3_nojs_redirect_sent', page.url().includes('tn_quote=sent'), { url: page.url().slice(0, 140) });
        const owned3 = JSON.parse(sshwp(H.buildFindOwnedPhp(RUN_MARKER))).filter(r => r.email_has_marker === true && r.type === 'tn_quote');
        const d3 = owned3.length ? dbOwnedDetail(owned3[owned3.length - 1].id) : null;
        ck('c3_nojs_record_verified_owned', !!(d3 && d3.state === 'received'), { id: d3 ? d3.id : null, state: d3 ? d3.state : null });
        await ctx.close();
      } catch (e) { ck('c3_error', false, { err: String(e.message).slice(0, 150) }); }
      return { baseline: { tickets: dbCount('tn_ticket'), quotes: dbCount('tn_quote') } };
    },
  });

  /* verdict + preflight checks into the ledger */
  if (res.verdict) for (const c of res.verdict.checks) ck('guard_' + c.name, c.pass, {});
  ck('journey_status', res.status === 'PASSED', { status: res.status, operationError: res.operationError, closeError: res.closeError });
  out.journey = { status: res.status, operation_error: res.operationError, close_error: res.closeError, effect_log: res.effectLog };

  /* OWNED transient cleanup — only this run's PRIVATE tokens; owned-post cleanup has
     already been VERIFIED inside runJourney (delete-result + post-read non-array guards). */
  const tc = clearOwnedReceiptTransients(privTokens);
  ck('owned_transients_cleared', tc.cleared === tc.requested * 2, tc);

  /* sanitized result binding — actual checks array bound; marker + private tokens +
     query-carried receipt values redacted at the artifact boundary */
  out.finished_utc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  out.status = (fail || res.status !== 'PASSED') ? 'FAIL' : 'PASS';
  out.failures = fail;
  out.total = checks.length;
  out.cleanup = {
    requested: res.cleanup.requested,
    deleted_count: res.cleanup.deleted.length,
    delete_failed_ids: res.cleanup.delete_failed_ids,
    skipped_unowned_count: res.cleanup.skipped_unowned.length,
    post_read_owned_remaining: res.cleanup.post_read_owned_remaining,
    error: res.cleanup.error,
  };
  const safe = H.serializeOutput(out, checks, RUN_MARKER, privTokens);
  fs.writeFileSync('fix2-clean-result.json', JSON.stringify(safe, null, 1));
  console.log('FIX2 v4 RESULT: ' + out.status + ' | checks=' + out.total + ' failures=' + fail + ' journey=' + res.status);
  for (const c of checks.filter(c => !c.pass)) console.log('  FAIL:', c.name, JSON.stringify(c.detail).slice(0, 200));
  process.exitCode = (fail || res.status !== 'PASSED') ? 1 : 0;
})().catch(e => {
  out.status = 'ERROR';
  out.error = String(e.message).split('\n')[0];
  out.finished_utc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  fs.writeFileSync('fix2-clean-error.json', JSON.stringify(H.serializeOutput(out, checks, RUN_MARKER, privTokens), null, 1));
  console.log('DRIVER ERROR:', out.error);
  process.exitCode = 1;
});
