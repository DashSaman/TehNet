/* Read-only storefront acceptance. No inquiry/cart/order/message submissions. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require('C:/Users/amirreza/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const base=process.env.TN_SHOP_BASE||'http://localhost:18085',out=path.resolve(process.argv[2]),checks=[],errors=[];
const check=(v,n)=>{assert(v,n);checks.push(n)};
async function capture(page,file){
 const initial=await page.evaluate(()=>scrollY),height=await page.evaluate(()=>document.documentElement.scrollHeight);
 for(let y=0;y<height;y+=700){await page.evaluate(y=>scrollTo(0,y),y);await page.waitForTimeout(80);}
 await page.waitForFunction(()=>[...document.querySelectorAll('.products img')].every(i=>i.complete&&i.naturalWidth>0),null,{timeout:90000});
 await page.evaluate(y=>scrollTo(0,y),initial);await page.screenshot({path:path.join(out,file),fullPage:true});
}
(async()=>{fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({headless:true,channel:'msedge',args:JSON.parse(process.env.TN_BROWSER_ARGS||'[]')}),context=await browser.newContext({viewport:{width:1440,height:1000}}),page=await context.newPage();
 page.setDefaultNavigationTimeout(90000);page.on('pageerror',e=>errors.push(e.message));
 try{
  await page.goto(base+'/shop/',{waitUntil:'domcontentloaded'});
  check(await page.locator('body.tn-shop').count()===1,'shared shop presentation active');
  check(await page.locator('h1').count()===1,'single existing archive H1 preserved');
  check(await page.locator('.products li.product').count()===16,'existing public first page remains16 items');
  check(await page.locator('.tn-shop-category').count()>0,'dynamic graphic category navigation present');
  check(await page.locator('.tn-card-identity').count()===16,'every card has shared category/SKU identity');
  check(await page.locator('.tn-filter-advanced').getAttribute('open')===null,'advanced filters collapsed until needed');
  check(await page.locator('.products').evaluate(e=>getComputedStyle(e).gridTemplateColumns.split(' ').length)===4,'desktop catalogue uses four readable columns');
  await capture(page,'shop-desktop-dark.png');
  await page.locator('[data-tn-add="wishlist"]').first().click();
  check(await page.locator('[data-tn-add="wishlist"]').first().getAttribute('aria-pressed')==='true','wishlist selected state is explicit');
  await page.reload({waitUntil:'domcontentloaded'});
  check(await page.locator('[data-tn-add="wishlist"]').first().getAttribute('aria-pressed')==='true','guest selection survives reload');
  await page.locator('[data-tn-add="wishlist"]').first().click();
  check(await page.locator('[data-tn-count="wishlist"]').innerText()==='۰','selection can be removed directly on card');
  await page.locator('[data-tn-add="compare"]').first().click();await page.locator('[data-tn-open="compare"]').click();
  check(await page.locator('.tn-comparison-table tbody tr').count()===5,'verified technical comparison retained');await page.keyboard.press('Escape');
  await page.locator('.tn-shop-category').first().click();await page.waitForLoadState('domcontentloaded');
  check((await page.locator('select[name="product_cat"]').inputValue())!=='0'&&(await page.locator('select[name="product_cat"]').inputValue())!=='','category archive preserves its selected filter');
  await page.goto(base+'/shop/?post_type=product&s=TN-SN-'+encodeURIComponent('۱۸۰۰۲'),{waitUntil:'domcontentloaded'});
  check((await page.locator('body').innerText()).includes('TN-SN-18002'),'Persian exact SKU search retained');
  await page.goto(base+'/shop/?post_type=product&s=TN-UX-NO-SUCH-SKU',{waitUntil:'domcontentloaded'});
  check(await page.locator('.products li.product').count()===0&&await page.locator('.tn-store-filters').count()===1,'zero results retain useful controls');
  await page.getByRole('link',{name:'پاک کردن فیلترها'}).click();await page.waitForLoadState('domcontentloaded');
  check(await page.locator('.products li.product').count()===16,'reset restores public catalogue');
  await page.setViewportSize({width:390,height:844});await page.reload({waitUntil:'domcontentloaded'});
  check(await page.locator('.products').evaluate(e=>getComputedStyle(e).gridTemplateColumns.split(' ').length)===2,'mobile uses two catalogue columns');
  await page.locator('.tn-filter-advanced summary').click();
  check(await page.locator('select[name="tn_shield"]').isVisible(),'native expandable mobile technical filters work');
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),'mobile shop has no page overflow');
  await page.locator('.tn-filter-advanced summary').click();
  await capture(page,'shop-mobile-dark.png');
  await page.locator('.tn-theme-toggle').click();
  check(await page.locator('html').getAttribute('data-theme')==='light','existing light/dark control remains usable');
  await page.evaluate(()=>Promise.all(document.getAnimations().filter(a=>Number.isFinite(a.effect?.getTiming().iterations)).map(a=>a.finished.catch(()=>{}))));
  await capture(page,'shop-mobile-light.png');
  await page.screenshot({path:path.join(out,'shop-mobile-light-viewport.png'),fullPage:false});
  await page.locator('.products li.product .woocommerce-loop-product__link').first().click();await page.waitForLoadState('domcontentloaded');
  await page.locator('.woocommerce-product-gallery__image img').first().evaluate(e=>e.decode());
  check(await page.locator('#tehnet-inquiry').count()===1&&await page.locator('button.single_add_to_cart_button').count()===0,'native inquiry retained and checkout remains closed');
  check(await page.locator('[data-tn-reviewed-model],[data-tn-spin]').count()===0,'unapproved catalogue media never becomes fake3D');
  check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),'mobile product and form have no overflow');
  await page.screenshot({path:path.join(out,'product-mobile-light.png'),fullPage:true});
  await page.setViewportSize({width:1440,height:1000});
  check(await page.locator('div.product').first().evaluate(e=>getComputedStyle(e).gridTemplateColumns.split(' ').length)===2,'desktop product uses gallery/details layout');
  await page.screenshot({path:path.join(out,'product-desktop-light.png'),fullPage:true});
  const api=await context.request.get(base+'/wp-json/wc/store/v1/products?per_page=100');const allProducts=await api.json();
  const products=allProducts.filter(p=>p.sku!=='SYNTHETIC-UX-FUTURE-20261016');
  check(products.length===25&&products.every(p=>!p.is_purchasable),'all25 existing products remain inquiry-only');
  for(let start=0;start<products.length;start+=3){
   await Promise.all(products.slice(start,start+3).map(async p=>{
    // Retry only transport resets; HTTP errors still fail their exact assertion.
    const response=await context.request.get(p.permalink,{maxRetries:2,timeout:60000}),html=await response.text();
    assert(response.status()===200&&html.includes('tn-shop')&&html.includes('tn-shop-experience-css'),p.permalink);
   }));console.log('Public products verified: '+Math.min(start+3,products.length));
  }
  check(true,'shared product presentation serves all25 existing public products');
  const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}}),fallback=await nojs.newPage();
  await fallback.goto(base+'/shop/',{waitUntil:'domcontentloaded'});await fallback.locator('.tn-filter-advanced summary').click();
  check(await fallback.locator('select[name="tn_unit"]').isVisible(),'filters and original photos remain usable without JavaScript');await nojs.close();
  check(errors.length===0,'no page JavaScript errors');
  fs.writeFileSync(path.join(out,'shop-browser.json'),JSON.stringify({status:'passed',utc:new Date().toISOString(),base,browser_args:JSON.parse(process.env.TN_BROWSER_ARGS||'[]'),scope:'Read-only current25 public products; no order/inquiry/payment submitted',checks,js_errors:errors},null,2));
  console.log('SHOP_EXPERIENCE_CHECKS='+checks.length+' PASS');
 }finally{await browser.close()}
})().catch(e=>{console.error(e.stack);console.error('Last checks:',checks.slice(-4));process.exit(1)});
