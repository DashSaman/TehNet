/* Shared controls for any exact-product reviewed GLB, independent of SKU/category. */
document.querySelectorAll('[data-tn-reviewed-model]').forEach((root,index)=>{
 const reduced=matchMedia('(prefers-reduced-motion:reduce)');let model,initialOrbit,initialTarget,initialFov,rotate,fullscreen,canvas;
 const status=document.createElement('p');status.dataset.tnModelControlStatus='';status.className='tn-model-control-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');
 const stop=()=>{model?.removeAttribute('auto-rotate');if(rotate){rotate.setAttribute('aria-pressed','false');rotate.textContent='چرخش خودکار';}};
 const motion=()=>{if(!rotate)return;rotate.disabled=reduced.matches;rotate.title=reduced.matches?'با تنظیم کاهش حرکت، چرخش خودکار خاموش است؛ چرخش دستی در دسترس است.':'';if(reduced.matches)stop();};
 reduced.addEventListener('change',motion);document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
 new MutationObserver(()=>{if(root.hidden)stop();}).observe(root,{attributes:true,attributeFilter:['hidden']});
 root.addEventListener('tn:media-load',async()=>{
  const next=root.querySelector('model-viewer');if(!next||next.dataset.tnControlsReady)return;
  model=next;model.dataset.tnControlsReady='true';await model.updateComplete;
  initialOrbit=model.cameraOrbit;initialTarget=model.cameraTarget;initialFov=model.fieldOfView;
  model.setAttribute('touch-action','none');model.setAttribute('auto-rotate-delay','0');model.setAttribute('rotation-per-second','20deg');
  let help=root.querySelector('[data-tn-model-help]');
  if(!help){help=document.createElement('p');help.dataset.tnModelHelp='';help.className='tn-model-help';help.textContent='برای چرخش مدل را بکشید. زوم با چرخ موس یا دو انگشت؛ جابه‌جایی با راست‌کلیک و کشیدن یا حرکت دو انگشت.';root.querySelector('[data-tn-model-stage]').before(help);}
  if(!help.id)help.id='tn-model-help-'+index;model.setAttribute('aria-describedby',help.id);
  const stage=root.querySelector('[data-tn-model-stage]');canvas=stage.closest('[data-tn-model-canvas]');
  if(!canvas){canvas=document.createElement('div');canvas.className='tn-model-canvas';canvas.dataset.tnModelCanvas='';stage.before(canvas);canvas.append(stage);}
  const previous=canvas.querySelector('[data-tn-model-toolbar]');if(previous)previous.remove();
  const toolbar=document.createElement('div');toolbar.className='tn-model-toolbar';toolbar.dataset.tnModelToolbar='';toolbar.setAttribute('role','group');toolbar.setAttribute('aria-label','کنترل مدل سه‌بعدی');
  const buttons={};for(const [name,label]of [['zoom-in','＋ نزدیک‌تر'],['zoom-out','− دورتر'],['rotate','چرخش خودکار'],['home','نمای اولیه'],['fullscreen','تمام‌صفحه']]){
   const b=document.createElement('button');b.type='button';b.dataset.tnModelAction=name;b.textContent=label;
   if(name==='rotate'||name==='fullscreen')b.setAttribute('aria-pressed','false');toolbar.append(b);buttons[name]=b;
  }
  rotate=buttons.rotate;fullscreen=buttons.fullscreen;fullscreen.hidden=!document.fullscreenEnabled||!canvas.requestFullscreen;
  canvas.append(toolbar);canvas.after(status);motion();
  new IntersectionObserver(entries=>{if(!entries[0].isIntersecting)stop();}).observe(model);
  toolbar.addEventListener('click',async event=>{
   const button=event.target.closest('[data-tn-model-action]');if(!button||!model.loaded)return;
   switch(button.dataset.tnModelAction){
    case'zoom-in':model.zoom(2);break;
    case'zoom-out':model.zoom(-2);break;
    case'rotate':{
     if(reduced.matches)return;const start=rotate.getAttribute('aria-pressed')!=='true';model.toggleAttribute('auto-rotate',start);
     rotate.setAttribute('aria-pressed',String(start));rotate.textContent=start?'توقف چرخش':'چرخش خودکار';status.textContent=start?'چرخش خودکار فعال است.':'چرخش متوقف شد.';break;
    }
    case'home':
     stop();model.resetTurntableRotation();model.fieldOfView=initialFov;model.requestUpdate('fieldOfView');
     model.cameraOrbit=initialOrbit;model.cameraTarget=initialTarget;await model.updateComplete;
     model.jumpCameraToGoal();await model.updateComplete;
     root.dispatchEvent(new CustomEvent('tn:reset-view',{bubbles:true}));await model.updateComplete;
     status.textContent='زاویه، زوم و مرکز مدل بازنشانی شد.';break;
    case'fullscreen':
     try{if(document.fullscreenElement===canvas)await document.exitFullscreen();else await canvas.requestFullscreen();}
     catch{status.textContent='مرورگر اجازهٔ تمام‌صفحه نداد؛ مدل در همین قاب قابل بررسی است.';}break;
   }
  });
  status.textContent='مدل آمادهٔ چرخش با موس یا لمس است.';
 });
 document.addEventListener('fullscreenchange',()=>{
  if(!fullscreen)return;const active=document.fullscreenElement===canvas;fullscreen.setAttribute('aria-pressed',String(active));fullscreen.textContent=active?'خروج از تمام‌صفحه':'تمام‌صفحه';
  if(model?.loaded)requestAnimationFrame(()=>root.dispatchEvent(new CustomEvent('tn:reset-view',{bubbles:true})));
 });
});
