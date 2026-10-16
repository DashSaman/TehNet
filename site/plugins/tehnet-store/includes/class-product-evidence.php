<?php
defined('ABSPATH')||exit;
/** Staff-reviewed product identity/media. Never changes sale, source or ERP fields. */
final class TehNet_Store_Product_Evidence {
    public function register(): void {
        add_action('woocommerce_product_options_inventory_product_data',[$this,'fields']);
        add_action('woocommerce_process_product_meta',[$this,'save']);
        add_action('woocommerce_single_product_summary',[$this,'viewer'],35);
        add_filter('upload_mimes',static function(array $m):array {if(current_user_can('manage_woocommerce')&&current_user_can('upload_files'))$m['glb']='model/gltf-binary';return $m;});
        add_filter('wp_check_filetype_and_ext',[$this,'filetype'],10,4);
        add_action('wp_enqueue_scripts',function():void {
            if(!function_exists('is_product')||!is_product())return;
            $p=wc_get_product(get_queried_object_id());
            if($p && $this->model($p))wp_enqueue_script('tn-reviewed-glb',$this->asset('reviewed-model.js'),[],'0.1.0',true);
        });
    }
    private function asset(string $name):string {return plugins_url('assets/'.$name,dirname(__DIR__).'/tehnet-store.php');}
    public static function validate_glb(string $file): array {
        if(!is_file($file)||filesize($file)<24||filesize($file)>20*1024*1024)throw new RuntimeException('GLB size invalid (maximum20MiB)');
        $h=fopen($file,'rb');if(!$h)throw new RuntimeException('Unreadable model');
        try{
            $header=fread($h,20);$v=unpack('Vversion/Vlength/Vchunk/Vtype',substr($header,4));
            if(substr($header,0,4)!=='glTF'||$v['version']!==2||$v['length']!==filesize($file)||$v['type']!==0x4E4F534A||$v['chunk']>4*1024*1024||$v['chunk']%4||$v['chunk']+20>filesize($file))throw new RuntimeException('Invalid glTF2 JSON header');
            $json=json_decode(rtrim(fread($h,$v['chunk']),"\0 \r\n\t"),true,64,JSON_THROW_ON_ERROR);
        }finally{fclose($h);}
        if(!is_array($json)||($json['asset']['version']??'')!=='2.0'||empty($json['meshes']))throw new RuntimeException('Model has no glTF2 mesh');
        foreach(array_merge($json['buffers']??[],$json['images']??[])as $item){
            $uri=$item['uri']??'';
            if($uri!==''&&!preg_match('@^data:(image/(png|jpeg|webp)|application/octet-stream);base64,[A-Za-z0-9+/=\r\n]+$@D',$uri))throw new RuntimeException('Model must embed all buffers/textures; external URIs rejected');
        }
        $blocked=['KHR_draco_mesh_compression','KHR_texture_basisu','EXT_meshopt_compression'];
        if(array_intersect(array_merge($json['extensionsUsed']??[],$json['extensionsRequired']??[]),$blocked))throw new RuntimeException('External decoder extensions are not enabled');
        $check=function(array $node)use(&$check,$blocked):void{foreach($node as $k=>$v){if(in_array($k,$blocked,true))throw new RuntimeException('External decoder extension rejected');if(is_array($v))$check($v);}};$check($json);
        return ['sha256'=>hash_file('sha256',$file),'bytes'=>filesize($file),'animations'=>array_values(array_filter(array_column($json['animations']??[],'name'),'is_string')),'nodes'=>array_values(array_filter(array_column($json['nodes']??[],'name'),'is_string'))];
    }
    /** Parts require their own exact-model documentary review; no inferred dimensions. */
    public static function parts(string $raw,string $mpn,array $info):array {
        if(strlen($raw)>48000)throw new RuntimeException('Parts document too large');
        $data=json_decode($raw,true,24,JSON_THROW_ON_ERROR);
        if(!is_array($data)||($data['mpn']??'')!==$mpn||!is_string($data['animation']??null)||!in_array($data['animation'],$info['animations'],true)||empty($data['parts'])||!is_array($data['parts'])||count($data['parts'])>32)throw new RuntimeException('Parts identity/animation mismatch');
        $text=static function($v,int $max):string{if(!is_string($v)||$v===''||strlen($v)>$max||$v!==strip_tags($v))throw new RuntimeException('Invalid part text');return $v;};
        $seen=[];$parts=[];
        foreach($data['parts']as $part){
            $name=$text($part['name']??'',240);$node=$text($part['node']??'',240);
            if(!in_array($node,$info['nodes'],true)||isset($seen[$node]))throw new RuntimeException('Part must identify one unique named model node');$seen[$node]=true;
            $source=$text($part['source']??'',1000);if(!filter_var($source,FILTER_VALIDATE_URL)||parse_url($source,PHP_URL_SCHEME)!=='https')throw new RuntimeException('Part evidence HTTPS required');
            $target=$part['target']??null;if(!is_array($target)||count($target)!==3||array_keys($target)!==[0,1,2])throw new RuntimeException('Exploded-position target required');foreach($target as $v)if(!is_numeric($v)||!is_finite((float)$v)||abs((float)$v)>1000)throw new RuntimeException('Invalid target');
            $measurements=$part['measurements']??[];if(!is_array($measurements)||count($measurements)>8)throw new RuntimeException('Too many measurements');$values=[];
            foreach($measurements as $v){$label=$text($v['label']??'',160);$number=$v['value']??null;$unit=$v['unit']??'';if(!is_numeric($number)||!is_finite((float)$number)||(float)$number<=0||(float)$number>1000000||!in_array($unit,['µm','mm','cm','m','AWG','mm²'],true))throw new RuntimeException('Documented value/unit required');$values[]=['label'=>$label,'value'=>(float)$number,'unit'=>$unit];}
            $parts[]=['name'=>$name,'node'=>$node,'description'=>$text($part['description']??'',2400),'material'=>$text($part['material']??'',240),'source'=>$source,'target'=>array_map('floatval',$target),'measurements'=>$values];
        }
        return ['mpn'=>$mpn,'animation'=>$data['animation'],'parts'=>$parts];
    }
    public function filetype(array $data,string $file,string $filename,$mimes):array {
        if(strtolower(pathinfo($filename,PATHINFO_EXTENSION))!=='glb')return $data;
        if(!current_user_can('manage_woocommerce')||!current_user_can('upload_files'))return ['ext'=>false,'type'=>false,'proper_filename'=>false];
        try{self::validate_glb($file);return ['ext'=>'glb','type'=>'model/gltf-binary','proper_filename'=>false];}
        catch(Throwable $e){return ['ext'=>false,'type'=>false,'proper_filename'=>false];}
    }
    private function attachment(int $id,int $product):string {
        $file=get_attached_file($id);$real=$file?realpath($file):false;$base=realpath(wp_get_upload_dir()['basedir']);
        if(!$real||!$base||!str_starts_with($real,$base.DIRECTORY_SEPARATOR)||(int)get_post_field('post_parent',$id)!==$product)throw new RuntimeException('Media must belong to this product in local uploads');
        return $real;
    }
    public function model($p):array {
        if($p->get_meta('_tn_model_reviewed')!=='yes'||$p->get_meta('_tn_model_rights')!=='yes')return [];
        $mpn=$p->get_meta('_tn_verified_mpn');
        if(!$mpn||$p->get_meta('_tn_model_mpn')!==$mpn||$p->get_meta('_tn_identity_reviewed')!=='yes')return [];
        $id=(int)$p->get_meta('_tn_model_attachment_id');
        try{$file=$this->attachment($id,$p->get_id());if(strtolower(pathinfo($file,PATHINFO_EXTENSION))!=='glb')return [];$info=self::validate_glb($file);}catch(Throwable $e){return [];}
        if(!hash_equals((string)$p->get_meta('_tn_model_sha256'),$info['sha256']))return [];
        $url=wp_get_attachment_url($id);if(!is_string($url)||!str_starts_with($url,home_url('/')))return [];
        $result=['id'=>$id,'url'=>$url,'mpn'=>$mpn,'sha256'=>$info['sha256']];
        if($p->get_meta('_tn_parts_reviewed')==='yes'&&hash_equals((string)$p->get_meta('_tn_parts_model_sha256'),$info['sha256']))try{$result['parts']=self::parts((string)$p->get_meta('_tn_parts_json'),$mpn,$info);}catch(Throwable $e){}
        return $result;
    }
    public function fields():void {
        echo '<div class="options_group"><h4 style="padding:0 12px">شناسایی مدل و رسانهٔ بازبینی‌شده</h4>';
        wp_nonce_field('tn_product_evidence','tn_product_evidence_nonce');
        foreach(['_tn_verified_mpn'=>'شماره فنی تطبیق‌داده‌شده با کالا','_tn_identity_source'=>'نشانی HTTPS مدرک شماره فنی','_tn_model_attachment_id'=>'شناسهٔ رسانه GLB متعلق به همین محصول','_tn_model_mpn'=>'شماره فنی مدل GLB','_tn_model_source'=>'نشانی منبع/مجوز مدل','_tn_spin_ids_input'=>'شناسه‌های فریم۳۶۰ به ترتیب و با ویرگول']as $key=>$label){
            global $thepostid;$value=$key==='_tn_spin_ids_input'?implode(',',(array)get_post_meta($thepostid,'_tn_spin_attachment_ids',true)):get_post_meta($thepostid,$key,true);
            woocommerce_wp_text_input(['id'=>$key,'label'=>$label,'value'=>$value]);
        }
        foreach(['_tn_identity_reviewed'=>'شماره فنی با همان کالای قابل‌تأمین تطبیق داده شد','_tn_model_rights'=>'مجوز استفاده و تعلق فایل GLB بررسی شد','_tn_model_reviewed'=>'هندسه، ابعاد و پورت‌های مدل بررسی شدند','_tn_spin_rights'=>'مجوز و تعلق عکس‌های فریم بررسی شد','_tn_spin_reviewed'=>'ترتیب و پوشش کامل فریم‌های همان کالا بررسی شد']as $key=>$label)woocommerce_wp_checkbox(['id'=>$key,'label'=>$label,'cbvalue'=>'yes']);
        woocommerce_wp_textarea_input(['id'=>'_tn_parts_json','label'=>'سند اجزا و اندازه‌های مستند (JSON)','description'=>'mpn، نام animation بازشدن داخل GLB و parts: نام/node، توضیح، جنس، source HTTPS، target در حالت باز، و measurements با label/value/unit. بدون مدرک ضخامت را وارد نکنید.']);
        woocommerce_wp_checkbox(['id'=>'_tn_parts_reviewed','label'=>'تطبیق تک‌تک اجزا، مواد، واحدها و اندازه‌ها با مدرک همان مدل بازبینی شد','cbvalue'=>'yes']);
        echo '<p class="form-field">فایل باید در رسانهٔ همین محصول بارگذاری شده باشد. بدون تطبیق شماره فنی/مجوز و بررسی فایل، نمایش فعال نمی‌شود. قیمت، موجودی و مجوز فروش از این بخش تغییر نمی‌کنند.</p></div>';
    }
    public function save(int $id):void {
        if(!current_user_can('manage_woocommerce')||!current_user_can('edit_post',$id)||empty($_POST['tn_product_evidence_nonce'])||!is_string($_POST['tn_product_evidence_nonce'])||!wp_verify_nonce(wp_unslash($_POST['tn_product_evidence_nonce']),'tn_product_evidence'))return;
        $input=static fn($k)=>isset($_POST[$k])&&is_string($_POST[$k])?sanitize_text_field(wp_unslash($_POST[$k])):'';
        $https=static fn($u)=>wp_parse_url($u,PHP_URL_SCHEME)==='https'&&wp_parse_url($u,PHP_URL_HOST);
        $mpn=$input('_tn_verified_mpn');$source=esc_url_raw($input('_tn_identity_source'));
        $identity=$input('_tn_identity_reviewed')==='yes'&&preg_match('@^[A-Za-z0-9][A-Za-z0-9 ._/-]{1,79}$@D',$mpn)&&$https($source);
        update_post_meta($id,'_tn_verified_mpn',$identity?$mpn:'');update_post_meta($id,'_tn_identity_source',$https($source)?$source:'');update_post_meta($id,'_tn_identity_reviewed',$identity?'yes':'');
        $model=(int)$input('_tn_model_attachment_id');$modelMpn=$input('_tn_model_mpn');$modelSource=esc_url_raw($input('_tn_model_source'));$rights=$input('_tn_model_rights')==='yes'&&$https($modelSource);$reviewed=false;$sha='';
        try{if($identity&&$rights&&$input('_tn_model_reviewed')==='yes'&&$modelMpn===$mpn){$file=$this->attachment($model,$id);if(strtolower(pathinfo($file,PATHINFO_EXTENSION))!=='glb')throw new RuntimeException('GLB required');$sha=self::validate_glb($file)['sha256'];$reviewed=true;}}catch(Throwable $e){}
        foreach(['_tn_model_attachment_id'=>$model,'_tn_model_mpn'=>$modelMpn,'_tn_model_source'=>$https($modelSource)?$modelSource:'','_tn_model_rights'=>$rights?'yes':'','_tn_model_reviewed'=>$reviewed?'yes':'','_tn_model_sha256'=>$sha]as $k=>$v)update_post_meta($id,$k,$v);
        $partsRaw=isset($_POST['_tn_parts_json'])&&is_string($_POST['_tn_parts_json'])?wp_unslash($_POST['_tn_parts_json']):'';$partsApproved=false;$partsJson='';
        try{if($reviewed&&$input('_tn_parts_reviewed')==='yes'){$partsJson=wp_json_encode(self::parts($partsRaw,$mpn,self::validate_glb($this->attachment($model,$id))));$partsApproved=true;}}catch(Throwable $e){}
        update_post_meta($id,'_tn_parts_json',$partsApproved?$partsJson:substr($partsRaw,0,48000));update_post_meta($id,'_tn_parts_reviewed',$partsApproved?'yes':'');update_post_meta($id,'_tn_parts_model_sha256',$partsApproved?$sha:'');
        $ids=array_values(array_filter(array_map('intval',preg_split('/[\s,،]+/u',substr($input('_tn_spin_ids_input'),0,2000))?:[])));$valid=$identity&&$input('_tn_spin_rights')==='yes'&&$input('_tn_spin_reviewed')==='yes'&&count($ids)>=12&&count($ids)<=144&&count(array_unique($ids))===count($ids);$hashes=[];
        try{if($valid)foreach($ids as $aid){$file=$this->attachment($aid,$id);if(!wp_attachment_is_image($aid))throw new RuntimeException('Image frame required');$hashes[]=hash_file('sha256',$file);}if(count(array_unique($hashes))!==count($hashes))$valid=false;}catch(Throwable $e){$valid=false;}
        update_post_meta($id,'_tn_spin_attachment_ids',$ids);update_post_meta($id,'_tn_spin_rights',$input('_tn_spin_rights')==='yes'?'yes':'');update_post_meta($id,'_tn_spin_reviewed',$valid?'yes':'');
        add_post_meta($id,'_tn_media_review_audit',wp_json_encode(['actor'=>get_current_user_id(),'utc'=>gmdate('c'),'model_reviewed'=>$reviewed,'spin_reviewed'=>$valid,'model_sha256'=>$sha]));
    }
    public function viewer():void {
        global $product;if(!$product)return;$model=$this->model($product);if(!$model)return;
        $poster=wp_get_attachment_image_url($product->get_image_id(),'large');
        echo '<section class="tn-reviewed-model" data-tn-reviewed-model data-model-src="'.esc_url($model['url']).'" data-model-parts="'.esc_attr(wp_json_encode($model['parts']??null)).'" data-model-poster="'.esc_url($poster?:'').'" data-model-module="'.esc_url($this->asset('vendor/model-viewer/model-viewer.min.js')).'"><h3>مدل سه‌بعدی بازبینی‌شده</h3><p>شماره فنی '.esc_html($model['mpn']).'؛ با لمس یا دکمه‌ها زاویه را تغییر دهید.</p><button type="button" data-tn-model-open>باز کردن مدل سه‌بعدی</button><div data-tn-model-stage></div><p role="status" data-tn-model-message aria-live="polite"></p><div class="tn-model-controls" hidden><button type="button" data-orbit="left">چپ</button><button type="button" data-orbit="right">راست</button><button type="button" data-orbit="up">بالا</button><button type="button" data-orbit="down">پایین</button><button type="button" data-orbit="reset">بازنشانی</button></div><div data-tn-parts-panel hidden></div></section>';
    }
}
