'use strict';
// Synthetic submissions are permitted ONLY in independently verified isolated native staging.
const assert = require('node:assert/strict'); const fs = require('node:fs'); const path = require('node:path');
const { chromium } = require('playwright');
const origin = process.env.TN_NATIVE_PREVIEW_URL; const marker = process.env.TN_CP63_MARKER;
assert.equal(process.env.TN_NATIVE_PREVIEW_ISOLATED, '1');
assert.ok(/^http:\/\/(localhost|127\.0\.0\.1):18085$/.test(origin)); assert.match(marker, /^TNCP63[A-F0-9]{20}$/);
const email = `${marker.toLowerCase()}@example.invalid`; const out = path.resolve(process.argv[2]);
const checks=[]; function check(label,value){assert.ok(value,label);checks.push(label);}
(async()=>{
 fs.mkdirSync(out,{recursive:true}); const browser=await chromium.launch({channel:'msedge',headless:true,args:['--host-resolver-rules=MAP localhost 127.0.0.1']});
 const errors=[]; const refs=[];
 async function context(js=true,width=1440){const c=await browser.newContext({javaScriptEnabled:js,viewport:{width,height:900}});await c.route('**/*',r=>r.request().url().startsWith(origin+'/')?r.continue():r.abort());return c;}
 async function fill(form,service,suffix){await form.locator('[name=tn_service_context]').selectOption(service);await form.locator('[name=tn_name]').fill('آزمون خصوصی');await form.locator('[name=tn_email]').fill(email);await form.locator('[name=tn_message]').fill(`${marker}-${suffix} درخواست مصنوعی؛ صرفاً آزمون نسخهٔ ایزوله.`);}
 try{
  const c=await context();const page=await c.newPage();page.on('pageerror',e=>errors.push(e.message));
  for(const route of ['/','/services/']){
   const response=await page.goto(origin+route,{waitUntil:'networkidle'});
   check(route+' native HTTP200',response.status()===200);check(route+' one H1',await page.locator('main h1').count()===1);
   check(route+' intentional noindex',((await page.locator('meta[name=robots]').getAttribute('content'))||'').includes('noindex'));
   check(route+' exactly one short service form',await page.locator('[data-tn-service-request]').count()===1);
   if(route==='/')for(const p of ['/learn/','/lab/','/services/','/shop/'])check('Homepage retains '+p,await page.locator(`main a[href="${p}"]`).count()>0);
   else{
    check('Service catalog has room for readable enterprise cards',await page.locator('main .entry-content').evaluate(e=>e.getBoundingClientRect().width>900));
    for(const id of ['active-network','managed-support','server-planning','security-planning','monitoring-planning','wifi-planning','branch-planning'])check('Browsable category '+id,await page.locator(`#${id}`).count()===1&&await page.locator(`main a[href="#${id}"]`).count()===1);
    for(const slug of ['network-tehran','network-support-tehran','network-setup-tehran','mikrotik-tehran','remote-support','voice-network-readiness'])check('Retains service owner '+slug,await page.locator(`main a[href="/services/${slug}/"]`).count()>0);
    check('Specialist VoIP remains contextual MyTel link',await page.locator('main a[href="https://mytel.one/services/"]').count()>0);
    check('No unsupported specialist availability promise',(await page.locator('main').innerText()).includes('به معنی تأیید ظرفیت اجرا'));
   }
   await page.screenshot({path:path.join(out,(route==='/'?'home':'services')+'-1440.png'),fullPage:true});
   if(route==='/services/')await page.locator('.tn-svc-grid').first().screenshot({path:path.join(out,'service-cards-1440.png')});
   await page.setViewportSize({width:375,height:812});check(route+' mobile RTL and no overflow',await page.evaluate(()=>document.documentElement.dir==='rtl'&&document.documentElement.scrollWidth<=innerWidth));
   await page.screenshot({path:path.join(out,(route==='/'?'home':'services')+'-375.png'),fullPage:true});await page.setViewportSize({width:1440,height:900});
  }
  await page.goto(origin+'/services/?tn_service_context=mikrotik#service-request',{waitUntil:'networkidle'});const form=page.locator('[data-tn-service-request]');
  check('CTA carries approved service into the form',await form.locator('[name=tn_service_context]').inputValue()==='mikrotik');
  check('Nonce belongs to submitted FormData',await form.evaluate(f=>!!new FormData(f).get('_wpnonce')&&f.querySelector('[name=_wpnonce]').form===f));
  await fill(form,'mikrotik','desktop');await form.locator('details').evaluate(e=>e.open=true);await form.locator('[name=tn_company]').fill(marker);
  await Promise.all([page.waitForURL('**/support/?tn_ticket=sent&tn_service_receipt=*'),form.locator('[type=submit]').click()]);
  const receiptURL=page.url();const notice=page.locator('.tn-service-receipt');
  const ref=(await notice.innerText()).match(/TN-\d+/)?.[0];check('Saved request yields actual reference and open status',!!ref&&(await notice.innerText()).includes('در انتظار بررسی'));refs.push(ref);
  check('Receipt reveals no contact or conversation',!(await notice.innerText()).includes(email)&&!(await notice.innerText()).includes(marker));
  const receiptResponse=await page.goto(receiptURL,{waitUntil:'networkidle'});
  check('Receipt prevents browser/shared caching',/no-cache|no-store/.test(receiptResponse.headers()['cache-control']||''));
  check('Receipt is not forwarded as a referrer',receiptResponse.headers()['referrer-policy']==='no-referrer');
  check('Reload keeps same reference without another POST',(await notice.innerText()).includes(ref));
  await notice.screenshot({path:path.join(out,'service-receipt.png')});
  await page.goto(origin+'/support/?tn_ticket=sent&tn_service_receipt=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',{waitUntil:'networkidle'});
  check('Guessed receipt has no success or reference',!(await notice.innerText()).includes('TN-')&&!(await notice.innerText()).includes('درخواست شما ثبت شد'));
  await page.goto(origin+'/services/',{waitUntil:'networkidle'});const nonce=await form.locator('[name=_wpnonce]').inputValue();
  const base={action:'tn_ticket_submit',_wpnonce:nonce,tn_request_kind:'service',tn_service_context:'network-support',tn_name:'آزمون خصوصی',tn_email:email,tn_message:marker+'-rejected درخواست مصنوعی برای رد شدن.'};
  const post=data=>page.request.post(origin+'/wp-admin/admin-post.php',{form:data,maxRedirects:0});
  check('Native invalid nonce rejected',(await post({...base,_wpnonce:'invalid-synthetic'})).status()===403);
  check('Honeypot rejected before creating a record',(await post({...base,tn_hp:'robot'})).status()===400);
  const array={...base};delete array.tn_service_context;array['tn_service_context[]']='network-support';
  check('Array service input rejected server-side',(await post(array)).status()===400);
  check('Malformed email rejected server-side',(await post({...base,tn_email:'not-email'})).status()===400);
  check('Short problem rejected server-side',(await post({...base,tn_message:'کم'})).status()===400);
  const nojs=await context(false,375);const np=await nojs.newPage();const nojsRequests=[];
  np.on('response',r=>{if(r.request().method()==='POST')nojsRequests.push({url:r.url(),status:r.status()});});
  np.on('request',r=>{if(r.method()==='POST')nojsRequests.push({request:r.url(),method:'POST'});});
  np.on('console',m=>nojsRequests.push({console:m.type(),text:m.text()}));np.on('requestfailed',r=>nojsRequests.push({failed:r.url(),error:r.failure()}));
  await np.goto(origin+'/',{waitUntil:'networkidle'});const nf=np.locator('[data-tn-service-request]');
  await fill(nf,'remote-support','nojs');
  check('Focused no-JS form uses stable immediate scrolling',await np.evaluate(()=>getComputedStyle(document.documentElement).scrollBehavior==='auto'));
  const validity=await nf.evaluate(f=>({valid:f.checkValidity(),invalid:[...f.elements].filter(e=>e.willValidate&&!e.validity.valid).map(e=>({name:e.name,message:e.validationMessage}))}));
  fs.writeFileSync(path.join(out,'nojs-before-private.json'),JSON.stringify(validity,null,2));check('No-JS form passes native client validation',validity.valid);
  try{await Promise.all([np.waitForURL('**/support/?tn_ticket=sent&tn_service_receipt=*'),nf.locator('[type=submit]').click()]);}
  catch(error){fs.writeFileSync(path.join(out,'nojs-failure-private.json'),JSON.stringify({url:np.url(),posts:nojsRequests,form:await nf.evaluate(f=>({action:f.getAttribute('action'),method:f.method,valid:f.checkValidity(),elements:[...f.elements].map(e=>({name:e.name,type:e.type,length:e.value?.length,required:e.required,valid:e.validity?.valid,message:e.validationMessage,associated:e.form===f,disabled:e.disabled}))})),body:await np.locator('body').innerText()},null,2));await np.screenshot({path:path.join(out,'nojs-failure-private.png'),fullPage:true});throw error;}
  const second=(await np.locator('.tn-service-receipt').innerText()).match(/TN-\d+/)?.[0];refs.push(second);
  check('Mobile no-JS request actually saved with distinct reference',!!second&&second!==ref);
  await np.locator('.tn-service-receipt').screenshot({path:path.join(out,'nojs-receipt-375.png')});await nojs.close();
  check('Existing per-IP ticket throttle rejects excess request',(await post(base)).status()===429);
  const unauthorized=await page.request.post(origin+'/wp-admin/admin-post.php',{form:{action:'tn_ticket_reply',post_id:ref.slice(3),tn_reply:'unauthorized synthetic'}});
  check('Anonymous reply cannot access staff operations',unauthorized.status()===400||unauthorized.status()===403||unauthorized.url().includes('wp-login.php'));
  const staff=await context();const sp=await staff.newPage();await sp.goto(origin+'/wp-login.php',{waitUntil:'networkidle'});
  await sp.locator('#user_login').fill(process.env.TN_CP63_STAFF_USER);await sp.locator('#user_pass').fill(process.env.TN_CP63_STAFF_PASSWORD);
  await Promise.all([sp.waitForURL('**/wp-admin/**'),sp.locator('#wp-submit').click()]);
  await sp.goto(origin+'/wp-admin/admin.php?page=tn-store-tickets',{waitUntil:'networkidle'});
  check('Authorized staff see the same two canonical ticket references',(await sp.locator('body').innerText()).includes(ref)&&(await sp.locator('body').innerText()).includes(second));
  const own=sp.locator('details.tn-ticket').filter({hasText:ref});check('Staff see persisted service and optional business context',await own.count()===1&&(await own.innerText()).includes('MikroTik')&&(await own.innerText()).includes(marker));
  await own.screenshot({path:path.join(out,'staff-synthetic-ticket.png')});
  check('No uncaught customer-facing JavaScript errors',errors.length===0);
  fs.writeFileSync(path.join(out,'browser.json'),JSON.stringify({status:'PASS',observed_utc:new Date().toISOString(),checks,passed:checks.length,refs,scope:'Isolated native WordPress only; two synthetic saved tickets, real staff login, no customer notification or payment'},null,2)+'\n');
  console.log(JSON.stringify({status:'PASS',checks:checks.length,synthetic_requests:2,staff_visibility:true}));await staff.close();await c.close();
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
