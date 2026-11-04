'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const{chromium}=require('playwright');
const out=path.resolve(process.argv[2]);const origin=process.env.TN_EDUCATION_ORIGIN;
const before=process.env.TN_EDUCATION_BEFORE==='1';
assert.ok(origin==='http://localhost:18085'||origin==='https://tehnet.ir');
const manifest=require('../content/educational-integrity-2026-11-04/manifest.json');
const checks=[];let writes=0;const check=(v,l)=>{assert.ok(v,l);checks.push(l);};
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({channel:'msedge',headless:true,args:['--host-resolver-rules=MAP localhost 127.0.0.1']});
try{
 for(const target of manifest.targets){
  if(before&&![40,67].includes(target.id))continue;
  for(const width of before?[1440,375]:([40,67].includes(target.id)?[1440,768,375,320]:[1440,375,320])){
   for(const theme of before?['dark']:width===320?['light']:['dark','light']){
    const context=await browser.newContext({viewport:{width,height:950},javaScriptEnabled:width!==320,reducedMotion:'reduce',colorScheme:theme});
    await context.route('**/*',r=>{if(!['GET','HEAD'].includes(r.request().method())){writes++;return r.abort();}return r.request().url().startsWith(origin+'/')?r.continue():r.abort();});
    await context.addInitScript(t=>localStorage.setItem('tn-theme',t),theme);
    const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
    const response=await page.goto(origin+'/'+target.uri+'/',{waitUntil:'networkidle'});const label=target.id+'/'+width+'/'+theme;
    check(response.status()===200,label+' HTTP200');
    if(!before){
     check(await page.locator('main h1').count()===1,label+' one H1');
     check((await page.locator('main h1').innerText())===(target.title||target.title_observed),label+' truthful H1');
     check((await page.locator('meta[name="robots"]').getAttribute('content')).includes('noindex'),label+' retained noindex');
     check(await page.locator('link[rel="canonical"]').getAttribute('href')===origin+'/'+target.uri+'/',label+' preserved canonical');
     check(await page.evaluate(()=>document.documentElement.dir==='rtl'&&document.documentElement.scrollWidth<=innerWidth),label+' RTL without horizontal overflow');
     check(await page.locator('html').getAttribute('data-theme')===theme,label+' actual theme');
     const text=await page.locator('main').innerText();
     check(text.includes([62,63,64,65,66].includes(target.id)?'آموزش نوشتاری مستقل':'تکمیلی مستقل'),label+' visible content role');
     if(target.id>=62&&target.id<=67)check(await page.locator('main a[href*="youtu"], main iframe[src*="youtu"]').count()===0,label+' no unsupported lesson-video association');
     if(target.id===67)check(text.includes('خارج از جلسات ضبط‌شده')&&text.includes('تدریس نشده'),label+' Queue separated from recordings');
     if(target.id===40)for(const id of ['Wbj3C0g__zw','a0JMhBdNNgs','hqjjvQoO7as','Z5EWfUn1Ejw','LO4m55Hf-do','XRIMAowqdM4','I_8T6nu8JNg','OgypQcQS3FA'])check(await page.locator('main a[href*="'+id+'"]').count()>0,label+' original video '+id);
     check(!(await page.locator('script[type="application/ld+json"]').allTextContents()).some(x=>x.includes('VideoObject')),label+' no fabricated video schema');
     check(errors.length===0,label+' no page exception');
    }
    if([40,67].includes(target.id)&&width!==320){
     await page.screenshot({path:path.join(out,(before?'before-':'after-')+target.id+'-'+width+'-'+theme+'.png'),fullPage:true});
    }
    await context.close();
   }
  }
 }
 check(writes===0,'Read-only browser journey');
 const result={status:'PASS',observed_utc:new Date().toISOString(),mode:before?'before':'after',origin,checks,passed:checks.length,submissions:0};
 fs.writeFileSync(path.join(out,before?'before-browser.json':'education-browser.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify({status:'PASS',mode:result.mode,passed:checks.length,submissions:0}));
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
