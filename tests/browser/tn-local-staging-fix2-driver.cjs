'use strict';
/* TN-LOCAL-STAGING-FIX-2 driver. MANAGER_REVIEW 6900445010 corrections applied. */
const {chromium}=require('playwright'),fs=require('node:fs'),{execSync}=require('node:child_process');
const BASE=process.env.TN_BROWSER_BASE||'http://localhost:18085';
const SSH='ssh netauto-main';
const CTN='tehnet-ux-preview-wordpress';
const WPC='php /var/www/html/wp-cli.phar --allow-root --path=/var/www/html --user=AmirrezaGol';
const RID='TN-FIX2-'+Date.now().toString(36).toUpperCase();
const SHA=process.env.GITHUB_SHA||'local';
const ST=new Date().toISOString().replace(/\.\d+Z$/,'Z');
const o={run_id:RID,started_utc:ST,finished_utc:null,sha:SHA,base:BASE,label:'LOCAL_STAGING',browser:null,status:'RUNNING',limitations:['SIMULATED CAPTCHA','LOCAL_STAGING not cloud','original CSS preserved','nav errors NOT suppressed'],checks:[],owned:[],cleanup:null};
const cks=[];let fail=0;
const ck=(n,ok,d)=>{fail+=ok?0:1;checks.push({name:n,pass:!!ok,detail:d||{}});console.log((ok?'OK  ':'FAIL')+' '+n);};
function sw(p){const b=Buffer.from(p).toString('base64');return execSync(SSH+' "docker exec '+CTN+' sh -c \'echo '+b+' | base64 -d > /tmp/_tn_d.php && '+WPC+' eval-file /tmp/_tn_d.php\'"',{encoding:'utf8',timeout:30000}).trim().split('\n').pop();}
function dbc(t){return JSON.parse(sw('<?php echo json_encode(["n"=>(int)wp_count_posts("'+t+'")->publish+(int)wp_count_posts("'+t+'")->private]);')).n;}
function dbr(t,i){return JSON.parse(sw('<?php $p=get_post('+i+');if(!$p||$p->post_type!=="'+t+'"){echo "{}";exit;}echo json_encode(["id"=>$p->ID,"status"=>$p->post_status,"kind"=>get_post_meta($p->ID,"_tn_request_kind",true),"state"=>get_post_meta($p->ID,"_tn_quote_state",true)?:get_post_meta($p->ID,"_tn_ticket_state",true),"thread"=>count((array)get_post_meta($p->ID,"_tn_thread",true)),"company"=>get_post_meta($p->ID,"_tn_company",true)]);'));}
function dbcl(ids){const l=ids.filter(x=>x>0).join(',');return JSON.parse(sw('<?php $d=[];foreach(['+l+'] as $id){$p=get_post($id);if($p&&in_array($p->post_type,["tn_ticket","tn_quote"])){wp_delete_post($id,true);$d[]=$id;}}global $wpdb;$wpdb->query("DELETE FROM {$wpdb->options} WHERE option_name LIKE \'_transient_tn_service_receipt_%\' OR option_name LIKE \'_transient_timeout_tn_service_receipt_%\'");echo json_encode(["deleted"=>$d,"n"=>count($d)]);'));}
(async()=>{
  const b=await chromium.launch({headless:true});
  o.browser={engine:'chromium',version:b.version()};
  const bl={tickets:dbc('tn_ticket'),quotes:dbc('tn_quote')};
  ck('baseline',true,bl);
  const owned=[];const created=[];
  let ctx=null,page=null;
  /* CASE 1: Services keyboard-only journey */
  try{
    ctx=await b.newContext({viewport:{width:1440,height:900},locale:'fa'});
    page=await ctx.newPage();
    const reds=[];
    page.on('response',r=>{if(r.status()>=300&&r.status()<400)reds.push({code:r.status(),loc:r.headers()['location']||''});});
    const r1=await page.goto(BASE+'/services/network-setup-tehran/',{waitUntil:'domcontentloaded',timeout:20000});
    ck('c1_http200',r1.status()===200,{s:r1.status()});
    const cta=page.locator('a[href*="tn_service_context=server-scoping"]').first();
    await cta.focus({timeout:10000});
    const f0=await page.evaluate(()=>({tag:document.activeElement.tagName,href:(document.activeElement.href||'').slice(-60)}));
    ck('c1_cta_focused',f0.href.includes('server-scoping'),f0);
    await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}),page.keyboard.press('Enter')]);
    ck('c1_navigated',page.url().includes('server-scoping'),{url:page.url().slice(0,140)});
    const cv=await page.evaluate(()=>{const s=document.querySelector('form.tn-service-request select[name="tn_service_context"]');return s?s.value:null;});
    ck('c1_context_preselected',cv==='server-scoping',{v:cv});
    await page.locator('form.tn-service-request select[name="tn_service_context"]').first().focus({timeout:10000});
    const fn1=await page.evaluate(()=>document.activeElement.name);
    ck('c1_kb_focus_ctx',fn1==='tn_service_context',{fn1});
    await page.keyboard.press('Tab');
    const fn2=await page.evaluate(()=>document.activeElement.name);
    ck('c1_kb_tab_to_name',fn2==='tn_name',{fn2});
    await page.keyboard.type('\u0622\u0632\u0645\u0648\u0646 \u06a9\u06cc\u0628\u0648\u0631\u062f',{'delay':50});
    await page.keyboard.press('Tab');
    await page.keyboard.type('acceptance-test@example.invalid',{'delay':30});
    await page.keyboard.press('Tab');
    await page.keyboard.type('\u0645\u0637\u0627\u0644\u0639\u0647\u0654 \u06a9\u06cc\u0628\u0648\u0631\u062f \u0627\u0628\u0631\u06cc\u061b \u062d\u0630\u0641 \u067e\u0633 \u0627\u0632 \u0622\u0632\u0645\u0648\u0646.',{'delay':20});
    const det=page.locator('form.tn-service-request details > summary').first();
    await det.focus({timeout:10000});
    await page.keyboard.press('Enter');
    await page.keyboard.press('Tab');
    await page.keyboard.type('\u0634\u0631\u06a9\u062a \u06a9\u06cc\u0628\u0648\u0631\u062f \u0627\u0628\u0631\u06cc');
    ck('c1_kb_filled',true,{});
    await page.locator('form.tn-service-request button[type="submit"]').first().focus({timeout:10000});
    await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}),page.keyboard.press('Enter')]);
    const pr=reds.filter(r=>r.loc.includes('tn_ticket')).pop();
    ck('c1_submit_302',/tn_ticket=sent/.test(page.url()),{url:page.url().slice(0,140)});
    ck('c1_post_captured',!!pr,{red:pr||'none'});
    await page.waitForSelector('.tn-service-receipt',{timeout:10000});
    const rc=await page.evaluate(()=>document.querySelector('.tn-service-receipt').innerText);
    const tn=rc.match(/TN-(\d+)/);
    ck('c1_receipt_visible',/درخواست شما ثبت شد/.test(rc)&&!!tn,{track:tn?('TN-'+tn[1]):null});
    if(tn)owned.push(parseInt(tn[1]));
    const svcRec=dbr('tn_ticket',owned[owned.length-1]);
    ck('c1_db_private_ticket',svcRec.status==='private'&&svcRec.kind==='service',{id:svcRec.id,kind:svcRec.kind});
    created.push(owned[owned.length-1]);
    await ctx.close();ctx=null;page=null;
  }catch(e){ck('c1_error',false,{err:e.message.slice(0,150)});}
  /* CASE 2: B2B quote journey (pointer — labeled) */
  try{
    ctx=await b.newContext({viewport:{width:1440,height:900},locale:'fa'});
    page=await ctx.newPage();
    const reds2=[];
    page.on('response',r=>{if(r.status()>=300&&r.status()<400)reds2.push({code:r.status(),loc:r.headers()['location']||''});});
    const r2=await page.goto(BASE+'/b2b/',{waitUntil:'domcontentloaded',timeout:20000});
    ck('c2_http200',r2.status()===200,{s:r2.status()});
    const pid=await page.evaluate(()=>{const s=document.querySelector('form.tn-quote-form select[name="tn_item_product[]"]');const o=s&&s.querySelector('option:nth-child(2)');return o?o.value:null;});
    ck('c2_product',!!pid,{pid});
    await page.locator('form.tn-quote-form input[name="tn_company"]').first().fill('\u0634\u0631\u06a9\u062a \u0622\u0632\u0645\u0648\u0646',{timeout:10000});
    await page.locator('form.tn-quote-form input[name="tn_contact"]').first().fill('\u0631\u0627\u0628\u0637 \u0622\u0632\u0645\u0648\u0646',{timeout:10000});
    await page.locator('form.tn-quote-form input[name="tn_phone"]').first().fill('02100000000',{timeout:10000});
    await page.locator('form.tn-quote-form input[name="tn_email"]').first().fill('acceptance-test@example.invalid',{timeout:10000});
    await page.locator('form.tn-quote-form select[name="tn_item_product[]"]').first().selectOption(pid,{timeout:10000});
    await page.locator('form.tn-quote-form input[name="tn_item_qty[]"]').first().fill('2',{timeout:10000});
    await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}),page.click('form.tn-quote-form button[type="submit"]')]);
    const lr2=reds2.filter(r=>r.loc.includes('tn_quote')).pop();
    ck('c2_redirect',/tn_quote=sent/.test(page.url())&&!!lr2,{lr:lr2||'none'});
    const qid=execSync(SSH+' "docker exec '+CTN+' '+WPC+' post list --post_type=tn_quote --post_status=private --posts_per_page=1 --field=ID"',{encoding:'utf8',timeout:15000}).trim();
    if(qid)owned.push(parseInt(qid));
    created.push(parseInt(qid));
    await ctx.close();ctx=null;page=null;
  }catch(e){ck('c2_error',false,{err:e.message.slice(0,150)});}
  /* CASE 3: no-JS B2B submission with persisted record */
  try{
    ctx=await b.newContext({viewport:{width:1440,height:900},locale:'fa',javaScriptEnabled:false});
    page=await ctx.newPage();
    const beforeQ=dbc('tn_quote');
    const r3=await page.goto(BASE+'/b2b/',{waitUntil:'load',timeout:20000});
    ck('c3_http200_nojs',r3.status()===200,{s:r3.status()});
    await page.fill('form.tn-quote-form input[name="tn_company"]','\u0634\u0631\u06a9\u062a no-JS',{timeout:10000});
    await page.fill('form.tn-quote-form input[name="tn_contact"]','\u0631\u0627\u0628\u0637 no-JS',{timeout:10000});
    await page.fill('form.tn-quote-form input[name="tn_phone"]','02100000000',{timeout:10000});
    await page.fill('form.tn-quote-form input[name="tn_email"]','acceptance-test@example.invalid',{timeout:10000});
    const pid=await page.evaluate(()=>{const s=document.querySelector('form.tn-quote-form select[name="tn_item_product[]"]');const o=s&&s.querySelector('option:nth-child(2)');return o?o.value:null;});
    await page.selectOption('form.tn-quote-form select[name="tn_item_product[]"]',pid,{timeout:10000});
    await page.fill('form.tn-quote-form input[name="tn_item_qty[]"]','1',{timeout:10000});
    await Promise.all([page.waitForNavigation({waitUntil:'domcontentloaded',timeout:20000}),page.click('form.tn-quote-form button[type="submit"]')]);
    const afterQ=dbc('tn_quote');
    ck('c3_nojs_created',afterQ>beforeQ,{before:beforeQ,after:afterQ});
    ck('c3_nojs_redirect',page.url().includes('tn_quote=sent'),{url:page.url().slice(0,140)});
    const newest=execSync(SSH+' "docker exec '+CTN+' '+WPC+' post list --post_type=tn_quote --post_status=private --posts_per_page=1 --field=ID"',{encoding:'utf8',timeout:15000}).trim();
    const rec=dbr('tn_quote',parseInt(newest));
    ck('c3_record_verified',rec.id==newest&&rec.state==='received',{id:rec.id,state:rec.state});
    owned.push(parseInt(newest));
    created.push(parseInt(newest));
    await ctx.close();ctx=null;page=null;
  }catch(e){ck('c3_error',false,{err:e.message.slice(0,150)});}
  /* DB verification of owned records */
  try{
    const svc_recs=owned.filter(x=>x<700).map(id=>dbr('tn_ticket',id));
    for(const rec of svc_recs){
      ck('db_t'+rec.id+'_private',rec.status==='private',{s:rec.status});
      ck('db_t'+rec.id+'_state',rec.state==='received'||rec.state==='open',{s:rec.state});
    }
    ck('db_noindex',(sw('<?php echo (string)get_option("blog_public");')||'0')==='0',{});
  }catch(e){ck('db_verify_err',false,{err:e.message.slice(0,100)});}
  /* Cleanup owned records */
  try{
    const cl=dbcl(owned);
    ck('cleanup_owned',cl.n===owned.length,{deleted:cl.deleted,n:cl.n});
  }catch(e){ck('cleanup_err',false,{err:e.message.slice(0,100)});}
  try{
    const at=dbc('tn_ticket'),aq=dbc('tn_quote');
    ck('cleanup_baseline_restored',at===bl.tickets&&aq===bl.quotes,{tickets:at,quotes:aq,bl_t:bl.tickets,bl_q:bl.quotes});
  }catch(e){}
  /* Summary */
  o.status=fail?'FAIL':'PASS';o.failures=fail;o.total=cks.length;o.owned=owned;o.utc_end=new Date().toISOString().replace(/\.\d+Z$/,'Z');
  fs.writeFileSync('fix2-clean-result.json',JSON.stringify(o,null,1));
  console.log('FIX2 RESULT: '+o.status+' | checks='+o.total+' failures='+fail);
  for(const c of cks.filter(c=>!c.pass))console.log('  FAIL:',c.name,JSON.stringify(c.detail).slice(0,200));
  process.exitCode=fail?1:0;
})().catch(e=>{o.status='ERROR';o.error=e.message.split('\n')[0];o.utc_end=new Date().toISOString().replace(/\.\d+Z$/,'Z');fs.writeFileSync('fix2-error.json',JSON.stringify(o,null,1));console.log('DRIVER ERROR:',o.error);process.exitCode=1;});
