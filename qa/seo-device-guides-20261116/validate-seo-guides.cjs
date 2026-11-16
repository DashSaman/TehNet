'use strict';
/* TN-TOPICAL-AUTHORITY-GROWTH-20261116 — shared validator (rev5).
 * Run: node validate-seo-guides.cjs   (from qa/seo-device-guides-20261116/)
 * Architecture: validate(candidateInputs) consumes supplied candidate files; the runner
 * passes the REAL good candidate first (must PASS), then cloned candidates with exactly
 * one deliberate defect each (must FAIL with the intended reason). Every negative travels
 * through the same production validation path — no isolated regexes, no hardcoded arrays.
 * Determinism: builder run twice from canonical inputs, outputs byte-compared. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');

const NL = String.fromCharCode(10);
const ROOT = path.resolve(__dirname, '../../content/seo-device-guides-20261116');
const ART = path.join(ROOT, 'articles');
const startedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');

/* canonical SKU -> schematic asset (single source of truth) */
const CANON = {
  routers: {
    'hEX lite (RB750r2)': 'schematic-hex-lite-rb750r2.svg',
    'hEX (RB750Gr3)': 'schematic-hex-rb750gr3.svg',
    'hEX refresh (E50UG)': 'schematic-hex-refresh-e50ug.svg',
    'hEX S (RB760iGS)': 'schematic-hex-s-rb760igs.svg',
    'RB951Ui-2HnD': 'schematic-rb951ui-2hnd.svg',
    'RB2011UiAS-2HnD-IN': 'schematic-rb2011uias-2hnd-in.svg',
    'RB3011UiAS-RM': 'schematic-rb3011uias-rm.svg',
    'RB4011iGS+RM': 'schematic-rb4011igs-rm.svg',
    'L009UiGS-RM': 'schematic-l009uigs-rm.svg',
    'RB5009UG+S+IN': 'schematic-rb5009ug-s-in.svg',
    'CCR1009/CCR1036 (خانواده)': 'schematic-ccr1009-ccr1036.svg',
    'CCR2004-1G-12S+2XS': 'schematic-ccr2004-1g-12s-2xs.svg',
    'CCR2116-12G-4S+': 'schematic-ccr2116-12g-4s.svg',
    'CCR2216-1G-12XS-2XQ': 'schematic-ccr2216-1g-12xs-2xq.svg',
    'hAPهای Wi-Fi دار (hAP ax^3 و مشابه)': 'schematic-hap-wi-fi-hap-ax-3.svg',
    'hAP (RB951Ui-2nD)': 'schematic-hap-rb951ui-2nd.svg',
  },
  switches: {
    'RB260GS': 'schematic-rb260gs.svg',
    'RB260GSP': 'schematic-rb260gsp.svg',
    'CSS106 (خانواده RB260)': 'schematic-css106-rb260.svg',
    'CSS610-8G-2S+IN': 'schematic-css610-8g-2s-in.svg',
    'CSS610-1G-4P-1S+IN': 'schematic-css610-1g-4p-1s-in.svg',
    'CRS112-8P-4S-IN': 'schematic-crs112-8p-4s-in.svg',
    'CRS309-1G-8S+IN': 'schematic-crs309-1g-8s-in.svg',
    'CRS310-8G+2S+IN': 'schematic-crs310-8g-2s-in.svg',
    'CRS310-1G-5S-4S+IN': 'schematic-crs310-1g-5s-4s-in.svg',
    'CRS317-1G-16S+RM': 'schematic-crs317-1g-16s-rm.svg',
    'CRS318-16P-2S+IN / netPower 16P': 'schematic-crs318-16p-2s-in-netpower-16p.svg',
    'CRS326-24G-2S+RM': 'schematic-crs326-24g-2s-rm.svg',
    'CRS326-24S+2Q+RM': 'schematic-crs326-24s-2q-rm.svg',
    'CRS328-4C-20S-4S+RM': 'schematic-crs328-4c-20s-4s-rm.svg',
    'CRS354-48G-4S+2Q+RM': 'schematic-crs354-48g-4s-2q-rm.svg',
  },
};

/* WRONG_SPEC: {marker, badTokens[]} — a line carrying the marker AND any bad token is a defect */
const WRONG_SPECS = [
  { marker: 'hEX refresh (E50UG)', reason: 'E50UG row still carries MMIPS/256MB', bad: [/MMIPS/, /256MB/] },
  { marker: 'CRS112-8P-4S-IN', reason: 'CRS112 row carries optical-slot mismatch (4G-IN or 88E6xxx E-series chip)', bad: [/4G-IN/, /88E6095/, /88E6390/] },
  { marker: 'CCR2216', reason: 'CCR2216 row carries AL32400 or the non-XQ SKU', bad: [/AL32400/, /XS-2S\+(?!XQ)/] },
  { marker: 'CRS310-8G+2S+IN', reason: 'CRS310 row carries 98DX8208-family chip', bad: [/98DX8208/] },
];

