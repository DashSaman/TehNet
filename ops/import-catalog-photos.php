<?php
/** wp eval-file SCRIPT MANIFEST SHA256 [apply|rollback]; dry run is default. No remote fetch. */
defined('ABSPATH')||exit;
if(!defined('WP_CLI')||!WP_CLI||!current_user_can('manage_woocommerce')||!current_user_can('edit_products')){throw new RuntimeException('Staff CLI only');}
$manifest=$args[0]??'';$digest=$args[1]??'';$mode=$args[2]??'dry';
if(!in_array($mode,['dry','apply','rollback'],true)||!preg_match('/^[a-f0-9]{64}$/',$digest)||!is_file($manifest)||hash_file('sha256',$manifest)!==$digest){throw new RuntimeException('Manifest/hash/mode mismatch');}
if(wp_get_environment_type()!=='local'&&wp_parse_url(home_url(),PHP_URL_HOST)!=='tehnet.ir'){throw new RuntimeException('Unexpected site');}
$data=json_decode(file_get_contents($manifest),true,512,JSON_THROW_ON_ERROR);
if(($data['schema']??0)!==1||($data['source']??'')!=='saieedshabake.ir'||($data['rights']['status']??'')!=='owner-confirmed'||empty($data['rights']['evidence'])||count($data['products']??[])!==25){throw new RuntimeException('Unreviewed manifest');}
$key='tn_photo_release_'.substr($digest,0,16);$receipt=get_option($key,[]);$plans=[];$seen=[];$base=dirname(realpath($manifest));
foreach($data['products'] as $row) {
    $sku=$row['sku']??'';$sid=(int)($row['source_id']??0);
    if($sku!=='TN-SN-'.$sid||isset($seen[$sku])||($row['source_key']??'')!=='saieedshabake.ir:product:'.$sid||!empty($row['spin_frames'])){throw new RuntimeException('Identity or unreviewed spin: '.$sku);}$seen[$sku]=true;
    $id=wc_get_product_id_by_sku($sku);$p=wc_get_product($id);
    if(!$p||$p->get_meta('_tn_source_key')!==$row['source_key']||(int)$p->get_meta('_tn_source_id')!==$sid){throw new RuntimeException('Source ownership: '.$sku);}
    $current=['image'=>(int)$p->get_image_id(),'gallery'=>array_map('intval',$p->get_gallery_image_ids())];
    $done=$receipt['products'][$sku]??null;
    if($done) {
        if($current!==$done['after']||$p->get_meta('_tn_photo_release')!==$digest){throw new RuntimeException('Media edited since release: '.$sku);}
        foreach(array_merge([$current['image']],$current['gallery']) as $aid){if(!wp_attachment_is_image($aid)||!is_file(get_attached_file($aid))){throw new RuntimeException('Released image missing: '.$sku);}}
    } elseif($current['image']||$current['gallery']||$p->get_meta('_tn_photo_release')) {throw new RuntimeException('Existing human media preserved: '.$sku);}
    if(empty($row['images'])||count($row['images'])>10){throw new RuntimeException('Photo count: '.$sku);}
    foreach($row['images'] as $image) {
        $file=$image['file']??'';
        if(!preg_match('/^[a-f0-9]{64}\.(jpg|png|webp)$/',$file)){throw new RuntimeException('Unsafe filename');}
        $path=$base.'/'.$file;$info=is_file($path)?getimagesize($path):false;
        if(!$info||!in_array($info['mime'],['image/jpeg','image/png','image/webp'],true)||filesize($path)>6*1024*1024||hash_file('sha256',$path)!==$image['sha256']||[$info[0],$info[1]]!==$image['dimensions']){throw new RuntimeException('Media bytes mismatch: '.$sku);}
        if(wp_parse_url($image['url'],PHP_URL_HOST)!=='saieedshabake.ir'){throw new RuntimeException('Unexpected provenance');}
    }
    $plans[]=['id'=>$id,'sku'=>$sku,'row'=>$row,'current'=>$current,'done'=>$done];
}
if($mode==='dry'){echo wp_json_encode(['mode'=>'dry','products'=>count($plans),'create'=>count(array_filter($plans,fn($p)=>!$p['done'])),'skip'=>count(array_filter($plans,fn($p)=>(bool)$p['done'])),'sha256'=>$digest])."\n";return;}
$lock='tn_catalog_photo_lock';if(!add_option($lock,['sha'=>$digest,'time'=>time()],'','no')){throw new RuntimeException('Media operation already locked; inspect before recovery');}
require_once ABSPATH.'wp-admin/includes/file.php';require_once ABSPATH.'wp-admin/includes/image.php';require_once ABSPATH.'wp-admin/includes/media.php';
$receipt=$receipt?:['sha256'=>$digest,'actor'=>get_current_user_id(),'created_utc'=>gmdate('c'),'products'=>[]];$created=0;$skipped=0;
try {
    foreach($plans as $plan) {
        $id=$plan['id'];$sku=$plan['sku'];$done=$plan['done'];
        if($mode==='rollback') {
            if(!$done){continue;}
            update_post_meta($id,'_thumbnail_id',$done['before']['image']);update_post_meta($id,'_product_image_gallery',implode(',',$done['before']['gallery']));
            delete_post_meta($id,'_tn_photo_release');delete_post_meta($id,'_tn_photo_provenance');
            unset($receipt['products'][$sku]);update_option($key,$receipt,false);clean_post_cache($id);wc_delete_product_transients($id);$created++;continue;
        }
        if($done){$skipped++;continue;}
        $new=[];
        try {
            foreach($plan['row']['images'] as $n=>$image) {
                $bits=wp_upload_bits('tn-'.$plan['row']['source_id'].'-'.$n.'-'.substr($image['sha256'],0,12).'.'.pathinfo($image['file'],PATHINFO_EXTENSION),null,file_get_contents($base.'/'.$image['file']));
                if($bits['error']){throw new RuntimeException('Upload failed: '.$sku);}
                $aid=wp_insert_attachment(['post_mime_type'=>wp_check_filetype($bits['file'])['type'],'post_title'=>'تصویر کاتالوگ '.$sku.' — '.($n+1),'post_status'=>'inherit','post_parent'=>$id],$bits['file'],$id,true);
                if(is_wp_error($aid)){wp_delete_file($bits['file']);throw new RuntimeException('Attachment creation failed');}$new[]=$aid;
                update_post_meta($aid,'_tn_photo_source_url',$image['url']);update_post_meta($aid,'_tn_original_sha256',$image['sha256']);update_post_meta($aid,'_tn_photo_rights',$data['rights']);
                update_post_meta($aid,'_wp_attachment_image_alt','تصویر کاتالوگ '.$sku.'؛ تطبیق مدل هنگام استعلام');
                $metadata=wp_generate_attachment_metadata($aid,$bits['file']);if(empty($metadata['width'])){throw new RuntimeException('Image decoding failed');}wp_update_attachment_metadata($aid,$metadata);
            }
        } catch(Throwable $e) {foreach($new as $aid){wp_delete_attachment($aid,true);}throw $e;}
        $after=['image'=>(int)$new[0],'gallery'=>array_map('intval',array_slice($new,1))];
        // Only media metadata is changed; native prices, stock, title, status, and orders are untouched.
        update_post_meta($id,'_tn_photo_release',$digest);update_post_meta($id,'_tn_photo_provenance',['source_url'=>$plan['row']['source_url'],'rights'=>$data['rights'],'photographic_origin'=>'unverified-source-catalog-image','exact_model_verified'=>false]);
        update_post_meta($id,'_thumbnail_id',$after['image']);update_post_meta($id,'_product_image_gallery',implode(',',$after['gallery']));
        $receipt['products'][$sku]=['id'=>$id,'before'=>$plan['current'],'after'=>$after,'created_attachments'=>$new];update_option($key,$receipt,false);
        clean_post_cache($id);wc_delete_product_transients($id);$created++;
    }
    echo wp_json_encode(['mode'=>$mode,'products_changed'=>$created,'skipped'=>$skipped,'receipt_option'=>$key,'sha256'=>$digest])."\n";
} finally {delete_option($lock);}
