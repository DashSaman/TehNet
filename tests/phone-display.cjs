'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');const {chromium}=require('playwright');
const origin=process.env.TN_PHONE_ORIGIN||'http://localhost:18085';const native=origin==='http://localhost:18085';assert.ok(native||origin==='https://tehnet.ir');
const out=path.resolve(process.argv[2]);fs.mkdirSync(out,{recursive:true});const checks=[];const results=[];
const check=(label,v)=>{assert.ok(v,label);checks.push(label);};
async function numbers(p){return p.locator('body').evaluate(root=>{
 const normalize=s=>s.replace(/[۰-۹٠-٩]/g,c=>String('۰۱۲۳۴۵۶۷۸۹'.includes(c)?'۰۱۲۳۴۵۶۷۸۹'.indexOf(c):'٠١٢٣٤٥٦٧٨٩'.indexOf(c)));
 const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);const found=[];let n;
 while(n=walker.nextNode()){
  if(n.parentElement.closest('script,style,noscript,textarea'))continue;
  const at=normalize(n.textContent).indexOf('021-91018746');if(at<0)continue;
  const positions=[...'021-91018746'].map((_,i)=>{const r=document.createRange();r.setStart(n,at+i);r.setEnd(n,at+i+1);return r.getBoundingClientRect();});
  if(!positions[0].width)continue;
  found.push({text:n.textContent.slice(at,at+12),ltr:positions.every((r,i)=>i===0||r.left>positions[i-1].left),nowrap:positions.every(r=>Math.abs(r.top-positions[0].top)<1),href:n.parentElement.closest('a')?.getAttribute('href')||null});
 }return found;
});}
(async()=>{const b=await chromium.launch({channel:'msedge',headless:true,args:native?['--host-resolver-rules=MAP localhost 127.0.0.1']:[]});try{
 const routes=native?['/','/services/','/contact/','/about/','/services/network-tehran/','/services/network-support-tehran/','/services/network-setup-tehran/','/services/mikrotik-tehran/','/services/remote-support/','/shop/','/support/','/b2b/','/learn/','/lab/']:JSON.parse(fs.readFileSync(process.env.TN_PHONE_ROUTES));
 for(const js of [false,true]){
  const c=await b.newContext({viewport:{width:1440,height:1000},javaScriptEnabled:js});await c.route('**/*',r=>['GET','HEAD'].includes(r.request().method())&&r.request().url().startsWith(origin+'/')?r.continue():r.abort());const p=await c.newPage();
  for(const route of routes){
   const response=await p.goto(origin+route,{waitUntil:'networkidle'});check(route+' HTTP200',response.status()===200);
   for(const width of [1440,375]){
    await p.setViewportSize({width,height:900});await p.evaluate(()=>document.fonts.ready);const data=await numbers(p);check(`${route} ${width} JS=${js} business phone exists`,data.length>0);
    check(`${route} ${width} JS=${js} 021 before subscriber digits`,data.every(n=>n.ltr&&n.nowrap));check(`${route} ${width} JS=${js} dial target preserved`,data.every(n=>!n.href||n.href==='tel:+982191018746'));
    results.push({route,width,js,phones:data});
    if(!js&&route==='/services/')await p.locator('.tn-svc-intake>p').last().screenshot({path:path.join(out,`phone-services-${width}.png`)});
    if(!js&&route==='/contact/'&&width===375)await p.locator('.tn-footer-contact').screenshot({path:path.join(out,'phone-footer-375.png')});
   }
  }await c.close();
 }
 if(native){
  const c=await b.newContext({javaScriptEnabled:false,viewport:{width:1024,height:900}});await c.route('**/*',r=>r.abort());const p=await c.newPage();
  for(const type of ['invoice','quote']){await p.setContent(fs.readFileSync(path.join(out,type+'-fixture.html'),'utf8'));const data=await numbers(p);check(type+' actual print template phone geometry',data.length===2&&data.every(n=>n.ltr&&n.nowrap&&n.text==='021-91018746'));await p.emulateMedia({media:'print'});check(type+' print media phone geometry',(await numbers(p)).every(n=>n.ltr&&n.nowrap));await p.locator('.letterhead').screenshot({path:path.join(out,type+'-phone.png')});}await c.close();
 }
 const result={status:'PASS',observed_utc:new Date().toISOString(),checks,passed:checks.length,results,production_submissions:0,scope:native?'Isolated native WordPress and synthetic print renderer; no stored document created':'Public read-only pages; no form submitted'};fs.writeFileSync(path.join(out,'phone-browser.json'),JSON.stringify(result,null,2));fs.writeFileSync(path.join(out,'browser.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({status:'PASS',checks:checks.length,routes:routes.length,production_submissions:0}));
}finally{await b.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
