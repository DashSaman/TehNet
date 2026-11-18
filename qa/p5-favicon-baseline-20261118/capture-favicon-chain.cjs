'use strict';
/* TN-P5-FAVICON-PUBLIC-BASELINE-20261118 — read-only public favicon-chain capturer.
 * Bounded: home + services + linked public manifest + /favicon.ico 302 + followed
 * target; max 3 public icon assets. No cookies/auth/admin/customer/form/payment/
 * security requests; no broad crawl; finite retries (2 per response). */
const fs = require('fs'), crypto = require('crypto'), { execSync } = require('node:child_process');
const out = {
  capture_type: 'read-only public favicon-chain capture',
  tool: 'curl (existing), unauthenticated, normal TLS',
  capture_start_utc: new Date().toISOString(),
  pre_work_git_head: execSync('git rev-parse HEAD').toString().trim(),
  responses: [], failures: []
};
function grab(name, url, redirects) {
  for (let attempt = 1; attempt <= 2; attempt++) {
    const t0 = new Date().toISOString();
    const tmp = 'tmp_fav_' + name + '.bin';
    try {
      const meta = execSync(
        'curl -sS --ssl-revoke-best-effort --max-time 30' +
        (redirects ? ' -L --max-redirs 2' : '') +
        ' -w "META|%{http_code}|%{content_type}|%{size_download}|%{url_effective}"' +
        ' -D "' + tmp + '.hdr"' +
        ' "' + url + '" -o "' + tmp + '" 2>nul',
        { encoding: 'utf8' }
      );
      const m = meta.match(/META\|(\d+)\|([^|]*)\|(\d+)\|(.*)$/);
      if (!m) throw new Error('meta parse fail');
      const b = fs.readFileSync(tmp);
      const hdr = fs.readFileSync(tmp + '.hdr', 'utf8');
      const loc = (hdr.match(/^location:\s*(.*)$/im) || [])[1] || null;
      out.responses.push({
        name, url, redirects_followed: !!redirects, attempt,
        request_started_utc: t0, response_completed_utc: new Date().toISOString(),
        status: +m[1], mime: m[2].trim(), bytes: +m[3], final_url: m[4].trim(),
        location_header: loc,
        raw_body_sha256: 'sha256:' + crypto.createHash('sha256').update(b).digest('hex')
      });
      try { fs.unlinkSync(tmp); fs.unlinkSync(tmp + '.hdr'); } catch (_) {}
      return;
    } catch (e) {
      const msg = String(e.message || e).slice(0, 140);
      out.failures.push({ name, url, attempt, error: msg });
      if (fs.existsSync(tmp)) { try { fs.unlinkSync(tmp); } catch (_) {} }
      if (fs.existsSync(tmp + '.hdr')) { try { fs.unlinkSync(tmp + '.hdr'); } catch (_) {} }
    }
  }
}
grab('home', 'https://tehnet.ir/', false);
grab('services', 'https://tehnet.ir/services/', false);
grab('manifest', 'https://tehnet.ir/?tn_pwa=manifest', false);
grab('favicon-ico-302', 'https://tehnet.ir/favicon.ico', false);
grab('favicon-followed-png', 'https://tehnet.ir/wp-includes/images/w-logo-gray-white-bg.png', false);
out.capture_end_utc = new Date().toISOString();
fs.writeFileSync(__dirname + '/fresh-capture-meta.json', JSON.stringify(out, null, 1));
console.log('RESPONSES=' + out.responses.length + ' FAILURES=' + out.failures.length);
console.log('CAPTURE_WINDOW=' + out.capture_start_utc + ' .. ' + out.capture_end_utc);
