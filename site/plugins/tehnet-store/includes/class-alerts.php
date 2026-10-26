<?php
defined('ABSPATH') || exit;

/** Price-drop and back-in-stock alerts. Delivery depends on a configured mail sender; checks never invent data. */
final class TehNet_Store_Alerts {
    public const CPT='tn_alert';
    private const TYPES=['price','stock'];
    public const STATE_OPTION='tn_alerts_state';

    public static function install(): void {
        register_post_type(self::CPT,['labels'=>['name'=>'هشدار کالا','singular_name'=>'هشدار کالا'],'public'=>false,'show_ui'=>false,
            'supports'=>['title'],'capability_type'=>'post','capabilities'=>['create_posts'=>'do_not_allow'],'map_meta_cap'=>true]);
    }

    /** Pure validation: email shape, known type, optional positive integer target. */
    public static function validate_subscription(string $email,string $type,string $target=''): array {
        $errors=[];
        $email=trim($email);
        if (!filter_var($email,FILTER_VALIDATE_EMAIL) || mb_strlen($email)>120) { $errors[]='email'; }
        if (!in_array($type,self::TYPES,true)) { $errors[]='type'; }
        $target=trim($target);
        if ($type==='price' && $target!=='') {
            if (!preg_match('/^\d{1,15}$/D',$target) || (int)$target<=0) { $errors[]='target'; }
        }
        return $errors===[] ? ['ok'=>true,'email'=>$email,'type'=>$type,'target'=>$type==='price'&&$target!==''?(int)$target:null] : ['ok'=>false,'errors'=>$errors];
    }

    /** Pure decision: should a waiting alert fire for the observed product state? */
    public static function evaluate_alert(string $type,int $price_irr,string $stock_status,?int $target): bool {
        if ($type==='price') { return $price_irr>0 && ($target===null || $price_irr<=$target); }
        if ($type==='stock') { return $stock_status==='instock'; }
        return false;
    }

    public function register(): void {
        add_action('init',[self::class,'install']);
        add_action('woocommerce_after_single_product_summary',[$this,'product_form'],28);
        add_action('admin_post_tn_alert_subscribe',[$this,'subscribe']);
        add_action('admin_post_nopriv_tn_alert_subscribe',[$this,'subscribe']);
        add_action('tn_alerts_check',[$this,'check']);
        add_action('admin_menu',function():void { add_submenu_page('tn-store','هشدار قیمت و موجودی','هشدارها','tn_store_operations_view','tn-store-alerts',[$this,'admin_page']); });
        if (!wp_next_scheduled('tn_alerts_check')) { wp_schedule_event(time()+HOUR_IN_SECONDS,'hourly','tn_alerts_check'); }
    }

    public function product_form(): void {
        global $product;
        if (!$product instanceof WC_Product) { return; }
        $price=(int)round((float)$product->get_price());
        if (isset($_GET['tn_alert']) && $_GET['tn_alert']==='sent') { echo '<p role="status" class="tn-qa-notice">هشدار شما ثبت شد.</p>'; }
        echo '<details class="tn-alert-form"><summary>هشدار تغییر قیمت یا موجود شدن</summary>';
        echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'"><input type="hidden" name="action" value="tn_alert_subscribe"><input type="hidden" name="product_id" value="'.esc_attr($product->get_id()).'">';
        wp_nonce_field('tn_alert_'.$product->get_id());
        echo '<p><label>ایمیل شما <input type="email" name="tn_email" maxlength="120" required></label></p>';
        echo '<p><label>نوع هشدار <select name="tn_type"><option value="stock">موجود شد</option><option value="price"'.($price>0?'':' disabled').'>قیمت ثبت شد یا کاهش یافت</option></select></label></p>';
        echo '<p><label>حداکثر قیمت، ریال (اختیاری، برای هشدار قیمت) <input type="number" min="0" step="1000" name="tn_target"></label></p>';
        echo '<p><button class="button" type="submit">ثبت هشدار</button></p>';
        echo '<p class="description">ارسال ایمیل پس از پیکربندی سرویس ایمیل فعال می‌شود؛ هشدارها هر ساعت بررسی می‌شوند.</p>';
        echo '</form></details>';
    }

    public function subscribe(): void {
        $raw=$_POST['product_id']??null;
        $product=is_scalar($raw)?wc_get_product(absint($raw)):false;
        if (!$product instanceof WC_Product) { wp_die('کالا در دسترس نیست.',404); }
        check_admin_referer('tn_alert_'.$product->get_id());
        if (!TehNet_Store_Policy::throttle('alert',5,3600)) { wp_die('تعداد درخواست‌های شما زیاد است؛ کمی بعد دوباره تلاش کنید.',429); }
        $email=isset($_POST['tn_email'])&&is_string($_POST['tn_email'])?sanitize_text_field(wp_unslash($_POST['tn_email'])):'';
        $type=isset($_POST['tn_type'])&&is_string($_POST['tn_type'])?sanitize_key(wp_unslash($_POST['tn_type'])):'';
        $target=isset($_POST['tn_target'])&&is_string($_POST['tn_target'])?sanitize_text_field(wp_unslash($_POST['tn_target'])):'';
        $valid=self::validate_subscription($email,$type,$target);
        if (!$valid['ok']) { wp_die('اطلاعات هشدار نامعتبر است.',400); }
        $existing=get_posts(['post_type'=>self::CPT,'post_status'=>'private','posts_per_page'=>1,'meta_query'=>[
            ['key'=>'_tn_email','value'=>$valid['email']],['key'=>'_tn_product_id','value'=>$product->get_id()],['key'=>'_tn_type','value'=>$valid['type']]]]);
        if (!$existing) {
            $id=wp_insert_post(['post_type'=>self::CPT,'post_status'=>'private','post_title'=>'هشدار '.$valid['type'].' — '.$product->get_sku()],true);
            if (is_wp_error($id)) { wp_die('ثبت هشدار انجام نشد.',500); }
            update_post_meta($id,'_tn_email',$valid['email']);
            update_post_meta($id,'_tn_product_id',$product->get_id());
            update_post_meta($id,'_tn_type',$valid['type']);
            update_post_meta($id,'_tn_target',$valid['target']);
            update_post_meta($id,'_tn_state','waiting');
        }
        wp_safe_redirect(add_query_arg('tn_alert','sent',$product->get_permalink()));exit;
    }

