'use strict';
/* TN-SEO-DEVICE-GUIDES-20261116 — deterministic Gutenberg builder (rev2).
 * Rebuilds both article HTML files from their .fa.md sources. No timestamps in output.
 * Asset paths use ../assets/ (resolvable from articles/ in the repo preview tree);
 * the proposed-public-URL map lives in publication-notes.json.
 * Determinism: running twice must produce byte-identical files (checked by validate-seo-guides.cjs). */
const fs = require('node:fs');
const path = require('node:path');

const DIR = __dirname;
const ART = path.join(DIR, 'articles');

/* canonical exact-SKU -> schematic asset (single map; families/aliases listed explicitly) */
const SKU_SCHEMATIC = {
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
  'CCR2004-1G-12S+2XS': 'schematic-ccr2004-1g-12s-2xs.svg',
  'CCR2116-12G-4S+': 'schematic-ccr2116-12g-4s.svg',
  'CCR2216-1G-12XS-2XQ': 'schematic-ccr2216-1g-12xs-2xq.svg',
  'RB260GS': 'schematic-rb260gs.svg',
  'RB260GSP': 'schematic-rb260gsp.svg',
  'CSS106 (خانواده RB260)': 'schematic-css106-rb260.svg',
  'CSS610-8G-2S+IN': 'schematic-css610-8g-2s-in.svg',
  'CRS112-8P-4S-IN': 'schematic-crs112-8p-4s-in.svg',
  'CRS309-1G-8S+IN': 'schematic-crs309-1g-8s-in.svg',
  'CRS310-8G+2S+IN': 'schematic-crs310-8g-2s-in.svg',
  'CRS318-16P-2S+IN / netPower 16P': 'schematic-crs318-16p-2s-in-netpower-16p.svg',
    'CSS610-1G-4P-1S+IN': 'schematic-css610-1g-4p-1s-in.svg',
    'CRS310-1G-5S-4S+IN': 'schematic-crs310-1g-5s-4s-in.svg',
    'CRS317-1G-16S+RM': 'schematic-crs317-1g-16s-rm.svg',
  'CRS326-24G-2S+RM': 'schematic-crs326-24g-2s-rm.svg',
  'CRS326-24S+2Q+RM': 'schematic-crs326-24s-2q-rm.svg',
  'CRS328-4C-20S-4S+RM': 'schematic-crs328-4c-20s-4s-rm.svg',
  'CRS354-48G-4S+2Q+RM': 'schematic-crs354-48g-4s-2q-rm.svg',
  'CCR1009/CCR1036 (خانواده)': 'schematic-ccr1009-ccr1036.svg',
  'hAPهای Wi-Fi دار (hAP ax^3 و مشابه)': 'schematic-hap-wi-fi-hap-ax-3.svg',
  'hAP (RB951Ui-2nD)': 'schematic-hap-rb951ui-2nd.svg',
};

