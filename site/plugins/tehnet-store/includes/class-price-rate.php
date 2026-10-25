<?php
defined('ABSPATH') || exit;

/** FX-rate bulk price tool. Only writes price data; sale approval and ERP readiness stay untouched. */
final class TehNet_Store_Price_Rate {
    public const STATE_OPTION = 'tn_fx_rate';
    public const LOG_OPTION = 'tn_fx_log';
    private const LOG_BOUND = 50;

    public static function state(): array {
        $state = get_option(self::STATE_OPTION,[]);
        if (!is_array($state) || !isset($state['rate'])) { return ['rate'=>0.0,'base'=>'USD','updated_at'=>'','updated_by'=>0]; }
        return ['rate'=>(float)$state['rate'],'base'=>(string)($state['base'] ?? 'USD'),'updated_at'=>(string)($state['updated_at'] ?? ''),'updated_by'=>(int)($state['updated_by'] ?? 0)];
    }

    /** ceil(base*rate) rounded up to the next multiple of $round IRR; exact integer math on scaled values. */
    public static function compute(string $base_price, float $rate, int $round = 1000): int {
        if ($rate <= 0 || $round <= 0) { throw new InvalidArgumentException('Rate and rounding must be positive'); }
        if (!preg_match('/^\d+(\.\d{1,6})?$/D',$base_price)) { throw new InvalidArgumentException('Base price must be a plain decimal'); }
        $scaled = (int)round(((float)$base_price) * $rate * 1000);
        if ($scaled <= 0) { throw new InvalidArgumentException('Base price must be positive'); }
        if ($scaled > 9223372036854775807 - $round) { throw new InvalidArgumentException('Result overflows integer rial'); }
        return (intdiv($scaled + $round*1000 - 1, $round*1000)) * $round;
    }

    /** Pure planning step over [['id','sku','base','price']] rows; returns proposed rows and skips. */
    public static function plan(array $products, float $rate, int $round = 1000): array {
        $rows = $skipped = [];
        foreach ($products as $product) {
            $base = (string)($product['base'] ?? '');
            if ($base === '') { $skipped[] = ['sku'=>(string)($product['sku'] ?? ''),'reason'=>'no-base-price']; continue; }
            try { $proposed = self::compute($base,$rate,$round); }
            catch (InvalidArgumentException $e) { $skipped[] = ['sku'=>(string)($product['sku'] ?? ''),'reason'=>'invalid-base-price']; continue; }
            $rows[] = ['id'=>(int)$product['id'],'sku'=>(string)($product['sku'] ?? ''),'base'=>$base,'current_irr'=>(int)($product['price'] ?? 0),'proposed_irr'=>$proposed];
        }
        return ['rows'=>$rows,'skipped'=>$skipped];
    }

    private function product_rows(): array {
        $out = [];
        foreach (wc_get_products(['limit'=>500,'status'=>'any','orderby'=>'ID','order'=>'ASC']) as $product) {
            if (!$product instanceof WC_Product) { continue; }
            $out[] = ['id'=>$product->get_id(),'sku'=>$product->get_sku() ?: ('#'.$product->get_id()),'base'=>(string)$product->get_meta('_tn_base_price'),'price'=>(int)round((float)$product->get_price())];
        }
        return $out;
    }

    public function preview(float $rate, int $round = 1000): array {
        if ($rate <= 0) { throw new InvalidArgumentException('Rate must be positive'); }
        return self::plan($this->product_rows(),$rate,$round);
    }

    public function apply(float $rate, int $round = 1000, int $actor = 0): array {
        $preview = $this->preview($rate,$round);
        $changed = 0;
        $previous = [];
        foreach ($preview['rows'] as $row) {
            $product = wc_get_product($row['id']);
            if (!$product instanceof WC_Product) { continue; }
            if ((int)round((float)$product->get_price()) === $row['proposed_irr']) { continue; }
            $previous[] = ['id'=>$row['id'],'sku'=>$row['sku'],'price_irr'=>(int)round((float)$product->get_price())];
            $product->set_regular_price((string)$row['proposed_irr']);
            $product->update_meta_data('_tn_price_fx_at',gmdate('c'));
            $product->update_meta_data('_tn_price_fx_rate',(string)$rate);
            $product->save();
            $changed++;
        }
        update_option(self::STATE_OPTION,['rate'=>$rate,'base'=>'USD','updated_at'=>gmdate('c'),'updated_by'=>$actor],false);
        $this->log(['at'=>gmdate('c'),'actor'=>$actor,'rate'=>$rate,'changed'=>$changed,'skipped'=>count($preview['skipped']),'previous'=>$previous]);
        return ['rate'=>$rate,'changed'=>$changed,'skipped'=>count($preview['skipped']),'rows'=>$preview['rows']];
    }

    private function log(array $entry): void {
        $log = get_option(self::LOG_OPTION,[]);
        if (!is_array($log)) { $log = []; }
        array_unshift($log,$entry);
        update_option(self::LOG_OPTION,array_slice($log,0,self::LOG_BOUND),false);
    }

