<?php
// A hidden, explicitly synthetic future Woo product in the isolated clone only.
if(wp_get_environment_type()!=='staging'||home_url()!=='http://localhost:18085'){throw new RuntimeException('Isolated UX clone only');}
if(!current_user_can('manage_woocommerce'))throw new RuntimeException('Staff required');
$id=wc_get_product_id_by_sku('SYNTHETIC-UX-FUTURE-20261016');$p=$id?wc_get_product($id):new WC_Product_Simple();
$p->set_name('نمونهٔ آموزشی آزمون رابط؛ کالای قابل فروش نیست');$p->set_sku('SYNTHETIC-UX-FUTURE-20261016');$p->set_status('publish');$p->set_catalog_visibility('hidden');$p->set_regular_price('');$p->set_manage_stock(true);$p->set_stock_quantity(0);$p->set_description('این رکورد فقط در نسخهٔ آزمایشی برای آزمون مدل آموزشی تألیفی ساخته شده است. ابعاد واقعی یا کالای قابل فروش نیست.');$p->save();$id=$p->get_id();
$attachment=(int)$p->get_meta('_tn_model_attachment_id');
if(!$attachment){$bits=wp_upload_bits('tn-synthetic-ux-cable.glb',null,file_get_contents('/tmp/tn-ux-model.glb'));if($bits['error'])throw new RuntimeException('Fixture upload failed');$attachment=wp_insert_attachment(['post_mime_type'=>'model/gltf-binary','post_title'=>'Synthetic educational UX fixture, never manufacturer CAD','post_status'=>'inherit','post_parent'=>$id],$bits['file'],$id,true);if(is_wp_error($attachment))throw new RuntimeException('Fixture attachment failed');}
$parts=json_decode(file_get_contents('/tmp/tn-ux-parts.json'),true);$parts['mpn']='SYNTHETIC-UX-FUTURE';
$_POST=['tn_product_evidence_nonce'=>wp_create_nonce('tn_product_evidence'),'_tn_verified_mpn'=>'SYNTHETIC-UX-FUTURE','_tn_identity_source'=>'https://example.invalid/synthetic-identity','_tn_identity_reviewed'=>'yes','_tn_model_attachment_id'=>(string)$attachment,'_tn_model_mpn'=>'SYNTHETIC-UX-FUTURE','_tn_model_source'=>'https://example.invalid/original-teaching-geometry','_tn_model_rights'=>'yes','_tn_model_reviewed'=>'yes','_tn_parts_json'=>wp_slash(wp_json_encode($parts)),'_tn_parts_reviewed'=>'yes'];
(new TehNet_Store_Product_Evidence())->save($id);$p=wc_get_product($id);$model=(new TehNet_Store_Product_Evidence())->model($p);
if(!$model||empty($model['parts'])||$p->get_meta('_tn_source_key')||$p->is_purchasable())throw new RuntimeException('Native future-product contract failed');
if(!is_wp_error(wp_remote_get('https://example.invalid/isolation-probe')))throw new RuntimeException('HTTP isolation missing');
if(wp_mail('nobody@example.invalid','Synthetic isolation probe','Never delivered')!==false)throw new RuntimeException('Mail isolation missing');
echo wp_json_encode(['scope'=>'Isolated synthetic fixture only, no production product modified','product_id'=>$id,'url'=>$p->get_permalink(),'source_catalogue_key'=>'','model'=>true,'parts'=>count($model['parts']['parts']),'purchasable'=>$p->is_purchasable(),'external_http_blocked'=>true,'mail_blocked'=>true]);
