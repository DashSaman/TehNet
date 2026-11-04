"use strict";
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const origin=process.env.TN_SERVICE_ORIGIN,out=path.resolve(process.argv[2]),before=process.env.TN_SERVICE_BEFORE==='1';
assert.ok(['http://localhost:18085','https://tehnet.ir'].includes(origin));const checks=[];let writes=0,activePage;
const check=(value,label)=>{assert.ok(value,label);checks.push(label);};
const items=[{card:'server-planning',module:'server-project-brief',label:'دامنه و معیار تحویل سرور و مجازی‌سازی ←',context:'server-scoping',cta:'درخواست بررسی سرور و مجازی‌سازی'},{card:'branch-planning',module:'branch-connectivity-brief',label:'دامنه و معیار تحویل ارتباط شعب ←',context:'wifi-branch-scoping',cta:'درخواست طراحی ارتباط شعب'}];
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({channel:'msedge',headless:true,args:['--host-resolver-rules=MAP localhost 127.0.0.1']});
try{
 for(const width of [1440,375,320])for(const theme of width===320?['light']:['light','dark']){
  const ctx=await browser.newContext({viewport:{width,height:950},colorScheme:theme,javaScriptEnabled:width!==320,reducedMotion:'reduce'});
  await ctx.route('**/*',r=>{if(!['GET','HEAD'].includes(r.request().method())){writes++;return r.abort();}return r.request().url().startsWith(origin+'/')?r.continue():r.abort();});
  await ctx.addInitScript(t=>localStorage.setItem('tn-theme',t),theme);const page=await ctx.newPage();activePage=page;const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const response=await page.goto(origin+'/services/',{waitUntil:'networkidle'}),label=width+'/'+theme;
  check(response.status()===200,label+' catalog HTTP200');
  check(await page.locator('main h1').count()===1&&await page.locator('link[rel="canonical"]').getAttribute('href')===origin+'/services/',label+' existing owner and H1');
  check((await page.locator('meta[name="robots"]').getAttribute('content')).includes('noindex'),label+' existing noindex');
  check(await page.evaluate(()=>document.documentElement.dir==='rtl'&&document.documentElement.scrollWidth<=innerWidth),label+' RTL without horizontal overflow');
  check(await page.locator('main a[href="https://mytel.one/services/"]').count()>0,label+' contextual MyTel referral');
  check(await page.locator('.tn-service-request').count()===1,label+' one existing request form');
  for(const item of items){
   const card=page.locator('.tn-svc-card').filter({has:page.locator('#'+item.card)}),link=card.getByRole('link',{name:item.label,exact:true});
   check(await card.count()===1,label+' original card '+item.card);
   if(before){check(await link.count()===0,label+' gap reproduced '+item.card);}
   else{
    check(await link.count()===1&&await link.getAttribute('href')==='/services/network-setup-tehran/#'+item.module,label+' descriptive detail link '+item.card);
    check(await card.locator('a[href="/services/?tn_service_context='+item.context+'#service-request"]').count()===1,label+' direct request retained '+item.card);
   }
   if(width!==320){await card.scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,(before?'before-':'after-')+item.card+'-'+width+'-'+theme+'.png')});}
   if(before)continue;
   await Promise.all([page.waitForURL(origin+'/services/network-setup-tehran/#'+item.module,{waitUntil:'domcontentloaded'}),link.click({noWaitAfter:true})]);
   check(await page.locator('#'+item.module).count()===1,label+' detail module reached '+item.card);
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),label+' detail responsive '+item.card);
   const cta=page.getByRole('link',{name:item.cta,exact:true});check(await cta.count()===1,label+' contextual CTA exists '+item.card);
   await Promise.all([page.waitForURL(origin+'/services/?tn_service_context='+item.context+'#service-request',{waitUntil:'domcontentloaded'}),cta.click({noWaitAfter:true})]);
   check(await page.locator('.tn-service-request select[name="tn_service_context"]').inputValue()===item.context,label+' correct request subject '+item.card);
   check(await page.locator('.tn-service-request input[name="action"]').getAttribute('value')==='tn_ticket_submit'&&(await page.locator('.tn-service-request input[name="_wpnonce"]').getAttribute('value')).length>0,label+' existing ticket action and nonce '+item.card);
   await page.goto(origin+'/services/',{waitUntil:'networkidle'});
  }
  check(errors.length===0,label+' no browser exception');await ctx.close();
 }
 check(writes===0,'No mutation attempted');const result={status:'PASS',origin,observed_utc:new Date().toISOString(),checks,passed:checks.length,submissions:0};fs.writeFileSync(path.join(out,before?'before-service-browser.json':'service-browser.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({status:'PASS',checks:checks.length,submissions:0}));
}catch(error){if(activePage&&!activePage.isClosed())await activePage.screenshot({path:path.join(out,'failure-view-private.png')}).catch(()=>{});throw error;}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
