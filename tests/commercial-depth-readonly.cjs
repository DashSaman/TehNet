'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');const{chromium}=require('playwright');
const origin=process.env.TN_DEPTH_ORIGIN;assert.ok(origin==='http://localhost:18085'||origin==='https://tehnet.ir');
const out=path.resolve(process.argv[2]);const target=JSON.parse(process.env.TN_DEPTH_TARGET);assert.ok([31,33,35].includes(target.id));let writes=0;const checks=[];
const check=(s,v)=>{assert.ok(v,s);checks.push(s);};
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({channel:'msedge',headless:true,args:['--host-resolver-rules=MAP localhost 127.0.0.1']});
try{for(const width of [1440,375])for(const js of [true,false]){
 const context=await browser.newContext({viewport:{width,height:900},javaScriptEnabled:js,reducedMotion:'reduce'});await context.route('**/*',r=>{if(!['GET','HEAD'].includes(r.request().method())){writes++;return r.abort();}return r.request().url().startsWith(origin+'/')?r.continue():r.abort();});
 const page=await context.newPage();const response=await page.goto(origin+'/'+target.uri+'/',{waitUntil:'domcontentloaded'});
 check(`${width}/js=${js} HTTP200`,response.status()===200);check(`${width}/js=${js} one H1`,await page.locator('main h1').count()===1);
 check(`${width}/js=${js} retained noindex`,(await page.locator('meta[name=robots]').getAttribute('content')).includes('noindex'));
 check(`${width}/js=${js} same URL owner`,await page.locator('link[rel=canonical]').getAttribute('href')===origin+'/'+target.uri+'/');
 check(`${width}/js=${js} RTL/no overflow`,await page.evaluate(()=>document.documentElement.dir==='rtl'&&document.documentElement.scrollWidth<=innerWidth));
 check(`${width}/js=${js} substantive new module`,await page.locator('#'+target.anchor).count()===1&&(await page.locator('main').innerText()).includes(target.phrase));
 check(`${width}/js=${js} explicit synthetic example`,(await page.locator('main').innerText()).includes('فرضی'));
 check(`${width}/js=${js} official linked source`,await page.locator(`main a[href="${target.source}"]`).count()>0);
 check(`${width}/js=${js} existing service request route`,await page.locator(`main a[href="/services/?tn_service_context=${target.context}#service-request"]`).count()>0);
 check(`${width}/js=${js} service brief avoids equipment B2B destination`,await page.locator('main a[href="/b2b/"]').count()===0);
 if(js){await page.locator('#'+target.anchor).scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'module-'+width+'.png')});}
 await context.close();
}check('No writes attempted',writes===0);const receipt={status:'PASS',observed_utc:new Date().toISOString(),id:target.id,url:origin+'/'+target.uri+'/',checks,passed:checks.length,submissions:0,device_network_tests:0};fs.writeFileSync(path.join(out,'depth-browser.json'),JSON.stringify(receipt,null,2));console.log(JSON.stringify({status:'PASS',id:target.id,passed:checks.length}));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
