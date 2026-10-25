/* Original schematic geometry in relative units. No product measurements or concealed details inferred. */
export function mount(root) {
  if (root.dataset.loaded) return;
  const canvas = root.querySelector('canvas'), ctx = canvas.getContext('2d');
  if (!ctx) throw new Error('Canvas unavailable');
  root.dataset.loaded = 'yes';
  const yaw = root.querySelector('[data-tn-yaw]'), pitch = root.querySelector('[data-tn-pitch]');
  const faces = [];
  function box(x, y, z, w, h, d, color) {
    const v = [[x-w/2,y-h/2,z-d/2],[x+w/2,y-h/2,z-d/2],[x+w/2,y+h/2,z-d/2],[x-w/2,y+h/2,z-d/2],[x-w/2,y-h/2,z+d/2],[x+w/2,y-h/2,z+d/2],[x+w/2,y+h/2,z+d/2],[x-w/2,y+h/2,z+d/2]];
    [[0,1,2,3],[4,7,6,5],[0,4,5,1],[3,2,6,7],[0,3,7,4],[1,5,6,2]].forEach((ids,i)=>faces.push({v:ids.map(k=>v[k]),color,shade:0.58+i*.075}));
  }
  const kind=root.dataset.tnModel;
  if (kind === 'cable') {
    const segments=48,sides=8;
    function point(a,b){return [(1.05+.27*Math.cos(b))*Math.cos(a),.27*Math.sin(b),(1.05+.27*Math.cos(b))*Math.sin(a)];}
    for(let i=0;i<segments;i++)for(let j=0;j<sides;j++){
      const a=i*2*Math.PI/segments,b=j*2*Math.PI/sides,da=2*Math.PI/segments,db=2*Math.PI/sides;
      faces.push({v:[point(a,b),point(a+da,b),point(a+da,b+db),point(a,b+db)],color:'#3e91ad',shade:.55+.4*(j/sides)});
    }
    box(1.2,0,0,.7,.12,.12,'#d8aa66');
  } else if(kind==='socket') {
    box(0,0,0,2.1,2.1,.4,'#d4e4ed');box(0,0,.23,1.35,1.35,.14,'#7599ad');
    box(-.32,0,.32,.18,.26,.04,'#132737');box(.32,0,.32,.18,.26,.04,'#132737');
  } else {
    box(0,0,0,1.25,1.05,1.8,kind==='plug'?'#6eaec4':'#b9cfdc');
    box(0,0,.93,.9,.68,.06,'#102738');
    for(let i=0;i<8;i++)box(-.4+i*.115,.38,.95,.06,.22,.05,'#d9b16c');
    if(kind==='plug')box(0,.63,-.2,.5,.12,1.6,'#8bb9cc');
  }
  const rgb=h=>[1,3,5].map(i=>parseInt(h.slice(i,i+2),16));
  function draw(){
    const width=canvas.clientWidth||320,height=300,ratio=Math.min(devicePixelRatio||1,2);
    if(canvas.width!==width*ratio||canvas.height!==height*ratio){canvas.width=width*ratio;canvas.height=height*ratio;}
    ctx.setTransform(ratio,0,0,ratio,0,0);ctx.clearRect(0,0,width,height);
    const a=Number(yaw.value)*Math.PI/180,b=Number(pitch.value)*Math.PI/180,scale=Math.min(width*.29,88);
    const rotate=v=>{let x=v[0]*Math.cos(a)+v[2]*Math.sin(a),z=-v[0]*Math.sin(a)+v[2]*Math.cos(a);return [x,v[1]*Math.cos(b)-z*Math.sin(b),v[1]*Math.sin(b)+z*Math.cos(b)];};
    faces.map(f=>({...f,p:f.v.map(rotate)})).sort((l,r)=>l.p.reduce((s,v)=>s+v[2],0)-r.p.reduce((s,v)=>s+v[2],0)).forEach(f=>{
      ctx.beginPath();f.p.forEach((v,i)=>{const x=width/2+v[0]*scale,y=height/2-v[1]*scale;i?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.closePath();
      ctx.fillStyle='rgb('+rgb(f.color).map(n=>Math.round(n*f.shade)).join(',')+')';ctx.fill();ctx.strokeStyle='#16354b';ctx.lineWidth=.6;ctx.stroke();
    });
    ctx.globalAlpha=.2;ctx.fillStyle='#8ed6e7';ctx.font='bold 18px Arial';ctx.textAlign='right';ctx.fillText('TEHNET.IR',width-14,height-18);ctx.globalAlpha=1;
    canvas.dataset.yaw=yaw.value;canvas.dataset.pitch=pitch.value;
  }
  let drag;
  canvas.style.touchAction='none';
  canvas.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY,a:Number(yaw.value),b:Number(pitch.value)};canvas.setPointerCapture(e.pointerId);});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;yaw.value=((((drag.a+(e.clientX-drag.x)*.7)+180)%360+360)%360)-180;pitch.value=Math.max(-80,Math.min(80,drag.b-(e.clientY-drag.y)*.5));draw();});
  for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,()=>{drag=null;});
  canvas.addEventListener('keydown',e=>{const map={ArrowLeft:[-10,0],ArrowRight:[10,0],ArrowUp:[0,10],ArrowDown:[0,-10]};if(!map[e.key])return;e.preventDefault();yaw.value=Number(yaw.value)+map[e.key][0];pitch.value=Number(pitch.value)+map[e.key][1];draw();});
  [yaw,pitch].forEach(input=>input.addEventListener('input',draw));
  root.querySelector('[data-tn-model-reset]').addEventListener('click',()=>{yaw.value=-30;pitch.value=-20;draw();});
  new ResizeObserver(draw).observe(canvas);requestAnimationFrame(draw);
}
