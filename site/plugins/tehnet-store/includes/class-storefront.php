<?php
defined('ABSPATH') || exit;

final class TehNet_Store_Storefront {
    private const UNITS=['piece'=>'عدد','meter'=>'متر','reel'=>'قرقره','pack'=>'بسته'];
    private const SPECS=['shield'=>['شیلد',['UTP','FTP','SFTP']],'jacket'=>['روکش',['PVC','LSZH']],'environment'=>['محیط نصب',['Indoor','Outdoor']]];
    public function register(): void {
        add_action('wp_enqueue_scripts',[$this,'assets']);
        add_action('woocommerce_before_shop_loop',[$this,'filters'],5);
        add_action('woocommerce_no_products_found',[$this,'filters'],5);
        add_filter('request',[$this,'normalize_request']);
        add_filter('posts_search',[$this,'sku_search'],20,2);
        add_filter('woocommerce_redirect_single_search_result',fn($value)=>$this->preview_allowed()?false:$value);
        add_action('woocommerce_after_shop_loop_item',[$this,'tools'],20);
        add_action('woocommerce_single_product_summary',[$this,'unit'],11);
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
        wp_enqueue_style('tn-store',plugins_url('assets/store.css',dirname(__DIR__).'/tehnet-store.php'),[], '0.2.3');
        wp_enqueue_script('tn-store',plugins_url('assets/store.js',dirname(__DIR__).'/tehnet-store.php'),[], '0.2.1',true);
    }
    public function filters(): void {
        $unit=isset($_GET['tn_unit']) && is_string($_GET['tn_unit']) ? sanitize_key(wp_unslash($_GET['tn_unit'])) : '';
        echo '<form class="tn-store-filters" method="get" action="'.esc_url(wc_get_page_permalink('shop')).'">';
        echo '<input type="hidden" name="post_type" value="product"><label>جست‌وجوی کالا <input name="s" type="search" value="'.esc_attr(get_search_query()).'" placeholder="نام، مدل یا SKU کالا"></label>';
        if ($this->preview_allowed()) { echo '<input type="hidden" name="tn_preview" value="1">'; }
        $category=isset($_GET['product_cat'])&&is_string($_GET['product_cat'])?sanitize_title(wp_unslash($_GET['product_cat'])):'';
        echo '<label>دسته کالا ';wp_dropdown_categories(['taxonomy'=>'product_cat','name'=>'product_cat','value_field'=>'slug','selected'=>$category,'show_option_all'=>'همه دسته‌ها','hide_empty'=>true,'hierarchical'=>true]);echo '</label>';
        echo '<label>واحد فروش <select name="tn_unit"><option value="">همه واحدها</option>';
        foreach(self::UNITS as $key=>$label) { printf('<option value="%s" %s>%s</option>',esc_attr($key),selected($unit,$key,false),esc_html($label)); }
        echo '</select></label>';
        foreach (self::SPECS as $key=>$definition) {
            $current=isset($_GET['tn_'.$key]) && is_string($_GET['tn_'.$key])?sanitize_text_field(wp_unslash($_GET['tn_'.$key])):'';
            echo '<label>'.esc_html($definition[0]).' <select name="tn_'.esc_attr($key).'"><option value="">همه مشخصات تأییدشده</option>';
            foreach ($definition[1] as $value) { echo '<option value="'.esc_attr($value).'" '.selected($current,$value,false).'>'.esc_html($value).'</option>'; }
            echo '</select></label>';
        }
        $reset=$this->preview_allowed()?add_query_arg('tn_preview','1',wc_get_page_permalink('shop')):wc_get_page_permalink('shop');
        echo '<button class="button" type="submit">اعمال فیلتر</button><a class="tn-filter-reset" href="'.esc_url($reset).'">پاک کردن فیلترها</a></form>';
        echo '<div class="tn-store-toolbar"><span>قیمت‌ها با واحد ریال نمایش داده می‌شوند؛ موجودی و ارسال پیش از تأیید سفارش بررسی می‌شود.</span><button type="button" data-tn-open="compare">مقایسه <span data-tn-count="compare">۰</span></button><button type="button" data-tn-open="wishlist">علاقه‌مندی <span data-tn-count="wishlist">۰</span></button></div>';
    }
    public function query($query): void {
        if ($this->preview_allowed()) { $query->set('post_status',['publish','draft']); }
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
        return ['id'=>$product->get_id(),'sku'=>$product->get_sku(),'name'=>$product->get_name(),'url'=>$this->preview_link($product->get_permalink(),$product),'unit'=>self::UNITS[$product->get_meta('_tn_sale_unit')]??'تأیید نشده','minimum'=>$product->get_meta('_tn_min_quantity')?:'تأیید نشده','specs'=>$specs,'price'=>$this->eligible($product)?number_format(TehNet_Store_Policy::irr($product->get_price(),'IRR')).' ریال':'نیازمند استعلام'];
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
        add_post_meta($id,'_tn_store_review_audit',wp_json_encode(['user'=>get_current_user_id(),'at'=>gmdate('c'),'action'=>'product-sale-review']));
    }
}
