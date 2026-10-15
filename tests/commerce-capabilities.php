<?php
if(wp_get_environment_type()!=='local'){throw new RuntimeException('Local tests only');}
$admin=get_user_by('login','tehnet-stage');
wp_set_current_user($admin->ID);
if(!current_user_can('manage_woocommerce')){throw new RuntimeException('Administrator lost primitive manage_woocommerce after commerce post type registration');}
echo "PASS: administrator can manage WooCommerce\n";
$created=[];$documents=[];$token=wp_generate_password(8,false,false);
try{
    foreach(['shop_manager','customer'] as $role){
        $id=wp_insert_user(['user_login'=>'tn-permission-'.$role.'-'.$token,'user_pass'=>wp_generate_password(32,true),'user_email'=>$role.'-'.$token.'@example.invalid','role'=>$role]);
        if(is_wp_error($id)){throw new RuntimeException($id->get_error_message());}
        $created[$role]=$id;
    }
    foreach(['tn_inquiry','tn_quote','tn_invoice'] as $type){
        $id=wp_insert_post(['post_type'=>$type,'post_status'=>'private','post_author'=>$admin->ID,'post_title'=>'LOCAL PERMISSION FIXTURE '.$token]);$documents[]=$id;
        foreach([$admin->ID,$created['shop_manager']] as $staff){
            wp_set_current_user($staff);
            if(!current_user_can('manage_woocommerce') || !current_user_can('edit_post',$id)){throw new RuntimeException('Authorized staff cannot edit '.$type);}
        }
        wp_set_current_user($created['customer']);
        if(current_user_can('manage_woocommerce') || current_user_can('read_post',$id) || current_user_can('edit_post',$id)){throw new RuntimeException('Customer can access private commerce document');}
        echo 'PASS: staff/customer isolation '.$type."\n";
    }
}finally{
    wp_set_current_user($admin->ID);
    foreach($documents as $id){if(str_ends_with(get_the_title($id),$token)){wp_delete_post($id,true);}}
    require_once ABSPATH.'wp-admin/includes/user.php';
    foreach($created as $id){$user=get_userdata($id);if($user && str_ends_with($user->user_email,'@example.invalid')){wp_delete_user($id);}}
}
echo "COMMERCE_CAPABILITIES=PASSED\n";
