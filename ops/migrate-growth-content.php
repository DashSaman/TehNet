<?php
/** Bounded WP-CLI content migration. Journal and raw snapshots must stay outside Git/web roots. */
final class TehNet_Growth_Content_Migration {
    private const EXISTING_PAGE_SCOPES=[
        'tehnet-editorial-routeros-20261101-v1'=>['id'=>62,'uri'=>'learn/mikrotik/mtcna/routeros-winbox','file'=>'routeros-winbox.html'],
        'tehnet-editorial-routing-20261101-v1'=>['id'=>64,'uri'=>'learn/mikrotik/mtcna/static-routing','file'=>'static-routing.html'],
        'tehnet-service-network-support-20261101-v1'=>['id'=>31,'uri'=>'services/network-support-tehran','file'=>'network-support.html'],
        'tehnet-editorial-ip-dhcp-dns-20261101-v1'=>['id'=>63,'uri'=>'learn/mikrotik/mtcna/ip-dhcp-dns','file'=>'ip-dhcp-dns.html'],
        'tehnet-service-network-setup-20261101-v1'=>['id'=>33,'uri'=>'services/network-setup-tehran','file'=>'network-setup.html'],
    ];
    private array $manifest;
    private string $digest;
    private string $directory;
    private array $touched=[];
    private bool $existingPage=false;
    private string $expectedTitle='';
    private array $pageScope=[];

    public static function authorizes($authorization,array $requested):bool {
        return is_string($authorization)&&($authorization==='tehnet-growth-20261031-v1'||isset(self::EXISTING_PAGE_SCOPES[$authorization]))&&($requested['key']??null)===$authorization;
    }

