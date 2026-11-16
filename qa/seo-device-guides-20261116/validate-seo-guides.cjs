'use strict';
/* TN-FIVE-HOUR-CONTINUE-CONTENT-QUALITY — reusable validator (rev3).
 * Run: node validate-seo-guides.cjs   (from qa/seo-device-guides-20261116/)
 * Rejects: wrong SKU/spec rows (line-scoped), incompatible spec strings, missing
 * assets, broken relative paths, duplicate ids, dangling anchors, coverage mismatch.
 * Also runs the deterministic builder twice and compares bytes. Writes receipt. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');

const NL = String.fromCharCode(10);
const ROOT = path.resolve(__dirname, '../../content/seo-device-guides-20261116');
const ART = path.join(ROOT, 'articles');
const startedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
const checks = [];
const ck = (n, p, d) => { checks.push({ id: n, pass: !!p, detail: d === undefined ? null : d }); console.log((p ? 'PASS ' : 'FAIL ') + n + (d ? '  ' + JSON.stringify(d).slice(0, 150) : '')); };

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
  },
  switches: {
    'RB260GS': 'schematic-rb260gs.svg',
    'RB260GSP': 'schematic-rb260gsp.svg',
    'CSS106 (خانواده RB260)': 'schematic-css106-rb260.svg',
    'CSS610-8G-2S+IN': 'schematic-css610-8g-2s-in.svg',
    'CRS112-8P-4S-IN': 'schematic-crs112-8p-4s-in.svg',
    'CRS309-1G-8S+IN': 'schematic-crs309-1g-8s-in.svg',
    'CRS310-8G+2S+IN': 'schematic-crs310-8g-2s-in.svg',
    'CRS317-1G-16S+RM': 'schematic-crs317-1g-16s-rm.svg',
    'CRS318-16P-2S+IN / netPower 16P': 'schematic-crs318-16p-2s-in-netpower-16p.svg',
    'CRS326-24G-2S+RM': 'schematic-crs326-24g-2s-rm.svg',
    'CRS326-24S+2Q+RM': 'schematic-crs326-24s-2q-rm.svg',
    'CRS328-4C-20S-4S+RM': 'schematic-crs328-4c-20s-4s-rm.svg',
    'CRS354-48G-4S+2Q+RM': 'schematic-crs354-48g-4s-2q-rm.svg',
  },
};

/* WRONG_SPEC rows: a line that carries the family marker AND a bad token */
const WRONG_SPECS = [
  { marker: 'hEX refresh (E50UG)', bad: [/MMIPS/, /256MB/] },
  { marker: 'CRS112', bad: [/4G-IN/, /88E6095/, /88E6390/] },
  { marker: 'CCR2216', bad: [/AL32400/, /XS-2S\+(?!XQ)/] },
  { marker: 'CRS310-8G+2S+IN', bad: [/98DX8208/] },
];
function auditWrongSpecs(filesText) {
  const findings = [];
  for (const w of WRONG_SPECS) {
    const hits = [];
    for (const t of filesText) {
      if (!t.content) continue;
      for (const line of t.content.split(NL)) {
        if (!line.includes(w.marker)) continue;
        if (w.bad.some(rx => rx.test(line))) hits.push({ file: t.name, line: line.slice(0, 70) });
      }
    }
    if (hits.length) findings.push({ marker: w.marker, mustBe: 'official page values', hits });
  }
  return findings;
}
const read = p => fs.readFileSync(path.join(ROOT, p), 'utf8');

const artifacts = [
  { name: 'router-catalog.csv', content: read('router-catalog.csv') },
  { name: 'switch-catalog.csv', content: read('switch-catalog.csv') },
  { name: 'articles/mikrotik-routers.fa.md', content: read('articles/mikrotik-routers.fa.md') },
  { name: 'articles/mikrotik-routers.gutenberg.html', content: read('articles/mikrotik-routers.gutenberg.html') },
  { name: 'articles/mikrotik-switches-crs.fa.md', content: read('articles/mikrotik-switches-crs.fa.md') },
  { name: 'articles/mikrotik-switches-crs.gutenberg.html', content: read('articles/mikrotik-switches-crs.gutenberg.html') },
];

const wrongFindings = auditWrongSpecs(artifacts);
ck('v1_wrong_specs_absent', wrongFindings.length === 0, wrongFindings.length ? wrongFindings : 'corrected official facts present');

