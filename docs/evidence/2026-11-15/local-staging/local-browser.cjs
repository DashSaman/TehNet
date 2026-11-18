'use strict';
/* TN-LOCAL-STAGING-20261115 — real browser test on local staging (owner-authorized).
 * Combined journey: Services CTA + B2B + Support at desktop/mobile/RTL.
 * LOCAL_STAGING label per owner addendum 6899649773. NOT cloud. NOT E2E. */
const {chromium}=require('playwright'),fs=require('node:fs');
const BASE='http://localhost:18085';
const RUN_ID='TN-LOCAL-STAGING-'+Date.now().toString(36).toUpperCase();
const out={run_id:RUN_ID,label:'LOCAL_STAGING (owner temporary overnight permission)',utc:new Date().toISOString().replace(/\.\d+Z$/,'Z'),browser:null,checks:[],status:'RUNNING'};
const ck=(n,ok,d)=>{out.checks.push({name:n,pass:!!ok,detail:d||{}});if(!ok)out.failures++;console.log((ok?'OK  ':'FAIL')+' '+n+(d?' '+JSON.stringify(d).slice(0,120):''));};
out.failures=0;
(async()=>{
  const browser=await chromium.launch({headless:true});
  out.browser={engine:'chromium',version:browser.version()};
  let ctx=null;
  try{
    /* --- Desktop: Services CTA journey --- */
    ctx=await browser.newContext({viewport:{width:1440,height:900},locale:'fa'});
    let page=await ctx.newPage();
    const r1=await page.goto(BASE+'/services/network-setup-tehran/',{waitUntil:'domcontentloaded',timeout:20000});
    ck('svc_http200',r1.status()===200,{status:r1.status()});
    const cta=page.locator('a[href*="tn_service_context=server-scoping"]').first();
    ck('svc_cta_present',await cta.count()>0);
    await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}).catch(()=>null),cta.click()]);
    ck('svc_cta_lands_form',page.url().includes('tn_service_context=server-scoping'),{url:page.url().slice(0,120)});
    await page.addStyleTag({content:'html{scroll-behavior:auto !important} *{scroll-behavior:auto !important}'});
    await page.locator('form.tn-service-request select[name="tn_service_context"]').first().selectOption('server-scoping',{timeout:10000});
    await page.locator('form.tn-service-request input[name="tn_name"]').first().fill('آزمون شبانه',{timeout:10000});
    await page.locator('form.tn-service-request input[name="tn_email"]').first().fill('night-test@example.invalid',{timeout:10000});
    await page.locator('form.tn-service-request textarea[name="tn_message"]').first().fill('آزمون LOCAL_STAGING؛ حذف پس از آزمون.',{timeout:10000});
    await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}).catch(()=>null),page.click('form.tn-service-request button[type="submit"]')]);
    ck('svc_submit_302',/tn_ticket=sent/.test(page.url()),{url:page.url().slice(0,140)});
    await page.waitForSelector('.tn-service-receipt',{timeout:10000});
    const svcReceipt=await page.evaluate(()=>document.querySelector('.tn-service-receipt').innerText);
    const svcTN=svcReceipt.match(/TN-(\d+)/);
    ck('svc_receipt_visible',/درخواست شما ثبت شد/.test(svcReceipt),{tracking:svcTN?('TN-'+svcTN[1]):null});
    await page.screenshot({path:'night-svc-1440.png',fullPage:false});
    await ctx.close();
    /* --- B2B quote journey (desktop) --- */
    ctx=await browser.newContext({viewport:{width:1440,height:900},locale:'fa'});
    page=await ctx.newPage();
    await page.goto(BASE+'/b2b/',{waitUntil:'domcontentloaded',timeout:20000});
    await page.addStyleTag({content:'html{scroll-behavior:auto !important} *{scroll-behavior:auto !important}'});
    const pid=await page.evaluate(()=>{const s=document.querySelector('form.tn-quote-form select[name="tn_item_product[]"]');const o=s&&s.querySelector('option:nth-child(2)');return o?o.value:null;});
    await page.locator('form.tn-quote-form input[name="tn_company"]').first().fill('آزمون شبانه',{timeout:10000});
    await page.locator('form.tn-quote-form input[name="tn_contact"]').first().fill('رابط آزمون',{timeout:10000});
    await page.locator('form.tn-quote-form input[name="tn_phone"]').first().fill('02100000000',{timeout:10000});
    await page.locator('form.tn-quote-form input[name="tn_email"]').first().fill('night-test@example.invalid',{timeout:10000});
    await page.locator('form.tn-quote-form select[name="tn_item_product[]"]').first().selectOption(pid,{timeout:10000});
    await page.locator('form.tn-quote-form input[name="tn_item_qty[]"]').first().fill('2',{timeout:10000});
    await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}).catch(()=>null),page.click('form.tn-quote-form button[type="submit"]')]);
    ck('b2b_submit_302',/tn_quote=sent/.test(page.url()),{url:page.url().slice(0,140)});
    await page.screenshot({path:'night-b2b-1440.png',fullPage:false});
    await ctx.close();
    /* --- Support journey (mobile 375 + RTL) --- */
    ctx=await browser.newContext({viewport:{width:375,height:667},locale:'fa'});
    page=await ctx.newPage();
    await page.goto(BASE+'/support/',{waitUntil:'domcontentloaded',timeout:20000});
    await page.addStyleTag({content:'html{scroll-behavior:auto !important} *{scroll-behavior:auto !important}'});
    await page.locator('form.tn-ticket-form input[name="tn_subject"]').first().fill('آزمون شبانه',{timeout:10000});
    await page.locator('form.tn-ticket-form input[name="tn_name"]').first().fill('آزمون',{timeout:10000});
    await page.locator('form.tn-ticket-form input[name="tn_email"]').first().fill('night-test@example.invalid',{timeout:10000});
    await page.locator('form.tn-ticket-form textarea[name="tn_message"]').first().fill('آزمون LOCAL_STAGING؛ حذف پس از آزمون.',{timeout:10000});
    await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}).catch(()=>null),page.click('form.tn-ticket-form button[type="submit"]')]);
    ck('support_submit_302',/tn_ticket=sent/.test(page.url()),{url:page.url().slice(0,140)});
    const ov=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
    ck('support_mobile375_no_overflow',ov<=0,{px:ov});
    await page.screenshot({path:'night-support-375.png',fullPage:false});
    await ctx.close();
    /* --- mobile 320 render check --- */
    ctx=await browser.newContext({viewport:{width:320,height:568},locale:'fa'});
    page=await ctx.newPage();
    await page.goto(BASE+'/services/network-setup-tehran/',{waitUntil:'domcontentloaded',timeout:20000});
    const ov320=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
    ck('svc_mobile320_no_overflow',ov320<=0,{px:ov320});
    await ctx.close();
    /* --- no-JS: form POST works without JavaScript --- */
    ctx=await browser.newContext({viewport:{width:375,height:667},locale:'fa',javaScriptEnabled:false});
    page=await ctx.newPage();
    await page.goto(BASE+'/b2b/',{waitUntil:'load',timeout:20000});
    const nojsForm=await page.evaluate(()=>{const f=document.querySelector('form.tn-quote-form');return{present:!!f,method:f?f.getAttribute('method'):null,submit:!!(f&&f.querySelector('button[type="submit"]'))};});
    ck('b2b_nojs_form_html_post',nojsForm.present&&nojsForm.method==='post'&&nojsForm.submit,nojsForm);
    await ctx.close();
    /* --- dark mode toggle --- */
    ctx=await browser.newContext({viewport:{width:1440,height:900},locale:'fa'});
    page=await ctx.newPage();
    await page.goto(BASE+'/b2b/',{waitUntil:'domcontentloaded',timeout:20000});
    const tgl=await page.$('.tn-theme-toggle');
    if(tgl){await tgl.click();await page.waitForTimeout(300);
      const theme=await page.evaluate(()=>document.documentElement.dataset.theme);
      ck('dark_mode_toggle',theme==='dark',{theme});
    } else ck('dark_toggle_found',false);
    await ctx.close();
  }finally{
    if(ctx)try{await ctx.close();}catch(e){}
    try{await browser.close();}catch(e){}
  }
  out.status=out.failures?'FAIL':'PASS';
  fs.writeFileSync('local-staging-result.json',JSON.stringify(out,null,1));
  console.log('LOCAL STAGING RESULT:',out.status,'| checks:',out.checks.length,'failures:',out.failures);
  for(const c of out.checks.filter(c=>!c.pass))console.log('  FAIL:',c.name,JSON.stringify(c.detail).slice(0,160));
  process.exitCode=out.failures?1:0;
})().catch(e=>{out.status='ERROR';out.error=e.message.split('\n')[0];fs.writeFileSync('local-staging-result.json',JSON.stringify(out,null,1));console.log('ERROR:',out.error);process.exitCode=1;});
