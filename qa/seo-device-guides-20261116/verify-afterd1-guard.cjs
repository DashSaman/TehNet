'use strict';
/* TN-AFTERD1-GUARD-VERIFY-20261116 — executable after-D1 guard verifier.
 * REV 3 (TN-CLUSTER-HUB-LINKS correction, MANAGER_REVIEW 6973101846 item D):
 *   - pure core verifyPageCore({baseContent, patchText, proposedContent, afterD1Sha256,
 *     expectedGuides, forbiddenSlugs}) — the SAME consuming path for CLI and probes;
 *   - G5: every manifest expected_guides href occurs in the selected proposed page;
 *   - G6: none of the manifest forbidden_slugs (known-dead, replaced by the candidate
 *     repairs) reappears in the selected proposed page;
 *   - CRLF-normalizing reads (working-tree checkout artifact; blob semantics stay LF);
 *   - `--probes` mode: four negative probes (removed required guide, reintroduced
 *     dead slug, proposed bytes changed without patch update, wrong pinned base) run
 *     through the SAME core and must FAIL with the specific reasons.
 * G1: sha256(base content at the header-referenced commit) == manifest after_d1_sha256
 * G2: patch header after-D1 digest prefix == manifest digest prefix
 * G3: every patch hunk parses and all its context/removal lines match the base exactly
 * G4: proposed.html is byte-identical to base+patch reconstruction
 * Read-only against git history; writes only receipts.
 * Run: node verify-afterd1-guard.cjs [alt-manifest-rel-path|--probes]  (from qa/seo-device-guides-20261116/) */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');

const NL = String.fromCharCode(10);
const QA = __dirname;
const ROOT = path.resolve(QA, '../..');
const CONTENT = path.join(ROOT, 'content/seo-device-guides-20261116');
const ARG = process.argv[2] || '';
const PROBES = ARG === '--probes';
const MANIFEST_ARG = (!PROBES && ARG) ? ARG : '';
const MANIFEST_PATH = MANIFEST_ARG ? path.join(CONTENT, 'page-edits', MANIFEST_ARG) : path.join(CONTENT, 'page-edits/pages-manifest.json');
const MANIFEST = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));
const startedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
const sha256 = b => crypto.createHash('sha256').update(b).digest('hex');
const norm = s => s.replace(/\r\n/g, NL);

function git(args, opts) {
  return execFileSync('git', args, Object.assign({ cwd: ROOT, maxBuffer: 32 * 1024 * 1024 }, opts)).toString();
}

