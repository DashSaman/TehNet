/* Owner-authorized read-only SSR crawl + selected rendered mobile checks. No forms submitted. */
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {chromium}=require('C:/Users/amirreza/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const root=path.resolve(__dirname,'..'),out=path.join(root,'seo/audit-2026-10-16');
const inventory=JSON.parse(fs.readFileSync(path.join(out,'native-inventory.json'))),origin='https://tehnet.ir';
const normalize=u=>{try{const x=new URL(u,origin);if(x.origin!==origin||x.search||x.pathname.startsWith('/wp-')||/\.(?:jpg|png|webp|svg|pdf|zip|vcf|mp4|js|css)$/i.test(x.pathname))return null;x.hash='';return x.href;}catch{return null}};
const records=[],queue=[...new Set([origin+'/',...inventory.posts.map(x=>x.url),...inventory.terms.map(x=>x.url),...inventory.menus.map(x=>x.url)].map(normalize).filter(Boolean))],seen=new Set(queue),started=new Date().toISOString();
function extract({html,url}){
 const d=new DOMParser().parseFromString(html,'text/html'),q=s=>[...d.querySelectorAll(s)],content=s=>q(s).map(e=>e.getAttribute('content')||''),resolve=u=>{try{return new URL(u,url).href}catch{return u}};
 const schemas=q('script[type="application/ld+json"]').map(e=>{try{return {value:JSON.parse(e.textContent)}}catch{return {invalid:true,sample:e.textContent.slice(0,120)}}});
 const links=q('a[href]').map(e=>({url:resolve(e.getAttribute('href')),text:e.textContent.trim().replace(/\s+/g,' ').slice(0,120),rel:e.rel}));
 const images=q('img').map(e=>({src:resolve(e.getAttribute('src')||''),alt:e.getAttribute('alt'),width:e.getAttribute('width'),height:e.getAttribute('height'),loading:e.getAttribute('loading'),fetchpriority:e.getAttribute('fetchpriority'),srcset:!!e.getAttribute('srcset')}));
 const main=(d.querySelector('main')||d.body).cloneNode(true);main.querySelectorAll('script,style,noscript,nav,header,footer').forEach(e=>e.remove());const text=main.textContent.replace(/\s+/g,' ').trim();
 const h1=q('h1').map(e=>e.textContent.trim()),h2=q('h2').map(e=>e.textContent.trim());
 return {title:d.title,descriptions:content('meta[name="description"]'),canonicals:q('link[rel="canonical"]').map(e=>resolve(e.href)),robots:content('meta[name="robots"]'),og:{title:content('meta[property="og:title"]'),description:content('meta[property="og:description"]'),image:content('meta[property="og:image"]')},lang:d.documentElement.lang,viewport:content('meta[name="viewport"]'),h1,h2,main_chars:text.length,main_excerpt:text.slice(0,1900),text_sha256:null,schemas,links,images,model_viewers:q('model-viewer,[data-tn-spin],[data-tn-model]').map(e=>({tag:e.tagName,spin:e.hasAttribute('data-tn-spin'),model:e.getAttribute('data-tn-model')})),videos:q('video,iframe').map(e=>({tag:e.tagName,src:e.getAttribute('src')})),tables:q('table').length,details:q('details').length,author_nodes:q('[rel="author"],.author,.byline').map(e=>e.textContent.trim()),dates:q('time').map(e=>({text:e.textContent.trim(),datetime:e.getAttribute('datetime')})),analytics_scripts:q('script[src]').map(e=>e.src).filter(s=>/google-analytics|googletagmanager|clarity|matomo|plausible/i.test(s))};
}
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'msedge'}),context=await browser.newContext({viewport:{width:1440,height:1000}}),parser=await context.newPage();
 const support=[];try{
  console.log('NATIVE_URL_SEEDS='+queue.length);
  for(const suffix of ['/robots.txt','/wp-sitemap.xml','/sitemap_index.xml','/llms.txt','/not-a-real-tehnet-page-audit-20261016/']){
   try{const t=Date.now(),r=await context.request.get(origin+suffix,{timeout:25000}),h=r.headers();support.push({url:origin+suffix,status:r.status(),elapsed_ms:Date.now()-t,headers:{'content-type':h['content-type'],'x-robots-tag':h['x-robots-tag'],'cache-control':h['cache-control']},body:(await r.text()).slice(0,suffix.endsWith('.txt')?16000:300)});}catch(e){support.push({url:origin+suffix,error:e.message})}
  }
  for(let cursor=0;cursor<queue.length&&cursor<200;cursor++){
   const url=queue[cursor],t=Date.now();let record;
   try{
    const r=await context.request.get(url,{timeout:25000}),html=await r.text(),headers=r.headers(),data=await parser.evaluate(extract,{html,url});
    record={url,final_url:r.url(),status:r.status(),elapsed_ms:Date.now()-t,html_bytes:Buffer.byteLength(html),headers:{'content-type':headers['content-type'],'x-robots-tag':headers['x-robots-tag'],'cf-cache-status':headers['cf-cache-status'],'cache-control':headers['cache-control']},...data};
    record.text_sha256=crypto.createHash('sha256').update(data.main_excerpt).digest('hex');
    for(const l of data.links){const u=normalize(l.url);if(u&&!seen.has(u)){seen.add(u);queue.push(u)}}
   }catch(e){record={url,error:e.message,elapsed_ms:Date.now()-t}}
   records.push(record);
   if((cursor+1)%10===0){fs.writeFileSync(path.join(out,'public-crawl-progress.json'),JSON.stringify({started,complete:false,completed:records.length,queued:queue.length,last_url:url},null,2));console.log('CRAWL_PROGRESS '+records.length+'/'+queue.length)}
  }
  const render=[];
  for(const suffix of ['/','/learn/','/services/','/lab/','/shop/','/product/tn-sn-17929/','/amirreza-golavar/']){
   const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
   try{
    await page.setViewportSize({width:390,height:844});const t=Date.now(),r=await page.goto(origin+suffix,{waitUntil:'networkidle',timeout:40000});
    const data=await page.evaluate(()=>({title:document.title,h1:[...document.querySelectorAll('h1')].map(e=>e.innerText),overflow:document.documentElement.scrollWidth>innerWidth+2,scroll_width:document.documentElement.scrollWidth,viewport:innerWidth,broken_images:[...document.images].filter(i=>i.loading!=='lazy'&&(!i.complete||!i.naturalWidth)).map(i=>i.src),model_elements:document.querySelectorAll('model-viewer,[data-tn-spin],[data-tn-model]').length,description:[...document.querySelectorAll('meta[name="description"]')].map(e=>e.content),metrics:{navigation_ttfb_ms:performance.getEntriesByType('navigation')[0]?.responseStart,domcontentloaded_ms:performance.getEntriesByType('navigation')[0]?.domContentLoadedEventEnd},model_assets:performance.getEntriesByType('resource').filter(x=>/\.glb|\.gltf|photo-spin|model-viewer|three\.module/.test(x.name)).map(x=>x.name)}));
    const name=suffix.replace(/[^a-z0-9]/gi,'-').replace(/^-|-$/g,'')||'home';await page.screenshot({path:path.join(out,'mobile-'+name+'.png'),fullPage:false});render.push({url:origin+suffix,status:r.status(),elapsed_ms:Date.now()-t,...data,js_errors:errors});
   }catch(e){render.push({url:origin+suffix,error:e.message,js_errors:errors})}finally{await page.close()}
  }
  const result={started,finished:new Date().toISOString(),scope:'All native published content/terms/menu URLs plus discovered same-origin HTML paths; excludes query permutations, assets, admin and private content. Browser viewport390; no forms/orders/messages submitted. Request timings are one-session observations, not Core Web Vitals.',native_posts:inventory.posts.length,native_terms:inventory.terms.length,crawled:records.length,discovered:queue.length,limit:200,limit_hit:records.length<queue.length,support,pages:records,rendered_mobile:render};
  fs.writeFileSync(path.join(out,'public-crawl.json'),JSON.stringify(result,null,2));fs.rmSync(path.join(out,'public-crawl-progress.json'),{force:true});
  console.log(JSON.stringify({crawled:records.length,discovered:queue.length,errors:records.filter(x=>x.error).length,http_200:records.filter(x=>x.status===200).length,missing_description:records.filter(x=>x.status===200&&!x.descriptions?.length).length,mobile:render.map(x=>({url:x.url,status:x.status,overflow:x.overflow,error:x.error})),support:support.map(x=>({url:x.url,status:x.status,error:x.error}))}));
 }finally{await browser.close()}
})().catch(e=>{console.error(e.stack);process.exit(1)});
