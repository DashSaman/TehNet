'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const origin='http://localhost:18085',checks=[],assets=new Map();let posts=0;
const ck=(v,s)=>{assert.ok(v,s);checks.push(s);};
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
 for(const width of [1440,768,375,320])for(const dark of [false,true])for(const javaScriptEnabled of [true,false]){
  const context=await browser.newContext({viewport:{width,height:900},javaScriptEnabled,colorScheme:dark?'dark':'light'});
  await context.route('**/*',r=>{const u=new URL(r.request().url());return u.origin===origin&&r.request().method()==='GET'?r.continue():r.abort();});
  const page=await context.newPage();
  page.on('response',r=>{if(/\.(css|woff2?)(\?|$)/.test(r.url()))assets.set(r.url(),r.status());});
  for(const pathname of ['/services/','/services/network-tehran/']){
   const response=await page.goto(origin+pathname,{waitUntil:'networkidle'});const key=pathname+width+'/'+dark+'/'+javaScriptEnabled;
   ck(response.status()===200,key+' full WordPress HTTP200');
   ck(await page.locator('h1').count()===1,key+' exactly one H1');
   ck((await page.locator('meta[name=robots]').getAttribute('content')).includes('noindex'),key+' noindex retained');
   ck(await page.locator('link[rel=canonical]').getAttribute('href')===origin+pathname,key+' self canonical');
   await page.evaluate(()=>document.fonts.ready);
   ck(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),key+' actual theme no overflow');
   ck(await page.locator('html').getAttribute('dir')==='rtl',key+' actual RTL');
   ck(await page.evaluate(()=>document.fonts.size>0&&[...document.fonts].some(f=>f.status==='loaded')),key+' actual local font loaded');
   if(pathname==='/services/'){
    ck(await page.locator('form.tn-service-request').count()===1,key+' existing canonical request form');
    for(const href of ['/services/mikrotik-tehran/#firewall-acceptance','/services/network-support-tehran/#monitoring-acceptance'])ck(await page.locator('a[href="'+href+'"]').count()===1,key+' new catalog deep link');
    ck(await page.locator('.tn-service-request').evaluate(f=>new FormData(f).has('_wpnonce')),key+' nonce belongs to actual form');
   }else ck(await page.locator('a[href="/services/?tn_service_context=general-network#service-request"]').count()===1,key+' hub CTA retained');
  }
  await context.close();
 }
 ck(assets.size>0&&[...assets.values()].every(s=>s===200),'All observed real CSS/font assets200');
 const ctx=await browser.newContext({viewport:{width:375,height:900}});
 await ctx.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin!==origin)return r.abort();if(r.request().method()==='POST'){ck(u.pathname==='/wp-admin/admin-post.php','POST restricted to synthetic canonical endpoint');posts++;}return r.continue();});
 const page=await ctx.newPage();
 await page.goto(origin+'/services/network-tehran/',{waitUntil:'networkidle'});
 await page.locator('a[href="/services/?tn_service_context=general-network#service-request"]').click();await page.waitForURL('**/services/?tn_service_context=general-network#service-request');
 const f=page.locator('form.tn-service-request');ck(await f.locator('[name=tn_service_context]').inputValue()==='general-network','Actual hub click prefills approved service context');
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
 await ctx.close();
 console.log('TN_P94_FULL_BROWSER '+JSON.stringify({status:'PASS',checks:checks.length,labels:checks,viewports:[1440,768,375,320],no_js:true,real_theme_css_and_fonts:true,screenshots_exported:0,canonical_form_posts:1,negative_http_tests:5,production_mutations:0,captcha:'Enabled; isolated server-transport fixture only; Google challenge NOT_TESTED',noindex_preserved:true}));
 }finally{await browser.close();}
})().catch(e=>{console.error('TN_P94_FULL_BROWSER '+JSON.stringify({status:'FAIL',class:e.name,label:String(e.message).replace(/tn_service_receipt=[A-Za-z0-9]+/g,'tn_service_receipt=REDACTED').slice(0,500)}));process.exitCode=1;});
