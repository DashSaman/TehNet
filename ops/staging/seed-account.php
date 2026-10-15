<?php
if (wp_get_environment_type()!=='local') { throw new RuntimeException('Local fixtures only'); }
$login='tn-sandbox-customer';$user=get_user_by('login',$login);
if ($user && get_user_meta($user->ID,'_tn_sandbox_customer',true)!=='yes') { throw new RuntimeException('Existing account is not a synthetic fixture'); }
$password=wp_generate_password(36,false,false);
if (!$user) {
    $id=wp_insert_user(['user_login'=>$login,'user_pass'=>$password,'user_email'=>'tn-sandbox@example.invalid','first_name'=>'مشتری آزمایشی','role'=>'customer']);
    if (is_wp_error($id)) { throw new RuntimeException('Synthetic account creation failed'); }
    update_user_meta($id,'_tn_sandbox_customer','yes');
} else { $id=$user->ID;wp_set_password($password,$id); }
$orders=wc_get_orders(['limit'=>1,'orderby'=>'date','order'=>'DESC','meta_query'=>[['key'=>'_tn_synthetic_fixture','value'=>'yes']]]);
if (!$orders) { throw new RuntimeException('Run erp-lifecycle.php before seeding the account preview'); }
$order=$orders[0];$order->set_customer_id($id);$order->save();
// A local wrapper captures this directly into ignored .env; never print it in tool output.
echo wp_json_encode(['username'=>$login,'password'=>$password,'order_id'=>$order->get_id()]);
