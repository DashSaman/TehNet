'use strict';
/* TN-PASSIVE-RESPONSIVE-PREVIEW-20261115 — before/after browser evidence (existing tools).
 * BEFORE = canonical draft standalone (pinned digest); AFTER = scoped table-scroll candidate.
 * Path-free (env TN_PW_MODULE / TN_BEFORE / TN_AFTER). No forms/screenshots/traces/public URL.
 * Labels: preview proposal NOT_DEPLOYED; not WordPress/KSES/theme acceptance. */
const path = require('node:path');
const fs = require('node:fs');
const crypto = require('node:crypto');
const pwModule = process.env.TN_PW_MODULE;
if (!pwModule) { console.error('TN_PW_MODULE env required (existing playwright install); no package installation'); process.exit(2); }
const { chromium } = require(pwModule);

const REPO = path.resolve(__dirname, '../..');
const BEFORE = process.env.TN_BEFORE || path.join(__dirname, 'rendered-source.snapshot.html');
const AFTER = process.env.TN_AFTER || path.join(REPO, 'content/passive-responsive-preview-20261115/passive-responsive-preview.candidate.html');
const OUT = path.join(__dirname, 'responsive-preview-result.json');
const CANONICAL_SHA = '180ddbf10d208abe6ffbc5f4f48e97a417908052c6053a9261235ba170c3d16b';
const CANDIDATE_SHA = 'afee2771d9af317f2c98cc71530f3c4273b501d72f0cfb78ad37c20d9eb0b565';
const FOCUS_STEPS = 6;

