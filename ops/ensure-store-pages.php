<?php
if (!defined('WP_CLI') || !WP_CLI || !current_user_can('manage_woocommerce')) {throw new RuntimeException('CLI operator required');}
if(home_url()!=='https://tehnet.ir'){throw new RuntimeException('Wrong deployment');}
$result=[];
foreach(['cart'=>['سبد خرید','tn-cart','[woocommerce_cart]'],'checkout'=>['تسویه حساب','tn-checkout','[woocommerce_checkout]'],'myaccount'=>['حساب کاربری','tn-account','[woocommerce_my_account]']] as $key=>$definition){
    $id=wc_get_page_id($key);
    if($id<1||get_post_status($id)!=='publish'){
        $old=$id;
        $id=wp_insert_post(['post_type'=>'page','post_status'=>'publish','post_title'=>$definition[0],'post_name'=>$definition[1],'post_content'=>$definition[2]],true);
        if(is_wp_error($id)){throw new RuntimeException('Could not create native page');}
        update_option('woocommerce_'.$key.'_page_id',$id);
        add_option('tn_native_page_migration_'.$key,['old_id'=>$old,'new_id'=>$id,'at'=>gmdate('c')],'',false);
    }
    $result[$key]=['id'=>$id,'url'=>get_permalink($id),'status'=>get_post_status($id)];
}
echo wp_json_encode($result);
