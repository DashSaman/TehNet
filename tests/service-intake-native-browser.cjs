'use strict';
// Sends synthetic records ONLY to an operator-confirmed isolated preview.
// The private orchestrator verifies identity/egress and removes owned test records.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require('playwright');
const origin = process.env.TN_NATIVE_PREVIEW_URL;
assert.equal(process.env.TN_NATIVE_PREVIEW_ISOLATED, '1', 'Native isolation must be independently verified first');
const url = new URL(origin);
assert.ok(url.protocol === 'http:' && ['localhost', '127.0.0.1'].includes(url.hostname) && !url.username && !url.password);
const marker = process.env.TN_NATIVE_QA_RUN;
assert.match(marker || '', /^TNQAGROWTH[0-9A-F]{12,40}$/);
const out = path.resolve(process.argv[2]);
const checks = [];
function check(label, value) { assert.ok(value, label); checks.push(label); }
async function main() {
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ channel: process.env.PLAYWRIGHT_CHANNEL || 'msedge', headless: true });
  try {
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, acceptDownloads: true });
    const page = await context.newPage(); const errors = [];
    page.on('pageerror', err => errors.push(err.message));
    await context.route('**/*', route => route.request().url().startsWith(origin + '/') || route.request().url().startsWith('blob:') ? route.continue() : route.abort());
    for (const pathname of ['/services/voice-network-readiness/', '/lab/voice-network-checklist/']) {
      const response = await page.goto(origin + pathname, { waitUntil: 'networkidle' });
      check(pathname + ' responds 200', response.status() === 200);
      check(pathname + ' retains noindex', (response.headers()['x-robots-tag'] || '').includes('noindex') || (await page.locator('meta[name=robots]').getAttribute('content')).includes('noindex'));
      check(pathname + ' has one page H1', await page.locator('h1').count() === 1);
      check(pathname + ' canonical identifies the page', await page.locator('link[rel=canonical]').getAttribute('href') === origin + pathname);
      check(pathname + ' body uses actual rendered content', (await page.locator('body').innerText()).includes('شبکه') && !(await page.locator('body').innerText()).includes('[tn_voice_network_readiness]'));
    }
    const tool = page.locator('[data-tn-readiness]');
    check('Native shortcode has all eight questions', await tool.locator('select').count() === 8);
    await tool.locator('select').nth(0).selectOption('issue');
    check('Native enqueued script updates summary', (await tool.locator('output').innerText()).includes('نیاز به اصلاح: ۱'));
    const downloaded = page.waitForEvent('download'); await tool.locator('[data-tn-readiness-export]').click();
    const download = await downloaded; await download.saveAs(path.join(out, 'native-manual-report.json'));
    const report = JSON.parse(fs.readFileSync(path.join(out, 'native-manual-report.json'), 'utf8'));
    check('Native export is a manual report with selected state', report.measured === false && report.answers.length === 8 && report.answers[0].state === 'issue');
    await page.setViewportSize({ width: 375, height: 812 });
    check('Native themed mobile has no horizontal overflow', await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await tool.screenshot({ path: path.join(out, 'native-tool-mobile.png') });
    const supportResponse = await page.goto(origin + '/support/?tn_service_context=voice-network', { waitUntil: 'networkidle' });
    check('Intake context does not collide with WordPress service CPT routing', supportResponse.status() === 200);
    const ticket = page.locator('form.tn-ticket-form');
    check('Ticket nonce belongs to submitted FormData', await ticket.evaluate(form => !!new FormData(form).get('_wpnonce') && form.querySelector('[name=_wpnonce]').form === form));
    check('Service context and subject are prefilled', await ticket.locator('[name=tn_service_context]').inputValue() === 'voice-network' && (await ticket.locator('[name=tn_subject]').inputValue()).includes('شبکه'));
    await ticket.locator('[name=tn_name]').fill('آزمون خصوصی'); await ticket.locator('[name=tn_email]').fill('qa@example.invalid');
    await ticket.locator('[name=tn_subject]').fill(marker + '-approved'); await ticket.locator('[name=tn_message]').fill('این درخواست مصنوعی فقط در نسخهٔ آزمایشی ایجاد شده است.');
    await Promise.all([page.waitForURL('**/support/?tn_ticket=sent'), ticket.locator('[type=submit]').click()]);
    check('Actual approved-context ticket POST succeeds', new URL(page.url()).searchParams.get('tn_ticket') === 'sent');
    await page.goto(origin + '/support/?tn_service_context%5B%5D=voice-network', { waitUntil: 'networkidle' });
    check('Array query cannot inject service context', await ticket.locator('[name=tn_service_context]').count() === 0 && await ticket.locator('[name=tn_subject]').inputValue() === '');
    await ticket.locator('[name=tn_name]').fill('آزمون خصوصی'); await ticket.locator('[name=tn_email]').fill('qa@example.invalid');
    await ticket.locator('[name=tn_subject]').fill(marker + '-array'); await ticket.locator('[name=tn_message]').fill('این درخواست مصنوعی برای بررسی رد ورودی آرایه‌ای است.');
    await ticket.evaluate(form => { const field = document.createElement('input'); field.type = 'hidden'; field.name = 'tn_service_context[]'; field.value = 'voice-network'; form.appendChild(field); });
    await Promise.all([page.waitForURL('**/support/?tn_ticket=sent'), ticket.locator('[type=submit]').click()]);
    check('Array POST retains valid ticket workflow', new URL(page.url()).searchParams.get('tn_ticket') === 'sent');
    const invalid = await page.request.post(origin + '/wp-admin/admin-post.php', { form: { action: 'tn_ticket_submit', _wpnonce: 'invalid-synthetic', tn_name: 'آزمون خصوصی', tn_email: 'qa@example.invalid', tn_subject: marker + '-invalid', tn_message: 'درخواست با nonce نامعتبر نباید ذخیره شود.' } });
    check('Invalid nonce is rejected by native WordPress', invalid.status() === 403);
    await page.goto(origin + '/b2b/', { waitUntil: 'networkidle' });
    const quote = page.locator('form.tn-quote-form');
    check('B2B nonce belongs to submitted FormData', await quote.evaluate(form => !!new FormData(form).get('_wpnonce') && form.querySelector('[name=_wpnonce]').form === form));
    await quote.locator('[name=tn_company]').fill(marker); await quote.locator('[name=tn_contact]').fill('آزمون خصوصی');
    await quote.locator('[name=tn_phone]').fill('00000000'); await quote.locator('[name=tn_email]').fill('qa@example.invalid');
    const product = await quote.locator('select').nth(0).locator('option').nth(1).getAttribute('value');
    await quote.locator('select').nth(0).selectOption(product); await quote.locator('[name="tn_item_qty[]"]').nth(0).fill('2.5');
    await quote.locator('[name=tn_notes]').fill('درخواست مصنوعی نسخهٔ آزمایشی؛ فروش یا تأمین واقعی نیست.');
    await Promise.all([page.waitForURL('**/b2b/?tn_quote=sent'), quote.locator('[type=submit]').click()]);
    check('Actual B2B request POST succeeds', new URL(page.url()).searchParams.get('tn_quote') === 'sent');
    check('No uncaught native-page JavaScript errors', errors.length === 0);
    fs.writeFileSync(path.join(out, 'browser-verification.json'), JSON.stringify({ observed_utc: new Date().toISOString(), scope: 'Isolated native WordPress preview only; synthetic records checked and cleaned by private orchestrator', passed: checks.length, failed: 0, checks, production_changed: false }, null, 2) + '\n');
    console.log(JSON.stringify({ passed: checks.length, failed: 0, scope: 'isolated native WordPress browser/HTTP only' }));
    await context.close();
  } finally { await browser.close(); }
}
main().catch(err => { console.error(err); process.exitCode = 1; });