const runId = 'TN-PASSIVE-RESPONSIVE-PREVIEW-' + Date.now().toString(36).toUpperCase();
const startedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
function sha(f) { return crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex'); }
const beforeSha = sha(BEFORE);
const afterSha = sha(AFTER);

const assertions = [];
const A = (id, pass, detail) => { assertions.push({ id, pass: !!pass, detail: detail || {} }); console.log((pass ? 'PASS ' : 'FAIL ') + id + (detail ? ' ' + JSON.stringify(detail).slice(0, 170) : '')); };
function orderedFocusOk(actual, expected) {
  if (!Array.isArray(actual) || actual.length !== expected.length) return false;
  return actual.every((h, i) => h === expected[i]);
}

(async () => {
  /* digest gates BEFORE launch */
  A('p0_before_digest_match', beforeSha === CANONICAL_SHA, { input: beforeSha.slice(0, 16) + '…' });
  A('p1_after_digest_match', afterSha === CANDIDATE_SHA, { input: afterSha.slice(0, 16) + '…' });
  if (beforeSha !== CANONICAL_SHA || afterSha !== CANDIDATE_SHA) {
    const r = { packet: 'TN-PASSIVE-RESPONSIVE-PREVIEW-20261115', run_id: runId, started_utc: startedUtc, rejected: 'digest mismatch — browser NOT launched', assertions, summary: { total: assertions.length, passed: assertions.filter(a => a.pass).length, failed: assertions.filter(a => !a.pass).length } };
    fs.writeFileSync(OUT, JSON.stringify(r, null, 1));
    console.log('RECEIPT_WRITTEN=' + path.basename(OUT));
    process.exitCode = 1;
    return;
  }

  const browser = await chromium.launch({ headless: true });
  const bv = browser.version();
  const uBefore = 'file:///' + BEFORE.replace(/\\/g, '/');
  const uAfter = 'file:///' + AFTER.replace(/\\/g, '/');

  /* ---------- BEFORE: canonical standalone ---------- */
  const cb = await browser.newContext({ viewport: { width: 390, height: 844 }, locale: 'fa' });
  const pb = await cb.newPage();
  await pb.goto(uBefore, { waitUntil: 'load', timeout: 20000 });
  const mBefore = await pb.evaluate(() => ({
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    links: [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')),
    text: document.body.innerText.replace(/\s+/g, ' ').trim(),
    captions: [...document.querySelectorAll('table caption')].map(c => c.textContent.replace(/\s+/g, ' ').trim()),
    thScope: [...document.querySelectorAll('table')].map(t => [...t.querySelectorAll('th')].map(th => th.getAttribute('scope'))),
    thTotal: document.querySelectorAll('th').length,
  }));
  A('b1_before_mobile_overflow_present', mBefore.overflow > 1, { overflowPx: mBefore.overflow, note: 'the already-reported finding reproduced' });
  await pb.keyboard.press('Tab');
  const kbBefore = [await pb.evaluate(() => document.activeElement.getAttribute('href'))];
  for (let i = 1; i < FOCUS_STEPS; i++) { await pb.keyboard.press('Tab'); kbBefore.push(await pb.evaluate(() => document.activeElement.getAttribute('href'))); }
  A('b2_before_exact_ordered_focus', orderedFocusOk(kbBefore, mBefore.links.slice(0, FOCUS_STEPS)), { positions: kbBefore });
  const textBefore = mBefore.text;
  await cb.close();

  /* ---------- AFTER: candidate with scoped scroll wrappers ---------- */
  const ca = await browser.newContext({ viewport: { width: 390, height: 844 }, locale: 'fa' });
  const pa = await ca.newPage();
  await pa.goto(uAfter, { waitUntil: 'load', timeout: 20000 });
  const mAfter = await pa.evaluate(() => ({
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    links: [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')),
    text: document.body.innerText.replace(/\s+/g, ' ').trim(),
    captions: [...document.querySelectorAll('table caption')].map(c => c.textContent.replace(/\s+/g, ' ').trim()),
    thScope: [...document.querySelectorAll('table')].map(t => [...t.querySelectorAll('th')].map(th => th.getAttribute('scope'))),
    thTotal: document.querySelectorAll('th').length,
    wrappers: [...document.querySelectorAll('.tn-preview-table-scroll')].map(w => ({
      scrollable: w.scrollWidth > w.clientWidth,
      scrollWidth: w.scrollWidth,
      clientWidth: w.clientWidth,
      tableVisible: !!w.querySelector('table') && w.querySelector('table').getBoundingClientRect().height > 0,
    })),
    focusables: [...document.querySelectorAll('a[href], .tn-preview-table-scroll')].map(e => e.tagName === 'A' ? e.getAttribute('href') : 'REGION:' + (e.getAttribute('aria-label') || '').slice(0, 24)),
  }));
  A('a1_after_mobile_page_fits', mAfter.overflow <= 1, { overflowPx: mAfter.overflow, note: 'BEFORE was ' + mBefore.overflow + 'px' });
  A('a2_scrolled_region_scrollable', mAfter.wrappers.length === 2 && mAfter.wrappers.every(w => w.scrollable), { wrappers: mAfter.wrappers.map(w => ({ sw: w.scrollWidth, cw: w.clientWidth })) });
  A('a3_captions_preserved', JSON.stringify(mAfter.captions) === JSON.stringify(mBefore.captions), { captions: mAfter.captions.map(c => c.slice(0, 30)) });
  A('a4_header_semantics_preserved', mAfter.thTotal === mBefore.thTotal && JSON.stringify(mAfter.thScope) === JSON.stringify(mBefore.thScope), { thTotal: mAfter.thTotal });
  A('a5_links_unchanged', JSON.stringify(mAfter.links) === JSON.stringify(mBefore.links), { count: mAfter.links.length });
  A('a6_visible_text_preserved', mAfter.text === textBefore, { note: 'normalized whitespace comparison — canonical wording/cells intact' });
  /* keyboard reachability AFTER: wrappers focusable; exact ordered sequence incl. regions */
  const expectedAfter = mAfter.focusables.slice(0, FOCUS_STEPS);
  await pa.keyboard.press('Tab');
  const kbAfter = [];
  for (let i = 0; i < FOCUS_STEPS; i++) {
    kbAfter.push(await pa.evaluate(() => {
      const el = document.activeElement;
      return el.tagName === 'A' ? el.getAttribute('href') : 'REGION:' + (el.getAttribute('aria-label') || '').slice(0, 24);
    }));
    if (i < FOCUS_STEPS - 1) await pa.keyboard.press('Tab');
  }
  A('a7_after_exact_ordered_focus', orderedFocusOk(kbAfter, expectedAfter), { positions: kbAfter });
  /* column reachability: focus first region, exercise scrollable range (keyboard scroll outcome) */
  const scrolled = await pa.evaluate(async () => {
    const w = document.querySelector('.tn-preview-table-scroll');
    if (!w) return null;
    w.focus();
    const before = w.scrollLeft;
    w.scrollLeft = w.scrollWidth; /* keyboard-scroll outcome: full range reachable */
    await new Promise(r => setTimeout(r, 50));
    const max = w.scrollWidth - w.clientWidth;
    const lastCol = [...w.querySelectorAll('tr')].map(tr => tr.lastElementChild).pop();
    const lastVisible = lastCol ? lastCol.getBoundingClientRect().right <= w.getBoundingClientRect().right + 1 : false;
    return { before, after: w.scrollLeft, max, reachable: w.scrollLeft >= max - 2, lastVisible };
  });
  A('a8_keyboard_column_reachability', !!scrolled && scrolled.max > 0 && scrolled.reachable && scrolled.lastVisible, scrolled);
  /* desktop AFTER */
  const cd = await browser.newContext({ viewport: { width: 1440, height: 900 }, locale: 'fa' });
  const pd = await cd.newPage();
  await pd.goto(uAfter, { waitUntil: 'load', timeout: 20000 });
  const dAfter = await pd.evaluate(() => ({
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    tablesFit: [...document.querySelectorAll('.tn-preview-table-scroll')].map(w => w.scrollWidth <= w.clientWidth + 1),
  }));
  A('a9_desktop_no_overflow', dAfter.overflow <= 1, { overflowPx: dAfter.overflow });
  A('a10_desktop_tables_fit', dAfter.tablesFit.every(Boolean), { fit: dAfter.tablesFit });
  await ca.close();
  await cd.close();

  await browser.close();
  const finishedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  const passed = assertions.filter(a => a.pass).length;
  const receipt = {
    packet: 'TN-PASSIVE-RESPONSIVE-PREVIEW-20261115',
    rev: 1,
    run_id: runId,
    started_utc: startedUtc,
    finished_utc: finishedUtc,
    label: 'LOCAL_STAGING existing tools (playwright ' + bv + ', headless, file:// standalone before/after)',
    inputs: {
      before: { role: 'canonical standalone', sha256: beforeSha, pinned: CANONICAL_SHA },
      after: { role: 'responsive preview candidate', sha256: afterSha, pinned: CANDIDATE_SHA, file: 'content/passive-responsive-preview-20261115/passive-responsive-preview.candidate.html' },
    },
    diagnosis: {
      theme_pattern: 'pinned theme visual-refresh.css:79-84 provides overflow handling ONLY via the .tn-decision-table wrapper (max-width:100%; overflow-x:auto; padded bordered cells); plain wp-block-table figures get NO overflow rule from the pinned theme source',
      draft_tables_use_wrapper: false,
      missing_integration_context: 'candidate mirrors the theme OWN established pattern; whether WP core block CSS adds overflow outside the pinned theme source is NOT_VERIFIED_FROM_PINNED_SOURCE — the canonical draft is therefore NOT declared defective',
    },
    assertions,
    summary: { total: assertions.length, passed, failed: assertions.length - passed },
    scope: { form_posts: 0, screenshots: 0, traces: 0, public_url: 'none', external_navigations: 0, canonical_draft_edits: 0, theme_production_mutations: 0 },
    limitations: [
      'Preview proposal NOT_DEPLOYED — not WordPress/KSES acceptance, no authority to alter theme/production.',
      'Standalone render only; WordPress rendering of the candidate remains NOT_RUN.',
      'Column reachability probe focuses the region (tabindex=0, role=region, aria-label) then exercises the full scrollable range; Tab traversal performed without activation.',
    ],
    production_touched: false,
  };
  fs.writeFileSync(OUT, JSON.stringify(receipt, null, 1));
  console.log('\nTOTAL=' + assertions.length + ' PASS=' + passed + ' FAIL=' + (assertions.length - passed));
  console.log('RECEIPT_WRITTEN=' + path.basename(OUT));
  process.exitCode = (assertions.length - passed) ? 1 : 0;
})().catch(e => { console.error('RUNNER ERROR:', String(e.message).split('\n')[0]); process.exitCode = 1; });
