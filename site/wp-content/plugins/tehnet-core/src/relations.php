<?php
if(!defined('ABSPATH'))exit;
function tehnet_register_relation_meta():void{$keys=['_tehnet_related_lab_ids','_tehnet_related_course_ids','_tehnet_related_product_ids','_tehnet_related_service_ids'];foreach(['post','tn_lab','tn_service'] as $type){foreach($keys as $key){register_post_meta($type,$key,['type'=>'array','single'=>true,'show_in_rest'=>['schema'=>['type'=>'array','items'=>['type'=>'integer']]],'sanitize_callback'=>'tehnet_sanitize_id_list','auth_callback'=>static fn()=>current_user_can('edit_posts')]);}}}
add_action('init','tehnet_register_relation_meta');
function tehnet_sanitize_id_list($value):array{if(!is_array($value))return[];return array_values(array_unique(array_filter(array_map('absint',$value))));}
