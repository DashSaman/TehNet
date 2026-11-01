'use strict';
// Public, read-only layout evidence. No forms, logins or competitor claims tested.
const fs = require('node:fs'); const path = require('node:path');
const { chromium } = require('playwright');
const out = path.resolve(process.argv[2]); fs.mkdirSync(out, { recursive: true });
const targets = [
  ['tehnet-services', 'https://tehnet.ir/services/'], ['tehnet-home', 'https://tehnet.ir/'],
  ['taraz-active', 'https://taraznet.com/active-network-services/'],
  ['taraz-monitoring', 'https://taraznet.com/active-network-services/network-monitoring/'],
  ['taraz-vmware', 'https://taraznet.com/active-network-services/configure-vmware/']
];
(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true }); const rows = [];
  try { for (const [name, url] of targets) { for (const width of [1440, 375]) {
    const context = await browser.newContext({ viewport: { width, height: 900 } });
    const origin = new URL(url).origin; let blockedWrites = 0;
    await context.route('**/*', route => {
      const req = route.request();
      if (!['GET', 'HEAD'].includes(req.method())) { blockedWrites++; return route.abort(); }
      return new URL(req.url()).origin === origin ? route.continue() : route.abort();
    });
    const page = await context.newPage(); const response = await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
    await page.screenshot({ path: path.join(out, `${name}-${width}.png`), fullPage: true });
    const row = await page.evaluate(() => { const main = document.querySelector('main') || document.body; return {
      title: document.title, h1: [...main.querySelectorAll('h1')].map(e => e.textContent.trim()),
      forms: main.querySelectorAll('form').length, links: [...main.querySelectorAll('a[href]')].map(a => ({ text: a.textContent.trim(), href: a.getAttribute('href') })),
      overflow: document.documentElement.scrollWidth > innerWidth,
    }; });
    rows.push({ name, url, width, status: response.status(), ...row, blockedWrites });
    await context.close();
  } } fs.writeFileSync(path.join(out, 'before.json'), JSON.stringify({ observed_utc: new Date().toISOString(), rows, scope: 'Five public pages; layout/navigation only; cross-origin assets fenced; no SLA, service capacity, delivery, rank or performance measurement' }, null, 2));
  console.log(JSON.stringify({ status: 'CAPTURED', pages: targets.length, screenshots: rows.length, rows: rows.map(({name,width,status,forms,overflow})=>({name,width,status,forms,overflow})) }));
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
