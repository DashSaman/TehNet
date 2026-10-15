<?php
if (wp_get_environment_type()!=='local') { throw new RuntimeException('Local fixture only'); }
$assert=static function($ok,$name){if(!$ok){throw new RuntimeException($name);}echo "PASS: $name\n";};
$service=new TehNet_Store_Catalog();$file='/catalog/saieedshabake-2026-10-15.json';$hash=hash_file('sha256',$file);
wp_set_current_user(0);
try{$service->release($file,$hash);throw new LogicException('anonymous release accepted');}catch(RuntimeException $e){$assert(str_contains($e->getMessage(),'operator'),'anonymous release rejected');}
$admin=get_users(['role'=>'administrator','number'=>1])[0];wp_set_current_user($admin->ID);
try{$service->release($file,str_repeat('0',64));throw new LogicException('bad hash accepted');}catch(RuntimeException $e){$assert(str_contains($e->getMessage(),'hash mismatch'),'mismatched release hash rejected');}
$plan=$service->release($file,$hash);$assert($plan['dry_run']&&count($plan['created'])===0,'release dry run makes no catalog changes');
$preview=new TehNet_Store_Storefront();$_GET['tn_preview']='1';
$fake=new class {public $args=[];public function set($k,$v){$this->args[$k]=$v;}public function get($k){return $this->args[$k]??null;}};
$preview->query($fake);$assert(($fake->args['post_status']??null)===['publish','draft'],'authorized staff can preview drafts');
wp_set_current_user(0);$fake->args=[];$preview->query($fake);$assert(!isset($fake->args['post_status']),'anonymous query never expands draft visibility');
unset($_GET['tn_preview']);wp_set_current_user($admin->ID);$fake->args=[];$preview->query($fake);$assert(!isset($fake->args['post_status']),'staff default shop remains public-only');
echo "ONLINE_RELEASE=PASSED\n";
