/* Built-in imagegen reconstructs backgrounds. This deterministic compositor restores
   original pixels outside reviewed lettering masks; it never generates a product. */
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const sharp=require(process.env.SHARP_MODULE||'sharp');
const root=path.resolve(__dirname,'..'),source=path.join(root,'content/media/saieedshabake-2026-10-16'),out=path.join(root,'content/media/tehnet-clean-2026-10-16');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const polygon=(points,color)=>'<polygon points="'+points.reduce((a,v,i)=>a+(i%2?',':' ')+v,'').trim()+'" fill="'+color+'"/>';
function inwardAlpha(binary,w,h,feather){
 const d=new Uint16Array(w*h);for(let i=0;i<d.length;i++)d[i]=binary[i]>=128?Math.min(60000,Math.min(i%w,w-1-i%w,Math.floor(i/w),h-1-Math.floor(i/w))+1):0;
 for(let y=0;y<h;y++)for(let x=0;x<w;x++){const i=y*w+x;if(d[i])d[i]=Math.min(d[i],x?d[i-1]+1:1,y?d[i-w]+1:1);}
 for(let y=h-1;y>=0;y--)for(let x=w-1;x>=0;x--){const i=y*w+x;if(d[i])d[i]=Math.min(d[i],x<w-1?d[i+1]+1:1,y<h-1?d[i+w]+1:1);}
 const alpha=Buffer.alloc(d.length);for(let i=0;i<d.length;i++)alpha[i]=Math.min(255,Math.round(d[i]*255/feather));return alpha;
}
(async()=>{
 assert.deepEqual([...inwardAlpha(Buffer.from([0,0,0,0,255,0,0,0,0]),3,3,1)],[0,0,0,0,255,0,0,0,0],'inward mask must be opaque at its intended core and zero outside');
 const jobs=JSON.parse(fs.readFileSync(path.resolve(process.argv[2]),'utf8'));assert.equal(jobs.length,15);fs.mkdirSync(path.join(out,'patches'),{recursive:true});
 const candidates=[];const pending=[];
 for(const job of jobs){
  if(!job.generated_file||!fs.existsSync(job.generated_file)){pending.push([job.id,job.index]);continue;}
  const originalFile=path.join(source,job.source_file),originalBytes=fs.readFileSync(originalFile);assert.equal(hash(originalBytes),job.source_sha256);
  const {data:original,info}=await sharp(originalFile).removeAlpha().toColourspace('srgb').raw().toBuffer({resolveWithObject:true}),w=info.width,h=info.height;assert.equal(info.channels,3);
  assert.deepEqual([w,h],job.dimensions);
  const generation=await sharp(job.generated_file).resize(w,h,{fit:'fill'}).removeAlpha().toColourspace('srgb').raw().toBuffer();
  const svg=Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><rect width="100%" height="100%" fill="black"/>${job.regions.map(p=>polygon(p,'white')).join('')}${job.hard_protect?'':(job.protect||[]).map(p=>polygon(p,'black')).join('')}</svg>`);
  const binary=await sharp(svg).removeAlpha().greyscale().raw().toBuffer(),alpha=inwardAlpha(binary,w,h,job.feather||10),pixels=Buffer.from(original),patch=Buffer.alloc(w*h*4);let edited=0;
  // Feather the outer background only. Never blend over a protected product edge.
  if(job.hard_protect){
   const guard=Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><rect width="100%" height="100%" fill="black"/>${(job.protect||[]).map(p=>polygon(p,'white')).join('')}</svg>`);
   const protectedPixels=await sharp(guard).removeAlpha().greyscale().raw().toBuffer();
   for(let i=0;i<alpha.length;i++)if(protectedPixels[i]>0)alpha[i]=0;
  }
  for(let i=0;i<w*h;i++){const a=alpha[i];if(!a)continue;edited++;for(let c=0;c<3;c++){pixels[i*3+c]=Math.round((original[i*3+c]*(255-a)+generation[i*3+c]*a)/255);patch[i*4+c]=generation[i*3+c];}patch[i*4+3]=a;}
  assert(edited>100&&edited<w*h*.4,'Background mask must be bounded');
  const clean=await sharp(pixels,{raw:{width:w,height:h,channels:3}}).webp({lossless:true,effort:4}).toBuffer();
  const decoded=await sharp(clean).removeAlpha().toColourspace('srgb').raw().toBuffer();assert.equal(Buffer.compare(decoded,pixels),0,'Lossless delivery must retain every RGB value');
  let changedOutside=0;for(let i=0;i<w*h;i++)if(!alpha[i]&&(decoded[i*3]!==original[i*3]||decoded[i*3+1]!==original[i*3+1]||decoded[i*3+2]!==original[i*3+2]))changedOutside++;
  assert.equal(changedOutside,0,'Original product/background outside mask must remain exact');
  const file=hash(clean)+'.webp';fs.writeFileSync(path.join(out,file),clean);
  const patchFile='patches/'+job.source_sha256+'.png';const patchBytes=await sharp(patch,{raw:{width:w,height:h,channels:4}}).png().toBuffer();fs.writeFileSync(path.join(out,patchFile),patchBytes);
  candidates.push({id:job.id,index:job.index,source_file:job.source_file,source_sha256:job.source_sha256,file,sha256:hash(clean),dimensions:[w,h],bytes:clean.length,patch_file:patchFile,patch_sha256:hash(patchBytes),regions:job.regions,protect:job.protect||[],hard_protect:!!job.hard_protect,feather_inward_px:job.feather||10,edited_pixels:edited,total_pixels:w*h,changed_pixels_outside_mask:changedOutside,provider:'built-in imagegen for background inpainting; deterministic original-pixel restoration',prompt:job.prompt||'Owner-authorized removal of only '+job.mark+'; retain all product details and manufacturer marks.'});
 }
 const evidence={schema:1,scope:'Owner-authorized retailer-lettering removal only; exact original RGB outside reviewed background masks',edited:candidates.length,pending,candidates,reviewed:false};
 const qa=path.join(root,'qa/store-2026-10-16');fs.mkdirSync(qa,{recursive:true});fs.writeFileSync(path.join(qa,'watermark-candidates.json'),JSON.stringify(evidence,null,2));
 if(!pending.length){const release=JSON.parse(fs.readFileSync(path.join(qa,'photos-apply.json'),'utf8'));const byHash=new Map(candidates.map(x=>[x.source_sha256,x]));
  const products=release.products.map(p=>({sku:p.sku,id:Number(p.product_id),before:{image:Number(p.photos[0].attachment_id),gallery:p.photos.slice(1).map(x=>Number(x.attachment_id))},images:p.photos.map(photo=>({old_attachment_id:Number(photo.attachment_id),old_sha256:photo.sha256,replacement:byHash.get(photo.sha256)||null}))}));
  fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify({schema:1,operation:'owner-authorized-retailer-mark-cleanup',owner_authorized:true,reviewed:false,products,candidates},null,2)+'\n');
 }
 console.log(JSON.stringify({edited:candidates.length,pending,outside_mask_rgb_changed:0,total_delivery_bytes:candidates.reduce((n,x)=>n+x.bytes,0)}));
})().catch(e=>{console.error(e.stack);process.exit(1)});
