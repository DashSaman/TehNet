"""Original parametric EDUCATIONAL geometry. No real SKU, dimensions, materials or CAD claimed."""
from pathlib import Path
import argparse,json,math,shutil,struct
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True);root=Path(__file__).resolve().parents[1]
g={'asset':{'version':'2.0','generator':'TehNet original educational cable schematic; normalized units, not product CAD'},'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'materials':[],'buffers':[],'bufferViews':[],'accessors':[],'animations':[]};binary=bytearray()
def acc(values,kind,components):
 while len(binary)%4:binary.append(0)
 start=len(binary);fmt='f'if kind==5126 else'H';binary.extend(struct.pack('<'+fmt*len(values),*values));view=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':start,'byteLength':len(binary)-start});a={'bufferView':view,'componentType':kind,'count':len(values)//components,'type':{1:'SCALAR',3:'VEC3',4:'VEC4'}[components]}
 if kind==5126:a.update(min=[min(values[k::components])for k in range(components)],max=[max(values[k::components])for k in range(components)])
 g['accessors'].append(a);return len(g['accessors'])-1
def material(name,color,metal=0):
 g['materials'].append({'name':name,'doubleSided':True,'pbrMetallicRoughness':{'baseColorFactor':color+[1],'metallicFactor':metal,'roughnessFactor':.45}});return len(g['materials'])-1
colors=[material('Schematic jacket',[.035,.12,.20]),material('Schematic braid',[.55,.65,.72],.8),material('Schematic foil',[.72,.78,.85],.8),material('Schematic insulation',[.1,.60,.78]),material('Schematic conductor',[.8,.35,.12],.7)]
def mesh_tube(radius,length,mat,inner=None,cut=False,center=(0,0),curve=None):
 pos=[];norm=[];indices=[];segments=40;steps=48 if curve else 1
 for r,sign in [(radius,1)]+([(inner,-1)]if inner else[]):
  base=len(pos)//3
  for row in range(steps+1):
   y=length*(row/steps-.5);cx,cz=curve(y)if curve else center
   for k in range(segments+1):
    angle=(-math.pi/4)+(math.pi*1.5 if cut else math.pi*2)*k/segments;x,z=math.cos(angle),math.sin(angle);pos.extend([cx+r*x,y,cz+r*z]);norm.extend([sign*x,0,sign*z])
  for row in range(steps):
   for k in range(segments):
    a=base+row*(segments+1)+k;b=a+segments+1;indices.extend([a,b,a+1,a+1,b,b+1]if sign==1 else[a,a+1,b,a+1,b+1,b])
 g['meshes'].append({'primitives':[{'attributes':{'POSITION':acc(pos,5126,3),'NORMAL':acc(norm,5126,3)},'indices':acc(indices,5123,1),'material':mat}]});return len(g['meshes'])-1
groups=[];parts=[];times=acc([0,1],5126,1);samplers=[];channels=[]
definitions=[('jacket','روکش بیرونی','لایهٔ محافظ بیرونی در این شماتیک برش خورده تا لایه‌های داخلی دیده شوند. جنس و ضخامت واقعی به مدل و دیتاشیت وابسته است.'),('braid','شیلد کلی','پوستهٔ فلزی نمادینِ این بخش فقط جای شیلد کلی را نشان می‌دهد؛ شکل بافت و پوشش واقعی از این مدل آموزشی قابل تعیین نیست.'),('foils','فویل زوج‌ها','چهار پوستهٔ نمادین برای توضیح جداسازی شیلد زوج‌ها؛ ترکیب و ضخامت فویل باید برای همان مدل مستند شود.'),('insulation','عایق هادی‌ها','رنگ و مسیر هشت رشته برای فهم ساختار نمایش داده شده است؛ جنس، قطر و گام تابِ واقعی از این شماتیک اندازه‌گیری نمی‌شود.'),('conductors','هادی‌ها','هادی‌های نمادین با رنگ مسی مشخص شده‌اند؛ رنگ تصویر، مدرک جنس، خلوص، AWG یا قطر واقعی نیست.')]
for i,(name,label,description)in enumerate(definitions):
 node=len(g['nodes']);g['nodes'].append({'name':name,'children':[]});g['scenes'][0]['nodes'].append(node);groups.append(node)
 targets=[[-2.3,0,0],[-1.15,0,0],[0,0,0],[1.15,0,0],[2.3,0,0]];target=targets[i]
 samplers.append({'input':times,'output':acc([0,0,0]+target,5126,3),'interpolation':'LINEAR'});channels.append({'sampler':i,'target':{'node':node,'path':'translation'}})
 parts.append({'name':label,'node':name,'description':description,'material':'جنس واقعی تأیید نشده؛ وابسته به شماره فنی','source':'https://tehnet.ir/technical-methodology/','target':target,'measurements':[]})
 def add(mesh,name):
  child=len(g['nodes']);g['nodes'].append({'name':name,'mesh':mesh});g['nodes'][node]['children'].append(child)
 if i<2:add(mesh_tube(.57 if i==0 else .49,3 if i==0 else 2.9,colors[i],.535 if i==0 else .475,True),name+'-shell')
 elif i==2:
  for k in range(4):
   angle=math.pi/4+k*math.pi/2;add(mesh_tube(.185,2.8,colors[i],.172,True,center=(.26*math.cos(angle),.26*math.sin(angle))),name+str(k))
 else:
  for pair in range(4):
   angle=math.pi/4+pair*math.pi/2;cx,cz=.26*math.cos(angle),.26*math.sin(angle)
   for wire in range(2):
    phase=wire*math.pi;curve=lambda y,cx=cx,cz=cz,phase=phase,pair=pair:(cx+.075*math.cos(y*(5+pair*.25)+phase),cz+.075*math.sin(y*(5+pair*.25)+phase))
    add(mesh_tube(.052 if i==3 else .027,2.9 if i==3 else 3.15,colors[i],.032 if i==3 else None,curve=curve),name+str(pair)+'-'+str(wire))
g['animations']=[{'name':'Explode','samplers':samplers,'channels':channels}];g['buffers']=[{'byteLength':len(binary)}]
j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);binary.extend(b'\0'*((-len(binary))%4));glb=b'glTF'+struct.pack('<II',2,28+len(j)+len(binary))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(binary),0x004e4942)+binary;(out/'educational-cable.glb').write_bytes(glb)
data={'mpn':'EDUCATIONAL-NOT-A-PRODUCT','animation':'Explode','parts':parts}
html='''<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>تهران نتورک | آزمایش بازکردن اجزای کابل</title><link rel="stylesheet" href="store.css"><style>:root{--tn-ink:#eaf1f8;--tn-muted:#a9bdcc;--tn-accent:#79e7f7;--tn-surface:#102333;--tn-border:#34586b}*{box-sizing:border-box}body{margin:0;background:#08131f;color:var(--tn-ink);font:16px/2 Tahoma,Arial,sans-serif}main{max-width:1120px;margin:auto;padding:32px 22px}a{color:#79e7f7}.tag{display:inline-block;border:1px solid #9f8357;color:#f0d39e;padding:3px 14px;border-radius:24px}h1{font-size:clamp(25px,4vw,42px);line-height:1.7;margin-bottom:12px}p{color:var(--tn-muted)}button{background:#133449;color:#eaf1f8;border:1px solid #4b819b;border-radius:9px;cursor:pointer}button:focus-visible,input:focus-visible{outline:3px solid #79e7f7;outline-offset:3px}button[aria-pressed=true]{background:#1b526b}button:disabled{opacity:.6}button[hidden],[hidden]{display:none!important}.tn-reviewed-model{border-color:#34586b}.tn-reviewed-model model-viewer{height:530px;max-height:70vh}.tn-part-detail dd{direction:ltr}.tn-model-controls{gap:8px}small{font-size:13px}footer{border-top:1px solid #34586b;margin-top:24px;padding-top:18px}@media(max-width:600px){main{padding:20px 14px}.tn-reviewed-model{padding:12px}.tn-reviewed-model model-viewer{height:420px}}</style><main><span class="tag">نمونهٔ آموزشی؛ مدل هیچ کالای فروشگاه نیست</span><h1>کابل را لایه‌به‌لایه ببینید</h1><p>مدل را باز کنید، سپس «باز کردن اجزا» را بزنید. هر بخش، توضیح مستقل دارد و اسلایدر، میزان بازشدگی را کنترل می‌کند. هندسه و تناسب‌ها برای آموزش ترسیم شده‌اند؛ هیچ ضخامت یا عدد میکرون واقعی در این نمونه ثبت نشده است.</p><section class="tn-reviewed-model" data-tn-reviewed-model data-model-src="/educational-cable.glb" data-model-module="/model-viewer.min.js" data-model-parts='PARTS'><h2>شماتیک آموزشی ساختار لایه‌ای کابل</h2><button type="button" data-tn-model-open>باز کردن مدل سه‌بعدی</button><div data-tn-model-stage></div><p role="status" data-tn-model-message aria-live="polite"></p><div class="tn-model-controls" hidden>CONTROLS</div><div data-tn-parts-panel hidden></div></section><footer><strong>تهران نتورک · tehnet.ir</strong><p>در محصول واقعی، نمایش اجزا و عددهایی مثل ضخامت فویل فقط پس از تطبیق شماره فنی، مدل سه‌بعدی، مواد، واحد اندازه‌گیری و مدرک معتبر فعال می‌شود. این نمونه برای بررسی تجربهٔ کاربری است.</p></footer></main><script src="reviewed-model.js"></script><script>document.addEventListener('tn:media-load',()=>{const v=document.querySelector('model-viewer');v.cameraOrbit='20deg 75deg 11m';v.jumpCameraToGoal()});</script></html>'''
html=html.replace('PARTS',json.dumps(data,ensure_ascii=False).replace('&','&amp;').replace("'",'&#39;')).replace('CONTROLS',''.join('<button type="button" data-orbit="'+key+'">'+label+'</button>'for key,label in [('left','چپ'),('right','راست'),('up','بالا'),('down','پایین'),('reset','بازنشانی')]))
(out/'index.html').write_text(html,encoding='utf-8');
for src,dest in [('assets/reviewed-model.js','reviewed-model.js'),('assets/store.css','store.css'),('assets/vendor/model-viewer/model-viewer.min.js','model-viewer.min.js'),('assets/vendor/model-viewer/LICENSE','LICENSE-model-viewer'),('assets/vendor/model-viewer/PROVENANCE.json','model-viewer-provenance.json')]:shutil.copyfile(root/'site/plugins/tehnet-store'/src,out/dest)
(out/'README.fa.txt').write_text('نمونهٔ آموزشی تهران نتورک؛ کالا و CAD سازنده نیست. ابعاد و مواد واقعی تأیید نشده‌اند. برای اجرا: python -m http.server 18084 --bind 127.0.0.1 --directory همین پوشه، سپس http://localhost:18084 را باز کنید. فایل‌ها self-hosted و بدون analytics هستند. مدل آموزشی با کد خود مخزن ساخته شده؛ نمایشگر Apache-2.0 با مجوز پیوست است.',encoding='utf-8');print('EDUCATIONAL_EXPLODED_DEMO_BUILT;parts=5;no physical measurements claimed;GLB bytes='+str(len(glb)))
