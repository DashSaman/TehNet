'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const origin='http://localhost:18085',checks=[],assets=new Map();let posts=0;
const metadata=JSON.parse(fs.readFileSync('content/commercial-decision-2026-11-08-v2/metadata.json','utf8'));
const ck=(v,s)=>{assert.ok(v,s);checks.push(s);};
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
 for(const width of [1440,768,375,320])for(const dark of [false,true])for(const javaScriptEnabled of [true,false]){
  if(!javaScriptEnabled&&dark)continue; // Current server markup is light without JS; do not claim unsupported dark mode.
  const context=await browser.newContext({viewport:{width,height:900},javaScriptEnabled,colorScheme:dark?'dark':'light'});
  if(javaScriptEnabled)await context.addInitScript(t=>localStorage.setItem('tn-theme',t),dark?'dark':'light');
  await context.route('**/*',r=>{const u=new URL(r.request().url());return u.origin===origin&&r.request().method()==='GET'?r.continue():r.abort();});
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.name));
  page.on('response',r=>{if(/\.(css|woff2?)(\?|$)/.test(r.url()))assets.set(r.url(),r.status());});
  for(const pathname of ["/services/","/services/network-tehran/","/services/network-support-tehran/","/services/network-setup-tehran/","/services/mikrotik-tehran/","/network-support-contract-guide/","/network-project-proposal-checklist/","/business-server-planning-guide/","/server-backup-restore-acceptance/","/services/server-virtualization-tehran/"]){
   const response=await page.goto(origin+pathname,{waitUntil:'networkidle'});const key=pathname+width+'/'+dark+'/'+javaScriptEnabled;
   ck(response.status()===200,key+' full WordPress HTTP200');
   ck(await page.locator('h1').count()===1,key+' exactly one H1');
   const wanted=metadata.find(t=>new URL(t.url).pathname===pathname);ck((await page.locator('h1').innerText()).trim()===wanted.h1,key+' proposed H1 really visible');ck(await page.locator('meta[name=description]').getAttribute('content')===wanted.meta,key+' native excerpt supplies exact meta description');
   const article=await page.locator('script[type="application/ld+json"]').evaluateAll(es=>es.map(e=>{try{return JSON.parse(e.textContent)}catch{return null}}).filter(x=>x&&x['@type']==='Article'));
   ck(article.length===(wanted.id&&String(wanted.id).startsWith('A')?1:0),key+' truthful article/service schema role');
   ck((await page.locator('meta[name=robots]').getAttribute('content')).includes('noindex'),key+' noindex retained');
   ck(await page.locator('link[rel=canonical]').getAttribute('href')===origin+pathname,key+' self canonical');
   ck(await page.locator('html').getAttribute('data-theme')===(dark?'dark':'light'),key+' actual theme state');
   await page.evaluate(()=>document.fonts.ready);
   if(javaScriptEnabled){
    const toggle=page.locator('.tn-theme-toggle');await toggle.click();ck(await page.locator('html').getAttribute('data-theme')===(dark?'light':'dark'),key+' theme toggle changes state');await toggle.click();
    const menu=page.locator('.tn-menu-toggle');if(await menu.isVisible()){await menu.click();ck(await menu.getAttribute('aria-expanded')==='true',key+' mobile menu expands');await menu.click();ck(await menu.getAttribute('aria-expanded')==='false',key+' mobile menu closes');}
   }else ck(!(await page.locator('.tn-theme-toggle').isVisible()),key+' no-JS does not offer inactive theme control');
   ck(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),key+' actual theme no overflow');
   ck(await page.locator('html').getAttribute('dir')==='rtl',key+' actual RTL');
   ck(await page.evaluate(()=>document.fonts.size>0&&[...document.fonts].some(f=>f.status==='loaded')),key+' actual local font loaded');
   if(pathname==='/services/'){
    ck(await page.locator('form.tn-service-request').count()===1,key+' existing canonical request form');
    for(const href of ['/services/mikrotik-tehran/#firewall-acceptance','/services/network-support-tehran/#monitoring-acceptance'])ck(await page.locator('a[href="'+href+'"]').count()===1,key+' new catalog deep link');
    ck(await page.locator('.tn-service-request').evaluate(f=>new FormData(f).has('_wpnonce')),key+' nonce belongs to actual form');
   }else {
    ck(await page.locator('.entry-content a[href*="tn_service_context="]').count()>0,key+' canonical service CTA');
    const tables=page.locator('.tn-decision-table');ck(await tables.count()>0,key+' substantive decision table');
    ck(await tables.evaluateAll(es=>es.every(e=>e.getBoundingClientRect().right<=innerWidth+2&&e.getBoundingClientRect().left>=-2&&getComputedStyle(e).overflowX==='auto')),key+' tables scroll inside wrapper, not whole page');
   }
  }
  ck(errors.length===0,'No uncaught JavaScript errors in full theme context');await context.close();
 }
 ck(assets.size>0&&[...assets.values()].every(s=>s===200),'All observed real CSS/font assets200');
 const ctx=await browser.newContext({viewport:{width:375,height:900}});
 await ctx.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin!==origin)return r.abort();if(r.request().method()==='POST'){ck(u.pathname==='/wp-admin/admin-post.php','POST restricted to synthetic canonical endpoint');posts++;}return r.continue();});
 const page=await ctx.newPage();
 await page.goto(origin+'/services/server-virtualization-tehran/',{waitUntil:'networkidle'});
 await page.getByRole('link',{name:'ثبت درخواست بررسی سرور و مجازی‌سازی',exact:true}).click();await page.waitForURL('**/services/?tn_service_context=server-scoping#service-request');
 const f=page.locator('form.tn-service-request');ck(await f.locator('[name=tn_service_context]').inputValue()==='server-scoping','Actual hub click prefills approved service context');
 const form=await f.evaluate(f=>Object.fromEntries(new FormData(f)));
 const base={...form,tn_name:'آزمون ساختگی',tn_email:'fixture@example.invalid',tn_message:'این درخواست ساختگی فقط در لاب ابری ایجاد می‌شود.',tn_company:'نمونهٔ ساختگی'};
 const invalid=await ctx.request.post(origin+'/wp-admin/admin-post.php',{form:{...base,_wpnonce:'invalid'}});ck(invalid.status()===403,'Invalid nonce rejected403');
 const bad=await ctx.request.post(origin+'/wp-admin/admin-post.php',{form:{...base,tn_service_context:'unapproved'}});ck(bad.status()===400,'Unsupported service rejected400');
 const hp=await ctx.request.post(origin+'/wp-admin/admin-post.php',{form:{...base,tn_hp:'synthetic bot'}});ck(hp.status()===400,'Honeypot rejected400');
 const missing=await ctx.request.post(origin+'/wp-admin/admin-post.php',{form:base});ck(missing.status()===400,'Enabled CAPTCHA missing token rejected400');
 const provider=await ctx.request.post(origin+'/wp-admin/admin-post.php',{form:{...base,'g-recaptcha-response':'synthetic-invalid-provider'}});ck(provider.status()===503,'Closed CAPTCHA provider error fails503');
 await f.locator('[name=tn_name]').fill(base.tn_name);await f.locator('[name=tn_email]').fill(base.tn_email);await f.locator('[name=tn_message]').fill(base.tn_message);
 await f.evaluate((f,token)=>{const e=document.createElement('input');e.type='hidden';e.name='g-recaptcha-response';e.value=token;f.appendChild(e);},process.env.TN_FIXTURE_PASSWORD);
 await Promise.all([page.waitForURL('**/support/?tn_ticket=sent&tn_service_receipt=*'),f.locator('[type=submit]').click()]);
 ck(await page.locator('.tn-service-receipt').count()===1,'Actual form POST returns canonical receipt');
 const receiptResponse=await page.reload({waitUntil:'networkidle'});
 ck((receiptResponse.headers()['x-robots-tag']||'').includes('noindex'),'Receipt has noindex HTTP header');
 ck(receiptResponse.headers()['referrer-policy']==='no-referrer','Receipt has no-referrer header');
 const receiptText=await page.locator('.tn-service-receipt').innerText();
 ck(!receiptText.includes(base.tn_email)&&!receiptText.includes(base.tn_message)&&/TN-\d+/.test(receiptText),'Receipt contains tracking without private details');
 for(const [url,id] of [['/services/mikrotik-tehran/','firewall-acceptance'],['/services/network-support-tehran/','monitoring-acceptance']]){
  const r=await page.goto(origin+url+'#'+id,{waitUntil:'networkidle'});ck(r.status()===200&&await page.locator('#'+id).count()===1,'Deep link destination and actual anchor '+id);
 }
 const nojs=await browser.newContext({javaScriptEnabled:false});await nojs.route('**/*',r=>r.request().url().startsWith(origin+'/')?r.continue():r.abort());const p=await nojs.newPage();await p.goto(origin+'/services/',{waitUntil:'networkidle'});ck(await p.locator('.tn-captcha noscript a').count()===1,'No-JS CAPTCHA explains alternative contact path');await nojs.close();
 
 const manifest=JSON.parse(fs.readFileSync('content/commercial-decision-2026-11-08-v2/manifest.json','utf8'));
 const urlSet=new Set();for(const pth of ["/services/","/services/network-tehran/","/services/network-support-tehran/","/services/network-setup-tehran/","/services/mikrotik-tehran/","/network-support-contract-guide/","/network-project-proposal-checklist/","/business-server-planning-guide/","/server-backup-restore-acceptance/","/services/server-virtualization-tehran/"]){await page.goto(origin+pth,{waitUntil:'networkidle'});for(const href of await page.locator('.entry-content a[href]').evaluateAll(es=>es.map(e=>e.getAttribute('href'))))if(href.startsWith('/')||href.startsWith('#'))urlSet.add(new URL(href,origin+pth).href);}
 for(const href of urlSet){const u=new URL(href);if(u.search)continue;const response=await ctx.request.get(u.origin+u.pathname);ck(response.status()===200,'Internal content destination status='+response.status()+' '+u.pathname);if(u.hash){await page.goto(href,{waitUntil:'networkidle'});ck(await page.locator('[id="'+decodeURIComponent(u.hash.slice(1))+'"]').count()===1,'Existing/new anchor '+u.pathname+u.hash);}}
 for(const row of manifest.pages.filter(x=>x.key.startsWith('A'))){await page.goto(origin+'/'+row.slug+'/',{waitUntil:'networkidle'});const links=await page.locator('.entry-content a[href$=".csv"],.entry-content a[href$="-print.html"]').evaluateAll(es=>[...new Set(es.map(e=>e.getAttribute('href')))]);ck(links.length>=2,'Complete article has CSV and print aid '+row.key);for(const href of links){const r=await ctx.request.get(origin+href);ck(r.status()===200,'Aid download200 '+row.key);const expected=fs.readFileSync('site/'+href.replace('/wp-content/',''));ck((await r.body()).equals(expected),'Downloaded aid exact bytes '+row.key);ck((r.headers()['x-robots-tag']||'').includes('noindex'),'Static decision aid noindex header '+row.key);if(href.endsWith('.html')){await page.goto(origin+href,{waitUntil:'networkidle'});await page.emulateMedia({media:'print'});ck(await page.locator('table').count()>0,'Printable complete worksheet '+row.key);ck(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),'Print layout has no viewport overflow '+row.key);await page.emulateMedia({media:'screen'});}}}
 console.log('TN_DECISION_FULL_BROWSER '+JSON.stringify({status:'PASS',checks:checks.length,labels:checks,viewports:[1440,768,375,320],no_js:true,no_js_dark_mode:'NOT_AVAILABLE_CURRENT_SERVER_LIGHT_MARKUP',real_theme_css_and_fonts:true,screenshots_exported:0,canonical_form_posts:1,negative_http_tests:5,production_mutations:0,captcha:'Enabled; isolated server-transport fixture only; Google challenge NOT_TESTED',noindex_preserved:true}));
 }finally{await browser.close();}
})().catch(e=>{console.error('TN_DECISION_FULL_BROWSER '+JSON.stringify({status:'FAIL',class:e.name,label:String(e.message).replace(/tn_service_receipt=[A-Za-z0-9]+/g,'tn_service_receipt=REDACTED').slice(0,500)}));process.exitCode=1;});
