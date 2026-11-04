'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const origin=process.env.TN_SERVICE_ORIGIN,out=path.resolve(process.argv[2]),before=process.env.TN_SERVICE_BEFORE==='1';
assert.ok(['http://localhost:18085','https://tehnet.ir'].includes(origin));let writes=0;const checks=[];const check=(v,l)=>{assert.ok(v,l);checks.push(l);};
const modules=[{anchor:'server-project-brief',context:'server-scoping',ctaLabel:'درخواست بررسی سرور و مجازی‌سازی',source:'https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/checkpoints'},{anchor:'branch-connectivity-brief',context:'wifi-branch-scoping',ctaLabel:'درخواست طراحی ارتباط شعب',source:'https://manual.mikrotik.com/docs/cli-reference/interface/wireguard/peers/'}];
let activePage;const navigationEvents=[];
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({channel:'msedge',headless:true,args:['--host-resolver-rules=MAP localhost 127.0.0.1']});
try{
 for(const width of [1440,375,320])for(const theme of width===320?['light']:['light','dark']){
  const context=await browser.newContext({viewport:{width,height:950},javaScriptEnabled:width!==320,colorScheme:theme,reducedMotion:'reduce'});
  await context.route('**/*',r=>{if(!['GET','HEAD'].includes(r.request().method())){writes++;return r.abort();}return r.request().url().startsWith(origin+'/')?r.continue():r.abort();});
  await context.addInitScript(t=>localStorage.setItem('tn-theme',t),theme);const page=await context.newPage();activePage=page;const errors=[];page.on('pageerror',e=>errors.push(e.message));
  page.on('request',r=>{if(r.isNavigationRequest())navigationEvents.push({event:'request',url:r.url()});});
  page.on('requestfailed',r=>{if(r.isNavigationRequest())navigationEvents.push({event:'failed',url:r.url(),reason:r.failure()?.errorText});});
  page.on('framenavigated',f=>{if(f===page.mainFrame())navigationEvents.push({event:'committed',url:f.url()});});
  const response=await page.goto(origin+'/services/network-setup-tehran/',{waitUntil:'networkidle'});const label=width+'/'+theme;
  check(response.status()===200,label+' HTTP200');
  check(await page.locator('main h1').count()===1&&(await page.locator('main h1').innerText())==='راه‌اندازی شبکه شرکت در تهران',label+' existing title/H1');
  check((await page.locator('meta[name="robots"]').getAttribute('content')).includes('noindex'),label+' preserved noindex');
  check(await page.locator('link[rel="canonical"]').getAttribute('href')===origin+'/services/network-setup-tehran/',label+' same URL owner');
  check(await page.evaluate(()=>document.documentElement.dir==='rtl'&&document.documentElement.scrollWidth<=innerWidth),label+' RTL/no overflow');
  if(!before){
   check(await page.locator('html').getAttribute('data-theme')===theme,label+' actual theme');const text=await page.locator('main').innerText();
   check(text.includes('مثال فرضی')&&text.includes('اندازه‌گیری نشده'),label+' hypothetical examples distinguished');
   check(await page.locator('main a[href="https://mytel.one/services/"]').count()>0,label+' independent MyTel referral retained');
   for(const item of modules){
    check(await page.locator('#'+item.anchor).count()===1&&await page.locator('main a[href="#'+item.anchor+'"]').count()>0,label+' discoverable module '+item.anchor);
    check(await page.locator('main a[href="'+item.source+'"]').count()>0,label+' official scoped source '+item.anchor);
    const cta=page.getByRole('link',{name:item.ctaLabel,exact:true});check(await cta.count()===1&&await cta.getAttribute('href')==='/services/?tn_service_context='+item.context+'#service-request',label+' canonical request link '+item.context);
    if(width!==320){await page.locator('#'+item.anchor).scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,(before?'before-':'after-')+item.anchor+'-'+width+'-'+theme+'.png')});}
    await Promise.all([page.waitForURL(origin+'/services/?tn_service_context='+item.context+'#service-request',{waitUntil:'domcontentloaded'}),cta.first().click({noWaitAfter:true})]);
    check(await page.locator('.tn-service-request select[name="tn_service_context"]').inputValue()===item.context,label+' context preselected '+item.context);
    check(await page.locator('.tn-service-request input[name="action"]').getAttribute('value')==='tn_ticket_submit',label+' existing ticket action '+item.context);
    check((await page.locator('.tn-service-request input[name="_wpnonce"]').getAttribute('value')).length>0,label+' real existing form nonce '+item.context);
    await page.goto(origin+'/services/network-setup-tehran/',{waitUntil:'networkidle'});
   }
   check(errors.length===0,label+' no page exception');
  }else if(width!==320){await page.screenshot({path:path.join(out,'before-existing-service-'+width+'-'+theme+'.png')});}
  await context.close();
 }
 check(writes===0,'No form or other writes attempted');const result={status:'PASS',observed_utc:new Date().toISOString(),origin,checks,passed:checks.length,submissions:0,request_infrastructure:'existing tn_ticket_submit; navigation/context/nonce verified; no new ticket in this read-only run'};
 fs.writeFileSync(path.join(out,before?'before-service-browser.json':'service-browser.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({status:'PASS',checks:checks.length,submissions:0}));
}catch(error){
 fs.writeFileSync(path.join(out,'navigation-events-private.json'),JSON.stringify({current_url:activePage&&!activePage.isClosed()?activePage.url():null,events:navigationEvents},null,2));
 if(activePage&&!activePage.isClosed())await activePage.screenshot({path:path.join(out,'failure-view-private.png')}).catch(()=>{});
 throw error;
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
