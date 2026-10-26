<?php
defined('ABSPATH') || exit;

final class TehNet_Store_Storefront {
    private const UNITS=['piece'=>'عدد','meter'=>'متر','reel'=>'قرقره','pack'=>'بسته'];
    private const SPECS=['shield'=>['شیلد',['UTP','FTP','SFTP']],'jacket'=>['روکش',['PVC','LSZH']],'environment'=>['محیط نصب',['Indoor','Outdoor']]];
    public function register(): void {
        add_action('wp_enqueue_scripts',[$this,'assets']);
        add_filter('body_class',[$this,'body_classes']);
        add_action('woocommerce_before_shop_loop',[$this,'categories'],2);
        add_action('woocommerce_no_products_found',[$this,'categories'],2);
        add_action('woocommerce_before_shop_loop_item_title',static function():void{echo '<div class="tn-card-media">';},5);
        add_action('woocommerce_before_shop_loop_item_title',static function():void{echo '</div>';},20);
        add_action('woocommerce_shop_loop_item_title',[$this,'card_badge'],4);
        add_action('woocommerce_shop_loop_item_title',[$this,'card_identity'],5);
        add_action('woocommerce_shop_loop_item_title',[$this,'card_specs'],15);
        add_action('woocommerce_before_shop_loop',[$this,'filters'],5);
        add_action('woocommerce_no_products_found',[$this,'filters'],5);
        add_filter('request',[$this,'normalize_request']);
        add_filter('posts_search',[$this,'sku_search'],20,2);
        add_filter('woocommerce_redirect_single_search_result',fn($value)=>$this->preview_allowed()?false:$value);
        add_action('woocommerce_after_shop_loop_item',[$this,'tools'],20);
        add_action('woocommerce_single_product_summary',[$this,'unit'],11);
        add_action('woocommerce_after_single_product_summary',[$this,'related_products'],19);
        add_action('woocommerce_single_product_summary',[$this,'editorial'],40);
        add_action('woocommerce_single_product_summary',[$this,'tools'],32);
        add_action('woocommerce_product_query',[$this,'query']);
        add_action('woocommerce_before_shop_loop',[$this,'preview_notice'],1);
        add_filter('woocommerce_loop_product_link',[$this,'preview_link'],10,2);
        add_action('template_redirect',[$this,'preview_headers']);
        add_filter('woocommerce_get_stock_html',[$this,'stock_html'],30,2);
        add_action('wp_footer',[$this,'dialog']);
        add_filter('woocommerce_is_purchasable',[$this,'purchasable'],30,2);
        add_filter('woocommerce_get_price_html',[$this,'price'],30,2);
        add_filter('woocommerce_loop_add_to_cart_link',[$this,'cta'],30,3);
        add_action('woocommerce_check_cart_items',[$this,'validate_cart']);
        add_action('woocommerce_product_options_inventory_product_data',[$this,'fields']);
        add_action('woocommerce_process_product_meta',[$this,'save_fields']);
        remove_filter('woocommerce_stock_amount','intval');
        add_filter('woocommerce_stock_amount','floatval');
        add_filter('woocommerce_quantity_input_args',[$this,'quantity_args'],10,2);
        add_filter('woocommerce_add_to_cart_validation',[$this,'validate_quantity'],10,3);
        remove_action('woocommerce_sidebar','woocommerce_get_sidebar',10);
        add_filter('woocommerce_placeholder_img_src',static fn()=>plugins_url('assets/product-placeholder.svg',dirname(__DIR__).'/tehnet-store.php'));
        add_action('after_setup_theme',static function():void {
            add_theme_support('wc-product-gallery-zoom');
            add_theme_support('wc-product-gallery-lightbox');
            add_theme_support('wc-product-gallery-slider');
        });
    }
    private function physical($product): bool {
        return $product instanceof WC_Product && !$product->is_virtual() && !$product->is_downloadable();
    }
    public static function normalize_search(string $term): string {
        return trim(strtr($term,['ي'=>'ی','ك'=>'ک','۰'=>'0','۱'=>'1','۲'=>'2','۳'=>'3','۴'=>'4','۵'=>'5','۶'=>'6','۷'=>'7','۸'=>'8','۹'=>'9','٠'=>'0','١'=>'1','٢'=>'2','٣'=>'3','٤'=>'4','٥'=>'5','٦'=>'6','٧'=>'7','٨'=>'8','٩'=>'9']));
    }
    public function normalize_request(array $vars): array {
        if(!is_admin()&&($vars['post_type']??null)==='product'&&is_string($vars['s']??null)){$vars['s']=self::normalize_search($vars['s']);}
        return $vars;
    }
    public function sku_search(string $search,$query): string {
        if(is_admin()||$query->get('post_type')!=='product'||!$query->is_search()||!is_string($query->get('s'))){return $search;}
        $id=wc_get_product_id_by_sku(self::normalize_search($query->get('s')));
        if(!$id){return $search;}
        // Only replaces the text-search clause. Native post status, capability, taxonomy and stock constraints remain.
        global $wpdb;
        return $wpdb->prepare(" AND {$wpdb->posts}.ID = %d ",$id).(!is_user_logged_in()?" AND {$wpdb->posts}.post_password = '' ":'');
    }
    private function eligible(WC_Product $product): bool {
        // Until a working ERP reservation endpoint is connected, physical checkout stays closed.
        $ready=class_exists('TehNet_Store_ERP') && (new TehNet_Store_ERP())->ready();
        return get_woocommerce_currency()==='IRR' && TehNet_Store_Policy::can_sell([
            'approved'=>$product->get_meta('_tn_sale_approved'), 'price'=>$product->get_price(),
            'stock'=>(string)$product->get_stock_quantity(), 'unit'=>$product->get_meta('_tn_sale_unit'),
            'minimum'=>$product->get_meta('_tn_min_quantity'),
            'erp_fresh_until'=>$product->get_meta('_tn_erp_fresh_until'),'erp_ready'=>$ready,
        ],time());
    }
    public function purchasable(bool $value,$product): bool {
        return $this->physical($product) ? $this->eligible($product) : $value;
    }
    public function price(string $value,$product): string {
        if (!$this->physical($product) || !$this->eligible($product)) { return $value; }
        return wc_price($product->get_price()).' <small>برای هر '.esc_html(self::UNITS[$product->get_meta('_tn_sale_unit')]).'</small>';
    }
    public function cta(string $value,$product,array $args): string {
        if (!$this->physical($product) || !$this->eligible($product)) { return $value; }
        return sprintf('<a class="button" href="%s">%s</a>',esc_url($product->get_permalink()),esc_html__('انتخاب مقدار و خرید','tehnet-store'));
    }
    public function validate_cart(): void {
        if (!WC()->cart) { return; }
        foreach (WC()->cart->get_cart() as $line) {
            if ($this->physical($line['data']) && !$this->eligible($line['data'])) {
                wc_add_notice('قیمت یا موجودی تأییدشده این کالا در دسترس نیست. پیش از خرید استعلام بگیرید.','error');
                return;
            }
        }
    }
    public function quantity_args(array $args,$product): array {
        $args['step']='1';
        if ($product instanceof WC_Product && $product->get_meta('_tn_sale_unit')==='meter') {
            $args['step']='0.001';$args['min_value']=$product->get_meta('_tn_min_quantity')?:'0.001';
        }
        return $args;
    }
    public function validate_quantity(bool $valid,int $id,$quantity): bool {
        $product=wc_get_product($id);
        try {
            $milli=TehNet_Store_Policy::quantity_milli((string)$quantity);
            if (!$product || ($product->get_meta('_tn_sale_unit')!=='meter' && $milli%1000!==0)) { throw new InvalidArgumentException('Whole units required'); }
            if ($this->physical($product) && $milli<TehNet_Store_Policy::quantity_milli((string)$product->get_meta('_tn_min_quantity'))) { throw new InvalidArgumentException('Below minimum'); }
        } catch (InvalidArgumentException $e) { wc_add_notice('مقدار سفارش با واحد فروش یا حداقل مقدار مجاز سازگار نیست.','error');return false; }
        return $valid;
    }
    public function assets(): void {
        if (!function_exists('is_woocommerce') || !(is_woocommerce() || is_cart() || is_checkout() || is_account_page())) { return; }
        wp_enqueue_style('tn-store',plugins_url('assets/store.css',dirname(__DIR__).'/tehnet-store.php'),[], '0.5.3');
        wp_enqueue_script('tn-store',plugins_url('assets/store.js',dirname(__DIR__).'/tehnet-store.php'),[], '0.5.1',true);
        if(is_shop()||is_product_taxonomy()||is_product())wp_enqueue_style('tn-shop-experience',plugins_url('assets/store-experience.css',dirname(__DIR__).'/tehnet-store.php'),['tn-store','tehnet-visual-refresh'],'0.4.0');
    }
    public function body_classes(array $classes):array {
        if(function_exists('is_shop')&&(is_shop()||is_product_taxonomy()||is_product()))$classes[]='tn-shop';return $classes;
    }
    public function categories():void {
        $terms=get_terms(['taxonomy'=>'product_cat','hide_empty'=>true,'exclude'=>[(int)get_option('default_product_cat')],'orderby'=>'count','order'=>'DESC']);
        if(is_wp_error($terms)||!$terms)return;
        $children=[];foreach($terms as $term)$children[$term->parent][]=$term;$selected=[];
        // Collapse single-child wrappers. Keep overlapping brand/spec facets
        // together; expand distinct product families, without hardcoded IDs.
        $walk=function($term,int $depth=0)use(&$walk,&$selected,$children):void{
            $next=$children[$term->term_id]??[];
            if($depth<10&&$next&&count($next)<=6&&(count($next)===1||max(array_map(static fn($t)=>(int)$t->count,$next))<(int)$term->count))foreach($next as $child)$walk($child,$depth+1);
            else $selected[]=$term;
        };
        foreach($children[0]??$terms as $term)$walk($term);$terms=array_slice($selected,0,6);
        echo '<nav class="tn-shop-categories" aria-label="دسته‌های محصولات">';
        foreach($terms as $term){
            $url=get_term_link($term);if(is_wp_error($url))continue;
            $label=$term->slug.' '.$term->name;
            $path=match(true){str_contains($label,'cable')||str_contains($label,'کابل')=>'M4 5h6v6H4zM14 13h6v6h-6zM7 11v6h7M6 3v2m2-2v2m8 14v2m2-2v2',str_contains($label,'keystone')||str_contains($label,'کیستون')=>'M5 6h14v13H5zM8 6V3h8v3M8 10v5m3-5v5m3-5v5m3-5v5',str_contains($label,'socket')||str_contains($label,'پریز')=>'M4 4h16v16H4zM9 10v3m6-3v3M11 16h2',str_contains($label,'plug')||str_contains($label,'سوکت')=>'M7 8h10v9H7zM9 8V3m6 5V3m-3 14v4',default=>'m12 3 9 5v9l-9 5-9-5V8l9-5Zm0 10 9-5M3 8l9 5v9'};
            echo '<a class="tn-shop-category" href="'.esc_url($url).'"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="'.esc_attr($path).'"/></svg><span>'.esc_html($term->name).'</span><span class="tn-category-arrow" aria-hidden="true">←</span></a>';
        }
        echo '</nav><div class="tn-shop-steps" aria-label="مراحل سفارش"><span><b>۱</b> بررسی مدل و مشخصات</span><span><b>۲</b> درخواست پیش‌فاکتور</span><span><b>۳</b> تأیید شرایط تأمین</span></div>';
    }
    public function card_identity():void {
        global $product;if(!$product instanceof WC_Product)return;
        $terms=get_the_terms($product->get_id(),'product_cat');
        echo '<div class="tn-card-identity">';if(is_array($terms)&&$terms){$parents=array_column($terms,'parent');$chosen=$terms[0];foreach($terms as $term)if(!in_array($term->term_id,$parents,true)){$chosen=$term;break;}echo '<span>'.esc_html($chosen->name).'</span>';}
        if($product->get_sku())echo '<span class="tn-card-sku" dir="ltr">'.esc_html($product->get_sku()).'</span>';echo '</div>';
    }
    public function card_specs():void {
        global $product;if(!$product instanceof WC_Product)return;$chips=[];
        foreach(self::SPECS as $key=>$definition){$v=$product->get_meta('_tn_verified_'.$key);if(in_array($v,$definition[1],true))$chips[]=$definition[0].': '.$v;}
        if($chips)echo '<p class="tn-card-specs">'.esc_html(implode(' · ',$chips)).'</p>';
    }
    public function filters(): void {
        $unit=isset($_GET['tn_unit']) && is_string($_GET['tn_unit']) ? sanitize_key(wp_unslash($_GET['tn_unit'])) : '';
        echo '<form class="tn-store-filters" method="get" action="'.esc_url(wc_get_page_permalink('shop')).'">';
        echo '<input type="hidden" name="post_type" value="product"><label class="tn-filter-search"><span>جست‌وجوی کالا</span><input name="s" type="search" value="'.esc_attr(get_search_query()).'" placeholder="جست‌وجو با نام، مدل یا کد کالا"></label>';
        if ($this->preview_allowed()) { echo '<input type="hidden" name="tn_preview" value="1">'; }
        $category=isset($_GET['product_cat'])&&is_string($_GET['product_cat'])?sanitize_title(wp_unslash($_GET['product_cat'])):'';
        if($category===''&&function_exists('is_product_category')&&is_product_category())$category=(string)(get_queried_object()->slug??'');
        echo '<label class="tn-filter-category"><span>دسته کالا</span>';wp_dropdown_categories(['taxonomy'=>'product_cat','name'=>'product_cat','value_field'=>'slug','selected'=>$category,'show_option_all'=>'همه دسته‌ها','hide_empty'=>true,'hierarchical'=>true]);echo '</label>';
        $advanced=$unit!=='';foreach(array_keys(self::SPECS)as $key)if(isset($_GET['tn_'.$key])&&is_string($_GET['tn_'.$key])&&$_GET['tn_'.$key]!=='')$advanced=true;
        $orderby=isset($_GET['orderby'])&&is_string($_GET['orderby'])?sanitize_key(wp_unslash($_GET['orderby'])):'';
        echo '<label class="tn-filter-sort"><span>مرتب‌سازی</span><select name="orderby">';
        foreach ([''=>'پیش‌فرض','date'=>'جدیدترین','tn_title'=>'الفبایی نام','tn_sku'=>'کد کالا','price'=>'ارزان‌ترین (ریال)','price-desc'=>'گران‌ترین (ریال)'] as $value=>$label) {
            echo '<option value="'.esc_attr($value).'" '.selected($orderby,$value,false).'>'.esc_html($label).'</option>';
        }
        echo '</select></label>';
        $pmin=isset($_GET['tn_pmin'])&&is_numeric($_GET['tn_pmin'])?sanitize_text_field(wp_unslash($_GET['tn_pmin'])):'';
        $pmax=isset($_GET['tn_pmax'])&&is_numeric($_GET['tn_pmax'])?sanitize_text_field(wp_unslash($_GET['tn_pmax'])):'';
        $instock=isset($_GET['tn_stock'])&&$_GET['tn_stock']==='1';
        echo '<button class="button tn-filter-submit" type="submit">جست‌وجو و فیلتر</button><details class="tn-filter-advanced"'.($advanced?' open':'').'><summary>فیلترهای فنی و واحد فروش</summary><div class="tn-filter-options"><label>واحد فروش <select name="tn_unit"><option value="">همه واحدها</option>';
        foreach(self::UNITS as $key=>$label) { printf('<option value="%s" %s>%s</option>',esc_attr($key),selected($unit,$key,false),esc_html($label)); }
        echo '</select></label>';
        foreach (self::SPECS as $key=>$definition) {
            $current=isset($_GET['tn_'.$key]) && is_string($_GET['tn_'.$key])?sanitize_text_field(wp_unslash($_GET['tn_'.$key])):'';
            echo '<label>'.esc_html($definition[0]).' <select name="tn_'.esc_attr($key).'"><option value="">همه مشخصات تأییدشده</option>';
            foreach ($definition[1] as $value) { echo '<option value="'.esc_attr($value).'" '.selected($current,$value,false).'>'.esc_html($value).'</option>'; }
            echo '</select></label>';
        }
        echo '<label class="tn-filter-price">قیمت از (ریال) <input type="number" min="0" step="1000" name="tn_pmin" value="'.esc_attr($pmin).'"></label>';
        echo '<label class="tn-filter-price">تا (ریال) <input type="number" min="0" step="1000" name="tn_pmax" value="'.esc_attr($pmax).'"></label>';
        echo '<label class="tn-filter-stock"><input type="checkbox" name="tn_stock" value="1" '.checked($instock,true,false).'> فقط کالاهای موجود</label>';
        $reset=$this->preview_allowed()?add_query_arg('tn_preview','1',wc_get_page_permalink('shop')):wc_get_page_permalink('shop');
        echo '</div></details><a class="tn-filter-reset" href="'.esc_url($reset).'">پاک کردن فیلترها</a></form>';
        echo '<div class="tn-store-toolbar"><span>قیمت‌ها با واحد ریال نمایش داده می‌شوند؛ موجودی و ارسال پیش از تأیید سفارش بررسی می‌شود.</span><button type="button" data-tn-open="compare">مقایسه <span data-tn-count="compare">۰</span></button><button type="button" data-tn-open="wishlist">علاقه‌مندی <span data-tn-count="wishlist">۰</span></button></div>';
    }
    public function query($query): void {
        if ($this->preview_allowed()) { $query->set('post_status',['publish','draft']); }
        $orderby=isset($_GET['orderby'])&&is_string($_GET['orderby'])?sanitize_key(wp_unslash($_GET['orderby'])):'';
        if ($orderby==='tn_title') { $query->set('orderby','title'); $query->set('order','ASC'); }
        elseif ($orderby==='tn_sku') { $query->set('meta_key','_sku'); $query->set('orderby','meta_value'); $query->set('order','ASC'); }
        $meta=$query->get('meta_query');$meta=is_array($meta)?$meta:[];
        if (isset($_GET['tn_stock']) && $_GET['tn_stock']==='1') { $meta[]=['key'=>'_stock_status','value'=>'instock']; }
        $pmin=isset($_GET['tn_pmin'])&&is_numeric($_GET['tn_pmin'])?(float)wp_unslash($_GET['tn_pmin']):null;
        $pmax=isset($_GET['tn_pmax'])&&is_numeric($_GET['tn_pmax'])?(float)wp_unslash($_GET['tn_pmax']):null;
        if ($pmin!==null || $pmax!==null) {
            $meta[]=['key'=>'_price','compare'=>'BETWEEN','type'=>'NUMERIC','value'=>[$pmin??0,$pmax??PHP_FLOAT_MAX]];
        }
        if (count($meta)>($query->get('meta_query')?count($query->get('meta_query')):0)) { $query->set('meta_query',$meta); }
        $unit=isset($_GET['tn_unit']) && is_string($_GET['tn_unit']) ? sanitize_key(wp_unslash($_GET['tn_unit'])) : '';
        if (isset(self::UNITS[$unit])) {
            $meta=$query->get('meta_query');$meta=is_array($meta)?$meta:[];
            $meta[]=['key'=>'_tn_sale_unit','value'=>$unit];$query->set('meta_query',$meta);
        }
        foreach (self::SPECS as $key=>$definition) {
            $value=isset($_GET['tn_'.$key]) && is_string($_GET['tn_'.$key])?sanitize_text_field(wp_unslash($_GET['tn_'.$key])):'';
            if (in_array($value,$definition[1],true)) {
                $meta=$query->get('meta_query');$meta=is_array($meta)?$meta:[];
                $meta[]=['key'=>'_tn_verified_'.$key,'value'=>$value];$query->set('meta_query',$meta);
            }
        }
    }
    private function preview_allowed(): bool {
        return current_user_can('manage_woocommerce') && current_user_can('edit_products') && current_user_can('read_private_products') && isset($_GET['tn_preview']) && $_GET['tn_preview']==='1';
    }
    public function preview_headers(): void {
        if (isset($_GET['tn_preview'])) {
            if (!defined('DONOTCACHEPAGE')) { define('DONOTCACHEPAGE',true); }
            nocache_headers();header('X-Robots-Tag: noindex, nofollow, noarchive');
        }
    }
    public function stock_html(string $html,$product): string {
        if (!$this->physical($product) || !$this->eligible($product)) { return $html; }
        $unit=self::UNITS[$product->get_meta('_tn_sale_unit')];
        return '<p class="stock in-stock">'.esc_html((string)$product->get_stock_quantity().' '.$unit.' قابل فروش').'</p>';
    }
    public function preview_notice(): void {
        if ($this->preview_allowed()) { echo '<div class="woocommerce-info">نمای مدیریت کاتالوگ: پیش‌نویس‌ها نیز فقط برای مدیر نمایش داده می‌شوند.</div>'; }
    }
    public function preview_link(string $url,$product): string {
        return $this->preview_allowed() && $product instanceof WC_Product && $product->get_status()==='draft' ? get_preview_post_link($product->get_id()) : $url;
    }
    public function tools(): void {
        global $product;
        if (!$product instanceof WC_Product) { return; }
        $data=$this->comparison_data($product);
        echo '<div class="tn-store-tools" data-tn-product="'.esc_attr(wp_json_encode($data)).'"><button type="button" data-tn-add="compare">مقایسه</button><button type="button" data-tn-add="wishlist">ذخیره در علاقه‌مندی</button></div>';
    }
    public function comparison_data(WC_Product $product): array {
        $specs=[];
        foreach(self::SPECS as $key=>$definition){$value=$product->get_meta('_tn_verified_'.$key);$specs[$key]=in_array($value,$definition[1],true)?$value:'تأیید نشده';}
        $price=0;
        $raw_price=$product->get_price();
        if (is_string($raw_price) && $raw_price!=='' && is_numeric($raw_price) && (float)$raw_price>0) {
            try { $price=TehNet_Store_Policy::irr($raw_price,'IRR'); } catch (InvalidArgumentException $e) { $price=0; }
        }
        return ['id'=>$product->get_id(),'sku'=>$product->get_sku(),'name'=>$product->get_name(),'url'=>$this->preview_link($product->get_permalink(),$product),'unit'=>self::UNITS[$product->get_meta('_tn_sale_unit')]??'تأیید نشده','minimum'=>$product->get_meta('_tn_min_quantity')?:'تأیید نشده','specs'=>$specs,'price'=>$price>0?number_format($price).' ریال':'نیازمند استعلام','price_irr'=>$price,'source_specs'=>self::source_specs($product->get_meta('_tn_source_attributes'))];
    }
    /** Vendor-declared attribute projection for comparison display; never mixed with verified specs. */
    public static function source_specs($attributes,int $bound = 8): array {
        if (!is_array($attributes)) { return []; }
        $out=[];
        foreach ($attributes as $attribute) {
            if (!is_array($attribute)) { continue; }
            if (count($out)>=$bound) { break; }
            $name=isset($attribute['name']) && is_string($attribute['name']) ? mb_substr(trim($attribute['name']),0,60) : '';
            $terms=[];
            foreach (is_array($attribute['terms']??null) ? $attribute['terms'] : [] as $term) {
                if (is_array($term) && isset($term['name']) && is_string($term['name']) && trim($term['name'])!=='') { $terms[]=mb_substr(trim($term['name']),0,60); }
                if (count($terms)>=3) { break; }
            }
            if ($name!=='' && $terms) { $out[$name]=implode(' / ',$terms); }
        }
        return $out;
    }
    public function card_badge(): void {
        global $product;
        if (!$product instanceof WC_Product) { return; }
        $created=$product->get_date_created();
        if (!$created instanceof WC_DateTime) { return; }
        if (time()-$created->getTimestamp() <= 45*DAY_IN_SECONDS) { echo '<span class="tn-badge tn-badge-new">جدید</span>'; }
    }
    public function related_products(): void {
        global $product;
        if (!$product instanceof WC_Product || is_cart() || is_checkout()) { return; }
        $ids=wc_get_related_products($product->get_id(),4);
        if (!$ids) {
            $args=['limit'=>5,'exclude'=>[$product->get_id()],'return'=>'ids','orderby'=>'rand'];
            if ($product->get_category_ids()) { $args['category']=array_map(static function($id){ $t=get_term($id,'product_cat'); return $t&&!is_wp_error($t)?$t->slug:''; },$product->get_category_ids()); }
            $ids=array_filter(wc_get_products($args));
        }
        if (!$ids) { return; }
        echo '<section class="tn-related" aria-labelledby="tn-related-title"><h2 id="tn-related-title">کالاهای مرتبط</h2><ul class="tn-related-list">';
        foreach ($ids as $related_id) {
            $related=wc_get_product($related_id);
            if (!$related instanceof WC_Product || $related->get_status()!=='publish') { continue; }
            echo '<li><a href="'.esc_url($related->get_permalink()).'">'.esc_html($related->get_name()).'</a></li>';
        }
        echo '</ul></section>';
    }
    /** Pure: newline list to bounded clean lines (2..120 chars, max 6). */
    public static function editorial_lines(string $raw): array {
        $out=[];
        foreach (preg_split('/?
/',$raw) ?: [] as $line) {
            $line=trim($line);
            if ($line==='' || mb_strlen($line)<2 || mb_strlen($line)>120) { continue; }
            $out[]=$line;
            if (count($out)>=6) { break; }
        }
        return $out;
    }
    public function editorial(): void {
        global $product;
        if (!$product instanceof WC_Product) { return; }
        $pros=$product->get_meta('_tn_editorial_pros'); $cons=$product->get_meta('_tn_editorial_cons');
        $pros=is_array($pros)?$pros:[]; $cons=is_array($cons)?$cons:[];
        if (!$pros && !$cons) { return; }
        echo '<div class="tn-editorial"><h2>نگاه تحریرهٔ تهران نتورک</h2><div class="tn-editorial-grid">';
        foreach ([['قوت','pros',$pros,'+'],['ضعف','cons',$cons,'−']] as [$label,$key,$lines,$mark]) {
            if (!$lines) { continue; }
            echo '<section class="tn-editorial-'.$key.'"><h3>نقاط '.$label.'</h3><ul>';
            foreach ($lines as $line) { echo '<li>'.esc_html($mark.' '.$line).'</li>'; }
            echo '</ul></section>';
        }
        echo '</div><p class="description">دیدگاه تحریریه بر پایهٔ بررسی کاتالوگ است؛ جای مشخصات تأییدشدهٔ فنی را نمی‌گیرد.</p></div>';
    }
    public function unit(): void {
        global $product;
        if (!$this->physical($product)) { return; }
        $unit=self::UNITS[$product->get_meta('_tn_sale_unit')]??'نیازمند تأیید';
        echo '<div class="tn-store-unit"><p>واحد فروش: <strong>'.esc_html($unit).'</strong></p><p>شرایط ضمانت، بسته‌بندی و هزینه ارسال در پیش‌فاکتور نهایی اعلام می‌شود.</p></div>';
    }
    public function dialog(): void {
        if (!wp_script_is('tn-store','enqueued')) { return; }
        echo '<dialog id="tn-store-dialog" aria-labelledby="tn-store-dialog-title" dir="rtl"><h2 id="tn-store-dialog-title">انتخاب‌های شما</h2><div id="tn-store-dialog-content"></div><button type="button" data-tn-close>بستن</button></dialog><p id="tn-store-feedback" class="screen-reader-text" role="status" aria-live="polite"></p>';
    }
    public function fields(): void {
        wp_nonce_field('tn_store_product','tn_store_nonce');
        woocommerce_wp_select(['id'=>'_tn_sale_unit','label'=>'واحد فروش تأییدشده','options'=>[''=>'نیازمند تأیید']+self::UNITS]);
        woocommerce_wp_text_input(['id'=>'_tn_min_quantity','label'=>'حداقل مقدار سفارش','type'=>'text','description'=>'عدد دقیق؛ موجودی و رزرو فقط از ERP تأیید می‌شوند.']);
        woocommerce_wp_checkbox(['id'=>'_tn_sale_approved','label'=>'مشخصات و قیمت تهران نتورک تأیید شد','cbvalue'=>'yes']);
        woocommerce_wp_text_input(['id'=>'_tn_erp_sku','label'=>'شناسه کالای تأییدشده در ERP']);
        woocommerce_wp_text_input(['id'=>'_tn_erp_uom','label'=>'واحد دقیق ERP','description'=>'نام واحد در ERP؛ تبدیل قرقره/متر باید در همان کالا ثبت شده باشد.']);
        woocommerce_wp_text_input(['id'=>'_tn_technical_evidence_url','label'=>'منبع معتبر مشخصات تأییدشده','type'=>'url']);
        foreach (self::SPECS as $key=>$definition) { woocommerce_wp_select(['id'=>'_tn_verified_'.$key,'label'=>$definition[0].' تأییدشده','options'=>[''=>'نیازمند بررسی']+array_combine($definition[1],$definition[1])]); }
        woocommerce_wp_textarea_input(['id'=>'_tn_editorial_pros','label'=>'نقاط قوت تحریریه (هر خط یک مورد، حداکثر ۶)','rows'=>4]);
        woocommerce_wp_textarea_input(['id'=>'_tn_editorial_cons','label'=>'نقاط ضعف تحریریه (هر خط یک مورد، حداکثر ۶)','rows'=>4]);
    }
    public function save_fields(int $id): void {
        if (!current_user_can('manage_woocommerce') || !isset($_POST['tn_store_nonce']) || !is_string($_POST['tn_store_nonce']) || !wp_verify_nonce(wp_unslash($_POST['tn_store_nonce']),'tn_store_product')) { return; }
        $unit=isset($_POST['_tn_sale_unit']) && is_string($_POST['_tn_sale_unit'])?sanitize_key(wp_unslash($_POST['_tn_sale_unit'])):'';
        $minimum=isset($_POST['_tn_min_quantity']) && is_string($_POST['_tn_min_quantity'])?sanitize_text_field(wp_unslash($_POST['_tn_min_quantity'])):'';
        try { TehNet_Store_Policy::quantity_milli($minimum); } catch(InvalidArgumentException $e) { $minimum=''; }
        update_post_meta($id,'_tn_sale_unit',isset(self::UNITS[$unit])?$unit:'');
        update_post_meta($id,'_tn_min_quantity',$minimum);
        update_post_meta($id,'_tn_sale_approved',isset($_POST['_tn_sale_approved'])?'yes':'no');
        foreach (['_tn_erp_sku','_tn_erp_uom'] as $key) {
            if (isset($_POST[$key]) && is_string($_POST[$key])) { update_post_meta($id,$key,sanitize_text_field(wp_unslash($_POST[$key]))); }
        }
        delete_post_meta($id,'_tn_erp_fresh_until');
        $evidence=isset($_POST['_tn_technical_evidence_url']) && is_string($_POST['_tn_technical_evidence_url'])?esc_url_raw(wp_unslash($_POST['_tn_technical_evidence_url'])):'';
        $verified=wp_parse_url($evidence,PHP_URL_SCHEME)==='https' && wp_parse_url($evidence,PHP_URL_HOST);
        update_post_meta($id,'_tn_technical_evidence_url',$verified?$evidence:'');
        foreach (self::SPECS as $key=>$definition) {
            $field='_tn_verified_'.$key;$value=isset($_POST[$field]) && is_string($_POST[$field])?sanitize_text_field(wp_unslash($_POST[$field])):'';
            update_post_meta($id,$field,$verified && in_array($value,$definition[1],true)?$value:'');
        }
        foreach (['_tn_editorial_pros','_tn_editorial_cons'] as $editorial_key) {
            $raw=isset($_POST[$editorial_key]) && is_string($_POST[$editorial_key])?sanitize_textarea_field(wp_unslash($_POST[$editorial_key])):'';
            update_post_meta($id,$editorial_key,self::editorial_lines($raw));
        }
        add_post_meta($id,'_tn_store_review_audit',wp_json_encode(['user'=>get_current_user_id(),'at'=>gmdate('c'),'action'=>'product-sale-review']));
    }
}
