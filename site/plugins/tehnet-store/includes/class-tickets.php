<?php
defined('ABSPATH') || exit;

/** Support tickets. Reply delivery to customers depends on a configured mail sender; Telegram bridge stays a separate token-gated feature. */
final class TehNet_Store_Tickets {
    public const CPT='tn_ticket';
    private const PAGE_SLUG='support';
    public const STATES=['open','answered','closed'];

    /** Only supported infrastructure intents may prefill the existing ticket intake. */
    public static function service_context($value): array {
        $options=self::service_options();
        if (!is_string($value) || !isset($options[$value])) { return []; }
        return ['key'=>$value,'label'=>$options[$value]];
    }

    /** Intake routing, not a promise of availability, price or specialist capacity. */
    public static function service_options(): array {
        return [
            'general-network'=>'انتخاب مسیر مناسب برای نیاز شبکه',
            'network-support'=>'عیب‌یابی و پشتیبانی شبکه',
            'network-setup'=>'طراحی یا توسعه شبکه',
            'mikrotik'=>'پیکربندی و عیب‌یابی MikroTik',
            'remote-support'=>'بررسی امکان پشتیبانی از راه دور',
            'voice-network'=>'بررسی آمادگی شبکه برای VoIP',
            'monitoring-scoping'=>'نیازسنجی مانیتورینگ؛ پس از تأیید دامنه',
            'server-scoping'=>'نیازسنجی سرور و مجازی‌سازی؛ پس از تأیید دامنه',
            'security-scoping'=>'نیازسنجی امنیت شبکه؛ پس از تأیید دامنه',
            'wifi-branch-scoping'=>'نیازسنجی Wi-Fi و شعب؛ پس از تأیید دامنه',
        ];
    }

    public static function install(): void {
        register_post_type(self::CPT,['labels'=>['name'=>'تیکت پشتیبانی','singular_name'=>'تیکت'],'public'=>false,'show_ui'=>false,
            'supports'=>['title'],'capability_type'=>'post','capabilities'=>['create_posts'=>'do_not_allow'],'map_meta_cap'=>true]);
        if (!get_option('tn_support_page_created') && !get_page_by_path(self::PAGE_SLUG)) {
            $id=wp_insert_post(['post_type'=>'page','post_status'=>'publish','post_name'=>self::PAGE_SLUG,'post_title'=>'پشتیبانی و تیکت','post_content'=>'<!-- wp:paragraph --><p>مشکل سفارش، استعلام یا پیش‌فاکتور خود را ثبت کنید؛ کارشناسان تهران نتورک در ساعات کاری پاسخ می‌دهند.</p><!-- /wp:paragraph -->'."\n".'[tn_support_ticket]']);
            if ($id && !is_wp_error($id)) { update_option('tn_support_page_created',true,false); }
        }
    }

    /** Pure validation for ticket intake. */
    public static function validate_ticket(string $name,string $email,string $subject,string $message,string $reference=''): array {
        $errors=[];
        $name=trim($name); $email=trim($email); $subject=trim($subject); $message=trim($message); $reference=trim($reference);
        if (mb_strlen($name)<2 || mb_strlen($name)>80) { $errors[]='name'; }
        if (!filter_var($email,FILTER_VALIDATE_EMAIL) || mb_strlen($email)>120) { $errors[]='email'; }
        if (mb_strlen($subject)<3 || mb_strlen($subject)>140) { $errors[]='subject'; }
        if (mb_strlen($message)<10 || mb_strlen($message)>3000) { $errors[]='message'; }
        if (mb_strlen($reference)>80) { $errors[]='reference'; }
        return $errors===[] ? ['ok'=>true,'name'=>$name,'email'=>$email,'subject'=>$subject,'message'=>$message,'reference'=>$reference] : ['ok'=>false,'errors'=>$errors];
    }

    public function register(): void {
        add_action('init',[self::class,'install']);
        add_shortcode('tn_support_ticket',[$this,'shortcode']);
        add_shortcode('tn_service_request',[$this,'service_shortcode']);
        add_action('template_redirect',[$this,'protect_service_receipt'],0);
        add_action('admin_post_tn_ticket_submit',[$this,'submit']);
        add_action('admin_post_nopriv_tn_ticket_submit',[$this,'submit']);
        add_action('woocommerce_after_single_product_summary',[$this,'product_inquiry_form'],26);
        add_action('admin_post_tn_inquiry_submit',[$this,'submit_inquiry']);
        add_action('admin_post_nopriv_tn_inquiry_submit',[$this,'submit_inquiry']);
        add_action('admin_post_tn_ticket_reply',[$this,'reply']);
        add_action('admin_menu',function():void { add_submenu_page('tn-store','تیکت‌های پشتیبانی','تیکت‌ها','tn_store_operations_view','tn-store-tickets',[$this,'admin_page']); });
    }

