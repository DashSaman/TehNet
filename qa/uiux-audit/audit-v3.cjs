'use strict';
// Corrected audit v3 (r2): bounded corrections per owner directive 2026-11-13.
// Corrections vs the committed v1 evidence (audit-v3-results.json preserved):
//   1. Escape is tested BEFORE navigation (not after leaving the page).
//   2. Navigation asserts the URL actually changed to a different page.
//   3. Dark mode is exercised through the real .tn-theme-toggle button (click,
//      persistence on reload, both directions) instead of programmatic attributes.
//   4. Missing/hidden/link-less no-JS navigation is a hard failure, not silent.
//   5. Nonzero HTTP failures are blocking (exit code 2).
// Modes: full (default) reruns everything -> audit-v3-r2-results.json
//        --regressions reruns only the affected regressions (all 8 pages x
//        {HTTP, real theme toggle, mobile nav, no-JS}) -> audit-v3-r2-regressions-results.json
const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path');
const BASE='http://localhost:18085';
const REGRESSIONS_ONLY=process.argv.includes('--regressions');
const OUT=path.join(__dirname,'screenshots-v3');
const RESULTS=path.join(__dirname,REGRESSIONS_ONLY?'audit-v3-r2-regressions-results.json':'audit-v3-r2-results.json');
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
if(!REGRESSIONS_ONLY&&!fs.existsSync(OUT))fs.mkdirSync(OUT,{recursive:true});

function lum(bg){const m=bg&&bg.match(/\d+/g);return m?parseInt(m[0])*0.299+parseInt(m[1])*0.587+parseInt(m[2])*0.114:128;}

async function gotoOrRecord(page,ctx,pg,vpLabel){
  try{
    const resp=await page.goto(BASE+pg.u,{waitUntil:'networkidle',timeout:30000});
    const status=resp.status();
    if(status!==200){
      http_fails.push({page:pg.n,vp:vpLabel,status});
      issues.push({page:pg.n,vp:vpLabel,type:'http_non_200',status,blocking:true});
      return false;
    }
    return true;
  }catch(e){
    http_fails.push({page:pg.n,vp:vpLabel,error:e.message.slice(0,100)});
    issues.push({page:pg.n,vp:vpLabel,type:'http_goto_error',msg:e.message.slice(0,100),blocking:true});
    return false;
  }
}

// Real theme toggle exercise: click -> assert flip -> reload persistence -> click back.
// Returns the theme to light so subsequent checks stay comparable.
async function exerciseThemeToggle(page,pg,vpLabel){
  const probe=await page.evaluate(()=>{
    const t=document.querySelector('.tn-theme-toggle');
    return{present:!!t,visible:t?getComputedStyle(t).display!=='none':false,
           initial:document.documentElement.dataset.theme,
           bgBefore:getComputedStyle(document.body).backgroundColor,
           metaBefore:(document.querySelector('meta[name="theme-color"]')||{}).content||''};
  });
  if(!probe.present||!probe.visible){
    issues.push({page:pg.n,vp:vpLabel,type:'theme_toggle_missing',present:probe.present,visible:probe.visible});
    return;
  }
  // to dark
  await page.click('.tn-theme-toggle');
  await page.waitForTimeout(250);
  const dark=await page.evaluate(()=>({
    theme:document.documentElement.dataset.theme,
    bg:getComputedStyle(document.body).backgroundColor,
    meta:(document.querySelector('meta[name="theme-color"]')||{}).content||'',
    stored:localStorage.getItem('tn-theme'),
    pressed:document.querySelector('.tn-theme-toggle').getAttribute('aria-pressed')}));
  if(dark.theme!=='dark'||dark.stored!=='dark'||lum(dark.bg)>150||dark.meta===''||dark.meta===probe.metaBefore||dark.pressed!=='false')
    issues.push({page:pg.n,vp:vpLabel,type:'theme_toggle_dark_click_no_effect',before:probe,dark});
  // persistence through reload (real user path: localStorage + header inline script)
  await page.reload({waitUntil:'networkidle'});
  const persisted=await page.evaluate(()=>({theme:document.documentElement.dataset.theme,bg:getComputedStyle(document.body).backgroundColor}));
  if(persisted.theme!=='dark'||lum(persisted.bg)>150)
    issues.push({page:pg.n,vp:vpLabel,type:'dark_mode_not_persisted_after_reload',persisted});
  // back to light (second direction of the real toggle)
  await page.click('.tn-theme-toggle');
  await page.waitForTimeout(250);
  const light=await page.evaluate(()=>({theme:document.documentElement.dataset.theme,bg:getComputedStyle(document.body).backgroundColor,stored:localStorage.getItem('tn-theme')}));
  if(light.theme!=='light'||light.stored!=='light'||lum(light.bg)<100)
    issues.push({page:pg.n,vp:vpLabel,type:'theme_toggle_light_click_no_effect',light});
  checked.push({page:pg.n,vp:vpLabel,type:'theme_toggle_real_exercise',darkBg:dark.bg,lightBg:light.bg,meta:dark.meta});
}

