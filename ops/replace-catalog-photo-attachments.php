<?php
/** Reviewed owner-authorized background cleanup. CLI MANIFEST SHA [dry|apply|rollback]. */
defined('ABSPATH')||exit;
if(!defined('WP_CLI')||!WP_CLI||!current_user_can('manage_woocommerce')||!current_user_can('edit_products')){throw new RuntimeException('Staff CLI only');}
$manifest=$args[0]??'';$digest=$args[1]??'';$mode=$args[2]??'dry';
if(!in_array($mode,['dry','apply','rollback'],true)||!preg_match('/^[a-f0-9]{64}$/',$digest)||!is_file($manifest)||hash_file('sha256',$manifest)!==$digest){throw new RuntimeException('Manifest/hash/mode mismatch');}
if(wp_get_environment_type()!=='local'&&wp_parse_url(home_url(),PHP_URL_HOST)!=='tehnet.ir'){throw new RuntimeException('Unexpected site');}
$data=json_decode(file_get_contents($manifest),true,512,JSON_THROW_ON_ERROR);$base=dirname(realpath($manifest));
if(($data['operation']??'')!=='owner-authorized-retailer-mark-cleanup'||($data['owner_authorized']??false)!==true||($data['reviewed']??false)!==true||count($data['products']??[])!==25||count($data['candidates']??[])!==15){throw new RuntimeException('Unreviewed media cleanup');}
require_once ABSPATH.'wp-admin/includes/file.php';require_once ABSPATH.'wp-admin/includes/image.php';require_once ABSPATH.'wp-admin/includes/media.php';
$key='tn_photo_cleanup_'.substr($digest,0,16);$receipt=get_option($key,[]);$plans=[];$seen=[];$targets=0;
foreach($data['products'] as $row) {
    $sku=$row['sku']??'';$id=wc_get_product_id_by_sku($sku);$p=wc_get_product($id);
    if(!$p||$id!==(int)$row['id']||!preg_match('/^TN-SN-([0-9]+)$/',$sku,$m)||$p->get_meta('_tn_source_key')!=='saieedshabake.ir:product:'.$m[1]||isset($seen[$sku])){throw new RuntimeException('Product ownership mismatch');}$seen[$sku]=true;
    $current=['image'=>(int)$p->get_image_id(),'gallery'=>array_map('intval',$p->get_gallery_image_ids())];$done=$receipt['products'][$sku]??null;
    if($done) {if($current!==$done['after']||$p->get_meta('_tn_photo_cleanup_release')!==$digest){throw new RuntimeException('Human media edit preserved: '.$sku);}}
    elseif($current!==$row['before']||$p->get_meta('_tn_photo_cleanup_release')){throw new RuntimeException('Media drift preserved: '.$sku);}
    $expected=array_merge([$row['before']['image']],$row['before']['gallery']);
    if($expected!==array_column($row['images'],'old_attachment_id')){throw new RuntimeException('Image sequence mismatch');}
    $changed=false;
    foreach($row['images'] as $image) {
        $old=$image['old_attachment_id'];$original=get_attached_file($old);
        if(!wp_attachment_is_image($old)||(int)get_post_field('post_parent',$old)!==$id||!is_file($original)||hash_file('sha256',$original)!==$image['old_sha256']){throw new RuntimeException('Original media drift');}
        $replacement=$image['replacement']??null;if(!$replacement){continue;}$changed=true;$targets++;
        $file=$replacement['file']??'';
        if(!preg_match('/^[a-f0-9]{64}\.webp$/',$file)||($replacement['changed_pixels_outside_mask']??-1)!==0||$replacement['source_sha256']!==$image['old_sha256']){throw new RuntimeException('Unverified image fidelity');}
        $path=$base.'/'.$file;$info=is_file($path)?getimagesize($path):false;
        if(!$info||$info['mime']!=='image/webp'||hash_file('sha256',$path)!==$replacement['sha256']||[$info[0],$info[1]]!==$replacement['dimensions']||!wp_image_editor_supports(['mime_type'=>'image/webp'])){throw new RuntimeException('Unsupported/mismatched lossless image');}
    }
    if($done){foreach(array_merge([$current['image']],$current['gallery'])as $aid){$f=get_attached_file($aid);if(!wp_attachment_is_image($aid)||!is_file($f)){throw new RuntimeException('Clean media missing');}}}
    $plans[]=['id'=>$id,'sku'=>$sku,'row'=>$row,'current'=>$current,'done'=>$done,'changed'=>$changed];
}
if($targets!==15){throw new RuntimeException('Cleanup target count mismatch');}
if($mode==='dry'){echo wp_json_encode(['mode'=>'dry','products'=>25,'create'=>count(array_filter($plans,fn($p)=>$p['changed']&&!$p['done'])),'skip'=>count(array_filter($plans,fn($p)=>!$p['changed']||$p['done'])),'replacement_images'=>15,'sha256'=>$digest])."\n";return;}
$lock='tn_catalog_photo_cleanup_lock';if(!add_option($lock,['sha'=>$digest,'time'=>time()],'','no')){throw new RuntimeException('Cleanup already locked; inspect before recovery');}
$receipt=$receipt?:['sha256'=>$digest,'actor'=>get_current_user_id(),'utc'=>gmdate('c'),'products'=>[]];$changed=0;$skipped=0;$attachmentsCreated=0;
try {
    foreach($plans as $plan) {
        $id=$plan['id'];$sku=$plan['sku'];$done=$plan['done'];
        if($mode==='rollback') {
            if(!$done){$skipped++;continue;}
            update_post_meta($id,'_thumbnail_id',$done['before']['image']);update_post_meta($id,'_product_image_gallery',implode(',',$done['before']['gallery']));delete_post_meta($id,'_tn_photo_cleanup_release');delete_post_meta($id,'_tn_photo_inpaint_note');
            unset($receipt['products'][$sku]);update_option($key,$receipt,false);clean_post_cache($id);wc_delete_product_transients($id);$changed++;continue;
        }
        if(!$plan['changed']||$done){$skipped++;continue;}
        $ids=[];$new=[];
        try {
            foreach($plan['row']['images']as $index=>$image) {
                $replacement=$image['replacement']??null;if(!$replacement){$ids[]=$image['old_attachment_id'];continue;}
                $bits=wp_upload_bits('tn-clean-'.$id.'-'.$index.'-'.substr($replacement['sha256'],0,12).'.webp',null,file_get_contents($base.'/'.$replacement['file']));
                if($bits['error']){throw new RuntimeException('Clean upload failed');}
                $aid=wp_insert_attachment(['post_mime_type'=>'image/webp','post_title'=>'تصویر '.$sku.'؛ ویرایش نوشتهٔ پس‌زمینه','post_parent'=>$id,'post_status'=>'inherit'],$bits['file'],$id,true);
                if(is_wp_error($aid)){wp_delete_file($bits['file']);throw new RuntimeException('Clean attachment failed');}$new[]=$aid;$ids[]=$aid;
                update_post_meta($aid,'_tn_original_sha256',$replacement['sha256']);update_post_meta($aid,'_tn_source_original_sha256',$image['old_sha256']);update_post_meta($aid,'_tn_cleanup_from_attachment',$image['old_attachment_id']);
                update_post_meta($aid,'_tn_photo_rights',get_post_meta($image['old_attachment_id'],'_tn_photo_rights',true));update_post_meta($aid,'_wp_attachment_image_alt','تصویر کالا '.$sku.'؛ جزئیات کالا از تصویر اصلی حفظ شده است');
                $metadata=wp_generate_attachment_metadata($aid,$bits['file']);if(empty($metadata['width'])){throw new RuntimeException('Clean image metadata failed');}wp_update_attachment_metadata($aid,$metadata);
            }
        } catch(Throwable $e) {foreach($new as $aid){wp_delete_attachment($aid,true);}throw $e;}
        $after=['image'=>(int)$ids[0],'gallery'=>array_map('intval',array_slice($ids,1))];
        update_post_meta($id,'_thumbnail_id',$after['image']);update_post_meta($id,'_product_image_gallery',implode(',',$after['gallery']));update_post_meta($id,'_tn_photo_cleanup_release',$digest);update_post_meta($id,'_tn_photo_inpaint_note','Owner-authorized retailer lettering removal; original product pixels preserved outside reviewed background masks.');
        $receipt['products'][$sku]=['id'=>$id,'before'=>$plan['current'],'after'=>$after,'created_attachments'=>$new];update_option($key,$receipt,false);clean_post_cache($id);wc_delete_product_transients($id);$changed++;$attachmentsCreated+=count($new);
    }
    echo wp_json_encode(['mode'=>$mode,'products_changed'=>$changed,'skipped'=>$skipped,'attachments_created'=>$attachmentsCreated,'receipt_option'=>$key,'sha256'=>$digest])."\n";
} finally {delete_option($lock);}