    public function register(): void {
        add_action('admin_menu',function():void {
            add_submenu_page('tn-store','قیمت و نرخ ارز','قیمت و نرخ ارز','manage_woocommerce','tn-store-pricing',[$this,'page']);
        });
        add_action('admin_post_tn_fx_apply',[$this,'submit']);
        add_action('woocommerce_product_options_pricing',function():void {
            woocommerce_wp_text_input(['id'=>'_tn_base_price','label'=>'قیمت پایه (USD)','data_type'=>'decimal','description'=>'مبنای به‌روزرسانی گروهی با نرخ ارز؛ فروش همچنان نیازمند تأیید جداگانه است.']);
        });
        add_action('woocommerce_process_product_meta',function(int $id):void {
            $raw = isset($_POST['_tn_base_price']) && is_string($_POST['_tn_base_price']) ? wp_unslash($_POST['_tn_base_price']) : '';
            $value = preg_replace('/[^0-9.]/','',$raw);
            if ($value !== '' && !preg_match('/^\d+(\.\d{1,6})?$/D',$value)) { $value = ''; }
            $product = wc_get_product($id);
            if ($product) { $product->update_meta_data('_tn_base_price',$value); $product->save(); }
        });
    }

    public function page(): void {
        if (!current_user_can('manage_woocommerce')) { wp_die('دسترسی مجاز نیست.',403); }
        $state = self::state();
        $rate = isset($_GET['rate']) && is_numeric($_GET['rate']) ? (float)wp_unslash($_GET['rate']) : 0.0;
        echo '<div class="wrap" dir="rtl"><h1>قیمت و نرخ ارز</h1>';
        echo '<p>قیمت پایهٔ هر کالا (USD) در صفحهٔ ویرایش کالا ثبت می‌شود؛ این ابزار همهٔ قیمت‌های ریالی را با «قیمت پایه × نرخ» به‌صورت گروهی بازمحاسبه و به بالا گرد می‌کند. فروش و نمایش قیمت همچنان به تأیید فروش و آمادگی ERP وابسته است و این ابزار آن وضعیت را تغییر نمی‌دهد.</p>';
        if ($state['updated_at']) { echo '<p>آخرین نرخ ثبت‌شده: <bdi>'.esc_html($state['rate']).'</bdi> ریال/'.esc_html($state['base']).' در '.esc_html($state['updated_at']).'</p>'; }
        echo '<form method="get" action="'.esc_url(admin_url('admin.php')).'"><input type="hidden" name="page" value="tn-store-pricing">';
        echo '<p><label>نرخ ارز (ریال به ازای هر ۱ '.esc_html($state['base'] ?: 'USD').') <input type="number" step="any" min="0.000001" name="rate" value="'.esc_attr($rate ?: '').'" required></label> ';
        submit_button('پیش‌نمایش تغییرات','secondary','preview',false);
        echo '</p></form>';
        if ($rate > 0) {
            try { $preview = $this->preview($rate); }
            catch (InvalidArgumentException $e) { echo '<div class="notice notice-error"><p>نرخ نامعتبر است.</p></div>'; $preview = null; }
            if ($preview !== null) {
                echo '<h2>پیش‌نمایش ('.count($preview['rows']).' کالا؛ '.count($preview['skipped']).' کالا بدون قیمت پایه)</h2>';
                echo '<table class="widefat striped"><thead><tr><th>کالا</th><th>قیمت پایه</th><th>قیمت فعلی (ریال)</th><th>قیمت پیشنهادی (ریال)</th></tr></thead><tbody>';
                foreach ($preview['rows'] as $row) {
                    echo '<tr><td><bdi>'.esc_html($row['sku']).'</bdi></td><td>'.esc_html($row['base']).'</td><td>'.esc_html(number_format($row['current_irr'])).'</td><td><b>'.esc_html(number_format($row['proposed_irr'])).'</b></td></tr>';
                }
                echo '</tbody></table>';
                echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';
                wp_nonce_field('tn_fx_apply');
                echo '<input type="hidden" name="action" value="tn_fx_apply"><input type="hidden" name="rate" value="'.esc_attr($rate).'">';
                submit_button('اعمال روی '.count($preview['rows']).' کالا','primary');
                echo '</form>';
            }
        }
        $log = get_option(self::LOG_OPTION,[]);
        if (is_array($log) && $log) {
            echo '<h2>تاریخچه</h2><table class="widefat striped"><thead><tr><th>زمان</th><th>نرخ</th><th>تغییرکرد</th><th>ردشده</th></tr></thead><tbody>';
            foreach (array_slice($log,0,20) as $entry) {
                echo '<tr><td>'.esc_html($entry['at'] ?? '').'</td><td><bdi>'.esc_html($entry['rate'] ?? '').'</bdi></td><td>'.(int)($entry['changed'] ?? 0).'</td><td>'.(int)($entry['skipped'] ?? 0).'</td></tr>';
            }
            echo '</tbody></table>';
        }
        echo '</div>';
    }

    public function submit(): void {
        if (!current_user_can('manage_woocommerce')) { wp_die('دسترسی مجاز نیست.',403); }
        check_admin_referer('tn_fx_apply');
        $rate = isset($_POST['rate']) && is_numeric($_POST['rate']) ? (float)wp_unslash($_POST['rate']) : 0.0;
        try { $result = $this->apply($rate,1000,get_current_user_id()); }
        catch (InvalidArgumentException $e) { wp_safe_redirect(add_query_arg(['page'=>'tn-store-pricing','tn_error'=>'rate'],admin_url('admin.php')));exit; }
        wp_safe_redirect(add_query_arg(['page'=>'tn-store-pricing','tn_result'=>'ok','changed'=>$result['changed']],admin_url('admin.php')));exit;
    }
}