/* ---- PURE CORE: every consumer (CLI and probes) goes through this function ---- */
function verifyPageCore(input) {
  const r = { name: input.name, checks: {}, reasons: [] };
  let failures = 0;
  const patchText = norm(input.patchText);
  const proposed = norm(input.proposedContent);
  // G0: locate the commit referenced by the patch header
  const hdr = patchText.match(/^--- a\/(.+?)@([0-9a-f]{40}) \(after-D1 ([0-9a-f]{12})…\)/m);
  if (!hdr) {
    r.checks.g0_header_parse = 'FAIL: no parseable header';
    r.reasons.push('g0_header_parse');
    return { r, failures: failures + 1 };
  }
  const baseFile = hdr[1], baseCommit = hdr[2], hdrPrefix = hdr[3];
  r.base_commit = baseCommit;
  // G1
  let baseContent;
  try {
    baseContent = git(['show', baseCommit + ':' + baseFile], { stdio: ['ignore', 'pipe', 'pipe'] });
    const digest = sha256(Buffer.from(norm(baseContent), 'utf8'));
    const expected = input.afterD1Sha256;
    r.checks.g1_base_digest = digest === expected ? 'PASS' : 'FAIL: ' + digest.slice(0, 12) + ' != ' + expected.slice(0, 12);
    if (digest !== expected) { failures++; r.reasons.push('g1_base_digest_mismatch'); }
  } catch (e) {
    r.checks.g1_base_digest = 'FAIL: git show error ' + String(e.message).slice(0, 60);
    r.reasons.push('g1_git_show_error');
    return { r, failures: failures + 1 };
  }
  // G2
  r.checks.g2_header_prefix = hdrPrefix === input.afterD1Sha256.slice(0, 12) ? 'PASS' : 'FAIL: ' + hdrPrefix + ' vs ' + input.afterD1Sha256.slice(0, 12);
  if (hdrPrefix !== input.afterD1Sha256.slice(0, 12)) { failures++; r.reasons.push('g2_header_prefix_mismatch'); }
  // G3+G4
  try {
    const baseLines = norm(baseContent).split(NL);
    const lines = patchText.split(NL);
    let i = 0; const hunks = [];
    while (i < lines.length) {
      const m = lines[i].match(/^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@/);
      if (m) {
        const hunk = { oldStart: parseInt(m[1], 10), lines: [] };
        i++;
        while (i < lines.length && !/^@@ -\d+/.test(lines[i])) {
          if (lines[i] === '' && i === lines.length - 1) break;
          hunk.lines.push(lines[i]);
          i++;
        }
        hunks.push(hunk);
      } else i++;
    }
    if (!hunks.length) {
      r.checks.g3_hunks_parse = 'FAIL: no hunks found';
      r.reasons.push('g3_no_hunks');
      return { r, failures: failures + 1 };
    }
    let rebuilt = baseLines.slice();
    let offset = 0, ctxBad = 0;
    for (const h of hunks) {
      const start = h.oldStart - 1 + offset;
      const out = [];
      let cursor = start;
      for (const l of h.lines) {
        const op = l[0], body = l.slice(1);
        if (op === ' ') {
          if (rebuilt[cursor] !== body) ctxBad++;
          out.push(body); cursor++;
        } else if (op === '-') {
          if (rebuilt[cursor] !== body) ctxBad++;
          cursor++;
        } else if (op === '+') {
          out.push(body);
        }
      }
      rebuilt = rebuilt.slice(0, start).concat(out, rebuilt.slice(cursor));
      offset += out.length - (cursor - start);
    }
    r.checks.g3_context_verified = ctxBad === 0 ? 'PASS (' + hunks.length + ' hunk[s], all context lines match base)' : 'FAIL: ' + ctxBad + ' context mismatch[es]';
    if (ctxBad !== 0) { failures++; r.reasons.push('g3_context_mismatch'); }
    const rebuiltText = rebuilt.join(NL);
    const identical = rebuiltText === proposed;
    r.checks.g4_proposed_matches = identical ? 'PASS' : 'FAIL: rebuilt ' + sha256(Buffer.from(rebuiltText, 'utf8')).slice(0, 12) + ' vs proposed ' + sha256(Buffer.from(proposed, 'utf8')).slice(0, 12);
    if (!identical) { failures++; r.reasons.push('g4_proposed_bytes_differ'); }
  } catch (e) {
    r.checks.g3_hunks_parse = 'FAIL: ' + String(e.message).slice(0, 80);
    r.reasons.push('g3_parse_error');
    return { r, failures: failures + 1 };
  }
  // G5: expected guide edges — each expected href must occur in the selected proposed page
  if (Array.isArray(input.expectedGuides)) {
    const missing = input.expectedGuides.filter(href => proposed.indexOf('href="' + href + '"') === -1);
    r.checks.g5_expected_guides = missing.length === 0
      ? 'PASS (' + input.expectedGuides.length + ' canonical guide edges present)'
      : 'FAIL: missing ' + missing.join(', ');
    if (missing.length) { failures++; for (const m of missing) r.reasons.push('expected_guide_missing:' + m); }
  }
  // G6: forbidden known-dead slugs must not reappear
  if (Array.isArray(input.forbiddenSlugs)) {
    const present = input.forbiddenSlugs.filter(slug => proposed.indexOf(slug) !== -1);
    r.checks.g6_forbidden_slugs = present.length === 0
      ? 'PASS (' + input.forbiddenSlugs.length + ' known-dead slugs absent)'
      : 'FAIL: reintroduced ' + present.join(', ');
    if (present.length) { failures++; for (const p of present) r.reasons.push('forbidden_dead_slug_present:' + p); }
  }
  // G7 (6970814289 follow-up / 6980096096 item 1): EVERY /guides/ href in the selected
  // proposed page must be a known committed topic-map row — invented/unknown guide
  // slugs fail even when byte parity (G4) still passes.
  if (Array.isArray(input.topicMapSlugs)) {
    const used = proposed.match(/href="\/guides\/[a-z0-9-]+\/"/g) || [];
    const unknown = used.map(h => h.slice(6, -1)).filter(href => input.topicMapSlugs.indexOf(href) === -1);
    r.checks.g7_topic_map_known = unknown.length === 0
      ? 'PASS (' + used.length + ' guide hrefs, all committed topic-map rows)'
      : 'FAIL: unknown ' + unknown.join(', ');
    if (unknown.length) { failures++; for (const u of unknown) r.reasons.push('unknown_guide_href:' + u); }
  }
  return { r, failures };
}

