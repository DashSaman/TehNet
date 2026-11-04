'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),{contains,trace,evaluate}=require('../site/mu-plugins/tehnet-technical-resources/static-routing-lab.js');
test('documentation prefixes and /30 transit are matched numerically',()=>{
 assert.equal(contains('203.0.113.0/30','203.0.113.2'),true);assert.equal(contains('203.0.113.0/30','203.0.113.9'),false);
 assert.equal(contains('192.0.2.0/24','198.51.100.10'),false);assert.equal(contains('192.0.2.0/24','192.0.2.10'),true);
});
test('all sixteen answer pairs require independently valid forward and return routes',()=>{
 for(const r1 of ['missing','wrong-network','wrong-gateway','correct'])for(const r2 of ['missing','wrong-network','wrong-gateway','correct']){
  const result=evaluate({r1,r2});assert.equal(result.forward.arrived,r1==='correct');assert.equal(result.reply.arrived,r2==='correct');
  assert.equal(result.status==='MODEL_ROUND_TRIP',r1==='correct'&&r2==='correct');
 }
});
test('one-way reachability does not invent a successful round trip',()=>{
 const x=evaluate({r1:'correct',r2:'missing'});assert.equal(x.status,'MODEL_FORWARD_ONLY');assert.deepEqual(x.forward.path,['client','r1','r2','server']);assert.deepEqual(x.reply.path,['server','r2']);
});
test('missing prefix and unreachable next hop remain distinct explanations',()=>{
 assert.equal(trace('forward',{r1:'wrong-network'}).decision.status,'NO_MATCHING_PREFIX');
 assert.equal(trace('forward',{r1:'wrong-gateway'}).decision.status,'UNREACHABLE_NEXTHOP');
});
test('unknown choices do not count as configured routes; no result mutates another',()=>{
 assert.equal(trace('forward',{r1:'__proto__'}).decision.status,'NEEDS_CHOICE');const a=evaluate({r1:'correct',r2:'correct'});evaluate({r1:'missing',r2:'missing'});assert.equal(a.status,'MODEL_ROUND_TRIP');assert.throws(()=>trace('fake',{}),/direction/);
 assert.equal(evaluate({r1:'',r2:'correct'}).status,'NEEDS_CHOICES');
});
