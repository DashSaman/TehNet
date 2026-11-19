'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict'),{chromium}=require('playwright');
const phase=process.argv[2],lab=process.argv[3],origin='http://localhost:18085';
const manifest=JSON.parse(fs.readFileSync('seo/index-decision-2026-11-08-v2/activation-manifest.json','utf8'));
const expected=manifest.targets.map(t=>origin+t.path).sort(),labels=[];
const ck=(v,label)=>{assert.ok(v,label);labels.push(label);};
(async()=>{const browser=await chromium.launch({headless:true});try{
 const ctx=await browser.newContext({userAgent:'Googlebot (synthetic fixture verification only)'});
 await ctx.route('**/*',r=>r.request().url().startsWith(origin+'/')&&r.request().method()==='GET'?r.continue():r.abort());
 for(const url of expected){const r=await ctx.request.get(url);ck(r.status()===200,phase+' approved canonical200 '+new URL(url).pathname);const body=await r.text(),meta=body.match(/<meta name=['"]robots['"] content=['"]([^'"]*)/i)?.[1]||'',canonical=body.match(/<link rel=['"]canonical['"] href=['"]([^'"]*)/i)?.[1]||'';ck(canonical===url,phase+' exact self canonical '+new URL(url).pathname);ck(phase==='active'?!/noindex|nofollow/i.test(meta):/noindex/i.test(meta),phase+' expected HTML robots '+new URL(url).pathname);if(phase==='active')ck(!/noindex/i.test(r.headers()['x-robots-tag']||''),'No conflicting HTTP noindex '+new URL(url).pathname);}
 const root=await ctx.request.get(origin+'/wp-sitemap.xml');
 if(phase==='active'){
  ck(root.status()===200,'Enabled core XML sitemap200');const xml=await root.text();const children=[...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m=>m[1].replaceAll('&amp;','&'));ck(children.length===1&&children[0]===origin+'/wp-sitemap-posts-page-1.xml','Only page provider; no user/taxonomy/post/product sitemap');
  const r=await ctx.request.get(children[0]);ck(r.status()===200,'Actual page sitemap200');const locations=[...(await r.text()).matchAll(/<loc>([^<]+)<\/loc>/g)].map(m=>m[1].replaceAll('&amp;','&'));ck(JSON.stringify([...new Set(locations)].sort())===JSON.stringify(expected)&&locations.length===16,'Sitemap contains exact16 canonical URLs once; no hidden/private URLs');
  for(const path of ['/shop/','/cart-2/','/tn-checkout/','/tn-account/','/support/','/b2b/','/learn/','/lab/','/amirreza-golavar/','/services/?tn_preview=1','/services/?tn_service_context=server-scoping','/support/?tn_ticket=sent','/?s=synthetic','/missing-synthetic-page/']){
   const res=await ctx.request.get(origin+path);const text=await res.text();ck(/noindex/i.test(res.headers()['x-robots-tag']||'')||/<meta name=['"]robots['"] content=['"][^'"]*noindex/i.test(text),'Private/unlisted/query route retains noindex '+path);
  }
  const robots=await ctx.request.get(origin+'/robots.txt'),text=await robots.text();ck(robots.status()===200&&text.includes('Sitemap: '+origin+'/wp-sitemap.xml'),'Real robots response discovers scoped sitemap');ck(!/^Disallow:\s*\/\s*$/m.test(text),'Fixture robots permits ordinary canonical crawl');ck(text.includes('Disallow: /wp-admin/')&&text.includes('Allow: /wp-admin/admin-ajax.php'),'Existing admin crawl controls retained');
  fs.writeFileSync(lab+'/web/wp-content/tn-fixture-conflict-flag','synthetic only');try{const conflict=await ctx.request.get(origin+'/services/network-tehran/');ck(/<meta name=['"]robots['"] content=['"][^'"]*noindex/i.test(await conflict.text()),'Unrelated plugin noindex is NOT stripped: conflict would block live activation acceptance');}finally{fs.unlinkSync(lab+'/web/wp-content/tn-fixture-conflict-flag');}
 }else ck(root.status()===404,'OFF/restored core sitemap404');
 await ctx.close();console.log('TN_INDEX_HTTP '+JSON.stringify({status:'PASS',phase,checks:labels.length,labels,production_mutations:0,screenshots_exported:0,real_google_crawl:'NOT_TESTED',independent_software_tunnels:'UNCHANGED_NOT_EMULATED'}));
}finally{await browser.close();}})().catch(e=>{console.error('TN_INDEX_HTTP '+JSON.stringify({status:'FAIL',phase,label:e.message.slice(0,700)}));process.exitCode=1;});