    public function shortcode(): string {
        $service=self::service_context($_GET['tn_service_context']??'');
        $out='<form method="post" action="'.esc_url(admin_url('admin-post.php')).'" class="tn-ticket-form" dir="rtl"><input type="hidden" name="action" value="tn_ticket_submit">';
        $out.=wp_nonce_field('tn_ticket','_wpnonce',true,false);
        if ($service) { $out.='<input type="hidden" name="tn_service_context" value="'.esc_attr($service['key']).'">'; }
        $out.='<p class="tn-qa-hp" aria-hidden="true"><label>خالی بگذارید <input name="tn_hp" tabindex="-1" autocomplete="off"></label></p>';
        $out.='<p><label>نام شما <input name="tn_name" maxlength="80" required></label></p>';
        $out.='<p><label>ایمیل <input type="email" name="tn_email" maxlength="120" required></label></p>';
        $out.='<p><label>موضوع <input name="tn_subject" maxlength="140" required value="'.esc_attr($service['label']??'').'"></label></p>';
        $out.='<p><label>ارجاع (اختیاری: شماره سفارش/پیش‌فاکتور یا کد کالا) <input name="tn_reference" maxlength="80"></label></p>';
        $out.='<p><label>شرح مشکل <textarea name="tn_message" maxlength="3000" required></textarea></label></p>';
        $out.='<p><button class="button button-primary" type="submit">ثبت تیکت</button></p></form>';
        return $this->service_receipt_notice().$out;
    }

    /** No JavaScript dependency; submits to the existing private ticket store. */
    public function service_shortcode(): string {
        $service=self::service_context($_GET['tn_service_context']??'');
        $out='<form method="post" action="'.esc_url(admin_url('admin-post.php')).'" class="tn-ticket-form tn-service-request" data-tn-service-request dir="rtl">';
        $out.='<input type="hidden" name="action" value="tn_ticket_submit"><input type="hidden" name="tn_request_kind" value="service">';
        $out.=wp_nonce_field('tn_ticket','_wpnonce',true,false);
        $out.='<p class="tn-qa-hp" aria-hidden="true"><label>خالی بگذارید <input name="tn_hp" tabindex="-1" autocomplete="off"></label></p>';
        $out.='<p><label>موضوع درخواست <select name="tn_service_context" required><option value="">خدمت یا نیاز خود را انتخاب کنید</option>';
        foreach(self::service_options()as$key=>$label){
            $out.='<option value="'.esc_attr($key).'"'.(($service['key']??'')===$key?' selected':'').'>'.esc_html($label).'</option>';
        }
        $out.='</select></label></p><div class="tn-request-contact">';
        $out.='<p><label>نام شما <input name="tn_name" autocomplete="name" minlength="2" maxlength="80" required></label></p>';
        $out.='<p><label>ایمیل برای پاسخ <input type="email" name="tn_email" dir="ltr" autocomplete="email" maxlength="120" required></label></p></div>';
        $out.='<p><label>نیاز یا مشکل شما <textarea name="tn_message" rows="4" minlength="10" maxlength="3000" placeholder="مثلاً: ارتباط بین دو بخش قطع می‌شود؛ بررسی اولیه می‌خواهیم." required></textarea></label></p>';
        $out.='<details><summary>اطلاعات سازمان (اختیاری)</summary><p><label>نام سازمان <input name="tn_company" autocomplete="organization" maxlength="120"></label></p></details>';
        $out.='<p class="tn-request-privacy">نام و ایمیل شما برای بررسی و پیگیری درخواست دریافت می‌شود. رمز، IP عمومی، آدرس دقیق یا فایل تنظیمات نفرستید. ارائهٔ خدمت، هزینه و پیش‌فاکتور پس از بررسی دامنه و توافق مشخص می‌شود.</p>';
        $out.='<button class="button button-primary" type="submit">ثبت درخواست و دریافت شماره پیگیری</button></form>';
        return $out;
    }

