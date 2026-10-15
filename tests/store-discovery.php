<?php
if(wp_get_environment_type()!=='local'){throw new RuntimeException('Local synthetic tests only');}
$assert=static function($ok,$name){if(!$ok){throw new RuntimeException($name);}echo "PASS: $name\n";};
$assert(method_exists('TehNet_Store_Storefront','normalize_search'),'search normalizer exists');
$assert(TehNet_Store_Storefront::normalize_search('كيستون ۱۲۳٤٥۶')==='کیستون 123456','Persian/Arabic letters and numerals normalize');
$service=new TehNet_Store_Storefront();
$request=$service->normalize_request(['post_type'=>'product','s'=>'كابل']);$assert($request['s']==='کابل','product request normalizes letters');
$blog=$service->normalize_request(['post_type'=>'post','s'=>'كابل']);$assert($blog['s']==='كابل','blog requests are unchanged');
$id=wc_get_product_id_by_sku('TN-SN-18002');$assert($id>0,'review catalog fixture exists');
wp_set_current_user(0);
$public=new WP_Query(['post_type'=>'product','s'=>'TN-SN-18002','fields'=>'ids']);$assert(!in_array($id,$public->posts,true),'SKU lookup never publishes an existing draft to anonymous search');
$admin=get_users(['role'=>'administrator','number'=>1])[0];wp_set_current_user($admin->ID);
$staff=new WP_Query(['post_type'=>'product','post_status'=>'draft','s'=>'TN-SN-۱۸۰۰۲','fields'=>'ids']);$assert(array_map('intval',$staff->posts)===[$id],'staff exact SKU search accepts Persian digits');
$p=new WC_Product_Simple();$p->set_name('SYNTHETIC DISCOVERY TEST');$p->set_status('draft');$p->set_sku('TN-DISCOVERY-'.wp_generate_uuid4());$p->update_meta_data('_tn_source_attributes',['shield'=>'SFTP']);$p->save();
try{
    $data=$service->comparison_data($p);
    $assert($data['specs']['shield']==='تأیید نشده','unverified source attributes never enter technical comparison');
    $p->update_meta_data('_tn_verified_shield','UTP');$p->update_meta_data('_tn_verified_jacket','PVC');
    $data=$service->comparison_data($p);$assert($data['specs']['shield']==='UTP'&&$data['specs']['jacket']==='PVC','reviewed specs are compared');
    $assert($data['sku']===$p->get_sku()&&$data['price']==='نیازمند استعلام','SKU identity and inquiry price are explicit');
    $p->update_meta_data('_tn_verified_environment','GUESS');$data=$service->comparison_data($p);$assert($data['specs']['environment']==='تأیید نشده','unsupported technical values remain unknown');
}finally{wp_delete_post($p->get_id(),true);}
echo "STORE_DISCOVERY=PASSED\n";