function mdToGutenberg(md, perModel) {
  const out = [];
  let inList = false, inTable = false, rows = [], cur = [];
  const flushList = () => {
    if (inList) {
      out.push('<!-- wp:list -->\n<ul class="wp-block-list">' + cur.map(l => '<!-- wp:list-item -->\n<li>' + l + '</li>\n<!-- /wp:list-item -->').join('') + '\n</ul>\n<!-- /wp:list -->');
      inList = false;
    }
  };
  const flushTable = () => {
    if (inTable && rows.length) {
      const head = rows[0], body = rows.slice(1);
      const cells = (r, tag) => r.map(c => '<!-- wp:table-cell -->\n<' + tag + '>' + c.trim() + '</' + tag + '>\n<!-- /wp:table-cell -->').join('');
      out.push('<!-- wp:table -->\n<figure class="wp-block-table"><table class="has-fixed-layout"><thead><tr>' + cells(head, 'th') + '</tr></thead><tbody>' + body.map(r => '<tr>' + cells(r, 'td') + '</tr>').join('') + '</tbody></table>\n<!-- /wp:table -->');
      inTable = false; rows = [];
    }
  };
  for (const line of md.split('\n')) {
    const l = line.trim();
    if (l.startsWith('|')) {
      if (!inTable) { flushList(); inTable = true; }
      rows.push(l.replace(/^\|/, '').replace(/\|$/, '').split('|'));
      continue;
    }
    flushTable();
    if (l.startsWith('### ')) { flushList(); out.push('<!-- wp:heading {"level":3} -->\n<h3 class="wp-block-heading">' + l.slice(4) + '</h3>\n<!-- /wp:heading -->'); }
    else if (l.startsWith('## ')) { flushList(); out.push('<!-- wp:heading -->\n<h2 class="wp-block-heading">' + l.slice(3) + '</h2>\n<!-- /wp:heading -->'); }
    else if (l.startsWith('# ')) { flushList(); out.push('<!-- wp:heading {"level":1} -->\n<h1 class="wp-block-heading">' + l.slice(2) + '</h1>\n<!-- /wp:heading -->'); }
    else if (l.startsWith('- ')) {
      if (!inList) { flushTable(); inList = true; cur = []; }
      cur.push(l.slice(2));
    }
    else if (/^\*[^*].*\*$/.test(l)) out.push('<!-- wp:paragraph -->\n<p><em>' + l.slice(1, -1) + '</em></p>\n<!-- /wp:paragraph -->');
    else if (l.startsWith('**')) {
      const m = l.match(/^\*\*(.+?)\*\*(.*)$/);
      out.push('<!-- wp:paragraph -->\n<p><strong>' + m[1] + '</strong>' + m[2] + '</p>\n<!-- /wp:paragraph -->');
    }
    else if (l) { flushList(); out.push('<!-- wp:paragraph -->\n<p>' + l + '</p>\n<!-- /wp:paragraph -->'); }
  }
  flushList(); flushTable();
  let html = out.join('\n\n');
  /* links: local repo-file cross-links become proposed public slugs */
  html = html.replace(/\[([^\]]+)\]\(mikrotik-routers\.gutenberg\.html\)/g, '[$1](/guides/mikrotik-routers/)');
  html = html.replace(/\[([^\]]+)\]\(mikrotik-switches-crs\.gutenberg\.html\)/g, '[$1](/guides/mikrotik-switches-crs/)');
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  /* heading anchors {#id} -> id attribute */
  html = html.replace(/<h([123]) class="wp-block-heading">([^<]+?) \{#([a-z0-9-]+)\}<\/h\1>/g, '<h$1 class="wp-block-heading" id="$3">$2</h$1>');
  /* per-model schematics BEFORE the model's full <p><strong>SKU…</strong> paragraph
   * (6916713513: keep parenthesized SKU in anchor so hEX variants don't cross-match;
   *  image block sits OUTSIDE the wp:paragraph block) */
  let imgCount = 0;
  const NLX = String.fromCharCode(10); // real newline, escape-proof
  const imgBlock = (file, alt) => ['<!-- wp:image -->', '<figure class="wp-block-image size-large"><img src="../assets/' + file + '" alt="' + alt + '" width="420" height="120" loading="lazy"/><figcaption>' + alt + ' (عکس رسمی: mikrotik.com — تصویر واقعی embed نشده)</figcaption></figure>', '<!-- /wp:image -->'].join(NLX);
  const embedded = f => html.includes('assets/' + f);
  /* 1) per-model paragraphs with EXACT <strong>SKU text */
  const strongPairs = [
    ['hEX lite (RB750r2)', 'schematic-hex-lite-rb750r2.svg'],
    ['hEX (RB750Gr3)', 'schematic-hex-rb750gr3.svg'],
    ['hEX refresh (E50UG)', 'schematic-hex-refresh-e50ug.svg'],
    ['hEX S (RB760iGS)', 'schematic-hex-s-rb760igs.svg'],
    ['RB951Ui-2HnD', 'schematic-rb951ui-2hnd.svg'],
    ['hAP (RB951Ui-2nD)', 'schematic-hap-rb951ui-2nd.svg'],
    ['RB2011UiAS-2HnD', 'schematic-rb2011uias-2hnd-in.svg'],
    ['RB3011UiAS-RM', 'schematic-rb3011uias-rm.svg'],
    ['RB4011iGS+RM', 'schematic-rb4011igs-rm.svg'],
    ['L009UiGS-RM', 'schematic-l009uigs-rm.svg'],
    ['RB5009UG+S+IN', 'schematic-rb5009ug-s-in.svg'],
    ['CCR1009/CCR1036', 'schematic-ccr1009-ccr1036.svg'],
    ['CCR2004-1G-12S+2XS', 'schematic-ccr2004-1g-12s-2xs.svg'],
    ['CCR2116-12G-4S+', 'schematic-ccr2116-12g-4s.svg'],
    ['CCR2216-1G-12XS-2XQ', 'schematic-ccr2216-1g-12xs-2xq.svg'],
  ];
  for (const [sku, file] of strongPairs) {
    const anchor = '<!-- wp:paragraph -->' + NLX + '<p><strong>' + sku + '</strong>';
    const i = html.indexOf(anchor);
    if (i >= 0 && !embedded(file)) {
      html = html.slice(0, i) + imgBlock(file, sku + ' — شماتیک تألیفی') + NLX + NLX + html.slice(i);
      imgCount++;
    }
  }
  /* 2) table-only models (RB951/hAP/CCR1009-family): embed right after the quick-compare table */
  const tableEnd = html.indexOf('<!-- /wp:table -->');
  if (tableEnd >= 0) {
    const tableOnly = [
      ['schematic-rb951ui-2hnd.svg', 'RB951Ui-2HnD — شماتیک تألیفی'],
      ['schematic-hap-rb951ui-2nd.svg', 'hAP (RB951Ui-2nD) — شماتیک تألیفی'],
      ['schematic-ccr1009-ccr1036.svg', 'CCR1009/CCR1036 (خانواده) — شماتیک تألیفی'],
      ['schematic-hap-wi-fi-hap-ax-3.svg', 'hAPهای Wi-Fi دار — شماتیک تألیفی'],
    ].filter(([f]) => !embedded(f));
    if (tableOnly.length) {
      const ins = tableEnd + '<!-- /wp:table -->'.length;
      const blocks = tableOnly.map(([f, alt]) => imgBlock(f, alt)).join(NLX + NLX);
      html = html.slice(0, ins) + NLX + NLX + blocks + html.slice(ins);
      imgCount += tableOnly.length;
    }
  }
  /* 2b) hAP Wi-Fi family paragraph (short name in MD, no suffix) — same outside-block rule */
  const hapShort = '<p><strong>hAPهای Wi-Fi دار</strong>';
  const hapI = html.indexOf(hapShort);
  if (hapI >= 0 && !embedded('schematic-hap-wi-fi-hap-ax-3.svg')) {
    const blockStart = html.lastIndexOf('<!-- wp:paragraph -->', hapI);
    html = html.slice(0, blockStart) + imgBlock('schematic-hap-wi-fi-hap-ax-3.svg', 'hAPهای Wi-Fi دار — شماتیک تألیفی') + NLX + NLX + html.slice(blockStart);
    imgCount++;
  }
  /* 3) switch guides: embed ALL switch schematics after first table (full coverage) */
  const isSwitch = String(perModel).includes('switches');
  if (isSwitch) {
    const firstTableEnd = html.indexOf('<!-- /wp:table -->');
    if (firstTableEnd >= 0) {
      const ins = firstTableEnd + '<!-- /wp:table -->'.length;
      const allSwitch = Object.entries(SKU_SCHEMATIC).filter(([sku]) => sku.includes('CRS') || sku.includes('CSS') || sku.includes('RB260'));
      const blocks = allSwitch.filter(([sku]) => !embedded(SKU_SCHEMATIC[sku])).map(([sku, file]) => imgBlock(file, sku + ' — شماتیک تألیفی'));
      if (blocks.length) { html = html.slice(0, ins) + NLX + NLX + blocks.join(NLX + NLX) + html.slice(ins); imgCount += blocks.length; }
    }
  }
  const diagram = perModel.includes('switches') ? 'switch-decision.svg' : 'router-decision.svg';
  const decAlt = perModel.includes('switches') ? 'نمودار تصمیم سوئیچ/روترسوئیچ میکروتیک — شماتیک تألیفی' : 'نمودار تصمیم انتخاب روتر میکروتیک بر اساس نیاز — شماتیک تألیفی';
  const H2_END = '</h2>\n<!-- /wp:heading -->';
  const firstH2 = html.indexOf(H2_END);
  if (firstH2 >= 0 && !html.includes('assets/' + diagram)) {
    const ins = firstH2 + H2_END.length;
    const decBlock = '<!-- wp:image -->\n<figure class="wp-block-image size-large"><img src="../assets/' + diagram + '" alt="' + decAlt + '" width="640" height="420" loading="lazy"/><figcaption>' + decAlt + ' (تصویر شماتیک تألیفی TehNet)</figcaption></figure>\n<!-- /wp:image -->';
    html = html.slice(0, ins) + '\n\n' + decBlock + html.slice(ins);
  }
  /* repo-relative catalog links: from articles/ the CSVs are one level up */
  html = html.replace(/href="router-catalog\.csv"/g, 'href="../router-catalog.csv"').replace(/href="switch-catalog\.csv"/g, 'href="../switch-catalog.csv"');
  return { html, imgCount };
}

const jobs = [
  ['mikrotik-routers.fa.md', 'mikrotik-routers.gutenberg.html'],
  ['mikrotik-switches-crs.fa.md', 'mikrotik-switches-crs.gutenberg.html'],
];
const summary = [];
for (const [mdF, htmlF] of jobs) {
  const md = fs.readFileSync(path.join(DIR, mdF), 'utf8');
  const { html, imgCount } = mdToGutenberg(md, mdF);
  const full = '<!-- READY_FOR_REVIEW / NOT_DEPLOYED — generated deterministically by build-gutenberg.cjs from ' + mdF + ' -->\n' + html;
  fs.writeFileSync(path.join(DIR, htmlF), full, 'utf8');
  summary.push({ md: mdF, html: htmlF, bytes: Buffer.byteLength(full, 'utf8'), per_model_images: imgCount });
  console.log('BUILT ' + htmlF + ' bytes=' + summary[summary.length - 1].bytes + ' perModelImgs=' + imgCount);
}
fs.writeFileSync(path.join(DIR, 'build-summary.json'), JSON.stringify({ deterministic: true, jobs: summary }, null, 1), 'utf8');