    /** The opaque, short-lived receipt exposes no contact or conversation data. */
    public function service_receipt_notice(): string {
        if(!isset($_GET['tn_service_receipt']))return '';
        $token=$_GET['tn_service_receipt'];
        $id=is_string($token)&&preg_match('/^[a-zA-Z0-9]{32}$/D',$token)?(int)get_transient('tn_service_receipt_'.$token):0;
        $post=$id?get_post($id):null;
        if(!$post||$post->post_type!==self::CPT||$post->post_status!=='private')return '<p class="tn-service-receipt" role="status">این رسید معتبر نیست یا مهلت نمایش آن پایان یافته است. اگر شماره پیگیری دارید، آن را در ارجاع تیکت بنویسید.</p>';
        $state=(string)get_post_meta($id,'_tn_ticket_state',true);
        $label=['open'=>'ثبت‌شده؛ در انتظار بررسی','answered'=>'پاسخ ثبت شده است','closed'=>'بسته‌شده'][$state]??'در انتظار بررسی';
        return '<section class="tn-service-receipt" role="status"><h2>درخواست شما ثبت شد</h2><p>شماره پیگیری: <strong dir="ltr">TN-'.esc_html((string)$id).'</strong></p><p>وضعیت: '.esc_html($label).'</p><p>این شماره را نگه دارید. رسید یک ساعت نمایش داده می‌شود و جزئیات خصوصی درخواست را نشان نمی‌دهد. برای پیگیری، شماره را در فیلد ارجاع تیکت وارد کنید. ثبت درخواست، رزرو زمان یا تأیید پیش‌فاکتور نیست.</p></section>';
    }

    public function protect_service_receipt(): void {
        if(!isset($_GET['tn_service_receipt']))return;
        nocache_headers();
        header('Referrer-Policy: no-referrer');
        header('X-Robots-Tag: noindex, nofollow');
    }

    public function submit(): void {
        check_admin_referer('tn_ticket');
        $field=static fn(string $key):string => isset($_POST[$key])&&is_string($_POST[$key])?sanitize_textarea_field(wp_unslash($_POST[$key])):'';
        if ($field('tn_hp')!=='') { wp_die('اطلاعات تیکت نامعتبر است.',400); }
        if (!TehNet_Store_Policy::throttle('ticket',5,3600)) { wp_die('تعداد درخواست‌های شما زیاد است؛ کمی بعد دوباره تلاش کنید.',429); }
        $service=self::service_context($field('tn_service_context'));
        $is_service=$field('tn_request_kind')==='service';
        $company=$field('tn_company');
        if($is_service&&(!$service||mb_strlen($company)>120)){wp_die('خدمت معتبر را انتخاب کنید؛ نام سازمان باید حداکثر ۱۲۰ نویسه باشد.',400,['back_link'=>true]);}
        $valid=self::validate_ticket($field('tn_name'),$field('tn_email'),$is_service?$service['label']:$field('tn_subject'),$field('tn_message'),$field('tn_reference'));
        if (!$valid['ok']) { wp_die('نام، ایمیل معتبر و شرح حداقل ۱۰ نویسه‌ای نیاز را بررسی کنید و دوباره تلاش کنید.',400,['back_link'=>true]); }
        $id=wp_insert_post(['post_type'=>self::CPT,'post_status'=>'private','post_title'=>$valid['subject']],true);
        if (is_wp_error($id)||!$id) { wp_die('ثبت درخواست انجام نشد؛ کمی بعد دوباره تلاش کنید.',500,['back_link'=>true]); }
        update_post_meta($id,'_tn_name',$valid['name']);
        update_post_meta($id,'_tn_email',$valid['email']);
        update_post_meta($id,'_tn_message',$valid['message']);
        update_post_meta($id,'_tn_reference',$valid['reference']);
        if ($service) { update_post_meta($id,'_tn_service_context',$service['key']); }
        if($is_service){update_post_meta($id,'_tn_request_kind','service');if($company!=='')update_post_meta($id,'_tn_company',$company);}
        update_post_meta($id,'_tn_ticket_state','open');
        update_post_meta($id,'_tn_thread',[['who'=>'customer','at'=>gmdate('c'),'text'=>$valid['message']]]);
        if($is_service){
            $token=wp_generate_password(32,false,false);
            if(!set_transient('tn_service_receipt_'.$token,$id,HOUR_IN_SECONDS)){wp_die('درخواست ثبت شد. شماره پیگیری TN-'.(int)$id.' را برای پیگیری نگه دارید؛ نمایش رسید موقت در دسترس نیست.',503);}
            wp_safe_redirect(add_query_arg(['tn_ticket'=>'sent','tn_service_receipt'=>$token],get_permalink(get_page_by_path(self::PAGE_SLUG))));exit;
        }
        wp_safe_redirect(add_query_arg('tn_ticket','sent',get_permalink(get_page_by_path(self::PAGE_SLUG))));exit;
    }

