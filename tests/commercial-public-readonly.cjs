'use strict';
// Production verification MUST NOT submit forms or use customer/staff credentials.
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');const{chromium}=require('playwright');
const out=path.resolve(process.argv[2]);const origin='https://tehnet.ir';const checks=[];let blockedWrites=0;
function check(s,v){assert.ok(v,s);checks.push(s);}
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({channel:'msedge',headless:true});
try{
 for(const width of [1440,375])for(const js of [true,false]){
  const context=await browser.newContext({viewport:{width,height:900},javaScriptEnabled:js,reducedMotion:'reduce'});
  await context.route('**/*',r=>{if(!['GET','HEAD'].includes(r.request().method())){blockedWrites++;return r.abort();}return new URL(r.request().url()).origin===origin?r.continue():r.abort();});
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const route of ['/','/services/']){
   const response=await page.goto(origin+route,{waitUntil:'domcontentloaded'});await page.locator('[data-tn-service-request]').waitFor();
   check(`${route} ${width} js=${js} HTTPS200`,response.status()===200);
   check(`${route} ${width} js=${js} one H1`,await page.locator('main h1').count()===1);
   check(`${route} ${width} js=${js} noindex`,(await page.locator('meta[name=robots]').getAttribute('content')).includes('noindex'));
   check(`${route} ${width} js=${js} RTL/no overflow`,await page.evaluate(()=>document.documentElement.dir==='rtl'&&document.documentElement.scrollWidth<=innerWidth));
   const form=page.locator('[data-tn-service-request]');check(`${route} ${width} js=${js} one canonical intake`,await form.count()===1&&await form.locator('[name=action]').inputValue()==='tn_ticket_submit'&&!!await form.locator('[name=_wpnonce]').inputValue());
   check(`${route} ${width} js=${js} four required inputs`,await form.locator('[required]').count()===4);
   check(`${route} ${width} js=${js} rejects empty form locally`,!(await form.evaluate(f=>f.checkValidity())));
   if(route==='/')for(const p of ['/learn/','/lab/','/services/','/shop/'])check(`Home ${width} js=${js} preserves ${p}`,await page.locator(`main a[href="${p}"]`).count()>0);
   else{
    for(const id of ['active-network','managed-support','server-planning','security-planning','monitoring-planning','wifi-planning','branch-planning'])check(`Catalog ${width} js=${js} category ${id}`,await page.locator(`#${id}`).count()===1&&await page.locator(`main a[href="#${id}"]`).count()===1);
    for(const slug of ['network-tehran','network-support-tehran','network-setup-tehran','mikrotik-tehran','remote-support','voice-network-readiness'])check(`Catalog ${width} js=${js} owner ${slug}`,await page.locator(`main a[href="/services/${slug}/"]`).count()>0);
    check(`Catalog ${width} js=${js} MyTel referral`,await page.locator('main a[href="https://mytel.one/services/"]').count()>0);
    if(width===1440)check('Desktop catalog readable width',await page.locator('main .entry-content').evaluate(e=>e.getBoundingClientRect().width>900));
   }
   if(js){await page.evaluate(()=>{document.activeElement?.blur();scrollTo(0,0);});await page.screenshot({path:path.join(out,(route==='/'?'after-home':'after-services')+'-'+width+'.png'),fullPage:true});if(route==='/services/'&&width===1440)await page.locator('.tn-svc-grid').first().screenshot({path:path.join(out,'after-service-cards-1440.png')});}
  }
  await page.goto(origin+'/services/?tn_service_context=mikrotik#service-request',{waitUntil:'domcontentloaded'});
  check(`CTA ${width} js=${js} selects requested service`,await page.locator('[data-tn-service-request] [name=tn_service_context]').inputValue()==='mikrotik');
  check(`Customer pages ${width} js=${js} no uncaught script error`,errors.length===0);await context.close();
 }
 check('No production write request attempted',blockedWrites===0);
 const receipt={status:'PASS',observed_utc:new Date().toISOString(),checks,passed:checks.length,production_submissions:0,credentials_used:0,tls_validation:true,scope:'Public desktop1440/mobile375 with JS/no-JS; same-origin assets; no form submit, notification or payment; actual persistence was verified separately in isolated staging'};
 fs.writeFileSync(path.join(out,'browser.json'),JSON.stringify(receipt,null,2));console.log(JSON.stringify({status:'PASS',passed:checks.length,production_submissions:0}));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
