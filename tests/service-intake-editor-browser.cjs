const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const {chromium}=require('playwright');
const OUT=process.argv[2];
const base='http://localhost:18085';
(async()=>{
 const credentials=JSON.parse(fs.readFileSync(0,'utf8'));
 assert.equal(process.env.TN_NATIVE_PREVIEW_ISOLATED,'1','Independent native isolation verification required');
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const ctx=await browser.newContext({viewport:{width:1440,height:1000}});
 const page=await ctx.newPage();const external=new Set();const errors=[];const pending=new Map();const cache=new Map();
 page.on('dialog',d=>d.accept());
 page.on('response',async r=>{const u=new URL(r.url());if(r.status()===200&&u.origin===base&&/^\/(wp-includes|wp-content)\//.test(u.pathname)&&/\.(js|css|woff2?|png|svg)(?:$)/.test(u.pathname)){try{cache.set(r.url(),{status:200,contentType:r.headers()['content-type'],body:await r.body()});}catch{}}});
 page.on('request',r=>pending.set(r,r.method()+' '+new URL(r.url()).pathname));page.on('requestfinished',r=>pending.delete(r));page.on('requestfailed',r=>pending.delete(r));
 await ctx.route('**/*',route=>{const u=new URL(route.request().url());if(u.origin!==base&&!['data:','blob:'].includes(u.protocol)){external.add(u.origin);return route.abort();}if(route.request().method()==='GET'&&cache.has(route.request().url()))return route.fulfill(cache.get(route.request().url()));return route.continue();});
 page.on('pageerror',e=>errors.push(e.message));
 const observations=[];
 try{
  for(const [key,url]of [['service','/services/voice-network-readiness/'],['lab','/lab/voice-network-checklist/']]){
   const response=await page.goto(base+url);await page.waitForLoadState('networkidle');
   await page.evaluate(()=>{document.activeElement?.blur();window.scrollTo(0,0);});
   await page.screenshot({path:path.join(OUT,key+'-desktop-full.png'),fullPage:true});
   observations.push({key,status:response.status(),h1:await page.locator('h1').count(),desktop:await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,title:document.title}))});
   await page.setViewportSize({width:375,height:812});await page.evaluate(()=>window.scrollTo(0,0));
   await page.screenshot({path:path.join(OUT,key+'-mobile-full.png'),fullPage:true});
   observations.at(-1).mobile=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));
   await page.setViewportSize({width:1440,height:1000});
  }
  await page.goto(base+'/wp-login.php?redirect_to='+encodeURIComponent(base+'/wp-admin/post.php?post=193&action=edit'));await page.locator('#user_login').fill(credentials.username);await page.locator('#user_pass').fill(credentials.password);
  await Promise.all([page.waitForURL('**/wp-admin/**',{waitUntil:'domcontentloaded',timeout:90000}),page.locator('#wp-submit').click()]);
  // Page REST writes are deliberately fenced: editor interaction is unsaved.
  await ctx.route('**/wp-json/wp/v2/pages/**',route=>['POST','PUT','PATCH','DELETE'].includes(route.request().method())?route.abort():route.continue());
  const editor=[];
  for(const [key,id]of [['service',193],['lab',194]]){
   if(new URL(page.url()).searchParams.get('post')!==String(id))await page.goto(base+'/wp-admin/post.php?post='+id+'&action=edit',{waitUntil:'domcontentloaded',timeout:90000});
   await page.waitForLoadState('networkidle',{timeout:60000});
   await page.waitForFunction(()=>window.wp?.data?.select('core/block-editor')?.getBlocks()?.length>0);
   const result=await page.evaluate(()=>{
    const blocks=wp.data.select('core/block-editor').getBlocks();
    const flat=[];const visit=items=>{for(const b of items){flat.push({name:b.name,valid:b.isValid,issues:b.validationIssues?.length||0});visit(b.innerBlocks||[]);}};visit(blocks);
    const original=wp.data.select('core/editor').getEditedPostContent();const canonical=wp.blocks.serialize(blocks);
    const first=blocks.find(b=>b.name==='core/paragraph');if(!first)throw Error('Editable paragraph missing');
    wp.data.dispatch('core/block-editor').updateBlockAttributes(first.clientId,{content:first.attributes.content+' <em>TNQA-UNSAVED-EDIT</em>'});
    const changed=wp.data.select('core/editor').getEditedPostContent();const editVerified=changed.includes('TNQA-UNSAVED-EDIT')&&wp.data.select('core/editor').isEditedPostDirty();
    wp.data.dispatch('core/block-editor').resetBlocks(blocks);
    const restored=wp.blocks.serialize(wp.data.select('core/block-editor').getBlocks())===canonical&&!wp.data.select('core/editor').getEditedPostContent().includes('TNQA-UNSAVED-EDIT');
    if(wp.data.select('core/edit-post')?.isFeatureActive?.('welcomeGuide'))wp.data.dispatch('core/edit-post').toggleFeature('welcomeGuide');
    return {count:flat.length,invalid:flat.filter(b=>b.valid===false),names:[...new Set(flat.map(b=>b.name))],title:wp.data.select('core/editor').getCurrentPost().title,content:original,dirty_after_format_normalization:wp.data.select('core/editor').isEditedPostDirty(),raw_format_differs_from_editor_serialization:canonical!==original,unsaved_block_edit_verified:editVerified,original_editor_blocks_restored:restored};
   });
   fs.writeFileSync(path.join(OUT,key+'-editor-content-private.txt'),result.content);delete result.content;
   assert.equal(result.invalid.length,0);assert(result.unsaved_block_edit_verified);assert(result.original_editor_blocks_restored);
   await page.screenshot({path:path.join(OUT,key+'-editor-private.png'),fullPage:true});editor.push({key,...result});
  }
  for(const o of observations){assert.equal(o.status,200);assert.equal(o.h1,1);assert.equal(o.desktop.width,o.desktop.scroll);assert.equal(o.mobile.width,o.mobile.scroll);}assert.equal(errors.length,0);
  fs.writeFileSync(path.join(OUT,'browser-verification.json'),JSON.stringify({scope:'Isolated native WordPress full-page and unsaved Gutenberg block-edit acceptance',observations,editor,blocked_external_origins:external.size,page_errors:errors,static_cache:'Only byte-identical public static responses observed in this browser run; no authenticated HTML or REST data cached',page_saves:0},null,2));
 }catch(e){fs.writeFileSync(path.join(OUT,'failure-page-private.html'),await page.content());fs.writeFileSync(path.join(OUT,'failure-pending-private.json'),JSON.stringify({url:page.url(),pending:[...pending.values()],errors},null,2));await page.screenshot({path:path.join(OUT,'failure-page-private.png'),fullPage:true}).catch(()=>{});throw e;}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
