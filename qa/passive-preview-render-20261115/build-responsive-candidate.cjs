'use strict';
/* TN-PASSIVE-RESPONSIVE-PREVIEW-20261115 — deterministic candidate builder.
 * Reads the pinned canonical passive draft bytes and emits the preview candidate:
 * canonical bytes preserved (cells/captions/wording untouched) + narrowly scoped
 * table-scroll wrappers mirroring the theme's own established pattern
 * (.tn-decision-table: max-width:100%; overflow-x:auto) plus keyboard reachability
 * (tabindex=0 + role=region + aria-label). NOT_DEPLOYED preview proposal. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const REPO = path.resolve(__dirname, '../..');
const CANONICAL = process.env.TN_RENDER_INPUT || path.join(__dirname, 'rendered-source.snapshot.html');
const OUT = process.env.TN_CANDIDATE_OUT || path.join(REPO, 'content/passive-responsive-preview-20261115/passive-responsive-preview.candidate.html');
const PINNED_SHA256 = '180ddbf10d208abe6ffbc5f4f48e97a417908052c6053a9261235ba170c3d16b';

const src = fs.readFileSync(CANONICAL, 'utf8');
const srcSha = crypto.createHash('sha256').update(Buffer.from(src, 'utf8')).digest('hex');
if (srcSha !== PINNED_SHA256) {
  console.error('REJECTED: canonical digest mismatch — got ' + srcSha.slice(0, 16) + '…');
  process.exit(1);
}

const WRAPPER_OPEN = '<div class="tn-preview-table-scroll" tabindex="0" role="region" aria-label="جدول — برای دیدن همه ستون‌ها افقی بپیمایید">';
const STYLE = [
  '<style data-tn-preview="scoped-table-scroll">',
  '/* TN-PASSIVE-RESPONSIVE-PREVIEW-20261115 — scoped to .tn-preview-table-scroll only;',
  '   mirrors the pinned theme pattern .tn-decision-table (visual-refresh.css:80-84):',
  '   wrapper max-width:100%; overflow-x:auto with table width:100%; min-width:44rem;',
  '   table-layout:fixed so columns keep readable width and the wrapper scrolls.',
  '   Canonical bytes untouched. */',
  '.tn-preview-table-scroll{max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch;margin-block:1.5rem;border:1px solid #d9dde3;border-radius:.65rem;outline-offset:2px}',
  '.tn-preview-table-scroll:focus-visible{outline:2px solid #1a6cff}',
  '.tn-preview-table-scroll table{width:100%;min-width:44rem;max-width:none;table-layout:fixed;border-collapse:collapse}',
  '.tn-preview-table-scroll th,.tn-preview-table-scroll td{overflow-wrap:anywhere}',
  '</style>',
].join('\n');

/* wrap each <table>…</table> occurrence (2 in the canonical draft; none nested) */
let count = 0;
const wrapped = src.replace(/<table\b[\s\S]*?<\/table>/g, m => {
  count++;
  return WRAPPER_OPEN + '\n' + m + '\n</div>';
});
if (count !== 2) { console.error('REJECTED: expected exactly 2 tables, wrapped ' + count); process.exit(1); }

const header = '<!-- TN-PASSIVE-RESPONSIVE-PREVIEW-20261115 candidate — canonical passive draft bytes preserved; scoped table-scroll wrappers + style block added; NOT_DEPLOYED preview proposal; source canonical sha256 ' + PINNED_SHA256 + ' -->\n';
const candidate = header + STYLE + '\n' + wrapped;
fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, candidate, 'utf8');

/* round-trip verification: strip added nodes -> must equal canonical bytes */
const stripped = candidate
  .replace(header, '')
  .replace(STYLE + '\n', '')
  .replace(/<div class="tn-preview-table-scroll"[^>]*>\n/g, '')
  .replace(/\n<\/div>/g, '');
const roundTrip = stripped === src;
const candSha = crypto.createHash('sha256').update(Buffer.from(candidate, 'utf8')).digest('hex');
const meta = {
  canonical_sha256: srcSha,
  candidate_sha256: candSha,
  tables_wrapped: count,
  roundtrip_preserves_canonical_bytes: roundTrip,
  generated_utc: new Date().toISOString().replace(/\.\d+Z$/, 'Z'),
};
fs.writeFileSync(path.join(path.dirname(OUT), 'candidate-build-meta.json'), JSON.stringify(meta, null, 1));
console.log('CANDIDATE_WRITTEN tables=' + count + ' roundtrip=' + roundTrip + ' sha256=' + candSha.slice(0, 16) + '…');
if (!roundTrip) { console.error('REJECTED: round-trip does not preserve canonical bytes'); process.exit(1); }
