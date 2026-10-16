/* Demo presentation only. No production product mapping or material claims. */
const photos=[
 {src:'sftp-cat7-talifero.jpg',width:670,height:500,credit:'عکس اصلی: Talifero؛ نسخهٔ Ru wiki / DmitryKo',source:'https://commons.wikimedia.org/wiki/File:S-FTP_CAT_7.jpg',alt:'عکس واقعی یک نمونه کابل Cat7 بازشده؛ زوج‌های رنگی، فویل و شیلد بافته‌شده؛ این عکس کالای تهران نتورک نیست'},
 {src:'cat7-bewareircd.jpg',width:1600,height:1200,credit:'عکس اصلی: Bewareircd؛ ویرایش‌های Aavindraa / DmitryKo',source:'https://commons.wikimedia.org/wiki/File:Cat7.jpg',alt:'عکس واقعی نمونه‌ای دیگر از کابل Cat7 با شیلد بازشده و نوشته‌های اصلی سازنده؛ این عکس کالای تهران نتورک نیست'}
];
const photoPanel=document.getElementById('photo-panel'),modelPanel=document.getElementById('model-panel');
const viewButtons=[...document.querySelectorAll('[data-view]')];
viewButtons.forEach(button=>button.addEventListener('click',()=>{
 const showModel=button.dataset.view==='model';
 photoPanel.hidden=showModel;modelPanel.hidden=!showModel;
 viewButtons.forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
 document.querySelector('[data-view-note]').textContent=showModel?'هندسهٔ آموزشی · قابل چرخش و بازشدن':'عکس مرجع · بدون تغییر در فایل اصلی';
 if(showModel&&!modelPanel.querySelector('model-viewer')){
  const load=modelPanel.querySelector('[data-tn-model-open]');
  if(!load.disabled)load.click();
 }
 if(showModel&&modelPanel.querySelector('model-viewer')?.loaded)
  frameIllustration(Number(modelPanel.querySelector('[data-tn-explode-range]')?.value||0)/100);
}));
document.querySelectorAll('[data-photo]').forEach(button=>button.addEventListener('click',()=>{
 const selected=photos[Number(button.dataset.photo)],image=document.getElementById('reference-photo');
 image.src=selected.src;image.alt=selected.alt;image.width=selected.width;image.height=selected.height;
 document.querySelector('[data-photo-credit]').textContent=selected.credit;
 document.querySelector('[data-photo-source]').href=selected.source;
 document.getElementById('photo-original').href=selected.src;
 document.querySelectorAll('[data-photo]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
}));
// Demo alt/lighting only; retain the production renderer unchanged.
new MutationObserver(()=>{
 const viewer=modelPanel.querySelector('model-viewer');if(!viewer||viewer.dataset.studio)return;
 viewer.dataset.studio='true';
 viewer.alt='مدل آموزشی غیرمقیاس ساختار کابل؛ مدل هیچ کالای تهران نتورک نیست؛ چرخش با لمس یا دکمه‌ها';
 viewer.setAttribute('environment-image','neutral');viewer.setAttribute('tone-mapping','aces');
 viewer.setAttribute('exposure','1.05');viewer.setAttribute('shadow-intensity','1');viewer.setAttribute('shadow-softness','1');
 viewer.setAttribute('camera-orbit','10deg 75deg auto');
}).observe(modelPanel.querySelector('[data-tn-model-stage]'),{childList:true});
// Fit the actual illustrative bounds, rather than a generic bounding sphere.
// This is local presentation data; these coordinates are never real dimensions.
function frameIllustration(amount){
 const viewer=modelPanel.querySelector('model-viewer');if(!viewer?.loaded||modelPanel.hidden)return;
 const parts=JSON.parse(modelPanel.dataset.modelParts).parts,lo=[Infinity,Infinity,Infinity],hi=[-Infinity,-Infinity,-Infinity];
 parts.forEach(p=>p.illustration_bounds.forEach((bound,side)=>bound.forEach((v,k)=>{
  const position=v+p.target[k]*amount;
  if(side===0)lo[k]=Math.min(lo[k],position);else hi[k]=Math.max(hi[k],position);
 })));
 const target=lo.map((v,k)=>(v+hi[k])/2),orbit=viewer.getCameraOrbit(),theta=orbit.theta,phi=orbit.phi;
 const forward=[Math.sin(theta)*Math.sin(phi),Math.cos(phi),Math.cos(theta)*Math.sin(phi)];
 const right=[Math.cos(theta),0,-Math.sin(theta)],up=[-Math.sin(theta)*Math.cos(phi),Math.sin(phi),-Math.cos(theta)*Math.cos(phi)];
 const tanV=Math.tan(viewer.getFieldOfView()*Math.PI/360),tanH=tanV*viewer.clientWidth/Math.max(1,viewer.clientHeight);
 const dot=(a,b)=>a.reduce((s,x,k)=>s+x*b[k],0);let distance=0;
 for(let mask=0;mask<8;mask++){
  const corner=lo.map((v,k)=>((mask>>k)&1?hi[k]:v)-target[k]),depth=dot(corner,forward);
  distance=Math.max(distance,depth+Math.abs(dot(corner,right))/tanH,depth+Math.abs(dot(corner,up))/tanV);
 }
 viewer.cameraTarget=target.map(x=>x+'m').join(' ');
 viewer.cameraOrbit=`${theta}rad ${phi}rad ${distance*1.18}m`;
 if(matchMedia('(prefers-reduced-motion:reduce)').matches)viewer.jumpCameraToGoal();
}
document.addEventListener('tn:media-load',()=>frameIllustration(0));
document.addEventListener('tn:parts-view',e=>frameIllustration(e.detail.expanded?1:0));
modelPanel.addEventListener('input',e=>{if(e.target.matches('[data-tn-explode-range]'))frameIllustration(Number(e.target.value)/100)});
modelPanel.addEventListener('click',e=>{if(e.target.matches('[data-tn-explode]'))frameIllustration(e.target.disabled||e.target.getAttribute('aria-pressed')==='true'?1:0)});
window.addEventListener('resize',()=>frameIllustration(Number(modelPanel.querySelector('[data-tn-explode-range]')?.value||0)/100));
