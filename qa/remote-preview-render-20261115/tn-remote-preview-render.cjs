'use strict';
/* TN-REMOTE-PREVIEW-RENDER-20261115 rev2 — corrections per MANAGER_REVIEW 6902812202.
 * Path-free runner: module/input via env overrides, repository-relative defaults.
 * Pinned source digest is asserted BEFORE the browser launches; mismatch = reject.
 * k2 asserts EXACT ordered focus (with a fabricated-repeat negative predicate check).
 * Intake = the H3 template under scope-and-request (six-field list), NOT the older
 * session-example H2 (kept separately named). Standalone render only; WordPress
 * shortcode/theme rendering stays NOT_RUN. No forms/screenshots/traces/public URL. */
const path = require('node:path');
const fs = require('node:fs');
const crypto = require('node:crypto');
const pwModule = process.env.TN_PW_MODULE;
if (!pwModule) { console.error('TN_PW_MODULE env required (existing playwright install); no package installation'); process.exit(2); }
const { chromium } = require(pwModule);

const OUT = path.join(__dirname, 'remote-preview-render-result.json');
const INPUT = process.env.TN_RENDER_INPUT || path.join(__dirname, 'rendered-source.snapshot.html');
const SOURCE_COMMIT = '395413a0bb1d57f63321e1fef6e9d78833a50ce3';
const PINNED_SHA256 = 'c33df1e3a033760915122e4f7268bd040987489b9d10ce5bffc41e5e772a8f49';

const runId = 'TN-REMOTE-PREVIEW-RENDER-' + Date.now().toString(36).toUpperCase();
const startedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');

const EXPECTED_H2 = ['session-journey', 'remote-fit', 'before-connection', 'view-and-control', 'session-boundaries', 'session-example', 'session-handoff', 'scope-and-request', 'why-tehnet'];
const EXPECTED_INTERNAL = ['/support/', '/support/', '/b2b/', '/b2b/', '/services/network-support-tehran/', '/services/network-setup-tehran/', '/services/network-setup-tehran/', '/services/voice-network-readiness/', '/services/mikrotik-tehran/', '/technical-methodology/', '/learn/mikrotik/mtcna/', '/lab/voice-network-checklist/', '/contact/'];
const IN_PAGE_ANCHORS = ['before-connection', 'session-boundaries', 'session-handoff'];
const INTAKE_H3_TEXT = 'قالب درخواست اولیه؛ پشتیبانی از راه دور';
const INTAKE_FIELDS = 6;
const FOCUS_STEPS = 6;

/* exact ordered focus predicate (pure; also used for the negative check) */
function orderedFocusOk(actual, expected) {
  if (!Array.isArray(actual) || actual.length !== expected.length) return false;
  return actual.every((h, i) => h === expected[i]);
}

const assertions = [];
const A = (id, pass, detail) => { assertions.push({ id, pass: !!pass, detail: detail || {} }); console.log((pass ? 'PASS ' : 'FAIL ') + id + (detail ? ' ' + JSON.stringify(detail).slice(0, 180) : '')); };

