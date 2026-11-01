'use strict';
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const {chromium}=require('playwright');
const origin=process.env.TN_NATIVE_PREVIEW_URL;assert.equal(process.env.TN_NATIVE_PREVIEW_ISOLATED,'1');assert.equal(origin,'http://localhost:18085');
const out=path.resolve(process.argv[2]);const checks=[];const check=(label,value)=>{assert.ok(value,label);checks.push(label);};
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true,args:['--host-resolver-rules=MAP localhost 127.0.0.1']});
 try{
  const c=await browser.newContext({viewport:{width:1440,height:1000}});
  const external=[];await c.route('**/*',r=>r.request().url().startsWith(origin+'/')?r.continue():(external.push(r.request().url()),r.abort()));
  const p=await c.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(origin+'/services/',{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);
  check('Estedad variable font actually loaded',await p.evaluate(()=>[...document.fonts].some(f=>f.family==='Estedad'&&f.status==='loaded')));
  check('Default corporate light theme',await p.locator('html').getAttribute('data-theme')==='light');
  check('Personal resume removed only from footer',await p.locator('footer a[href$="/amirreza-golavar/"]').count()===0);
  check('Menu text is at least15px',await p.locator('.tn-site-nav>ul>li>a').evaluateAll(a=>a.every(e=>parseFloat(getComputedStyle(e).fontSize)>=15)));
  const root=await p.locator('.tn-site-nav>ul>li>a').allTextContents();
  check('Seven organized primary destinations',root.map(s=>s.trim()).join('|')==='خانه|خدمات|آموزش|آزمایشگاه|فروشگاه|مجله شبکه|درباره ما');
  const service=p.getByRole('button',{name:'زیرمنوی خدمات',exact:true});
  await service.focus();await p.keyboard.press('Enter');
  check('Keyboard opens Services disclosure',await service.getAttribute('aria-expanded')==='true');
  check('Tunnel is an actual Services child',await p.locator('.tn-site-nav li.is-submenu-open>ul.sub-menu a[href$="/tunnels/"]').isVisible());
  await p.keyboard.press('Escape');check('Escape closes submenu and restores focus',await service.getAttribute('aria-expanded')==='false'&&await service.evaluate(e=>e===document.activeElement));
  const tops=await p.locator('.tn-svc-step').evaluateAll(es=>es.map(e=>e.getBoundingClientRect().top));
  check('Four workflow cards aligned within1px',tops.length===4&&Math.max(...tops)-Math.min(...tops)<1);
  await p.locator('.tn-site-header').screenshot({path:path.join(out,'after-header-1440.png')});
  await p.locator('.tn-svc-process').screenshot({path:path.join(out,'after-workflow-1440.png')});
  await p.screenshot({path:path.join(out,'after-services-1440.png'),fullPage:true});
  await p.locator('.tn-theme-toggle').click();check('Dark theme remains usable',await p.locator('html').getAttribute('data-theme')==='dark');
  await p.locator('.tn-svc-process').screenshot({path:path.join(out,'after-workflow-dark-1440.png')});
  await p.reload({waitUntil:'networkidle'});check('Saved dark preference survives reload',await p.locator('html').getAttribute('data-theme')==='dark');await p.locator('.tn-theme-toggle').click();
  for(const width of [320,375,768,1024,1280,1440]){
   await p.setViewportSize({width,height:900});
   check('No horizontal overflow at'+width,await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   if(width<=1050){const toggle=p.locator('.tn-menu-toggle');await toggle.click();check('Touch menu opens at'+width,await toggle.getAttribute('aria-expanded')==='true');await service.click();check('Mobile Services child visible at'+width,await p.locator('.tn-site-nav .sub-menu a[href$="/tunnels/"]').isVisible());await p.keyboard.press('Escape');await toggle.click();}
   if(width===375)await p.screenshot({path:path.join(out,'after-services-375.png'),fullPage:true});
  }
  await p.setViewportSize({width:1440,height:1000});await p.goto(origin+'/',{waitUntil:'networkidle'});await p.screenshot({path:path.join(out,'after-home-1440.png'),fullPage:true});
  check('No Google traffic while CAPTCHA inactive',external.every(u=>!u.includes('google.com/recaptcha')));check('No customer UI JavaScript errors',errors.length===0);await c.close();
  const n=await browser.newContext({javaScriptEnabled:false,viewport:{width:375,height:812}});await n.route('**/*',r=>r.request().url().startsWith(origin+'/')?r.continue():r.abort());const np=await n.newPage();await np.goto(origin+'/services/',{waitUntil:'networkidle'});
  check('No-JS navigation exposes nested tunnel link',await np.locator('.tn-site-nav a[href$="/tunnels/"]').isVisible());check('No-JS mobile page has no horizontal overflow',await np.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await np.locator('.tn-site-header').screenshot({path:path.join(out,'after-nojs-header-375.png')});await n.close();
 }finally{await browser.close();}
 fs.writeFileSync(path.join(out,'corporate-browser.json'),JSON.stringify({status:'PASS',checks,passed:checks.length},null,2));
 const q=require('node:child_process').spawnSync(process.execPath,[path.join(__dirname,'commercial-service-journey.cjs'),out],{stdio:'inherit',env:process.env});assert.equal(q.status,0,'Existing native service journey');
 const result=JSON.parse(fs.readFileSync(path.join(out,'browser.json')));result.corporate_checks=checks;result.passed+=checks.length;fs.writeFileSync(path.join(out,'browser.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify({status:'PASS',corporate_checks:checks.length,total_checks:result.passed}));
})().catch(e=>{console.error(e);process.exitCode=1;});
