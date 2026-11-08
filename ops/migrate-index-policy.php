<?php
/**
 * Native option-only policy transaction, invoked by the canonical release operator.
 * Private raw row snapshots/journal stay outside web/Git. Never flips blog_public.
 */
try{
 if(!defined('WP_CLI')||!WP_CLI||!current_user_can('manage_options')||is_multisite())throw new RuntimeException('Bounded administrator native CLI required');
 $path=(string)getenv('TN_GROWTH_MANIFEST');$digest=(string)getenv('TN_GROWTH_DIGEST');$dir=(string)getenv('TN_GROWTH_JOURNAL_DIR');$mode=getenv('TN_GROWTH_MODE')?:'check';
 if(!in_array($mode,['check','apply','rollback'],true)||!is_file($path)||is_link($path)||!preg_match('/^[a-f0-9]{64}$/D',$digest)||!hash_equals($digest,hash_file('sha256',$path)))throw new RuntimeException('Immutable policy manifest required');
 $m=json_decode(file_get_contents($path),true,512,JSON_THROW_ON_ERROR);$key=$m['key']??'';$install=$key==='tehnet-index-runtime-20261108-v1';
 if(($m['schema']??null)!==1||!in_array($key,['tehnet-index-runtime-20261108-v1','tehnet-index-allowlist-20261108-v1'],true)||($m['operation']??null)!==($install?'install-off':'activate'))throw new RuntimeException('Unapproved index scope');
 $staging=wp_get_environment_type()==='staging'&&home_url('/')==='http://localhost:18085/';
 $production=home_url('/')==='https://tehnet.ir/'&&getenv('TN_GROWTH_AUTHORIZED_RELEASE')===$key;
 if(!$staging&&!$production)throw new RuntimeException('Index target outside bounded release');
 if($staging&&(!DISABLE_WP_CRON||!WP_HTTP_BLOCK_EXTERNAL||apply_filters('pre_wp_mail',null,[])!==false||!is_wp_error(apply_filters('pre_http_request',false,[],'https://example.invalid'))||apply_filters('woocommerce_available_payment_gateways',['probe'=>new stdClass])!==[]))throw new RuntimeException('Closed staging required');
 $real=realpath($dir);$web=realpath(ABSPATH);
 if(!$real||!is_dir($real)||is_link($dir)||($web&&($real===$web||str_starts_with($real,$web.DIRECTORY_SEPARATOR)))||(fileperms($real)&0077)!==0)throw new RuntimeException('Private policy journal required');
 $file=$real.'/journal.json';if(is_link($file)||is_link($real.'/.lock'))throw new RuntimeException('Policy journal link refused');
 $lock=fopen($real.'/.lock','c+b');if(!$lock||!chmod($real.'/.lock',0600)||!flock($lock,LOCK_EX|LOCK_NB))throw new RuntimeException('Policy journal busy');
 global$wpdb;$option='tn_index_policy_20261108';$dbLock='tn-growth-'.substr(hash('sha256',$wpdb->dbname),0,24);$held=false;$transaction=false;$committed=false;$journal=null;
 $clear=static function()use($option):void{wp_cache_delete($option,'options');wp_cache_delete('alloptions','options');wp_cache_delete('notoptions','options');};
 $row=static function()use($wpdb,$option){return $wpdb->get_row($wpdb->prepare("SELECT option_name,option_value,autoload FROM {$wpdb->options} WHERE option_name=%s",$option),ARRAY_A);};
 $protected=static function()use($wpdb):string{
  $tables=$wpdb->get_col($wpdb->prepare('SHOW TABLES LIKE %s',$wpdb->esc_like($wpdb->prefix).'%'));sort($tables);$state=[];
  foreach($tables as$table){if(!preg_match('/^[A-Za-z0-9_]+$/D',$table))throw new RuntimeException('Unexpected policy table');if($table===$wpdb->options||str_starts_with($table,$wpdb->prefix.'actionscheduler_'))continue;$cols=$wpdb->get_results("SHOW COLUMNS FROM `$table`",ARRAY_A);$order=array_column(array_values(array_filter($cols,static fn($c)=>$c['Key']==='PRI')),'Field')?:array_column($cols,'Field');foreach($order as$c)if(!preg_match('/^[A-Za-z0-9_]+$/D',$c))throw new RuntimeException('Unexpected policy column');$rows=$wpdb->get_results("SELECT * FROM `$table` ORDER BY `".implode('`,`',$order)."`",ARRAY_A);if($wpdb->last_error)throw new RuntimeException('Policy protected read failed');$state[$table]=hash('sha256',serialize($rows));}
  $keys=['blog_public','home','siteurl','active_plugins','stylesheet','template','show_on_front','page_on_front','page_for_posts','woocommerce_shop_page_id','woocommerce_cart_page_id','woocommerce_checkout_page_id','woocommerce_myaccount_page_id','tn_store_settings','woocommerce_cod_settings','woocommerce_bacs_settings','woocommerce_cheque_settings','woocommerce_tn_zarinpal_sandbox_settings','tn_recaptcha_enabled','tn_recaptcha_site_key','tn_recaptcha_secret_key'];
  $rows=$wpdb->get_results($wpdb->prepare("SELECT option_name,option_value,autoload FROM {$wpdb->options} WHERE option_name IN (".implode(',',array_fill(0,count($keys),'%s')).') ORDER BY option_name',...$keys),ARRAY_A);if($wpdb->last_error)throw new RuntimeException('Policy protected option read failed');$state['selected_options']=hash('sha256',serialize($rows));return hash('sha256',serialize($state));
 };
 $save=static function(array $j)use($file):void{$tmp=$file.'.tmp.'.bin2hex(random_bytes(6));$stream=fopen($tmp,'x+b');if(!$stream||!chmod($tmp,0600))throw new RuntimeException('Private policy receipt create failed');$data=wp_json_encode($j,JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE);if(fwrite($stream,$data)!==strlen($data)||!fflush($stream))throw new RuntimeException('Policy receipt write failed');fclose($stream);if(!rename($tmp,$file))throw new RuntimeException('Policy receipt publish failed');};
 $set=static function($expected,$desired)use($wpdb,$option,$row,$clear):void{
  if($row()!==$expected)throw new RuntimeException('Policy option drift; refuse overwrite');
  if($desired===null){if($expected!==null&&$wpdb->delete($wpdb->options,['option_name'=>$option])!==1)throw new RuntimeException('Policy rollback delete failed');}
  elseif($expected===null){if($wpdb->insert($wpdb->options,$desired)!==1)throw new RuntimeException('Policy create failed');}
  elseif($wpdb->update($wpdb->options,$desired,['option_name'=>$option])===false)throw new RuntimeException('Policy restore failed');
  $clear();if($row()!==$desired)throw new RuntimeException('Policy persisted row mismatch');
 };
 $plan=static function()use($m,$install):?array{
  if($install)return null;
  if(!class_exists('TehNet_Core_Index_Policy')||count($m['targets']??[])!==16)throw new RuntimeException('Installed runtime and exact proposed allowlist required');
  $fixed=['/'=>5,'/services/'=>8,'/services/voice-network-readiness/'=>206,'/services/remote-support/'=>37,'/services/mikrotik-tehran/'=>35,'/services/network-setup-tehran/'=>33,'/services/network-support-tehran/'=>31,'/services/network-tehran/'=>29,'/about/'=>10,'/contact/'=>11,'/technical-methodology/'=>187];
  $created=['/network-support-contract-guide/'=>'A1','/network-project-proposal-checklist/'=>'A2','/business-server-planning-guide/'=>'A3','/server-backup-restore-acceptance/'=>'A4','/services/server-virtualization-tehran/'=>'N1'];$approved=[];$seen=[];
  foreach($m['targets']as$t){$p=$t['path']??'';if(!in_array($p,TehNet_Core_Index_Policy::MAX_PATHS,true)||isset($seen[$p]))throw new RuntimeException('Unapproved index path');
   $post=$p==='/'?get_post((int)get_option('page_on_front')):get_page_by_path(trim($p,'/'),OBJECT,'page');
   if(!$post||$post->post_status!=='publish'||$post->post_password!==''||get_permalink($post)!==home_url($p)||$post->post_title!==($t['title']??null)||!hash_equals((string)($t['body_sha256']??''),hash('sha256',$post->post_content)))throw new RuntimeException('Index content readiness or identity drift');
   if(isset($fixed[$p])&&($post->ID!==$fixed[$p]||($t['id']??null)!==$fixed[$p])||isset($created[$p])&&(($t['key']??null)!==$created[$p]||get_post_meta($post->ID,'_tn_growth_key',true)!==$created[$p]))throw new RuntimeException('Index managed owner mismatch');
   if(isset($t['excerpt_sha256'])&&!hash_equals($t['excerpt_sha256'],hash('sha256',$post->post_excerpt)))throw new RuntimeException('Index metadata drift');
   $seen[$p]=true;$approved[]=['path'=>$p,'id'=>(int)$post->ID];
  }
  return ['schema'=>1,'key'=>'tehnet-index-allowlist-20261108-v1','approved'=>$approved];
 };
 try{
  $held=(string)$wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s,0)',$dbLock))==='1';if(!$held)throw new RuntimeException('Policy database lock busy');
  if((string)get_option('blog_public')!=='0'||has_filter('wp_robots','wp_robots_noindex')===false)throw new RuntimeException('Known Reading/core noindex baseline required');
  if((string)$wpdb->get_var('SELECT @@in_transaction')!=='0'||(string)$wpdb->get_var('SELECT @@autocommit')!=='1')throw new RuntimeException('Fresh policy transaction required');
  $engine=$wpdb->get_var($wpdb->prepare('SELECT ENGINE FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s',$wpdb->options));if(strtoupper((string)$engine)!=='INNODB')throw new RuntimeException('Transactional options table required');
  $journal=is_file($file)?json_decode(file_get_contents($file),true,512,JSON_THROW_ON_ERROR):null;
  if($journal&&($journal['digest']!==$digest||$journal['home']!==home_url('/')||$journal['key']!==$key))throw new RuntimeException('Policy journal identity mismatch');
  if($journal&&$journal['status']==='ROLLED_BACK'){if($row()!==$journal['before_option'])throw new RuntimeException('Rolled policy drift');if($mode!=='rollback')throw new RuntimeException('New reviewed policy attempt required');echo wp_json_encode(['status'=>'ROLLED_BACK','option_restored'=>true,'protected_state_unchanged'=>true]);return;}
  if($journal&&$journal['status']!=='APPLIED')throw new RuntimeException('Policy reconciliation required');
  if($journal&&$row()!==$journal['after_option'])throw new RuntimeException('Applied policy option drift');
  if($journal&&$mode!=='rollback'){echo wp_json_encode(['status'=>'APPLIED','protected_state_unchanged'=>true,'policy_scope_unchanged'=>true,'option_writes'=>0]);return;}
  if(!$journal&&$mode==='rollback')throw new RuntimeException('No matching policy journal');
  if(!$journal){if($row()!==null)throw new RuntimeException('Do not adopt existing policy option');$desired=$plan();$before=$protected();if($mode==='check'){echo wp_json_encode(['status'=>'READY','protected_digest'=>$before,'option_writes'=>$install?0:1,'approved_paths'=>$install?0:count($desired['approved']),'blog_public'=>'0']);return;}$journal=['schema'=>1,'status'=>'PREPARED','digest'=>$digest,'home'=>home_url('/'),'key'=>$key,'before_option'=>null,'created_utc'=>gmdate('c')];$save($journal);}
  $before=$protected();if($wpdb->query('START TRANSACTION')===false)throw new RuntimeException('Policy transaction failed');$transaction=true;
  $wpdb->get_results($wpdb->prepare("SELECT option_name FROM {$wpdb->options} WHERE option_name IN (%s,%s) FOR UPDATE",'blog_public',$option));
  $clear();wp_cache_delete('blog_public','options');if((string)get_option('blog_public')!=='0')throw new RuntimeException('Visibility option changed under lock');
  if($mode==='apply'){
   $desired=$plan();if($install&&!class_exists('TehNet_Core_Index_Policy'))throw new RuntimeException('Runtime install incomplete');
   $after=$desired===null?null:['option_name'=>$option,'option_value'=>maybe_serialize($desired),'autoload'=>'off'];$set($journal['before_option'],$after);$journal['after_option']=$after;
   if(!$install&&count(TehNet_Core_Index_Policy::approved())!==16)throw new RuntimeException('Activated allowlist did not validate');
  }else{$set($journal['after_option'],$journal['before_option']);}
  if($protected()!==$before)throw new RuntimeException('Index operation changed protected business state');
  $journal['status']='COMMIT_READY';$save($journal);if($wpdb->query('COMMIT')===false)throw new RuntimeException('Policy commit failed');$transaction=false;$committed=true;
  $journal['status']=$mode==='apply'?'APPLIED':'ROLLED_BACK';$journal['completed_utc']=gmdate('c');$save($journal);
  echo wp_json_encode(['status'=>$journal['status'],'protected_digest'=>$before,'protected_state_unchanged'=>true,'blog_public'=>'0','option_writes'=>$install?0:1,'option_restored'=>$mode==='rollback']);
 }catch(Throwable$e){if($transaction){$ok=$wpdb->query('ROLLBACK')!==false;$clear();if($journal){$journal['status']=$ok?'FAILED':'NEEDS_RECONCILIATION';$save($journal);}}elseif($committed&&$journal){$journal['status']='NEEDS_RECONCILIATION';$save($journal);}throw $e;
 }finally{if($held)$wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)',$dbLock));flock($lock,LOCK_UN);fclose($lock);}
}catch(Throwable$e){throw $e;}
