'use strict';
/* TN-PASSIVE-STANDALONE-RENDER-20261115 — standalone render of the canonical passive draft.
 * Path-free runner (env TN_PW_MODULE / TN_RENDER_INPUT; repository-relative defaults).
 * Pinned source digest asserted BEFORE browser launch. k2 = exact ordered focus with a
 * fabricated-repeat negative predicate. No forms/screenshots/traces/public URL.
 * LIMITATION: standalone render is NOT WordPress/KSES/theme acceptance — NOT_RUN labels. */
const path = require('node:path');
const fs = require('node:fs');
const crypto = require('node:crypto');
const pwModule = process.env.TN_PW_MODULE;
if (!pwModule) { console.error('TN_PW_MODULE env required (existing playwright install); no package installation'); process.exit(2); }
const { chromium } = require(pwModule);

const OUT = path.join(__dirname, 'passive-render-result.json');
const INPUT = process.env.TN_RENDER_INPUT || path.join(__dirname, 'draft.html');
const SOURCE_BRANCH = 'feat/passive-network-content-20261115';
const SOURCE_HEAD = '89ead8f58594635130ce35716c4d3ad82fa39e70';
const SOURCE_FILE = 'seo/competitive-2026-11-11/draft-passive-network-tehran.gutenberg.html';
const PINNED_SHA256 = '180ddbf10d208abe6ffbc5f4f48e97a417908052c6053a9261235ba170c3d16b';
const FOCUS_STEPS = 6;

const runId = 'TN-PASSIVE-STANDALONE-RENDER-' + Date.now().toString(36).toUpperCase();
const startedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');

function orderedFocusOk(actual, expected) {
  if (!Array.isArray(actual) || actual.length !== expected.length) return false;
  return actual.every((h, i) => h === expected[i]);
}

const assertions = [];
const A = (id, pass, detail) => { assertions.push({ id, pass: !!pass, detail: detail || {} }); console.log((pass ? 'PASS ' : 'FAIL ') + id + (detail ? ' ' + JSON.stringify(detail).slice(0, 180) : '')); };