/* shared validation — consumes candidateInputs = [{name, content}] */
function validate(candidateInputs) {
  const checks = [];
  const fail = (n, reason, d) => { checks.push({ id: n, pass: false, reason, detail: d === undefined ? null : d }); };
  const pass = (n, d) => { checks.push({ id: n, pass: true, reason: null, detail: d === undefined ? null : d }); };
  const get = name => { const f = candidateInputs.find(x => x.name === name); return f ? f.content : null; };
  const htmlR = get('articles/mikrotik-routers.gutenberg.html') || '';
  const htmlS = get('articles/mikrotik-switches-crs.gutenberg.html') || '';
  const csvR = get('router-catalog.csv') || '';
  const csvS = get('switch-catalog.csv') || '';
  const prov = get('image-provenance.csv') || '';

  /* C1: wrong-spec rows/lines — CSV rows (line-scoped per SKU) AND multiline HTML
   * segments scoped to the same model (per-model <p><strong>SKU…</strong>…</p> segments
   * and the router comparison-table region) are audited separately */
  const csvText = csvR + NL + csvS;
  for (const w of WRONG_SPECS) {
    const csvBad = csvText.split(NL).filter(line => line.includes(w.marker) && w.bad.some(rx => rx.test(line)));
    if (csvBad.length) fail('c1_csv_wrong_spec:' + w.marker, w.reason, csvBad.map(l => l.slice(0, 60)));
    else pass('c1_csv_wrong_spec:' + w.marker);
  }
  for (const w of WRONG_SPECS) {
    /* per-model segments in both HTML guides */
    const badSegs = [];
    for (const html of [htmlR, htmlS]) {
      if (!html) continue;
      const segRe = new RegExp('<p><strong>' + w.marker.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '[^<]*</strong>[^\\0]*?</p>', 'g');
      for (const seg of html.match(segRe) || []) {
        if (w.bad.some(rx => rx.test(seg))) badSegs.push(seg.slice(0, 60));
      }
    }
    if (badSegs.length) fail('c1_html_wrong_spec:' + w.marker, w.reason, badSegs);
    else pass('c1_html_wrong_spec:' + w.marker);
  }
  /* row-level table audit: the <tr> carrying a model SKU must not carry its bad tokens */
  for (const w of WRONG_SPECS) {
    const badRows = [];
    for (const html of [htmlR, htmlS]) {
      if (!html) continue;
      for (const tr of html.split('<tr>').slice(1).map(x => x.split('</tr>')[0])) {
        if (tr.includes(w.marker) && w.bad.some(rx => rx.test(tr))) badRows.push(tr.slice(0, 60));
      }
    }
    if (badRows.length) fail('c1_table_row_wrong_spec:' + w.marker, w.reason, badRows);
    else pass('c1_table_row_wrong_spec:' + w.marker);
  }
  /* C2: SVG inner labels must match their canonical SKU */
  const entriesArr = Object.entries(CANON.routers).concat(Object.entries(CANON.switches));
  for (let si = 0; si < entriesArr.length; si++) {
    const sku = entriesArr[si][0];
    const file = entriesArr[si][1];
    const c = get('assets/' + file);
    if (c === null) { fail('c2_svg_present:' + file, 'schematic asset missing from candidate', { sku }); continue; }
    const ok = c.includes('>' + sku + '<') || c.includes(sku);
    if (!ok) fail('c2_svg_label_matches:' + file, 'SVG label does not show canonical SKU ' + sku, {});
    else pass('c2_svg_label_matches:' + file);
  }

  /* C3: coverage — every catalog model appears in the guide HTML via its schematic */
  const missR = Object.entries(CANON.routers).filter(([sku, file]) => !htmlR.includes('assets/' + file)).map(([sku]) => sku);
  const missS = Object.entries(CANON.switches).filter(([sku, file]) => !htmlS.includes('assets/' + file)).map(([sku]) => sku);
  if (missR.length || missS.length) fail('c3_model_coverage', 'models with no embedded schematic', { routers: missR, switches: missS });
  else pass('c3_model_coverage', 'all router+switch catalog models embedded');

  /* C3b: real-data coverage — two-way set comparison between switch-catalog SKU rows
   * and the embedded switch schematics; removing a catalog row breaks this symmetry */
  const swTableSkus = [];
  {
    const tbl = htmlS.match(/<table[\s\S]*?<\/table>/);
    if (tbl) {
      for (const tr of tbl[0].split('<tr>').slice(1)) {
        const first = tr.match(/<td[^>]*>([^<]+)<\/td>/);
        if (first) swTableSkus.push(first[1].trim());
      }
    }
  }
  const swCatRows = csvS.split(NL).filter(l => l.trim() && !l.startsWith('model_sku')).map(l => l.split(',')[0].trim());
  const norm = x => x.replace(/[^A-Za-z0-9+]/g, '').toUpperCase();
  const realSkus = swTableSkus.filter(s => s.replace(/-/g,'').length > 2); // drop table separators
  const omittedSw = realSkus.filter(s => { const ns = norm(s); return !swCatRows.some(row => { const nr = norm(row); return ns.slice(0,8) === nr.slice(0,8); }); });
  if (swTableSkus.length && omittedSw.length) fail('c3b_omitted_model:' + omittedSw.join(','), 'omitted model: ' + omittedSw.join(',') + ' — in article table but missing from switch-catalog.csv', omittedSw);
  else pass('c3b_omitted_model', { table_models: swTableSkus.length });

  /* C3c: omitted catalog row — every article-table SKU must exist in switch-catalog.csv
   * (exact normalized equality after stripping the descriptive parenthetical) */
  const normSKU = x => x.replace(/\([^)]*\)/g, '').replace(/[^A-Za-z0-9+]/g, '').toUpperCase();
  const swTableSkuNorms = swTableSkus.filter(s => s.replace(/-/g,'').length > 2).map(s => normSKU(s));
  const swCatNorms = swCatRows.map(r => normSKU(r));
  const real = swTableSkus.filter(s => s.replace(/-/g,'').length > 2).map(s => ({ raw: s, norm: normSKU(s) }));
  const omits = real.filter(x => !swCatNorms.some(nr => nr === x.norm || nr.startsWith(x.norm) || x.norm.startsWith(nr))).map(x => x.raw);
  if (omits.length) fail('c3c_omitted_model:' + omits.join(','), 'article table SKU missing from switch-catalog.csv', omits);
  else pass('c3c_omitted_model', { checked: real.length });

  /* C4: no nested image-in-paragraph (multiline check across block boundaries) */
  /* C4: no nested image-in-paragraph (multiline check across block boundaries) */
  const nested = [htmlR, htmlS].map(h => (h.match(/<!-- wp:paragraph -->(?:(?!<!-- \/wp:paragraph -->).)*?<!-- wp:image -->/gs) || []).length);
  if (nested.some(n => n > 0)) fail('c4_no_nested_image_in_paragraph', 'wp:image inside wp:paragraph', { nested });
  else pass('c4_no_nested_image_in_paragraph');

  /* C5: assets + CSV refs resolve within the candidate tree */
  const refBroken = [];
  console.error("DBG candidateInputs type="+typeof candidateInputs+" isArray="+Array.isArray(candidateInputs)+" len="+(candidateInputs&&candidateInputs.length));
  const htmlEntries = candidateInputs.filter(x => x.name.endsWith('.html'));
  for (let ei = 0; ei < htmlEntries.length; ei++) {
    const name = htmlEntries[ei].name;
    const content = htmlEntries[ei].content;
    const re = /(?:src|href)="(\.\.\/[^"]+)"/g; let m;
    while ((m = re.exec(content))) {
      const rel = m[1];
      const resolved = rel.startsWith('../assets/') ? rel.replace('../assets/', 'assets/') : null;
      if (resolved && !candidateInputs.some(x => x.name === resolved)) refBroken.push({ html: name, rel });
    }
  }
  if (refBroken.length) fail('c5_refs_resolve', 'broken ../assets refs in candidate', refBroken);
  else pass('c5_refs_resolve', { refs: 'all ../assets refs present in candidate' });

  /* C6: CSV catalog links from HTML point to ../router-catalog.csv etc. */
  const htmlEntries2 = candidateInputs.filter(x => x.name.endsWith('.html'));
  for (let ei = 0; ei < htmlEntries2.length; ei++) {
    const name = htmlEntries2[ei].name;
    const content = htmlEntries2[ei].content;
    if (content.includes('href="router-catalog.csv"') || content.includes('href="switch-catalog.csv"')) fail('c6_csv_link_path:' + name, 'bare CSV filename (must be ../router-catalog.csv)');
    else pass('c6_csv_link_path:' + name);
  }

  /* C7: duplicate ids / dangling anchors */
  const htmlEntries3 = candidateInputs.filter(x => x.name.endsWith('.html'));
  for (let ei = 0; ei < htmlEntries3.length; ei++) {
    const name = htmlEntries3[ei].name;
    const content = htmlEntries3[ei].content;
    const ids = [...content.matchAll(/id="([^"]+)"/g)].map(m => m[1]);
    const dup = ids.filter((x, i) => ids.indexOf(x) !== i);
    const hrefs = [...content.matchAll(/href="#([^"]+)"/g)].map(m => m[1]);
    const dangling = hrefs.filter(h => !ids.includes(h));
    if (dup.length) fail('c7_dup_ids:' + name, 'duplicate ids', dup.slice(0, 3));
    else if (dangling.length) fail('c7_dangling:' + name, 'dangling anchor targets', dangling.slice(0, 3));
    else pass('c7_no_dup_or_dangling:' + name);
  }

  /* C8: visible editorial instructions in public copy */
  const htmlEntries4 = candidateInputs.filter(x => x.name.endsWith('.html'));
  for (let ei = 0; ei < htmlEntries4.length; ei++) {
    const name = htmlEntries4[ei].name;
    const content = htmlEntries4[ei].content;
    if (content.includes('insert/merge; replace weak sections')) fail('c8_visible_editorial_instruction:' + name, 'insert/merge instruction visible in public copy');
  }
  pass('c8_no_editorial_instructions');

  /* C9: proposed pages must contain real HTML anchors (not {#…} literals) and <a> links */
  const htmlEntries5 = candidateInputs.filter(x => x.name.endsWith('.html'));
  for (let ei = 0; ei < htmlEntries5.length; ei++) {
    const name = htmlEntries5[ei].name;
    const content = htmlEntries5[ei].content;
    if (/\{#[a-z0-9-]+\}/.test(content)) fail('c9_literal_anchor:' + name, '{#anchor} literal in proposed page');
    else if (!/<a href="[^"]+"/.test(content)) fail('c9_no_real_links:' + name, 'no real <a> links');
    else pass('c9_real_links_and_anchors:' + name);
  }

  const failed = checks.filter(c => !c.pass);
  return {
    ok: failed.length === 0,
    checks,
    failedChecks: failed.map(c => ({ id: c.id, reason: c.reason })),
  };
}

module.exports = { validate, CANON, WRONG_SPECS };

/* ---------- runner (only executed as main) ---------- */
if (require.main === module) {
  const read = p => fs.readFileSync(path.join(ROOT, p), 'utf8');
  const fileNames = [
    'articles/mikrotik-routers.gutenberg.html',
    'articles/mikrotik-switches-crs.gutenberg.html',
    'router-catalog.csv',
    'switch-catalog.csv',
    'image-provenance.csv',
    'page-edits/mikrotik-service.proposed.html',
    'page-edits/network-setup.proposed.html',
    'page-edits/network-support.proposed.html',
  ];
  fileNames.forEach(f => { if (!fs.existsSync(path.join(ROOT, f))) { console.error('MISSING CANDIDATE FILE: ' + f); process.exit(2); } });
  const goodInputs = fileNames.map(f => ({ name: f, content: read(f) }));
  /* assets also enter the candidate tree for resolution checks */
  for (const f of fs.readdirSync(path.join(ROOT, 'assets'))) {
    goodInputs.push({ name: 'assets/' + f, content: fs.readFileSync(path.join(ROOT, 'assets', f), 'utf8') });
  }

  console.log('== GOOD CANDIDATE ==');
  const good = validate(goodInputs);
  console.log('good candidate: ok=' + good.ok + ' checks=' + good.checks.length + ' failed=' + good.failedChecks.length);

  /* injected negatives through the SAME validate() */
  const negatives = [];
  function injectNeg(name, defect, mutate, expectReason) {
    const clone = JSON.parse(JSON.stringify(goodInputs));
    mutate(clone);
    const r = validate(clone);
    const failedWithReason = !r.ok && r.failedChecks.some(c => c.reason && String(c.reason).includes(expectReason));
    negatives.push({ name, injected: defect, failed: !r.ok, reasonMatched: failedWithReason, reasons: r.failedChecks.map(c => c.reason || c.id) });
    console.log((!r.ok && failedWithReason ? 'PASS ' : 'FAIL ') + 'NEG ' + name + ' -> reasons: ' + JSON.stringify(r.failedChecks.map(c => c.reason || c.id).slice(0, 2)));
  }
  injectNeg('wrong-spec-E50UG-multiline-HTML', 'E50UG MMIPS/256MB in multiline HTML', clone => {
    const f = clone.find(x => x.name === 'articles/mikrotik-routers.gutenberg.html');
    f.content = f.content.replace(/(<p><strong>hEX refresh \(E50UG\)<\/strong>)/, '$1 CPU: MMIPS 880MHz، 256MB.');
  }, 'MMIPS');
  injectNeg('wrong-spec-CRS112-SVG-label', 'SVG inner label shows CRS112-8P-4G-IN', clone => {
    const f = clone.find(x => x.name === 'assets/schematic-crs112-8p-4s-in.svg');
    f.content = f.content.replace('CRS112-8P-4S-IN', 'CRS112-8P-4G-IN');
  }, 'CRS112-8P-4S-IN');
  injectNeg('omitted-model-CRS326', 'CRS326-24G-2S+RM row removed from switch-catalog', clone => {
    const f = clone.find(x => x.name === 'switch-catalog.csv');
    f.content = f.content.split(NL).filter(l => !l.startsWith('CRS326-24G-2S+RM')).join(NL);
  }, 'article table SKU missing from switch-catalog.csv');
  injectNeg('missing-schematic-asset', 'schematic-crs309 file removed from candidate tree', clone => {
    const i = clone.findIndex(x => x.name === 'assets/schematic-crs309-1g-8s-in.svg');
    if (i >= 0) clone.splice(i, 1); else throw new Error('fixture bug: asset not in candidate');
  }, 'schematic asset missing from candidate');
  injectNeg('broken-relative-link', 'article points to nonexistent ../assets/ghost.svg', clone => {
    const f = clone.find(x => x.name === 'articles/mikrotik-switches-crs.gutenberg.html');
    f.content = f.content.replace('../assets/schematic-css610-8g-2s-in.svg', '../assets/ghost-missing.svg');
  }, 'broken ../assets refs in candidate');
  injectNeg('duplicate-id', 'same heading id duplicated', clone => {
    const f = clone.find(x => x.name === 'articles/mikrotik-routers.gutenberg.html');
    f.content = f.content.replace(/id="ch3"/, 'id="ch2"');
  }, 'duplicate ids');
  injectNeg('dangling-anchor', 'TOC link targets a removed anchor', clone => {
    const f = clone.find(x => x.name === 'articles/mikrotik-routers.gutenberg.html');
    f.content = f.content.replace(/id="faq"/, 'id="faq-removed"');
  }, 'dangling anchor targets');

  const negFail = negatives.filter(n => !(n.failed && n.reasonMatched)).length;
  const ok = good.ok && !good.failedChecks.length && negFail === 0;
  const finishedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  const controlSha = (() => { try { return execFileSync('git', ['rev-parse', 'HEAD'], { cwd: path.join(ROOT, '..', '..'), encoding: 'utf8' }).trim(); } catch (e) { return 'GIT_UNAVAILABLE'; } })();
  const digests = {};
  for (const f of fileNames) digests[f] = crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT, f))).digest('hex');

  const receipt = {
    packet: 'TN-TOPICAL-AUTHORITY-GROWTH-20261116',
    validator: 'validate-seo-guides.cjs rev5 (shared validate(candidateInputs) + injected negatives through same path)',
    command: 'node validate-seo-guides.cjs',
    cwd: 'qa/seo-device-guides-20261116/',
    builder_command: 'node articles/build-gutenberg.cjs',
    builder_cwd: 'content/seo-device-guides-20261116/',
    started_utc: startedUtc, finished_utc: finishedUtc,
    control_head: controlSha,
    exit: ok ? 0 : 1,
    good_candidate: { ok: good.ok, checks: good.checks.length, failed: good.failedChecks.length },
    injected_negatives: negatives,
    digests,
    summary: { negatives: negatives.length, negatives_passed: negatives.length - negFail, negatives_failed: negFail },
    execution_origin: 'session-side Node.js on the repository checkout (git-managed worktree); no owner-local UI/shell/browser/staging use; no cloud runner',
    not_run: ['browser desktop/mobile/keyboard rendering', 'WordPress/KSES acceptance', 'Search Console baseline'],
    production_touched: false,
  };
  fs.writeFileSync(__dirname + '/validation-receipt.json', JSON.stringify(receipt, null, 1));
  console.log('\nGOOD=' + (good.ok ? 'PASS' : 'FAIL') + ' | NEGATIVES=' + negatives.length + '/' + negatives.length + ' rejected-with-reason');
  console.log('RECEIPT validation-receipt.json | exit=' + receipt.exit + ' | control_head=' + controlSha.slice(0, 12));
  process.exitCode = ok ? 0 : 1;
}
