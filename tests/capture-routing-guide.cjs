'use strict';
// Original documentation capture of the real public conceptual tool, not router UI.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto'),{chromium}=require('playwright');
const out=path.resolve(process.argv[2]);assert.ok(!fs.existsSync(out),'New capture directory required');
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true});let writes=0;const shots=[];
try{
 const ctx=await browser.newContext({viewport:{width:1440,height:1000},colorScheme:'light',reducedMotion:'reduce'});
 await ctx.route('**/*',r=>{if(!['GET','HEAD'].includes(r.request().method())){writes++;return r.abort();}return r.request().url().startsWith('https://tehnet.ir/')?r.continue():r.abort();});
 await ctx.addInitScript(()=>localStorage.setItem('tn-theme','light'));const page=await ctx.newPage();await page.goto('https://tehnet.ir/lab/',{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
 const root=page.locator('[data-tn-routing-lab]');assert.equal(await root.getAttribute('data-tn-routing-ready'),'1');assert.equal(await root.count(),1);
 // Wrap the existing controls solely to crop a readable documentation region.
 // No UI text, labels, options, result or model logic is substituted.
 await root.evaluate(el=>{const first=el.querySelector('[data-tn-routing-choice="r1"]').previousElementSibling,last=el.querySelector('[data-tn-routing-next]').parentElement,box=document.createElement('div');box.dataset.guideCapture='';box.style.cssText='padding:16px;';el.insertBefore(box,first);let n=first;while(n){const next=n.nextElementSibling;box.append(n);if(n===last)break;n=next;}});
 await page.addStyleTag({content:'[data-guide-highlight]{outline:4px solid #b45b00!important;outline-offset:4px!important}'});
 fs.mkdirSync(path.join(out,'originals'),{recursive:true});
 async function shot(name,selector,expected){await page.evaluate(()=>document.querySelectorAll('[data-guide-highlight]').forEach(e=>e.removeAttribute('data-guide-highlight')));assert.ok((await root.locator('output').innerText()).includes(expected));const original=path.join(out,'originals',name+'.png');await root.locator('[data-guide-capture]').screenshot({path:original});await root.locator(selector).evaluate(e=>e.setAttribute('data-guide-highlight',''));const file=path.join(out,name+'.png');await root.locator('[data-guide-capture]').screenshot({path:file});const bytes=fs.readFileSync(file);shots.push({file:name+'.png',sha256:crypto.createHash('sha256').update(bytes).digest('hex'),original_sha256:crypto.createHash('sha256').update(fs.readFileSync(original)).digest('hex'),width:bytes.readUInt32BE(16),height:bytes.readUInt32BE(20),highlight_selector:selector});}
 await root.locator('[data-tn-routing-choice="r1"]').selectOption('correct');await root.locator('[data-tn-routing-choice="r2"]').selectOption('missing');await root.locator('[data-tn-routing-check]').click();
 await shot('r1-forward','[data-tn-routing-choice="r1"]','رفت در مدل به سرویس می‌رسد');
 await shot('return-missing','[data-tn-routing-choice="r2"]','روتر R2');
 await root.locator('[data-tn-routing-choice="r2"]').selectOption('correct');await root.locator('[data-tn-routing-check]').click();
 await shot('return-correct','[data-tn-routing-check]','در این مدل درست است');
 await root.locator('[data-tn-routing-direction]').selectOption('return');await root.locator('[data-tn-routing-next]').click();
 assert.equal(await root.locator('[data-tn-routing-node="r2"]').getAttribute('data-visit'),'current');await shot('return-steps','[data-tn-routing-next]','در این مدل درست است');
 assert.equal(writes,0);fs.writeFileSync(path.join(out,'captures.json'),JSON.stringify({schema:1,source_url:'https://tehnet.ir/lab/#static-routing-practice',source_release:'1114367b892364a892263bca26ecd3b08c326c21',observed_utc:new Date().toISOString(),kind:'Actual TehNet conceptual Lab; not RouterOS/GNS3',annotation:'Amber CSS outline on the existing click target; wrapper for crop only; no UI text or result edits',submissions:0,shots},null,2)+'\n');console.log(JSON.stringify({status:'PASS',actual_captures:shots.length,submissions:0}));
 await ctx.close();
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
