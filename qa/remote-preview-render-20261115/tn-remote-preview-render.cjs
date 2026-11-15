'use strict';
/* TN-REMOTE-PREVIEW-RENDER-20261115 — LOCAL_STAGING existing-tools render check.
 * Renders the committed standalone integrated preview (395413a) in Chromium:
 * desktop/mobile/keyboard/link-target assertions. NO form posts (none exist),
 * NO screenshots, NO traces, NO public URL. Textual receipt only.
 * LIMITATION encoded in receipt: standalone render does NOT prove WordPress
 * shortcode/theme rendering — [tehnet_phone] and [tn_editorial_note] stay literal. */
const { chromium } = require('D:/Codex-Projects/Codex/2026-10-15/referenced-chatgpt-conversation-this-is-an/work/tmp-20261113/pw-env/node_modules/playwright');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const PREVIEW = 'D:/Codex-Projects/Codex/2026-10-15/referenced-chatgpt-conversation-this-is-an/work/tmp-20261113/remote-preview-run/preview.html';
const OUT = 'D:/Codex-Projects/Codex/2026-10-15/referenced-chatgpt-conversation-this-is-an/work/TehNet-growth-20261031/qa/remote-preview-render-20261115/remote-preview-render-result.json';
const SOURCE_COMMIT = '395413a0bb1d57f63321e1fef6e9d78833a50ce3';

const runId = 'TN-REMOTE-PREVIEW-RENDER-' + Date.now().toString(36).toUpperCase();
const startedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
const blob = fs.readFileSync(PREVIEW);
const blobSha = crypto.createHash('sha256').update(blob).digest('hex');

const EXPECTED_H2 = ['session-journey', 'remote-fit', 'before-connection', 'view-and-control', 'session-boundaries', 'session-example', 'session-handoff', 'scope-and-request', 'why-tehnet'];
const EXPECTED_INTERNAL = ['/support/', '/support/', '/b2b/', '/b2b/', '/services/network-support-tehran/', '/services/network-setup-tehran/', '/services/network-setup-tehran/', '/services/voice-network-readiness/', '/services/mikrotik-tehran/', '/technical-methodology/', '/learn/mikrotik/mtcna/', '/lab/voice-network-checklist/', '/contact/'];
const IN_PAGE_ANCHORS = ['before-connection', 'session-boundaries', 'session-handoff'];

const assertions = [];
const A = (id, pass, detail) => { assertions.push({ id, pass: !!pass, detail: detail || {} }); console.log((pass ? 'PASS ' : 'FAIL ') + id + (detail ? ' ' + JSON.stringify(detail).slice(0, 160) : '')); };

