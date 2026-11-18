'use strict';
const {chromium}=require('playwright'),fs=require('node:fs');
const BASE='http://localhost:18085';
const checks=[];let fail=0;
const ck=(n,ok,d)=>{fail+=ok?0:1;checks.push({name:n,pass:!!ok,detail:d||{}});};
(async()=>{
  const b=await chromium.launch({headless:true});
  for(const [n,u,sel] of [['services','/services/?tn_service_context=server-scoping','form.tn-service-request'],['b2b','/b2b/','form.tn-quote-form'],['support','/support/','form.tn-ticket-form']]){
    const c=await b.newContext({viewport:{width:320,height:568},locale:'fa'});
    const p=await c.newPage();
    const r=await p.goto(BASE+u,{waitUntil:'domcontentloaded',timeout:20000});
    ck('m320_'+n+'_200',r.status()===200,{status:r.status()});
    ck('m320_'+n+'_form',await p.evaluate(s=>!!document.querySelector(s),sel));
    const ov=await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
    ck('m320_'+n+'_no_overflow',ov<=0,{px:ov});
    await c.close();
  }
  {
    const c=await b.newContext({viewport:{width:1440,height:900},locale:'fa'});
    const p=await c.newPage();
    await p.goto(BASE+'/b2b/',{waitUntil:'domcontentloaded',timeout:20000});
    const tgl=await p.$('.tn-theme-toggle');
    if(tgl){await tgl.click();await p.waitForTimeout(300);
      const theme=await p.evaluate(()=>document.documentElement.dataset.theme);
      ck('b2b_dark_toggle',theme==='dark',{theme});
      ck('b2b_dark_form_still_present',await p.evaluate(()=>!!document.querySelector('form.tn-quote-form')));
    } else ck('b2b_dark_toggle_found',false);
    await c.close();
  }
  {
    const c=await b.newContext({viewport:{width:1440,height:900},locale:'fa',javaScriptEnabled:false});
    const p=await c.newPage();
    await p.goto(BASE+'/b2b/',{waitUntil:'load',timeout:20000});
    const res=await p.evaluate(()=>{const f=document.querySelector('form.tn-quote-form');return{present:!!f,actionOk:f?String(f.getAttribute('action')).indexOf('admin-post.php')>0:false,method:f?f.method:null,submitBtn:!!(f&&f.querySelector('button[type="submit"]'))};});
    ck('b2b_nojs_form_html_post',res.present&&res.actionOk&&res.method==='post'&&res.submitBtn,res);
    const p2=await c.newPage();
    await p2.goto(BASE+'/support/',{waitUntil:'load',timeout:20000});
    const res2=await p2.evaluate(()=>{const f=document.querySelector('form.tn-ticket-form');return{present:!!f,method:f?f.method:null,submitBtn:!!(f&&f.querySelector('button[type="submit"]'))};});
    ck('support_nojs_form_html_post',res2.present&&res2.method==='post'&&res2.submitBtn,res2);
    await c.close();
  }
  fs.writeFileSync('case4-matrix.json',JSON.stringify({status:fail?'FAIL':'PASS',total:checks.length,failures:fail,checks},null,1));
  console.log('CASE4 MATRIX | RESULT:',fail?'FAIL':'PASS','| checks:',checks.length,'failures:',fail);
  for(const c of checks.filter(c=>!c.pass))console.log('  FAIL:',c.name,JSON.stringify(c.detail).slice(0,120));
  process.exitCode=fail?1:0;
})().catch(e=>{console.log('ERR:',e.message.split('\n')[0]);process.exit(1);});
