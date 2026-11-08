'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto'),{chromium}=require('playwright');
const origin=process.env.TN_SERVICE_ORIGIN,out=path.resolve(process.argv[2]),before=process.env.TN_SERVICE_BEFORE==='1';assert.equal(origin,'http://localhost:18085');
const prefix='/wp-content/mu-plugins/tehnet-technical-resources/learning-media/queue-cloud-20261108/',manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'../content/queue-winbox-cloud-2026-11-08/manifest.json'))),captures=JSON.parse(fs.readFileSync(path.join(__dirname,'../content/queue-winbox-cloud-2026-11-08/captures.json'))),checks=[];let writes=0;
const check=(v,s)=>{assert.ok(v,s);checks.push(s);};
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({headless:true,args:['--host-resolver-rules=MAP localhost 127.0.0.1']});
try{
 for(const target of [manifest.target])for(const width of before?[375]:[1440,768,375,320])for(const mode of before?['light']:(width===320?['light','dark','nojs']:['light','dark'])){
  const ctx=await browser.newContext({viewport:{width,height:1000},javaScriptEnabled:mode!=='nojs',colorScheme:mode==='dark'?'dark':'light',reducedMotion:'reduce'});await ctx.route('**/*',r=>{if(!['GET','HEAD'].includes(r.request().method())){writes++;return r.abort();}return r.request().url().startsWith(origin+'/')?r.continue():r.abort();});await ctx.addInitScript(t=>localStorage.setItem('tn-theme',t),mode==='dark'?'dark':'light');
  const page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));const article='/'+target.uri+'/',response=await page.goto(origin+article,{waitUntil:'networkidle'}),label=target.id+'/'+width+'/'+mode;
  check(response.status()===200&&await page.locator('main h1').count()===1,label+' original article HTTP/H1');check((await page.locator('meta[name="robots"]').getAttribute('content')).includes('noindex')&&await page.locator('link[rel="canonical"]').getAttribute('href')===origin+article,label+' intentional noindex/canonical retained');
  const imgs=page.locator('main img[src^="'+prefix+'"]'),expected=12,anchor='#winbox-queue-cloud';
  if(before){check(await imgs.count()===0&&await page.locator(anchor).count()===0,label+' before has no real illustrated guide');await page.screenshot({path:path.join(out,'before-'+target.id+'-375-light.png')});await ctx.close();continue;}
  check(await imgs.count()===expected,label+' exact original screenshot count');check(await page.locator(anchor).count()===1,label+' guide reachable in existing owner');
  const text=await page.locator('main').innerText();check(text.includes('راهنمای تکمیلی مستقل')&&text.includes('CHR')&&text.includes('WinBox'),label+' actual lab clearly separate from old videos');
  check((await page.locator('main strong').count())>20,label+' click options bold');
  for(const img of await imgs.all()){
   await img.scrollIntoViewIfNeeded();await img.evaluate(el=>el.decode());const src=await img.getAttribute('src'),name=path.basename(src),figure=img.locator('../..'),a=img.locator('..');
   check(await img.evaluate(el=>el.complete&&el.naturalWidth>=600&&el.getBoundingClientRect().width<=innerWidth),label+' loaded responsive '+name);
   check((await img.getAttribute('alt')).length>25&&await a.getAttribute('href')===src,label+' alt/original full-size '+name);
   const overlay=await a.evaluate(el=>{const p=getComputedStyle(el,'::after'),a=el.getBoundingClientRect(),img=el.querySelector('img').getBoundingClientRect();return {border:p.borderTopStyle,pointer:p.pointerEvents,x:parseFloat(p.left),y:parseFloat(p.top),w:parseFloat(p.width),h:parseFloat(p.height),aw:a.width,ah:a.height,iw:img.width,ih:img.height};});
   check(overlay.border==='solid'&&overlay.pointer==='none'&&overlay.w>0&&overlay.h>0&&overlay.x>=0&&overlay.y>=0&&overlay.x+overlay.w<=overlay.aw+1&&overlay.y+overlay.h<=overlay.ah+1&&Math.abs(overlay.ah-overlay.ih)<2,label+' callout stays on actual image '+name);
   check((await figure.getAttribute('class')).includes('tn-lab-capture'),label+' native figure class '+name);
  }
  check(await page.evaluate(()=>document.documentElement.dir==='rtl'&&document.documentElement.scrollWidth<=innerWidth),label+' RTL no horizontal overflow');
  if([1440,375].includes(width)&&mode==='light'){await page.locator(anchor).scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'after-'+target.id+'-'+width+'-light.png')});await imgs.first().scrollIntoViewIfNeeded();await page.screenshot({path:path.join(out,'callout-'+target.id+'-'+width+'-light.png')});}
  if(width===375&&mode==='light'){const first=imgs.first(),src=await first.getAttribute('src');await first.click();check(page.url()===origin+src,label+' actual full-size image opens');await page.goBack({waitUntil:'networkidle'});}
  check(errors.length===0,label+' no page exception');await ctx.close();
 }
 if(!before){const ctx=await browser.newContext();for(const shot of captures.captures){const response=await ctx.request.get(origin+prefix+shot.name+'.png');check(response.status()===200&&crypto.createHash('sha256').update(await response.body()).digest('hex')===shot.sha256,'Served original bytes '+shot.name);}await ctx.close();}
 check(writes===0,'Zero form submissions or writes');const result={status:'PASS',passed:checks.length,checks,origin,observed_utc:new Date().toISOString(),submissions:0};fs.writeFileSync(path.join(out,before?'before-browser.json':'browser.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({status:'PASS',checks:checks.length,submissions:0}));
}finally{await browser.close();}})().catch(e=>{
 const message=String(e.message||'').replace(/\/(?:tmp|home|root)\/[^\s'"]+/g,'<CLOUD_TEMP_PATH>').slice(0,450);
 console.log('TN_BROWSER_ERROR '+JSON.stringify({name:e.name,message}));
 process.exitCode=1;
});
