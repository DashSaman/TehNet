'use strict';
// Read-only browser verification of the improved /services/network-setup-tehran/
// on the isolated staging preview. Usage: node service-setup-buyer-readonly.cjs [BASE] [OUTDIR]
const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path');
const BASE=process.argv[2]||'http://localhost:18085';
const OUT=process.argv[3]||path.join(__dirname,'..','docs','evidence','2026-11-13','service-setup-buyer');
const PAGE='/services/network-setup-tehran/';
const SECTIONS=['فرایند کار از درخواست تا تحویل','تحویل‌دادنی‌های پایه پروژه','مرزهای خدمت','بعد از راه‌اندازی','چرا تهران نتورک','درخواست بررسی پروژه'];
const INTERNAL=['/contact/','/technical-methodology/','/services/network-support-tehran/','/services/remote-support/','/learn/mikrotik/mtcna/'];
const checks=[];let fail=0;
function check(n,pass,detail){fail+=pass?0:1;checks.push({name:n,pass,detail});}
if(!fs.existsSync(OUT))fs.mkdirSync(OUT,{recursive:true});
(async()=>{
  const browser=await chromium.launch({headless:true});
  // Desktop verification
  {
    const ctx=await browser.newContext({viewport:{width:1440,height:900},locale:'fa'});
    const page=await ctx.newPage();
    const errors=[];
    page.on('console',m=>{if(m.type()==='error'&&!m.text().includes('favicon'))errors.push(m.text().slice(0,120))});
    const resp=await page.goto(BASE+PAGE,{waitUntil:'networkidle',timeout:30000});
    check('http_200',resp.status()===200,{status:resp.status()});
    const text=await page.evaluate(()=>document.body.innerText);
    for(const s of SECTIONS)check('section_'+s.slice(0,12),text.includes(s));
    check('phone_shortcode_replaced',!text.includes('[tehnet_phone]'));
    check('inquiry_cta_contact_link',await page.evaluate(()=>!!document.querySelector('.tn-entry-content a[href="/contact/"], article a[href="/contact/"], main a[href="/contact/"]')));
    check('no_console_errors',errors.length===0,{errors:errors.slice(0,3)});
    // internal links resolve
    for(const link of INTERNAL){
      const r=await page.request.get(BASE+link,{maxRedirects:0});
      check('link_'+link+'_'+r.status(),r.status()===200||r.status()===(link==='/contact/'?200:301));
      if(r.status()!==200){const r2=await page.request.get(BASE+link,{maxRedirects:3});check('link_follow_'+link,r2.status()===200,{final:r2.status()});}
    }
    await page.screenshot({path:path.join(OUT,'desktop-1440.png'),fullPage:true});
    await ctx.close();
  }
  // Mobile verification
  {
    const ctx=await browser.newContext({viewport:{width:375,height:667},locale:'fa'});
    const page=await ctx.newPage();
    await page.goto(BASE+PAGE,{waitUntil:'networkidle',timeout:30000});
    const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
    check('mobile_no_horizontal_overflow',overflow<=0,{px:overflow});
    const lead=await page.evaluate(()=>{const el=document.querySelector('.tn-lead');return el?getComputedStyle(el).fontSize:null;});
    check('lead_paragraph_rendered',!!lead);
    await page.screenshot({path:path.join(OUT,'mobile-375.png'),fullPage:true});
    await ctx.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(OUT,'service-setup-buyer-browser.json'),
    JSON.stringify({base:BASE,page:PAGE,status:fail?'FAIL':'PASS',total:checks.length,failures:fail,checks},null,1));
  console.log(`SERVICE-SETUP-BUYER BROWSER VERIFY | RESULT: ${fail?'FAIL':'PASS'} | checks=${checks.length} failures=${fail}`);
  for(const c of checks.filter(c=>!c.pass))console.log('  FAIL:',c.name,JSON.stringify(c.detail||{}).slice(0,120));
  process.exitCode=fail?1:0;
})();
