/* Local renderer, activated only by the user's click for a reviewed native GLB. */
document.querySelectorAll('[data-tn-reviewed-model]').forEach(root=>{
 const button=root.querySelector('[data-tn-model-open]'),message=root.querySelector('[data-tn-model-message]');let viewer,yaw=0,pitch=75;
 button.addEventListener('click',async()=>{
  button.disabled=true;message.textContent='در حال بارگذاری مدل…';
  try{
   for(const u of [root.dataset.modelSrc,root.dataset.modelModule])if(new URL(u,location.href).origin!==location.origin)throw Error('Local model required');
   await import(root.dataset.modelModule);await customElements.whenDefined('model-viewer');
   viewer=document.createElement('model-viewer');viewer.src=root.dataset.modelSrc;viewer.alt='مدل سه‌بعدی همین محصول؛ کنترل زاویه با لمس یا دکمه‌ها';viewer.setAttribute('camera-controls','');viewer.setAttribute('touch-action','pan-y');viewer.setAttribute('interaction-prompt','none');viewer.setAttribute('camera-orbit','0deg 75deg auto');if(root.dataset.modelPoster)viewer.poster=root.dataset.modelPoster;
   viewer.addEventListener('load',()=>{message.textContent='مدل آماده است.';root.querySelector('.tn-model-controls').hidden=false;setupReviewedParts(root,viewer);root.dispatchEvent(new CustomEvent('tn:media-load',{bubbles:true,detail:{type:'reviewed-glb'}}));});
   viewer.addEventListener('error',()=>{message.textContent='مدل بارگذاری نشد؛ گالری تصاویر همچنان در دسترس است.';button.hidden=false;button.disabled=false;});
   root.querySelector('[data-tn-model-stage]').replaceChildren(viewer);button.hidden=true;
  }catch(e){message.textContent='بارگذاری مدل انجام نشد؛ دوباره تلاش کنید یا گالری را ببینید.';button.disabled=false;}
 });
 root.querySelectorAll('[data-orbit]').forEach(b=>b.addEventListener('click',()=>{if(!viewer)return;const o=viewer.getCameraOrbit();yaw=o.theta*180/Math.PI;pitch=o.phi*180/Math.PI;const action=b.dataset.orbit;if(action==='reset'){yaw=0;pitch=75;}else if(action==='left')yaw-=15;else if(action==='right')yaw+=15;else pitch=Math.max(15,Math.min(165,pitch+(action==='up'?-15:15)));viewer.setAttribute('camera-orbit',`${yaw}deg ${pitch}deg ${o.radius}m`);if(matchMedia('(prefers-reduced-motion:reduce)').matches)viewer.jumpCameraToGoal();}));
});

