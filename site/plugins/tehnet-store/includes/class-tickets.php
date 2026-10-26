<?php
defined('ABSPATH') || exit;

/** Support tickets. Reply delivery to customers depends on a configured mail sender; Telegram bridge stays a separate token-gated feature. */
final class TehNet_Store_Tickets {
    public const CPT='tn_ticket';
    private const PAGE_SLUG='support';
    public const STATES=['open','answered','closed'];

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
        add_action('admin_post_tn_ticket_submit',[$this,'submit']);
        add_action('admin_post_nopriv_tn_ticket_submit',[$this,'submit']);
        add_action('admin_post_tn_ticket_reply',[$this,'reply']);
        add_action('admin_menu',function():void { add_submenu_page('tn-store','تیکت‌های پشتیبانی','تیکت‌ها','tn_store_operations_view','tn-store-tickets',[$this,'admin_page']); });
    }

    public function shortcode(): string {
        $out='<form method="post" action="'.esc_url(admin_url('admin-post.php')).'" class="tn-ticket-form" dir="rtl"><input type="hidden" name="action" value="tn_ticket_submit">';
        wp_nonce_field('tn_ticket');
        $out.='<p class="tn-qa-hp" aria-hidden="true"><label>خالی بگذارید <input name="tn_hp" tabindex="-1" autocomplete="off"></label></p>';
        $out.='<p><label>نام شما <input name="tn_name" maxlength="80" required></label></p>';
        $out.='<p><label>ایمیل <input type="email" name="tn_email" maxlength="120" required></label></p>';
        $out.='<p><label>موضوع <input name="tn_subject" maxlength="140" required></label></p>';
        $out.='<p><label>ارجاع (اختیاری: شماره سفارش/پیش‌فاکتور یا کد کالا) <input name="tn_reference" maxlength="80"></label></p>';
        $out.='<p><label>شرح مشکل <textarea name="tn_message" maxlength="3000" required></textarea></label></p>';
        $out.='<p><button class="button button-primary" type="submit">ثبت تیکت</button></p></form>';
        return $out;
    }

    public function submit(): void {
        check_admin_referer('tn_ticket');
        $field=static fn(string $key):string => isset($_POST[$key])&&is_string($_POST[$key])?sanitize_textarea_field(wp_unslash($_POST[$key])):'';
        if ($field('tn_hp')!=='') { wp_die('اطلاعات تیکت نامعتبر است.',400); }
        if (!TehNet_Store_Policy::throttle('ticket',5,3600)) { wp_die('تعداد درخواست‌های شما زیاد است؛ کمی بعد دوباره تلاش کنید.',429); }
        $valid=self::validate_ticket($field('tn_name'),$field('tn_email'),$field('tn_subject'),$field('tn_message'),$field('tn_reference'));
        if (!$valid['ok']) { wp_die('اطلاعات تیکت نامعتبر است.',400); }
        $id=wp_insert_post(['post_type'=>self::CPT,'post_status'=>'private','post_title'=>$valid['subject']],true);
        if (is_wp_error($id)) { wp_die('ثبت تیکت انجام نشد.',500); }
        update_post_meta($id,'_tn_name',$valid['name']);
        update_post_meta($id,'_tn_email',$valid['email']);
        update_post_meta($id,'_tn_message',$valid['message']);
        update_post_meta($id,'_tn_reference',$valid['reference']);
        update_post_meta($id,'_tn_ticket_state','open');
        update_post_meta($id,'_tn_thread',[['who'=>'customer','at'=>gmdate('c'),'text'=>$valid['message']]]);
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
