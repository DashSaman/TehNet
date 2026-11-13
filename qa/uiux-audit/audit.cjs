'use strict';
const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path');
const BASE='http://localhost:18085';
const OUT=path.join(__dirname,'screenshots');
const PAGES=[
  {n:'homepage',u:'/'},
  {n:'services',u:'/services/'},
  {n:'contact',u:'/contact/'},
  {n:'about',u:'/about/'},
  {n:'mtcna-hub',u:'/learn/mikrotik/mtcna/'},
  {n:'lab',u:'/lab/'},
  {n:'shop',u:'/shop/'},
];
const VIEWPORTS=[[320,568],[375,667],[768,1024],[1024,768],[1440,900]];
const issues=[];
if(!fs.existsSync(OUT))fs.mkdirSync(OUT,{recursive:true});
(async()=>{
  const browser=await chromium.launch({channel:'msedge',headless:true});
  const results={pages:{},console_errors:[],overflow:[],broken_links:[]};
  for(const pg of PAGES){
    results.pages[pg.n]={};
    for(const[w,h]of VIEWPORTS){
      const label=`${pg.n}_${w}`;
      const ctx=await browser.newContext({viewport:{width:w,height:h},locale:'fa'});
      const page=await ctx.newPage();
      const errors=[];
      page.on('console',msg=>{if(msg.type()==='error')errors.push(msg.text().slice(0,120))});
      page.on('pageerror',e=>errors.push(e.message.slice(0,120)));
      try{
        await page.goto(BASE+pg.u,{waitUntil:'networkidle',timeout:30000});
        // horizontal overflow check
        const overflow=await page.evaluate(()=>{
          return document.documentElement.scrollWidth>document.documentElement.clientWidth?
            document.documentElement.scrollWidth-document.documentElement.clientWidth:0;
        });
        if(overflow>0&&w<=375)issues.push({page:pg.n,vp:`${w}x${h}`,type:'horizontal_overflow',px:overflow});
        // CTA visibility
        const cta=await page.evaluate(()=>{
          const btns=[...document.querySelectorAll('a[href*="inquiry"],a[href*="contact"],a[href*="quote"],button[type*="submit"]')];
          return btns.filter(b=>{const r=b.getBoundingClientRect();return r.width>0&&r.height>0}).length;
        });
        if(w===375)results.pages[pg.n]['cta_'+w]=cta;
        // screenshot
        await page.screenshot({path:path.join(OUT,`${label}.png`),fullPage:w===375});
        // dark mode
        if(w===375){
          await page.emulateMedia({colorScheme:'dark'});
          await page.screenshot({path:path.join(OUT,`${label}_dark.png`)});
        }
        results.pages[pg.n][`vp_${w}`]={overflow,cta_count:cta,console_errors:errors.length};
      }catch(e){
        results.pages[pg.n][`vp_${w}_error`]=e.message.slice(0,120);
      }
      await ctx.close();
    }
    // no-JS check at 375
    const ctx3=await browser.newContext({viewport:{width:375,height:667},javaScriptEnabled:false});
    const page3=await ctx3.newPage();
    try{
      await page3.goto(BASE+pg.u,{waitUntil:'load',timeout:20000});
      const nav=await page3.evaluate(()=>document.querySelector('nav,#menu,.nav,.menu')?'visible':'missing');
      if(nav==='missing')issues.push({page:pg.n,type:'no_js_no_navigation'});
    }catch(e){issues.push({page:pg.n,type:'no_js_error',msg:e.message.slice(0,80)})}
    await ctx3.close();
  }
  await browser.close();
  fs.writeFileSync(path.join(__dirname,'audit-results.json'),JSON.stringify(results,null,1));
  fs.writeFileSync(path.join(OUT,'issues.json'),JSON.stringify(issues,null,1));
  console.log('AUDIT COMPLETE');
  console.log('Issues:',JSON.stringify(issues.slice(0,10)));
  console.log('Total issues:',issues.length);
})();
