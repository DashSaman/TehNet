'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const origin=process.env.TN_SERVICE_ORIGIN,out=path.resolve(process.argv[2]),before=process.env.TN_SERVICE_BEFORE==='1';assert.ok(['http://localhost:18085','https://tehnet.ir'].includes(origin));
const checks=[];let writes=0;const check=(v,label)=>{assert.ok(v,label);checks.push(label);};
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({channel:'msedge',headless:true,args:['--host-resolver-rules=MAP localhost 127.0.0.1']});
try{
 for(const width of before?[375]:[1440,768,375,320])for(const mode of before?['light']:(width===320?['light','dark','nojs']:['light','dark'])){
  const ctx=await browser.newContext({viewport:{width,height:950},javaScriptEnabled:mode!=='nojs',colorScheme:mode==='dark'?'dark':'light',acceptDownloads:true,reducedMotion:'reduce'});
  await ctx.route('**/*',r=>{if(!['GET','HEAD'].includes(r.request().method())){writes++;return r.abort();}return r.request().url().startsWith(origin+'/')?r.continue():r.abort();});
  await ctx.addInitScript(t=>localStorage.setItem('tn-theme',t),mode==='dark'?'dark':'light');const page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));const response=await page.goto(origin+'/lab/',{waitUntil:'networkidle'}),label=width+'/'+mode;
  check(response.status()===200&&await page.locator('main h1').count()===1,label+' existing Lab owner HTTP/H1');
  check((await page.locator('meta[name="robots"]').getAttribute('content')).includes('noindex')&&await page.locator('link[rel="canonical"]').getAttribute('href')===origin+'/lab/',label+' existing noindex/canonical');
  check(await page.evaluate(()=>document.documentElement.dir==='rtl'&&document.documentElement.scrollWidth<=innerWidth),label+' RTL without overflow');
  for(const route of ['/lab/gns3-mikrotik/','/lab/wireguard-mtu/','/lab/voice-network-checklist/'])check(await page.locator('main a[href="'+route+'"]').count()>0,label+' existing Lab path retained '+route);
  const root=page.locator('[data-tn-triage]');
  if(before){check(await root.count()===0,label+' before tool absent');await page.screenshot({path:path.join(out,'before-lab-375-light.png')});await ctx.close();continue;}
  check(await root.count()===1&&await root.locator('[data-tn-triage-rule]').count()===7,label+' one real shortcode and seven rules');
  check(await root.locator('input').count()===0&&await root.locator('form').count()===0,label+' no sensitive input or parallel backend');
  check(await root.locator('a[href="https://mytel.one/services/"]').count()===1,label+' independent MyTel context');
  check(await page.locator('link[href*="network-troubleshooting.css"]').count()===1&&await page.locator('script[src*="network-troubleshooting.js"]').count()===1,label+' component assets loaded only once');
  if(mode==='nojs'){
   for(const rule of await root.locator('[data-tn-triage-rule]').all())check(await rule.isVisible(),label+' manual rule readable');
   check(await root.locator('noscript').isVisible(),label+' explicit no-JS guidance');await root.scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'after-triage-320-nojs.png')});
  }else{
   check(await page.locator('html').getAttribute('data-theme')===mode,label+' actual theme');
   for(const problem of width===1440&&mode==='light'?['internet','dns','dhcp','vpn','vlan','nat','gateway']:['dns','gateway']){
    await root.locator('[data-tn-triage-problem]').selectOption(problem);await root.locator('[data-tn-triage-next]').click();await root.locator('[data-tn-triage-scope]').selectOption('one');await root.locator('[data-tn-triage-next]').click();
    const rule=root.locator('[data-tn-triage-rule="'+problem+'"]');check(await rule.isVisible(),label+'/'+problem+' relevant question');
    await root.locator('[data-tn-triage-build]').click();const report=root.locator('[data-tn-triage-summary]');check((await report.inputValue()).includes('هیچ فرمانی اجرا نشده')&&(await report.inputValue()).includes('تشخیص قطعی'),label+'/'+problem+' unknown observation and honest summary');
    check(await report.evaluate(e=>e.scrollTop===0&&e.selectionStart===0),label+'/'+problem+' new report starts at beginning');
    const [download]=await Promise.all([page.waitForEvent('download'),root.locator('[data-tn-triage-download]').click()]);const file=path.join(out,'site-report-'+width+'-'+mode+'-'+problem+'.json');await download.saveAs(file);const json=JSON.parse(fs.readFileSync(file,'utf8'));
    check(json.problem===problem&&json.observation==='unknown'&&json.scope==='one'&&json.status==='MANUAL_UNVERIFIED',label+'/'+problem+' real local JSON');
    if(problem==='dns'&&[375,1440].includes(width)){await root.locator('[data-tn-triage-result]').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'after-triage-'+width+'-'+mode+'.png')});}
    await root.locator('[data-tn-triage-reset]').click();check(await root.locator('[data-tn-triage-result]').isHidden(),label+'/'+problem+' reset clears summary');
   }
  }
  const cta=root.getByRole('link',{name:'درخواست عیب‌یابی از مسیر فعلی خدمات',exact:true});
  check(await cta.getAttribute('href')===origin+'/services/?tn_service_context=network-support#service-request',label+' canonical request href');
  await Promise.all([page.waitForURL(origin+'/services/?tn_service_context=network-support#service-request',{waitUntil:'domcontentloaded'}),cta.click({noWaitAfter:true})]);
  check(await page.locator('.tn-service-request select[name="tn_service_context"]').inputValue()==='network-support',label+' existing support context selected');
  check(await page.locator('.tn-service-request input[name="action"]').getAttribute('value')==='tn_ticket_submit'&&(await page.locator('.tn-service-request input[name="_wpnonce"]').getAttribute('value')).length>0,label+' existing ticket action/nonce');
  check(await page.locator('script[src*="network-troubleshooting.js"]').count()===0&&await page.locator('link[href*="network-troubleshooting.css"]').count()===0,label+' assets absent from unrelated Services');
  check(errors.length===0,label+' no page exceptions');await ctx.close();
 }
 check(writes===0,'No form or other mutation attempted');const result={status:'PASS',passed:checks.length,checks,origin,observed_utc:new Date().toISOString(),submissions:0};fs.writeFileSync(path.join(out,before?'before-service-browser.json':'service-browser.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({status:'PASS',checks:checks.length,submissions:0}));
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
