<?php
/** Phone presentation-only scope. Reads WordPress data; journals digests privately, never updates DB rows. */
if (!defined('WP_CLI') || !WP_CLI || !current_user_can('manage_options') || (string)get_option('blog_public') !== '0') throw new RuntimeException('Authorized closed-index native CLI required');
$scope='tehnet-phone-rtl-20261101-v1';
$environment=wp_get_environment_type();$home=home_url('/');
$staging=$environment==='staging' && $home==='http://localhost:18085/';
if (!$staging && !($environment==='production' && $home==='https://tehnet.ir/' && getenv('TN_GROWTH_AUTHORIZED_RELEASE')===$scope)) throw new RuntimeException('Unapproved phone display target');
if ($staging && (!DISABLE_WP_CRON || !WP_HTTP_BLOCK_EXTERNAL || apply_filters('pre_wp_mail',null,[])!==false || !is_wp_error(apply_filters('pre_http_request',false,[],'https://example.invalid')) || apply_filters('woocommerce_available_payment_gateways',['probe'=>new stdClass])!==[])) throw new RuntimeException('Native staging isolation required');
$path=(string)getenv('TN_GROWTH_MANIFEST');$digest=(string)getenv('TN_GROWTH_DIGEST');$directory=(string)getenv('TN_GROWTH_JOURNAL_DIR');$real=realpath($directory);$web=realpath(ABSPATH);
if (is_link($path) || !is_file($path) || !preg_match('/^[a-f0-9]{64}$/D',$digest) || !hash_equals($digest,hash_file('sha256',$path))) throw new RuntimeException('Immutable phone display manifest required');
$manifest=json_decode(file_get_contents($path),true,512,JSON_THROW_ON_ERROR);
if (($manifest['schema']??null)!==1 || ($manifest['key']??'')!==$scope || ($manifest['runtime_files']??null)!==['plugins/tehnet-core/includes/class-settings.php','themes/tehnet/footer.php','plugins/tehnet-core/includes/class-quotes.php','themes/tehnet/assets/css/corporate.css'] || ($manifest['database_changes_allowed']??null)!==false || ($manifest['phone_display_only']??null)!==true) throw new RuntimeException('Unexpected phone display scope');
if (!$real || is_link($directory) || (fileperms($real)&0077)!==0 || !$web || $real===$web || str_starts_with($real,$web.DIRECTORY_SEPARATOR)) throw new RuntimeException('Private journal outside web root required');
$mode=getenv('TN_GROWTH_MODE')?:'check';if (!in_array($mode,['check','apply','rollback'],true)) throw new RuntimeException('Unknown phone display operation');
$file=$real.'/journal.json';$lockPath=$real.'/.lock';
if (is_link($file) || is_link($lockPath)) throw new RuntimeException('Journal symlink refused');
$lock=fopen($lockPath,'c+b');if (!$lock || !chmod($lockPath,0600) || !flock($lock,LOCK_EX|LOCK_NB)) throw new RuntimeException('Phone display journal busy');
global $wpdb;
$held=false;$transaction=false;$previousErrors=$wpdb->suppress_errors(true);$dbLock='tn-growth-'.substr(hash('sha256',$wpdb->dbname),0,24);
try {
    $held=(string)$wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s,0)',$dbLock))==='1';if (!$held) throw new RuntimeException('Native release database lock busy');
    if ((string)$wpdb->get_var('SELECT @@in_transaction')!=='0' || (string)$wpdb->get_var('SELECT @@autocommit')!=='1') throw new RuntimeException('Fresh native session required');
    if ($wpdb->query('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ')===false || $wpdb->query('START TRANSACTION WITH CONSISTENT SNAPSHOT')===false) throw new RuntimeException('Read-only state snapshot failed');
    $transaction=true;$state=[];
    $tables=$wpdb->get_col($wpdb->prepare('SHOW TABLES LIKE %s',$wpdb->esc_like($wpdb->prefix).'%'));sort($tables);
    foreach ($tables as $table) {
        if (!preg_match('/^[A-Za-z0-9_]+$/D',$table)) throw new RuntimeException('Unexpected table name');
        if ($table===$wpdb->options || str_starts_with($table,$wpdb->prefix.'actionscheduler_')) continue;
        $columns=$wpdb->get_results("SHOW COLUMNS FROM `$table`",ARRAY_A);
        $order=array_column(array_values(array_filter($columns,static fn($c)=>$c['Key']==='PRI')),'Field')?:array_column($columns,'Field');
        foreach ($order as $column) if (!preg_match('/^[A-Za-z0-9_]+$/D',$column)) throw new RuntimeException('Unexpected column name');
        $rows=$wpdb->get_results("SELECT * FROM `$table` ORDER BY `".implode('`,`',$order).'`',ARRAY_A);if ($wpdb->last_error) throw new RuntimeException('Protected table read failed');
        $state[$table]=hash('sha256',serialize($rows));
    }
    $keys=['blog_public','home','siteurl','active_plugins','stylesheet','template','show_on_front','page_on_front','page_for_posts','woocommerce_shop_page_id','woocommerce_cart_page_id','woocommerce_checkout_page_id','woocommerce_myaccount_page_id','tn_store_settings','tehnet_phone','theme_mods_tehnet','woocommerce_cod_settings','woocommerce_bacs_settings','woocommerce_cheque_settings','woocommerce_tn_zarinpal_sandbox_settings'];
    $rows=$wpdb->get_results($wpdb->prepare("SELECT option_name,option_value,autoload FROM {$wpdb->options} WHERE option_name IN (".implode(',',array_fill(0,count($keys),'%s')).') ORDER BY option_name',...$keys),ARRAY_A);if ($wpdb->last_error) throw new RuntimeException('Protected option read failed');
    $state['selected_options']=hash('sha256',serialize($rows));
    $state['commerce']=['erp'=>(new TehNet_Store_ERP())->ready(),'sandbox'=>TehNet_Store_Zarinpal_Sandbox::enabled()];
    if ($state['commerce']['erp'] || $state['commerce']['sandbox']) throw new RuntimeException('Closed commerce required');
    $protected=hash('sha256',serialize($state));
    $journal=is_file($file)?json_decode(file_get_contents($file),true,512,JSON_THROW_ON_ERROR):null;
    if ($journal && (($journal['digest']??'')!==$digest || ($journal['home']??'')!==$home || ($journal['environment']??'')!==$environment || ($journal['protected_digest']??'')!==$protected || !in_array($journal['status']??'',['APPLIED','ROLLED_BACK'],true))) throw new RuntimeException('Phone display protected state/journal drift; preserve foreign data');
    if (!$journal && $mode==='rollback') throw new RuntimeException('No applied phone display journal');
    if ($journal && $journal['status']==='ROLLED_BACK' && $mode!=='rollback') throw new RuntimeException('Rolled-back phone display release needs a reviewed new attempt');
    if ($mode!=='check') {
        $journal=['digest'=>$digest,'home'=>$home,'environment'=>$environment,'status'=>$mode==='apply'?'APPLIED':'ROLLED_BACK','protected_digest'=>$protected];
        $tmp=$file.'.tmp.'.bin2hex(random_bytes(6));$data=wp_json_encode($journal);$stream=fopen($tmp,'x+b');
        if (!$stream || !chmod($tmp,0600)) throw new RuntimeException('Private journal create failed');
        try {if (fwrite($stream,$data)!==strlen($data) || !fflush($stream) || (function_exists('fsync') && !fsync($stream))) throw new RuntimeException('Durable journal write failed');} finally {fclose($stream);}
        if (!rename($tmp,$file)) throw new RuntimeException('Private journal replace failed');
    }
    $status=$journal['status']??'READY';
    echo wp_json_encode(['status'=>$status,'pages_pending'=>0,'hubs_pending'=>0,'pages_created'=>0,'hubs_updated'=>0,'hubs_restored'=>0,'pages_drafted'=>0,'protected_digest'=>$protected,'protected_state_unchanged'=>true,'database_rows_written'=>0]);
} finally {
    if ($transaction) $wpdb->query('ROLLBACK');
    if ($held) $wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)',$dbLock));
    $wpdb->suppress_errors($previousErrors);flock($lock,LOCK_UN);fclose($lock);
}
