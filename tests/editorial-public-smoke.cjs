const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium } = require('playwright');
const base = 'https://tehnet.ir';
const route = '/learn/mikrotik/mtcna/routeros-winbox/';
const output = process.argv[2];

(async () => {
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const blocked = new Set(); const errors = []; const methods = new Set(); let checks = 0;
  const check = (condition, label) => { assert(condition, label); ++checks; };
  const observations = [];
  try {
    for (const [width, javascript] of [[1440, true], [375, true], [375, false]]) {
      const context = await browser.newContext({ viewport: { width, height: width === 375 ? 812 : 1000 }, javaScriptEnabled: javascript });
      await context.route('**/*', (handler) => {
        const request = handler.request(); const url = new URL(request.url()); methods.add(request.method());
        if (!['GET', 'HEAD'].includes(request.method())) return handler.abort();
        if (url.origin !== base && !['data:', 'blob:'].includes(url.protocol)) { blocked.add(url.origin); return handler.abort(); }
        return handler.continue();
      });
      const page = await context.newPage(); page.on('pageerror', (error) => errors.push(error.message));
      const response = await page.goto(base + route, { waitUntil: 'networkidle' });
      check(response.status() === 200, 'Live HTTP200');
      check(await page.locator('h1').count() === 1, 'One H1');
      check((await page.locator('h1').innerText()).includes('شروع با RouterOS و Winbox'), 'Existing lesson H1 retained');
      check(await page.locator('link[rel="canonical"]').getAttribute('href') === base + route, 'Original canonical retained');
      check((await page.locator('meta[name="robots"]').getAttribute('content')).includes('noindex'), 'Deliberate noindex retained');
      const text = await page.locator('main').innerText();
      check(text.includes('سناریوی آموزشی') && text.includes('فرم پذیرش بازیابی') && text.includes('اندازه‌گیری نشده'), 'Useful sections and unmeasured lab boundary visible');
      check(await page.evaluate(() => document.documentElement.scrollWidth === innerWidth), 'No horizontal overflow');
      check(await page.locator('main iframe').count() === 0 && await page.locator('main a[href="https://www.youtube.com/watch?v=Wbj3C0g__zw"]').count() === 1, 'Existing video link without automatic player');
      check(await page.locator('main a[href="/services/mikrotik-tehran/"]').count() === 1, 'Relevant CTA available');
      check(!text.includes('/system reset-configuration') && !text.includes('/system backup save name=before-lab'), 'Old direct-copy reset/unencrypted-backup examples absent');
      const modified = await page.locator('.tn-editorial-note time').getAttribute('datetime');
      check(new Date(modified).getTime() >= Date.parse('2026-10-31T22:00:00Z'), 'Actual release modification date rendered');
      if (javascript) await page.screenshot({ path: path.join(output, 'lesson-live-' + width + '.png'), fullPage: true });
      observations.push({ width, javascript, status: response.status(), modified, overflow: false });
      await context.close();
    }
    check(errors.length === 0, 'No page errors');
    check([...methods].every((method) => ['GET', 'HEAD'].includes(method)), 'No state-changing requests attempted');
    fs.writeFileSync(path.join(output, 'public-browser.json'), JSON.stringify({ status: 'PASS', scope: 'Read-only production existing lesson acceptance; default browser TLS validation', checks, observations, page_errors: errors, blocked_external_origins: blocked.size, methods: [...methods], form_submissions: 0, routeros_lab: 'NOT_RUN' }, null, 2));
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });
