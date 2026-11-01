'use strict';
// Public verification never submits a form or allows a non-read request.
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');const {chromium}=require('playwright');
const out=path.resolve(process.argv[2]);fs.mkdirSync(out,{recursive:true});const checks=[];let writes=0;const check=(label,v)=>{assert.ok(v,label);checks.push(label);};
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});try{
 const c=await browser.newContext({viewport:{width:1440,height:1000}});await c.route('**/*',r=>{if(!['GET','HEAD'].includes(r.request().method())){writes++;return r.abort();}return new URL(r.request().url()).origin==='https://tehnet.ir'?r.continue():r.abort();});const p=await c.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
 for(const route of ['/services/','/']){
  const response=await p.goto('https://tehnet.ir'+route,{waitUntil:'networkidle'});check(route+' HTTP200',response.status()===200);await p.evaluate(()=>document.fonts.ready);
  check(route+' local Estedad loaded',await p.evaluate(()=>[...document.fonts].some(f=>f.family==='Estedad'&&f.status==='loaded')));
  check(route+' intentional noindex retained',(await p.locator('meta[name=robots]').getAttribute('content')).includes('noindex'));
  check(route+' corporate light default',await p.locator('html').getAttribute('data-theme')==='light');
  check(route+' footer personal link removed',await p.locator('footer a[href$="/amirreza-golavar/"]').count()===0);
  check(route+' one canonical request form',await p.locator('[data-tn-service-request]').count()===1&&await p.locator('[data-tn-service-request] input[name=_wpnonce]').count()===1);
  check(route+' Google CAPTCHA honestly inactive',await p.locator('[data-tn-recaptcha],script[src*="recaptcha"]').count()===0);
  check(route+' navigation text at least15px',await p.locator('.tn-site-nav>ul>li>a').evaluateAll(es=>es.every(e=>parseFloat(getComputedStyle(e).fontSize)>=15)));
  await p.getByRole('button',{name:'زیرمنوی خدمات',exact:true}).click();check(route+' tunnel nested under Services and visible',await p.locator('.tn-site-nav .is-submenu-open>ul.sub-menu a[href$="/tunnels/"]').isVisible());await p.keyboard.press('Escape');
  if(route==='/services/'){
   const tops=await p.locator('.tn-svc-step').evaluateAll(es=>es.map(e=>e.getBoundingClientRect().top));check('Workflow aligned within1px',tops.length===4&&Math.max(...tops)-Math.min(...tops)<1);
   check('MyTel specialist referral retained',await p.locator('main a[href="https://mytel.one/services/"]').count()>0);await p.locator('.tn-svc-process').screenshot({path:path.join(out,'live-workflow-1440.png')});await p.locator('.tn-site-header').screenshot({path:path.join(out,'live-header-1440.png')});
  }
  await p.screenshot({path:path.join(out,route==='/'?'live-home-1440.png':'live-services-1440.png')});
  for(const width of [320,375,768,1024,1280,1440]){await p.setViewportSize({width,height:900});check(route+' no overflow at'+width,await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));if(width===375){await p.locator('.tn-menu-toggle').click();await p.getByRole('button',{name:'زیرمنوی خدمات',exact:true}).click();check(route+' mobile tunnel visible',await p.locator('.tn-site-nav .is-submenu-open>ul.sub-menu a[href$="/tunnels/"]').isVisible());await p.screenshot({path:path.join(out,route==='/'?'live-home-menu-375.png':'live-services-menu-375.png')});await p.locator('.tn-menu-toggle').click();await p.screenshot({path:path.join(out,route==='/'?'live-home-375.png':'live-services-375.png')});}}
 }
 check('No production write request attempted',writes===0);check('No uncaught UI errors',errors.length===0);
 fs.writeFileSync(path.join(out,'public-browser.json'),JSON.stringify({status:'PASS',observed_utc:new Date().toISOString(),checks,passed:checks.length,production_writes:writes},null,2));console.log(JSON.stringify({status:'PASS',checks:checks.length,production_writes:writes}));await c.close();
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