// Mobile nav: open -> Escape closes (BEFORE any navigation) -> reopen -> click a
// link whose resolved path differs from the current one -> assert real navigation.
async function testMobileNav(browser,pg){
  const ctx=await browser.newContext({viewport:{width:375,height:667}});
  const page=await ctx.newPage();
  try{
    if(!await gotoOrRecord(page,ctx,pg,'mobile_nav')){await ctx.close();return;}
    const toggle=await page.$('button.tn-menu-toggle');
    if(!toggle){issues.push({page:pg.n,type:'mobile_nav_toggle_missing'});await ctx.close();return;}
    const ariaBefore=await toggle.getAttribute('aria-expanded');
    await toggle.click();await page.waitForTimeout(500);
    const ariaAfter=await toggle.getAttribute('aria-expanded');
    const openState=await page.evaluate(()=>{
      const nav=document.querySelector('nav#tn-main-menu.tn-site-nav');
      if(!nav)return{found:false};
      return{found:true,hasIsOpen:nav.classList.contains('is-open'),
             visible:getComputedStyle(nav).display!=='none',
             links:[...nav.querySelectorAll('a[href]')].map(a=>a.getAttribute('href'))};
    });
    if(ariaAfter!=='true')issues.push({page:pg.n,type:'mobile_nav_aria_not_toggled',before:ariaBefore,after:ariaAfter});
    if(!openState.found){issues.push({page:pg.n,type:'mobile_nav_menu_not_found'});await ctx.close();return;}
    if(!openState.hasIsOpen||!openState.visible||openState.links.length===0)
      issues.push({page:pg.n,type:'mobile_nav_menu_not_open',hasIsOpen:openState.hasIsOpen,visible:openState.visible,links:openState.links.length});
    // 1. Escape BEFORE navigation must close the open menu (no submenu open here)
    await page.keyboard.press('Escape');await page.waitForTimeout(400);
    const closedByEscape=await page.evaluate(()=>{
      const nav=document.querySelector('nav#tn-main-menu.tn-site-nav');
      return nav&&!nav.classList.contains('is-open')&&getComputedStyle(nav).display==='none';
    });
    if(!closedByEscape)issues.push({page:pg.n,type:'escape_does_not_close_menu_before_navigation'});
    // 2. reopen and navigate to a DIFFERENT page
    await toggle.click();await page.waitForTimeout(400);
    const reopenOk=await page.evaluate(()=>document.querySelector('nav#tn-main-menu.tn-site-nav').classList.contains('is-open'));
    if(!reopenOk)issues.push({page:pg.n,type:'mobile_nav_reopen_failed'});
    const currentPath=new URL(page.url()).pathname;
    const altHref=openState.links.find(h=>{try{return new URL(h,BASE).pathname!==currentPath&&h!=='#';}catch(e){return false;}});
    if(!altHref){
      checked.push({page:pg.n,type:'mobile_nav_no_alternative_link',links:openState.links.length});
    }else{
      await Promise.all([
        page.waitForNavigation({waitUntil:'load',timeout:15000}).catch(()=>null),
        page.click(`nav#tn-main-menu a[href="${altHref.replace(/"/g,'\\"')}"]`),
      ]);
      await page.waitForTimeout(800);
      const nowPath=new URL(page.url()).pathname;
      const navigated=nowPath!==currentPath;
      if(!navigated)issues.push({page:pg.n,type:'mobile_nav_click_did_not_navigate',href:altHref,from:currentPath,to:nowPath});
      else checked.push({page:pg.n,type:'mobile_nav_navigation_verified',from:currentPath,to:nowPath,href:altHref});
    }
    checked.push({page:pg.n,type:'mobile_nav_test_complete',ariaBefore,ariaAfter,escapeClosedFirst:closedByEscape,links:openState.links.length});
  }catch(e){
    issues.push({page:pg.n,type:'mobile_nav_test_error',msg:e.message.slice(0,120)});
  }
  await ctx.close();
}

