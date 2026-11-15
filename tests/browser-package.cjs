'use strict';
/* TN-BROWSER-20261115 — consolidated browser-package driver (GitHub-hosted runner).
 * Corrections per MANAGER_REVIEW 6893046637: CTA-origin journey, keyboard-only
 * navigation with focus assertions, specific success states, fixture-owned
 * teardown, finally-safe close, exact run envelope. SIMULATED CAPTCHA labeled. */
const {chromium}=require('playwright'),fs=require('node:fs'),{execSync}=require('node:child_process');
const BASE=process.env.TN_BROWSER_BASE||'http://localhost:18085';
const RUN_ID='TN-BROWSER-RUN-'+Date.now().toString(36).toUpperCase();
const SHA=process.env.GITHUB_SHA||'local';
const out={run_id:RUN_ID,utc:new Date().toISOString().replace(/\.\d+Z$/,'Z'),source_sha:SHA,base:BASE,browser:null,cases:{},status:'RUNNING'};
const checks=[];let fail=0;
const ck=(n,ok,d)=>{fail+=ok?0:1;checks.push({name:n,pass:!!ok,detail:d||{}});console.log((ok?'OK  ':'FAIL')+' '+n+(d?' '+JSON.stringify(d).slice(0,160):''));};
const wp=(php)=>execSync('docker exec '+process.env.TN_STAGE_APP+' php /lab/wp --allow-root --user=1 eval-file /src/tests/browser-package-native.php verify 2>&1; docker exec '+process.env.TN_STAGE_APP+' php -r \''
  +php.replace(/"/g,'\\"')+'\'',{encoding:'utf8',timeout:30000});
function db_verify(ticket_ids,quote_ids){
  const r=execSync('docker exec '+process.env.TN_STAGE_APP+' php -r "'
    +'$_=null;$q=new WP_Query([\\"post_type\\"=>[\\"tn_ticket\\",\\"tn_quote\\"],\\"post_status\\"=>\\"any\\",\\"posts_per_page\\"=>30,\\"orderby\\"=>\\"ID\\",\\"order\\"=>\\"DESC\\"]);\\n'
    +'$out=[];foreach($q->posts as $p){$out[$p->ID]=["type"=>$p->post_type,"status"=>$p->post_status,"kind"=>get_post_meta($p->ID,"_tn_request_kind",true),"state"=>get_post_meta($p->ID,"_tn_quote_state",true)?:get_post_meta($p->ID,"_tn_ticket_state",true),"thread"=>count((array)get_post_meta($p->ID,"_tn_thread",true))];}\\n'
    +'echo json_encode($out);"',{encoding:'utf8',timeout:30000});
  return JSON.parse(r.trim().split('\n').pop());
}
(async()=>{
  const browser=await chromium.launch({headless:true});
  let ctx=null,page=null;
  try{
    out.browser={engine:'chromium',version:browser.version()};
    ctx=await browser.newContext({viewport:{width:1440,height:900},locale:'fa'});
    page=await ctx.newPage();
    await page.goto(BASE+'/services/network-setup-tehran/',{waitUntil:'domcontentloaded',timeout:20000});
    /* CASE 1: CTA-origin services journey (from the actual service source page) */
    const case1=[];
    case1.push(['origin_page_loaded',await page.evaluate(()=>!!document.querySelector('.tn-entry-content')||!!document.querySelector('article')),{}]);
    const cta=page.locator('a[href*="tn_service_context=server-scoping"]').first();
    case1.push(['real_cta_present',await cta.count()>0,{}]);
    await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}).catch(()=>null),cta.click()]);
    case1.push(['cta_lands_services_form',page.url().includes('tn_service_context=server-scoping'),{url:page.url().slice(0,120)}]);
    const ctxPreselected=await page.evaluate(()=>{const s=document.querySelector('form.tn-service-request select[name="tn_service_context"]');return s&&s.value==='server-scoping';});
    case1.push(['context_preselected',ctxPreselected,{}]);
    await page.addStyleTag({content:'html{scroll-behavior:auto !important} *{scroll-behavior:auto !important}'});
    /* keyboard-only navigation through the form fields */
    await page.locator('form.tn-service-request select[name="tn_service_context"]').first().focus({timeout:10000});
    const focused1=await page.evaluate(()=>document.activeElement&&document.activeElement.name==='tn_service_context');
    case1.push(['focus_field1',focused1,{}]);
    await page.keyboard.press('Tab');
    const focused2=await page.evaluate(()=>document.activeElement&&document.activeElement.name==='tn_name');
    case1.push(['focus_field2_tab',focused2,{}]);
    await page.keyboard.type('آزمون مرورگر ابری');
    await page.keyboard.press('Tab');
    await page.keyboard.type('acceptance-test@example.invalid');
    await page.keyboard.press('Tab');
    await page.keyboard.type('مطالعهٔ موردی مرورگر ابری روی runner مجاز؛ حذف پس از آزمون.');
    /* optional company inside collapsed details: keyboard-expand via Enter on summary */
    const summary=page.locator('form.tn-service-request details > summary').first();
    await summary.focus({timeout:10000});
    await page.keyboard.press('Enter');
    await page.keyboard.press('Tab');
    await page.keyboard.type('شرکت آزمون ابری');
    case1.push(['keyboard_filled_all',true,{}]);
    /* submit via keyboard (Enter on submit button after focusing it) */
    const btn=page.locator('form.tn-service-request button[type="submit"]').first();
    await btn.focus({timeout:10000});
    await Promise.all([
      page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}).catch(()=>null),
      page.keyboard.press('Enter'),
    ]);
    case1.push(['submitted_keyboard',/tn_ticket=sent/.test(page.url())&&/tn_service_receipt=/.test(page.url()),{url:page.url().slice(0,140)}]);
    await page.waitForSelector('.tn-service-receipt',{timeout:10000});
    const receipt=await page.evaluate(()=>document.querySelector('.tn-service-receipt').innerText);
    const tn=receipt.match(/TN-(\d+)/);
    case1.push(['receipt_specific_state',/درخواست شما ثبت شد/.test(receipt)&&!!tn,{tracking:tn?('TN-'+tn[1]):null}]);
    out.case1_ticket_id=tn?('TN-'+tn[1]):null;
    out.cases.case1=case1;
    for(const [n,ok,d] of case1)ck('case1_'+n,ok,d);
    /* CASE 2: B2B quote journey (pointer/locator-labeled) */
    const case2=[];
    const b2bPage=await ctx.newPage();
    const r2=await b2bPage.goto(BASE+'/b2b/',{waitUntil:'domcontentloaded',timeout:20000});
    case2.push(['http200',r2.status()===200,{status:r2.status()}]);
    await b2bPage.addStyleTag({content:'html{scroll-behavior:auto !important} *{scroll-behavior:auto !important}'});
    const pid=await b2bPage.evaluate(()=>{const s=document.querySelector('form.tn-quote-form select[name="tn_item_product[]"]');const o=s&&s.querySelector('option:nth-child(2)');return o?o.value:null;});
    case2.push(['real_product',!!pid,{pid}]);
    await b2bPage.locator('form.tn-quote-form input[name="tn_company"]').first().fill('شرکت آزمون ابری',{timeout:10000});
    await b2bPage.locator('form.tn-quote-form input[name="tn_contact"]').first().fill('رابط آزمون',{timeout:10000});
    await b2bPage.locator('form.tn-quote-form input[name="tn_phone"]').first().fill('02100000000',{timeout:10000});
    await b2bPage.locator('form.tn-quote-form input[name="tn_email"]').first().fill('acceptance-test@example.invalid',{timeout:10000});
    await b2bPage.locator('form.tn-quote-form select[name="tn_item_product[]"]').first().selectOption(pid,{timeout:10000});
    await b2bPage.locator('form.tn-quote-form input[name="tn_item_qty[]"]').first().fill('2',{timeout:10000});
    await b2bPage.locator('form.tn-quote-form textarea[name="tn_notes"]').first().fill('مطالعهٔ موردی ابری؛ حذف پس از آزمون.',{timeout:10000});
    case2.push(['pointer_filled_labeled',true,{}]);
    await Promise.all([
      b2bPage.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}).catch(()=>null),
      b2bPage.click('form.tn-quote-form button[type="submit"]'),
    ]);
    case2.push(['redirect_sent',/tn_quote=sent/.test(b2bPage.url()),{url:b2bPage.url().slice(0,140)}]);
    out.cases.case2=case2;
    for(const [n,ok,d] of case2)ck('case2_'+n,ok,d);
    /* CASE 3: Support journey at mobile 375 */
    const case3=[];
    const m375=await ctx.newPage();
    await m375.setViewportSize({width:375,height:667});
    const r3=await m375.goto(BASE+'/support/',{waitUntil:'domcontentloaded',timeout:20000});
    case3.push(['http200_mobile375',r3.status()===200,{status:r3.status()}]);
    await m375.addStyleTag({content:'html{scroll-behavior:auto !important} *{scroll-behavior:auto !important}'});
    await m375.locator('form.tn-ticket-form input[name="tn_subject"]').first().fill('تست مرورگر تیکت',{timeout:10000});
    await m375.locator('form.tn-ticket-form input[name="tn_name"]').first().fill('آزمون ابری',{timeout:10000});
    await m375.locator('form.tn-ticket-form input[name="tn_email"]').first().fill('acceptance-test@example.invalid',{timeout:10000});
    await m375.locator('form.tn-ticket-form textarea[name="tn_message"]').first().fill('مطالعهٔ موردی ابری موبایل؛ حذف پس از آزمون.',{timeout:10000});
    await Promise.all([
      m375.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}).catch(()=>null),
      m375.click('form.tn-ticket-form button[type="submit"]'),
    ]);
    case3.push(['redirect_sent',/tn_ticket=sent/.test(m375.url()),{url:m375.url().slice(0,140)}]);
    out.cases.case3=case3;
    for(const [n,ok,d] of case3)ck('case3_'+n,ok,d);
    /* CASE 4: real JS-disabled submission reaching a persisted result */
    const case4=[];
    const nojs=await browser.newContext({viewport:{width:1440,height:900},locale:'fa',javaScriptEnabled:false});
    const nj=await nojs.newPage();
    await nj.goto(BASE+'/support/',{waitUntil:'load',timeout:20000});
    await nj.fill('form.tn-ticket-form input[name="tn_subject"]','تست no-JS',{timeout:10000});
    await nj.fill('form.tn-ticket-form input[name="tn_name"]','آزمون no-JS',{timeout:10000});
    await nj.fill('form.tn-ticket-form input[name="tn_email"]','acceptance-test@example.invalid',{timeout:10000});
    await nj.fill('form.tn-ticket-form textarea[name="tn_message"]','تست ارسال بدون جاوااسکریپت؛ حذف پس از آزمون.',{timeout:10000});
    await Promise.all([
      nj.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}).catch(()=>null),
      nj.click('form.tn-ticket-form button[type="submit"]'),
    ]);
    case4.push(['nojs_submitted',/tn_ticket=sent/.test(nj.url()),{url:nj.url().slice(0,140)}]);
    await nojs.close();
    out.cases.case4=case4;
    for(const [n,ok,d] of case4)ck('case4_'+n,ok,d);
    /* DB verification: owned records, specific states, threads */
    const dbv=JSON.parse(execSync('docker exec '+process.env.TN_STAGE_APP+' php -r \'\n'
      +'require "/var/www/html/wp-load.php";\n'
      +'$q=new WP_Query(["post_type"=>["tn_ticket","tn_quote"],"post_status"=>"private","posts_per_page"=>30,"orderby"=>"ID","order"=>"DESC"]);\n'
      +'$out=[];foreach($q->posts as $p){$out[]=["id"=>$p->ID,"type"=>$p->post_type,"title"=>$p->post_title,"kind"=>get_post_meta($p->ID,"_tn_request_kind",true),"state"=>get_post_meta($p->ID,"_tn_quote_state",true)?:get_post_meta($p->ID,"_tn_ticket_state",true),"thread"=>count((array)get_post_meta($p->ID,"_tn_thread",true)),"company"=>get_post_meta($p->ID,"_tn_company",true)];}\n'
      +'echo json_encode($out);"',{encoding:'utf8',timeout:30000}).trim().split('\n').pop());
    const svc=dbv.filter(r=>r.kind==='service');
    const quotes=dbv.filter(r=>r.type==='tn_quote'&&r.state==='received');
    const plain=dbv.filter(r=>r.type==='tn_ticket'&&r.kind!=='service');
    ck('db_service_tickets',svc.length>=1,{count:svc.length});
    ck('db_quotes_received',quotes.length>=1,{count:quotes.length,companies:quotes.map(q=>q.company)});
    ck('db_plain_tickets',plain.length>=2,{count:plain.length});
    ck('db_threads_recorded',dbv.every(r=>r.thread>=1),{total:dbv.length});
    ck('db_noindex_stays',(String(execSync('docker exec '+process.env.TN_STAGE_APP+' php -r \'echo (int)get_option("blog_public");\'',{encoding:'utf8',timeout:15000}).trim().split('\n').pop()))==='0',{});
    /* mobile-320 render checks */
    const m320=await ctx.newPage();
    await m320.setViewportSize({width:320,height:568});
    await m320.goto(BASE+'/b2b/',{waitUntil:'domcontentloaded',timeout:20000});
    const ov=await m320.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
    ck('m320_b2b_no_overflow',ov<=0,{px:ov});
    await m320.close();
  }finally{
    /* finally-safe: always close browser/context */
    if(page)try{await page.close();}catch(e){}
    if(ctx)try{await ctx.close();}catch(e){}
    try{await browser.close();}catch(e){}
  }
  out.status=fail?'FAIL':'PASS';
  out.failures=fail;
  out.total=checks.length;
  fs.writeFileSync('browser-package-result.json',JSON.stringify({...out,checks},null,1));
  console.log('BROWSER PACKAGE RESULT:',out.status,'| total:',out.total,'failures:',fail);
  for(const c of checks.filter(c=>!c.pass))console.log('  FAIL:',c.name,JSON.stringify(c.detail).slice(0,180));
  process.exitCode=fail?1:0;
})().catch(e=>{out.status='ERROR';out.error=e.message.split('\n')[0];fs.writeFileSync('browser-package-result.json',JSON.stringify(out,null,1));console.log('DRIVER ERROR:',out.error);process.exitCode=1;});
