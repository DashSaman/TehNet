'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {buildReport,summary}=require('../site/mu-plugins/tehnet-technical-resources/network-troubleshooting.js');
const model=Object.fromEntries(['internet','dns','dhcp','vpn','vlan','nat','gateway'].map(key=>[key,{title:key,test:'safe manual check',why:'scoped reason',source:'https://example.invalid/',observations:{unknown:{label:'not checked',advice:'collect evidence'},observed:{label:'manual observation',advice:'review, not certainty'}}}]));
test('all seven problems preserve evidence and explicitly unverified status',()=>{
 for(const problem of Object.keys(model)){
  const r=buildReport(model,{problem,scope:'one',observation:'observed'});
  assert.equal(r.status,'MANUAL_UNVERIFIED');assert.equal(r.problem,problem);assert.equal(r.observation,'observed');
  assert.match(summary(r),/تشخیص قطعی/);assert.match(summary(r),/هیچ فرمانی اجرا نشده/);
 }
});
test('unrecognized or inherited answers remain unknown and extra private fields are excluded',()=>{
 for(const value of ['__proto__','constructor','<script>','arbitrary']){
  const r=buildReport(model,{problem:'dns',scope:value,observation:value,password:'must-not-copy',ip:'must-not-copy'});
  assert.equal(r.scope,'unknown');assert.equal(r.observation,'unknown');assert.ok(!JSON.stringify(r).includes('must-not-copy'));
 }
});
test('unknown problem is rejected rather than a fabricated diagnosis',()=>{
 for(const problem of ['','constructor','__proto__','fake'])assert.throws(()=>buildReport(model,{problem}),/known problem/);
});
test('independent reports do not mutate earlier answers or source model',()=>{
 const before=JSON.stringify(model),a=buildReport(model,{problem:'dns',scope:'one',observation:'observed'});
 const b=buildReport(model,{problem:'dhcp',scope:'unknown',observation:'unknown'});
 assert.equal(a.problem,'dns');assert.equal(a.observation,'observed');assert.equal(b.observation,'unknown');assert.equal(JSON.stringify(model),before);
});
