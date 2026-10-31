'use strict';
// Read-only public acceptance. Never submit a production form or authenticate.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
const origin = 'https://tehnet.ir';
const out = path.resolve(process.argv[2]);
const checks = [];
function check(label, value) { assert.ok(value, label); checks.push(label); }

async function main() {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ channel: process.env.PLAYWRIGHT_CHANNEL || 'msedge', headless: true });
  const errors = [], rejected = [], assetFailures = [];
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, acceptDownloads: true });
    await context.route('**/*', route => {
      const r = route.request(), u = new URL(r.url());
      if (r.method() !== 'GET' || ![origin, 'null'].includes(u.origin)) {
        rejected.push({ method: r.method(), external: u.origin !== origin });
        return route.abort();
      }
      return route.continue();
    });
    const page = await context.newPage();
    page.on('pageerror', e => errors.push(e.message));
    page.on('response', r => { if (r.url().includes('/network-readiness.') && r.status() !== 200) assetFailures.push(r.status()); });
    for (const url of ['/services/voice-network-readiness/', '/lab/voice-network-checklist/']) {
      const response = await page.goto(origin + url, { waitUntil: 'networkidle' });
      check(url + ' HTTP200', response.status() === 200);
      check(url + ' single H1', await page.locator('h1').count() === 1);
      check(url + ' canonical', await page.locator('link[rel=canonical]').getAttribute('href') === origin + url);
      check(url + ' noindex retained', (await page.locator('meta[name=robots]').getAttribute('content')).includes('noindex'));
      check(url + ' desktop no overflow', await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      await page.screenshot({ path: path.join(out, url.includes('/lab/') ? 'lab-desktop.png' : 'service-desktop.png'), fullPage: true });
    }
    const tool = page.locator('[data-tn-readiness]');
    check('Eight manual fields', await tool.locator('select').count() === 8);
    check('Export enabled by actual deployed JS', await tool.locator('[data-tn-readiness-export]').isEnabled());
    await tool.locator('select').nth(0).selectOption('issue');
    const download = page.waitForEvent('download');
    await tool.locator('[data-tn-readiness-export]').click();
    const downloaded = await download;
    const file = path.join(out, 'manual-report.json');
    await downloaded.saveAs(file);
    const report = JSON.parse(fs.readFileSync(file, 'utf8'));
    check('Local JSON schema', report.schema === 'tehnet.voice-network-checklist.v1');
    check('No measurement claim', report.measured === false && report.type === 'manual-self-assessment');
    check('Eight answers and selected state', report.answers.length === 8 && report.answers[0].state === 'issue');
    await tool.locator('[data-tn-readiness-reset]').click();
    check('Reset all states', (await tool.locator('select').evaluateAll(nodes => nodes.map(n => n.value))).every(v => v === 'unknown'));
    check('Reset returns keyboard focus', await tool.locator('select').first().evaluate(n => document.activeElement === n));
    await page.setViewportSize({ width: 375, height: 812 });
    for (const url of ['/services/voice-network-readiness/', '/lab/voice-network-checklist/']) {
      await page.goto(origin + url, { waitUntil: 'networkidle' });
      check(url + ' mobile no overflow', await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
      await page.screenshot({ path: path.join(out, url.includes('/lab/') ? 'lab-mobile.png' : 'service-mobile.png'), fullPage: true });
    }
    const nojs = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 375, height: 812 } });
    await nojs.route('**/*', route => route.request().method() === 'GET' && route.request().url().startsWith(origin + '/') ? route.continue() : route.abort());
    const fallback = await nojs.newPage();
    await fallback.goto(origin + '/lab/voice-network-checklist/', { waitUntil: 'networkidle' });
    check('No-JS all questions readable', await fallback.locator('[data-tn-readiness] select').count() === 8);
    check('No-JS manual fallback visible', await fallback.locator('[data-tn-readiness] noscript').isVisible());
    check('No-JS export remains disabled', await fallback.locator('[data-tn-readiness-export]').isDisabled());
    check('No deployed readiness asset failures', assetFailures.length === 0);
    check('No page errors', errors.length === 0);
    check('No unexpected outgoing request attempted', rejected.length === 0);
    await nojs.close();
    await context.close();
    const result = { schema: 1, observed_utc: new Date().toISOString(), scope: 'Read-only production browser; no forms submitted', passed: checks.length, failed: 0, checks, post_requests: 0, cross_origin_requests: rejected.length };
    fs.writeFileSync(path.join(out, 'verification.json'), JSON.stringify(result, null, 2) + '\n');
    process.stdout.write(JSON.stringify({ status: 'PASS', passed: checks.length, failed: 0 }) + '\n');
  } finally { await browser.close(); }
}

main().catch(error => { process.stderr.write(error.stack + '\n'); process.exitCode = 1; });
