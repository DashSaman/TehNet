(function(){
'use strict';
// Conceptual teaching model only: fixed documentation networks, no sockets or RouterOS execution.
const topology = Object.freeze({client:'192.0.2.10',server:'198.51.100.10',
  r1:Object.freeze({lan:'192.0.2.0/24',transit:'203.0.113.1'}),r2:Object.freeze({lan:'198.51.100.0/24',transit:'203.0.113.2'}),transit:'203.0.113.0/30'});
const keys = ['missing','wrong-network','wrong-gateway','correct'];
function ipv4(value) {
 const parts=value.split('.');
 if(parts.length!==4||parts.some(p=>!/^\d{1,3}$/.test(p)||Number(p)>255))throw new Error('Invalid fixed-model address');
 return parts.reduce((n,p)=>(n*256+Number(p))>>>0,0);
}
function contains(network,address) {
 const [base,length]=network.split('/'),bits=Number(length);
 if(!/^\d{1,2}$/.test(length)||!Number.isInteger(bits)||bits<0||bits>32)throw new Error('Invalid fixed-model prefix');
 const mask=bits===0?0:(0xffffffff << (32-bits))>>>0;return ((ipv4(base)&mask)>>>0)===((ipv4(address)&mask)>>>0);
}
function route(router,choice,target) {
 const here=topology[router],other=topology[router==='r1'?'r2':'r1'];
 if(!keys.includes(choice))return {status:'NEEDS_CHOICE',router};
 if(contains(here.lan,target)||contains(topology.transit,target))return {status:'CONNECTED',router};
 if(choice==='missing')return {status:'NO_ROUTE',router};
 const destination=choice==='wrong-network'?here.lan:other.lan;
 if(!contains(destination,target))return {status:'NO_MATCHING_PREFIX',router};
 const gateway=choice==='wrong-gateway'?'203.0.113.9':other.transit;
 if(!contains(topology.transit,gateway))return {status:'UNREACHABLE_NEXTHOP',router};
 return {status:'STATIC',router,destination,gateway};
}
function trace(direction,choices) {
 if(!['forward','return'].includes(direction))throw new Error('Unknown model direction');
 const forward=direction==='forward',first=forward?'r1':'r2',second=forward?'r2':'r1';
 const origin=forward?'client':'server',target=forward?topology.server:topology.client,destination=forward?'server':'client';
 const decision=route(first,choices[first],target),path=[origin,first];
 if(decision.status!=='STATIC')return {direction,path,arrived:false,decision};
 path.push(second,destination);return {direction,path,arrived:true,decision};
}
function evaluate(choices) {
 const forward=trace('forward',choices),reply=trace('return',choices);
 return {status:!keys.includes(choices.r1)||!keys.includes(choices.r2)?'NEEDS_CHOICES':forward.arrived&&reply.arrived?'MODEL_ROUND_TRIP':forward.arrived?'MODEL_FORWARD_ONLY':'MODEL_FORWARD_BLOCKED',forward,reply,
  limits:'Conceptual routing exercise only; assumes working links/hosts/ARP, correct host gateways and no default route, ACL, NAT, VRF, ECMP or policy routing. No packet was sent and no RouterOS configuration was executed.'};
}
if(typeof module!=='undefined'&&module.exports)module.exports={topology,contains,route,trace,evaluate};
if(typeof document==='undefined')return;

const names={client:'رایانهٔ نمونه',r1:'روتر R1',r2:'روتر R2',server:'سرویس نمونه'};
const explanations={NEEDS_CHOICE:'مسیر این روتر هنوز انتخاب نشده است.',NO_ROUTE:'در این مدل مسیر static نداریم و مسیر متصل نیز با مقصد منطبق نیست؛ default route هم فرض نشده است.',NO_MATCHING_PREFIX:'prefix مسیر انتخاب‌شده با شبکهٔ مقصد منطبق نیست؛ صرف داشتن یک مسیر، کافی نیست.',UNREACHABLE_NEXTHOP:'next-hop انتخاب‌شده در لینک مستقیم /30 این مدل نیست و مسیر دیگری برای رسیدن به آن وجود ندارد.'};
function init(root){
 if(root.dataset.tnRoutingReady)return;
 const one=s=>root.querySelector(s),r1=one('[data-tn-routing-choice="r1"]'),r2=one('[data-tn-routing-choice="r2"]');
 const direction=one('[data-tn-routing-direction]'),diagram=one('[data-tn-routing-topology]'),result=one('[data-tn-routing-result]'),step=one('[data-tn-routing-step]');
 const check=one('[data-tn-routing-check]'),reset=one('[data-tn-routing-reset]'),prev=one('[data-tn-routing-prev]'),next=one('[data-tn-routing-next]');
 let evaluated=null,cursor=0;
 function paint(){
  diagram.dataset.direction=direction.value;const selected=evaluated?.[direction.value==='forward'?'forward':'reply'];
  root.querySelectorAll('[data-tn-routing-node]').forEach(node=>{
   const index=selected?selected.path.indexOf(node.dataset.tnRoutingNode):-1;
   if(index<0||index>cursor)delete node.dataset.visit;else node.dataset.visit=index===cursor?'current':'visited';
  });
  prev.hidden=next.hidden=!selected;prev.disabled=!selected||cursor===0;next.disabled=!selected||cursor>=selected.path.length-1;
  if(!selected){step.textContent='';return;}
  const atEnd=cursor===selected.path.length-1;
  step.textContent='گام مفهومی '+(cursor+1)+' از '+selected.path.length+' · '+names[selected.path[cursor]]+(atEnd?(selected.arrived?' · مقصد این جهت در مدل در دسترس است.':' · توقف مدل: '+explanations[selected.decision.status]):'');
 }
 function clear(){evaluated=null;cursor=0;result.textContent='انتخاب‌ها تغییر کرده‌اند؛ برای نتیجهٔ مدل، هر دو مسیر را انتخاب و پاسخ را بررسی کنید.';paint();}
 function describe(x){
  if(x.status==='NEEDS_CHOICES')return 'ابتدا برای هر دو روتر یک گزینه انتخاب کنید؛ انتخاب‌نکردن، به معنای قطع واقعی شبکه نیست.';
  if(x.status==='MODEL_ROUND_TRIP')return 'پاسخ تمرین در این مدل درست است: هر دو جهت مسیر دارند. این نتیجه، تست شبکه یا تأیید اجرای RouterOS نیست.';
  const forward=x.forward.arrived?'رفت در مدل به سرویس می‌رسد.':'رفت در '+names[x.forward.decision.router]+' متوقف می‌شود: '+explanations[x.forward.decision.status];
  const reply=x.reply.arrived?'مسیر برگشتِ فرضی نیز موجود است.':'مسیر برگشتِ فرضی در '+names[x.reply.decision.router]+' متوقف می‌شود: '+explanations[x.reply.decision.status];
  return forward+' '+reply+' برگشت مستقل بررسی شده است؛ این نمایش، بسته یا پاسخ واقعی تولید نمی‌کند.';
 }
 check.addEventListener('click',()=>{const x=evaluate({r1:r1.value,r2:r2.value});result.textContent=describe(x);evaluated=x.status==='NEEDS_CHOICES'?null:x;cursor=0;paint();});
 [r1,r2].forEach(select=>select.addEventListener('change',clear));direction.addEventListener('change',()=>{cursor=0;paint();});
 prev.addEventListener('click',()=>{if(evaluated){cursor=Math.max(0,cursor-1);paint();}});
 next.addEventListener('click',()=>{if(evaluated){const p=evaluated[direction.value==='forward'?'forward':'reply'].path;cursor=Math.min(p.length-1,cursor+1);paint();}});
 reset.addEventListener('click',()=>{r1.value=r2.value='';direction.value='forward';clear();r1.focus();});
 check.hidden=reset.hidden=false;check.disabled=reset.disabled=false;root.dataset.tnRoutingReady='1';clear();
}
const start=()=>document.querySelectorAll('[data-tn-routing-lab]').forEach(init);
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();

}());