if (PROBES) {
  /* ---- NEGATIVE PROBES: same core, mutated in-memory inputs from the real selected bytes ---- */
  const pages = MANIFEST.pages;
  const tmSlugs = MANIFEST.topic_map_file
    ? Array.from(new Set((fs.readFileSync(path.join(ROOT, MANIFEST.topic_map_file), 'utf8').replace(/\r\n/g, NL).match(/\/guides\/[a-z0-9-]+\//g) || [])))
    : [];
  const loadPage = (p) => ({
    patchText: fs.readFileSync(path.join(CONTENT, p.patch), 'utf8'),
    proposedContent: fs.readFileSync(path.join(CONTENT, p.proposed), 'utf8'),
    afterD1Sha256: p.after_d1_sha256,
    expectedGuides: p.expected_guides || [],
    forbiddenSlugs: p.forbidden_slugs || [],
    topicMapSlugs: tmSlugs,
  });
  const setup = pages.find(p => p.name === 'network-setup');
  const base = loadPage(setup);
  const probes = [];
  // P1: removed required guide — strip the S3 guide anchor from the proposed bytes
  {
    const mutated = base.proposedContent.replace('<a href="/guides/sfp-sfp-plus-guide/">', '<a href="#" data-removed="probe">');
    const out = verifyPageCore(Object.assign({}, base, { name: 'P1-removed-required-guide', proposedContent: mutated }));
    const ok = out.failures > 0 && out.r.reasons.some(x => x.indexOf('expected_guide_missing:/guides/sfp-sfp-plus-guide/') === 0);
    probes.push({ probe: 'P1_removed_required_guide', expected_failure: 'expected_guide_missing:/guides/sfp-sfp-plus-guide/', failed_as_expected: ok, reasons: out.r.reasons });
  }
  // P2: reintroduced known-dead slug — swap the repaired /services/ href back to the dead child page
  {
    const mutated = base.proposedContent.replace('<a href="/services/">خدمت سرور و مجازی‌سازی در تهران</a>', '<a href="/services/server-virtualization-tehran/">خدمت سرور و مجازی‌سازی در تهران</a>');
    const out = verifyPageCore(Object.assign({}, base, { name: 'P2-reintroduced-dead-slug', proposedContent: mutated }));
    const ok = out.failures > 0 && out.r.reasons.some(x => x.indexOf('forbidden_dead_slug_present:/services/server-virtualization-tehran/') === 0);
    probes.push({ probe: 'P2_reintroduced_dead_slug', expected_failure: 'forbidden_dead_slug_present:/services/server-virtualization-tehran/', failed_as_expected: ok, reasons: out.r.reasons });
  }
  // P3: proposed bytes changed without patch update — append a stray block to proposed
  {
    const mutated = base.proposedContent + '\n<!-- wp:paragraph --><p>probe stray</p><!-- /wp:paragraph -->\n';
    const out = verifyPageCore(Object.assign({}, base, { name: 'P3-proposed-changed-without-patch', proposedContent: mutated }));
    const ok = out.failures > 0 && out.r.reasons.indexOf('g4_proposed_bytes_differ') >= 0;
    probes.push({ probe: 'P3_proposed_changed_without_patch_update', expected_failure: 'g4_proposed_bytes_differ', failed_as_expected: ok, reasons: out.r.reasons });
  }
  // P4: wrong pinned base — patch header commit switched to the pre-D1 ref (778ee3f…)
  {
    const mutated = base.patchText.replace(/--- a\/(.+?)@[0-9a-f]{40} \(after-D1 [0-9a-f]{12}…\)/,
      '--- a/$1@778ee3f4a5bdb852a1c491b3af12e263a9eee3ad (after-D1 778ee3f4a5bd…)');
    const out = verifyPageCore(Object.assign({}, base, { name: 'P4-wrong-pinned-base', patchText: mutated }));
    /* the pre-D1 commit lacks the after-D1 payload file entirely, so the wrong-base
     * regression surfaces as g1_git_show_error — an equally specific failure reason */
    const ok = out.failures > 0 && (out.r.reasons.indexOf('g1_base_digest_mismatch') >= 0 || out.r.reasons.indexOf('g2_header_prefix_mismatch') >= 0 || out.r.reasons.indexOf('g1_git_show_error') >= 0);
    probes.push({ probe: 'P4_wrong_pinned_base', expected_failure: 'g1_base_digest_mismatch|g2_header_prefix_mismatch|g1_git_show_error', failed_as_expected: ok, reasons: out.r.reasons });
  }
  // P5 (6980096096 item 1): a JOINTLY updated patch+proposed pair carrying an extra
  // UNKNOWN /guides/ link — byte parity (G4) still passes, but G7 must reject the
  // unknown guide through the same consuming path.
  {
    const unknownSentence = ' درس <a href="/guides/probe-unknown-guide/">probe unknown</a> جدا توضیح داده می‌شود.';
    /* find a '+' added line in the setup patch that carries the office-network-design paragraph */
    const anchorLine = base.patchText.split('\n').find(l => l.charAt(0) === '+' && l.indexOf('/guides/office-network-design/') >= 0);
    if (!anchorLine) throw new Error('P5 anchor added-line not found');
    const mutatedLine = anchorLine.slice(0, -4) + unknownSentence + '</p>';
    const mutatedPatch = base.patchText.split(anchorLine).join('+' + mutatedLine.slice(1));
    /* the SAME sentence inserted into the proposed paragraph -> byte parity preserved */
    const proposedAnchor = base.proposedContent.indexOf('/guides/office-network-design/');
    const paraEnd = base.proposedContent.indexOf('</p>', proposedAnchor);
    const mutatedProposed = base.proposedContent.slice(0, paraEnd) + unknownSentence + base.proposedContent.slice(paraEnd);
    const out = verifyPageCore(Object.assign({}, base, { name: 'P5-joint-unknown-guide', patchText: mutatedPatch, proposedContent: mutatedProposed }));
    const ok = out.failures > 0
      && out.r.reasons.some(x => x.indexOf('unknown_guide_href:/guides/probe-unknown-guide/') === 0)
      && out.r.reasons.indexOf('g4_proposed_bytes_differ') === -1;
    probes.push({ probe: 'P5_joint_patch_plus_proposed_unknown_guide', expected_failure: 'unknown_guide_href:/guides/probe-unknown-guide/ (with G4 byte parity still passing)', failed_as_expected: ok, reasons: out.r.reasons });
  }
  const allOk = probes.every(p => p.failed_as_expected);
  const finishedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  const receipt = {
    packet: 'TN-AFTERD1-GUARD-PROBES-20261118',
    command: 'node verify-afterd1-guard.cjs --probes',
    cwd: 'qa/seo-device-guides-20261116/',
    started_utc: startedUtc, finished_utc: finishedUtc,
    exit: allOk ? 0 : 1,
    note: 'same verifyPageCore consuming path as the default guard; mutated in-memory inputs only — no repo file modified',
    probes: probes,
    all_probes_failed_as_expected: allOk,
    mode: 'LOCAL_TEST — read-only; no WordPress/browser/production effect',
  };
  fs.writeFileSync(path.join(QA, 'afterd1-guard-receipt-probes.json'), JSON.stringify(receipt, null, 1));
  for (const p of probes) console.log(p.probe, p.failed_as_expected ? 'FAILED-AS-EXPECTED' : 'UNEXPECTED-RESULT', JSON.stringify(p.reasons));
  console.log('PROBES=' + (allOk ? 'ALL-AS-EXPECTED' : 'MISMATCH') + ' | RECEIPT afterd1-guard-receipt-probes.json | exit=' + receipt.exit);
  process.exitCode = allOk ? 0 : 1;
} else {
  /* ---- CLI path: default or alternate manifest ---- */
  /* topic-map slug set for G7 (node parsing — grep mis-detects this UTF-8 file as binary) */
  const tmRel = MANIFEST.topic_map_file;
  const topicMapSlugs = tmRel
    ? Array.from(new Set((fs.readFileSync(path.join(ROOT, tmRel), 'utf8').replace(/\r\n/g, NL).match(/\/guides\/[a-z0-9-]+\//g) || [])))
    : null;
  const results = [];
  let failures = 0;
  for (const page of MANIFEST.pages) {
    const patchRel = page.patch.startsWith('page-edits/') ? page.patch : 'page-edits/' + page.patch;
    const proposedRel = page.proposed.startsWith('page-edits/') ? page.proposed : 'page-edits/' + page.proposed;
    const input = {
      name: page.name,
      patchText: fs.readFileSync(path.join(CONTENT, patchRel), 'utf8'),
      proposedContent: fs.readFileSync(path.join(CONTENT, proposedRel), 'utf8'),
      afterD1Sha256: page.after_d1_sha256,
      expectedGuides: page.expected_guides || null,
      forbiddenSlugs: page.forbidden_slugs || null,
      topicMapSlugs: topicMapSlugs || null,
    };
    const { r, failures: f } = verifyPageCore(input);
    failures += f;
    results.push(r);
  }
  const ok = failures === 0;
  const finishedUtc = new Date().toISOString().replace(/\.\d+Z$/, 'Z');
  const receiptName = MANIFEST_ARG ? 'afterd1-guard-receipt-candidates.json' : 'afterd1-guard-receipt.json';
  const receipt = {
    packet: 'TN-AFTERD1-GUARD-VERIFY-20261116',
    manifest_selected_bundle: MANIFEST.selected_bundle || null,
    command: 'node verify-afterd1-guard.cjs' + (MANIFEST_ARG ? ' ' + MANIFEST_ARG : ''),
    cwd: 'qa/seo-device-guides-20261116/',
    started_utc: startedUtc, finished_utc: finishedUtc,
    exit: ok ? 0 : 1,
    manifest_base_ref: MANIFEST.base_ref,
    failures: failures,
    results: results,
    mode: 'LOCAL_TEST — read-only against git history; writes only the receipt',
    not_run: ['WordPress/KSES apply of patches', 'production deployment', 'browser rendering'],
    production_touched: false,
  };
  fs.writeFileSync(path.join(QA, receiptName), JSON.stringify(receipt, null, 1));
  for (const r of results) console.log(r.name, JSON.stringify(r.checks));
  console.log('GUARD=' + (ok ? 'PASS' : 'FAIL') + ' failures=' + failures + ' | RECEIPT ' + receiptName + ' | exit=' + receipt.exit);
  process.exitCode = ok ? 0 : 1;
}
