const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'qa/store-2026-10-15');
const env=Object.fromEntries(fs.readFileSync(path.join(root,'ops/staging/.env'),'utf8').trim().split(/\r?\n/).map(l=>{const i=l.indexOf('=');return [l.slice(0,i),l.slice(i+1)];}));
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const context=await browser.newContext({viewport:{width:1440,height:1000}}),page=await context.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 async function login(user,password){await page.goto('http://localhost:18083/wp-login.php');await page.locator('#user_login').fill(user);await page.locator('#user_pass').fill(password);await Promise.all([page.waitForURL(u=>!u.pathname.endsWith('wp-login.php')),page.locator('#wp-submit').click()]);}
 try{
  await login('tehnet-stage',env.WP_ADMIN_PASSWORD);
  await page.goto('http://localhost:18083/wp-admin/admin.php?page=tn-store');await page.waitForLoadState('networkidle');
  assert(await page.getByRole('heading',{name:'عملیات فروشگاه تهران نتورک'}).isVisible());
  assert.equal(await page.locator('input[name=action][value=tn_store_operation]').count(),1,'the complete operations form must render');
  assert((await page.locator('table tbody tr').count())>0,'native refund records must not break the order listing');
  await page.screenshot({path:path.join(out,'store-operations.png'),fullPage:true});
  await context.clearCookies();await login(env.WP_CUSTOMER_USER,env.WP_CUSTOMER_PASSWORD);
  const orderUrl='http://localhost:18083/my-account/view-order/'+env.WP_CUSTOMER_ORDER+'/';
  await page.goto(orderUrl);await page.waitForLoadState('networkidle');
  const invoice=page.getByRole('link',{name:'مشاهده فاکتور شماره‌دار'});assert(await invoice.isVisible());
  const invoiceUrl=await invoice.getAttribute('href');
  const denied=await page.request.get(invoiceUrl.replace('order_id='+env.WP_CUSTOMER_ORDER,'order_id='+(Number(env.WP_CUSTOMER_ORDER)-1)));
  assert.equal(denied.status(),403,'customer cannot read another order invoice');
  const csrf=await page.request.post('http://localhost:18083/wp-admin/admin-post.php',{form:{action:'tn_store_return_request',order_id:env.WP_CUSTOMER_ORDER,reason:'SYNTHETIC CSRF CHECK'}});
  assert.equal(csrf.status(),403,'return request must have a valid nonce');
  await page.screenshot({path:path.join(out,'customer-order.png'),fullPage:true});
  await invoice.click();await page.waitForLoadState('networkidle');assert((await page.locator('body').innerText()).includes('2100'));
  const stamp=page.getByAltText('مهر تهران نتورک');assert.equal(await stamp.count(),1);await stamp.evaluate(e=>e.decode());
  await page.screenshot({path:path.join(out,'customer-invoice.png'),fullPage:true});
  await page.goto(orderUrl);await page.locator('details summary').click();
  await page.locator('textarea[name=reason]').fill('درخواست ساختگی آزمون: بررسی مرجوعی یک متر کابل؛ هیچ پیام یا استرداد بانکی ارسال نمی‌شود.');
  await Promise.all([page.waitForURL(/tn_return=requested/),page.getByRole('button',{name:'ثبت درخواست بررسی'}).click()]);
  assert(await page.getByRole('status').filter({hasText:'درخواست بررسی مرجوعی ثبت شد'}).isVisible());
  await page.setViewportSize({width:390,height:844});await page.reload();await page.waitForLoadState('networkidle');
  await page.screenshot({path:path.join(out,'customer-order-mobile.png'),fullPage:true});
  assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)),'customer order has no mobile overflow');
  assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,'account-browser-results.json'),JSON.stringify({adminOperations:true,customerOwnInvoice:true,otherInvoiceDenied:true,csrfDenied:true,returnRequest:true,mobileNoOverflow:true,jsErrors:errors,scope:'Real local Woo account and ERP invoice. Synthetic completed/refunded order; no provider payment or message.'},null,2));
  console.log('ACCOUNT_BROWSER=PASSED');
 }finally{await browser.close()}
})().catch(e=>{console.error(e.message);process.exit(1)});
