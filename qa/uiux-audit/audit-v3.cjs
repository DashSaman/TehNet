'use strict';
const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path');
const BASE='http://localhost:18085';
const OUT=path.join(__dirname,'screenshots-v3');
const PAGES=[
  {n:'homepage',u:'/'},
  {n:'services',u:'/services/'},
  {n:'contact',u:'/contact/'},
  {n:'about',u:'/about/'},
  {n:'mtcna-hub',u:'/learn/mikrotik/mtcna/'},
  {n:'lab',u:'/lab/'},
  {n:'shop',u:'/shop/'},
  {n:'routeros-winbox',u:'/learn/mikrotik/mtcna/routeros-winbox/'},
];
const VIEWPORTS=[[320,568],[375,667],[768,1024],[1024,768],[1440,900]];
const issues=[],checked=[],console_errors=[],http_fails=[];
if(!fs.existsSync(OUT))fs.mkdirSync(OUT,{recursive:true});

(async()=>{
  const browser=await chromium.launch({channel:'msedge',headless:true});

  for(const pg of PAGES){
    for(const[w,h]of VIEWPORTS){
      for(const mode of(w===375?['light','dark']:['light'])){
        const ctx=await browser.newContext({viewport:{width:w,height:h},locale:'fa'});
        const page=await ctx.newPage();
        const errors=[];
        page.on('console',msg=>{if(msg.type()==='error'&&!msg.text().includes('favicon'))errors.push(msg.text().slice(0,150))});
        page.on('pageerror',e=>errors.push('PAGEERROR: '+e.message.slice(0,150)));
        page.on('requestfailed',r=>{if(r.url().startsWith(BASE))errors.push('REQFAIL: '+r.url().slice(0,100))});

        let http_status=0;
        try{
          const resp=await page.goto(BASE+pg.u,{waitUntil:'networkidle',timeout:30000});
          http_status=resp.status();
        }catch(e){
          http_fails.push({page:pg.n,vp:`${w}x${h}m${mode}`,error:e.message.slice(0,100)});
          await ctx.close();continue;
        }
        if(http_status!==200)
          http_fails.push({page:pg.n,vp:`${w}x${h}m${mode}`,status:http_status});

        // Real dark mode via theme toggle
        if(mode==='dark'){
          await page.evaluate(()=>{
            document.documentElement.setAttribute('data-theme','dark');
            localStorage.setItem('tn-theme','dark');
          });
          await page.reload({waitUntil:'networkidle'});
          // verify dark actually applied
          const bg=await page.evaluate(()=>getComputedStyle(document.body).backgroundColor);
          const m=bg&&bg.match(/\d+/g);
          const lum=m?parseInt(m[0])*0.299+parseInt(m[1])*0.587+parseInt(m[2])*0.114:128;
          if(lum>150)issues.push({page:pg.n,vp:w,mode,type:'dark_mode_not_dark',bg});
        }

        const label=`${pg.n}_${w}_${mode}`;
        // horizontal overflow
        const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
        if(overflow>0&&w<=375)issues.push({page:pg.n,vp:`${w}x${h}`,mode,type:'horizontal_overflow',px:overflow});

        // CTA above fold (1440 only)
        if(w===1440&&mode==='light'&&['homepage','services'].includes(pg.n)){
          const ctas=await page.evaluate(()=>{
            const fold=innerHeight;
            return [...document.querySelectorAll('a[href*="inquiry"],a[href*="contact"],a[href*="quote"],a[href*="مشاوره"],a.tn-btn,a.tn-cta')]
              .filter(el=>{const r=el.getBoundingClientRect();return r.top>=0&&r.top<fold&&r.width>40})
              .map(el=>({href:el.getAttribute('href'),text:el.textContent.trim().slice(0,40)}));
          });
          checked.push({page:pg.n,type:'cta_above_fold',count:ctas.length,ctas:ctas.slice(0,3)});
        }

        // screenshot with unique name (page_vp_mode)
        await page.screenshot({path:path.join(OUT,`${pg.n}_${w}_${mode}.png`),fullPage:w===375&&mode==='light'});

        // console errors recorded as explicit findings
        if(errors.length>0)
          issues.push({page:pg.n,vp:`${w}x${h}`,mode,type:'console_errors',count:errors.length,sample:errors[0]});

        await ctx.close();
      }
    }

    // Mobile navigation (theme selectors)
    {
      const ctx=await browser.newContext({viewport:{width:375,height:667}});
      const page=await ctx.newPage();
      try{
        await page.goto(BASE+pg.u,{waitUntil:'networkidle',timeout:30000});
        const toggle=await page.$('button.tn-menu-toggle');
        if(toggle){
          // 1. initial aria-expanded
          const ariaBefore=await toggle.getAttribute('aria-expanded');
          // 2. click to open
          await toggle.click();await page.waitForTimeout(500);
          const ariaAfter=await toggle.getAttribute('aria-expanded');
          const isOpen=await page.evaluate(()=>{
            const nav=document.querySelector('nav#tn-main-menu.tn-site-nav');
            if(!nav)return{found:false};
            return{found:true,hasIsOpen:nav.classList.contains('is-open'),
                   visible:getComputedStyle(nav).display!=='none',
                   links:nav.querySelectorAll('a[href]').length};
          });
          // 3. verify aria-expanded changed
          if(ariaBefore!=='true'&&ariaAfter!=='true')
            issues.push({page:pg.n,type:'mobile_nav_aria_not_toggled',before:ariaBefore,after:ariaAfter});
          if(!isOpen.found)issues.push({page:pg.n,type:'mobile_nav_menu_not_found'});
          else{
            if(isOpen.links===0)issues.push({page:pg.n,type:'mobile_nav_menu_no_links'});
            // 4. test navigation link click
            const firstLink=await page.$('nav#tn-main-menu.tn-site-nav a[href]');
            if(firstLink){
              const href=await firstLink.getAttribute('href');
              await firstLink.click();await page.waitForTimeout(1500);
              checked.push({page:pg.n,type:'mobile_nav_click',href,navigated:page.url().includes(href)});
            }
          }
          // 5. Escape key closes
          await page.keyboard.press('Escape');await page.waitForTimeout(400);
          const stillOpen=await page.evaluate(()=>{
            const nav=document.querySelector('nav#tn-main-menu.tn-site-nav');
            return nav&&nav.classList.contains('is-open');
          });
          if(stillOpen)issues.push({page:pg.n,type:'escape_does_not_close'});
          checked.push({page:pg.n,type:'mobile_nav_test_complete',ariaBefore,ariaAfter,found:isOpen.found});
        }
      }catch(e){
        issues.push({page:pg.n,type:'mobile_nav_test_error',msg:e.message.slice(0,120)});
      }
      await ctx.close();
    }

    // No-JS: computed visibility and usable links
    {
      const ctx=await browser.newContext({viewport:{width:375,height:667},javaScriptEnabled:false});
      const page=await ctx.newPage();
      try{
        await page.goto(BASE+pg.u,{waitUntil:'load',timeout:20000});
        const navCheck=await page.evaluate(()=>{
          const nav=document.querySelector('nav#tn-main-menu.tn-site-nav');
          if(!nav)return{exists:false};
          const cs=getComputedStyle(nav);
          const links=[...nav.querySelectorAll('a[href]')];
          return{exists:true,display:cs.display,visible:cs.display!=='none'&&nav.getBoundingClientRect().height>0,
                 linkCount:links.length,linkTexts:links.slice(0,3).map(a=>a.textContent.trim().slice(0,20))};
        });
        if(navCheck.exists){
          checked.push({page:pg.n,type:'no_js_nav',visible:navCheck.visible,linkCount:navCheck.linkCount});
          if(!navCheck.visible)issues.push({page:pg.n,type:'no_js_nav_hidden'});
        }
      }catch(e){/* expected */}
      await ctx.close();
    }
  }

  // Product images detailed check (shop page only)
  {
    const ctx=await browser.newContext({viewport:{width:1440,height:900}});
    const page=await ctx.newPage();
    try{
      await page.goto(BASE+'/shop/',{waitUntil:'networkidle',timeout:30000});
      // scroll all images into view
      await page.evaluate(async()=>{
        const imgs=[...document.querySelectorAll('img[src*="uploads"]')];
        for(const img of imgs){img.scrollIntoView({behavior:'instant',block:'center'});await new Promise(r=>setTimeout(r,200))}
      });
      await page.waitForTimeout(2000); // lazy loading grace
      const imgData=await page.evaluate(()=>{
        return [...document.querySelectorAll('img[src*="uploads"]')].map(img=>{
          const r=img.getBoundingClientRect();
          return{src:img.src.slice(-60),complete:img.complete,naturalWidth:img.naturalWidth,
                 visible:r.width>0&&r.height>0,inViewport:r.top<innerHeight&&r.bottom>0};
        });
      });
      // group by unique URL
      const byUrl={};
      for(const img of imgData){
        const key=img.src;
        if(!byUrl[key])byUrl[key]={...img,occurrences:1};
        else byUrl[key].occurrences++;
      }
      const uniqueUrls=Object.keys(byUrl).length;
      const brokenUrls=Object.values(byUrl).filter(i=>!i.complete||i.naturalWidth===0);
      checked.push({page:'shop',uniqueImageUrls:uniqueUrls,brokenImages:brokenUrls.length,
                    brokenUrlList:brokenUrls.map(b=>b.src.slice(-40))});
      if(brokenUrls.length>0)
        issues.push({page:'shop',type:'broken_product_images',count:brokenUrls.length,urls:brokenUrls.map(b=>b.src)});
    }catch(e){
      issues.push({page:'shop',type:'image_check_error',msg:e.message.slice(0,100)});
    }
    await ctx.close();
  }

  await browser.close();

  // summary
  fs.writeFileSync(path.join(__dirname,'audit-v3-results.json'),JSON.stringify({
    pages:PAGES.length,issues,http_fails,checked,
    summary:{total_issues:issues.length,unique_issue_types:[...new Set(issues.map(i=>i.type))]}
  },null,1));
  console.log(`AUDIT v3 COMPLETE | pages=${PAGES.length} issues=${issues.length} http_fails=${http_fails.length}`);
  const types={};issues.forEach(i=>types[i.type]=(types[i.type]||0)+1);
  console.log('Issue types:',JSON.stringify(types));
  for(const i of issues.slice(0,15))
    console.log(`  [${i.page||'-'}] ${i.type} ${i.vp||''}${i.mode?' '+i.mode:''} ${i.msg||i.detail?JSON.stringify({msg:i.msg,detail:i.detail}).slice(0,120):''}`);
})();