    public function reply(): void {
        if (!current_user_can('tn_store_support')) { wp_die('دسترسی مجاز نیست.',403); }
        check_admin_referer('tn_ticket_reply');
        $post_id=absint($_POST['post_id']??0); $text=sanitize_textarea_field(wp_unslash($_POST['tn_reply']??'')); $close=sanitize_key($_POST['ticket_action']??'');
        $post=get_post($post_id);
        if (!$post || $post->post_type!==self::CPT) { wp_die('تیکت یافت نشد.',404); }
        if (mb_strlen($text)>=2 && mb_strlen($text)<=3000) {
            $thread=get_post_meta($post_id,'_tn_thread',true);
            $thread=is_array($thread)?$thread:[];
            $thread[]=['who'=>'agent','user'=>get_current_user_id(),'at'=>gmdate('c'),'text'=>$text];
            update_post_meta($post_id,'_tn_thread',$thread);
            update_post_meta($post_id,'_tn_ticket_state','answered');
            wp_mail((string)get_post_meta($post_id,'_tn_email',true),'پاسخ تیکت تهران نتورک',esc_html($text),['Content-Type: text/html; charset=UTF-8']);
        }
        if ($close==='close') { update_post_meta($post_id,'_tn_ticket_state','closed'); }
        wp_safe_redirect(add_query_arg(['page'=>'tn-store-tickets','tn_result'=>'ok'],admin_url('admin.php')));exit;
    }

