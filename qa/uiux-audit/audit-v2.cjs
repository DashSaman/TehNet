'use strict';
const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path');
const BASE='http://localhost:18085';
const OUT=path.join(__dirname,'screenshots-v2');
const PAGES=[
  {n:'homepage',u:'/'},{n:'services',u:'/services/'},{n:'contact',u:'/contact/'},
  {n:'about',u:'/about/'},{n:'mtcna-hub',u:'/learn/mikrotik/mtcna/'},
  {n:'lab',u:'/lab/'},{n:'shop',u:'/shop/'},
  {n:'routeros-winbox',u:'/learn/mikrotik/mtcna/routeros-winbox/'},
];
const VIEWPORTS=[[320,568],[375,667],[768,1024],[1024,768],[1440,900]];
const issues=[],http_fails=[];
if(!fs.existsSync(OUT))fs.mkdirSync(OUT,{recursive:true});

(async()=>{
  const browser=await chromium.launch({channel:'msedge',headless:true});
  const all_results={};

  for(const pg of PAGES){
    for(const[w,h]of VIEWPORTS){
      for(const mode of (w===375?['light','dark']:['light'])){
        const ctx=await browser.newContext({viewport:{width:w,height:h},locale:'fa'});
        const page=await ctx.newPage();
        const errors=[];
        page.on('console',m=>{if(m.type()==='error'&&!m.text().includes('favicon'))errors.push(m.text().slice(0,120))});
        page.on('pageerror',e=>errors.push(e.message.slice(0,120)));
        page.on('requestfailed',r=>{if(r.url().startsWith(BASE))errors.push('REQFAIL:'+r.url().slice(0,80))});
        let http_status=0;
        try{
          const resp=await page.goto(BASE+pg.u,{waitUntil:'networkidle',timeout:30000});
          http_status=resp.status();
          if(http_status!==200){http_fails.push({page:pg.n,vp:`${w}x${h}`,status:http_status});await ctx.close();continue;}
        }catch(e){http_fails.push({page:pg.n,vp:`${w}x${h}`,error:e.message.slice(0,80)});await ctx.close();continue;}

        // real dark mode via localStorage + data-theme attribute
        if(mode==='dark'){
          await page.evaluate(()=>{
            document.documentElement.setAttribute('data-theme','dark');
            localStorage.setItem('tn-theme','dark');
          });
          await page.reload({waitUntil:'networkidle'});
        }

        const key=`${pg.n}_${w}_${mode}`;
        const ov=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
        if(ov>0&&w<=375)issues.push({page:pg.n,vp:w,mode,type:'horizontal_overflow',px:ov});
        const errs=await page.evaluate(()=>({
          console_errors:performance.getEntriesByType('resource').filter(r=>r.responseStatus>=400).length,
          images_broken:[...document.querySelectorAll('img')].filter(i=>!i.complete||i.naturalWidth===0).length,
        }));
        if(errs.images_broken>0)issues.push({page:pg.n,vp:w,mode,type:'broken_images',count:errs.images_broken});
        // dark mode check: body bg should be dark
        if(mode==='dark'){
          const bg=await page.evaluate(()=>getComputedStyle(document.body).backgroundColor);
          const m=bg.match(/\d+/g);
          if(m&&parseInt(m[0])>150)issues.push({page:pg.n,vp:w,mode,type:'dark_mode_not_applied',bg});
        }
        // CTA above fold at 1440
        if(w===1440&&mode==='light'){
          const ctas=await page.evaluate(()=>{
            const fold=innerHeight;
            return [...document.querySelectorAll('a[href*="inquiry"],a[href*="contact"],a[href*="quote"],a[href*="مشاوره"]')]
              .filter(el=>{const r=el.getBoundingClientRect();return r.top>=0&&r.top<fold&&r.width>30})
              .map(el=>el.getAttribute('href'));
          });
          if(['homepage','services'].includes(pg.n)&&ctas.length===0)
            issues.push({page:pg.n,type:'no_above_fold_cta'});
        }
        // screenshot
        await page.screenshot({path:path.join(OUT,`${key}.png`),fullPage:w===375&&mode==='light'});
        if(mode==='dark'&&w===375)
          await page.screenshot({path:path.join(OUT,`${key}_dark.png`)});
        await ctx.close();
      }
    }

    // mobile navigation with aria checks
    {
      const ctx=await browser.newContext({viewport:{width:375,height:667}});
      const page=await ctx.newPage();
      try{
        await page.goto(BASE+pg.u,{waitUntil:'networkidle',timeout:30000});
        const toggle=await page.$('[data-bs-toggle="collapse"],.navbar-toggler,.tn-mobile-menu-btn,button[aria-expanded],[aria-controls*="nav"]');
        if(toggle){
          const pre=await toggle.getAttribute('aria-expanded');
          await toggle.click();await page.waitForTimeout(400);
          const post=await toggle.getAttribute('aria-expanded');
          if(pre==='false'&&post!=='true')issues.push({page:pg.n,type:'mobile_toggle_not_expanding'});
          // links inside expanded menu
          const links=await page.evaluate(()=>{
            const nav=document.querySelector('.navbar-collapse,.tn-mobile-nav,.collapse.show');
            return nav?nav.querySelectorAll('a[href]').length:0;
          });
          if(links===0)issues.push({page:pg.n,type:'mobile_menu_no_links'});
          // navigate
          const firstNav=await page.$('.navbar-collapse a[href],.tn-mobile-nav a[href]');
          if(firstNav){
            const href=await firstNav.getAttribute('href');
            await firstNav.click();await page.waitForTimeout(1500);
            if(!page.url().includes(href)&&href!=='#')issues.push({page:pg.n,type:'mobile_nav_broken',href});
          }
        }
      }catch(e){/* silent */}
      await ctx.close();
    }

    // no-JS: nav visible and usable
    {
      const ctx=await browser.newContext({viewport:{width:375,height:667},javaScriptEnabled:false});
      const page=await ctx.newPage();
      try{
        await page.goto(BASE+pg.u,{waitUntil:'load',timeout:20000});
        const navCheck=await page.evaluate(()=>{
          const nav=document.querySelector('nav,[role="navigation"],#site-navigation,.tn-header-nav');
          if(!nav)return{exists:false};
          const cs=getComputedStyle(nav);
          const links=nav.querySelectorAll('a[href]');
          return{exists:true,visible:cs.display!=='none'&&nav.getBoundingClientRect().height>0,links:links.length};
        });
        if(navCheck.exists&&!navCheck.visible)issues.push({page:pg.n,type:'no_js_nav_hidden'});
        if(navCheck.exists&&navCheck.links===0)issues.push({page:pg.n,type:'no_js_nav_no_links'});
      }catch(e){}
      await ctx.close();
    }
  }

  // Internal link check (bounded, 30 links from homepage)
  {
    const ctx=await browser.newContext();
    const page=await ctx.newPage();
    await page.goto(BASE,{waitUntil:'networkidle',timeout:30000});
    const links=await page.evaluate(()=>[...new Set([...document.querySelectorAll('a[href^="/"]')].map(a=>a.getAttribute('href')))].slice(0,30));
    let broken=0;
    for(const link of links){
      try{
        const r=await page.request.get(BASE+link,{maxRedirects:3});
        if(r.status()>=400){broken++;issues.push({type:'broken_internal_link',url:link,status:r.status()})}
      }catch(e){broken++;issues.push({type:'link_error',url:link})}
    }
    await ctx.close();
    if(broken>0)issues.push({type:'broken_links_summary',count:broken});
  }

  await browser.close();

  // summary
  fs.writeFileSync(path.join(__dirname,'audit-v2-results.json'),JSON.stringify({issues,http_fails,timestamp:new Date().toISOString()},null,1));
  console.log(`AUDIT v2 COMPLETE | issues=${issues.length} http_fails=${http_fails.length}`);
  for(const i of issues.slice(0,20))
    console.log(`  [${i.page||'-'}] ${i.type} vp=${i.vp||'-'} mode=${i.mode||'-'} ${i.detail||i.msg||i.url||''} ${i.status||''} ${i.px?'+'+i.px+'px':''}`);
})();
