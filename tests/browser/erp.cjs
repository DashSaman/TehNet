const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'qa/store-2026-10-15');
const env=Object.fromEntries(fs.readFileSync(path.join(root,'ops/staging/.env'),'utf8').trim().split(/\r?\n/).map(l=>{const i=l.indexOf('=');return [l.slice(0,i),l.slice(i+1)];}));
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'});
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 try{
  await page.goto('http://localhost:18084/login');await page.waitForLoadState('networkidle');
  await page.locator('#login_email').fill('Administrator');await page.locator('#login_password').fill(env.ERP_ADMIN_PASSWORD);
  await page.getByRole('button',{name:'Continue',exact:true}).click();await page.waitForURL(/\/(app|desk)/,{timeout:45000});
  for(const [route,name] of [['/app/sales-order','erp-sales-orders'],['/app/stock-balance','erp-stock-balance'],['/app/query-report/General%20Ledger','erp-general-ledger'],['/app/query-report/Stock%20Ledger','erp-stock-ledger']]){
   await page.goto('http://localhost:18084'+route);await page.waitForLoadState('networkidle');
   await page.screenshot({path:path.join(out,name+'.png'),fullPage:true});
   console.log(JSON.stringify({route,title:await page.title(),body:(await page.locator('body').innerText()).slice(0,300)}));
  }
 }finally{await browser.close()}
})().catch(e=>{console.error(e.message);process.exit(1)});