    public function product_inquiry_form(): void {
        global $product;
        if (!$product instanceof WC_Product) { return; }
        echo '<section class="tn-inquiry" id="tn-inquiry" aria-labelledby="tn-inquiry-title"><h2 id="tn-inquiry-title">استعلام قیمت و موجودی این کالا</h2>';
        echo '<p>مدل، موجودی و قیمت این کالا پیش از ثبت سفارش با شما تطبیق داده می‌شود؛ پاسخ در ساعات کاری از طریق ایمیل ارسال می‌شود.</p>';
        echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'" class="tn-inquiry-form"><input type="hidden" name="action" value="tn_inquiry_submit"><input type="hidden" name="product_id" value="'.esc_attr($product->get_id()).'">';
        wp_nonce_field('tn_inquiry_'.$product->get_id());
        echo '<p class="tn-qa-hp" aria-hidden="true"><label>خالی بگذارید <input name="tn_hp" tabindex="-1" autocomplete="off"></label></p>';
        echo '<p><label>نام شما <input name="tn_name" maxlength="80" required></label></p>';
        echo '<p><label>ایمیل <input type="email" name="tn_email" maxlength="120" required></label></p>';
        echo '<p><label>مقدار موردنیاز (مثلاً ۲.۵ متر یا ۳ عدد) <input name="tn_qty" maxlength="60" required></label></p>';
        echo '<p><label>توضیح (اختیاری) <textarea name="tn_notes" maxlength="1000"></textarea></label></p>';
        echo '<p><button class="button button-primary" type="submit">ثبت استعلام</button></p>';
        if (isset($_GET['tn_inquiry']) && $_GET['tn_inquiry']==='sent') { echo '<p role="status" class="tn-qa-notice">استعلام شما ثبت شد؛ نتیجه از طریق ایمیل اعلام می‌شود.</p>'; }
        echo '</form></section>';
    }
    public function submit_inquiry(): void {
        $raw=$_POST['product_id']??null;
        $product=is_scalar($raw)?wc_get_product(absint($raw)):false;
        if (!$product instanceof WC_Product) { wp_die('کالا در دسترس نیست.',404); }
        check_admin_referer('tn_inquiry_'.$product->get_id());
        $field=static fn(string $key):string => isset($_POST[$key])&&is_string($_POST[$key])?sanitize_textarea_field(wp_unslash($_POST[$key])):'';
        if ($field('tn_hp')!=='') { wp_die('اطلاعات استعلام نامعتبر است.',400); }
        if (!TehNet_Store_Policy::throttle('inquiry',5,3600)) { wp_die('تعداد درخواست‌های شما زیاد است؛ کمی بعد دوباره تلاش کنید.',429); }
        $qty=$field('tn_qty'); $notes=$field('tn_notes');
        $message='مقدار: '.$qty.' | کالا: '.$product->get_name().($notes!==''?' | توضیح: '.$notes:'');
        $valid=self::validate_ticket($field('tn_name'),$field('tn_email'),'استعلام قیمت — '.($product->get_sku()?:$product->get_id()),$message,$product->get_sku()?:'');
        if (!$valid['ok']) { wp_die('اطلاعات استعلام نامعتبر است.',400); }
        $id=wp_insert_post(['post_type'=>self::CPT,'post_status'=>'private','post_title'=>$valid['subject']],true);
        if (is_wp_error($id)) { wp_die('ثبت استعلام انجام نشد.',500); }
        update_post_meta($id,'_tn_name',$valid['name']);
        update_post_meta($id,'_tn_email',$valid['email']);
        update_post_meta($id,'_tn_message',$valid['message']);
        update_post_meta($id,'_tn_reference',$valid['reference']);
        update_post_meta($id,'_tn_ticket_state','open');
        update_post_meta($id,'_tn_inquiry_product',$product->get_id());
        update_post_meta($id,'_tn_thread',[['who'=>'customer','at'=>gmdate('c'),'text'=>$valid['message']]]);
        wp_safe_redirect(add_query_arg('tn_inquiry','sent',$product->get_permalink().'#tn-inquiry'));exit;
    }
    public function admin_page(): void {
        if (!current_user_can('tn_store_operations_view')) { wp_die('دسترسی مجاز نیست.',403); }
        echo '<div class="wrap" dir="rtl"><h1>تیکت‌های پشتیبانی</h1>';
        echo '<p>پاسخ‌ها ذخیره و (پس از پیکربندی ایمیل) برای مشتری ارسال می‌شوند. پل تلگرام به توکن ربات مالک وابسته است و جداگانه فعال می‌شود.</p>';
        $query=new WP_Query(['post_type'=>self::CPT,'post_status'=>'private','posts_per_page'=>50]);
        if (!$query->have_posts()) { echo '<p>تیکتی ثبت نشده است.</p></div>'; return; }
        while ($query->have_posts()) {
            $query->the_post(); $t=get_post();
            $state=(string)get_post_meta($t->ID,'_tn_ticket_state',true);
            echo '<details class="tn-ticket" '.($state==='open'?'open':'').'><summary>'.esc_html($t->post_title).' — '.esc_html((string)get_post_meta($t->ID,'_tn_name',true)).' ['.esc_html($state).']</summary>';
            $context=self::service_context(get_post_meta($t->ID,'_tn_service_context',true));
            echo '<p>شماره پیگیری: <bdi>TN-'.esc_html((string)$t->ID).'</bdi>'.($context?' | خدمت: '.esc_html($context['label']):'').'</p>';
            $company=(string)get_post_meta($t->ID,'_tn_company',true);if($company!=='')echo '<p>سازمان: '.esc_html($company).'</p>';
            echo '<p><bdi>'.esc_html((string)get_post_meta($t->ID,'_tn_email',true)).'</bdi>'.((string)get_post_meta($t->ID,'_tn_reference',true)!=='?'&&get_post_meta($t->ID,'_tn_reference',true)?' — ارجاع: <bdi>'.esc_html((string)get_post_meta($t->ID,'_tn_reference',true)).'</bdi>':'').'</p>';
            $thread=get_post_meta($t->ID,'_tn_thread',true);
            if (is_array($thread)) { foreach ($thread as $entry) { echo '<blockquote><b>'.esc_html($entry['who']==='agent'?'کارشناس':'مشتری').'</b> ('.esc_html((string)$entry['at']).'):<br>'.nl2br(esc_html((string)$entry['text'])).'</blockquote>'; } }
            echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field('tn_ticket_reply');
            echo '<input type="hidden" name="action" value="tn_ticket_reply"><input type="hidden" name="post_id" value="'.esc_attr($t->ID).'">';
            echo '<textarea name="tn_reply" maxlength="3000" placeholder="پاسخ" required></textarea> ';
            echo '<button class="button button-primary" name="ticket_action" value="reply">ارسال پاسخ</button> ';
            echo '<button class="button" name="ticket_action" value="close">بستن تیکت</button></form></details>';
        }
        wp_reset_postdata();
        echo '</div>';
    }
}
