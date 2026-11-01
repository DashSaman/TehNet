const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { chromium } = require('playwright');

const base = 'http://localhost:18085';
const target = '/learn/mikrotik/mtcna/ip-dhcp-dns/';
const out = process.argv[2];

(async () => {
  assert.equal(process.env.TN_NATIVE_PREVIEW_ISOLATED, '1');
  const account = JSON.parse(fs.readFileSync(0, 'utf8'));
  const browser = await chromium.launch({ channel: 'msedge', headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  const external = new Set();
  const errors = [];
  const observations = [];
  let checks = 0;
  const check = (condition, label) => { assert(condition, label); ++checks; };
  const fence = async (ctx) => {
    await ctx.route('**/*', (route) => {
      const request = route.request();
      const url = new URL(request.url());
      if (url.origin !== base && !['data:', 'blob:'].includes(url.protocol)) {
        external.add(url.origin); return route.abort();
      }
      if (url.pathname.startsWith('/wp-json/') && !['GET', 'HEAD', 'OPTIONS'].includes(request.method())) {
        return route.abort();
      }
      return route.continue();
    });
  };
  await fence(context);
  const page = await context.newPage();
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('dialog', (dialog) => dialog.accept());
  try {
    for (const width of [1440, 375]) {
      await page.setViewportSize({ width, height: width === 375 ? 812 : 1000 });
      const response = await page.goto(base + target, { waitUntil: 'networkidle' });
      check(response.status() === 200, 'Native lesson HTTP200');
      check(await page.locator('h1').count() === 1, 'One H1');
      check(await page.evaluate(() => document.documentElement.scrollWidth === innerWidth), 'No horizontal overflow');
      const text = await page.locator('main').innerText();
      check(text.includes('Reservation') && text.includes('برگهٔ پذیرش لاب'), 'Lease planning and acceptance sections render');
      check(text.includes('7.26') && text.includes('اندازه‌گیری نشده'), 'Version and unmeasured lab limitations visible');
      check(text.includes('disabled=yes') && text.includes('NoHostsFile') && text.includes('SERVFAIL'), 'Disabled lab fragment, controlled DNS query and response distinction visible');
      check((await page.locator('meta[name="robots"]').getAttribute('content')).includes('noindex'), 'Staging noindex retained');
      await page.screenshot({ path: path.join(out, 'lesson-' + width + '-full.png'), fullPage: true });
      observations.push({ width, status: response.status(), h1: 1, overflow: false });
    }
    const nojs = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 375, height: 812 } });
    await fence(nojs);
    const plain = await nojs.newPage();
    const nojsResponse = await plain.goto(base + target, { waitUntil: 'networkidle' });
    check(nojsResponse.status() === 200, 'No-JS HTTP200');
    check((await plain.locator('main').innerText()).includes('برگهٔ پذیرش لاب'), 'No-JS lesson available');
    check(await plain.locator('a[href="/services/mikrotik-tehran/"]').count() > 0, 'No-JS relevant service link');
    await nojs.close();
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.goto(base + '/wp-login.php?redirect_to=' + encodeURIComponent(base + '/wp-admin/post.php?post=63&action=edit'));
    await page.locator('#user_login').fill(account.username);
    await page.locator('#user_pass').fill(account.password);
    await Promise.all([page.waitForURL('**/wp-admin/**', { waitUntil: 'domcontentloaded', timeout: 90000 }), page.locator('#wp-submit').click()]);
    await page.waitForLoadState('networkidle', { timeout: 60000 });
    await page.waitForFunction(() => window.wp?.data?.select('core/block-editor')?.getBlocks()?.length > 0);
    const editor = await page.evaluate(() => {
      const blocks = wp.data.select('core/block-editor').getBlocks();
      const flat = [];
      const visit = (items) => { for (const block of items) { flat.push({ name: block.name, valid: block.isValid }); visit(block.innerBlocks || []); } };
      visit(blocks);
      const canonical = wp.blocks.serialize(blocks);
      const first = blocks.find((block) => block.name === 'core/paragraph');
      wp.data.dispatch('core/block-editor').updateBlockAttributes(first.clientId, { content: first.attributes.content + ' <em>TNQA-UNSAVED-EDIT</em>' });
      const changed = wp.data.select('core/editor').getEditedPostContent().includes('TNQA-UNSAVED-EDIT') && wp.data.select('core/editor').isEditedPostDirty();
      wp.data.dispatch('core/block-editor').resetBlocks(blocks);
      return { blocks: flat.length, names: [...new Set(flat.map((block) => block.name))], invalid: flat.filter((block) => block.valid === false), changed, restored: wp.blocks.serialize(wp.data.select('core/block-editor').getBlocks()) === canonical, source: canonical };
    });
    fs.writeFileSync(path.join(out, 'lesson-editor-canonical-private.txt'), editor.source); delete editor.source;
    check(editor.invalid.length === 0, 'All nested Gutenberg blocks valid');
    check(editor.changed && editor.restored, 'Unsaved edit and reset work');
    check(editor.names.every((name) => ['core/paragraph', 'core/heading', 'core/list', 'core/list-item', 'core/code', 'core/shortcode'].includes(name)), 'Only expected registered editable blocks');
    check(errors.length === 0, 'No browser page errors');
    fs.writeFileSync(path.join(out, 'browser-verification.json'), JSON.stringify({ scope: 'Temporary existing lesson in independently guarded native staging', status: 'PASS', checks, observations, editor, page_errors: errors, blocked_external_origins: external.size, page_saves: 0, production_mutations: 0 }, null, 2));
  } catch (error) {
    fs.writeFileSync(path.join(out, 'failure-page-private.html'), await page.content());
    await page.screenshot({ path: path.join(out, 'failure-page-private.png'), fullPage: true }).catch(() => {});
    throw error;
  } finally { await browser.close(); }
})().catch((error) => { console.error(error); process.exitCode = 1; });
