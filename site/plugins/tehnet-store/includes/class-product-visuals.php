<?php
defined('ABSPATH') || exit;

/** Native catalogue photos and reviewed photo sequences; generic art is only a fallback. */
final class TehNet_Store_Product_Visuals {
    public function register(): void {
        add_filter('woocommerce_product_get_image',[$this,'image'],30,2);
        add_filter('woocommerce_single_product_image_thumbnail_html',[$this,'gallery'],30,2);
        add_action('woocommerce_product_thumbnails',[$this,'viewer'],25);
        add_action('wp_enqueue_scripts',function():void {
            if(function_exists('is_product')&&is_product()) {
                global $product;
                if(!$product instanceof WC_Product){$product=wc_get_product(get_queried_object_id());}
                if($product instanceof WC_Product && $this->spin_frames($product)) {
                    wp_enqueue_script('tn-photo-spin',$this->asset('photo-spin.js'),[],'0.2.2',true);
                } elseif(!$product instanceof WC_Product || (!$product->get_image_id()&&!$product->get_gallery_image_ids())) {
                    wp_enqueue_script('tn-model-loader',$this->asset('model-loader.js'),[],'0.2.0',true);
                }
            }
        });
    }
    private function asset(string $path): string {return plugins_url('assets/'.$path,dirname(__DIR__).'/tehnet-store.php');}
    private function kind($p): string {
        if(!$p instanceof WC_Product || !$p->get_meta('_tn_source_key')){return '';}
        $id=(int)$p->get_meta('_tn_source_id');
        if(in_array($id,[17989,17982],true)){return 'socket';}
        if(in_array($id,[18002,17991],true)){return 'plug';}
        if(in_array($id,[17941,17935,17929,17927,17920,17888],true)){return 'keystone';}
        return 'cable';
    }
    public function image(string $html,$p): string {
        if(!$p instanceof WC_Product){return $html;}
        if($p->get_image_id()){return $p->get_meta('_tn_photo_release')?$this->watermark($html):$html;}
        $kind=$this->kind($p);if(!$kind){return $html;}
        return '<img src="'.esc_url($this->asset('illustrations/'.$kind.'.svg')).'" width="640" height="420" loading="lazy" decoding="async" alt="'.esc_attr('تصویرسازی شماتیک '.$p->get_name().'؛ عکس واقعی محصول نیست').'" class="tn-product-illustration">';
    }
    public function gallery(string $html,$image_id): string {
        global $product;
        if(!$product instanceof WC_Product){return $html;}
        if($product->get_image_id() || $image_id){
            return $product->get_meta('_tn_photo_release')?str_replace('</a>','<span class="tn-photo-watermark" aria-hidden="true">tehnet.ir</span></a>',$html):$html;
        }
        $kind=$this->kind($product);if(!$kind){return $html;}
        return '<div class="woocommerce-product-gallery__image--placeholder"><a href="'.esc_url($this->asset('illustrations/'.$kind.'.svg')).'">'.$this->image('',$product).'</a><p class="tn-visual-caption">تصویرسازی شماتیک با نشان تهران نتورک؛ عکس واقعی این مدل نیست.</p></div>';
    }
    public function viewer(): void {
        global $product;if(!$product instanceof WC_Product){return;}$kind=$this->kind($product);
        $frames=$this->spin_frames($product);
        if($product->get_image_id()||$product->get_gallery_image_ids()||$frames) {
            if($frames) {
                echo '<section class="tn-photo-spin" data-tn-spin="'.esc_attr(wp_json_encode($frames)).'"><h3>نمای ۳۶۰ محصول</h3><p>توالی تصاویر بازبینی‌شدهٔ همین کالا؛ برای تغییر زاویه بکشید یا از کلیدهای جهت استفاده کنید.</p><button type="button" class="button" data-tn-spin-load>باز کردن نمای ۳۶۰</button><div data-tn-spin-stage hidden><div class="tn-photo-frame"><img tabindex="0" alt="نمای چرخان محصول" width="640" height="640"><span class="tn-photo-watermark" aria-hidden="true">tehnet.ir</span></div><div class="tn-spin-controls"><button type="button" data-tn-spin-prev>زاویه قبل</button><label>زاویه <input type="range" min="0" max="'.esc_attr((string)(count($frames)-1)).'" value="0" step="1" data-tn-spin-range></label><button type="button" data-tn-spin-next>زاویه بعد</button></div><p role="status" data-tn-spin-status></p></div></section>';
            } elseif($product->get_meta('_tn_photo_release')) {
                echo '<p class="tn-photo-note">تصاویر کاتالوگ منبع؛ تطبیق مدل و مشخصات هنگام استعلام انجام می‌شود. نمای ۳۶۰ این مدل هنوز آماده نیست.</p>';
            }
            return;
        }
        if(!$kind){return;}
        echo '<section class="tn-model-viewer" data-tn-model="'.esc_attr($kind).'" data-module="'.esc_url($this->asset('model-viewer.js')).'"><h3>کالا را از زاویه‌های مختلف بررسی کنید</h3><p>نمای شماتیک سه‌بعدیِ گروه کالا؛ ابعاد، پورت‌ها و جزئیات این مدل واقعی تأیید نشده‌اند.</p><button type="button" class="button" data-tn-model-load>باز کردن نمای شماتیک ۳۶۰ درجه</button><div class="tn-model-stage" hidden><canvas tabindex="0" role="img" aria-label="نمای شماتیک چرخان؛ با کشیدن یا کلیدهای جهت بچرخانید"></canvas><p>با انگشت یا ماوس بکشید؛ با کلیدهای جهت بچرخانید.</p><div class="tn-model-controls"><label>چرخش افقی <input type="range" min="-180" max="180" step="1" value="-30" data-tn-yaw></label><label>چرخش عمودی <input type="range" min="-80" max="80" step="1" value="-20" data-tn-pitch></label><button type="button" data-tn-model-reset>بازنشانی نما</button></div><p role="status" data-tn-model-status>نمای تقریبی؛ جایگزین عکس واقعی یا دیتاشیت نیست.</p></div></section>';
    }
    private function watermark(string $html): string {
        return '<span class="tn-product-photo">'.$html.'<span class="tn-photo-watermark" aria-hidden="true">tehnet.ir</span></span>';
    }
    public function spin_frames($p): array {
        if(!$p instanceof WC_Product||$p->get_meta('_tn_spin_reviewed')!=='yes'||$p->get_meta('_tn_spin_rights')!=='yes'||$p->get_meta('_tn_identity_reviewed')!=='yes'||!$p->get_meta('_tn_verified_mpn')){return [];}
        $ids=$p->get_meta('_tn_spin_attachment_ids');
        if(!is_array($ids)||count($ids)<12||count($ids)>144){return [];}
        $ids=array_map('intval',$ids);if(count(array_unique($ids))!==count($ids)){return [];}
        $frames=[];
        foreach($ids as $id) {
            if($id<=0||(int)get_post_field('post_parent',$id)!==$p->get_id()||!wp_attachment_is_image($id)){return [];}
            $url=wp_get_attachment_image_url($id,'large');if(!$url){return [];}$frames[]=$url;
        }
        return $frames;
    }
}