(async () => {
  /* pinned-digest gate BEFORE launching the browser */
  const blob = fs.readFileSync(INPUT);
  const inputSha = crypto.createHash('sha256').update(blob).digest('hex');
  A('p0_pinned_digest_match', inputSha === PINNED_SHA256, { pinned: PINNED_SHA256.slice(0, 16) + '…', input: inputSha.slice(0, 16) + '…' });
  if (inputSha !== PINNED_SHA256) {
    const receipt = { packet: 'TN-REMOTE-PREVIEW-RENDER-20261115', run_id: runId, started_utc: startedUtc, rejected: 'input digest mismatch — browser NOT launched', assertions, summary: { total: assertions.length, passed: assertions.filter(a => a.pass).length, failed: assertions.filter(a => !a.pass).length } };
    fs.writeFileSync(OUT, JSON.stringify(receipt, null, 1));
    console.log('RECEIPT_WRITTEN=' + path.basename(OUT));
    process.exitCode = 1;
    return;
  }

  const browser = await chromium.launch({ headless: true });
  const bv = browser.version();
  const url = 'file:///' + INPUT.replace(/\\/g, '/');

  /* --- desktop --- */
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'fa' });
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: 'load', timeout: 20000 });
  const d = await page.evaluate((inPageAnchors) => {
    const h2s = [...document.querySelectorAll('h2')].map(h => h.id || null);
    const links = [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'));
    const h3s = [...document.querySelectorAll('h3')].map(h => h.textContent.trim());
    /* locate the intake H3 and its following six-field list */
    const intakeH3 = h3s.find(t => t === 'قالب درخواست اولیه؛ پشتیبانی از راه دور');
    let intake = { found: !!intakeH3 };
    if (intakeH3) {
      let node = [...document.querySelectorAll('h3')].find(h => h.textContent.trim() === intakeH3);
      const scopeIdx = h2s.indexOf('scope-and-request');
      const whyIdx = h2s.indexOf('why-tehnet');
      /* structural placement: H3 must appear between scope-and-request H2 and why-tehnet H2 */
      let cur = node; let seenScope = false; let beforeWhy = true; let insideScope = false;
      while (cur) { cur = cur.previousElementSibling || (cur.parentElement && cur.parentElement.previousElementSibling ? null : null); if (!cur) break;
        if (cur.id === 'scope-and-request') { insideScope = true; break; }
        if (cur.id === 'session-journey') break;
      }
      /* simpler: compare document positions */
      const scopeH2 = document.getElementById('scope-and-request');
      const whyH2 = document.getElementById('why-tehnet');
      const pos = (a, b) => (a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0;
      insideScope = pos(scopeH2, node) && pos(node, whyH2);
      let ul = node; while ((ul = ul.nextElementSibling)) { if (ul.tagName === 'UL') break; if (ul.tagName === 'H2' || ul.tagName === 'H3') { ul = null; break; } }
      intake = { found: true, insideScopeBeforeWhy: insideScope, listLi: ul ? ul.querySelectorAll(':scope > li').length : 0 };
    }
    return {
      bodyLen: document.body.innerText.length,
      h2s, h3s,
      internal: links.filter(h => h.startsWith('/')),
      external: links.filter(h => /^https?:/.test(h)),
      inpage: links.filter(h => h.startsWith('#')),
      anchorsResolve: inPageAnchors.map(id => !!document.getElementById(id)),
      phoneLiteral: document.body.innerText.includes('[tehnet_phone]'),
      noteLiteral: document.body.innerText.includes('[tn_editorial_note]'),
      forms: document.querySelectorAll('form').length,
      sessionExampleIdx: h2s.indexOf('session-example'),
      whyTehnetIdx: h2s.indexOf('why-tehnet'),
      domLinks: links,
      intake,
    };
  }, IN_PAGE_ANCHORS);

  A('d1_standalone_loads', d.bodyLen > 2000, { chars: d.bodyLen });
  A('d2_h2_set_exact', JSON.stringify(d.h2s) === JSON.stringify(EXPECTED_H2), { order: d.h2s });
  A('d3_session_example_h2_order', d.sessionExampleIdx >= 0 && d.whyTehnetIdx > d.sessionExampleIdx, { sessionExampleIdx: d.sessionExampleIdx, whyTehnetIdx: d.whyTehnetIdx, note: 'pre-existing fictional-session H2 — NOT the intake' });
  A('d4_intake_h3_in_scope_and_request', d.intake.found === true && d.intake.insideScopeBeforeWhy === true, { intake: d.intake });
  A('d5_intake_six_field_list', d.intake.listLi === 6, { li: d.intake.listLi });
  A('d6_inpage_anchors_resolve', d.anchorsResolve.every(Boolean), { resolved: d.anchorsResolve });
  A('d7_internal_links_exact', JSON.stringify(d.internal.slice().sort()) === JSON.stringify([...EXPECTED_INTERNAL].sort()), { expected: EXPECTED_INTERNAL.length, found: d.internal.length });
  A('d8_external_links_three', d.external.length === 3, { count: d.external.length });
  A('d9_phone_shortcode_literal_standalone', d.phoneLiteral === true, { note: 'standalone does NOT expand shortcodes' });
  A('d10_editorial_note_literal_standalone', d.noteLiteral === true, { note: 'standalone does NOT expand shortcodes' });
  A('d11_no_forms_present', d.forms === 0, { forms: d.forms });

  /* keyboard: EXACT ordered focus against the first six DOM anchors */
  const expectedSeq = d.domLinks.slice(0, FOCUS_STEPS);
  await page.keyboard.press('Tab');
  const kb = [await page.evaluate(() => document.activeElement.getAttribute('href'))];
  for (let i = 1; i < FOCUS_STEPS; i++) { await page.keyboard.press('Tab'); kb.push(await page.evaluate(() => document.activeElement.getAttribute('href'))); }
  A('k1_first_tab_focuses_first_link', kb[0] === expectedSeq[0], { focused: kb[0] });
  A('k2_exact_ordered_focus', orderedFocusOk(kb, expectedSeq), { positions: kb.map((h, i) => ({ step: i + 1, href: h, expected: expectedSeq[i] })), hrefsSanitized: true });
  /* negative predicate check: a fabricated repeated-focus sequence MUST fail */
  const fabricated = [expectedSeq[0], expectedSeq[0], expectedSeq[0], expectedSeq[0], expectedSeq[0], expectedSeq[0]];
  A('k3_negative_repeated_focus_rejected', orderedFocusOk(fabricated, expectedSeq) === false && !orderedFocusOk(kb, kb.slice(0, 3).concat(kb.slice(0, 3))), { fabricated: 'six repeats of first href', predicateVerdictOnFabricated: orderedFocusOk(fabricated, expectedSeq) });
  await ctx.close();

  /* --- mobile --- */
  const mctx = await browser.newContext({ viewport: { width: 390, height: 844 }, locale: 'fa' });
  const mpage = await mctx.newPage();
  await mpage.goto(url, { waitUntil: 'load', timeout: 20000 });
  const m = await mpage.evaluate(() => {
    const intakeH3 = [...document.querySelectorAll('h3')].find(h => h.textContent.trim() === 'قالب درخواست اولیه؛ پشتیبانی از راه دور');
    const r = intakeH3 ? intakeH3.getBoundingClientRect() : null;
    return {
      overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      h2Visible: [...document.querySelectorAll('h2')].map(h => h.getBoundingClientRect().height > 0),
      sessionExampleVisible: (() => { const h = document.getElementById('session-example'); return !!h && h.getBoundingClientRect().height > 0; })(),
      intake: { found: !!intakeH3, visible: !!r && r.height > 0, heightPx: r ? Math.round(r.height) : 0, widthPx: r ? Math.round(r.width) : 0, withinViewportWidth: !!r && r.width <= 390 },
    };
  });
  A('m1_mobile_loads', m.h2Visible.length === EXPECTED_H2.length, { h2: m.h2Visible.length });
  A('m2_no_horizontal_overflow', m.overflow <= 1, { overflowPx: m.overflow });
  A('m3_all_h2_visible_mobile', m.h2Visible.every(Boolean), { hidden: m.h2Visible.filter(v => !v).length });
  A('m4_intake_h3_rendered_mobile', m.intake.found && m.intake.visible && m.intake.withinViewportWidth, { heightPx: m.intake.heightPx, widthPx: m.intake.widthPx, note: 'actual intake H3 (not session-example)' });
  A('m5_session_example_visible_mobile_separately_named', m.sessionExampleVisible === true, { note: 'pre-existing section, tracked separately' });
  await mctx.close();

  await browser.close();
  const finishedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  const passed = assertions.filter(a => a.pass).length;
  const receipt = {
    packet: 'TN-REMOTE-PREVIEW-RENDER-20261115',
    rev: 2,
    run_id: runId,
    started_utc: startedUtc,
    finished_utc: finishedUtc,
    label: 'LOCAL_STAGING existing tools (playwright, headless, file:// standalone)',
    source: {
      commit: SOURCE_COMMIT,
      file: 'content/remote-intake-example-20261115/remote-support-with-intake.preview.html',
      pinned_sha256: PINNED_SHA256,
      input_sha256: inputSha,
      bytes: blob.length,
    },
    assertions,
    summary: { total: assertions.length, passed, failed: assertions.length - passed },
    scope: { form_posts: 0, screenshots: 0, traces: 0, public_url: 'none', external_navigations: 0 },
    limitations: [
      'STANDALONE static render — does NOT prove WordPress shortcode/theme rendering; [tehnet_phone] and [tn_editorial_note] remain literal (asserted as source preservation).',
      'WordPress-integration claim remains NOT_RUN: intake fragment NOT_DEPLOYED; no fixture render of the integrated page exists.',
      'Keyboard check verifies exact ordered focus traversal only (no Enter activation, no navigations).',
    ],
    production_touched: false,
  };
  fs.writeFileSync(OUT, JSON.stringify(receipt, null, 1));
  console.log('\nTOTAL=' + assertions.length + ' PASS=' + passed + ' FAIL=' + (assertions.length - passed));
  console.log('RECEIPT_WRITTEN=' + path.basename(OUT));
  process.exitCode = (assertions.length - passed) ? 1 : 0;
})().catch(e => { console.error('RUNNER ERROR:', String(e.message).split('\n')[0]); process.exitCode = 1; });
