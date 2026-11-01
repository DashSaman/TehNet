const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const base=process.argv[2],out=process.argv[3];
const hubs=['/learn/','/lab/','/learn/mikrotik/','/learn/mikrotik/mtcna/'];
const lessons=['/learn/mikrotik/mtcna/routeros-winbox/','/learn/mikrotik/mtcna/static-routing/','/learn/mikrotik/mtcna/ip-dhcp-dns/','/lab/voice-network-checklist/'];
const services=['/services/','/services/network-tehran/','/services/network-support-tehran/','/services/network-setup-tehran/','/services/mikrotik-tehran/','/services/remote-support/','/services/voice-network-readiness/'];
(async()=>{
 assert(base==='https://tehnet.ir'||base==='http://localhost:18085'&&process.env.TN_NATIVE_PREVIEW_ISOLATED==='1');
 const browser=await chromium.launch({channel:'msedge',headless:true}),rows=[],methods=new Set(),blocked=new Set(),errors=[];let checks=0;
 const check=(value,label)=>{assert(value,label);++checks};
 try{
  for(const [width,javascript] of [[1440,true],[375,true],[375,false]]){
   const context=await browser.newContext({viewport:{width,height:850},javaScriptEnabled:javascript});
   await context.route('**/*',handler=>{
    const request=handler.request(),url=new URL(request.url());methods.add(request.method());
    if(!['GET','HEAD'].includes(request.method()))return handler.abort();
    if(url.origin!==base&&!['data:','blob:'].includes(url.protocol)){blocked.add(url.origin);return handler.abort()}
    return handler.continue();
   });
   const page=await context.newPage();page.on('pageerror',e=>errors.push(e.message));
   for(const route of [...hubs,...lessons,...services,'/','/shop/']){
    const response=await page.goto(base+route,{waitUntil:'networkidle'});
    check(response.status()===200,'HTTP200 '+route);
    check(await page.locator('h1').count()===1,'One H1 '+route);
    check(await page.locator('link[rel="canonical"]').getAttribute('href')===base+route,'Original canonical '+route);
    check((await page.locator('meta[name="robots"]').getAttribute('content')).includes('noindex'),'Noindex preserved '+route);
    check(await page.locator('meta[name="description"]').count()===1,'Description retained '+route);
    const article=await page.locator('script.tehnet-article-schema').count();
    check(article===(lessons.includes(route)?1:0),'Article matches page role '+route);
    check(await page.evaluate(()=>document.documentElement.scrollWidth===innerWidth),'No horizontal overflow '+route);
    if(hubs.includes(route)||lessons.includes(route)||route==='/services/voice-network-readiness/')check(await page.locator('.tn-editorial-note').count()===1,'Visible editorial note retained '+route);
    rows.push({route,width,javascript,status:response.status(),articles:article,overflow:false});
   }
   await context.close();
  }
  check(errors.length===0,'No page errors');check([...methods].every(m=>['GET','HEAD'].includes(m)),'No state-changing requests');
  const receipt={status:'PASS',method:'Native/public service-page-role acceptance, real browser with normal TLS when HTTPS',checks,observations:rows,page_errors:errors,blocked_external_origins:blocked.size,methods:[...methods],form_submissions:0,limits:['Functional acceptance, not a Google rich-result/URL Inspection/SEO measurement']};
  fs.writeFileSync(path.join(out,'service-metadata-role-browser.json'),JSON.stringify(receipt,null,2));console.log(JSON.stringify({status:'PASS',checks,observations:rows.length,form_submissions:0}));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