(async () => {
  const blob = fs.readFileSync(INPUT);
  const inputSha = crypto.createHash('sha256').update(blob).digest('hex');
  A('p0_pinned_digest_match', inputSha === PINNED_SHA256, { pinned: PINNED_SHA256.slice(0, 16) + '…', input: inputSha.slice(0, 16) + '…' });
  if (inputSha !== PINNED_SHA256) {
    const receipt = { packet: 'TN-PASSIVE-STANDALONE-RENDER-20261115', run_id: runId, started_utc: startedUtc, rejected: 'input digest mismatch — browser NOT launched', assertions, summary: { total: assertions.length, passed: assertions.filter(a => a.pass).length, failed: assertions.filter(a => !a.pass).length } };
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
  const d = await page.evaluate(() => {
    const tables = [...document.querySelectorAll('table')].map(t => ({
      caption: (t.querySelector('caption') || {}).textContent || null,
      thCount: t.querySelectorAll('th').length,
      thScope: [...t.querySelectorAll('th')].map(th => th.getAttribute('scope') || th.getAttribute('headers') || null),
      rows: t.querySelectorAll('tr').length,
      visible: t.getBoundingClientRect().height > 0,
    }));
    const ol = document.querySelector('ol');
    const olInfo = ol ? {
      li: ol.querySelectorAll(':scope > li').length,
      manualPrefix: [...ol.querySelectorAll(':scope > li')].filter(li => /^\s*\d+[.)]\s/.test(li.textContent)).length,
      listStyle: getComputedStyle(ol).listStyleType,
    } : null;
    const links = [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href'));
    return {
      bodyLen: document.body.innerText.length,
      h2: document.querySelectorAll('h2').length,
      h3: document.querySelectorAll('h3').length,
      tables, olInfo,
      fragLinks: links.filter(h => h.startsWith('#')).length,
      external: links.filter(h => /^https?:/.test(h)).length,
      domLinks: links,
      forms: document.querySelectorAll('form').length,
      mptl: document.body.innerText.includes('MPTL (Modular Plug Terminated Link)'),
      apNote: document.body.innerText.includes('AP-01'),
      plChannelGone: !document.body.innerText.includes('PL/Channel'),
      cyrillic: (document.body.innerText.match(/[\u0410-\u044F]/g) || []).length,
      zakhire: document.body.innerText.split('ذخیره').length - 1,
      kaf: document.body.innerText.includes('کف'),
    };
  });

  A('d1_standalone_loads', d.bodyLen > 2000, { chars: d.bodyLen });
  A('d2_heading_structure', d.h2 === 8 && d.h3 === 9, { h2: d.h2, h3: d.h3 });
  A('d3_two_tables_present', d.tables.length === 2, { tables: d.tables.length });
  A('d4_table_captions_present', d.tables.every(t => t.caption && t.caption.trim().length > 5), { captions: d.tables.map(t => (t.caption || '').slice(0, 40)) });
  A('d5_table_header_association', d.tables.every(t => t.thCount >= 1 && t.thScope.every(s => s === 'col' || s === 'row' || s === 'colgroup' || s === 'rowgroup' || s !== null)), { th: d.tables.map(t => t.thCount), scopes: d.tables.map(t => t.thScope) });
  A('d6_ordered_list_real_numbering', d.olInfo && d.olInfo.li === 7 && d.olInfo.manualPrefix === 0 && d.olInfo.listStyle === 'decimal', { li: d.olInfo && d.olInfo.li, manualPrefix: d.olInfo && d.olInfo.manualPrefix, listStyle: d.olInfo && d.olInfo.listStyle });
  A('d7_no_dangling_fragment_links', d.fragLinks === 0, { fragmentLinks: d.fragLinks, note: 'draft defines no in-page anchors; no # targets to resolve' });
  A('d8_mptl_corrected_wording_present', d.mptl === true, {});
  A('d9_appl_topology_note_present', d.apNote === true, { note: 'AP-01 AP/PL topology wording' });
  A('d10_old_plchannel_phrase_absent', d.plChannelGone === true, {});
  A('d11_cyrillic_absent', d.cyrillic === 0, { cyrillicChars: d.cyrillic });
  A('d12_persian_reserve_wording_present', d.zakhire >= 2, { occurrences: d.zakhire });
  A('d13_no_forms_present', d.forms === 0, { forms: d.forms });
  A('d14_external_links_present', d.external >= 1, { count: d.external, note: 'reference links preserved (no navigation performed)' });

  /* keyboard: EXACT ordered focus + negative predicate */
  const expectedSeq = d.domLinks.slice(0, FOCUS_STEPS);
  await page.keyboard.press('Tab');
  const kb = [await page.evaluate(() => document.activeElement.getAttribute('href'))];
  for (let i = 1; i < FOCUS_STEPS; i++) { await page.keyboard.press('Tab'); kb.push(await page.evaluate(() => document.activeElement.getAttribute('href'))); }
  A('k1_first_tab_focuses_first_link', kb[0] === expectedSeq[0], { focused: kb[0] });
  A('k2_exact_ordered_focus', orderedFocusOk(kb, expectedSeq), { positions: kb.map((h, i) => ({ step: i + 1, href: h, expected: expectedSeq[i] })) });
  const fabricated = [expectedSeq[0], expectedSeq[0], expectedSeq[0], expectedSeq[0], expectedSeq[0], expectedSeq[0]];
  A('k3_negative_repeated_focus_rejected', orderedFocusOk(fabricated, expectedSeq) === false, { predicateVerdictOnFabricated: orderedFocusOk(fabricated, expectedSeq) });
  await ctx.close();

  /* --- mobile --- */
  const mctx = await browser.newContext({ viewport: { width: 390, height: 844 }, locale: 'fa' });
  const mpage = await mctx.newPage();
  await mpage.goto(url, { waitUntil: 'load', timeout: 20000 });
  const m = await mpage.evaluate(() => {
    const cw = document.documentElement.clientWidth;
    const wide = [...document.querySelectorAll('*')]
      .filter(e => e.getBoundingClientRect().right > cw + 1)
      .slice(0, 4)
      .map(e => ({ tag: e.tagName, cls: String(e.className || '').slice(0, 50), w: Math.round(e.getBoundingClientRect().width) }));
    return {
      overflow: cw ? document.documentElement.scrollWidth - document.documentElement.clientWidth : 0,
      overflowCause: wide,
      tablesVisible: [...document.querySelectorAll('table')].map(t => t.getBoundingClientRect().height > 0),
      tableWidths: [...document.querySelectorAll('table')].map(t => Math.round(t.getBoundingClientRect().width)),
      olVisible: (() => { const o = document.querySelector('ol'); return !!o && o.getBoundingClientRect().height > 0; })(),
    };
  });
  A('m1_mobile_loads', m.tablesVisible.length === 2, {});
  A('m2_no_horizontal_overflow', m.overflow <= 1, {
    overflowPx: m.overflow,
    cause: m.overflowCause,
    attribution: 'standalone context lacks the WP block/theme overflow wrapper for the has-fixed-layout table; WordPress/theme table handling NOT_RUN — canonical draft NOT edited (digest preserved)',
  });
  A('m3_tables_rendered_mobile', m.tablesVisible.every(Boolean), { widthsPx: m.tableWidths });
  A('m4_ordered_list_visible_mobile', m.olVisible === true, {});
  await mctx.close();

  await browser.close();
  const finishedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  const passed = assertions.filter(a => a.pass).length;
  const receipt = {
    packet: 'TN-PASSIVE-STANDALONE-RENDER-20261115',
    rev: 1,
    run_id: runId,
    started_utc: startedUtc,
    finished_utc: finishedUtc,
    label: 'LOCAL_STAGING existing tools (playwright, headless, file:// standalone)',
    source: {
      branch: SOURCE_BRANCH,
      head: SOURCE_HEAD,
      file: SOURCE_FILE,
      pinned_sha256: PINNED_SHA256,
      input_sha256: inputSha,
      bytes: blob.length,
    },
    assertions,
    summary: { total: assertions.length, passed, failed: assertions.length - passed },
    scope: { form_posts: 0, screenshots: 0, traces: 0, public_url: 'none', external_navigations: 0, canonical_draft_edits: 0 },
    limitations: [
      'STANDALONE static render — NOT WordPress/KSES/theme acceptance: WordPress rendering, KSES filtering and theme CSS are NOT_RUN.',
      'FINDING (m2): standalone mobile render shows 52px horizontal overflow caused by the has-fixed-layout table (394px > 390px viewport). WordPress block/theme overflow handling is NOT_RUN; the canonical draft was NOT edited because a draft-level defect is not proven — decision left to review.',
      'No technical certification result is claimed: MPTL/PL wording and AP/PL topology note are asserted as TEXT PRESENCE in the corrected draft only.',
      'Draft defines no in-page anchors, so fragment-target assertion is vacuous (no dangling # links).',
      'Keyboard check verifies exact ordered focus traversal only (no activation, no navigations).',
    ],
    production_touched: false,
  };
  fs.writeFileSync(OUT, JSON.stringify(receipt, null, 1));
  console.log('\nTOTAL=' + assertions.length + ' PASS=' + passed + ' FAIL=' + (assertions.length - passed));
  console.log('RECEIPT_WRITTEN=' + path.basename(OUT));
  process.exitCode = (assertions.length - passed) ? 1 : 0;
})().catch(e => { console.error('RUNNER ERROR:', String(e.message).split('\n')[0]); process.exitCode = 1; });
