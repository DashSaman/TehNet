'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const origin=process.env.TN_SERVICE_ORIGIN,out=path.resolve(process.argv[2]),before=process.env.TN_SERVICE_BEFORE==='1';assert.ok(['http://localhost:18085','https://tehnet.ir'].includes(origin));
const checks=[];let writes=0;const check=(v,label)=>{assert.ok(v,label);checks.push(label);};
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({channel:'msedge',headless:true,args:['--host-resolver-rules=MAP localhost 127.0.0.1']});
try{
 for(const width of before?[375]:[1440,768,375,320])for(const mode of before?['light']:(width===320?['light','dark','nojs']:['light','dark'])){
  const ctx=await browser.newContext({viewport:{width,height:950},javaScriptEnabled:mode!=='nojs',colorScheme:mode==='dark'?'dark':'light',reducedMotion:'reduce'});
  await ctx.route('**/*',r=>{if(!['GET','HEAD'].includes(r.request().method())){writes++;return r.abort();}return r.request().url().startsWith(origin+'/')?r.continue():r.abort();});
  await ctx.addInitScript(t=>localStorage.setItem('tn-theme',t),mode==='dark'?'dark':'light');const page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));const response=await page.goto(origin+'/lab/',{waitUntil:'networkidle'}),label=width+'/'+mode;
  check(response.status()===200&&await page.locator('main h1').count()===1,label+' existing Lab HTTP/H1');
  check((await page.locator('meta[name="robots"]').getAttribute('content')).includes('noindex')&&await page.locator('link[rel="canonical"]').getAttribute('href')===origin+'/lab/',label+' original noindex/canonical');
  check(await page.evaluate(()=>document.documentElement.dir==='rtl'&&document.documentElement.scrollWidth<=innerWidth),label+' RTL no overflow');
  const root=page.locator('[data-tn-routing-lab]');
  if(before){check(await root.count()===0,label+' before conceptual tool absent');await page.screenshot({path:path.join(out,'before-routing-375-light.png')});await ctx.close();continue;}
  check(await root.count()===1&&await root.locator('[data-tn-routing-node]').count()===4,label+' actual shortcode and topology');
  check(await page.locator('[data-tn-triage]').count()===1&&await page.locator('[data-tn-triage-rule]').count()===7,label+' previous manual tool retained');
  check(await page.locator('main a[href="#static-routing-practice"]').count()===1&&await page.locator('main a[href="#network-troubleshooting"]').count()===1,label+' both tools discoverable');
  check((await root.innerText()).includes('شبیه‌ساز واقعی روتر نیست')&&(await root.innerText()).includes('RFC5737'),label+' conceptual limits visible');
  check(await root.locator('input,form,iframe').count()===0,label+' no target input or external emulator');
  check(await page.locator('link[href*="static-routing-lab.css"]').count()===1&&await page.locator('script[src*="static-routing-lab.js"]').count()===1,label+' conditional assets once');
  const answer=root.locator('details');
  if(mode==='nojs'){
   await answer.locator('summary').click();check(await answer.locator('pre').isVisible(),label+' no-JS educational answer accessible');check(await root.locator('noscript').isVisible(),label+' explicit no-JS limits');
   await root.scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'after-routing-320-nojs.png')});
  }else{
   check(await root.getAttribute('data-tn-routing-ready')==='1',label+' actual JS active');
   await root.locator('[data-tn-routing-check]').click();check((await root.locator('output').innerText()).includes('ابتدا برای هر دو روتر'),label+' unknown choices remain unknown');
   await root.locator('[data-tn-routing-choice="r1"]').selectOption('correct');await root.locator('[data-tn-routing-choice="r2"]').selectOption('missing');await root.locator('[data-tn-routing-check]').click();
   check((await root.locator('output').innerText()).includes('رفت در مدل به سرویس می‌رسد')&&(await root.locator('output').innerText()).includes('روتر R2'),label+' forward success does not fabricate return success');
   await root.locator('[data-tn-routing-direction]').selectOption('return');await root.locator('[data-tn-routing-next]').click();check(await root.locator('[data-tn-routing-node="r2"]').getAttribute('data-visit')==='current'&&await root.locator('[data-tn-routing-next]').isDisabled(),label+' return visibly stops at R2');
   await root.locator('[data-tn-routing-choice="r1"]').selectOption('wrong-gateway');check((await root.locator('output').innerText()).includes('انتخاب‌ها تغییر'),label+' route edit clears stale verdict');await root.locator('[data-tn-routing-check]').click();check((await root.locator('output').innerText()).includes('next-hop'),label+' unreachable next hop explained');
   await root.locator('[data-tn-routing-choice="r1"]').selectOption('wrong-network');await root.locator('[data-tn-routing-check]').click();check((await root.locator('output').innerText()).includes('prefix'),label+' nonmatching prefix distinguished');
   await root.locator('[data-tn-routing-choice="r1"]').selectOption('correct');await root.locator('[data-tn-routing-choice="r2"]').selectOption('correct');await root.locator('[data-tn-routing-check]').click();
   check((await root.locator('output').innerText()).includes('در این مدل درست است'),label+' correct pair accepted only as model');
   for(const [direction,destination]of [['forward','server'],['return','client']]){
    await root.locator('[data-tn-routing-direction]').selectOption(direction);for(let i=0;i<3;i++)await root.locator('[data-tn-routing-next]').click();
    check(await root.locator('[data-tn-routing-node="'+destination+'"]').getAttribute('data-visit')==='current'&&await root.locator('[data-tn-routing-next]').isDisabled(),label+' bounded packet steps '+direction);
    await root.locator('[data-tn-routing-prev]').click();check(!await root.locator('[data-tn-routing-next]').isDisabled(),label+' previous packet step '+direction);
   }
   check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),label+' topology/form no overflow after interaction');
   if([1440,375].includes(width)){await root.locator('[data-tn-routing-topology]').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'after-routing-'+width+'-'+mode+'.png')});}
   await root.locator('[data-tn-routing-reset]').click();check(await root.locator('[data-tn-routing-choice="r1"]').inputValue()===''&&await root.locator('[data-tn-routing-choice="r2"]').inputValue()===''&&await root.locator('[data-tn-routing-next]').isHidden(),label+' full reset');
   check(await page.locator('[data-tn-triage-problem]').inputValue()==='',label+' independent manual tool state');
  }
  check(errors.length===0,label+' no page exception');await ctx.close();
 }
 check(writes===0,'No writes or form submissions attempted');const r={status:'PASS',passed:checks.length,checks,origin,observed_utc:new Date().toISOString(),submissions:0};fs.writeFileSync(path.join(out,before?'before-service-browser.json':'service-browser.json'),JSON.stringify(r,null,2));console.log(JSON.stringify({status:'PASS',checks:checks.length,submissions:0}));
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