    public function check(): void {
        $checked=$fired=$failed=0;
        $alerts=get_posts(['post_type'=>self::CPT,'post_status'=>'private','posts_per_page'=>50,'meta_key'=>'_tn_state','meta_value'=>'waiting']);
        foreach ($alerts as $alert) {
            $checked++;
            $product=wc_get_product((int)get_post_meta($alert->ID,'_tn_product_id',true));
            if (!$product instanceof WC_Product) { continue; }
            $raw_price=$product->get_price();
            $price=0;
            if (is_string($raw_price) && $raw_price!=='' && is_numeric($raw_price) && (float)$raw_price>0) {
                try { $price=TehNet_Store_Policy::irr($raw_price,'IRR'); } catch (InvalidArgumentException $e) { $price=0; }
            }
            $should=self::evaluate_alert((string)get_post_meta($alert->ID,'_tn_type',true),$price,$product->get_stock_status(),get_post_meta($alert->ID,'_tn_target',true)!==''?(int)get_post_meta($alert->ID,'_tn_target',true):null);
            if (!$should) { continue; }
            $email=(string)get_post_meta($alert->ID,'_tn_email',true);
            $sent=wp_mail($email,'هشدار کالای تهران نتورک','کالای «'.$product->get_name().'» مطابق هشدار شما تغییر کرد: '.$product->get_permalink(),['Content-Type: text/html; charset=UTF-8']);
            if ($sent) { update_post_meta($alert->ID,'_tn_state','sent'); $fired++; } else { $failed++; }
        }
        update_option(self::STATE_OPTION,['at'=>gmdate('c'),'checked'=>$checked,'fired'=>$fired,'failed'=>$failed],false);
    }

    public function admin_page(): void {
        if (!current_user_can('tn_store_operations_view')) { wp_die('دسترسی مجاز نیست.',403); }
        $state=get_option(self::STATE_OPTION,[]);
        echo '<div class="wrap" dir="rtl"><h1>هشدار قیمت و موجودی</h1>';
        if (isset($_GET['tn_result']) && $_GET['tn_result']==='run') { $this->check(); echo '<div class="notice notice-success"><p>بررسی همین حالا اجرا شد.</p></div>'; $state=get_option(self::STATE_OPTION,[]); }
        echo '<p>آخرین بررسی خودکار: '.esc_html(is_array($state)&&isset($state['at'])?$state['at']:'—');
        if (is_array($state)&&isset($state['checked'])) { echo ' — بررسی‌شده: '.(int)$state['checked'].' | ارسال‌شده: '.(int)$state['fired'].' | ناموفق: '.(int)$state['failed']; }
        echo '</p><p><a class="button" href="'.esc_url(add_query_arg('tn_result','run',admin_url('admin.php?page=tn-store-alerts'))).'">اجرای بررسی همین حالا</a></p>';
        if (!function_exists('wp_mail')) { echo '<div class="notice notice-warning"><p>سرویس ایمیل پیکربندی نشده است؛ ارسال انجام نمی‌شود تا SMTP تنظیم شود.</p></div>'; }
        $alerts=new WP_Query(['post_type'=>self::CPT,'post_status'=>'private','posts_per_page'=>100]);
        if ($alerts->have_posts()) {
            echo '<table class="widefat striped"><thead><tr><th>کالا</th><th>ایمیل</th><th>نوع</th><th>هدف</th><th>وضعیت</th></tr></thead><tbody>';
            while ($alerts->have_posts()) { $alerts->the_post(); $a=get_post(); $pid=(int)get_post_meta($a->ID,'_tn_product_id',true); $product=wc_get_product($pid);
                echo '<tr><td>'.esc_html($product?$product->get_name():'#'.$pid).'</td><td><bdi>'.esc_html((string)get_post_meta($a->ID,'_tn_email',true)).'</bdi></td><td>'.esc_html((string)get_post_meta($a->ID,'_tn_type',true)==='price'?'قیمت':'موجودی').'</td><td>'.esc_html((string)(get_post_meta($a->ID,'_tn_target',true)?:'—')).'</td><td>'.esc_html((string)get_post_meta($a->ID,'_tn_state',true)).'</td></tr>';
            }
            wp_reset_postdata();
            echo '</tbody></table>';
        } else { echo '<p>هشداری ثبت نشده است.</p>'; }
        echo '</div>';
    }
}
