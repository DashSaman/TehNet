/* Real-photo-first teaching preview; never an exact-product/CAD test. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const {chromium}=require('C:/Users/amirreza/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../..'),out=path.resolve(process.argv[2]);
const base=process.env.TN_DEMO_URL||'http://127.0.0.1:18084';
const checks=[],errors=[],requests=[],responses=[];
const check=(value,name)=>{assert(value,name);checks.push(name)};

(async()=>{
 fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
 page.on('request',r=>requests.push(r.url()));page.on('pageerror',e=>errors.push(e.message));
 page.on('response',r=>{if(r.status()>=400)responses.push({url:r.url(),status:r.status()})});
 try{
  await page.goto(base,{waitUntil:'networkidle'});
  check((await page.locator('.tag').innerText()).includes('مدل هیچ کالای فروشگاه نیست'),'educational identity visible');
  check(await page.locator('#photo-panel').isVisible()&&!await page.locator('#model-panel').isVisible(),'real photograph is default view');
  check(!requests.some(x=>/\.glb|model-viewer.min.js/.test(x)),'model and renderer deferred until explicit click');
  check(await page.locator('#reference-photo').evaluate(i=>i.complete&&i.naturalWidth===670),'initial real photograph decoded');
  const provenance=JSON.parse(fs.readFileSync(path.join(root,'content/media/educational-cable-reference/provenance.json'),'utf8'));
  for(let i=0;i<provenance.files.length;i++){
   const asset=provenance.files[i],response=await page.request.get(base+'/'+asset.file);
   check(crypto.createHash('sha256').update(await response.body()).digest('hex')===asset.sha256,'served original photo unchanged: '+asset.file);
   await page.locator(`[data-photo="${i}"]`).click();
   await page.waitForFunction(width=>{const i=document.getElementById('reference-photo');return i.complete&&i.naturalWidth===width},asset.width);
   check((await page.locator('[data-photo-source]').getAttribute('href'))===asset.page,'source tracks selected photo '+i);
   check((await page.locator('#photo-original').getAttribute('href'))===asset.file,'original download tracks selected photo '+i);
  }
  check((await page.locator('.caption-note').innerText()).includes('دو نمونهٔ متفاوت'),'photos not falsely presented as a 360 sequence');
  await page.locator('[data-photo="0"]').click();
  await page.screenshot({path:path.join(out,'real-photo-desktop.png'),fullPage:true});

  // Exercise switching away while the GLB request is in flight.
  let release;
  const gate=new Promise(resolve=>release=resolve),arrival=page.waitForRequest('**/educational-cable.glb',{timeout:30000});
  await page.route('**/educational-cable.glb',async route=>{await gate;await route.continue()});
  await page.locator('[data-view="model"]').click();await arrival;
  await page.locator('[data-view="photo"]').click();release();
  await page.locator('model-viewer').waitFor({state:'attached'});
  await page.waitForFunction(()=>document.querySelector('model-viewer')?.loaded,null,{timeout:30000});
  check(await page.locator('#photo-panel').isVisible(),'switching away during model load retains photo mode');
  await page.locator('[data-view="model"]').click();
  await page.locator('[data-tn-explode]').waitFor({state:'visible',timeout:30000});
  check(await page.locator('model-viewer').count()===1,'return reuses the existing loaded model');
  check((await page.locator('model-viewer').evaluate(v=>v.alt)).includes('مدل هیچ کالای تهران نتورک نیست'),'model alt does not claim product identity');
  check(await page.locator('[data-tn-part]').count()===5,'five independently explained layers');
  check(await page.locator('model-viewer').evaluate(v=>v.availableAnimations.includes('Explode')),'native five-node animation loaded');
  await page.locator('model-viewer').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(out,'model-assembled-desktop.png'),fullPage:false});
  await page.locator('[data-tn-explode]').click();
  check(await page.locator('model-viewer').evaluate(v=>v.currentTime===v.duration),'reduced-motion explode reaches final pose');
  await page.locator('model-viewer').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(out,'model-exploded-desktop.png'),fullPage:false});
  await page.locator('[data-tn-part="2"]').click();
  check((await page.locator('.tn-part-detail').innerText()).includes('فویل')&&(await page.locator('.tn-part-detail').innerText()).includes('اندازهٔ تأییدشده'),'foil explanation discloses missing measurement');
  check(await page.locator('.tn-part-detail dd').count()===0,'no invented microns or material values');
  await page.locator('[data-tn-explode]').click();
  check(await page.locator('model-viewer').evaluate(v=>v.currentTime===0),'assemble restores original pose');
  await page.locator('[data-tn-explode-range]').fill('50');
  check(await page.locator('model-viewer').evaluate(v=>Math.abs(v.currentTime-v.duration*.5)<.001),'slider sets an intermediate pose');
  await page.locator('[data-tn-explode-range]').fill('0');

  await page.setViewportSize({width:390,height:844});
  await page.locator('[data-view="photo"]').click();
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),'mobile photo mode has no overflow');
  await page.screenshot({path:path.join(out,'real-photo-mobile.png'),fullPage:true});
  await page.locator('[data-view="model"]').click();
  await page.locator('[data-tn-explode]').click();
  await page.locator('model-viewer').scrollIntoViewIfNeeded();
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),'mobile model mode has no overflow');
  await page.screenshot({path:path.join(out,'model-exploded-mobile.png'),fullPage:false});
  await page.locator('[data-view="photo"]').click();await page.locator('[data-view="model"]').click();
  check(await page.locator('[data-tn-explode]').getAttribute('aria-pressed')==='true','mode switch preserves exploded state');
  const viewer=page.locator('model-viewer'),before=await viewer.evaluate(v=>v.getCameraOrbit().theta);
  await page.locator('[data-orbit="right"]').click();
  check(await viewer.evaluate((v,old)=>v.getCameraOrbit().theta>old,before),'rotation control changes actual model camera');

  const normal=await browser.newPage({viewport:{width:1280,height:900},reducedMotion:'no-preference'});
  normal.on('pageerror',e=>errors.push(e.message));
  await normal.goto(base,{waitUntil:'networkidle'});await normal.locator('[data-view="model"]').click();
  await normal.locator('[data-tn-explode]').waitFor({timeout:30000});await normal.locator('[data-tn-explode]').click();
  await normal.waitForFunction(()=>document.querySelector('[data-tn-explode]')?.getAttribute('aria-pressed')==='true',null,{timeout:10000});
  check(await normal.locator('model-viewer').evaluate(v=>v.currentTime===v.duration),'normal-motion animation reaches its final pose');
  await normal.waitForTimeout(250); // Verify the one-shot endpoint holds rather than loops.
  check(await normal.locator('model-viewer').evaluate(v=>v.currentTime===v.duration),'normal-motion final pose remains held');
  await normal.close();
  check(errors.length===0,'no JavaScript errors');
  check(responses.length===0,'no HTTP asset errors');
  check(requests.every(x=>x.startsWith(base)),'all image/model/renderer requests stay local');
  const evidence={status:'passed',scope:'Educational preview only, two independent real photos, original non-dimensional GLB',checks,js_errors:errors,http_errors:responses};
  fs.writeFileSync(path.join(out,'browser.json'),JSON.stringify(evidence,null,2));
  console.log('NATURAL_VISUAL_DEMO_CHECKS='+checks.length+' PASS');
 }finally{await browser.close()}
})().catch(e=>{console.error(e.stack);process.exit(1)});