    public function __construct(string $path,string $digest,string $directory,bool $authorizedProduction=false) {
        if(!defined('WP_CLI')||!WP_CLI||!current_user_can('manage_options')||(string)get_option('blog_public')!=='0')throw new RuntimeException('Authorized closed-index native CLI required');
        $staging=wp_get_environment_type()==='staging'&&home_url('/')==='http://localhost:18085/';
        $production=home_url('/')==='https://tehnet.ir/'&&$authorizedProduction;
        if(!$staging&&!$production)throw new RuntimeException('Target environment is outside the bounded release');
        if($staging&&(!DISABLE_WP_CRON||!WP_HTTP_BLOCK_EXTERNAL||apply_filters('pre_wp_mail',null,[])!==false||!is_wp_error(apply_filters('pre_http_request',false,[],'https://example.invalid'))||apply_filters('woocommerce_available_payment_gateways',['probe'=>new stdClass])!==[]))throw new RuntimeException('Staging isolation required');
        if(!preg_match('/^[a-f0-9]{64}$/D',$digest)||!is_file($path)||is_link($path)||!hash_equals($digest,hash_file('sha256',$path)))throw new RuntimeException('Immutable manifest digest mismatch');
        $real=realpath($directory);$web=realpath(ABSPATH);
        if(!$real||!is_dir($real)||is_link($directory)||($web&&($real===$web||str_starts_with($real,$web.DIRECTORY_SEPARATOR)))||(fileperms($real)&0077)!==0)throw new RuntimeException('Private journal directory outside the web root required');
        $this->manifest=json_decode(file_get_contents($path),true,512,JSON_THROW_ON_ERROR);$this->digest=$digest;$this->directory=$real;
        $m=$this->manifest;
        if(isset(self::EXISTING_PAGE_SCOPES[$m['key']??''])){
            $scope=self::EXISTING_PAGE_SCOPES[$m['key']];$this->pageScope=$scope;
            $target=$m['target']??[];
            if(($m['schema']??null)!==1||($target['id']??null)!==$scope['id']||($target['url']??'')!=='https://tehnet.ir/'.$scope['uri'].'/'||($target['change_fields']??null)!==['post_content']||($m['content_file']??'')!==$scope['file']||!is_string($target['title_observed']??null)||$target['title_observed']==='')throw new RuntimeException('Unapproved existing-page scope');
            $bodyPath=dirname($path).'/'.$scope['file'];
            if(is_link($bodyPath)||!is_file($bodyPath)||!preg_match('/^[a-f0-9]{64}$/D',$m['content_sha256_lf']??'')||!hash_equals($m['content_sha256_lf'],hash_file('sha256',$bodyPath)))throw new RuntimeException('Immutable page body mismatch');
            if(in_array($scope['id'],array_map('intval',[get_option('page_on_front'),get_option('page_for_posts'),get_option('woocommerce_shop_page_id')]),true))throw new RuntimeException('Protected role cannot be an editorial target');
            $this->existingPage=true;$this->expectedTitle=$target['title_observed'];
            $this->manifest=$m=['schema'=>1,'key'=>$m['key'],'pages'=>[],'updates'=>[['id'=>$scope['id'],'expected_content_sha256'=>$target['expected_content_sha256']??'','replace'=>file_get_contents($bodyPath)]]];
        }elseif(($m['schema']??null)!==1||($m['key']??'')!=='tehnet-growth-20261031-v1'||count($m['pages']??[])!==2||count($m['updates']??[])!==2)throw new RuntimeException('Unexpected migration scope');
        $keys=[];$hubs=[];
        foreach($m['updates']as$row){
            if(!is_int($row['id']??null)||$row['id']<1||isset($hubs[$row['id']])||!preg_match('/^[a-f0-9]{64}$/D',$row['expected_content_sha256']??''))throw new RuntimeException('Hub manifest identity invalid');
            $hub=get_post($row['id']);if(!$hub||$hub->post_type!=='page'||$hub->post_status!=='publish')throw new RuntimeException('Hub identity missing');
            $allowed=$this->existingPage?[$this->pageScope['id']=>$this->pageScope['uri']]:[7=>'lab',8=>'services'];
            if(($production||$this->existingPage)&&(!array_key_exists($hub->ID,$allowed)||get_page_uri($hub)!==$allowed[$hub->ID]))throw new RuntimeException('Unapproved managed page path');
            if($this->existingPage&&$hub->post_title!==$this->expectedTitle)throw new RuntimeException('Existing page title drift');
            $this->blocks($row[$this->existingPage?'replace':'append']??'');$hubs[$row['id']]=true;
        }
        foreach($m['pages']as$row){
            $key=$row['key']??'';$slug=$row['slug']??'';
            if(!in_array($key,['voice-service','voice-checklist'],true)||isset($keys[$key])||!is_string($slug)||!preg_match('/^[a-z0-9]+(?:-[a-z0-9]+)*$/D',$slug)||!isset($hubs[$row['parent_id']??0]))throw new RuntimeException('New-page identity invalid');
            if($production&&($slug!==['voice-service'=>'voice-network-readiness','voice-checklist'=>'voice-network-checklist'][$key]||$row['parent_id']!==['voice-service'=>8,'voice-checklist'=>7][$key]))throw new RuntimeException('Unapproved production page path');
            if(!is_string($row['title']??null)||!is_string($row['excerpt']??null)||$row['title']==='')throw new RuntimeException('Page text invalid');
            $this->blocks($row['content']??'');$keys[$key]=true;
        }
    }

    private function blocks(string $content):void {
        if($content===''||serialize_blocks(parse_blocks($content))!==$content)throw new RuntimeException('Block serialization mismatch');
        if($this->existingPage&&wp_kses_post($content)!==$content)throw new RuntimeException('Page sanitization mismatch');
        $existingPage=$this->existingPage;
        $walk=static function(array $blocks)use(&$walk,$existingPage):void {foreach($blocks as$b){
            if($b['blockName']===null){if(trim($b['innerHTML'])!=='')throw new RuntimeException('Unstructured block content');continue;}
            $allowed=['core/paragraph','core/heading','core/list','core/list-item','core/shortcode'];if($existingPage)$allowed[]='core/code';
            if(!in_array($b['blockName'],$allowed,true)||!WP_Block_Type_Registry::get_instance()->is_registered($b['blockName']))throw new RuntimeException('Unapproved block');
            if($b['blockName']==='core/shortcode'&&!in_array(trim($b['innerHTML']),['[tn_editorial_note]','[tn_voice_network_readiness]'],true))throw new RuntimeException('Unapproved shortcode');
            if($existingPage&&$b['blockName']==='core/shortcode'&&trim($b['innerHTML'])!=='[tn_editorial_note]')throw new RuntimeException('Unapproved page shortcode');
            $walk($b['innerBlocks']);
        }};$walk(parse_blocks($content));
    }

