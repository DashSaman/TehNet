<?php
/** One bounded, editable primary-menu migration; no content, users, commerce or CAPTCHA options change. */
if(!defined('WP_CLI')||!WP_CLI||!current_user_can('manage_options')||(string)get_option('blog_public')!=='0')throw new RuntimeException('Authorized closed-index CLI required');
$scope='tehnet-corporate-ui-20261101-v1';$environment=wp_get_environment_type();$home=home_url('/');
$staging=$environment==='staging'&&$home==='http://localhost:18085/';
if(!$staging&&!($environment==='production'&&$home==='https://tehnet.ir/'&&getenv('TN_GROWTH_AUTHORIZED_RELEASE')===$scope))throw new RuntimeException('Unapproved corporate target');
if($staging&&(!DISABLE_WP_CRON||!WP_HTTP_BLOCK_EXTERNAL||apply_filters('pre_wp_mail',null,[])!==false||!is_wp_error(apply_filters('pre_http_request',false,[],'https://example.invalid'))||apply_filters('woocommerce_available_payment_gateways',['probe'=>new stdClass])!==[]))throw new RuntimeException('Native staging isolation required');
$path=(string)getenv('TN_GROWTH_MANIFEST');$digest=(string)getenv('TN_GROWTH_DIGEST');$directory=(string)getenv('TN_GROWTH_JOURNAL_DIR');$real=realpath($directory);$web=realpath(ABSPATH);
if(is_link($path)||!is_file($path)||!preg_match('/^[a-f0-9]{64}$/D',$digest)||!hash_equals($digest,hash_file('sha256',$path)))throw new RuntimeException('Immutable manifest required');
$manifest=json_decode(file_get_contents($path),true,512,JSON_THROW_ON_ERROR);
if(($manifest['schema']??null)!==1||($manifest['key']??'')!==$scope||($manifest['menu_location']??'')!=='primary'||($manifest['captcha_activation']??null)!==false||count($manifest['routes']??[])!==10)throw new RuntimeException('Unexpected corporate scope');
if(!$real||is_link($directory)||(fileperms($real)&0077)!==0||!$web||$real===$web||str_starts_with($real,$web.DIRECTORY_SEPARATOR))throw new RuntimeException('Private journal outside web root required');
$mode=getenv('TN_GROWTH_MODE')?:'check';if(!in_array($mode,['check','apply','rollback'],true))throw new RuntimeException('Unknown operation');
$file=$real.'/journal.json';$lockPath=$real.'/.lock';if(is_link($file)||is_link($lockPath))throw new RuntimeException('Journal symlink refused');
$lock=fopen($lockPath,'c+b');if(!$lock||!chmod($lockPath,0600)||!flock($lock,LOCK_EX|LOCK_NB))throw new RuntimeException('Journal busy');
$save=static function(array $journal)use($file):void{
    $tmp=$file.'.tmp.'.bin2hex(random_bytes(6));$data=wp_json_encode($journal);$stream=fopen($tmp,'x+b');
    if(!$stream||!chmod($tmp,0600))throw new RuntimeException('Private journal create failed');
    try{if(fwrite($stream,$data)!==strlen($data)||!fflush($stream)||(function_exists('fsync')&&!fsync($stream)))throw new RuntimeException('Durable journal write failed');}finally{fclose($stream);}
    if(!rename($tmp,$file))throw new RuntimeException('Private journal replace failed');
};
global $wpdb;$held=false;$transaction=false;$previous=$wpdb->suppress_errors(true);$dbLock='tn-growth-'.substr(hash('sha256',$wpdb->dbname),0,24);
try{
    $held=(string)$wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s,0)',$dbLock))==='1';if(!$held)throw new RuntimeException('Database release busy');
    if((string)$wpdb->get_var('SELECT @@in_transaction')!=='0'||(string)$wpdb->get_var('SELECT @@autocommit')!=='1')throw new RuntimeException('Fresh session required');
    if($wpdb->query('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')===false||$wpdb->query('START TRANSACTION WITH CONSISTENT SNAPSHOT')===false)throw new RuntimeException('State snapshot failed');$transaction=true;
    $locations=get_nav_menu_locations();$menu=(int)($locations['primary']??0);$items=wp_get_nav_menu_items($menu);if(!$menu||!is_array($items)||count($items)!==10)throw new RuntimeException('Primary menu drift');
    $byPath=[];
    foreach($items as$item){$route=parse_url($item->url,PHP_URL_PATH);if(parse_url($item->url,PHP_URL_HOST)!==parse_url($home,PHP_URL_HOST)||isset($byPath[$route]))throw new RuntimeException('Foreign or duplicate menu route');$byPath[$route]=$item;}
    $before=[];$after=[];$current=[];$metaIds=[];
    foreach($manifest['routes']as$row){
        $item=$byPath[$row['path']]??null;if(!$item)throw new RuntimeException('Missing reviewed menu route');$id=(int)$item->ID;
        $post=$wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->posts} WHERE ID=%d FOR UPDATE",$id),ARRAY_A);
        $meta=$wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->postmeta} WHERE post_id=%d AND meta_key='_menu_item_menu_item_parent' FOR UPDATE",$id),ARRAY_A);
        if(!$post||count($meta)!==1)throw new RuntimeException('Menu field cardinality changed');$metaIds[$id]=(int)$meta[0]['meta_id'];
        $before[$id]=['menu_order'=>(string)$row['before_order'],'post_title'=>$row['before_title'],'parent'=>'0'];
        $parent=$row['parent']===''?0:(int)($byPath[$row['parent']]->ID??0);if($row['parent']!==''&&!$parent)throw new RuntimeException('Missing parent');
        $after[$id]=['menu_order'=>(string)$row['order'],'post_title'=>$row['title'],'parent'=>(string)$parent];
        $current[$id]=['menu_order'=>(string)$post['menu_order'],'post_title'=>$post['post_title'],'parent'=>$meta[0]['meta_value']];
    }
    $state=[];$tables=$wpdb->get_col($wpdb->prepare('SHOW TABLES LIKE %s',$wpdb->esc_like($wpdb->prefix).'%'));sort($tables);
    foreach($tables as$table){
        if(!preg_match('/^[A-Za-z0-9_]+$/D',$table))throw new RuntimeException('Unexpected table');
        if($table===$wpdb->options||str_starts_with($table,$wpdb->prefix.'actionscheduler_'))continue;
        $columns=$wpdb->get_results("SHOW COLUMNS FROM `$table`",ARRAY_A);$order=array_column(array_values(array_filter($columns,static fn($c)=>$c['Key']==='PRI')),'Field')?:array_column($columns,'Field');
        foreach($order as$column)if(!preg_match('/^[A-Za-z0-9_]+$/D',$column))throw new RuntimeException('Unexpected column');
        $rows=$wpdb->get_results("SELECT * FROM `$table` ORDER BY `".implode('`,`',$order).'`',ARRAY_A);if($wpdb->last_error)throw new RuntimeException('Protected table read failed');
        foreach($rows as&$r){
            if($table===$wpdb->posts&&isset($before[(int)$r['ID']])){$r['menu_order']='OWNED';$r['post_title']='OWNED';}
            if($table===$wpdb->postmeta&&in_array((int)$r['meta_id'],$metaIds,true))$r['meta_value']='OWNED';
        }unset($r);$state[$table]=hash('sha256',serialize($rows));
    }
    $keys=['blog_public','home','siteurl','active_plugins','stylesheet','template','show_on_front','page_on_front','page_for_posts','woocommerce_shop_page_id','woocommerce_cart_page_id','woocommerce_checkout_page_id','woocommerce_myaccount_page_id','tn_store_settings','woocommerce_cod_settings','woocommerce_bacs_settings','woocommerce_cheque_settings','woocommerce_tn_zarinpal_sandbox_settings','theme_mods_tehnet','tn_recaptcha_enabled','tn_recaptcha_site_key','tn_recaptcha_secret_key'];
    $rows=$wpdb->get_results($wpdb->prepare("SELECT option_name,option_value,autoload FROM {$wpdb->options} WHERE option_name IN (".implode(',',array_fill(0,count($keys),'%s')).') ORDER BY option_name',...$keys),ARRAY_A);if($wpdb->last_error)throw new RuntimeException('Protected option read failed');$state['selected_options']=hash('sha256',serialize($rows));
    if((new TehNet_Store_ERP())->ready()||TehNet_Store_Zarinpal_Sandbox::enabled()||get_option('tn_recaptcha_enabled','no')==='yes'||(defined('TN_RECAPTCHA_ENABLED')&&TN_RECAPTCHA_ENABLED))throw new RuntimeException('Closed commerce and inactive CAPTCHA required');
    $protected=hash('sha256',serialize($state));$journal=is_file($file)?json_decode(file_get_contents($file),true,512,JSON_THROW_ON_ERROR):null;
    if($journal&&(($journal['digest']??'')!==$digest||($journal['home']??'')!==$home||($journal['environment']??'')!==$environment||($journal['protected_digest']??'')!==$protected||!in_array($journal['status']??'',['APPLIED','ROLLED_BACK'],true)||$journal['before']!==$before||$journal['after']!==$after))throw new RuntimeException('Protected state or journal drift; preserve evidence');
    $expected=$journal&&$journal['status']==='APPLIED'?$after:$before;if($current!==$expected)throw new RuntimeException('Editable menu drift; preserve owner changes');
    if(!$journal&&$mode==='rollback')throw new RuntimeException('No applied journal');
    if($journal&&$journal['status']==='ROLLED_BACK'&&$mode!=='rollback')throw new RuntimeException('Rolled-back release requires reviewed new attempt');
    $changed=0;
    if(($mode==='apply'&&!$journal)||($mode==='rollback'&&$journal['status']==='APPLIED')){
        $target=$mode==='apply'?$after:$before;
        $journal=['digest'=>$digest,'home'=>$home,'environment'=>$environment,'status'=>'PREPARED','protected_digest'=>$protected,'before'=>$before,'after'=>$after];$save($journal);
        foreach($target as$id=>$value){
            if($wpdb->update($wpdb->posts,['menu_order'=>(int)$value['menu_order'],'post_title'=>$value['post_title']],['ID'=>$id])===false||$wpdb->update($wpdb->postmeta,['meta_value'=>$value['parent']],['meta_id'=>$metaIds[$id]])===false)throw new RuntimeException('Menu write failed');++$changed;
        }
        if($wpdb->query('COMMIT')===false)throw new RuntimeException('Ambiguous menu commit; reconcile privately');$transaction=false;
        foreach(array_keys($target)as$id)clean_post_cache($id);clean_term_cache($menu,'nav_menu');
        $journal['status']=$mode==='apply'?'APPLIED':'ROLLED_BACK';$save($journal);
    }
    echo wp_json_encode(['status'=>$journal['status']??'READY','protected_digest'=>$protected,'protected_state_unchanged'=>true,'menu_items_updated'=>$changed,'pages_created'=>0,'hubs_updated'=>0,'captcha_enabled'=>false]);
}finally{
    if($transaction)$wpdb->query('ROLLBACK');if($held)$wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)',$dbLock));$wpdb->suppress_errors($previous);flock($lock,LOCK_UN);fclose($lock);
}
