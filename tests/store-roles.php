<?php
if (wp_get_environment_type()!=='local') { throw new RuntimeException('Local tests only'); }
if (!class_exists('TehNet_Store_Operations')) { throw new RuntimeException('Store operations roles are missing'); }
TehNet_Store_Operations::install();
foreach (['tn_store_sales'=>['tn_store_sync'],'tn_store_warehouse'=>['tn_store_dispatch'],'tn_store_finance'=>['tn_store_refund','tn_store_settle'],'tn_store_support'=>[]] as $role=>$allowed) {
    $user_id=wp_insert_user(['user_login'=>'synthetic-'.wp_generate_uuid4(),'user_pass'=>wp_generate_password(32),'role'=>$role]);
    if (is_wp_error($user_id)) { throw new RuntimeException('Could not create local permission fixture'); }
    try {
        $user=new WP_User($user_id);
        foreach (['tn_store_sync','tn_store_dispatch','tn_store_refund','tn_store_settle'] as $cap) {
            if (user_can($user,$cap)!==in_array($cap,$allowed,true)) { throw new RuntimeException('Role boundary failed: '.$role.' '.$cap); }
        }
        if (!user_can($user,'tn_store_operations_view') || user_can($user,'manage_options')) { throw new RuntimeException('Read/admin boundary failed'); }
        echo "PASS: $role least-privilege operation boundary\n";
    } finally { require_once ABSPATH.'wp-admin/includes/user.php';wp_delete_user($user_id); }
}
echo "STORE_ROLES=PASSED\n";
