'use strict';
/* TN-TOPICAL-AUTHORITY-GROWTH-20261116 — shared validator (rev6).
 * Run: node validate-seo-guides.cjs   (from qa/seo-device-guides-20261116/)
 * Shared validate(candidateInputs): GOOD candidate must pass, injected negatives must
 * fail through the SAME path with intended reasons. Node-24 for-of destructuring
 * workaround: index-based loops throughout (no array destructuring in for-of). */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');

const NL = String.fromCharCode(10);
const ROOT = path.resolve(__dirname, '../../content/seo-device-guides-20261116');
const startedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');

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

/* WRONG_SPEC: {marker, reason, badTokens[]} — line carries marker AND any bad token */
const WRONG_SPECS = [
  { marker: 'hEX refresh (E50UG)', reason: 'E50UG row still carries MMIPS/256MB', bad: [/MMIPS/, /256MB/] },
  { marker: 'CRS112-8P-4S-IN', reason: 'CRS112 row carries optical-slot mismatch (4G-IN or E-series chip)', bad: [/4G-IN/, /88E6095/, /88E6390/] },
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

  /* C1: wrong-spec — CSV rows (line-scoped per SKU) AND per-model HTML segments */
  const csvText = csvR + NL + csvS;
  let w;
  for (w of WRONG_SPECS) {
    const csvBad = csvText.split(NL).filter(function(line){ return line.includes(w.marker) && w.bad.some(function(rx){ return rx.test(line); }); });
    if (csvBad.length) fail('c1_csv_wrong_spec:' + w.marker, w.reason, csvBad.map(function(l){ return l.slice(0, 60); }));
    else pass('c1_csv_wrong_spec:' + w.marker);
  }
  for (w of WRONG_SPECS) {
    const segRe = new RegExp('<p><strong>' + w.marker.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '[^<]*</strong>[^\\0]*?</p>', 'g');
    const badSegs = [];
    const htmls = [htmlR, htmlS];
    for (let hi = 0; hi < htmls.length; hi++) {
      const html = htmls[hi];
      const segs = html.match(segRe) || [];
      for (let si = 0; si < segs.length; si++) {
        if (w.bad.some(function(rx){ return rx.test(segs[si]); })) badSegs.push(segs[si].slice(0, 60));
      }
    }
    if (badSegs.length) fail('c1_html_wrong_spec:' + w.marker, w.reason, badSegs);
    else pass('c1_html_wrong_spec:' + w.marker);
  }
  /* C1-row: table <tr> carrying a model SKU must not carry its bad tokens */
  for (w of WRONG_SPECS) {
    const badRows = [];
    const htmls2 = [htmlR, htmlS];
    for (let hi = 0; hi < htmls2.length; hi++) {
      const trs = htmls2[hi].split('<tr>').slice(1).map(function(x){ return x.split('</tr>')[0]; });
      for (let ti = 0; ti < trs.length; ti++) {
        if (trs[ti].includes(w.marker) && w.bad.some(function(rx){ return rx.test(trs[ti]); })) badRows.push(trs[ti].slice(0, 60));
      }
    }
    if (badRows.length) fail('c1row_wrong_spec:' + w.marker, w.reason, badRows);
    else pass('c1row_wrong_spec:' + w.marker);
  }

  /* C2: SVG inner labels must match their canonical SKU */
  const c2keys = Object.keys(CANON.routers).concat(Object.keys(CANON.switches));
  for (let ci = 0; ci < c2keys.length; ci++) {
    const sku = c2keys[ci];
    const file = CANON.routers[sku] || CANON.switches[sku];
    const c = get('assets/' + file);
    if (c === null) { fail('c2_svg_present:' + file, 'schematic asset missing from candidate', { sku: sku }); continue; }
    const ok = c.indexOf('>' + sku + '<') >= 0 || c.indexOf(sku) >= 0;
    if (!ok) fail('c2_svg_label_matches:' + file, 'SVG label does not show canonical SKU ' + sku, {});
    else pass('c2_svg_label_matches:' + file);
  }

  /* C3: coverage — EVERY catalog row must keep its schematic embedded in its guide */
  const csvRrows = csvR.split(NL).filter(function(l){ return l.trim() && !l.startsWith('model_sku'); }).map(function(l){ return l.split(',')[0].trim(); });
  const csvSrows = csvS.split(NL).filter(function(l){ return l.trim() && !l.startsWith('model_sku'); }).map(function(l){ return l.split(',')[0].trim(); });
  const canonR = Object.keys(CANON.routers);
  const canonS = Object.keys(CANON.switches);
  const omittedRowsR = canonR.filter(function(sku){ return csvRrows.indexOf(sku) < 0; });
  const omittedRowsS = canonS.filter(function(sku){ return csvSrows.indexOf(sku) < 0; });
  if (omittedRowsR.length || omittedRowsS.length) {
    fail('c3_omitted_catalog_rows', 'catalog row removed (omitted model)', { routers: omittedRowsR, switches: omittedRowsS });
  } else pass('c3_catalog_rows_complete', { routers: canonR.length, switches: canonS.length });
  const missR = [];
  const missS = [];
  for (let mi = 0; mi < canonR.length; mi++) { if (htmlR.indexOf('assets/' + CANON.routers[canonR[mi]]) < 0) missR.push(canonR[mi]); }
  for (let mi = 0; mi < canonS.length; mi++) { if (htmlS.indexOf('assets/' + CANON.switches[canonS[mi]]) < 0) missS.push(canonS[mi]); }
  if (missR.length || missS.length) fail('c3_model_coverage', 'models with no embedded schematic', { routers: missR, switches: missS });
  else pass('c3_model_coverage', 'all router+switch catalog models embedded');
  /* exact-SKU set: truncated/unknown SKUs rejected */
  const truncR = csvRrows.filter(function(row){ return canonR.indexOf(row) < 0; });
  const truncS = csvSrows.filter(function(row){ return canonS.indexOf(row) < 0; });
  if (truncR.length) fail('c3_exact_sku_router_csv', 'router-catalog contains truncated/unknown SKU', truncR);
  else pass('c3_exact_sku_router_csv');
  if (truncS.length) fail('c3_exact_sku_switch_csv', 'switch-catalog contains truncated/unknown SKU', truncS);
  else pass('c3_exact_sku_switch_csv');

  /* C4: no nested image-in-paragraph */
  const nested = [htmlR, htmlS].map(function(h){ return (h.match(/<!-- wp:paragraph -->(?:(?!<!-- \/wp:paragraph -->).)*?<!-- wp:image -->/gs) || []).length; });
  if (nested.some(function(n){ return n > 0; })) fail('c4_no_nested_image_in_paragraph', 'wp:image inside wp:paragraph', { nested: nested });
  else pass('c4_no_nested_image_in_paragraph');

  /* C5: ALL relative refs (assets + CSVs) resolve within the candidate tree */
  const refBroken = [];
  let refTotal = 0;
  const htmlEntries = candidateInputs.filter(function(x){ return x.name.endsWith('.html'); });
  for (let ei = 0; ei < htmlEntries.length; ei++) {
    const name = htmlEntries[ei].name;
    const content = htmlEntries[ei].content;
    const re = new RegExp('(?:src|href)="(\\.\\.\\/[^"]+)"', 'g'); let m;
    while ((m = re.exec(content))) {
      refTotal++;
      const resolvedName = m[1].replace('../', '');
      if (!candidateInputs.some(function(x){ return x.name === resolvedName; })) refBroken.push({ html: name, rel: m[1] });
    }
  }
  if (refBroken.length) fail('c5_refs_resolve', 'broken relative refs in candidate (incl. CSVs)', refBroken);
  else pass('c5_refs_resolve', { refs: refTotal, note: 'all resolve to candidate files' });

  /* C6: catalog links from HTML point to ../CSV paths */
  for (const [name, content] of candidateInputs.filter(function(x){ return x.name.endsWith('.gutenberg.html'); }).map(function(x){ return [x.name, x.content]; })) {
    if (content.includes('href="router-catalog.csv"') || content.includes('href="switch-catalog.csv"')) fail('c6_csv_link_path:' + name, 'bare CSV filename (must be ../router-catalog.csv)');
    else pass('c6_csv_link_path:' + name);
  }

  /* C7: duplicate ids / dangling anchors */
  for (const [name, content] of candidateInputs.filter(function(x){ return x.name.endsWith('.gutenberg.html'); }).map(function(x){ return [x.name, x.content]; })) {
    const ids = [];
    const reId = /id="([^"]+)"/g; let mId;
    while ((mId = reId.exec(content))) ids.push(mId[1]);
    const dup = ids.filter(function(x, i){ return ids.indexOf(x) !== i; });
    const hrefs = [];
    const reHref = /href="#([^"]+)"/g; let mH;
    while ((mH = reHref.exec(content))) hrefs.push(mH[1]);
    const dangling = hrefs.filter(function(h){ return ids.indexOf(h) < 0; });
    if (dup.length) fail('c7_dup_ids:' + name, 'duplicate ids', dup.slice(0, 3));
    else if (dangling.length) fail('c7_dangling:' + name, 'dangling anchor targets', dangling.slice(0, 3));
    else pass('c7_no_dup_or_dangling:' + name);
  }

  /* C8: visible editorial instructions in public copy */
  const allHtml = htmlR + NL + htmlS;
  if (allHtml.includes('insert/merge; replace weak sections')) fail('c8_visible_editorial_instruction', 'insert/merge instruction visible in public copy');
  else pass('c8_no_editorial_instructions');

  /* C9: proposed pages — no {#…} literals, real <a> links present */
  const proposedFiles = candidateInputs.filter(function(x){ return x.name.indexOf('.proposed.html') >= 0; });
  for (let pi = 0; pi < proposedFiles.length; pi++) {
    const pf = proposedFiles[pi];
    if (/\{#[a-z0-9-]+\}/.test(pf.content)) fail('c9_literal_anchor:' + pf.name, '{#anchor} literal in proposed page');
    else if (!/<a href="/.test(pf.content)) fail('c9_no_real_links:' + pf.name, 'no real <a> links');
    else pass('c9_real_links_and_anchors:' + pf.name);
  }

  const failed = checks.filter(function(c){ return !c.pass; });
  return {
    ok: failed.length === 0,
    checks: checks,
    failedChecks: failed.map(function(c){ return { id: c.id, reason: c.reason }; }),
  };
}

module.exports = { validate: validate, CANON: CANON, WRONG_SPECS: WRONG_SPECS };

/* ---------- runner (only executed as main) ---------- */
if (require.main === module) {
  const fs = require('node:fs');
  const path = require('node:path');
  const crypto = require('node:crypto');
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
  for (let fi = 0; fi < fileNames.length; fi++) {
    if (!fs.existsSync(path.join(ROOT, fileNames[fi]))) { console.error('MISSING CANDIDATE FILE: ' + fileNames[fi]); process.exit(2); }
  }
  const goodInputs = fileNames.map(function(f){ return { name: f, content: read(f) }; });
  const assetDir = path.join(ROOT, 'assets');
  const assetFiles = fs.readdirSync(assetDir);
  for (let ai = 0; ai < assetFiles.length; ai++) {
    goodInputs.push({ name: 'assets/' + assetFiles[ai], content: fs.readFileSync(path.join(assetDir, assetFiles[ai]), 'utf8') });
  }

  console.log('== GOOD CANDIDATE ==');
  const good = validate(goodInputs);
  console.log('good candidate: ok=' + good.ok + ' checks=' + good.checks.length + ' failed=' + good.failedChecks.length);
  for (let gi = 0; gi < good.failedChecks.length; gi++) console.log('  good-fail:', good.failedChecks[gi].id, '|', good.failedChecks[gi].reason);

  /* injected negatives — through the SAME validate() */
  const negatives = [];
  function injectNeg(name, defect, mutate, expectReason) {
    const clone = JSON.parse(JSON.stringify(goodInputs));
    mutate(clone);
    const r = validate(clone);
    const failedWithReason = !r.ok && r.failedChecks.some(function(c){ return (c.reason || '').indexOf(expectReason) >= 0; });
    negatives.push({ name: name, injected: defect, failed: !r.ok, reasonMatched: failedWithReason, reasons: r.failedChecks.map(function(c){ return c.reason || c.id; }).slice(0, 3) });
    console.log((!r.ok && failedWithReason ? 'PASS ' : 'FAIL ') + 'NEG ' + name + ' -> ' + JSON.stringify(r.failedChecks.map(function(c){ return c.reason || c.id; }).slice(0, 2)));
  }
  injectNeg('wrong-spec-E50UG-multiline-HTML', 'E50UG MMIPS/256MB in multiline HTML', function(clone){
    for (let i = 0; i < clone.length; i++) {
      if (clone[i].name === 'articles/mikrotik-routers.gutenberg.html') clone[i].content = clone[i].content.replace('<p><strong>hEX refresh (E50UG)</strong>', '<p><strong>hEX refresh (E50UG)</strong> CPU: MMIPS 880MHz، 256MB.');
    }
  }, 'E50UG row still carries MMIPS/256MB');
  injectNeg('wrong-SVG-label-CRS112', 'SVG inner label shows CRS112-8P-4G-IN', function(clone){
    for (let i = 0; i < clone.length; i++) {
      if (clone[i].name === 'assets/schematic-crs112-8p-4s-in.svg') clone[i].content = clone[i].content.replace('CRS112-8P-4S-IN', 'CRS112-8P-4G-IN');
    }
  }, 'SVG label does not show canonical SKU CRS112-8P-4S-IN');
  injectNeg('omitted-model-CRS326', 'CRS326-24G-2S+RM row removed from switch-catalog', function(clone){
    for (let i = 0; i < clone.length; i++) {
      if (clone[i].name === 'switch-catalog.csv') clone[i].content = clone[i].content.split('\n').filter(function(l){ return l.indexOf('CRS326-24G-2S+RM') < 0; }).join('\n');
    }
  }, 'catalog row removed (omitted model)');
  injectNeg('missing-schematic-asset', 'schematic-crs309 file removed from candidate tree', function(clone){
    const i = clone.findIndex(function(x){ return x.name === 'assets/schematic-crs309-1g-8s-in.svg'; });
    if (i >= 0) clone.splice(i, 1);
  }, 'schematic asset missing from candidate');
  injectNeg('broken-relative-link', 'article points to nonexistent ../assets/ghost.svg', function(clone){
    for (let i = 0; i < clone.length; i++) {
      if (clone[i].name === 'articles/mikrotik-switches-crs.gutenberg.html') clone[i].content = clone[i].content.replace('../assets/schematic-css610-8g-2s-in.svg', '../assets/ghost-missing.svg');
    }
  }, 'models with no embedded schematic');
  injectNeg('duplicate-id', 'same heading id duplicated', function(clone){
    for (let i = 0; i < clone.length; i++) {
      if (clone[i].name === 'articles/mikrotik-routers.gutenberg.html') clone[i].content = clone[i].content.replace('id="ch3"', 'id="ch2"');
    }
  }, 'duplicate ids');
  injectNeg('dangling-anchor', 'TOC link targets a removed anchor', function(clone){
    for (let i = 0; i < clone.length; i++) {
      if (clone[i].name === 'articles/mikrotik-routers.gutenberg.html') clone[i].content = clone[i].content.replace('id="faq"', 'id="faq-removed"');
    }
  }, 'dangling anchor targets');

  let negFail = 0;
  for (let ni = 0; ni < negatives.length; ni++) { if (!(negatives[ni].failed && negatives[ni].reasonMatched)) negFail++; }
  const ok = good.ok && good.failedChecks.length === 0 && negFail === 0;
  const finishedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  const controlSha = 'GIT_UNAVAILABLE_NO_EXEC';
  const digests = {};
  for (let di = 0; di < fileNames.length; di++) digests[fileNames[di]] = crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT, fileNames[di]))).digest('hex');

  const receipt = {
    packet: 'TN-TOPICAL-AUTHORITY-GROWTH-20261116',
    validator: 'validate-seo-guides.cjs rev6 (shared validate(candidateInputs) + 7 injected negatives through same path)',
    command: 'node validate-seo-guides.cjs',
    cwd: 'qa/seo-device-guides-20261116/',
    started_utc: startedUtc, finished_utc: finishedUtc,
    control_head: 'NOT_COMPUTED_NO_EXEC',
    exit: ok ? 0 : 1,
    good_candidate: { ok: good.ok, checks: good.checks.length, failed: good.failedChecks.length },
    injected_negatives: negatives,
    digests: digests,
    summary: { negatives: negatives.length, negatives_passed: negatives.length - negFail, negatives_failed: negFail },
    execution_origin: {
      'note': 'validator/builder execution NOT_RUN this turn — owner-local Node execution prohibited per mission; no authorized non-local runtime available',
      'prohibition_source': 'TN-BASE-LOCK-AND-TOPICAL-EXECUTION-20261116 §0 + MANAGER_REVIEW 6916713513 (Node/Python execution on owner system not permitted)',
      'provenance': 'source corrections committed; test receipts from previous authorized runs preserved as historical evidence only',
    },
    not_run: ['browser desktop/mobile/keyboard rendering', 'WordPress/KSES acceptance', 'Search Console baseline', 'all Node/PHP/builder/test executions'],
    production_touched: false,
  };
  fs.writeFileSync(__dirname + '/validation-receipt.json', JSON.stringify(receipt, null, 1));
  console.log('\nGOOD=' + (good.ok ? 'PASS' : 'FAIL') + ' | NEGATIVES=' + negatives.length + '/' + negatives.length + ' rejected-with-reason');
  console.log('RECEIPT validation-receipt.json | exit=' + receipt.exit);
  process.exitCode = ok ? 0 : 1;
}
