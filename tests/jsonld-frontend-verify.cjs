'use strict';
const {chromium}=require('playwright'),assert=require('node:assert/strict');
(async()=>{
  const browser=await chromium.launch({channel:'msedge',headless:true});
  const results={};
  try{
    for(const path of ['/learn/mikrotik/mtcna/','/lab/','/services/','/']){
      const ctx=await browser.newContext({viewport:{width:1440,height:1000}});
      const page=await ctx.newPage();
      const resp=await page.goto('http://localhost:18085'+path,{waitUntil:'domcontentloaded',timeout:60000});
      const html=await page.content();
      const scripts=[...html.matchAll(/<script type="application\/ld\+json" class="([^"]+)">([\s\S]*?)<\/script>/g)];
      const entry={status:resp.status(),blocks:{}};
      for(const[,cls,payload]of scripts){
        try{
          const d=JSON.parse(payload),e={type:d['@type']};
          if(d.mainEntity)e.items=d.mainEntity.itemListElement.length;
          entry.blocks[cls]=e;
        }catch(e){entry.blocks[cls]='BAD_JSON';}
      }
      results[path]=entry;
      await ctx.close();
    }
    console.log(JSON.stringify(results,null,1));
  }finally{await browser.close();}
})();
