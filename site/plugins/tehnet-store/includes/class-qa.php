<?php
defined('ABSPATH') || exit;

/** Public product Q&A and inquiry feedback. Submissions start pending and never auto-publish. */
final class TehNet_Store_QA {
    public const Q_CPT='tn_question';
    public const F_CPT='tn_feedback';

    public static function install(): void {
        foreach ([self::Q_CPT=>['پرسش کالا','پرسش‌های کالا'],self::F_CPT=>['بازخورد استعلام','بازخوردهای استعلام']] as $cpt=>$labels) {
            register_post_type($cpt,['labels'=>['name'=>$labels[1],'singular_name'=>$labels[0]],'public'=>false,'show_ui'=>false,
                'supports'=>['title','editor'],'capability_type'=>'post','capabilities'=>['create_posts'=>'do_not_allow'],'map_meta_cap'=>true]);
        }
    }

    /** Pure validation shared by the form handlers and tests. */
    public static function validate_question(string $name,string $body,string $honeypot): array {
        $errors=[];
        if ($honeypot!=='') { $errors[]='spam'; }
        $name=trim($name); $body=trim($body);
        if (mb_strlen($name)<2 || mb_strlen($name)>80) { $errors[]='name'; }
        if (mb_strlen($body)<5 || mb_strlen($body)>1000) { $errors[]='body'; }
        return $errors===[] ? ['ok'=>true,'name'=>$name,'body'=>$body] : ['ok'=>false,'errors'=>$errors];
    }

    public static function validate_feedback(int $rating,string $comment,string $email): array {
        $errors=[];
        if ($rating<1 || $rating>5) { $errors[]='rating'; }
        $comment=trim($comment);
        if (mb_strlen($comment)<3 || mb_strlen($comment)>500) { $errors[]='comment'; }
        if ($email!=='' && !filter_var($email,FILTER_VALIDATE_EMAIL)) { $errors[]='email'; }
        return $errors===[] ? ['ok'=>true,'rating'=>$rating,'comment'=>$comment,'email'=>$email] : ['ok'=>false,'errors'=>$errors];
    }

    public function register(): void {
        add_action('init',[self::class,'install']);
        add_action('woocommerce_after_single_product_summary',[$this,'product_section'],25);
        add_action('admin_post_tn_question_submit',[$this,'submit_question']);
        add_action('admin_post_nopriv_tn_question_submit',[$this,'submit_question']);
        add_action('admin_post_tn_feedback_submit',[$this,'submit_feedback']);
        add_action('admin_post_nopriv_tn_feedback_submit',[$this,'submit_feedback']);
        add_action('admin_post_tn_qa_moderate',[$this,'moderate']);
        add_action('admin_menu',function():void { add_submenu_page('tn-store','پرسش‌وپاسخ و بازخورد','پرسش‌وپاسخ','tn_store_operations_view','tn-store-qa',[$this,'admin_page']); });
    }

    public function product_section(): void {
        global $product;
        if (!$product instanceof WC_Product) { return; }
        $id=$product->get_id();
        $questions=get_posts(['post_type'=>self::Q_CPT,'post_status'=>'publish','posts_per_page'=>20,'meta_key'=>'_tn_product_id','meta_value'=>$id]);
        $notice='';
        if (isset($_GET['tn_qa']) && $_GET['tn_qa']==='sent') { $notice='پرسش شما ثبت شد؛ پس از بررسی کارشناسان منتشر می‌شود.'; }
        elseif (isset($_GET['tn_qa']) && $_GET['tn_qa']==='feedback') { $notice='بازخورد شما ثبت شد؛ سپاسگزاریم.'; }
        echo '<section class="tn-qa" aria-labelledby="tn-qa-title"><h2 id="tn-qa-title">پرسش‌وپاسخ کالا</h2>';
        if ($notice!=='') { echo '<p role="status" class="tn-qa-notice">'.esc_html($notice).'</p>'; }
        if ($questions) {
            echo '<dl class="tn-qa-list">';
            foreach ($questions as $question) {
                $answer=get_post_meta($question->ID,'_tn_answer',true);
                echo '<dt>'.esc_html($question->post_title).'</dt>';
                if (is_string($answer) && $answer!=='') { echo '<dd>'.esc_html($answer).'</dd>'; }
            }
            echo '</dl>';
        } else { echo '<p>هنوز پرسش منتشرشده‌ای برای این کالا نیست.</p>'; }
        echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'" class="tn-qa-form"><input type="hidden" name="action" value="tn_question_submit"><input type="hidden" name="product_id" value="'.esc_attr($id).'">';
        wp_nonce_field('tn_question_'.$id);
        echo '<p class="tn-qa-hp" aria-hidden="true"><label>خالی بگذارید <input name="tn_hp" tabindex="-1" autocomplete="off"></label></p>';
        echo '<p><label>نام شما <input name="tn_name" maxlength="80" required></label></p>';
        echo '<p><label>پرسش شما <textarea name="tn_body" maxlength="1000" required></textarea></label></p>';
        echo '<p><button class="button" type="submit">ثبت پرسش (پس از بررسی منتشر می‌شود)</button></p></form>';
        echo '<details class="tn-feedback"><summary>بازخورد استعلام این کالا</summary>';
        echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'"><input type="hidden" name="action" value="tn_feedback_submit"><input type="hidden" name="product_id" value="'.esc_attr($id).'">';
        wp_nonce_field('tn_feedback_'.$id);
        echo '<p class="tn-qa-hp" aria-hidden="true"><label>خالی بگذارید <input name="tn_hp" tabindex="-1" autocomplete="off"></label></p>';
        echo '<p><label>امتیاز پاسخ استعلام <select name="tn_rating"><option value="5">۵ — کامل</option><option value="4">۴</option><option value="3">۳</option><option value="2">۲</option><option value="1">۱ — ناقص</option></select></label></p>';
        echo '<p><label>توضیح <textarea name="tn_comment" maxlength="500" required></textarea></label></p>';
        echo '<p><label>ایمیل (اختیاری، برای پیگیری) <input type="email" name="tn_email" maxlength="120"></label></p>';
        echo '<p><button class="button" type="submit">ثبت بازخورد</button></p></form></details>';
        echo '</section>';
    }

