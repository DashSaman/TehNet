<?php
// Native migration control flow with isolated filesystem-backed WP fixtures.
define('ABSPATH',sys_get_temp_dir().'/tn-cleanup-unit-'.getmypid().'/');define('WP_CLI',true);
$repo=dirname(__DIR__);$folder=$repo.'/content/media/tehnet-clean-2026-10-16';$realManifest=$folder.'/manifest.json';$originalManifest=json_decode(file_get_contents($realManifest),true);$products=[];$attachments=[];$parents=[];$updates=[];$options=[];$counter=4000;$webpSupported=true;
class CleanupFixture {function __construct(public $row){}function get_image_id(){global $updates;return $updates[$this->row['id']]['_thumbnail_id']??$this->row['before']['image'];}function get_gallery_image_ids(){global $updates;$v=$updates[$this->row['id']]['_product_image_gallery']??null;return $v===null?$this->row['before']['gallery']:($v===''?[]:array_map('intval',explode(',',$v)));}function get_meta($k){global $updates;return $updates[$this->row['id']][$k]??($k==='_tn_source_key'?'saieedshabake.ir:product:'.substr($this->row['sku'],6):'');}}
foreach($originalManifest['products']as $row){$products[$row['sku']]=new CleanupFixture($row);foreach($row['images']as $im){$files=glob($repo.'/content/media/saieedshabake-2026-10-16/'.$im['old_sha256'].'.*');$attachments[$im['old_attachment_id']]=$files[0];$parents[$im['old_attachment_id']]=$row['id'];}}
function current_user_can($c){return true;}function wp_get_environment_type(){return 'local';}function get_current_user_id(){return 1;}
function wc_get_product_id_by_sku($s){global $products;return $products[$s]->row['id']??0;}function wc_get_product($id){global $products;foreach($products as $p)if($p->row['id']===$id)return $p;return false;}
function wp_parse_url($u,$c){return parse_url($u,$c);}function wp_json_encode($v){return json_encode($v);}
function get_option($k,$d=false){global $options;return $options[$k]??$d;}function add_option($k,$v,...$a){global $options;if(isset($options[$k]))return false;$options[$k]=$v;return true;}function update_option($k,$v,...$a){global $options;$options[$k]=$v;}function delete_option($k){global $options;unset($options[$k]);}
function update_post_meta($id,$k,$v){global $updates;$updates[$id][$k]=$v;}function delete_post_meta($id,$k){global $updates;unset($updates[$id][$k]);}function get_post_meta($id,$k,$single){global $updates;return $updates[$id][$k]??['status'=>'owner-confirmed'];}
function clean_post_cache($id){}function wc_delete_product_transients($id){}function is_wp_error($x){return false;}
function wp_upload_bits($n,$unused,$b){$f=ABSPATH.$n;file_put_contents($f,$b);return ['file'=>$f,'error'=>false];}
function wp_insert_attachment($post,$file,$parent,$err){global $counter,$attachments,$parents;$id=++$counter;$attachments[$id]=$file;$parents[$id]=$parent;return $id;}
function wp_generate_attachment_metadata($id,$f){$i=getimagesize($f);return ['width'=>$i[0],'height'=>$i[1]];}function wp_update_attachment_metadata($id,$m){}
function wp_attachment_is_image($id){global $attachments;return isset($attachments[$id]);}function get_attached_file($id){global $attachments;return $attachments[$id]??'';}function get_post_field($field,$id){global $parents;return $parents[$id]??0;}
function wp_image_editor_supports($a){global $webpSupported;return $webpSupported;}
function wp_delete_file($f){if(!str_starts_with($f,ABSPATH))throw new RuntimeException('Fixture refuses source deletion');if(is_file($f))unlink($f);}
function wp_delete_attachment($id,$force){global $attachments;wp_delete_file($attachments[$id]);unset($attachments[$id]);}
mkdir(ABSPATH.'wp-admin/includes',0777,true);foreach(['file','image','media']as $n)file_put_contents(ABSPATH.'wp-admin/includes/'.$n.'.php','<?php');
$fixtureManifest=$folder.'/unit-manifest-tmp.json';$fixtureData=$originalManifest;$fixtureData['reviewed']=true;file_put_contents($fixtureManifest,json_encode($fixtureData));
function invokeCleanup($mode,$file=null){$input=$file??$GLOBALS['fixtureManifest'];$args=[$input,hash_file('sha256',$input),$mode];ob_start();try{include __DIR__.'/../ops/replace-catalog-photo-attachments.php';return json_decode(trim(ob_get_contents()),true);}finally{ob_end_clean();}}
function check($ok,$s){if(!$ok)throw new RuntimeException($s);echo "PASS $s\n";}
$first=$originalManifest['products'][0]['id'];$before=$originalManifest['products'][0]['before'];
try{
 $pending=ABSPATH.'pending.json';$p=$fixtureData;$p['reviewed']=false;file_put_contents($pending,json_encode($p));$failed=false;try{invokeCleanup('dry',$pending);}catch(RuntimeException $e){$failed=true;}check($failed,'unreviewed cleanup cannot run');unlink($pending);
 $r=invokeCleanup('dry');check($r['create']===11&&$r['skip']===14&&count($attachments)===30,'dry run reports 11 affected products and changes nothing');
 $updates[$first]['_thumbnail_id']=9999;$failed=false;try{invokeCleanup('apply');}catch(RuntimeException $e){$failed=true;}check($failed&&count($attachments)===30,'human media drift blocks all writes');unset($updates[$first]);
 $r=invokeCleanup('apply');check($r['products_changed']===11&&$r['attachments_created']===15&&count($attachments)===45,'15 clean files replace marked references on 11 products');
 $r=invokeCleanup('apply');check($r['products_changed']===0&&$r['skipped']===25&&count($attachments)===45,'repeat produces zero writes and no duplicate attachments');
 foreach($originalManifest['products']as $row){foreach(array_keys($updates[$row['id']]??[])as $k)check(in_array($k,['_thumbnail_id','_product_image_gallery','_tn_photo_cleanup_release','_tn_photo_inpaint_note'],true),'product mutation is media metadata only');}
 foreach($attachments as $id=>$f){check(is_file($f),'original and clean files retained');if($id>4000)check(hash_file('sha256',$f)===$updates[$id]['_tn_original_sha256'],'uploaded clean bytes match manifest');}
 $saved=$updates[$first]['_thumbnail_id'];$updates[$first]['_thumbnail_id']=9999;$failed=false;try{invokeCleanup('rollback');}catch(RuntimeException $e){$failed=true;}check($failed,'rollback protects later human edit');$updates[$first]['_thumbnail_id']=$saved;
 $r=invokeCleanup('rollback');check($r['products_changed']===11&&$updates[$first]['_thumbnail_id']===$before['image']&&count($attachments)===45,'rollback restores original references and retains recovery files');
 $webpSupported=false;$failed=false;try{invokeCleanup('dry');}catch(RuntimeException $e){$failed=true;}check($failed,'unsupported native image editor fails closed');
 echo "PHOTO_CLEANUP_CONTRACTS=PASSED\n";
}finally{unlink($fixtureManifest);foreach($attachments as $id=>$f)if($id>4000)wp_delete_file($f);foreach(['file','image','media']as $n)unlink(ABSPATH.'wp-admin/includes/'.$n.'.php');rmdir(ABSPATH.'wp-admin/includes');rmdir(ABSPATH.'wp-admin');rmdir(ABSPATH);}
