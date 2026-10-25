/* A real image sequence only. No invented geometry or generated hidden views. */
document.querySelectorAll('[data-tn-spin]').forEach(viewer=>{
  let frames;try{frames=JSON.parse(viewer.dataset.tnSpin);}catch{return;}
  if(!Array.isArray(frames)||frames.length<12||frames.length>144||new Set(frames).size!==frames.length)return;
  if(!frames.every(u=>{try{return new URL(u,location.href).origin===location.origin;}catch{return false;}}))return;
  const button=viewer.querySelector('[data-tn-spin-load]'),stage=viewer.querySelector('[data-tn-spin-stage]');
  button?.addEventListener('click',()=>{
    if(viewer.dataset.loaded)return;viewer.dataset.loaded='yes';button.hidden=true;stage.hidden=false;
    const img=stage.querySelector('img'),range=stage.querySelector('input'),status=stage.querySelector('[role=status]');
    let index=0,down=null;
    const show=n=>{index=((n%frames.length)+frames.length)%frames.length;img.src=frames[index];img.dataset.frame=String(index);range.value=String(index);status.textContent=`تصویر ${index+1} از ${frames.length}`;};
    img.addEventListener('error',()=>{status.textContent='بارگذاری این زاویه انجام نشد؛ زاویه دیگری را انتخاب کنید.';});
    img.addEventListener('dragstart',e=>e.preventDefault());
    img.addEventListener('keydown',e=>{if(['ArrowLeft','ArrowRight','Home','End'].includes(e.key)){e.preventDefault();show(e.key==='Home'?0:e.key==='End'?frames.length-1:index+(e.key==='ArrowRight'?1:-1));}});
    img.addEventListener('pointerdown',e=>{down={x:e.clientX,index};img.setPointerCapture(e.pointerId);});
    img.addEventListener('pointermove',e=>{if(down)show(down.index+Math.round((e.clientX-down.x)/18));});
    img.addEventListener('pointerup',()=>{down=null;});img.addEventListener('pointercancel',()=>{down=null;});
    stage.querySelector('[data-tn-spin-prev]').addEventListener('click',()=>show(index-1));
    stage.querySelector('[data-tn-spin-next]').addEventListener('click',()=>show(index+1));
    range.addEventListener('input',()=>show(Number(range.value)));show(0);
  },{once:true});
});
