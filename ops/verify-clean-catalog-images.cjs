// Reproduce the delivered lossless images from immutable originals + transparent patches.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const sharp=require(process.env.SHARP_MODULE||'C:/Users/amirreza/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=path.resolve(__dirname,'..'),folder=path.join(root,'content/media/tehnet-clean-2026-10-16');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
(async()=>{
 const manifest=JSON.parse(fs.readFileSync(path.join(folder,'manifest.json'))),results=[];
 assert.equal(manifest.candidates.length,15);assert.equal(manifest.products.length,25);
 for(const c of manifest.candidates){
  const source=fs.readFileSync(path.join(root,'content/media/saieedshabake-2026-10-16',c.source_file));assert.equal(hash(source),c.source_sha256);
  const clean=fs.readFileSync(path.join(folder,c.file)),patch=fs.readFileSync(path.join(folder,c.patch_file));assert.equal(hash(clean),c.sha256);assert.equal(hash(patch),c.patch_sha256);
  const original=await sharp(source).removeAlpha().toColourspace('srgb').raw().toBuffer(),decoded=await sharp(clean).removeAlpha().toColourspace('srgb').raw().toBuffer();
  const {data:delta,info}=await sharp(patch).ensureAlpha().raw().toBuffer({resolveWithObject:true});assert.equal(info.channels,4);assert.deepEqual([info.width,info.height],c.dimensions);
  let outside=0,edited=0;assert.equal(decoded.length,original.length);
  for(let i=0;i<info.width*info.height;i++){
   const a=delta[i*4+3];if(a)edited++;
   for(let ch=0;ch<3;ch++){
    assert.equal(decoded[i*3+ch],Math.round((original[i*3+ch]*(255-a)+delta[i*4+ch]*a)/255),'reproducible original+patch RGB');
    if(!a&&decoded[i*3+ch]!==original[i*3+ch])outside++;
   }
  }
  assert.equal(outside,0);assert.equal(edited,c.edited_pixels);results.push({id:c.id,index:c.index,sha256:c.sha256,edited_pixels:edited,changed_rgb_outside_mask:outside,reconstructed_rgb_exact:true});
 }
 const report={status:'passed',utc:new Date().toISOString(),manifest_sha256:hash(fs.readFileSync(path.join(folder,'manifest.json'))),checks:results,scope:'Pixel reconstruction and immutable source hashes; product-mask appropriateness is a separate visual review.'};
 fs.writeFileSync(path.join(root,'qa/store-2026-10-16/cleanup-pixel-verification.json'),JSON.stringify(report,null,2));
 console.log('CLEANUP_PIXEL_VERIFICATION=PASSED images=15 outside_mask_changed=0 exact_patch_reconstruction=15');
})().catch(e=>{console.error(e.stack);process.exit(1)});