// No-JS: nav must exist, be visible, and expose real links. Missing = failure.
async function testNoJsNav(browser,pg){
  const ctx=await browser.newContext({viewport:{width:375,height:667},javaScriptEnabled:false});
  const page=await ctx.newPage();
  try{
    await page.goto(BASE+pg.u,{waitUntil:'load',timeout:20000});
    const navCheck=await page.evaluate(()=>{
      const nav=document.querySelector('nav#tn-main-menu.tn-site-nav');
      if(!nav)return{exists:false};
      const cs=getComputedStyle(nav);
      const links=[...nav.querySelectorAll('a[href]')].filter(a=>a.getAttribute('href')&&a.getAttribute('href')!=='#');
      return{exists:true,display:cs.display,visible:cs.display!=='none'&&nav.getBoundingClientRect().height>0,
             linkCount:links.length,
             allReachable:links.every(a=>!a.getAttribute('href').startsWith('javascript'))};
    });
    if(!navCheck.exists)issues.push({page:pg.n,type:'no_js_nav_missing',blocking:true});
    else{
      checked.push({page:pg.n,type:'no_js_nav',visible:navCheck.visible,linkCount:navCheck.linkCount});
      if(!navCheck.visible)issues.push({page:pg.n,type:'no_js_nav_hidden',blocking:true});
      if(navCheck.linkCount===0)issues.push({page:pg.n,type:'no_js_nav_no_links',blocking:true});
    }
  }catch(e){
    issues.push({page:pg.n,type:'no_js_load_error',msg:e.message.slice(0,100),blocking:true});
  }
  await ctx.close();
}

