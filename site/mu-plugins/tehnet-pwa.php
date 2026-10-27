<?php
/**
 * Plugin Name: TehNet PWA
 * Description: Minimal installable PWA (manifest + service worker) for tehnet.ir. No push notifications; caching is read-only for visitors.
 * Version: 0.1.0
 */
defined('ABSPATH') || exit;

final class TehNet_PWA {
    public static function init(): void {
        add_action('init',[self::class,'route']);
        add_action('wp_head',[self::class,'head'],2);
        add_action('wp_footer',[self::class,'register_sw']);
    }
    public static function route(): void {
        if (!isset($_GET['tn_pwa'])) { return; }
        $mode=sanitize_key(wp_unslash($_GET['tn_pwa']));
        nocache_headers();
        if ($mode==='manifest') {
            header('Content-Type: application/manifest+json; charset=utf-8');
            $manifest=['name'=>'تهران نتورک | TehNet','short_name'=>'TehNet','description'=>'آموزش، خدمات و تجهیزات شبکه','lang'=>'fa','dir'=>'rtl','start_url'=>'/','scope'=>'/','display'=>'standalone','background_color'=>'#ffffff','theme_color'=>'#0e7490'];
            $icon=get_site_icon_url(512);
            if (is_string($icon) && $icon!=='') {
                $manifest['icons']=[['src'=>$icon,'sizes'=>'512x512','type'=>'image/png'],['src'=>$icon,'sizes'=>'192x192','type'=>'image/png']];
            }
            echo wp_json_encode($manifest,JSON_UNESCAPED_UNICODE|JSON_UNESCAPED_SLASHES);
            exit;
        }
        if ($mode==='sw') {
            header('Content-Type: application/javascript; charset=utf-8');
            header('Service-Worker-Allowed: /');
            echo "const C='tehnet-v1';self.addEventListener('install',e=>self.skipWaiting());self.addEventListener('activate',e=>self.clients.claim());";
            echo "self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const u=new URL(e.request.url);if(u.origin!==location.origin||u.pathname.startsWith('/wp-admin')||u.pathname.startsWith('/software/private'))return;";
            echo "if(e.request.mode==='navigate'){e.respondWith(fetch(e.request).then(r=>{const cc=(r.headers.get('cache-control')||'').toLowerCase();const ck=e.request.headers.get('cookie')||'';const cacheable=!cc.includes('no-store')&&!cc.includes('private')&&!cc.includes('no-cache')&&!ck.includes('wordpress_logged_in')&&!ck.includes('wordpress_sec')&&!ck.includes('comment_author');if(cacheable){const cp=r.clone();caches.open(C).then(c=>c.put('/',cp));}return r;}).catch(()=>caches.match('/')));return;}";
            echo "if(u.pathname.startsWith('/wp-content/')||u.pathname.startsWith('/wp-includes/')){e.respondWith(caches.open(C).then(c=>c.match(e.request).then(m=>m||fetch(e.request).then(r=>{const cp=r.clone();c.put(e.request,cp);return r;}))));}});";
            exit;
        }
    }
    public static function head(): void {
        echo '<link rel="manifest" href="'.esc_url(home_url('/?tn_pwa=manifest')).'"><meta name="theme-color" content="#0e7490">';
    }
    public static function register_sw(): void {
        echo "<script>if('serviceWorker' in navigator){navigator.serviceWorker.register('".esc_url(home_url('/?tn_pwa=sw'))."').catch(()=>{})}</script>";
    }
}
TehNet_PWA::init();
