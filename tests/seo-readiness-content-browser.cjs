'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const root=process.argv[2],browser=await chromium.launch({headless:true});let checks=0;const labels=[];
 const check=(v,s)=>{assert.ok(v,s);checks++;labels.push(s);};
 const css=['site/themes/tehnet/style.css','site/themes/tehnet/assets/css/visual-refresh.css','site/themes/tehnet/assets/css/service-catalog.css'].map(p=>fs.readFileSync(p,'utf8').replace(/<\/style/gi,'')).join('\n');
 try{
 for(const width of [1440,768,375,320])for(const dark of [false,true])for(const javaScriptEnabled of [true,false])for(const id of [8,29]){
  const context=await browser.newContext({viewport:{width,height:900},javaScriptEnabled,colorScheme:dark?'dark':'light'});
  await context.route('**/*',r=>r.abort());const page=await context.newPage();
  const html=fs.readFileSync(path.join(root,'owner-'+id+'.html'),'utf8');
  await page.setContent('<!doctype html><html lang="fa" dir="rtl" data-theme="'+(dark?'dark':'light')+'"><head><meta charset="utf-8"><style>'+css+'</style><style>body{margin:0}main{padding:16px;max-width:1200px;margin:auto;box-sizing:border-box}a{overflow-wrap:anywhere}</style></head><body><main class="entry-content">'+html+'</main></body></html>');
  const key=id+'/'+width+'/'+dark+'/'+javaScriptEnabled;
  check(await page.locator('html').getAttribute('dir')==='rtl',key+' RTL');
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),key+' no horizontal overflow');
  if(id===8){
   check(await page.locator('form').count()===1,key+' exactly existing form');
   for(const dest of ['/services/mikrotik-tehran/#firewall-acceptance','/services/network-support-tehran/#monitoring-acceptance'])check(await page.locator('a[href="'+dest+'"]').count()===1,key+' deep link '+dest);
  }else{
   check(await page.locator('a[href="/services/?tn_service_context=general-network#service-request"]').count()===1,key+' canonical request CTA');
   check(await page.locator('a[href="https://mytel.one/services/"]').count()===1,key+' MyTel specialist link');
  }
  await context.close();
 }
 console.log('TN_SEO_CONTENT_BROWSER '+JSON.stringify({status:'PASS',checks,labels,viewports:[1440,768,375,320],light_dark:true,no_js:true,scope:'Native rendered content components with source CSS; not full WordPress frontend or font/CAPTCHA integration',all_external_requests_blocked:true,submissions:0,production_mutations:0,screenshots_exported:0}));
 }finally{await browser.close();}
})().catch(e=>{console.error('TN_SEO_CONTENT_BROWSER '+JSON.stringify({status:'FAIL',name:e.name,label:String(e.message).slice(0,250)}));process.exitCode=1;});
