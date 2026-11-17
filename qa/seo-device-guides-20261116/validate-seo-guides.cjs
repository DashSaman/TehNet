'use strict';
/* TN-TOPICAL-AUTHORITY-GROWTH-20261116 — shared validator (rev7).
 * Run: node validate-seo-guides.cjs   (from qa/seo-device-guides-20261116/)
 * Shared validate(candidateInputs): GOOD candidate must pass, injected negatives must
 * fail through the SAME path with intended reasons. Node-24 for-of destructuring
 * workaround: index-based loops throughout (no array destructuring in for-of).
 * rev7 (TN-M2-M3-CORRECTIONS-20261116, manager 6923833096): tutorial candidates
 * M2/M3 (MD+HTML) join the shared path; C12 required tutorial sections, C13
 * tutorial diagram embedding + SVG accessible text, C14 generated-header origin;
 * c10-freshness in runner (builder re-run + byte-compare); 2 tutorial negatives. */
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

  /* C12-C14 (rev7): tutorial lessons M2/M3 — sections, diagram, origin (6923833096) */
  const TUTORIALS = [
    { md: 'tutorials/m2-vlan-small-office.fa.md', html: 'tutorials/m2-vlan-small-office.gutenberg.html', svg: 'assets/tutorial-m2-topology.svg', label: 'M2',
      extra: ['سیاست جریان'], service: 'https://tehnet.ir/services/mikrotik-tehran/' },
    { md: 'tutorials/m3-dhcp-dns.fa.md', html: 'tutorials/m3-dhcp-dns.gutenberg.html', svg: 'assets/tutorial-m3-dhcp-dns-flow.svg', label: 'M3',
      extra: ['مرز DNS مورداعتماد'], service: 'https://tehnet.ir/services/mikrotik-tehran/' },
    { md: 'tutorials/s2-poe-budget.fa.md', html: 'tutorials/s2-poe-budget.gutenberg.html', svg: 'assets/tutorial-s2-poe-budget.svg', label: 'S2',
      sectionsOverride: ['پاسخ کوتاه', 'مبنا آزمایشگاه', 'محاسبهٔ بودجه', 'مثال کارشده', 'خطاهای رایج', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع رسمی', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/network-setup-tehran/' },
    { md: 'tutorials/s3-sfp-dac-fiber.fa.md', html: 'tutorials/s3-sfp-dac-fiber.gutenberg.html', svg: 'assets/tutorial-s3-module-decision.svg', label: 'S3',
      sectionsOverride: ['پاسخ کوتاه', 'مبنا آزمایشگاه', 'قواعد سازگاری', 'مثال کارشده', 'خطاهای رایج', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع رسمی', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/network-setup-tehran/' },
    { md: 'tutorials/n1-network-troubleshooting.fa.md', html: 'tutorials/n1-network-troubleshooting.gutenberg.html', svg: 'assets/tutorial-n1-layer-ladder.svg', label: 'N1',
      sectionsOverride: ['پاسخ کوتاه', 'مبنا آزمایشگاه', 'جدول عیب‌یابی لایه‌ای', 'مثال کارشده', 'خطاهای رایج در فرایند عیب‌یابی', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/network-support-tehran/' },
    { md: 'tutorials/n4-delivery-acceptance.fa.md', html: 'tutorials/n4-delivery-acceptance.gutenberg.html', svg: 'assets/tutorial-n4-acceptance-phases.svg', label: 'N4',
      sectionsOverride: ['پاسخ کوتاه', 'مبنا آزمایشگاه', 'ثبت قبل/بعد', 'بستهٔ مستندات تحویل', 'خطاهای رایج پذیرش', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/network-setup-tehran/' },
    { md: 'tutorials/n2-monitoring-maintenance.fa.md', html: 'tutorials/n2-monitoring-maintenance.gutenberg.html', svg: 'assets/tutorial-n2-monitoring-loop.svg', label: 'N2',
      sectionsOverride: ['پاسخ کوتاه', 'مبنا آزمایشگاه', 'متریک‌های پایه', 'نمونهٔ Netwatch', 'چک‌لیست نگهداری دوره‌ای', 'مثال کارشده', 'خطاهای رایج', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/network-support-tehran/' },
    { md: 'tutorials/n3-support-contract-sla.fa.md', html: 'tutorials/n3-support-contract-sla.gutenberg.html', svg: 'assets/tutorial-n3-sla-timeline.svg', label: 'N3',
      sectionsOverride: ['پاسخ کوتاه', 'مبنا آزمایشگاه', 'شش سؤال کلیدی قبل از امضا', 'SLA سنجش‌پذیر', 'جدول مقایسهٔ ساختاریافتهٔ A/B', 'خطاهای رایج قبل از امضا', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/network-support-tehran/' },
    { md: 'tutorials/n5-config-backup-export.fa.md', html: 'tutorials/n5-config-backup-export.gutenberg.html', svg: 'assets/tutorial-n5-backup-export.svg', label: 'N5',
      sectionsOverride: ['پاسخ کوتاه', 'مبنا آزمایشگاه', 'backup در برابر export', 'زمان‌بندی خودکار', 'بازیابی و آزمون بازیابی', 'خطاهای رایج', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/network-support-tehran/' },
    { md: 'tutorials/n6-incident-path.fa.md', html: 'tutorials/n6-incident-path.gutenberg.html', svg: 'assets/tutorial-n6-incident-path.svg', label: 'N6',
      sectionsOverride: ['پاسخ کوتاه', 'مبنا آزمایشگاه', 'جدول مراحل', 'تشدید', 'استثناهای وابسته به اینترنت/قطعه', 'ثبت اثر اختلال', 'خطاهای رایج', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/network-support-tehran/' },
    { md: 'tutorials/n1-office-design.fa.md', html: 'tutorials/n1-office-design.gutenberg.html', svg: 'assets/tutorial-n1-office-design.svg', label: 'N1c',
      sectionsOverride: ['پاسخ کوتاه', 'مبنا آزمایشگاه', 'گام ۱: نیازسنجی', 'گام ۲: توپولوژی', 'گام ۳: نقشهٔ پورت', 'گام ۴: آدرس‌دهی و VLAN', 'گام ۵: انتخاب تجهیز', 'گام ۶: مستندسازی و آزمون پذیرش', 'خطاهای رایج', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/network-setup-tehran/' },
    { md: 'tutorials/m4-intervlan-l3hw.fa.md', html: 'tutorials/m4-intervlan-l3hw.gutenberg.html', svg: 'assets/tutorial-m4-l3hw-flow.svg', label: 'M4',
      sectionsOverride: ['پاسخ کوتاه', 'مبنا آزمایشگاه', 'HW در برابر CPU', 'شش الزام/هشدار سندشده', 'تلهٔ Fasttrack و حافظهٔ ACL', 'دستورهای مبنا', 'تصمیم‌گیری', 'خطاهای رایج', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع رسمی', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/mikrotik-tehran/' },
    { md: 'tutorials/m5-vpn-selection.fa.md', html: 'tutorials/m5-vpn-selection.gutenberg.html', svg: 'assets/tutorial-m5-vpn-architecture.svg', label: 'M5',
      sectionsOverride: ['پاسخ کوتاه', 'مبنا آزمایشگاه', 'جدول مقایسه', 'مثال کارشده', 'جدول تصمیم', 'نمودار معماری', 'خطاهای رایج', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع رسمی', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/mikrotik-tehran/' },
    { md: 'tutorials/m6-dual-wan-failover.fa.md', html: 'tutorials/m6-dual-wan-failover.gutenberg.html', svg: 'assets/tutorial-m6-dual-wan-failover.svg', label: 'M6',
      sectionsOverride: ['پاسخ کوتاه', 'مبنا آزمایشگاه', 'جدول مقایسهٔ روش‌ها', 'دستورهای مبنا', 'سناریوی آزمون failover', 'خطاهای رایج', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع رسمی', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/mikrotik-tehran/' },
    { md: 'tutorials/s5-uplink-trunk.fa.md', html: 'tutorials/s5-uplink-trunk.gutenberg.html', svg: 'assets/tutorial-s5-uplink-trunk.svg', label: 'S5',
      sectionsOverride: ['پاسخ کوتاه', 'مبنا آزمایشگاه', 'محاسبهٔ ظرفیت آپ‌لینک', 'راه‌اندازی ترانک', 'جدول بررسی ترانک', 'خطاهای رایج', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/network-setup-tehran/' },
    { md: 'tutorials/s6-psu-power.fa.md', html: 'tutorials/s6-psu-power.gutenberg.html', svg: 'assets/tutorial-s6-psu-power.svg', label: 'S6',
      sectionsOverride: ['پاسخ کوتاه', 'مبنا آزمایشگاه', 'محاسبهٔ انتخاب PSU', 'جدول تصمیم PSU', 'خطاهای رایج', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/network-setup-tehran/' },
    { md: 'tutorials/s5-loop-rstp-lacp.fa.md', html: 'tutorials/s5-loop-rstp-lacp.gutenberg.html', svg: 'assets/tutorial-s5-loop-rstp-lacp.svg', label: 'S5c',
      sectionsOverride: ['پاسخ کوتاه', 'مبنا آزمایشگاه', 'تنظیم LACP', 'RSTP روی پل', 'سناریوی حلقهٔ تصادفی', 'خطاهای رایج', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع رسمی', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/network-setup-tehran/' },
    { md: 'tutorials/n6-support-selection.fa.md', html: 'tutorials/n6-support-selection.gutenberg.html', svg: 'assets/tutorial-n6-support-selection.svg', label: 'N6c',
      sectionsOverride: ['پاسخ کوتاه', 'فهرست', 'پیش‌نیازها', 'مبنا آزمایشگاه', 'گام ۱: نیازسنجی', 'گام ۲: فهرست گزینه‌ها', 'گام ۳: تطبیق نیاز با پوشش', 'گام ۴: ارزیابی ساختاریافته', 'گام ۵: دورهٔ آزمایشی', 'گام ۶: بازنگری دوره‌ای', 'خطاهای رایج', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/network-support-tehran/' },
    { md: 'tutorials/s4-vlan-switch-l2.fa.md', html: 'tutorials/s4-vlan-switch-l2.gutenberg.html', svg: 'assets/tutorial-s4-vlan-l2.svg', label: 'S4c',
      sectionsOverride: ['پاسخ کوتاه', 'فهرست', 'پیش‌نیازها', 'مبنا آزمایشگاه یکتا، نقشهٔ پورت/VLAN و جدول endpoint سنتز', 'نقشهٔ پورت و VLAN', 'جدول endpoint سنتز و حالت آزمون', 'گام ۱: گارد مبنای آزمایشگاهی', 'گام ۲: قطعهٔ access', 'گام ۳: قطعهٔ جدول VLAN', 'گام ۴: قطعهٔ مسیر CPU', 'گام ۵: قطعهٔ فیلترینگ', 'مرز لایه۲ و لایه۳', 'آزمون پذیرش مثبت/منفی', 'بازگشت امن و بازیابی', 'عیب‌یابی', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع', 'آموزش‌های مرتبط'],
      service: 'https://tehnet.ir/services/network-setup-tehran/' },
  ];
  const TUT_SECTIONS_COMMON = ['پاسخ کوتاه', 'مبنا آزمایشگاه', 'تست پذیرش', 'تمرین کوتاه', 'چک‌لیست تحویل', 'منابع رسمی', 'آموزش‌های مرتبط'];
  for (let ti = 0; ti < TUTORIALS.length; ti++) {
    const t = TUTORIALS[ti];
    const TUT_SECTIONS = t.sectionsOverride || TUT_SECTIONS_COMMON.concat(t.extra);
    const mdC = get(t.md);
    const htmlC = get(t.html);
    if (mdC === null || htmlC === null) { fail('c12_tutorial_present:' + t.label, 'tutorial MD/HTML missing from candidate'); continue; }
    /* C12: required sections + service CTA link in MD */
    const missingSec = TUT_SECTIONS.filter(function(s){ return mdC.indexOf(s) < 0; });
    const hasService = mdC.indexOf(t.service || 'https://tehnet.ir/services/mikrotik-tehran/') >= 0;
    const hasMdImage = /^!\[[^\]]*\]\(\.\.\/assets\/tutorial-/m.test(mdC);
    if (missingSec.length || !hasService || !hasMdImage) {
      fail('c12_tutorial_sections:' + t.label, 'tutorial required section missing', { missing: missingSec, serviceCta: hasService, diagramLine: hasMdImage });
    } else pass('c12_tutorial_sections:' + t.label, { sections: TUT_SECTIONS.length });
    /* C13: HTML embeds the conceptual SVG + the SVG has accessible title/desc */
    const svgC = get(t.svg);
    const svgOk = svgC !== null && svgC.indexOf('<title>') >= 0 && svgC.indexOf('<desc>') >= 0;
    const embOk = htmlC.indexOf('../assets/tutorial-') >= 0 && htmlC.indexOf('<!-- wp:image -->') >= 0;
    if (!svgOk || !embOk) fail('c13_tutorial_diagram:' + t.label, 'tutorial diagram missing or SVG lacks accessible text', { svgText: svgOk, embedded: embOk });
    else pass('c13_tutorial_diagram:' + t.label);
    /* C14: honest generated-by origin header in HTML */
    const originOk = htmlC.indexOf('generated deterministically by build-gutenberg.cjs') >= 0 && htmlC.indexOf('NOT_DEPLOYED') >= 0;
    if (!originOk) fail('c14_tutorial_origin:' + t.label, 'tutorial HTML lacks generated-by/NOT_DEPLOYED origin header');
    else pass('c14_tutorial_origin:' + t.label);
  }

  /* C15-C17 (rev9): canonical N6 consumer checks per 6938667416 */
  const n6Html = get('tutorials/n6-support-selection.gutenberg.html');
  const n6Md = get('tutorials/n6-support-selection.fa.md');
  if (n6Html !== null) {
    const faLinks = (n6Html.match(/href="[^"]*\.fa\.md"/g) || []).length;
    const mapped = ['/guides/office-network-design/','/guides/network-monitoring/','/guides/support-contract-questions/','/guides/network-troubleshooting/','/guides/mikrotik-config-backup/','/guides/network-incident-path/'].filter(function(u){ return n6Html.indexOf('href="' + u + '"') >= 0; }).length;
    const tocLinks = (n6Html.match(/href="#[^"]+"/g) || []);
      const dangling = tocLinks.filter(function(hh){ const anchor = decodeURIComponent(hh.replace(/^href=/, '').replace(/"/g, '').replace(/^#/, '')); return n6Html.indexOf('id="' + anchor + '"') < 0; });
    if (faLinks > 0 || mapped < 6) fail('c15_n6_mapped_hrefs', 'N6 HTML has repository .fa.md links or missing mapped routes', { faLinks: faLinks, mapped: mapped });
    else pass('c15_n6_mapped_hrefs', { mapped_routes: mapped, fa_links: faLinks });
    if (tocLinks.length < 14 || dangling.length > 0) fail('c16_n6_toc_anchors', 'N6 TOC missing or has unresolved anchors', { toc_links: tocLinks.length, dangling: dangling });
    else pass('c16_n6_toc_anchors', { toc_links: tocLinks.length });
    // C17: extract the actual step-6 SECTION (heading line through the next heading) and verify its BODY
    let sec17 = 'MISSING';
    if (n6Md !== null) {
      const hIdx = n6Md.indexOf('## گام ۶: بازنگری دوره‌ای');
      if (hIdx >= 0) {
        const lineStart = n6Md.lastIndexOf('\n', hIdx) + 1;
        const nextH = n6Md.indexOf('\n## ', hIdx + 1);
        const end = nextH >= 0 ? nextH : n6Md.length;
        sec17 = n6Md.slice(lineStart, end);
      }
    }
    const body17 = sec17.replace(/^## [^\n]*$/, '').trim();
    const need17 = ['مسئول بازنگری', 'trigger', 'دادهٔ مقایسه', 'UNKNOWN', 'ادامه', 'اصلاح‌شرط', 'تعویض'];
    const missing17 = need17.filter(function(w){ return body17.indexOf(w) < 0; });
    if (sec17 === 'MISSING' || body17.length < 200 || missing17.length > 0) fail('c17_n6_step6_review', 'N6 step-6 review SECTION missing or body incomplete (owner/trigger/data/UNKNOWN/outcomes)', { section_found: sec17 !== 'MISSING', body_chars: body17.length, missing: missing17 });
    else pass('c17_n6_step6_review', { body_chars: body17.length });
  }

  /* C18 (6937439006 + 6939893685): per-ID row-shape/URL-field check INSIDE a valid contiguous GFM table block */
  const tm = get('topic-map.md');
  if (tm !== null) {
    const L = tm.split('\n');
    const isDelim = function(l){ return /^[|: -]+\|$/.test(l.trim()); };
    const isPipe = function(l){ return l.trim().indexOf('|') === 0; };
    const blocks = [];
    let bi = 0;
    while (bi < L.length) {
      if (isPipe(L[bi]) && bi + 1 < L.length && isDelim(L[bi + 1])) {
        let bj = bi;
        while (bj < L.length && isPipe(L[bj])) bj++;
        blocks.push({ headerIdx: bi + 1, delimIdx: bi + 2, rows: L.slice(bi + 2, bj), startLine: bi + 1 });
        bi = bj;
      } else bi++;
    }
    function tmRow(idPrefix) {
      for (let k = 0; k < blocks.length; k++) {
        const rows = blocks[k].rows;
        for (let ri = 0; ri < rows.length; ri++) {
          if (rows[ri].indexOf('| ' + idPrefix) === 0) return { block: blocks[k], blockIdx: k, cells: rows[ri].split('|').slice(1, -1).map(function(x){ return x.trim(); }) };
        }
      }
      return null;
    }
    const probs = [];
    const delimBroken = [];
    for (let li = 1; li < L.length - 1; li++) {
      if (L[li].trim() === '' && isPipe(L[li - 1]) && isPipe(L[li + 1])) delimBroken.push(li + 1);
    }
    if (delimBroken.length > 0) probs.push('blank line inside a pipe-table region breaks GFM table continuity at line(s) ' + delimBroken.join(','));
    const n6row = tmRow('N6 ');
    const suprow = tmRow('N-مکمل: قرارداد/SLA ');
    if (!n6row) probs.push('canonical N6 row missing from any valid table block');
    else {
      if (n6row.cells.length !== 9) probs.push('N6 row has ' + n6row.cells.length + ' columns (need 9)');
      if (n6row.cells[3].indexOf('/guides/network-support-selection/') !== 0) probs.push('N6 URL field is ' + n6row.cells[3] + ' (need /guides/network-support-selection/)');
      if (n6row.cells[6].indexOf('ساختار پشتیبانی') < 0) probs.push('N6 question field does not match selection intent');
    }
    if (!suprow) probs.push('supplement contract/SLA row missing from any valid table block');
    else {
      if (n6row && suprow.blockIdx !== n6row.blockIdx) probs.push('supplement row is in a DIFFERENT table block than canonical N6 (blank line or stray header between them)');
      if (suprow.cells.length !== 9) probs.push('supplement row has ' + suprow.cells.length + ' columns (need 9)');
      if (suprow.cells[3].indexOf('/guides/support-contract-questions/') !== 0) probs.push('supplement URL field is ' + suprow.cells[3] + ' (need /guides/support-contract-questions/)');
      if (suprow.cells[6].indexOf('قرارداد پشتیبانی چه چیزهایی') < 0) probs.push('supplement question field mismatch');
    }
    if (probs.length > 0) fail('c18_n6_route_consistency', 'topic-map N6 routing/row-shape mismatch (canonical vs supplement)', { problems: probs });
    else pass('c18_n6_route_consistency', { n6_route: n6row.cells[3], supplement_route: suprow.cells[3], columns: 9, table_blocks: blocks.length });
  }

  /* c19-c20 (per MANAGER_REVIEW 6961231363): S4 source-contract checks — PURE source
   * text contract, NOT RouterOS execution. (1) single no-defaults lab baseline with a
   * stop-on-error guard block whose identity/conflict preconditions precede the first
   * effect and whose filter-last closes the same block; honest recovery wording.
   * (2) replayable synthetic endpoint/test-mode acceptance plan (same-prefix L2 negative
   * + same-VLAN disposable positive + separately declared routed phase + trunk negative
   * with sender/positive-control/discriminating observation and the CPU-capture caveat). */
  const s4Md = get('tutorials/s4-vlan-switch-l2.fa.md');
  if (s4Md !== null) {
    const guardMarkers = [
      'stop-on-error',
      ':if ([:len [/interface bridge find]] > 0) do={ :error "S4: bridge(s) exist',
      ':if ([:len [/interface bridge port find]] > 0) do={ :error "S4: bridge-port memberships exist',
      'board-name~"CRS326"',
      ':if ([:len [/interface find where name="ether23"]]',
      '192.168.88."]] > 0) do={ :error "S4: management subnet',
      'frame-types=admit-only-untagged',
      'set bridge1 vlan-filtering=yes',
      ':put "S4: build complete (filtering enabled last)"',
      'disposable',
    ];
    const missingGuard = guardMarkers.filter(function(m){ return s4Md.indexOf(m) < 0; });
    const guardIdx = s4Md.indexOf(':if ([:len [/interface bridge find]] > 0)');
    const filterIdx = s4Md.indexOf('set bridge1 vlan-filtering=yes');
    const blockOpen = s4Md.indexOf('\n{', Math.max(0, guardIdx - 600));
    const blockClose = s4Md.indexOf('\n}', filterIdx);
    const sameBlock = guardIdx >= 0 && filterIdx >= 0 && blockOpen >= 0 && blockClose >= 0 && blockOpen < guardIdx && filterIdx < blockClose;
    const guardBeforeEffect = guardIdx >= 0 && s4Md.indexOf('add name=bridge1') > guardIdx;
    const recoveryOk = s4Md.indexOf('وارسی\u200cشده') >= 0 && s4Md.indexOf('از هر پورت access دیگری در حالت بی\u200cفیلتر در دسترس است') < 0;
    if (missingGuard.length > 0 || !sameBlock || !guardBeforeEffect || !recoveryOk)
      fail('c19_s4_baseline_guard_contract', 'S4 baseline guard contract missing (single no-defaults baseline, stop-on-error guard-before-effect, filter-last in same block, honest recovery wording)', { missing: missingGuard, sameBlock: sameBlock, guardBeforeEffect: guardBeforeEffect, recoveryOk: recoveryOk });
    else pass('c19_s4_baseline_guard_contract', { guard_markers: guardMarkers.length, same_block: true });

    const endpointMarkers = [
      'جدول endpoint سنتز و حالت آزمون',
      'آدرس آزمون',
      '192.168.10.21',
      'fixture موقت روی لینک ether23',
      'هم\u200cپیشوند',
      'کنترل مثبت disposable',
      'فاز routed',
      'بازگشت کامل به مبنای آزمون',
      'T-S',
      'آفلودشده لزوماً',
      'فقط همین ورودی',
    ];
    const missingEndpoint = endpointMarkers.filter(function(m){ return s4Md.indexOf(m) < 0; });
    if (missingEndpoint.length > 0)
      fail('c20_s4_endpoint_testmode_contract', 'S4 endpoint/test-mode contract missing (synthetic addresses/prefix/gateway, same-prefix negative + same-VLAN disposable positive, separate routed phase, trunk sender/positive-control/CPU-capture caveat)', { missing: missingEndpoint });
    else pass('c20_s4_endpoint_testmode_contract', { endpoint_markers: endpointMarkers.length });
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
    'tutorials/m2-vlan-small-office.fa.md',
    'tutorials/m2-vlan-small-office.gutenberg.html',
    'tutorials/m3-dhcp-dns.fa.md',
    'tutorials/m3-dhcp-dns.gutenberg.html',
    'tutorials/s2-poe-budget.fa.md',
    'tutorials/s2-poe-budget.gutenberg.html',
    'tutorials/s3-sfp-dac-fiber.fa.md',
    'tutorials/s3-sfp-dac-fiber.gutenberg.html',
    'tutorials/n1-network-troubleshooting.fa.md',
    'tutorials/n1-network-troubleshooting.gutenberg.html',
    'tutorials/n4-delivery-acceptance.fa.md',
    'tutorials/n4-delivery-acceptance.gutenberg.html',
    'tutorials/n2-monitoring-maintenance.fa.md',
    'tutorials/n2-monitoring-maintenance.gutenberg.html',
    'tutorials/n3-support-contract-sla.fa.md',
    'tutorials/n3-support-contract-sla.gutenberg.html',
    'tutorials/n5-config-backup-export.fa.md',
    'tutorials/n5-config-backup-export.gutenberg.html',
    'tutorials/n6-incident-path.fa.md',
    'tutorials/n6-incident-path.gutenberg.html',
    'tutorials/m4-intervlan-l3hw.fa.md',
    'tutorials/m4-intervlan-l3hw.gutenberg.html',
    'tutorials/m5-vpn-selection.fa.md',
    'tutorials/m5-vpn-selection.gutenberg.html',
    'tutorials/m6-dual-wan-failover.fa.md',
    'tutorials/m6-dual-wan-failover.gutenberg.html',
    'tutorials/s5-uplink-trunk.fa.md',
    'tutorials/s5-uplink-trunk.gutenberg.html',
    'tutorials/s6-psu-power.fa.md',
    'tutorials/s6-psu-power.gutenberg.html',
    'tutorials/s5-loop-rstp-lacp.fa.md',
    'tutorials/s5-loop-rstp-lacp.gutenberg.html',
    'tutorials/s6-nas-server-upgrade.fa.md',
    'tutorials/s6-nas-server-upgrade.gutenberg.html',
    'tutorials/n2-rack-cable.fa.md',
    'tutorials/n2-rack-cable.gutenberg.html',
    'tutorials/n1-office-design.fa.md',
    'tutorials/n1-office-design.gutenberg.html',
    'tutorials/n3-cable-test-report.fa.md',
    'tutorials/n3-cable-test-report.gutenberg.html',
    'tutorials/n6-support-selection.fa.md',
    'tutorials/n6-support-selection.gutenberg.html',
    'tutorials/s4-vlan-switch-l2.fa.md',
    'tutorials/s4-vlan-switch-l2.gutenberg.html',
    'topic-map.md',
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
  injectNeg('tutorial-diagram-removed', 'wp:image + SVG ref stripped from M2 tutorial HTML', function(clone){
    for (let i = 0; i < clone.length; i++) {
      if (clone[i].name === 'tutorials/m2-vlan-small-office.gutenberg.html') {
        clone[i].content = clone[i].content.replace(/<!-- wp:image -->[\s\S]*?<!-- \/wp:image -->/, '');
      }
    }
  }, 'tutorial diagram missing');
  injectNeg('n6-repo-link-restored', 'N6 HTML regenerated with a repository .fa.md link', function(clone){
    for (let i = 0; i < clone.length; i++) {
      if (clone[i].name === 'tutorials/n6-support-selection.gutenberg.html') clone[i].content = clone[i].content.replace('href="/guides/office-network-design/"', 'href="n1-office-design.fa.md"');
    }
  }, 'N6 HTML has repository .fa.md links or missing mapped routes');
    injectNeg('n6-step6-body-stripped', 'step-6 heading+TOC kept but the section BODY stripped', function(clone){
    for (let i = 0; i < clone.length; i++) {
      if (clone[i].name === 'tutorials/n6-support-selection.fa.md') {
        const c = clone[i].content;
        const hIdx = c.indexOf('## گام ۶: بازنگری دوره‌ای');
        if (hIdx >= 0) {
          const lineStart = c.lastIndexOf('\n', hIdx) + 1;
          const nextH = c.indexOf('\n## ', hIdx + 1);
          const end2 = nextH >= 0 ? nextH : c.length;
          clone[i].content = c.slice(0, lineStart) + '## گام ۶: بازنگری دوره‌ای {#step6-review}' + c.slice(end2);
        }
      }
    }
  }, 'N6 step-6 review SECTION missing or body incomplete (owner/trigger/data/UNKNOWN/outcomes)');
  injectNeg('n6-supplement-row-blankline', 'blank line inserted before the supplement row, breaking the GFM table', function(clone){
    for (let i = 0; i < clone.length; i++) {
      if (clone[i].name === 'topic-map.md') {
        const c = clone[i].content;
        const li = c.indexOf('| N-مکمل: قرارداد/SLA');
        if (li >= 0) { const NL = String.fromCharCode(10); clone[i].content = c.slice(0, li) + NL + c.slice(li); if (clone[i].content.indexOf(NL + NL + '| N-مکمل: قرارداد/SLA') < 0) throw new Error('n6-supplement-row-blankline setup error: real-LF blank line not established'); }
      }
    }
  }, 'topic-map N6 routing/row-shape mismatch (canonical vs supplement)');
  injectNeg('n6-topic-map-url-swap', 'topic-map URLs swapped between canonical N6 and the contract/SLA supplement', function(clone){
    for (let i = 0; i < clone.length; i++) {
      if (clone[i].name === 'topic-map.md') {
        clone[i].content = clone[i].content.replace('/guides/network-support-selection/', '@@N6TMP@@').replace('/guides/support-contract-questions/', '/guides/network-support-selection/').replace('@@N6TMP@@', '/guides/support-contract-questions/');
      }
    }
  }, 'topic-map N6 routing/row-shape mismatch (canonical vs supplement)');
  injectNeg('n6-toc-dangling', 'N6 TOC anchor renamed so a TOC link dangles', function(clone){
    for (let i = 0; i < clone.length; i++) {
      if (clone[i].name === 'tutorials/n6-support-selection.gutenberg.html') clone[i].content = clone[i].content.replace('id="step6-review"', 'id="step6-review-moved"');
    }
  }, 'N6 TOC missing or has unresolved anchors');
  injectNeg('tutorial-exercise-removed', 'exercise section removed from M3 MD', function(clone){
    for (let i = 0; i < clone.length; i++) {
      if (clone[i].name === 'tutorials/m3-dhcp-dns.fa.md') {
        clone[i].content = clone[i].content.split('\n').filter(function(l){ return l.indexOf('تمرین کوتاه') < 0; }).join('\n');
      }
    }
  }, 'tutorial required section missing');
  injectNeg('s4-baseline-guard-omitted', 'S4 stop-on-error guard lines stripped from the build block', function(clone){
    for (let i = 0; i < clone.length; i++) {
      if (clone[i].name === 'tutorials/s4-vlan-switch-l2.fa.md') {
        clone[i].content = clone[i].content.replace(/ {4}:if \(\[:len \[\/interface bridge find\]\] > 0\) do=\{ :error "S4: bridge\(s\) exist[^\n]*\n/, '').replace(/ {4}:if \(\[:len \[\/interface bridge port find\]\] > 0\) do=\{ :error "S4: bridge-port memberships exist[^\n]*\n/, '');
      }
    }
  }, 'S4 baseline guard contract missing');
  injectNeg('s4-endpoint-testmode-stripped', 'S4 synthetic endpoint/test-mode section body stripped', function(clone){
    for (let i = 0; i < clone.length; i++) {
      if (clone[i].name === 'tutorials/s4-vlan-switch-l2.fa.md') {
        const c = clone[i].content;
        const hIdx = c.indexOf('### جدول endpoint سنتز و حالت آزمون');
        if (hIdx >= 0) {
          const lineStart = c.lastIndexOf('\n', hIdx) + 1;
          const nextH = c.indexOf('\n![', hIdx + 1);
          const end2 = nextH >= 0 ? nextH + 1 : c.length;
          clone[i].content = c.slice(0, lineStart) + '### جدول endpoint سنتز و حالت آزمون {#endpoints-testmode}' + c.slice(end2);
        }
      }
    }
  }, 'S4 endpoint/test-mode contract missing');

  let negFail = 0;
  for (let ni = 0; ni < negatives.length; ni++) { if (!(negatives[ni].failed && negatives[ni].reasonMatched)) negFail++; }
  /* c10-freshness (rev7): deterministic builder re-run; every gutenberg output on disk
   * after the run must byte-match the CANDIDATE SNAPSHOT read at start (detects stale
   * HTML vs MD — comparing disk to disk would always pass, so snapshot comes from
   * goodInputs, captured before the builder executes) */
  let freshOk = true; const freshDetail = [];
  const snap = {};
  for (let si = 0; si < goodInputs.length; si++) {
    if (goodInputs[si].name.endsWith('.gutenberg.html')) snap[goodInputs[si].name] = Buffer.from(goodInputs[si].content, 'utf8');
  }
  try {
    execFileSync('node', [path.join(ROOT, 'articles', 'build-gutenberg.cjs')], { cwd: path.join(ROOT, 'articles'), stdio: 'pipe' });
    for (const nm in snap) {
      const disk = fs.readFileSync(path.join(ROOT, nm));
      if (!disk.equals(snap[nm])) { freshOk = false; freshDetail.push(nm); }
    }
  } catch (e) { freshOk = false; freshDetail.push('BUILDER_RUN_FAILED: ' + String(e.message).slice(0, 120)); }
  if (!freshOk) console.log('FAIL c10_output_freshness -> ' + JSON.stringify(freshDetail));
  else console.log('PASS c10_output_freshness (builder rerun byte-identical for ' + Object.keys(snap).length + ' gutenberg outputs)');
  const ok = good.ok && good.failedChecks.length === 0 && negFail === 0 && freshOk;
  const finishedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  let controlSha = 'GIT_UNAVAILABLE_NO_EXEC';
  try { controlSha = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: path.resolve(__dirname, '../..') }).toString().trim(); } catch (eGit) { controlSha = 'GIT_ERROR: ' + String(eGit.message).slice(0, 60); }
  const digests = {};
  for (let di = 0; di < fileNames.length; di++) digests[fileNames[di]] = crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT, fileNames[di]))).digest('hex');

  const receipt = {
    packet: 'TN-M2-M3-CORRECTIONS-20261116',
    validator: 'validate-seo-guides.cjs rev8 (rev7 + S2 tutorial candidate)',
    command: 'node validate-seo-guides.cjs',
    cwd: 'qa/seo-device-guides-20261116/',
    started_utc: startedUtc, finished_utc: finishedUtc,
    control_head: controlSha,
    exit: ok ? 0 : 1,
    good_candidate: { ok: good.ok, checks: good.checks.length, failed: good.failedChecks.length },
    injected_negatives: negatives,
    output_freshness: { ok: freshOk, stale: freshDetail },
    digests: digests,
    summary: { negatives: negatives.length, negatives_passed: negatives.length - negFail, negatives_failed: negFail },
    execution_origin: {
      'mode': 'LOCAL_TEST — owner-authorized local TehNet execution (owner grant, 2026-11-16); builder AND validator actually executed this turn',
      'builder_executed': true,
      'validator_executed': true,
      'node_version': process.version,
      'routeros_semantics': 'NOT_RUN — no authorized isolated RouterOS fixture available; lesson commands are documented procedures with expected results, NOT executed outputs; no emulator installed',
      'browser_render': 'NOT_RUN — static link/anchor/asset checks only; no browser rendering claimed',
      'wordpress_kses': 'NOT_RUN',
      'supersession': 'older blanket local-exec prohibition (TN-BASE-LOCK-AND-TOPICAL-EXECUTION-20261116 §0) superseded by owner grant; manager 6923833096 CORRECTION 6/7 confirms; previous NOT_RUN receipts remain historical, not revalidated',
    },
    not_run: ['RouterOS command execution (no fixture)', 'browser desktop/mobile/keyboard rendering', 'WordPress/KSES acceptance', 'Search Console baseline'],
    production_touched: false,
  };
  fs.writeFileSync(__dirname + '/validation-receipt.json', JSON.stringify(receipt, null, 1));
  console.log('\nGOOD=' + (good.ok ? 'PASS' : 'FAIL') + ' | NEGATIVES=' + (negatives.length - negFail) + '/' + negatives.length + ' rejected-with-reason | FRESHNESS=' + (freshOk ? 'PASS' : 'FAIL'));
  console.log('RECEIPT validation-receipt.json | exit=' + receipt.exit);
  process.exitCode = ok ? 0 : 1;
}
