<?php
// Exercises real release script control flow with a filesystem-backed synthetic WP API.
define('ABSPATH',sys_get_temp_dir().'/tn-photo-unit-'.getmypid().'/');define('WP_CLI',true);
$manifest=__DIR__.'/../content/media/saieedshabake-2026-10-16/manifest.json';$digest=hash_file('sha256',$manifest);
$data=json_decode(file_get_contents($manifest),true);$products=[];$options=[];$attachments=[];$counter=1000;$updates=[];
class PhotoFixture {function __construct(public $id,public $row){} function get_id(){return $this->id;}function get_image_id(){global $updates;return (int)($updates[$this->id]['_thumbnail_id']??0);}function get_gallery_image_ids(){global $updates;$v=$updates[$this->id]['_product_image_gallery']??'';return $v===''?[]:array_map('intval',explode(',',$v));}function get_meta($k){global $updates;return $updates[$this->id][$k]??match($k){'_tn_source_key'=>$this->row['source_key'],'_tn_source_id'=>$this->row['source_id'],default=>''};}}
foreach($data['products'] as $i=>$row){$products[$row['sku']]=new PhotoFixture($i+1,$row);}
function current_user_can($c){return true;}function wp_get_environment_type(){return 'local';}function get_current_user_id(){return 1;}
function wc_get_product_id_by_sku($sku){global $products;return $products[$sku]->id??0;}function wc_get_product($id){global $products;foreach($products as $p){if($p->id===$id)return $p;}return false;}
function wp_parse_url($u,$c){return parse_url($u,$c);}function wp_json_encode($v){return json_encode($v);}
function get_option($k,$d=false){global $options;return $options[$k]??$d;}function add_option($k,$v,...$a){global $options;if(isset($options[$k]))return false;$options[$k]=$v;return true;}function update_option($k,$v,...$a){global $options;$options[$k]=$v;}function delete_option($k){global $options;unset($options[$k]);}
function update_post_meta($id,$k,$v){global $updates;$updates[$id][$k]=$v;}function delete_post_meta($id,$k){global $updates;unset($updates[$id][$k]);}
function clean_post_cache($id){}function wc_delete_product_transients($id){}function is_wp_error($x){return false;}
function wp_upload_bits($name,$unused,$b){$p=ABSPATH.$name;file_put_contents($p,$b);return ['file'=>$p,'error'=>false];}
function wp_check_filetype($p){return ['type'=>getimagesize($p)['mime']];}
function wp_insert_attachment($post,$file,$parent,$err){global $counter,$attachments;$attachments[++$counter]=$file;return $counter;}
function wp_generate_attachment_metadata($id,$file){$i=getimagesize($file);return ['width'=>$i[0],'height'=>$i[1]];}
function wp_update_attachment_metadata($id,$m){}function wp_attachment_is_image($id){global $attachments;return isset($attachments[$id]);}
function get_attached_file($id){global $attachments;return $attachments[$id]??'';}function wp_delete_file($f){if(is_file($f))unlink($f);}
function wp_delete_attachment($id,$force){global $attachments;wp_delete_file($attachments[$id]);unset($attachments[$id]);}
mkdir(ABSPATH.'wp-admin/includes',0777,true);foreach(['file','image','media'] as $n)file_put_contents(ABSPATH.'wp-admin/includes/'.$n.'.php','<?php');
function invoke($mode,$sha=null){$path=$GLOBALS['manifest'];$args=[$path,$sha??hash_file('sha256',$path),$mode];ob_start();try{include __DIR__.'/../ops/import-catalog-photos.php';return json_decode(trim(ob_get_contents()),true);}finally{ob_end_clean();}}
function check($ok,$s){if(!$ok)throw new RuntimeException($s);echo "PASS $s\n";}
try{
 $failed=false;try{invoke('dry',str_repeat('0',64));}catch(RuntimeException $e){$failed=true;}check($failed,'wrong manifest SHA rejected');
 $r=invoke('dry');check($r['create']===25&&count($attachments)===0,'dry run leaves all data unchanged');
 $updates[1]['_thumbnail_id']=900;$failed=false;try{invoke('apply');}catch(RuntimeException $e){$failed=true;}check($failed&&count($attachments)===0,'human image blocks entire release before mutation');unset($updates[1]);
 $r=invoke('apply');check($r['products_changed']===25&&count($attachments)===30,'all 25 products and 30 native attachments applied');
 $r=invoke('apply');check($r['products_changed']===0&&$r['skipped']===25&&count($attachments)===30,'repeat skips all products and creates no duplicates');
 $updates[1]['_product_image_gallery']='999';$failed=false;try{invoke('rollback');}catch(RuntimeException $e){$failed=true;}check($failed,'rollback refuses human changes');$updates[1]['_product_image_gallery']='1002';
 $r=invoke('rollback');check($r['products_changed']===25&&$updates[1]['_thumbnail_id']===0&&count($attachments)===30,'rollback restores references and preserves image files for recovery');
 echo "PHOTO_IMPORT_CONTRACTS=7 PASSED\n";
}finally{foreach($attachments as $f)wp_delete_file($f);foreach(['file','image','media']as $n)unlink(ABSPATH.'wp-admin/includes/'.$n.'.php');rmdir(ABSPATH.'wp-admin/includes');rmdir(ABSPATH.'wp-admin');rmdir(ABSPATH);}
