/* Real browser DOM component test with synthetic thumbnails; not native Woo integration. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const out=process.argv[2],root=path.resolve(__dirname,'../..'),source=fs.readFileSync(path.join(root,'site/plugins/tehnet-store/assets/product-gallery.js'),'utf8');
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true}),page=await browser.newPage(),checks=[];const check=(v,n)=>{assert(v,n);checks.push(n)};
try{
 await page.route('**/*',r=>r.abort());
 await page.setContent('<main><div class="woocommerce-product-gallery" id="one"></div><div class="woocommerce-product-gallery" id="two"><ol class="flex-control-thumbs"><li><a href="#existing"><img alt="Already linked"></a></li></ol></div><form><button type="submit">Unrelated submit</button></form></main>');
 await page.addScriptTag({content:source});
 await page.evaluate(()=>{
  window.clicks=0;window.submits=0;document.querySelector('form').addEventListener('submit',e=>{e.preventDefault();++window.submits});
  for(const [id,count] of [['one',3],['two',2]]){
   const gallery=document.getElementById(id),list=gallery.querySelector('ol')||gallery.appendChild(document.createElement('ol'));list.className='flex-control-thumbs';
   for(let i=0;i<count;i++){
    const li=document.createElement('li'),image=document.createElement('img');image.alt='Synthetic thumbnail '+i;image.dataset.fixture='yes';if(i===0)image.className='flex-active';
    image.addEventListener('click',()=>{++window.clicks;list.querySelectorAll('img[data-fixture]').forEach(e=>e.classList.toggle('flex-active',e===image))});li.append(image);list.append(li);
   }
  }
 });
 await page.waitForFunction(()=>document.querySelectorAll('button.tn-gallery-thumb').length===5);
 check(await page.locator('#one .tn-gallery-thumb').count()===3,'Delayed native-style thumbnails enhanced');
 check(await page.locator('#two a[href="#existing"] .tn-gallery-thumb').count()===0,'Already linked image left untouched');
 const one=page.locator('#one .tn-gallery-thumb'),two=page.locator('#two .tn-gallery-thumb');
 check(await one.nth(1).getAttribute('aria-label')==='نمایش تصویر ۲ از ۳','Stable Persian position label');
 await one.nth(1).focus();await page.keyboard.press('Enter');
 check(await page.evaluate(()=>clicks)===1,'Enter bridges exactly one original image click');
 check(await one.nth(1).getAttribute('aria-current')==='true'&&await two.first().getAttribute('aria-current')==='true','Current state scoped to each gallery');
 check(await one.nth(1).evaluate(e=>e===document.activeElement),'Enter retains focus');
 await one.nth(2).focus();await page.keyboard.press('Space');check(await page.evaluate(()=>clicks)===2,'Space uses native button activation exactly once');
 await one.first().locator('img').click();check(await page.evaluate(()=>clicks)===3,'Image-origin pointer click is not doubled');
 await one.nth(1).click();check(await page.evaluate(()=>clicks)===4,'Button-origin pointer click is not doubled');
 await page.addScriptTag({content:source});await page.waitForFunction(()=>document.querySelectorAll('button.tn-gallery-thumb').length===5);
 check(await page.locator('.tn-gallery-thumb .tn-gallery-thumb').count()===0,'Repeated enhancement never nests controls');
 await one.nth(1).focus();await page.keyboard.press('Enter');check(await page.evaluate(()=>clicks)===5,'Repeated enhancement never duplicates click bridge');
 check(await page.evaluate(()=>submits)===0,'No form submission');
 check(await page.locator('img[alt^="Synthetic thumbnail"]').count()===5,'Original fixture image/alt nodes retained');
 const receipt={status:'PASS',checks,method:'Offline real-browser component with synthetic DOM and original module;not native WordPress/FlexSlider acceptance'};
 fs.writeFileSync(path.join(out,'gallery-keyboard-component.json'),JSON.stringify(receipt,null,2));console.log(JSON.stringify({status:'PASS',checks:checks.length}));
}finally{await browser.close()}})().catch(e=>{console.error(e.stack);process.exitCode=1});