(async () => {
  const browser = await chromium.launch({ headless: true });
  const bv = browser.version();

  /* --- desktop --- */
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'fa' });
  const page = await ctx.newPage();
  await page.goto('file:///' + PREVIEW.replace(/\\/g, '/'), { waitUntil: 'load', timeout: 20000 });
  const d = await page.evaluate((inPageAnchors) => {
    const h2s = [...document.querySelectorAll('h2')].map(h => h.id || null);
    const links = [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'));
    return {
      bodyLen: document.body.innerText.length,
      h2s,
      internal: links.filter(h => h.startsWith('/')),
      external: links.filter(h => /^https?:/.test(h)),
      inpage: links.filter(h => h.startsWith('#')),
      anchorsResolve: inPageAnchors.map(id => !!document.getElementById(id)),
      phoneLiteral: document.body.innerText.includes('[tehnet_phone]'),
      noteLiteral: document.body.innerText.includes('[tn_editorial_note]'),
      forms: document.querySelectorAll('form').length,
      sessionExampleIdx: h2s.indexOf('session-example'),
      whyTehnetIdx: h2s.indexOf('why-tehnet'),
    };
  }, IN_PAGE_ANCHORS);
  A('d1_standalone_loads', d.bodyLen > 2000, { chars: d.bodyLen });
  A('d2_h2_set_exact', JSON.stringify(d.h2s) === JSON.stringify(EXPECTED_H2), { order: d.h2s });
  A('d3_intake_h2_before_why_tehnet', d.sessionExampleIdx >= 0 && d.whyTehnetIdx > d.sessionExampleIdx, { sessionExampleIdx: d.sessionExampleIdx, whyTehnetIdx: d.whyTehnetIdx });
  A('d4_inpage_anchors_resolve', d.anchorsResolve.every(Boolean), { anchors: IN_PAGE_ANCHORS, resolved: d.anchorsResolve });
  A('d5_internal_links_exact', JSON.stringify(d.internal.slice().sort()) === JSON.stringify([...EXPECTED_INTERNAL].sort()), { expected: EXPECTED_INTERNAL.length, found: d.internal.length });
  A('d6_external_links_three', d.external.length === 3, { count: d.external.length });
  A('d7_phone_shortcode_literal_standalone', d.phoneLiteral === true, { note: 'standalone render does NOT expand shortcodes' });
  A('d8_editorial_note_literal_standalone', d.noteLiteral === true, { note: 'standalone render does NOT expand shortcodes' });
  A('d9_no_forms_present', d.forms === 0, { forms: d.forms });
  /* keyboard traversal: Tab from body through first 6 focusables — no navigation triggered */
  await page.keyboard.press('Tab');
  const kb = [await page.evaluate(() => ({ tag: document.activeElement.tagName, href: document.activeElement.getAttribute('href') || null }))];
  for (let i = 0; i < 5; i++) { await page.keyboard.press('Tab'); kb.push(await page.evaluate(() => ({ tag: document.activeElement.tagName, href: document.activeElement.getAttribute('href') || null }))); }
  const domLinks = await page.evaluate(() => [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')));
  A('k1_first_tab_focuses_link', kb[0].tag === 'A', kb[0]);
  A('k2_tab_traversal_follows_dom_links', kb.every(x => x.tag === 'A') && kb.every(x => x.href === null || domLinks.includes(x.href)), { traversed: kb.length, urlsShown: 'none — activation not pressed' });
  await ctx.close();

  /* --- mobile --- */
  const mctx = await browser.newContext({ viewport: { width: 390, height: 844 }, locale: 'fa' });
  const mpage = await mctx.newPage();
  await mpage.goto('file:///' + PREVIEW.replace(/\\/g, '/'), { waitUntil: 'load', timeout: 20000 });
  const m = await mpage.evaluate(() => ({
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    h2Visible: [...document.querySelectorAll('h2')].map(h => h.getBoundingClientRect().height > 0),
    intakeVisible: (() => { const h = document.getElementById('session-example'); return !!h && h.getBoundingClientRect().height > 0; })(),
  }));
  A('m1_mobile_loads', m.h2Visible.length === EXPECTED_H2.length, { h2: m.h2Visible.length });
  A('m2_no_horizontal_overflow', m.overflow <= 1, { overflowPx: m.overflow });
  A('m3_all_h2_visible_mobile', m.h2Visible.every(Boolean), { hidden: m.h2Visible.filter(v => !v).length });
  A('m4_intake_section_visible_mobile', m.intakeVisible === true, {});
  await mctx.close();

  await browser.close();
  const finishedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  const passed = assertions.filter(a => a.pass).length;
  const receipt = {
    packet: 'TN-REMOTE-PREVIEW-RENDER-20261115',
    run_id: runId,
    started_utc: startedUtc,
    finished_utc: finishedUtc,
    label: 'LOCAL_STAGING existing tools (playwright ' + bv + ', headless, file:// standalone)',
    source: {
      commit: SOURCE_COMMIT,
      file: 'content/remote-intake-example-20261115/remote-support-with-intake.preview.html',
      blob_sha256: blobSha,
      bytes: blob.length,
    },
    assertions,
    summary: { total: assertions.length, passed, failed: assertions.length - passed },
    scope: { form_posts: 0, screenshots: 0, traces: 0, public_url: 'none', external_navigations: 0 },
    limitations: [
      'STANDALONE static render — does NOT prove WordPress shortcode/theme rendering: [tehnet_phone] and [tn_editorial_note] remain literal text here (d7/d8 assert their literal preservation in source).',
      'WordPress-integration claim remains NOT_RUN: the intake fragment is NOT_DEPLOYED to staging, so no fixture render of the integrated page exists.',
      'Keyboard check verifies focus traversal only (no Enter activation, no navigations).',
    ],
    production_touched: false,
  };
  fs.writeFileSync(OUT, JSON.stringify(receipt, null, 1));
  console.log('\nTOTAL=' + assertions.length + ' PASS=' + passed + ' FAIL=' + (assertions.length - passed));
  console.log('WROTE ' + OUT);
  process.exitCode = (assertions.length - passed) ? 1 : 0;
})().catch(e => { console.error('RUNNER ERROR:', String(e.message).split('\n')[0]); process.exitCode = 1; });