    private function query(string $sql):void {global $wpdb;if($wpdb->query($sql)===false)throw new RuntimeException('Database operation failed; private reconciliation required');}
    private function snapshot(int $id):array {
        global $wpdb;$post=$wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->posts} WHERE ID=%d",$id),ARRAY_A);
        if(!$post)throw new RuntimeException('Managed post disappeared');
        $meta=$wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->postmeta} WHERE post_id=%d ORDER BY meta_id",$id),ARRAY_A);
        $revisions=[];foreach($wpdb->get_col($wpdb->prepare("SELECT ID FROM {$wpdb->posts} WHERE post_type='revision' AND post_parent=%d ORDER BY ID",$id))as$revision){$r=(int)$revision;$revisions[$r]=['post'=>$wpdb->get_row($wpdb->prepare("SELECT * FROM {$wpdb->posts} WHERE ID=%d",$r),ARRAY_A),'meta'=>$wpdb->get_results($wpdb->prepare("SELECT * FROM {$wpdb->postmeta} WHERE post_id=%d ORDER BY meta_id",$r),ARRAY_A)];}
        return ['post'=>$post,'meta'=>$meta,'revisions'=>$revisions];
    }
    private function equal($a,$b):bool {return hash('sha256',serialize($a))===hash('sha256',serialize($b));}
    private function lockManaged(array $newIds):void {
        global $wpdb;$ids=array_unique(array_map('intval',array_merge(array_column($this->manifest['updates'],'id'),array_values($newIds))));$set=implode(',',$ids);
        // The advisory lock coordinates migrations; these row/range locks also cover normal editors.
        $this->query("SELECT ID FROM {$wpdb->posts} WHERE ID IN ($set) ORDER BY ID FOR UPDATE");
        $revisions=$wpdb->get_col("SELECT ID FROM {$wpdb->posts} WHERE post_parent IN ($set) AND post_type='revision' ORDER BY ID FOR UPDATE");
        if($wpdb->last_error)throw new RuntimeException('Revision range lock failed');
        $all=array_unique(array_merge($ids,array_map('intval',$revisions)));$metaSet=implode(',',$all);
        $this->query("SELECT meta_id FROM {$wpdb->postmeta} WHERE post_id IN ($metaSet) ORDER BY meta_id FOR UPDATE");
        foreach($all as$id)clean_post_cache($id);
    }
    private function retainedRevisions(array $before,array $after):void {
        foreach($before['revisions']as$id=>$row)if(!isset($after['revisions'][$id])||!$this->equal($row,$after['revisions'][$id]))throw new RuntimeException('Preexisting revisions must remain intact');
    }
    private function pageFields(array $before,array $after,string $body,string $started):void {
        $expected=$before['post'];$expected['post_content']=$body;
        foreach(['post_modified','post_modified_gmt']as$key)$expected[$key]=$after['post'][$key];
        if(!$this->equal($expected,$after['post'])||!$this->equal($before['meta'],$after['meta']))throw new RuntimeException('Unapproved page field or meta change');
        $stamp=strtotime($after['post']['post_modified_gmt'].' UTC');
        if($stamp===false||$stamp<strtotime($started)||$stamp>time()+5||get_date_from_gmt($after['post']['post_modified_gmt'])!==$after['post']['post_modified'])throw new RuntimeException('Actual page modification date required');
        if(count(array_diff_key($after['revisions'],$before['revisions']))>1)throw new RuntimeException('Unexpected page revisions');
    }
    private function protectedState(array $newIds=[]):array {
        global $wpdb;$ids=array_map('intval',array_merge(array_column($this->manifest['updates'],'id'),array_values($newIds)));$set=implode(',',array_unique($ids));
        $revisions=$wpdb->get_col("SELECT ID FROM {$wpdb->posts} WHERE post_type='revision' AND post_parent IN ($set)");$excluded=implode(',',array_unique(array_merge($ids,array_map('intval',$revisions))));
        $tables=$wpdb->get_col($wpdb->prepare('SHOW TABLES LIKE %s',$wpdb->esc_like($wpdb->prefix).'%'));sort($tables);$result=[];
        foreach($tables as$table){
            if(!preg_match('/^[A-Za-z0-9_]+$/D',$table))throw new RuntimeException('Unexpected table name');
            if($table===$wpdb->options||str_starts_with($table,$wpdb->prefix.'actionscheduler_'))continue;
            $columns=$wpdb->get_results("SHOW COLUMNS FROM `$table`",ARRAY_A);$primary=array_column(array_values(array_filter($columns,static fn($c)=>$c['Key']==='PRI')),'Field');$order=$primary?:array_column($columns,'Field');
            foreach($order as$c)if(!preg_match('/^[A-Za-z0-9_]+$/D',$c))throw new RuntimeException('Unexpected column');
            $where=$table===$wpdb->posts?" WHERE ID NOT IN ($excluded)":($table===$wpdb->postmeta?" WHERE post_id NOT IN ($excluded)":'');
            $rows=$wpdb->get_results("SELECT * FROM `$table`$where ORDER BY `".implode('`,`',$order).'`',ARRAY_A);if($wpdb->last_error)throw new RuntimeException('Protected table read failed');
            $result[$table]=hash('sha256',serialize($rows));
        }
        $keys=['blog_public','home','siteurl','active_plugins','stylesheet','template','show_on_front','page_on_front','page_for_posts','woocommerce_shop_page_id','woocommerce_cart_page_id','woocommerce_checkout_page_id','woocommerce_myaccount_page_id','tn_store_settings','woocommerce_cod_settings','woocommerce_bacs_settings','woocommerce_cheque_settings','woocommerce_tn_zarinpal_sandbox_settings'];
        $options=$wpdb->get_results($wpdb->prepare("SELECT option_name,option_value,autoload FROM {$wpdb->options} WHERE option_name IN (".implode(',',array_fill(0,count($keys),'%s')).') ORDER BY option_name',...$keys),ARRAY_A);if($wpdb->last_error)throw new RuntimeException('Protected options read failed');
        $result['selected_options']=hash('sha256',serialize($options));
        $result['commerce']=['erp'=>(new TehNet_Store_ERP())->ready(),'sandbox'=>TehNet_Store_Zarinpal_Sandbox::enabled(),'environment'=>wp_get_environment_type()];
        return $result;
    }
    private function writeJournal(array $journal):void {
        $file=$this->directory.'/journal.json';if(is_link($file))throw new RuntimeException('Journal symlink refused');
        $tmp=$file.'.tmp.'.bin2hex(random_bytes(6));$data=wp_json_encode($journal,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES|JSON_PRETTY_PRINT);$f=fopen($tmp,'x+b');
        if(!$f||!chmod($tmp,0600))throw new RuntimeException('Private journal create failed');
        try {if(fwrite($f,$data)!==strlen($data)||!fflush($f)||(function_exists('fsync')&&!fsync($f)))throw new RuntimeException('Private journal write failed');}finally{fclose($f);}
        if(!rename($tmp,$file))throw new RuntimeException('Private journal replace failed');
    }
    private function verifyAfter(array $journal,string $field='after'):void {
        foreach($journal[$field]['hubs']as$id=>$snapshot)if(!$this->equal($snapshot,$this->snapshot((int)$id)))throw new RuntimeException('Managed hub drift; preserve other edits');
        foreach($journal[$field]['pages']as$id=>$snapshot){if(get_post_meta((int)$id,'_tn_growth_release',true)!==$this->digest||!$this->equal($snapshot,$this->snapshot((int)$id)))throw new RuntimeException('Managed page drift; preserve other edits');}
        if(!$this->equal($journal['protected'],$this->protectedState($journal['page_ids'])))throw new RuntimeException('Protected state drift; reconcile before continuing');
    }
    private function plan():array {
        $hubs=[];$pages=[];
        foreach($this->manifest['updates']as$row){$p=get_post($row['id']);if($this->existingPage&&(!$p||$p->post_type!=='page'||$p->post_status!=='publish'||$p->post_title!==$this->expectedTitle||get_page_uri($p)!==$this->pageScope['uri']))throw new RuntimeException('Existing page identity changed');if(hash('sha256',$p->post_content)!==$row['expected_content_sha256'])throw new RuntimeException('Hub body drift; refuse overwrite');$hubs[$p->ID]=$this->snapshot($p->ID);}
        foreach($this->manifest['pages']as$row){$path=get_page_uri($row['parent_id']).'/'.$row['slug'];if(get_page_by_path($path,OBJECT,'page'))throw new RuntimeException('New path already exists; do not adopt');$pages[$row['key']]=$path;}
        return ['hubs'=>$hubs,'paths'=>$pages];
    }
    private function restoreHub(int $id,array $before,array $after):void {
        global $wpdb;
        foreach($before['revisions']as$rid=>$row)if(!isset($after['revisions'][$rid])||!$this->equal($row,$after['revisions'][$rid]))throw new RuntimeException('Existing revision drift');
        foreach(array_diff_key($after['revisions'],$before['revisions'])as$rid=>$row){$wpdb->delete($wpdb->postmeta,['post_id'=>$rid]);if($wpdb->delete($wpdb->posts,['ID'=>$rid])!==1)throw new RuntimeException('Owned revision cleanup failed');clean_post_cache((int)$rid);}
        if($wpdb->update($wpdb->posts,$before['post'],['ID'=>$id])===false)throw new RuntimeException('Hub restoration failed');
        if(!$this->equal($before['meta'],$after['meta'])){if($wpdb->delete($wpdb->postmeta,['post_id'=>$id])===false)throw new RuntimeException('Hub meta restore failed');foreach($before['meta']as$row)if($wpdb->insert($wpdb->postmeta,$row)!==1)throw new RuntimeException('Hub meta insert failed');}
        clean_post_cache($id);
    }

    public function run(string $mode):array {
        global $wpdb;if(!in_array($mode,['check','apply','rollback'],true))throw new RuntimeException('Unknown migration operation');
        $lockPath=$this->directory.'/.lock';if(is_link($lockPath))throw new RuntimeException('Lock symlink refused');$lock=fopen($lockPath,'c+b');if(!$lock||!chmod($lockPath,0600)||!flock($lock,LOCK_EX|LOCK_NB))throw new RuntimeException('Another migration owns this journal');
        $previousErrors=$wpdb->suppress_errors(true);$dbLock='tn-growth-'.substr(hash('sha256',$wpdb->dbname),0,24);$held=false;$transaction=false;$committed=false;$journal=null;
        $capture=function($id,$post):void {if($post->post_type==='page')$this->touched[]=(int)$id;};
        $blockMail=static fn()=>false;$blockHttp=static fn()=>new WP_Error('tn_growth_isolated','Outbound HTTP disabled for this CLI migration');
        $keepRevisions=function($limit,$post){return in_array((int)$post->ID,array_column($this->manifest['updates'],'id'),true)||get_post_meta($post->ID,'_tn_growth_release',true)===$this->digest?-1:$limit;};
        add_filter('pre_wp_mail',$blockMail,PHP_INT_MAX);add_filter('pre_http_request',$blockHttp,PHP_INT_MAX);
        add_filter('wp_revisions_to_keep',$keepRevisions,PHP_INT_MAX,2);
        try {
            $held=(string)$wpdb->get_var($wpdb->prepare('SELECT GET_LOCK(%s,0)',$dbLock))==='1';if(!$held)throw new RuntimeException('Another native growth operation owns the database lock');
            if((string)$wpdb->get_var('SELECT @@in_transaction')!=='0'||(string)$wpdb->get_var('SELECT @@autocommit')!=='1')throw new RuntimeException('Migration must own a fresh autocommit session');
            $engines=$wpdb->get_results("SHOW TABLE STATUS WHERE Name IN ('{$wpdb->posts}','{$wpdb->postmeta}','{$wpdb->options}')",ARRAY_A);if(count($engines)!==3||array_filter($engines,static fn($r)=>strtoupper($r['Engine'])!=='INNODB'))throw new RuntimeException('Transactional WordPress tables required');
            $file=$this->directory.'/journal.json';if(is_link($file))throw new RuntimeException('Journal symlink refused');$journal=is_file($file)?json_decode(file_get_contents($file),true,512,JSON_THROW_ON_ERROR):null;
            if($journal&&($journal['digest']!==$this->digest||$journal['home']!==home_url('/')||$journal['environment']!==wp_get_environment_type()))throw new RuntimeException('Journal target/digest mismatch');
            if($journal&&$journal['status']==='ROLLED_BACK'){$this->verifyAfter($journal,'rolled');if($mode==='rollback')return ['status'=>'ROLLED_BACK','hubs_restored'=>0,'pages_drafted'=>0,'protected_state_unchanged'=>true];throw new RuntimeException('Rolled-back release requires a reviewed new attempt');}
            if($journal&&$journal['status']!=='APPLIED')throw new RuntimeException('Incomplete or failed journal requires explicit reconciliation');
            if($journal){$this->verifyAfter($journal);if($mode!=='rollback')return ['status'=>'APPLIED','pages_pending'=>0,'hubs_pending'=>0,'pages_created'=>0,'hubs_updated'=>0,'page_ids'=>$journal['page_ids'],'protected_state_unchanged'=>true];}
            elseif($mode==='rollback')throw new RuntimeException('No matching applied journal');
            if(!$journal){$plan=$this->plan();if($mode==='check')return ['status'=>'READY','pages_pending'=>count($this->manifest['pages']),'hubs_pending'=>count($this->manifest['updates']),'protected_digest'=>hash('sha256',serialize($this->protectedState()))];$journal=['schema'=>1,'digest'=>$this->digest,'home'=>home_url('/'),'environment'=>wp_get_environment_type(),'status'=>'PREPARED','before'=>$plan,'protected'=>$this->protectedState(),'page_ids'=>[],'created_utc'=>gmdate('c')];$this->writeJournal($journal);}
            $this->query('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ');
            $this->query('START TRANSACTION');$transaction=true;
            $this->lockManaged($journal['page_ids']);
            if($mode==='rollback')$this->verifyAfter($journal);
            add_action('save_post_page',$capture,1,2);
            if($mode==='apply'){
                $plan=$this->plan();if(!$this->equal($plan,$journal['before'])||!$this->equal($journal['protected'],$this->protectedState()))throw new RuntimeException('State changed before transaction');
                foreach($this->manifest['pages']as$row){$id=wp_insert_post(wp_slash(['post_type'=>'page','post_status'=>'publish','post_parent'=>$row['parent_id'],'post_name'=>$row['slug'],'post_title'=>$row['title'],'post_excerpt'=>$row['excerpt'],'post_content'=>$row['content'],'meta_input'=>['_tn_growth_release'=>$this->digest,'_tn_growth_key'=>$row['key']]]),true);if(is_wp_error($id))throw new RuntimeException('Page insert failed');$journal['page_ids'][$row['key']]=$id;$p=get_post($id);if($p->post_content!==$row['content']||$p->post_title!==$row['title']||$p->post_excerpt!==$row['excerpt']||$p->post_name!==$row['slug']||(int)$p->post_parent!==$row['parent_id'])throw new RuntimeException('Saved page mismatch');}
                foreach($this->manifest['updates']as$row){$body=$this->existingPage?$row['replace']:$journal['before']['hubs'][$row['id']]['post']['post_content']."\n\n".$row['append'];$id=wp_update_post(wp_slash(['ID'=>$row['id'],'post_content'=>$body]),true);if(is_wp_error($id)||get_post($id)->post_content!==$body)throw new RuntimeException('Managed body update failed');}
                $journal['after']=['hubs'=>[],'pages'=>[]];foreach($this->manifest['updates']as$row){$after=$this->snapshot($row['id']);$this->retainedRevisions($journal['before']['hubs'][$row['id']],$after);if($this->existingPage)$this->pageFields($journal['before']['hubs'][$row['id']],$after,$row['replace'],$journal['created_utc']);$journal['after']['hubs'][$row['id']]=$after;}foreach($journal['page_ids']as$id)$journal['after']['pages'][$id]=$this->snapshot($id);
                $this->verifyAfter($journal);
            }else{
                foreach($journal['before']['hubs']as$id=>$before)$this->restoreHub((int)$id,$before,$journal['after']['hubs'][$id]);
                foreach($journal['page_ids']as$id){$r=wp_update_post(['ID'=>$id,'post_status'=>'draft'],true);if(is_wp_error($r)||get_post_status($id)!=='draft')throw new RuntimeException('Owned page unpublish failed');}
                $journal['rolled']=['hubs'=>[],'pages'=>[]];foreach($this->manifest['updates']as$row){$current=$this->snapshot($row['id']);if(!$this->equal($current,$journal['before']['hubs'][$row['id']]))throw new RuntimeException('Hub restoration mismatch');$journal['rolled']['hubs'][$row['id']]=$current;}foreach($journal['page_ids']as$id)$journal['rolled']['pages'][$id]=$this->snapshot($id);
                $this->verifyAfter($journal,'rolled');
            }
            $journal['status']='COMMIT_READY';$this->writeJournal($journal);$this->query('COMMIT');$transaction=false;$committed=true;
            $journal['status']=$mode==='apply'?'APPLIED':'ROLLED_BACK';$journal['completed_utc']=gmdate('c');$this->writeJournal($journal);
            return $mode==='apply'?['status'=>'APPLIED','pages_created'=>count($this->manifest['pages']),'hubs_updated'=>count($this->manifest['updates']),'page_ids'=>$journal['page_ids'],'protected_digest'=>hash('sha256',serialize($journal['protected'])),'protected_state_unchanged'=>true]:['status'=>'ROLLED_BACK','hubs_restored'=>count($this->manifest['updates']),'pages_drafted'=>count($this->manifest['pages']),'protected_state_unchanged'=>true];
        } catch(Throwable $e) {
            if($transaction){$rolled=$wpdb->query('ROLLBACK')!==false;$transaction=false;if($journal){$journal['status']=$rolled?'FAILED':'NEEDS_RECONCILIATION';$journal['failure_utc']=gmdate('c');$this->writeJournal($journal);}}
            elseif($committed&&$journal){$journal['status']='NEEDS_RECONCILIATION';$this->writeJournal($journal);}
            throw $e;
        } finally {
            remove_action('save_post_page',$capture,1);foreach(array_unique($this->touched)as$id)clean_post_cache($id);
            remove_filter('pre_wp_mail',$blockMail,PHP_INT_MAX);remove_filter('pre_http_request',$blockHttp,PHP_INT_MAX);
            remove_filter('wp_revisions_to_keep',$keepRevisions,PHP_INT_MAX);
            if($held)$wpdb->get_var($wpdb->prepare('SELECT RELEASE_LOCK(%s)',$dbLock));$wpdb->suppress_errors($previousErrors);flock($lock,LOCK_UN);fclose($lock);
        }
    }
}

if(!defined('TN_GROWTH_LIBRARY_ONLY')){
    $authorization=getenv('TN_GROWTH_AUTHORIZED_RELEASE');$manifestPath=(string)getenv('TN_GROWTH_MANIFEST');
    $requested=is_file($manifestPath)?json_decode(file_get_contents($manifestPath),true,512,JSON_THROW_ON_ERROR):[];
    $authorized=TehNet_Growth_Content_Migration::authorizes($authorization,$requested);
    $migration=new TehNet_Growth_Content_Migration($manifestPath,(string)getenv('TN_GROWTH_DIGEST'),(string)getenv('TN_GROWTH_JOURNAL_DIR'),$authorized);
    echo wp_json_encode($migration->run(getenv('TN_GROWTH_MODE')?:'check'));
}
