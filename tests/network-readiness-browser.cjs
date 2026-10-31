'use strict';
// Portable component test. Set PHP_BINARY and NODE_PATH in the operator environment.
// Native WordPress and actual service submission require separate acceptance.
const assert = require('node:assert/strict');
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const out = path.resolve(process.argv[2] || path.join(root, 'qa/growth-2026-10-31/component-browser'));
const html = execFileSync(process.env.PHP_BINARY || 'php', [path.join(__dirname, 'fixtures/network-readiness.php')]);
const assetRoot = path.join(root, 'site/mu-plugins/tehnet-technical-resources');
const checks = [];
function check(label, value) { assert.ok(value, label); checks.push(label); }
async function main() {
  fs.mkdirSync(out, { recursive: true });
  const server = http.createServer((req, res) => {
    const files = {
      '/': [html, 'text/html; charset=utf-8'],
      '/network-readiness.css': [fs.readFileSync(path.join(assetRoot, 'network-readiness.css')), 'text/css'],
      '/network-readiness.js': [fs.readFileSync(path.join(assetRoot, 'network-readiness.js')), 'application/javascript']
    };
    const file = files[req.url];
    if (!file) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': file[1] }); res.end(file[0]);
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  let browser;
  try {
    browser = await chromium.launch({ channel: process.env.PLAYWRIGHT_CHANNEL || 'msedge', headless: true });
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, acceptDownloads: true });
    const page = await context.newPage();
    const errors = [], external = [];
    page.on('pageerror', err => errors.push(err.message));
    await context.route('**/*', route => {
      const url = route.request().url();
      if (!url.startsWith(origin + '/') && !url.startsWith('blob:')) { external.push(url); return route.abort(); }
      return route.continue();
    });
    await page.goto(origin, { waitUntil: 'networkidle' });
    const instances = page.locator('[data-tn-readiness]');
    check('Two independent rendered shortcode instances', await instances.count() === 2);
    const first = instances.nth(0), second = instances.nth(1);
    check('Eight labelled questions per instance', await first.locator('select').count() === 8 && await second.locator('label').count() === 8);
    check('All controls have associated visible labels', await page.locator('select').evaluateAll(elements => elements.every(el => el.labels.length === 1 && !!el.labels[0].textContent.trim())));
    check('IDs unique across instances', await page.locator('[id]').evaluateAll(elements => new Set(elements.map(el => el.id)).size === elements.length));
    check('Initial unknown summary is truthful', (await first.locator('output').innerText()).includes('بررسی‌نشده: ۸'));
    check('Live summary announced politely', await first.locator('output').getAttribute('aria-live') === 'polite');
    check('Progressive enhancement enables export', await first.locator('[data-tn-readiness-export]').isEnabled());
    await first.locator('select').nth(0).selectOption('ready');
    await first.locator('select').nth(1).selectOption('issue');
    await first.locator('select').nth(2).selectOption('na');
    const summary = await first.locator('output').innerText();
    check('Change events recalculate all four manual states', ['نیاز به اصلاح: ۱', 'بررسی‌نشده: ۵', 'دارای مدرک: ۱', 'بدون کاربرد: ۱'].every(s => summary.includes(s)));
    check('Second instance remains unchanged', (await second.locator('output').innerText()).includes('بررسی‌نشده: ۸'));
    await first.locator('select').nth(3).focus();
    await page.keyboard.press('ArrowDown'); await page.keyboard.press('Tab');
    check('Native select can be operated by keyboard', await first.locator('select').nth(3).inputValue() === 'ready');
    const downloadPromise = page.waitForEvent('download');
    await first.locator('[data-tn-readiness-export]').click();
    const download = await downloadPromise;
    const filename = path.join(out, 'manual-report.json'); await download.saveAs(filename);
    const data = JSON.parse(fs.readFileSync(filename, 'utf8'));
    check('Actual downloaded report uses versioned schema', data.schema === 'tehnet.voice-network-checklist.v1');
    check('Report explicitly states no measurements', data.measured === false && data.type === 'manual-self-assessment');
    check('Report preserves eight question keys and selected states', data.answers.length === 8 && new Set(data.answers.map(a => a.key)).size === 8 && data.answers[0].state === 'ready' && data.answers[1].state === 'issue');
    check('Report has a valid recorded timestamp', Number.isFinite(Date.parse(data.recorded_at)));
    check('Visible report is available without downloading again', await first.locator('pre').isVisible() && (await first.locator('pre').innerText()).includes('بدون اندازه‌گیری'));
    await first.locator('[data-tn-readiness-reset]').click();
    check('Reset restores unknown states and hides previous report', (await first.locator('select').evaluateAll(elements => elements.every(el => el.value === 'unknown'))) && await first.locator('pre').isHidden());
    check('Reset returns focus to first question', await first.locator('select').nth(0).evaluate(el => el === document.activeElement));
    await first.screenshot({ path: path.join(out, 'desktop.png') });
    await page.setViewportSize({ width: 375, height: 812 });
    check('375px viewport has no horizontal document overflow', await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    check('Mobile uses a single question column', await first.locator('.tn-readiness-grid').evaluate(el => getComputedStyle(el).gridTemplateColumns.split(' ').length === 1));
    check('Mobile interactive targets are at least 48px tall', await first.locator('select,button').evaluateAll(elements => elements.every(el => el.getBoundingClientRect().height >= 48)));
    await first.screenshot({ path: path.join(out, 'mobile.png') });
    check('No external HTTP request is made', external.length === 0);
    check('No uncaught browser JavaScript errors', errors.length === 0);
    check('No local/session storage is written', await page.evaluate(() => localStorage.length === 0 && sessionStorage.length === 0));
    const nojs = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 375, height: 812 } });
    const fallback = await nojs.newPage(); await fallback.goto(origin, { waitUntil: 'networkidle' });
    check('No-JS questions and guidance remain readable', await fallback.locator('legend:visible').count() === 16 && await fallback.locator('noscript p:visible').count() === 2);
    check('No-JS automatic controls stay disabled', await fallback.locator('button:disabled').count() === 4);
    check('No-JS mobile has no horizontal overflow', await fallback.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await nojs.close(); await context.close();
    const receipt = { observed_utc: new Date().toISOString(), scope: 'Synthetic local component fixture using real PHP renderer and JS/CSS; no native WordPress, theme or HTTP submission acceptance', checks, passed: checks.length, failed: 0, production_changed: false };
    fs.writeFileSync(path.join(out, 'verification.json'), JSON.stringify(receipt, null, 2) + '\n');
    console.log(JSON.stringify({ passed: checks.length, failed: 0, scope: receipt.scope }));
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
}
main().catch(err => { console.error(err); process.exitCode = 1; });
