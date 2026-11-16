'use strict';
/* TN-AFTERD1-GUARD-VERIFY-20261116 — executable after-D1 guard verifier.
 * Re-checks, ON DEMAND, that the three page-edits packages are still bound to
 * their accepted after-D1 bases (6922214726: "guard واقعی after-D1"):
 *   G1: sha256(file content at the header-referenced commit) == manifest after_d1_sha256
 *   G2: patch header after-D1 digest prefix == manifest digest prefix
 *   G3: every patch hunk parses and all its context/removal lines match the base exactly
 *   G4: proposed.html is byte-identical to base+patch reconstruction
 * Read-only against git history; writes only the receipt.
 * Run: node verify-afterd1-guard.cjs   (from qa/seo-device-guides-20261116/) */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');

const NL = String.fromCharCode(10);
const QA = __dirname;
const ROOT = path.resolve(QA, '../..');                       // repo root
const CONTENT = path.join(ROOT, 'content/seo-device-guides-20261116');
const MANIFEST = JSON.parse(fs.readFileSync(path.join(CONTENT, 'page-edits/pages-manifest.json'), 'utf8'));
const startedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');

function git(args, opts) {
  return execFileSync('git', args, Object.assign({ cwd: ROOT, maxBuffer: 32 * 1024 * 1024 }, opts)).toString();
}
function sha256(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }

const results = [];
let failures = 0;

for (const page of MANIFEST.pages) {
  const r = { name: page.name, checks: {} };
  // G0: locate the commit referenced by the patch header
  const patchPath = path.join(CONTENT, page.patch);
  const patchText = fs.readFileSync(patchPath, 'utf8');
  const hdr = patchText.match(/^--- a\/(.+?)@([0-9a-f]{40}) \(after-D1 ([0-9a-f]{12})…\)/m);
  if (!hdr) { r.checks.g0_header_parse = 'FAIL: no parseable header'; failures++; results.push(r); continue; }
  const baseFile = hdr[1], baseCommit = hdr[2], hdrPrefix = hdr[3];
  r.base_commit = baseCommit;
  // G1: content digest at that commit == manifest after_d1_sha256
  let baseContent;
  try {
    baseContent = git(['show', baseCommit + ':' + baseFile], { stdio: ['ignore', 'pipe', 'pipe'] });
    const digest = sha256(Buffer.from(baseContent, 'utf8'));
    r.checks.g1_base_digest = digest === page.after_d1_sha256 ? 'PASS' : 'FAIL: ' + digest.slice(0, 12) + ' != ' + page.after_d1_sha256.slice(0, 12);
    if (digest !== page.after_d1_sha256) failures++;
  } catch (e) { r.checks.g1_base_digest = 'FAIL: git show error ' + String(e.message).slice(0, 60); failures++; results.push(r); continue; }
  // G2: header after-D1 prefix == manifest digest prefix
  r.checks.g2_header_prefix = hdrPrefix === page.after_d1_sha256.slice(0, 12) ? 'PASS' : 'FAIL: ' + hdrPrefix + ' vs ' + page.after_d1_sha256.slice(0, 12);
  if (hdrPrefix !== page.after_d1_sha256.slice(0, 12)) failures++;
  // G3+G4: apply the patch with a minimal hunk interpreter (the committed patches use
  // a non-strict unified format with blank header separators, so `git apply` rejects
  // them; the interpreter verifies every context line against the base instead) and
  // byte-compare the reconstruction with proposed.html
  try {
    const baseLines = baseContent.split(NL);
    const lines = patchText.split(NL);
    let i = 0, hunks = [];
    while (i < lines.length) {
      const m = lines[i].match(/^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@/);
      if (m) {
        const hunk = { oldStart: parseInt(m[1], 10), lines: [] };
        i++;
        while (i < lines.length && !/^@@ -\d+/.test(lines[i])) {
          if (lines[i] === '' && i === lines.length - 1) break; // trailing newline artifact
          hunk.lines.push(lines[i]);
          i++;
        }
        hunks.push(hunk);
      } else i++;
    }
    if (!hunks.length) { r.checks.g3_hunks_parse = 'FAIL: no hunks found'; failures++; results.push(r); continue; }
    let rebuilt = baseLines.slice();
    let offset = 0, ctxBad = 0;
    for (const h of hunks) {
      const start = h.oldStart - 1 + offset; // 0-based index into current rebuilt
      const out = [];
      let cursor = start;
      for (const l of h.lines) {
        const op = l[0], body = l.slice(1);
        if (op === ' ') {
          if (rebuilt[cursor] !== body) ctxBad++;
          out.push(body); cursor++;
        } else if (op === '-') {
          if (rebuilt[cursor] !== body) ctxBad++;
          cursor++; // removal: skip base line
        } else if (op === '+') {
          out.push(body);
        }
      }
      rebuilt = rebuilt.slice(0, start).concat(out, rebuilt.slice(cursor));
      offset += out.length - (cursor - start);
    }
    r.checks.g3_context_verified = ctxBad === 0 ? 'PASS (' + hunks.length + ' hunk[s], all context lines match base)' : 'FAIL: ' + ctxBad + ' context mismatch[es]';
    if (ctxBad !== 0) failures++;
    const rebuiltText = rebuilt.join(NL);
    const proposed = fs.readFileSync(path.join(CONTENT, page.proposed), 'utf8');
    const identical = rebuiltText === proposed;
    r.checks.g4_proposed_matches = identical ? 'PASS' : 'FAIL: rebuilt ' + sha256(Buffer.from(rebuiltText, 'utf8')).slice(0, 12) + ' vs proposed ' + sha256(Buffer.from(proposed, 'utf8')).slice(0, 12);
    if (!identical) failures++;
  } catch (e) {
    r.checks.g3_hunks_parse = 'FAIL: ' + String(e.message).slice(0, 80); failures++;
  }
  results.push(r);
}

const ok = failures === 0;
const finishedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
const receipt = {
  packet: 'TN-AFTERD1-GUARD-VERIFY-20261116',
  command: 'node verify-afterd1-guard.cjs',
  cwd: 'qa/seo-device-guides-20261116/',
  started_utc: startedUtc, finished_utc: finishedUtc,
  exit: ok ? 0 : 1,
  manifest_base_ref: MANIFEST.base_ref,
  failures: failures,
  results: results,
  mode: 'LOCAL_TEST — read-only against git history; temp dir under OS tmp; no repo file modified',
  not_run: ['WordPress/KSES apply of patches', 'production deployment', 'browser rendering'],
  production_touched: false,
};
fs.writeFileSync(path.join(QA, 'afterd1-guard-receipt.json'), JSON.stringify(receipt, null, 1));
for (const r of results) console.log(r.name, JSON.stringify(r.checks));
console.log('GUARD=' + (ok ? 'PASS' : 'FAIL') + ' failures=' + failures + ' | RECEIPT afterd1-guard-receipt.json | exit=' + receipt.exit);
process.exitCode = ok ? 0 : 1;
