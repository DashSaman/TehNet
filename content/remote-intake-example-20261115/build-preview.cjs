'use strict';
/* TN-REMOTE-INTAKE-COMPLETENESS-20261116 — deterministic preview regenerator.
 * Rule (proved identical to the original integration): PR101 body bytes (cb391c2d)
 * + the intake fragment inserted immediately BEFORE the why-tehnet heading comment.
 * SELF-PROOF: running this builder with the ORIGINAL fragment (395413a) must reproduce
 * the committed preview bytes exactly; only then is the NEW fragment written.
 * No browser; pure byte assembly. */
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const REPO = path.resolve(__dirname, '../..');
const PR101 = 'cb391c2dc262a65e524962fa7fc44a0187f476fe';
const BODY_FILE = 'content/remote-support-2026-11-01/remote-support.html';
const FRAGMENT_FILE = 'content/remote-intake-example-20261115/remote-request-example.gutenberg.html';
const PREVIEW_FILE = 'content/remote-intake-example-20261115/remote-support-with-intake.preview.html';
const ANCHOR = '<!-- wp:heading {"anchor":"why-tehnet"} -->';
const ORIG_PREVIEW_SHA = 'c33df1e3a033760915122e4f7268bd040987489b9d10ce5bffc41e5e772a8f49';

const sha = b => crypto.createHash('sha256').update(b).digest('hex');
function build(fragmentBytes) {
  const body = execFileSync('git', ['show', PR101 + ':' + BODY_FILE], { cwd: REPO, maxBuffer: 32 * 1024 * 1024 });
  const idx = body.indexOf(Buffer.from(ANCHOR, 'utf8'));
  if (idx < 0) throw new Error('why-tehnet anchor not found in PR101 body');
  const out = Buffer.concat([body.slice(0, idx), fragmentBytes, Buffer.from('\n', 'utf8'), body.slice(idx)]);
  if (out.includes(Buffer.from('<form', 'utf8'))) throw new Error('form detected in output');
  return out;
}

const newFragment = fs.readFileSync(path.join(REPO, FRAGMENT_FILE));
const origFragment = execFileSync('git', ['show', '395413a0bb1d57f63321e1fef6e9d78833a50ce3:' + FRAGMENT_FILE], { cwd: REPO, maxBuffer: 4 * 1024 * 1024 });

/* SELF-PROOF with the original fragment */
const proof = build(origFragment);
const proofSha = sha(proof);
if (proofSha !== ORIG_PREVIEW_SHA) {
  console.error('SELF-PROOF FAILED: original-fragment rebuild sha256 ' + proofSha + ' != committed preview ' + ORIG_PREVIEW_SHA);
  process.exit(1);
}
console.log('SELF_PROOF_OK original fragment -> committed preview bytes reproduced (' + proofSha.slice(0, 16) + '…)');

/* real regeneration with the NEW fragment */
const preview = build(newFragment);
fs.writeFileSync(path.join(REPO, PREVIEW_FILE), preview);
console.log('PREVIEW_REGENERATED newFragmentSha=' + sha(newFragment).slice(0, 16) + '… previewSha=' + sha(preview).slice(0, 16) + '… bytes=' + preview.length);