    private function product_from_request(string $nonce_action): ?WC_Product {
        $raw=$_POST['product_id']??null;
        $product=is_scalar($raw)?wc_get_product(absint($raw)):false;
        if (!$product instanceof WC_Product) { wp_die('کالا در دسترس نیست.',404); }
        check_admin_referer($nonce_action.$product->get_id());
        return $product;
    }

    public function submit_question(): void {
        $product=$this->product_from_request('tn_question_');
        if (!TehNet_Store_Policy::throttle('qa',5,3600)) { wp_die('تعداد درخواست‌های شما زیاد است؛ کمی بعد دوباره تلاش کنید.',429); }
        $input=static fn(string $key):string => isset($_POST[$key])&&is_string($_POST[$key])?sanitize_textarea_field(wp_unslash($_POST[$key])):'';
        $valid=self::validate_question($input('tn_name'),$input('tn_body'),$input('tn_hp'));
        if (!$valid['ok']) { wp_die('اطلاعات پرسش نامعتبر است.',400); }
        $id=wp_insert_post(['post_type'=>self::Q_CPT,'post_status'=>'pending','post_title'=>$valid['name'],'post_content'=>$valid['body']],true);
        if (is_wp_error($id)) { wp_die('ثبت پرسش انجام نشد.',500); }
        update_post_meta($id,'_tn_product_id',$product->get_id());
        wp_safe_redirect(add_query_arg('tn_qa','sent',$product->get_permalink()));exit;
    }

    public function submit_feedback(): void {
        $product=$this->product_from_request('tn_feedback_');
        if (!TehNet_Store_Policy::throttle('feedback',5,3600)) { wp_die('تعداد درخواست‌های شما زیاد است؛ کمی بعد دوباره تلاش کنید.',429); }
        $input=static fn(string $key):string => isset($_POST[$key])&&is_string($_POST[$key])?sanitize_textarea_field(wp_unslash($_POST[$key])):'';
        $rating=isset($_POST['tn_rating'])?absint($_POST['tn_rating']):0;
        if ($input('tn_hp')!=='') { wp_die('اطلاعات بازخورد نامعتبر است.',400); }
        $valid=self::validate_feedback($rating,$input('tn_comment'),sanitize_email(wp_unslash($_POST['tn_email']??'')));
        if (!$valid['ok']) { wp_die('اطلاعات بازخورد نامعتبر است.',400); }
        $id=wp_insert_post(['post_type'=>self::F_CPT,'post_status'=>'private','post_title'=>'بازخورد '.$product->get_sku(),'post_content'=>$valid['comment']],true);
        if (is_wp_error($id)) { wp_die('ثبت بازخورد انجام نشد.',500); }
        update_post_meta($id,'_tn_product_id',$product->get_id());
        update_post_meta($id,'_tn_rating',$valid['rating']);
        if ($valid['email']!=='') { update_post_meta($id,'_tn_email',$valid['email']); }
        wp_safe_redirect(add_query_arg('tn_qa','feedback',$product->get_permalink()));exit;
    }

