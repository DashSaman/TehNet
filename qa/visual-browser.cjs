/* Read-only browser QA: preview modifies only the local browser DOM. */
const fs=require('fs'),path=require('path');
const puppeteer=require('/root/.npm/_npx/4b4c857f6efdfb61/node_modules/puppeteer');
const ROOT=path.resolve(__dirname,'..'),mode=process.argv[2]||'preview';
const widths=[320,375,390,768,1024,1440],report={mode,checks:[],errors:[]};
function check(name,ok,detail){report.checks.push({name,ok,detail});if(!ok)console.log('FAIL',name,JSON.stringify(detail));}
(async()=>{
 const browser=await puppeteer.launch({headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 try{
  for(const kind of ['home','profile']){
   const page=await browser.newPage();page.setDefaultNavigationTimeout(45000);
   const pageErrors=[];page.on('pageerror',e=>pageErrors.push(e.message));
   const url=mode==='preview'?'https://tehnet.ir/':kind==='home'?'https://tehnet.ir/':'https://tehnet.ir/amirreza-golavar/';
   const response=await page.goto(url,{waitUntil:'networkidle2'});check(kind+' HTTP',response.status()===200,response.status());
   if(mode==='preview'){
    const content=fs.readFileSync(path.join(ROOT,'content/pages',kind==='home'?'home.html':'amirreza-golavar.html'),'utf8');
    await page.evaluate(({content,kind})=>{
     document.body.classList.add('tn-visual');document.documentElement.classList.add('tn-js');document.documentElement.dataset.theme='dark';
     document.querySelector('main').innerHTML='<article class="'+(kind==='profile'?'tn-profile':'')+'"><div class="entry-content">'+content+'</div></article>';
     const nav=document.querySelector('.tn-site-nav');nav.id='tn-main-menu';
     const theme=document.querySelector('.tn-theme-toggle');theme.removeAttribute('onclick');theme.classList.add('tn-js-only');
     document.querySelector('.tn-header-actions').insertAdjacentHTML('beforeend','<button class="tn-menu-toggle tn-js-only" type="button" aria-label="بازکردن منو" aria-expanded="false" aria-controls="tn-main-menu"><svg viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16" fill="none" stroke="currentColor"/></svg></button>');
     document.body.insertAdjacentHTML('beforeend','<button class="tn-motion-toggle tn-js-only" id="tn-motion-toggle" type="button" aria-pressed="false">توقف حرکت‌های گرافیکی</button>');
     if(kind==='profile'){document.querySelector('.tn-site-footer')?.remove();document.querySelector('.tn-brand-strip')?.remove();}
    },{content,kind});
    await page.addStyleTag({content:fs.readFileSync(path.join(ROOT,'site/themes/tehnet/assets/css/visual-refresh.css'),'utf8')});
    await page.addScriptTag({content:fs.readFileSync(path.join(ROOT,'site/themes/tehnet/assets/js/visual-refresh.js'),'utf8')});
   }
   for(const theme of ['dark','light']){
    await page.evaluate(t=>document.documentElement.dataset.theme=t,theme);
    for(const width of widths){
     await page.setViewport({width,height:900,deviceScaleFactor:1});await new Promise(r=>setTimeout(r,120));
     const state=await page.evaluate(()=>{
      const overflow=[...document.querySelectorAll('main *,.tn-site-header *')].filter(el=>{const b=el.getBoundingClientRect(),s=getComputedStyle(el);return b.width>0&&b.height>0&&s.visibility!=='hidden'&&s.display!=='none'&&(b.left < -2||b.right>innerWidth+2)&&el.tagName!=='svg'&&!el.closest('svg');}).map(el=>({tag:el.tagName,cls:el.className,left:Math.round(el.getBoundingClientRect().left),right:Math.round(el.getBoundingClientRect().right)})).slice(0,8);
      return {h1:document.querySelectorAll('h1').length,dir:getComputedStyle(document.body).direction,bg:getComputedStyle(document.body).backgroundColor,overflow};
     });
     check(kind+' '+theme+' '+width,state.h1===1&&state.dir==='rtl'&&state.overflow.length===0,state);
     if((width===1440||width===390)&&theme==='dark')await page.screenshot({path:path.join(__dirname,`${mode}-${kind}-${width}.png`),fullPage:true});
     if(width===1440&&theme==='light')await page.screenshot({path:path.join(__dirname,`${mode}-${kind}-light.png`),fullPage:true});
    }
   }
   await page.setViewport({width:390,height:844});
   await page.evaluate(()=>window.scrollTo(0,0));
   await page.click('.tn-menu-toggle');
   check(kind+' mobile menu open',await page.$eval('.tn-menu-toggle',e=>e.getAttribute('aria-expanded')==='true'));
   await page.keyboard.press('Escape');
   check(kind+' mobile menu Escape',await page.$eval('.tn-menu-toggle',e=>e.getAttribute('aria-expanded')==='false'));
   const oldTheme=await page.evaluate(()=>document.documentElement.dataset.theme);
   await page.click('.tn-theme-toggle');
   check(kind+' theme toggle',await page.evaluate(t=>document.documentElement.dataset.theme!==t,oldTheme));
   await page.click('#tn-motion-toggle');check(kind+' pause animation',await page.evaluate(()=>document.documentElement.classList.contains('tn-motion-paused')));
   if(kind==='profile'){
    await page.click('[data-tn-filter="network"]');check('network skill filter',await page.$$eval('.tn-skill:not([hidden])',items=>items.length===6&&items.every(e=>e.dataset.group==='network')));
    await page.click('[data-tn-filter="all"]');check('all skills restored',await page.$$eval('.tn-skill:not([hidden])',items=>items.length===14));
    const printCheck=await page.evaluate(()=>{const list=[...document.querySelectorAll('.tn-work')],original=list.map(e=>e.open);window.dispatchEvent(new Event('beforeprint'));const opened=list.every(e=>e.open);window.dispatchEvent(new Event('afterprint'));return opened&&list.every((e,i)=>e.open===original[i]);});check('print state restoration',printCheck);
    const privacy=await page.evaluate(()=>{const s=document.querySelector('main').innerHTML;return !/PVNetwork|پیوی|(?:0|98)9[0-9]{9}|(?:0|98)9[0-9]{9}/i.test(s)&&!document.querySelector('a[href^="tel:"]');});check('profile privacy',privacy);
   }
   check(kind+' browser JavaScript errors',pageErrors.length===0,pageErrors);await page.close();
  }
 }finally{await browser.close();fs.writeFileSync(path.join(__dirname,mode+'-browser-report.json'),JSON.stringify(report,null,2));}
 const failed=report.checks.filter(c=>!c.ok);console.log('BROWSER_CHECKS',report.checks.length,'FAILURES',failed.length);if(failed.length)process.exitCode=1;
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
