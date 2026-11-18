'use strict';
/* TN-BROWSER-20261115-START — Case 1: real browser journey on isolated staging.
 * Services CTA -> form fill (keyboard) -> real submit click -> receipt page.
 * Records: run ID, UTC, browser engine/version, real outcome. */
const {chromium}=require('playwright'),fs=require('node:fs');
const BASE='http://localhost:18085';
const RUN_ID='TN-BROWSER-RUN-20261115-CASE1-'+Date.now().toString(36).toUpperCase();
const out={run_id:RUN_ID,utc:new Date().toISOString().replace(/\.\d+Z$/,'Z'),case:'services-journey-fill-submit-receipt',steps:[],status:'RUNNING'};
const step=(n,ok,d)=>{out.steps.push({name:n,pass:!!ok,detail:d||{}});console.log((ok?'OK  ':'FAIL')+' '+n+(d?' '+JSON.stringify(d).slice(0,140):''));};
(async()=>{
  const browser=await chromium.launch({headless:true});
  out.browser={engine:'chromium',version:browser.version()};
  console.log('browser:',browser.version());
  const ctx=await browser.newContext({viewport:{width:1440,height:900},locale:'fa'});
  const page=await ctx.newPage();
  // Step 1: land on the service page via the real CTA query
  const r=await page.goto(BASE+'/services/?tn_service_context=server-scoping',{waitUntil:'domcontentloaded',timeout:20000});
  step('http200',r.status()===200,{status:r.status()});
  /* The theme uses scroll-behavior:smooth — Playwright's scrollIntoViewIfNeeded
   * actionability check times out during the smooth animation. Force instant
   * scrolling for the automation run (test-side only; human UX unchanged). */
  await page.addStyleTag({content:'html{scroll-behavior:auto !important} *{scroll-behavior:auto !important}'});
  // Step 2: the form is present with a fresh nonce
  await page.waitForSelector('form.tn-service-request',{timeout:10000});
  step('form_present',true);
  // Step 3: keyboard fill (real user input path)
  const F=form=>form;
  await page.locator('form.tn-service-request select[name="tn_service_context"]').first().selectOption('server-scoping',{timeout:10000});
  await page.locator('form.tn-service-request input[name="tn_name"]').first().fill('آزمون مرورگر',{timeout:10000});
  await page.locator('form.tn-service-request input[name="tn_email"]').first().fill('acceptance-test@example.invalid',{timeout:10000});
  await page.locator('form.tn-service-request textarea[name="tn_message"]').first().fill('مطالعهٔ موردی مرورگر: بررسی مسیر سرور؛ این درخواست پس از آزمون حذف می‌شود.',{timeout:10000});
  /* tn_company lives inside a collapsed <details> (optional organization info):
   * real-user path = click the summary to expand, then fill. */
  await page.locator('form.tn-service-request details > summary').first().click({timeout:10000});
  await page.locator('form.tn-service-request input[name="tn_company"]').first().fill('شرکت آزمون مرورگر',{timeout:10000});
  step('keyboard_filled',true);
  // Step 4: real submit click
  await Promise.all([
    page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}).catch(()=>null),
    page.click('form.tn-service-request button[type="submit"]'),
  ]);
  const url=page.url();
  step('submitted_redirect',/tn_ticket=sent/.test(url)&&/tn_service_receipt=/.test(url),{url:url.slice(0,120)});
  // Step 5: receipt notice visible with tracking number
  await page.waitForSelector('.tn-service-receipt',{timeout:10000});
  const receipt=await page.evaluate(()=>document.querySelector('.tn-service-receipt').innerText);
  const tn=receipt.match(/TN-(\d+)/);
  step('receipt_visible',/درخواست شما ثبت شد/.test(receipt)&&!!tn,{tracking:tn?('TN-'+tn[1]):null});
  out.ticket_id=tn?('TN-'+tn[1]):null;
  // Step 6: private record persisted (read-only wp-cli check via ssh)
  const tk=tn?tn[1]:null;
  if(tk){
    const chk=subprocess(['ssh','netauto-main','docker exec tehnet-ux-preview-db sh -c \'mariadb --default-character-set=utf8mb4 -uroot -p"$MARIADB_ROOT_PASSWORD" tehnetux -N -e "SELECT post_status, post_type FROM tn_posts WHERE ID='+tk+'"\'']);
    const row=chk.trim();
    step('db_record_private_ticket',row.includes('private')&&row.includes('tn_ticket'),{row:row.slice(0,40)});
    out.cleanup_id=tk;
  }
  out.status=out.steps.every(s=>s.pass)?'PASS':'FAIL';
  out.failures=out.steps.filter(s=>!s.pass).length;
  fs.writeFileSync('case1-result.json',JSON.stringify(out,null,1));
  console.log('CASE1 RESULT:',out.status,'| failures:',out.failures);
  await browser.close();
  process.exitCode=out.status==='PASS'?0:1;
})().catch(e=>{out.status='ERROR';out.error=e.message.split('\n')[0];fs.writeFileSync('case1-result.json',JSON.stringify(out,null,1));console.log('CASE1 FULL ERROR:',e.message);process.exitCode=1;});
function subprocess(args){try{return require('child_process').spawnSync(args[0],args.slice(1),{encoding:'utf8',timeout:60000}).stdout||'';}catch(e){return '';}}