    public function moderate(): void {
        if (!current_user_can('tn_store_operations_view')) { wp_die('دسترسی مجاز نیست.',403); }
        check_admin_referer('tn_qa_moderate');
        $post_id=absint($_POST['post_id']??0); $action=sanitize_key($_POST['qa_action']??'');
        $post=get_post($post_id);
        if (!$post || !in_array($post->post_type,[self::Q_CPT,self::F_CPT],true)) { wp_die('مورد یافت نشد.',404); }
        if ($action==='approve') { wp_update_post(['ID'=>$post_id,'post_status'=>'publish']); }
        elseif ($action==='unapprove') { wp_update_post(['ID'=>$post_id,'post_status'=>'pending']); }
        elseif ($action==='answer' && isset($_POST['tn_answer'])&&is_string($_POST['tn_answer'])) {
            $answer=sanitize_textarea_field(wp_unslash($_POST['tn_answer']));
            if ($post->post_type===self::Q_CPT && mb_strlen($answer)>=2 && mb_strlen($answer)<=2000) { update_post_meta($post_id,'_tn_answer',$answer); wp_update_post(['ID'=>$post_id,'post_status'=>'publish']); }
        }
        elseif ($action==='trash') { wp_trash_post($post_id); }
        wp_safe_redirect(add_query_arg(['page'=>'tn-store-qa','tn_result'=>'ok'],admin_url('admin.php')));exit;
    }

    public function admin_page(): void {
        if (!current_user_can('tn_store_operations_view')) { wp_die('دسترسی مجاز نیست.',403); }
        echo '<div class="wrap" dir="rtl"><h1>پرسش‌وپاسخ و بازخورد استعلام</h1>';
        echo '<p>پرسش‌ها فقط پس از تأیید و پاسخ شما در صفحهٔ کالا منتشر می‌شوند. بازخوردها داخلی است و عمومی نمی‌شود.</p>';
        $query=new WP_Query(['post_type'=>self::Q_CPT,'post_status'=>['pending','publish'],'posts_per_page'=>50]);
        echo '<h2>پرسش‌ها</h2><table class="widefat striped"><thead><tr><th>کالا</th><th>پرسش</th><th>وضعیت</th><th>پاسخ/اقدام</th></tr></thead><tbody>';
        while ($query->have_posts()) { $query->the_post(); $q=get_post(); $pid=(int)get_post_meta($q->ID,'_tn_product_id',true); $product=wc_get_product($pid);
            echo '<tr><td>'.esc_html($product?($product->get_name()):'#'.$pid).'</td><td><b>'.esc_html($q->post_title).'</b><br>'.esc_html($q->post_content).'</td><td>'.esc_html($q->post_status==='publish'?'منتشرشده':'در انتظار').'</td><td>';
            echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field('tn_qa_moderate');
            echo '<input type="hidden" name="action" value="tn_qa_moderate"><input type="hidden" name="post_id" value="'.esc_attr($q->ID).'">';
            echo '<textarea name="tn_answer" placeholder="پاسخ" maxlength="2000">'.esc_textarea((string)get_post_meta($q->ID,'_tn_answer',true)).'</textarea> ';
            echo '<button class="button" name="qa_action" value="answer">ذخیره پاسخ و انتشار</button> ';
            if ($q->post_status==='publish') { echo '<button class="button" name="qa_action" value="unapprove">لغو انتشار</button> '; }
            echo '<button class="button" name="qa_action" value="trash">حذف</button></form></td></tr>';
        }
        wp_reset_postdata();
        echo '</tbody></table><h2>بازخوردهای استعلام</h2>';
        $feedback=new WP_Query(['post_type'=>self::F_CPT,'post_status'=>'private','posts_per_page'=>50]);
        if ($feedback->have_posts()) {
            echo '<table class="widefat striped"><thead><tr><th>کالا</th><th>امتیاز</th><th>توضیح</th></tr></thead><tbody>';
            while ($feedback->have_posts()) { $feedback->the_post(); $f=get_post(); $pid=(int)get_post_meta($f->ID,'_tn_product_id',true); $product=wc_get_product($pid);
                echo '<tr><td>'.esc_html($product?$product->get_name():'#'.$pid).'</td><td>'.(int)get_post_meta($f->ID,'_tn_rating',true).'/۵</td><td>'.esc_html($f->post_content).'</td></tr>';
            }
            wp_reset_postdata();
            echo '</tbody></table>';
        } else { echo '<p>بازخوردی ثبت نشده است.</p>'; }
        echo '</div>';
    }
}
