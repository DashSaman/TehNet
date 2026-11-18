'use strict';
const {chromium}=require('playwright'),fs=require('node:fs');
const BASE='http://localhost:18085';
const RUN_ID='TN-BROWSER-RUN-20261115-CASE3-'+Date.now().toString(36).toUpperCase();
const out={run_id:RUN_ID,utc:new Date().toISOString().replace(/\.\d+Z$/,'Z'),case:'support-ticket-journey',steps:[],status:'RUNNING'};
const step=(n,ok,d)=>{out.steps.push({name:n,pass:!!ok,detail:d||{}});console.log((ok?'OK  ':'FAIL')+' '+n+(d?' '+JSON.stringify(d).slice(0,140):''));};
(async()=>{
  const browser=await chromium.launch({headless:true});
  out.browser={engine:'chromium',version:browser.version()};
  const ctx=await browser.newContext({viewport:{width:375,height:667},locale:'fa'});
  const page=await ctx.newPage();
  const r=await page.goto(BASE+'/support/',{waitUntil:'domcontentloaded',timeout:20000});
  step('http200_mobile375',r.status()===200,{status:r.status()});
  await page.addStyleTag({content:'html{scroll-behavior:auto !important} *{scroll-behavior:auto !important}'});
  await page.waitForSelector('form.tn-ticket-form',{timeout:10000});
  step('form_present',true);
  await page.locator('form.tn-ticket-form input[name="tn_subject"]').first().fill('تست مرورگر تیکت',{timeout:10000});
  await page.locator('form.tn-ticket-form input[name="tn_name"]').first().fill('آزمون مرورگر',{timeout:10000});
  await page.locator('form.tn-ticket-form input[name="tn_email"]').first().fill('acceptance-test@example.invalid',{timeout:10000});
  await page.locator('form.tn-ticket-form textarea[name="tn_message"]').first().fill('مطالعهٔ موردی مرورگر موبایل؛ حذف پس از آزمون.',{timeout:10000});
  step('keyboard_filled_mobile375',true);
  await Promise.all([
    page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}).catch(()=>null),
    page.click('form.tn-ticket-form button[type="submit"]'),
  ]);
  const url=page.url();
  step('submitted_redirect',/tn_ticket=sent/.test(url),{url:url.slice(0,120)});
  out.status=out.steps.every(s=>s.pass)?'PASS':'FAIL';
  out.failures=out.steps.filter(s=>!s.pass).length;
  fs.writeFileSync('case3-result.json',JSON.stringify(out,null,1));
  console.log('CASE3 RESULT:',out.status,'| failures:',out.failures);
  await browser.close();
  process.exitCode=out.status==='PASS'?0:1;
})().catch(e=>{out.status='ERROR';out.error=e.message.split('\n')[0];fs.writeFileSync('case3-result.json',JSON.stringify(out,null,1));console.log('CASE3 ERROR:',out.error);process.exitCode=1;});
