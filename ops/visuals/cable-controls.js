/* Explicit controls for the educational preview; no production asset mapping. */
(()=>{
 const panel=document.getElementById('model-panel'),canvas=panel.querySelector('[data-model-canvas]');
 const toolbar=panel.querySelector('[data-demo-toolbar]'),status=panel.querySelector('[data-demo-status]');
 const rotate=toolbar.querySelector('[data-demo-action="rotate"]'),fullscreen=toolbar.querySelector('[data-demo-action="fullscreen"]');
 const reduced=matchMedia('(prefers-reduced-motion:reduce)');
 let initialFov='auto';
 const viewer=()=>panel.querySelector('model-viewer');
 const amount=()=>Number(panel.querySelector('[data-tn-explode-range]')?.value||0)/100;
 const stopRotation=()=>{
  viewer()?.removeAttribute('auto-rotate');rotate.setAttribute('aria-pressed','false');rotate.textContent='چرخش خودکار';
 };
 const syncMotionPreference=()=>{
  rotate.disabled=reduced.matches;
  rotate.title=reduced.matches?'چرخش خودکار با تنظیم کاهش حرکت غیرفعال است؛ می‌توانید مدل را دستی بچرخانید.':'';
  if(reduced.matches)stopRotation();
 };
 document.querySelector('[data-open-model]').addEventListener('click',()=>{
  document.querySelector('[data-view="model"]').click();
  panel.scrollIntoView({block:'start',behavior:reduced.matches?'instant':'smooth'});
 });
 document.querySelector('[data-view="photo"]').addEventListener('click',stopRotation);
 document.addEventListener('visibilitychange',()=>{if(document.hidden)stopRotation()});
 reduced.addEventListener('change',syncMotionPreference);
 document.addEventListener('tn:media-load',()=>{
  const model=viewer();if(!model)return;
  initialFov=model.fieldOfView;
  // The user has explicitly entered the interactive panel. Keep drag gestures
  // inside this canvas; page scrolling remains available around it.
  model.setAttribute('touch-action','none');model.setAttribute('aria-describedby','model-gesture-help');
  model.setAttribute('auto-rotate-delay','0');model.setAttribute('rotation-per-second','20deg');
  toolbar.hidden=false;fullscreen.hidden=!document.fullscreenEnabled||!canvas.requestFullscreen;
  syncMotionPreference();
  status.textContent='آمادهٔ چرخش؛ مدل را با موس یا انگشت بکشید.';
 });
 toolbar.addEventListener('click',async event=>{
  const button=event.target.closest('[data-demo-action]'),model=viewer();
  if(!button||!model?.loaded)return;
  switch(button.dataset.demoAction){
   case 'zoom-in':model.zoom(2);break;
   case 'zoom-out':model.zoom(-2);break;
   case 'rotate':{
    if(reduced.matches)return;
    const start=rotate.getAttribute('aria-pressed')!=='true';
    model.toggleAttribute('auto-rotate',start);rotate.setAttribute('aria-pressed',String(start));
    rotate.textContent=start?'توقف چرخش':'چرخش خودکار';
    status.textContent=start?'چرخش خودکار فعال است.':'چرخش خودکار متوقف شد.';break;
   }
   case 'home':
    stopRotation();model.resetTurntableRotation();
    // Gestures change the live FoV without changing the declarative property.
    // Restore its original aspect-aware value and await the asynchronous jump
    // before fitting bounds; otherwise portrait zoom uses a stale live FoV.
    model.fieldOfView=initialFov;model.requestUpdate('fieldOfView');
    await model.updateComplete;model.jumpCameraToGoal();await model.updateComplete;
    frameIllustration(amount(),{theta:10*Math.PI/180,phi:75*Math.PI/180});
    await model.updateComplete;
    status.textContent='زاویه، زوم و مرکز مدل بازنشانی شد.';break;
   case 'fullscreen':
    try{
     if(document.fullscreenElement===canvas)await document.exitFullscreen();
     else await canvas.requestFullscreen();
    }catch{status.textContent='مرورگر اجازهٔ تمام‌صفحه نداد؛ مدل در همین قاب قابل بررسی است.'}
    break;
  }
 });
 document.addEventListener('fullscreenchange',()=>{
  const active=document.fullscreenElement===canvas;
  fullscreen.setAttribute('aria-pressed',String(active));fullscreen.textContent=active?'خروج از تمام‌صفحه':'تمام‌صفحه';
  requestAnimationFrame(()=>frameIllustration(amount()));
 });
 // A direct URL is an explicit entrance to the interactive model. The ordinary
 // gallery still starts with the real photograph and defers the GLB.
 if(new URLSearchParams(location.search).get('view')==='3d')
  document.querySelector('[data-open-model]').click();
})();
