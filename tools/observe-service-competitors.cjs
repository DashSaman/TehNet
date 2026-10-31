// Bounded public page observations; external scripts fenced, no performance/rank audit.
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
const targets = [
  'https://taraznet.com/network-support/',
  'https://www.parag.pro/services/network-support',
  'https://varianet.ir/services/network-support/',
];
(async () => {
  const out = process.argv[2];
  if (!out || !path.isAbsolute(out) || !fs.statSync(out).isDirectory()) throw Error('Existing absolute private output directory required');
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const rows = [];
  try {
    for (const [i, target] of targets.entries()) {
      for (const [width, js] of [[1440, true], [375, true], [375, false]]) {
        const context = await browser.newContext({ viewport: { width, height: 900 }, javaScriptEnabled: js });
        const blocked = new Set(); let nonRead = 0; const errors = [];
        await context.route('**/*', route => {
          const request = route.request(); const u = new URL(request.url());
          if (!['GET', 'HEAD', 'OPTIONS'].includes(request.method())) { ++nonRead; return route.abort(); }
          if (u.origin !== new URL(target).origin && !['data:', 'blob:'].includes(u.protocol)) { blocked.add(u.origin); return route.abort(); }
          return route.continue();
        });
        const page = await context.newPage(); page.on('pageerror', e => errors.push(e.name));
        try {
          const response = await page.goto(target, { waitUntil: 'domcontentloaded', timeout: 45000 });
          await page.waitForLoadState('networkidle', { timeout: 15000 }).catch(() => {});
          const data = await page.evaluate(() => ({
            title: document.title, h1_count: document.querySelectorAll('h1').length,
            overflow: document.documentElement.scrollWidth > innerWidth,
            visible_links: [...document.querySelectorAll('a[href]')].filter(a => a.getClientRects().length).length,
            visible_forms: [...document.querySelectorAll('form')].filter(a => a.getClientRects().length).length,
          }));
          await page.screenshot({ path: path.join(out, `competitor-${i}-${width}-${js}.png`), fullPage: false });
          rows.push({ target, width, js, status: response.status(), ...data, page_error_count: errors.length, blocked_external_origins: blocked.size, blocked_nonread_requests: nonRead });
        } catch (e) { rows.push({ target, width, js, outcome: 'OBSERVATION_FAILED', error_type: e.name }); }
        finally { await context.close(); }
      }
    }
  } finally { await browser.close(); }
  fs.writeFileSync(path.join(out, 'browser-observations.json'), JSON.stringify({ observed_utc: new Date().toISOString(), scope: 'Three service URLs; fenced desktop/mobile/no-JS layout observations only', limits: ['External assets fenced: not normal-user performance or full functionality', 'No forms submitted, portal logins, lead delivery, SLA tests or customer quality verification', 'No CWV field/lab, rank, traffic, backlink or AI-citation measurements'], rows }, null, 2));
  console.log(JSON.stringify({ observations: rows.length, successful_reads: rows.filter(r => r.status === 200).length, failed: rows.filter(r => r.outcome).length }));
})().catch(e => { console.error(e.name + ': observation runner failed; inspect private output'); process.exitCode = 1; });