(async()=>{
  let browser;
  try{browser=await chromium.launch({channel:'msedge',headless:true});}
  catch(e){console.log('msedge channel unavailable, falling back to bundled chromium:',e.message.split('\n')[0]);
    browser=await chromium.launch({headless:true});}

  if(REGRESSIONS_ONLY){
    // Affected regressions only: HTTP status, real theme toggle, mobile nav, no-JS.
    for(const pg of PAGES){
      {
        const ctx=await browser.newContext({viewport:{width:375,height:667},locale:'fa'});
        const page=await ctx.newPage();
        const errors=[];
        page.on('console',msg=>{if(msg.type()==='error'&&!msg.text().includes('favicon'))errors.push(msg.text().slice(0,150))});
        page.on('pageerror',e=>errors.push('PAGEERROR: '+e.message.slice(0,150)));
        if(await gotoOrRecord(page,ctx,pg,'375_light')){
          await exerciseThemeToggle(page,pg,'375_light');
          if(errors.length>0){issues.push({page:pg.n,vp:'375',mode:'light',type:'console_errors',count:errors.length,sample:errors[0]});console_errors.push({page:pg.n,errors:errors.slice(0,5)});}
        }
        await ctx.close();
      }
      await testMobileNav(browser,pg);
      await testNoJsNav(browser,pg);
    }
  }else{
    // Full mode (corrected logic) — same coverage as committed v1 evidence.
    for(const pg of PAGES){
      for(const[w,h]of VIEWPORTS){
        for(const mode of(w===375?['light','dark']:['light'])){
          const ctx=await browser.newContext({viewport:{width:w,height:h},locale:'fa'});
          const page=await ctx.newPage();
          const errors=[];
          page.on('console',msg=>{if(msg.type()==='error'&&!msg.text().includes('favicon'))errors.push(msg.text().slice(0,150))});
          page.on('pageerror',e=>errors.push('PAGEERROR: '+e.message.slice(0,150)));
          page.on('requestfailed',r=>{if(r.url().startsWith(BASE))errors.push('REQFAIL: '+r.url().slice(0,100))});
          const vpLabel=`${w}x${h}m${mode}`;
          if(!await gotoOrRecord(page,ctx,pg,vpLabel)){await ctx.close();continue;}
          // Real dark mode through the theme toggle (corrected: was programmatic).
          if(mode==='dark')await exerciseThemeToggle(page,pg,vpLabel);
          const label=`${pg.n}_${w}_${mode}`;
          const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
          if(overflow>0&&w<=375)issues.push({page:pg.n,vp:`${w}x${h}`,mode,type:'horizontal_overflow',px:overflow});
          if(w===1440&&mode==='light'&&['homepage','services'].includes(pg.n)){
            const ctas=await page.evaluate(()=>{
              const fold=innerHeight;
              return [...document.querySelectorAll('a[href*="inquiry"],a[href*="contact"],a[href*="quote"],a[href*="مشاوره"],a.tn-btn,a.tn-cta')]
                .filter(el=>{const r=el.getBoundingClientRect();return r.top>=0&&r.top<fold&&r.width>40})
                .map(el=>({href:el.getAttribute('href'),text:el.textContent.trim().slice(0,40)}));
            });
            if(ctas.length===0)issues.push({page:pg.n,vp:`${w}x${h}`,mode,type:'no_above_fold_cta'});
            checked.push({page:pg.n,type:'cta_above_fold',count:ctas.length,ctas:ctas.slice(0,3)});
          }
          await page.screenshot({path:path.join(OUT,`${pg.n}_${w}_${mode}.png`),fullPage:w===375&&mode==='light'});
          if(errors.length>0)
            issues.push({page:pg.n,vp:`${w}x${h}`,mode,type:'console_errors',count:errors.length,sample:errors[0]});
          await ctx.close();
        }
      }
      await testMobileNav(browser,pg);
      await testNoJsNav(browser,pg);
    }
    // Product images detailed check (shop page only)
    {
      const ctx=await browser.newContext({viewport:{width:1440,height:900}});
      const page=await ctx.newPage();
      try{
        if(await gotoOrRecord(page,ctx,{n:'shop',u:'/shop/'},'1440_images')){
          await page.evaluate(async()=>{
            const imgs=[...document.querySelectorAll('img[src*="uploads"]')];
            for(const img of imgs){img.scrollIntoView({behavior:'instant',block:'center'});await new Promise(r=>setTimeout(r,200))}
          });
          await page.waitForTimeout(2000);
          const imgData=await page.evaluate(()=>{
            return [...document.querySelectorAll('img[src*="uploads"]')].map(img=>{
              const r=img.getBoundingClientRect();
              return{src:img.src.slice(-60),complete:img.complete,naturalWidth:img.naturalWidth,
                     visible:r.width>0&&r.height>0,inViewport:r.top<innerHeight&&r.bottom>0};
            });
          });
          const byUrl={};
          for(const img of imgData){
            const key=img.src;
            if(!byUrl[key])byUrl[key]={...img,occurrences:1};
            else byUrl[key].occurrences++;
          }
          const uniqueUrls=Object.keys(byUrl).length;
          const brokenUrls=Object.values(byUrl).filter(i=>!i.complete||i.naturalWidth===0);
          checked.push({page:'shop',uniqueImageUrls:uniqueUrls,brokenImages:brokenUrls.length});
          if(brokenUrls.length>0)
            issues.push({page:'shop',type:'broken_product_images',count:brokenUrls.length,urls:brokenUrls.map(b=>b.src)});
        }
      }catch(e){
        issues.push({page:'shop',type:'image_check_error',msg:e.message.slice(0,100)});
      }
      await ctx.close();
    }
  }

  await browser.close();

  // summary — preserved evidence file audit-v3-results.json is never overwritten
  const blocking=issues.filter(i=>i.blocking).length;
  fs.writeFileSync(RESULTS,JSON.stringify({
    mode:REGRESSIONS_ONLY?'regressions':'full',
    pages:PAGES.length,issues,http_fails,checked,console_errors,
    summary:{total_issues:issues.length,blocking_http:http_fails.length,blocking,
             unique_issue_types:[...new Set(issues.map(i=>i.type))]}
  },null,1));
  const verdict=http_fails.length>0?'BLOCKED':(issues.length>0?'FAIL':'PASS');
  console.log(`AUDIT v3-r2 (${REGRESSIONS_ONLY?'regressions':'full'}) COMPLETE | pages=${PAGES.length} issues=${issues.length} http_fails=${http_fails.length}`);
  console.log(`RESULT: ${verdict}`);
  const types={};issues.forEach(i=>types[i.type]=(types[i.type]||0)+1);
  console.log('Issue types:',JSON.stringify(types));
  for(const i of issues.slice(0,15))
    console.log(`  [${i.page||'-'}] ${i.type} ${i.vp||''}${i.mode?' '+i.mode:''} ${JSON.stringify({msg:i.msg,status:i.status,detail:i.detail}).slice(0,120)}`);
  // Exit codes: 2 = blocking HTTP failures, 1 = non-blocking issues, 0 = pass.
  process.exitCode=http_fails.length>0?2:(issues.length>0?1:0);
})();
