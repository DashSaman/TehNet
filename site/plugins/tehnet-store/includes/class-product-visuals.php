<?php
defined('ABSPATH') || exit;

/** Owned generic illustrations; never substitutes guessed geometry for an exact product model. */
final class TehNet_Store_Product_Visuals {
    public function register(): void {
        add_filter('woocommerce_product_get_image',[$this,'image'],30,2);
        add_filter('woocommerce_single_product_image_thumbnail_html',[$this,'gallery'],30,2);
        add_action('woocommerce_single_product_summary',[$this,'viewer'],34);
        add_action('wp_enqueue_scripts',function():void {
            if(function_exists('is_product')&&is_product()) {wp_enqueue_script('tn-model-loader',$this->asset('model-loader.js'),[],'0.2.0',true);}
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
        $kind=$this->kind($p);
        if(!$kind || $p->get_image_id()){return $html;}
        return '<img src="'.esc_url($this->asset('illustrations/'.$kind.'.svg')).'" width="640" height="420" loading="lazy" decoding="async" alt="'.esc_attr('تصویرسازی شماتیک '.$p->get_name().'؛ عکس واقعی محصول نیست').'" class="tn-product-illustration">';
    }
    public function gallery(string $html,$image_id): string {
        global $product;
        $kind=$this->kind($product);
        if(!$kind || $product->get_image_id() || $image_id){return $html;}
        return '<div class="woocommerce-product-gallery__image--placeholder"><a href="'.esc_url($this->asset('illustrations/'.$kind.'.svg')).'">'.$this->image('',$product).'</a><p class="tn-visual-caption">تصویرسازی شماتیک با نشان تهران نتورک؛ عکس واقعی این مدل نیست.</p></div>';
    }
    public function viewer(): void {
        global $product;$kind=$this->kind($product);
        if(!$kind){return;}
        echo '<section class="tn-model-viewer" data-tn-model="'.esc_attr($kind).'" data-module="'.esc_url($this->asset('model-viewer.js')).'"><h3>کالا را از زاویه‌های مختلف بررسی کنید</h3><p>نمای شماتیک سه‌بعدیِ گروه کالا؛ ابعاد، پورت‌ها و جزئیات این مدل واقعی تأیید نشده‌اند.</p><button type="button" class="button" data-tn-model-load>باز کردن نمای شماتیک ۳۶۰ درجه</button><div class="tn-model-stage" hidden><canvas tabindex="0" role="img" aria-label="نمای شماتیک چرخان؛ با کشیدن یا کلیدهای جهت بچرخانید"></canvas><p>با انگشت یا ماوس بکشید؛ با کلیدهای جهت بچرخانید.</p><div class="tn-model-controls"><label>چرخش افقی <input type="range" min="-180" max="180" step="1" value="-30" data-tn-yaw></label><label>چرخش عمودی <input type="range" min="-80" max="80" step="1" value="-20" data-tn-pitch></label><button type="button" data-tn-model-reset>بازنشانی نما</button></div><p role="status" data-tn-model-status>نمای تقریبی؛ جایگزین عکس واقعی یا دیتاشیت نیست.</p></div></section>';
    }
}
