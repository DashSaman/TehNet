'use strict';
/* TN-REMOTE-INTAKE-COMPLETENESS-20261116 — preview regeneration (bounded patch).
 * The original full assembly rule (PR101 body + session-journey block + fragment,
 * with CRLF endings) is NOT documented in the repo, so a from-scratch rebuild was
 * rejected as drift-prone. Instead this builder applies the fragment-derived
 * substitutions to the APPROVED preview bytes, enforces a bounded undiff, and
 * verifies a round-trip: reverting the substitutions reproduces the approved bytes.
 * Canonical inputs pinned to the resolvable published commit. */
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const REPO = path.resolve(__dirname, '../..');
const PUBLISHED = '778ee3f4a5bdb852a1c491b3af12e263a9eee3ad'; // approved-bytes commit (resolvable)
const PREVIEW_FILE = 'content/remote-intake-example-20261115/remote-support-with-intake.preview.html';
const ORIG_PREVIEW_SHA = 'c33df1e3a033760915122e4f7268bd040987489b9d10ce5bffc41e5e772a8f49';

/* the exact fragment-derived substitutions (old -> new), also applied to the fragment file */
const EDITS = [
  ['نتیجهٔ مورد انتظار: دریافت و ارسال ایمیل بدون خطا.</p>',
   'نتیجهٔ مورد انتظار: دریافت و ارسال ایمیل بدون خطا. زمان شروع دقیق: نامعلوم؛ کاربر فقط «از دیروز صبح» گفته است. بازهٔ تماس مجاز فرضی: شنبه تا چهارشنبه، ساعت ۹ تا ۱۷.</p>', 1],
  ['نتیجهٔ مورد انتظار: اتصال شبکه برای همهٔ کاربران طبقهٔ دوم بازیابی شود.</p>',
   'نتیجهٔ مورد انتظار: اتصال شبکه برای همهٔ کاربران طبقهٔ دوم بازیابی شود. بازهٔ تماس مجاز فرضی: همهٔ روزهای هفته، ساعت ۱۰ تا ۱۶.</p>', 1],
  ['رمز، کد اتصال، فایل Backup یا اطلاعات مشتری نفرستید.</p>',
   'رمز، کد اتصال، فایل Backup یا اطلاعات مشتری نفرستید. اگر زمان شروع، علت یا دستگاه‌های درگیر را نمی‌دانید، همان را «نامعلوم» بنویسید؛ حدس زدن لازم نیست و اطلاعات ناقص مانع ثبت درخواست نمی‌شود.</p>', 1],
];

const approved = execFileSync('git', ['show', PUBLISHED + ':' + PREVIEW_FILE], { cwd: REPO, maxBuffer: 8 * 1024 * 1024 })
  .toString('utf8').replace(/\r\n/g, '\n');
const approvedSha = crypto.createHash('sha256').update(Buffer.from(approved, 'utf8')).digest('hex');
if (approvedSha !== ORIG_PREVIEW_SHA) throw new Error('approved bytes mismatch: ' + approvedSha);

let regenerated = approved;
for (const [oldS, newS, n] of EDITS) {
  if (!regenerated.includes(oldS)) throw new Error('anchor text not found: ' + oldS.slice(0, 30));
  regenerated = regenerated.split(oldS).join(newS);
}
/* bounded undiff: reverting the substitutions must reproduce the approved bytes */
let undiff = regenerated;
for (const [oldS, newS, n] of EDITS) {
  if (!undiff.includes(newS)) throw new Error('regenerated text missing (undiff) — diff not bounded');
  undiff = undiff.split(newS).join(oldS);
}
if (undiff !== approved) throw new Error('UNDIFF FAILED: diff exceeded the bounded substitutions');

const out = Buffer.from(regenerated.replace(/\n/g, '\r\n'), 'utf8'); // preserve committed CRLF form
fs.writeFileSync(path.join(REPO, PREVIEW_FILE), out);
console.log('REGEN_OK approvedSha=' + approvedSha.slice(0, 16) + '… newSha=' + crypto.createHash('sha256').update(out).digest('hex').slice(0, 16) + '… undiff=PASS');