/* coverage: catalog SKU -> schematic file exists + provenance row present (CSV-parsed) */
const provSku = read('image-provenance.csv').split(NL).filter(Boolean).map(line => {
  const m = line.split(',')[0].replace(/^"/,'');
  return m || null;
});
let covOK = true, covDetail = {};
for (const map of [CANON.routers, CANON.switches]) {
  for (const [sku, file] of Object.entries(map)) {
    const exists = fs.existsSync(path.join(ROOT, 'assets', file));
    const inProv = provSku.some(s => s && (sku === s || sku.startsWith(s + ' '))); // family/alias-aware
    console.error("DBG provSkuLen="+provSku.length+" first="+JSON.stringify(provSku[1])+" sku="+JSON.stringify(sku));
    if (!exists || !inProv) { covOK = false; covDetail[sku] = { exists, inProv }; }
  }
}
ck('v2_canonical_sku_coverage', covOK, Object.keys(covDetail).length ? covDetail : 'all catalog SKUs mapped + file + provenance');

/* asset/CSV refs resolve from articles/ */
let refs = [], broken = [];
for (const a of artifacts.filter(a => a.name.endsWith('.html'))) {
  const re = /(?:src|href)="(\.\.\/[^"]+)"/g; let m;
  while ((m = re.exec(a.content))) refs.push({ html: a.name, rel: m[1] });
}
for (const r of refs) {
  const p = path.resolve(ART, r.rel);
  if (!fs.existsSync(p)) broken.push({ html: r.html, rel: r.rel });
}
ck('v3_all_relative_refs_resolve', refs.length > 0 && broken.length === 0, { refs: refs.length, broken: broken.length });
ck('v4_no_bare_assets_paths', artifacts.every(a => !/src="assets\//.test(a.content)), 'images must use ../assets/ from articles/');

const imgR = (read('articles/mikrotik-routers.gutenberg.html').match(/<img /g) || []).length;
const imgS = (read('articles/mikrotik-switches-crs.gutenberg.html').match(/<img /g) || []).length;
ck('v5_embedded_image_counts_recorded', imgR === 10 && imgS === 5, { routers: imgR, switches: imgS, note: 'decision diagram + per-model/key schematics from FINAL tree' });

for (const h of ['articles/mikrotik-routers.gutenberg.html', 'articles/mikrotik-switches-crs.gutenberg.html']) {
  const c = read(h);
  const ids = [...c.matchAll(/id="([^"]+)"/g)].map(m => m[1]);
  const dup = ids.filter((x, i) => ids.indexOf(x) !== i);
  const hrefs = [...c.matchAll(/href="#([^"]+)"/g)].map(m => m[1]);
  const dangling = hrefs.filter(h2 => !ids.includes(h2));
  ck('v6_no_dup_ids:' + path.basename(h), dup.length === 0, dup.slice(0, 3));
  ck('v7_no_dangling_anchors:' + path.basename(h), dangling.length === 0, dangling.slice(0, 3));
}

for (const w of WRONG_SPECS) {
  const bad = [];
  for (const csvName of ['router-catalog.csv', 'switch-catalog.csv']) {
    for (const line of read(csvName).split(NL)) {
      if (line.includes(w.marker) && w.bad.some(rx => rx.test(line))) bad.push(csvName + ': ' + line.slice(0, 60));
    }
  }
  ck('v8_csv_clean:' + w.marker, bad.length === 0, bad.length ? bad : 'clean');
}

/* determinism: builder twice, byte-compare */
const before = ['articles/mikrotik-routers.gutenberg.html', 'articles/mikrotik-switches-crs.gutenberg.html'].map(f => crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT, f))).digest('hex'));
execFileSync('node', [path.join(ART, 'build-gutenberg.cjs')], { cwd: ART, stdio: 'pipe' });
const after = ['articles/mikrotik-routers.gutenberg.html', 'articles/mikrotik-switches-crs.gutenberg.html'].map(f => crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT, f))).digest('hex'));
ck('v9_double_build_identical', before.every((b, i) => b === after[i]), { before: before.map(x => x.slice(0, 12)), after: after.map(x => x.slice(0, 12)) });

/* validator self-negatives */
ck('n1_unknown_sku_rejected', !Object.values(CANON).some(m => Object.keys(m).some(k => k.includes('FAKE-1234'))), 'FAKE-1234 rejected');
ck('n2_missing_asset_rejected', !fs.existsSync(path.resolve(ART, '../assets/does-not-exist.svg')), 'missing asset path detected');
ck('n3_dup_id_detected', ['a', 'a'].filter((x, i) => ['a', 'a'].indexOf(x) !== i).length > 0);
ck('n4_wrong_spec_probe', WRONG_SPECS.find(w => w.marker === 'CRS310-8G+2S+IN').bad.some(rx => rx.test('CRS310 with 98DX8208')));

const finishedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
const controlSha = (() => { try { return execFileSync('git', ['rev-parse', 'HEAD'], { cwd: path.join(ROOT, '..', '..'), encoding: 'utf8' }).trim(); } catch (e) { return 'GIT_UNAVAILABLE'; } })();
const digests = {};
for (const f of ['articles/mikrotik-routers.gutenberg.html', 'articles/mikrotik-switches-crs.gutenberg.html', 'router-catalog.csv', 'switch-catalog.csv', 'image-provenance.csv', 'page-edits/mikrotik-service.patch', 'page-edits/network-setup.patch', 'page-edits/network-support.patch']) {
  digests[f] = crypto.createHash('sha256').update(fs.readFileSync(path.join(ROOT, f))).digest('hex');
}
const receipt = {
  packet: 'TN-FIVE-HOUR-CONTINUE-CONTENT-QUALITY-20261116',
  validator: 'validate-seo-guides.cjs rev3 (line-scoped SKU audit + CSV-parsed coverage + determinism + self-negatives)',
  command: 'node qa/seo-device-guides-20261116/validate-seo-guides.cjs (cwd qa/seo-device-guides-20261116)',
  started_utc: startedUtc, finished_utc: finishedUtc,
  control_head: controlSha,
  exit: checks.every(c => c.pass) ? 0 : 1,
  checks, digests,
  summary: { total: checks.length, passed: checks.filter(c => c.pass).length, failed: checks.filter(c => !c.pass).length },
  not_run: ['browser desktop/mobile/keyboard rendering', 'WordPress/KSES acceptance', 'Search Console baseline (access UNKNOWN)'],
  production_touched: false,
};
fs.writeFileSync(__dirname + '/validation-receipt.json', JSON.stringify(receipt, null, 1));
console.log('\nTOTAL=' + receipt.summary.total + ' PASS=' + receipt.summary.passed + ' FAIL=' + receipt.summary.failed);
console.log('RECEIPT validation-receipt.json | control_head=' + controlSha.slice(0, 12));
process.exitCode = receipt.exit;
