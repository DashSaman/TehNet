/* Synthetic sequence UI test. These images never enter the catalogue. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),{execFileSync}=require('child_process');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'qa/store-2026-10-16');fs.mkdirSync(out,{recursive:true});
const fixture=path.join(out,'spin-test-fixture.html');
execFileSync(path.resolve(root,'../php-runtime/php.exe'),[path.join(root,'tests/product-photos-unit.php'),fixture]);
(async()=>{const b=await chromium.launch({headless:true,channel:'msedge'}),c=await b.newContext({viewport:{width:390,height:844}}),p=await c.newPage(),requested=[],errors=[];
try{
p.on('pageerror',e=>errors.push(e.message));await c.route('https://photo-fixture.invalid/**',async r=>{requested.push(r.request().url());const home=new URL(r.request().url()).pathname==='/';await r.fulfill({status:200,contentType:home?'text/html':'image/svg+xml',body:home?'<html><body></body></html>':'<svg xmlns="http://www.w3.org/2000/svg" width="640" height="640"><rect width="640" height="640" fill="#225577"/></svg>'});});
await p.goto('https://photo-fixture.invalid/');await p.setContent('<html dir="rtl"><head><style>'+fs.readFileSync(path.join(root,'site/plugins/tehnet-store/assets/store.css'),'utf8')+'</style></head><body>'+fs.readFileSync(fixture,'utf8')+'</body></html>');
requested.length=0;await p.addScriptTag({path:path.join(root,'site/plugins/tehnet-store/assets/photo-spin.js')});assert.equal(requested.length,0,'sequence stays lazy before request');
await p.locator('[data-tn-spin-load]').click();const img=p.locator('[data-tn-spin-stage] img');await img.evaluate(e=>e.decode());assert.equal(await img.getAttribute('data-frame'),'0');
await img.focus();await p.keyboard.press('ArrowRight');assert.equal(await img.getAttribute('data-frame'),'1');await p.keyboard.press('Home');assert.equal(await img.getAttribute('data-frame'),'0');await p.keyboard.press('ArrowLeft');assert.equal(await img.getAttribute('data-frame'),'11');
await p.locator('[data-tn-spin-range]').fill('6');await p.locator('[data-tn-spin-range]').dispatchEvent('input');assert.equal(await img.getAttribute('data-frame'),'6');await p.locator('[data-tn-spin-next]').click();assert.equal(await img.getAttribute('data-frame'),'7');
const box=await img.boundingBox();await p.mouse.move(box.x+box.width/2,box.y+box.height/2);await p.mouse.down();await p.mouse.move(box.x+box.width/2+40,box.y+box.height/2);await p.mouse.up();assert.equal(await img.getAttribute('data-frame'),'9');
assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2));assert.equal(await p.locator('.tn-photo-watermark').innerText(),'tehnet.ir');assert.deepEqual(errors,[]);
fs.writeFileSync(path.join(out,'spin-browser.json'),JSON.stringify({status:'passed',utc:new Date().toISOString(),scope:'Synthetic browser sequence only; no real catalogue spin frames exist',lazy:true,keyboard:true,wrap:true,range:true,buttons:true,drag:true,mobile_no_overflow:true,js_errors:errors},null,2));console.log('PHOTO_SPIN_BROWSER=PASSED');
}finally{await b.close();fs.unlinkSync(fixture);}})().catch(e=>{console.error(e.stack);process.exit(1)});
