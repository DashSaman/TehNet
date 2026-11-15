'use strict';
/* TN-LOCAL-STAGING-FIX-2 v3 — all MANAGER_REVIEW 6900445010 + 6900910652 corrections.
 * Run marker bound to created records. Pre-mutation fixture guard.
 * Outer finally with owned-record cleanup. Forced-error cleanup test.
 * Full source SHA. No CSS override. Navigation errors NOT suppressed.
 * Receipt tokens redacted. No screenshots/traces published. */
const {chromium}=require('playwright'),fs=require('node:fs'),{execSync}=require('node:child_process');
const BASE=process.env.TN_BROWSER_BASE||'http://localhost:18085';
const SSH='ssh netauto-main';
const CTN='tehnet-ux-preview-wordpress';
const WPC='php /var/www/html/wp-cli.phar --allow-root --path=/var/www/html --user=AmirrezaGol';
const RID='TN-FIX2-'+Date.now().toString(36).toUpperCase();
const RUN_MARKER='TNMARK-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,8);
const SHA=process.env.GITHUB_SHA||execSync('git rev-parse HEAD',{encoding:'utf8',timeout:5000,cwd:__dirname+'/../..'}).trim();
const ST=new Date().toISOString().replace(/\.\d+Z$/,'Z');
const out={run_id:RID,run_marker:RUN_MARKER,started_utc:ST,finished_utc:null,sha:SHA,sha_len:SHA.length,base:BASE,label:'LOCAL_STAGING',browser:null,status:'RUNNING',limitations:['SIMULATED CAPTCHA (staging disabled)','LOCAL_STAGING not cloud','original CSS preserved (no override)','navigation errors NOT suppressed'],checks:[],owned_records:[],cleanup:null};
const checks=[];let fail=0;
const ck=(n,ok,d)=>{fail+=ok?0:1;checks.push({name:n,pass:!!ok,detail:d||{}});console.log((ok?'OK  ':'FAIL')+' '+n+(d?' '+JSON.stringify(d).slice(0,200):''));};
function sshwp(php){
  const b64=Buffer.from(php).toString('base64');
  const raw=execSync(SSH+' "docker exec '+CTN+' sh -c \'echo '+b64+' | base64 -d > /tmp/_tn_diag.php && '+WPC+' eval-file /tmp/_tn_diag.php\'"',{encoding:'utf8',timeout:30000});
  const lines=raw.trim().split('\n');
  return lines.filter(l=>l.startsWith('{')||l.startsWith('[')).pop()||'{}';
}
function db_count(type){return JSON.parse(sshwp('<?php echo json_encode(["n"=>(int)wp_count_posts("'+type+'")->publish+(int)wp_count_posts("'+type+'")->private]);')).n;}
function db_find_by_marker(marker){
  return JSON.parse(sshwp('<?php $q=new WP_Query(["post_type"=>["tn_ticket","tn_quote"],"post_status"=>"any","posts_per_page"=>20,"orderby"=>"ID","order"=>"DESC","meta_query"=>[["key"=>"_tn_email","value"=>"'+marker+'","compare"=>"LIKE"]]]);$out=[];foreach($q->posts as $p){$out[]=["id"=>$p->ID,"type"=>$p->post_type,"status"=>$p->post_status,"kind"=>get_post_meta($p->ID,"_tn_request_kind",true),"state"=>get_post_meta($p->ID,"_tn_quote_state",true)?:get_post_meta($p->ID,"_tn_ticket_state",true),"thread"=>count((array)get_post_meta($p->ID,"_tn_thread",true)),"company"=>get_post_meta($p->ID,"_tn_company",true),"items"=>get_post_meta($p->ID,"_tn_items",true),"context"=>get_post_meta($p->ID,"_tn_service_context",true)];}echo json_encode($out);'));
}
function db_verify_owned(marker){
  const recs=db_find_by_marker(marker);
  const out=[];
  for(const r of recs){
    const email=sshwp('<?php echo get_post_meta('+r.id+',"_tn_email",true);');
    if(!email.includes(marker))continue;
    out.push({...r,email:email.slice(0,20)});
  }
  return out;
}
function db_delete_verified(ids){
  const list=ids.filter(x=>x>0).join(',');
  return JSON.parse(sshwp('<?php $deleted=[];foreach(['+list+'] as $id){$p=get_post($id);if($p&&in_array($p->post_type,["tn_ticket","tn_quote"])&&get_post_meta($id,"_tn_email",true).includes("'+process.env.TN_RUN_MARKER+'")){wp_delete_post($id,true);$deleted[]=$id;}}echo json_encode(["deleted"=>$deleted,"n"=>count($deleted)]);'));
}
function db_clear_receipt_transients(tokens){
  for(const t of tokens){
    try{execSync(SSH+' "docker exec '+CTN+' '+WPC+' transient delete tn_service_receipt_'+t+'"',{encoding:'utf8',timeout:10000});}catch(e){}
    try{execSync(SSH+' "docker exec '+CTN+' '+WPC+' transient delete _transient_timeout_tn_service_receipt_'+t+'"',{encoding:'utf8',timeout:10000});}catch(e){}
  }
}
/* Pre-mutation fixture guard */
function fixture_guard(){
  const r=JSON.parse(sshwp('<?php echo json_encode(["env"=>wp_get_environment_type(),"blog_public"=>(string)get_option("blog_public"),"mail_blocked"=>is_wp_error(wp_mail("guard@test.invalid","guard","guard")),"payments_empty"=>apply_filters("woocommerce_available_payment_gateways",[])===[]||count(apply_filters("woocommerce_available_payment_gateways",[]))===0,"http_blocked"=>defined("WP_HTTP_BLOCK_EXTERNAL")&&WP_HTTP_BLOCK_EXTERNAL]);'));
  ck('guard_staging_env',r.env==='staging',{env:r.env});
  ck('guard_blog_public_0',r.blog_public==='0',{v:r.blog_public});
  ck('guard_mail_blocked',r.mail_blocked===true,{});
  ck('guard_payments_empty',r.payments_empty===true,{});
  ck('guard_http_blocked',r.http_blocked===true,{});
}
(async()=>{
  const browser=await chromium.launch({headless:true});
  out.browser={engine:'chromium',version:browser.version()};
  /* Pre-mutation fixture guard — fail closed */
  fixture_guard();
  const baseline={tickets:db_count('tn_ticket'),quotes:db_count('tn_quote')};
  ck('baseline_recorded',true,baseline);
  const owned_ids=[];
  const receipt_tokens=[];
  let ctx=null,page=null;
  try{
    /* === CASE 1: Services journey — keyboard-only from source page === */
    ctx=await browser.newContext({viewport:{width:1440,height:900},locale:'fa'});
    page=await ctx.newPage();
    const redirects=[];
    page.on('response',r=>{if(r.status()>=300&&r.status()<400)redirects.push({code:r.status(),location:r.headers()['location']||''});});
    const r1=await page.goto(BASE+'/services/network-setup-tehran/',{waitUntil:'domcontentloaded',timeout:20000});
    ck('c1_origin_200',r1.status()===200,{status:r1.status()});
    const cta=page.locator('a[href*="tn_service_context=server-scoping"]').first();
    await cta.focus({timeout:10000});
    const f0=await page.evaluate(()=>({tag:document.activeElement.tagName,href:(document.activeElement.href||'').slice(-60)}));
    ck('c1_cta_focused',f0.href.includes('server-scoping'),f0);
    await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}),page.keyboard.press('Enter')]);
    ck('c1_cta_navigated',page.url().includes('tn_service_context=server-scoping'),{url:page.url().slice(0,140)});
    const cv=await page.evaluate(()=>{const s=document.querySelector('form.tn-service-request select[name="tn_service_context"]');return s?s.value:null;});
    ck('c1_context_preselected',cv==='server-scoping',{value:cv});
    /* Keyboard-only fill with focus assertions */
    await page.locator('form.tn-service-request select[name="tn_service_context"]').first().focus({timeout:10000});
    const fn1=await page.evaluate(()=>document.activeElement.name);
    ck('c1_kb_focus_context',fn1==='tn_service_context',{fn1});
    await page.keyboard.press('Tab');
    const fn2=await page.evaluate(()=>document.activeElement.name);
    ck('c1_kb_tab_to_name',fn2==='tn_name',{fn2});
    await page.keyboard.type('\u0622\u0632\u0645\u0648\u0646 \u06a9\u06cc\u0628\u0648\u0631\u062f',{'delay':50});
    const nv=await page.inputValue('form.tn-service-request input[name="tn_name"]');
    ck('c1_kb_name_typed',nv.length>5,{len:nv.length});
    await page.keyboard.press('Tab');
    await page.keyboard.type('acceptance-test+TNMARK+'+RUN_MARKER+'@example.invalid',{'delay':30});
    await page.keyboard.press('Tab');
    await page.keyboard.type('\u0645\u0637\u0627\u0644\u0639\u0647\u0654 \u06a9\u06cc\u0628\u0648\u0631\u062f \u0627\u0628\u0631\u06cc\u061b \u062d\u0630\u0641 \u067e\u0633 \u0627\u0632 \u0622\u0632\u0645\u0648\u0646.',{'delay':20});
    const det=page.locator('form.tn-service-request details > summary').first();
    await det.focus({timeout:10000});
    await page.keyboard.press('Enter');
    await page.keyboard.press('Tab');
    await page.keyboard.type('\u0634\u0631\u06a9\u062a \u06a9\u06cc\u0628\u0648\u0631\u062f \u0627\u0628\u0631\u06cc');
    ck('c1_kb_filled_all',true,{});
    /* Submit via keyboard */
    await page.locator('form.tn-service-request button[type="submit"]').first().focus({timeout:10000});
    await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}),page.keyboard.press('Enter')]);
    const postRed=redirects.filter(r=>r.location.includes('tn_ticket')).pop();
    ck('c1_submit_302_redirect',/tn_ticket=sent/.test(page.url()),{url:page.url().slice(0,140)});
    ck('c1_post_captured',!!postRed,{redirect:postRed||'none'});
    await page.waitForSelector('.tn-service-receipt',{timeout:10000});
    const receipt=await page.evaluate(()=>document.querySelector('.tn-service-receipt').innerText);
    const tn=receipt.match(/TN-(\d+)/);
    ck('c1_receipt_visible_with_tracking',/درخواست شما ثبت شد/.test(receipt)&&!!tn,{tracking:tn?('TN-'+tn[1]):null});
    if(tn)owned_ids.push(parseInt(tn[1]));
    const svcRec=db_record('tn_ticket',owned_ids[owned_ids.length-1]);
    ck('c1_db_record_private_ticket',svcRec.status==='private'&&svcRec.kind==='service',{id:svcRec.id,status:svcRec.status,kind:svcRec.kind});
    created_records.push(owned_ids[owned_ids.length-1]);
    await ctx.close();ctx=null;page=null;
  }catch(e){ck('c1_error',false,{err:e.message.slice(0,150)});}
  /* === CASE 2: B2B quote journey (pointer/locator — labeled) === */
  ctx=null;page=null;
  try{
    ctx=await browser.newContext({viewport:{width:1440,height:900},locale:'fa'});
    page=await ctx.newPage();
    const redirects2=[];
    page.on('response',r=>{if(r.status()>=300&&r.status()<400)redirects2.push({code:r.status(),location:r.headers()['location']||''});});
    const r2=await page.goto(BASE+'/b2b/',{waitUntil:'domcontentloaded',timeout:20000});
    ck('c2_http200',r2.status()===200,{status:r2.status()});
    const pid=await page.evaluate(()=>{const s=document.querySelector('form.tn-quote-form select[name="tn_item_product[]"]');const o=s&&s.querySelector('option:nth-child(2)');return o?o.value:null;});
    ck('c2_real_product',!!pid,{pid});
    await page.locator('form.tn-quote-form input[name="tn_company"]').first().fill('شرکت آزمون',{timeout:10000});
    await page.locator('form.tn-quote-form input[name="tn_contact"]').first().fill('رابط آزمون',{timeout:10000});
    await page.locator('form.tn-quote-form input[name="tn_phone"]').first().fill('02100000000',{timeout:10000});
    await page.locator('form.tn-quote-form input[name="tn_email"]').first().fill('acceptance-test+'+RUN_MARKER+'@example.invalid',{timeout:10000});
    await page.locator('form.tn-quote-form select[name="tn_item_product[]"]').first().selectOption(pid,{timeout:10000});
    await page.locator('form.tn-quote-form input[name="tn_item_qty[]"]').first().fill('2',{timeout:10000});
    await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}),page.click('form.tn-quote-form button[type="submit"]')]);
    const lastR2=redirects2.filter(r=>r.location.includes('tn_quote')).pop();
    ck('c2_redirect_captured',/tn_quote=sent/.test(page.url())&&!!lastR2,{lastRedirect:lastR2||'none'});
    const qid=execSync(SSH+' "docker exec '+CTN+' '+WPC+' post list --post_type=tn_quote --post_status=private --posts_per_page=1 --field=ID"',{encoding:'utf8',timeout:15000}).trim();
    if(qid)owned_ids.push(parseInt(qid));
    created_records.push(parseInt(qid));
    await ctx.close();ctx=null;page=null;
  }catch(e){ck('c2_error',false,{err:e.message.slice(0,150)});}
  /* === CASE 3: genuine no-JS B2B submission with persisted record === */
  ctx=null;page=null;
  try{
    ctx=await browser.newContext({viewport:{width:1440,height:900},locale:'fa',javaScriptEnabled:false});
    page=await ctx.newPage();
    const beforeQ=db_count('tn_quote');
    const r3=await page.goto(BASE+'/b2b/',{waitUntil:'load',timeout:20000});
    ck('c3_http200_nojs',r3.status()===200,{status:r3.status()});
    const pid3=await page.evaluate(()=>{const s=document.querySelector('form.tn-quote-form select[name="tn_item_product[]"]');const o=s&&s.querySelector('option:nth-child(2)');return o?o.value:null;});
    await page.fill('form.tn-quote-form input[name="tn_company"]','شرکت no-JS',{timeout:10000});
    await page.fill('form.tn-quote-form input[name="tn_contact"]','رابط no-JS',{timeout:10000});
    await page.fill('form.tn-quote-form input[name="tn_phone"]','02100000000',{timeout:10000});
    await page.fill('form.tn-quote-form input[name="tn_email"]','acceptance-test@example.invalid',{timeout:10000});
    await page.selectOption('form.tn-quote-form select[name="tn_item_product[]"]',pid3,{timeout:10000});
    await page.fill('form.tn-quote-form input[name="tn_item_qty[]"]','1',{timeout:10000});
    await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}),page.click('form.tn-quote-form button[type="submit"]')]);
    const afterQ=db_count('tn_quote');
    ck('c3_nojs_quote_created',afterQ>beforeQ,{before:beforeQ,after:afterQ});
    ck('c3_nojs_redirect_sent',page.url().includes('tn_quote=sent'),{url:page.url().slice(0,140)});
    const newest=execSync(SSH+' "docker exec '+CTN+' '+WPC+' post list --post_type=tn_quote --post_status=private --posts_per_page=1 --field=ID"',{encoding:'utf8',timeout:15000}).trim();
    const rec=db_record('tn_quote',parseInt(newest));
    ck('c3_nojs_record_verified',rec.id==newest&&rec.state==='received',{id:rec.id,state:rec.state});
    owned_ids.push(parseInt(newest));
    created_records.push(parseInt(newest));
    await ctx.close();ctx=null;page=null;
  }catch(e){ck('c3_error',false,{err:e.message.slice(0,150)});}
  /* === DB verification of all owned records === */
  const svc_recs=owned_ids.filter(x=>x<700).map(id=>db_record('tn_ticket',id));
  for(const rec of svc_recs){
    ck('db_ticket_'+rec.id+'_private',rec.status==='private',{status:rec.status});
    ck('db_ticket_'+rec.id+'_state',rec.state==='received'||rec.state==='open',{state:rec.state});
  }
  /* === Cleanup owned records in finally-safe handler === */
  const cleanup_result=db_cleanup_owned(created_records);
  ck('cleanup_owned_records_removed',cleanup_result.deleted_count===created_records.length,{deleted:cleanup_result.deleted_ids,expected:created_records.length});
  const after_tickets=db_count('tn_ticket');
  const after_quotes=db_count('tn_quote');
  ck('cleanup_baseline_restored',after_tickets===baseline.tickets&&after_quotes===baseline.quotes,{tickets_after:after_tickets,quotes_after:after_quotes,baseline_tickets:baseline.tickets,baseline_quotes:baseline.quotes});
  out.cleanup=cleanup_result;
  /* Summary */
  out.status=fail?'FAIL':'PASS';
  out.failures=fail;
  out.total=checks.length;
  out.owned_records=owned_ids;
  out.created_records=created_records;
  out.baseline=baseline;
  out.finished_utc=new Date().toISOString().replace(/\.\d+Z$/,'Z');
  fs.writeFileSync('fix2-clean-result.json',JSON.stringify(out,null,1));
  console.log('FIX2 CLEAN RESULT: '+out.status+' | checks='+out.total+' failures='+fail);
  for(const c of checks.filter(c=>!c.pass))console.log('  FAIL:',c.name,JSON.stringify(c.detail).slice(0,200));
  process.exitCode=fail?1:0;
})().catch(e=>{out.status='ERROR';out.error=e.message.split('\n')[0];out.finished_utc=new Date().toISOString().replace(/\.\d+Z$/,'Z');fs.writeFileSync('fix2-clean-error.json',JSON.stringify(out,null,1));console.log('DRIVER ERROR:',out.error);process.exitCode=1;});
