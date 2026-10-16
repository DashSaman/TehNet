/* Read-only catalogue photo acceptance. Never submits inquiry/order/payment. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require('C:/Users/amirreza/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'qa/store-2026-10-16');
(async()=>{const b=await chromium.launch({headless:true,channel:'msedge'}),c=await b.newContext({viewport:{width:390,height:844}}),p=await c.newPage(),errors=[],checks=[];
try{
p.on('pageerror',e=>errors.push(e.message));const response=await c.request.get('https://tehnet.ir/wp-json/wc/store/v1/products?per_page=100'),products=await response.json();assert.equal(products.length,25);assert.equal(products.reduce((n,x)=>n+x.images.length,0),30);assert(products.every(x=>x.images.length&&!x.is_purchasable));
checks.push('All 25 products expose 30 native images; no purchasable offer');
await p.goto('https://tehnet.ir/shop/');await p.waitForLoadState('networkidle');assert.equal(await p.locator('.tn-product-photo').count(),16);assert.equal(await p.locator('.tn-product-illustration').count(),0);await p.screenshot({path:path.join(out,'catalog-photos-mobile.png'),fullPage:true});checks.push('All 16 first-page cards use native images and website watermark');
const photoResults=[];
for(const product of products){for(const img of product.images){const r=await c.request.head(img.src);assert.equal(r.status(),200,'image HEAD HTTP 200 '+product.sku);photoResults.push({sku:product.sku,url:img.src,method:'HEAD',http:200});}}
checks.push('All 30 public catalogue image URLs return HEAD HTTP 200; gallery samples separately decode');
for(const sku of ['TN-SN-18002','TN-SN-17929','TN-SN-17989','TN-SN-17824']){
 const product=products.find(x=>x.sku===sku);await p.goto(product.permalink);await p.waitForLoadState('networkidle');const images=p.locator('.woocommerce-product-gallery__image img:not(.zoomImg)');assert.equal(await images.count(),product.images.length);await images.first().evaluate(e=>e.decode());assert(await images.first().isVisible());
 assert.equal(await p.locator('[data-tn-model],[data-tn-spin]').count(),0);assert.equal(await p.locator('button.single_add_to_cart_button').count(),0);assert.equal(await p.locator('.woocommerce-product-gallery .tn-photo-watermark').count(),product.images.length);assert((await p.locator('.tn-photo-note').innerText()).includes('۳۶۰'));assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2));
 await p.screenshot({path:path.join(out,sku+'-mobile.png')});await p.locator('.woocommerce-product-gallery').screenshot({path:path.join(out,sku+'-gallery.png')});checks.push(sku+' native gallery, watermark, honest 360 status, mobile layout');
 if(product.images.length>1){const target=await images.nth(1).getAttribute('src');assert(target!==await images.first().getAttribute('src'));await p.locator('.flex-control-thumbs li').nth(1).click();await p.waitForFunction(src=>{const e=document.querySelector('.flex-active-slide');if(!e||e.querySelector('img:not(.zoomImg)')?.getAttribute('src')!==src)return false;const r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+2;},target);await images.nth(1).evaluate(e=>e.decode());checks.push(sku+' second distinct native gallery image can be selected and decodes');}
 await p.locator('.woocommerce-product-gallery__trigger').click();await p.locator('.pswp--open').waitFor();await p.keyboard.press('Escape');checks.push(sku+' native lightbox opens and closes');
}
assert.deepEqual(errors,[]);fs.writeFileSync(path.join(out,'live-photos-browser.json'),JSON.stringify({status:'passed',utc:new Date().toISOString(),scope:'Read-only production; source catalogue images do not certify photographic origin or exact manufacturer model',products:25,image_references:30,real_360_products:0,checks,images:photoResults,js_errors:errors},null,2));console.log(checks.join('\n'));console.log('LIVE_PHOTOS_BROWSER=PASSED');
}finally{await b.close();}})().catch(e=>{console.error(e.stack);process.exit(1)});
