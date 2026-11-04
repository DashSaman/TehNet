'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const origin=process.env.TN_TRIAGE_ORIGIN,out=path.resolve(process.argv[2]);assert.match(origin,/^http:\/\/127\.0\.0\.1:\d+$/);
const checks=[];let writes=0,external=0;const check=(value,label)=>{assert.ok(value,label);checks.push(label);};
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({channel:'msedge',headless:true});
try{
 for(const width of [1440,768,375,320])for(const theme of ['light','dark']){
  const ctx=await browser.newContext({viewport:{width,height:950},acceptDownloads:true,reducedMotion:'reduce'});
  await ctx.route('**/*',r=>{if(!['GET','HEAD'].includes(r.request().method())){writes++;return r.abort();}if(!r.request().url().startsWith(origin+'/')){external++;return r.abort();}return r.continue();});
  const page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(origin+'/',{waitUntil:'networkidle'});await page.evaluate(t=>document.documentElement.dataset.theme=t,theme);
  const roots=page.locator('[data-tn-triage]'),root=roots.nth(0),second=roots.nth(1),label=width+'/'+theme;
  check(await roots.count()===2,label+' actual native-rendered multiple instances');
  check(await root.getAttribute('data-tn-triage-ready')==='1',label+' JS initialized');
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),label+' no page overflow');
  check(await root.locator('input').count()===0&&await root.locator('form').count()===0,label+' no private input or duplicate form');
  check(await root.locator('a[href="http://localhost:18085/services/?tn_service_context=network-support#service-request"]').count()===1,label+' existing request destination');
  for(const problem of ['internet','dns','dhcp','vpn','vlan','nat','gateway']){
   await root.locator('[data-tn-triage-problem]').selectOption(problem);await root.locator('[data-tn-triage-next]').click();
   check(await root.locator('[data-tn-triage-scope]').evaluate(e=>e===document.activeElement),label+'/'+problem+' focus advances');
   await root.locator('[data-tn-triage-scope]').selectOption('several');await root.locator('[data-tn-triage-next]').click();
   const rule=root.locator('[data-tn-triage-rule="'+problem+'"]');check(await rule.isVisible(),label+'/'+problem+' relevant rule shown');
   const select=rule.locator('select'),value=await select.locator('option').nth(1).getAttribute('value');await select.selectOption(value);await root.locator('[data-tn-triage-build]').click();
   const report=root.locator('[data-tn-triage-summary]');check(await report.isVisible()&&await report.getAttribute('readonly')!==null,label+'/'+problem+' reviewable readonly summary');
   check((await report.inputValue()).includes('هیچ فرمانی اجرا نشده')&&(await report.inputValue()).includes('تشخیص قطعی'),label+'/'+problem+' honest limits visible');
   const [download]=await Promise.all([page.waitForEvent('download'),root.locator('[data-tn-triage-download]').click()]);
   const target=path.join(out,'report-'+width+'-'+theme+'-'+problem+'.json');await download.saveAs(target);const data=JSON.parse(fs.readFileSync(target,'utf8'));
   check(data.problem===problem&&data.scope==='several'&&data.observation===value&&data.status==='MANUAL_UNVERIFIED',label+'/'+problem+' actual JSON download matches choices');
   check(await second.locator('[data-tn-triage-problem]').inputValue()===''&&await second.locator('[data-tn-triage-result]').isHidden(),label+'/'+problem+' other instance unchanged');
   if(problem==='dns'&&[375,1440].includes(width)){await root.locator('[data-tn-triage-result]').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'triage-result-'+width+'-'+theme+'.png')});}
   await root.locator('[data-tn-triage-back]').click();check(await root.locator('[data-tn-triage-result]').isHidden(),label+'/'+problem+' stale report cleared when navigating');
   await root.locator('[data-tn-triage-back]').click();await root.locator('[data-tn-triage-problem]').selectOption(problem==='dns'?'nat':'dns');
   check(await root.locator('[data-tn-triage-rule] select').evaluateAll(elements=>elements.every(e=>e.value==='unknown')),label+'/'+problem+' different issue clears stale observations');
   await root.locator('[data-tn-triage-reset]').click();check(await root.locator('[data-tn-triage-problem]').inputValue()===''&&await root.locator('[data-tn-triage-next]').isDisabled(),label+'/'+problem+' reset restores initial state');
  }
  check(errors.length===0,label+' no page exception');check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),label+' no overflow after interactions');await ctx.close();
 }
 const ctx=await browser.newContext({viewport:{width:320,height:950},javaScriptEnabled:false});const page=await ctx.newPage();await page.goto(origin+'/',{waitUntil:'networkidle'});const root=page.locator('[data-tn-triage]').first();
 check(await root.locator('[data-tn-triage-rule]').count()===7,'no-JS seven server-rendered guides');
 for(const rule of await root.locator('[data-tn-triage-rule]').all())check(await rule.isVisible(),'no-JS guide readable');
 check(await root.locator('noscript').isVisible(),'no-JS explicit capability boundary');
 check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'no-JS 320px no overflow');await page.screenshot({path:path.join(out,'triage-no-js-320.png')});await ctx.close();
 check(writes===0&&external===0,'No tool mutation or external network attempt');const result={schema:1,status:'PASS',checks,passed:checks.length,viewports:[1440,768,375,320],themes:['light','dark'],no_js_width:320,multiple_instances:2,actual_json_downloads:56,submissions:0,production_mutations:0,scope:'Actual WordPress renderer in isolated preview; local component fixture, not a published page or integrated site journey'};
 fs.writeFileSync(path.join(out,'browser-component-private.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({status:'PASS',checks:checks.length,downloads:56,submissions:0}));
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