/* Uses the reviewed animation already in the native CAD/GLB; never invents parts. */
function setupReviewedParts(root,viewer){
 const panel=root.querySelector('[data-tn-parts-panel]');if(!panel)return;panel.replaceChildren();panel.hidden=true;
 let data;try{data=JSON.parse(root.dataset.modelParts||'null');}catch{return;}
 if(!data||!Array.isArray(data.parts)||!data.parts.length||data.parts.length>32||!viewer.availableAnimations.includes(data.animation))return;
 const make=(tag,text)=>{const e=document.createElement(tag);if(text)e.textContent=text;return e;};
 const toggle=make('button','باز کردن اجزا'),range=make('input'),label=make('label','میزان باز شدن اجزا'),list=make('div'),detail=make('section'),status=make('p');
 toggle.type='button';toggle.dataset.tnExplode='';toggle.setAttribute('aria-pressed','false');range.type='range';range.min='0';range.max='100';range.step='1';range.value='0';range.dataset.tnExplodeRange='';range.setAttribute('aria-label','میزان باز شدن اجزا');label.append(range);list.className='tn-parts-list';detail.className='tn-part-detail';detail.setAttribute('aria-live','polite');status.setAttribute('role','status');panel.append(toggle,label,status,list,detail);panel.hidden=false;
 viewer.animationName=data.animation;viewer.setAttribute('animation-crossfade-duration','0');viewer.pause();viewer.currentTime=0;
 const baseRadius=viewer.getCameraOrbit().radius,maxTarget=Math.max(...data.parts.map(p=>Math.hypot(...p.target))),dimensions=viewer.getDimensions(),objectRadius=Math.hypot(dimensions.x,dimensions.y,dimensions.z)/2;
 viewer.setAttribute('max-camera-orbit',`auto auto ${Math.max(baseRadius,(maxTarget+objectRadius)*100)}m`);
 const fit=amount=>{const aspect=Math.max(.1,Math.min(1,viewer.clientWidth/Math.max(1,viewer.clientHeight))),halfFov=Math.atan(Math.tan(viewer.getFieldOfView()*Math.PI/360)*aspect),wideRadius=Math.max(baseRadius,(maxTarget+objectRadius)/Math.sin(halfFov)*1.1),o=viewer.getCameraOrbit();viewer.cameraOrbit=`${o.theta}rad ${o.phi}rad ${baseRadius+(wideRadius-baseRadius)*amount}m`;if(matchMedia('(prefers-reduced-motion:reduce)').matches)viewer.jumpCameraToGoal();};
 const targets=[];let expanded=false;
 const select=(part,index)=>{
  detail.replaceChildren(make('h4',part.name),make('p',part.description),make('p','جنس: '+part.material));const dl=make('dl');
  for(const value of part.measurements||[])dl.append(make('dt',value.label),make('dd',Number(value.value).toLocaleString('fa-IR')+' '+value.unit));
  if(dl.childElementCount)detail.append(dl);else detail.append(make('p','اندازهٔ تأییدشده برای این بخش ثبت نشده است.'));
  const link=make('a','مدرک مشخصات این جزء');try{if(new URL(part.source).protocol==='https:'){link.href=part.source;link.rel='noopener';detail.append(link);}}catch{}
  targets.forEach((b,i)=>b.setAttribute('aria-pressed',String(i===index)));
  if(expanded&&Array.isArray(part.target)&&part.target.length===3&&part.target.every(Number.isFinite)){viewer.cameraTarget=part.target.map(x=>x+'m').join(' ');fit(0);if(matchMedia('(prefers-reduced-motion:reduce)').matches)viewer.jumpCameraToGoal();}
 };
 data.parts.forEach((part,i)=>{const b=make('button',part.name);b.type='button';b.dataset.tnPart=String(i);b.setAttribute('aria-pressed','false');b.addEventListener('click',()=>select(part,i));list.append(b);targets.push(b);});
 const state=(value)=>{expanded=value;fit(value?1:0);toggle.disabled=false;toggle.textContent=value?'بستن اجزا':'باز کردن اجزا';toggle.setAttribute('aria-pressed',String(value));range.value=value?'100':'0';status.textContent=value?'اجزا جدا شده‌اند؛ هر بخش را برای توضیح انتخاب کنید.':'مدل در حالت مونتاژ است.';root.dispatchEvent(new CustomEvent('tn:parts-view',{bubbles:true,detail:{expanded:value}}));};
 const seek=time=>{viewer.play({repetitions:1});viewer.pause();viewer.currentTime=time;};
 toggle.addEventListener('click',()=>{viewer.pause();if(expanded){seek(0);viewer.cameraTarget='auto auto auto';state(false);return;}viewer.currentTime=0;if(matchMedia('(prefers-reduced-motion:reduce)').matches){seek(viewer.duration);state(true);}else{fit(1);viewer.scrollIntoView({block:'center',behavior:'smooth'});toggle.disabled=true;viewer.addEventListener('finished',()=>state(true),{once:true});viewer.play({repetitions:1});}});
 range.addEventListener('input',()=>{seek(viewer.duration*Number(range.value)/100);fit(Number(range.value)/100);expanded=Number(range.value)===100;toggle.disabled=false;toggle.textContent=expanded?'بستن اجزا':'باز کردن اجزا';toggle.setAttribute('aria-pressed',String(expanded));status.textContent='بازشدگی '+Number(range.value).toLocaleString('fa-IR')+' درصد';});
 select(data.parts[0],0);state(false);
}
