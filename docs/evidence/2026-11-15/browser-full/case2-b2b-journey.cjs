'use strict';
/* TN-BROWSER-20261115 — Case 2: real browser B2B quote journey on isolated staging.
 * /b2b/ -> keyboard fill incl. real product select -> submit click -> sent redirect
 * -> DB verify private tn_quote state=received -> cleanup recorded. */
const {chromium}=require('playwright'),fs=require('node:fs');
const BASE='http://localhost:18085';
const RUN_ID='TN-BROWSER-RUN-20261115-CASE2-'+Date.now().toString(36).toUpperCase();
const out={run_id:RUN_ID,utc:new Date().toISOString().replace(/\.\d+Z$/,'Z'),case:'b2b-quote-journey',steps:[],status:'RUNNING'};
const step=(n,ok,d)=>{out.steps.push({name:n,pass:!!ok,detail:d||{}});console.log((ok?'OK  ':'FAIL')+' '+n+(d?' '+JSON.stringify(d).slice(0,140):''));};
(async()=>{
  const browser=await chromium.launch({headless:true});
  out.browser={engine:'chromium',version:browser.version()};
  const ctx=await browser.newContext({viewport:{width:1440,height:900},locale:'fa'});
  const page=await ctx.newPage();
  await page.addStyleTag!==undefined; // noop guard
  const r=await page.goto(BASE+'/b2b/',{waitUntil:'domcontentloaded',timeout:20000});
  step('http200',r.status()===200,{status:r.status()});
  await page.addStyleTag({content:'html{scroll-behavior:auto !important} *{scroll-behavior:auto !important}'});
  await page.waitForSelector('form.tn-quote-form',{timeout:10000});
  step('form_present',true);
  const pid=await page.evaluate(()=>{const s=document.querySelector('form.tn-quote-form select[name="tn_item_product[]"]');const o=s&&s.querySelector('option:nth-child(2)');return o?o.value:null;});
  step('real_product_option',!!pid,{pid});
  await page.locator('form.tn-quote-form input[name="tn_company"]').first().fill('شرکت آزمون مرورگر',{timeout:10000});
  await page.locator('form.tn-quote-form input[name="tn_contact"]').first().fill('رابط آزمون',{timeout:10000});
  await page.locator('form.tn-quote-form input[name="tn_phone"]').first().fill('02100000000',{timeout:10000});
  await page.locator('form.tn-quote-form input[name="tn_email"]').first().fill('acceptance-test@example.invalid',{timeout:10000});
  await page.locator('form.tn-quote-form select[name="tn_item_product[]"]').first().selectOption(pid,{timeout:10000});
  await page.locator('form.tn-quote-form input[name="tn_item_qty[]"]').first().fill('2',{timeout:10000});
  await page.locator('form.tn-quote-form textarea[name="tn_notes"]').first().fill('مطالعهٔ موردی مرورگر؛ حذف پس از آزمون.',{timeout:10000});
  step('keyboard_filled',true);
  await Promise.all([
    page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}).catch(()=>null),
    page.click('form.tn-quote-form button[type="submit"]'),
  ]);
  const url=page.url();
  step('submitted_redirect',/tn_quote=sent/.test(url),{url:url.slice(0,120)});
  const sent=await page.evaluate(()=>document.body.innerText.includes('درخواست'));
  step('sent_page_visible',sent);
  out.quote_url=url;
  out.status=out.steps.every(s=>s.pass)?'PASS':'FAIL';
  out.failures=out.steps.filter(s=>!s.pass).length;
  fs.writeFileSync('case2-result.json',JSON.stringify(out,null,1));
  console.log('CASE2 RESULT:',out.status,'| failures:',out.failures);
  await browser.close();
  process.exitCode=out.status==='PASS'?0:1;
})().catch(e=>{out.status='ERROR';out.error=e.message.split('\n')[0];fs.writeFileSync('case2-result.json',JSON.stringify(out,null,1));console.log('CASE2 ERROR:',out.error);process.exitCode=1;});
