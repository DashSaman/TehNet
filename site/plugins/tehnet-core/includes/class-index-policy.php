<?php
/**
 * Explicit, bounded search visibility. Default OFF. Never changes blog_public.
 * This controls crawl signals, not authentication, WAF, bot training or indexing guarantees.
 */
declare(strict_types=1);
defined('ABSPATH') || exit;
final class TehNet_Core_Index_Policy {
    public const OPTION='tn_index_policy_20261108';
    public const KEY='tehnet-index-allowlist-20261108-v1';
    public const MAX_PATHS=['/','/services/','/services/voice-network-readiness/','/services/remote-support/','/services/mikrotik-tehran/','/services/network-setup-tehran/','/services/network-support-tehran/','/services/network-tehran/','/about/','/contact/','/technical-methodology/','/network-support-contract-guide/','/network-project-proposal-checklist/','/business-server-planning-guide/','/server-backup-restore-acceptance/','/services/server-virtualization-tehran/'];

    public function register():void {
        add_action('template_redirect',[$this,'request_policy'],0);
        add_filter('wp_sitemaps_enabled',[$this,'sitemap_enabled'],20);
        add_filter('wp_sitemaps_add_provider',[$this,'sitemap_provider'],20,2);
        add_filter('wp_sitemaps_post_types',[$this,'sitemap_types'],20);
        add_filter('wp_sitemaps_posts_query_args',[$this,'sitemap_query'],20,2);
        add_filter('robots_txt',[$this,'robots'],20,2);
    }
    /** Invalid, absent, drifted or empty option fails closed under blog_public=0. */
    public static function approved():array {
        $p=get_option(self::OPTION,null);
        if((string)get_option('blog_public')!=='0'||!is_array($p)||array_keys($p)!==['schema','key','approved']||$p['schema']!==1||$p['key']!==self::KEY||!is_array($p['approved'])||!array_is_list($p['approved'])||!$p['approved']||count($p['approved'])>count(self::MAX_PATHS))return [];
        $out=[];$ids=[];
        foreach($p['approved']as$row){
            if(!is_array($row)||array_keys($row)!==['path','id']||!is_string($row['path'])||!in_array($row['path'],self::MAX_PATHS,true)||!is_int($row['id'])||$row['id']<1||isset($out[$row['path']])||isset($ids[$row['id']]))return [];
            $post=get_post($row['id']);
            if(!$post||$post->post_type!=='page'||$post->post_status!=='publish'||$post->post_password!==''||get_permalink($post)!==home_url($row['path']))return [];
            $out[$row['path']]=$row['id'];$ids[$row['id']]=true;
        }
        return $out;
    }
    public function request_policy():void {
        $approved=self::approved();if(!$approved)return;
        $uri=(string)($_SERVER['REQUEST_URI']??'');$path=wp_parse_url($uri,PHP_URL_PATH);
        $clean=in_array($_SERVER['REQUEST_METHOD']??'GET',['GET','HEAD'],true)&&!str_contains($uri,'?')&&empty($_GET)&&is_string($path)&&isset($approved[$path])&&(int)get_queried_object_id()===$approved[$path]&&is_singular('page')&&!is_preview()&&!is_embed()&&!is_feed()&&!is_search()&&!is_404()&&!post_password_required();
        if($clean){
            // Remove exactly the known core Reading-setting producer for this request only.
            // Other plugin/header noindex signals are retained and fail external acceptance.
            remove_filter('wp_robots','wp_robots_noindex');
            return;
        }
        add_filter('wp_robots',static function(array $r):array{unset($r['index'],$r['follow']);$r['noindex']=true;$r['nofollow']=true;return $r;},PHP_INT_MAX);
        if(!headers_sent())header('X-Robots-Tag: noindex, nofollow',true);
    }
    public function sitemap_enabled($enabled):bool{return self::approved()?true:(bool)$enabled;}
    public function sitemap_provider($provider,string $name){return self::approved()&&$name!=='posts'?false:$provider;}
    public function sitemap_types(array $types):array{return self::approved()?array_intersect_key($types,['page'=>true]):$types;}
    public function sitemap_query(array $args,string $type):array {
        $approved=self::approved();if(!$approved)return $args;
        $args['post__in']=$type==='page'?array_values($approved):[0];$args['post_status']=['publish'];$args['has_password']=false;return $args;
    }
    public function robots(string $text,$public):string {
        if(!self::approved())return $text;
        // Preserve the original directives and managed crawler/training groups verbatim.
        $line='Sitemap: '.home_url('/wp-sitemap.xml');
        return str_contains($text,$line)?$text:rtrim($text)."\n".$line."\n";
    }
}
