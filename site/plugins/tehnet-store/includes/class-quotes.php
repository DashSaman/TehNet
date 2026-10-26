<?php
defined('ABSPATH') || exit;

/** B2B quote-request portal. Requests are internal documents; sending a formal quote stays a manual, evidence-backed step. */
final class TehNet_Store_Quotes {
    public const CPT='tn_quote';
    private const PAGE_SLUG='b2b';

    public static function install(): void {
        register_post_type(self::CPT,['labels'=>['name'=>'درخواست پیش‌فاکتور B2B','singular_name'=>'درخواست پیش‌فاکتور'],'public'=>false,'show_ui'=>false,
            'supports'=>['title'],'capability_type'=>'post','capabilities'=>['create_posts'=>'do_not_allow'],'map_meta_cap'=>true]);
        if (!get_option('tn_b2b_page_created') && !get_page_by_path(self::PAGE_SLUG)) {
            $id=wp_insert_post(['post_type'=>'page','post_status'=>'publish','post_name'=>self::PAGE_SLUG,'post_title'=>'خرید سازمانی و پیش‌فاکتور','post_content'=>'<!-- wp:paragraph --><p>درخواست پیش‌فاکتور سازمانی تهران نتورک: اقلام را با مقدار مشخص کنید؛ کارشناسان قیمت، موجودی و زمان تأمین را بررسی و پیش‌فاکتور رسمی صادر می‌کنند.</p><!-- /wp:paragraph -->'."\n".'[tn_b2b_quote]']);
            if ($id && !is_wp_error($id)) { update_option('tn_b2b_page_created',true,false); }
        }
    }

    /** Pure validation for request intake. */
    public static function validate_request(string $company,string $contact,string $phone,string $email,array $items,string $notes=''): array {
        $errors=[];
        $company=trim($company); $contact=trim($contact); $phone=trim($phone); $email=trim($email); $notes=trim($notes);
        if (mb_strlen($company)<2 || mb_strlen($company)>120) { $errors[]='company'; }
        if (mb_strlen($contact)<2 || mb_strlen($contact)>80) { $errors[]='contact'; }
        if (!preg_match('/^[0-9+\-\s]{6,20}$/D',$phone)) { $errors[]='phone'; }
        if (!filter_var($email,FILTER_VALIDATE_EMAIL) || mb_strlen($email)>120) { $errors[]='email'; }
        if (mb_strlen($notes)>1000) { $errors[]='notes'; }
        if (count($items)<1 || count($items)>5) { $errors[]='items-count'; }
        $clean=[];
        foreach ($items as $item) {
            if (!is_array($item) || !isset($item['product_id'],$item['qty'])) { $errors[]='items'; continue; }
            $pid=(int)$item['product_id']; $qty=(string)$item['qty'];
            if ($pid<=0 || !preg_match('/^\d{1,6}(\.\d{1,2})?$/D',$qty) || (float)$qty<=0) { $errors[]='items'; continue; }
            $clean[]=['product_id'=>$pid,'qty'=>$qty];
        }
        if (count($clean)!==count($items)) { $errors[]='items'; }
        return $errors===[] ? ['ok'=>true,'company'=>$company,'contact'=>$contact,'phone'=>$phone,'email'=>$email,'items'=>$clean,'notes'=>$notes] : ['ok'=>false,'errors'=>array_unique($errors)];
    }

    public function register(): void {
        add_action('init',[self::class,'install']);
        add_shortcode('tn_b2b_quote',[$this,'shortcode']);
        add_action('admin_post_tn_quote_submit',[$this,'submit']);
        add_action('admin_post_nopriv_tn_quote_submit',[$this,'submit']);
        add_action('admin_post_tn_quote_state',[$this,'set_state']);
        add_action('admin_menu',function():void { add_submenu_page('tn-store','درخواست‌های سازمانی','سفارش سازمانی','tn_store_settle','tn-store-quotes',[$this,'admin_page']); });
    }

    public function shortcode(): string {
        $products=wc_get_products(['limit'=>60,'status'=>'publish','orderby'=>'title','order'=>'ASC']);
        $out='<form method="post" action="'.esc_url(admin_url('admin-post.php')).'" class="tn-quote-form" dir="rtl"><input type="hidden" name="action" value="tn_quote_submit">';
        wp_nonce_field('tn_quote');
        $out.='<p class="tn-qa-hp" aria-hidden="true"><label>خالی بگذارید <input name="tn_hp" tabindex="-1" autocomplete="off"></label></p>';
        $out.='<p><label>نام سازمان <input name="tn_company" maxlength="120" required></label></p>';
        $out.='<p><label>نام رابط <input name="tn_contact" maxlength="80" required></label></p>';
        $out.='<p><label>تلفن <input name="tn_phone" maxlength="20" required placeholder="021..."></label></p>';
        $out.='<p><label>ایمیل سازمانی <input type="email" name="tn_email" maxlength="120" required></label></p>';
        $out.='<h3>اقلام درخواستی (حداکثر ۵ قلم)</h3>';
        for ($i=1;$i<=5;$i++) {
            $out.='<p class="tn-quote-row"><label>کالا '.$i.' <select name="tn_item_product[]"><option value="">—</option>';
            foreach ($products as $product) { $out.='<option value="'.esc_attr($product->get_id()).'">'.esc_html($product->get_name()).' ('.esc_html($product->get_sku()).')</option>'; }
            $out.='</select></label> <label>مقدار <input name="tn_item_qty[]" inputmode="decimal" placeholder="مثلاً 2.5"></label></p>';
        }
        $out.='<p><label>توضیحات <textarea name="tn_notes" maxlength="1000"></textarea></label></p>';
        $out.='<p><button class="button button-primary" type="submit">ثبت درخواست پیش‌فاکتور</button></p></form>';
        return $out;
    }

    public function submit(): void {
        check_admin_referer('tn_quote');
        $field=static fn(string $key):string => isset($_POST[$key])&&is_string($_POST[$key])?sanitize_text_field(wp_unslash($_POST[$key])):'';
        $items=[]; $pids=$_POST['tn_item_product']??[]; $qtys=$_POST['tn_item_qty']??[];
        if (is_array($pids)&&is_array($qtys)) {
            foreach ($pids as $index=>$pid) {
                if (!is_scalar($pid) || !isset($qtys[$index]) || !is_scalar($qtys[$index]) || trim((string)$qtys[$index])==='') { continue; }
                $items[]=['product_id'=>absint($pid),'qty'=>sanitize_text_field(wp_unslash((string)$qtys[$index]))];
            }
        }
        $hp=$field('tn_hp');
        $valid=self::validate_request($field('tn_company'),$field('tn_contact'),$field('tn_phone'),$field('tn_email'),$items,$field('tn_notes'));
        if ($hp!=='' || !$valid['ok']) { wp_die('اطلاعات درخواست نامعتبر است.',400); }
        $id=wp_insert_post(['post_type'=>self::CPT,'post_status'=>'private','post_title'=>'B2B — '.$valid['company']],true);
        if (is_wp_error($id)) { wp_die('ثبت درخواست انجام نشد.',500); }
        update_post_meta($id,'_tn_company',$valid['company']);
        update_post_meta($id,'_tn_contact',$valid['contact']);
        update_post_meta($id,'_tn_phone',$valid['phone']);
        update_post_meta($id,'_tn_email',$valid['email']);
        update_post_meta($id,'_tn_items',$valid['items']);
        update_post_meta($id,'_tn_notes',$valid['notes']);
        update_post_meta($id,'_tn_quote_state','received');
        wp_safe_redirect(add_query_arg('tn_quote','sent',get_permalink(get_page_by_path(self::PAGE_SLUG))));exit;
    }

    public function set_state(): void {
        if (!current_user_can('tn_store_settle')) { wp_die('دسترسی مجاز نیست.',403); }
        check_admin_referer('tn_quote_state');
        $post_id=absint($_POST['post_id']??0); $state=sanitize_key($_POST['state']??''); $ref=sanitize_text_field(wp_unslash($_POST['quote_ref']??''));
        $post=get_post($post_id);
        if (!$post || $post->post_type!==self::CPT || !in_array($state,['received','quoted','won','lost'],true)) { wp_die('مورد نامعتبر است.',400); }
        update_post_meta($post_id,'_tn_quote_state',$state);
        if ($state==='quoted' && mb_strlen($ref)>=2 && mb_strlen($ref)<=60) { update_post_meta($post_id,'_tn_quote_ref',$ref); }
        wp_safe_redirect(add_query_arg(['page'=>'tn-store-quotes','tn_result'=>'ok'],admin_url('admin.php')));exit;
    }

    public function admin_page(): void {
        if (!current_user_can('tn_store_settle')) { wp_die('دسترسی مجاز نیست.',403); }
        echo '<div class="wrap" dir="rtl"><h1>درخواست‌های سازمانی (B2B)</h1>';
        echo '<p>پیش‌فاکتور رسمی با مدارک مالی صادر می‌شود؛ این صفحه وضعیت گردش کار را نگه می‌دارد.</p>';
        $query=new WP_Query(['post_type'=>self::CPT,'post_status'=>'private','posts_per_page'=>50]);
        if (!$query->have_posts()) { echo '<p>درخواستی ثبت نشده است.</p></div>'; return; }
        echo '<table class="widefat striped"><thead><tr><th>سازمان</th><th>رابط/تلفن</th><th>اقلام</th><th>وضعیت</th><th>اقدام</th></tr></thead><tbody>';
        while ($query->have_posts()) {
            $query->the_post(); $q=get_post(); $items=get_post_meta($q->ID,'_tn_items',true);
            echo '<tr><td><b>'.esc_html((string)get_post_meta($q->ID,'_tn_company',true)).'</b><br><bdi>'.esc_html((string)get_post_meta($q->ID,'_tn_email',true)).'</bdi></td>';
            echo '<td>'.esc_html((string)get_post_meta($q->ID,'_tn_contact',true)).'<br><bdi>'.esc_html((string)get_post_meta($q->ID,'_tn_phone',true)).'</bdi></td><td>';
            if (is_array($items)) {
                echo '<ul>';
                foreach ($items as $item) { $product=wc_get_product((int)$item['product_id']); echo '<li>'.esc_html($product?$product->get_name():'#'.$item['product_id']).' × '.esc_html((string)$item['qty']).'</li>'; }
                echo '</ul>';
            }
            echo '</td><td>'.esc_html((string)get_post_meta($q->ID,'_tn_quote_state',true)).'</td><td>';
            echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field('tn_quote_state');
            echo '<input type="hidden" name="action" value="tn_quote_state"><input type="hidden" name="post_id" value="'.esc_attr($q->ID).'">';
            echo '<input name="quote_ref" placeholder="شماره پیش‌فاکتور" maxlength="60" value="'.esc_attr((string)get_post_meta($q->ID,'_tn_quote_ref',true)).'"> ';
            foreach (['quoted'=>'پیش‌فاکتور صادر شد','won'=>'تأیید شد','lost'=>'منتفی','received'=>'بازگشت به دریافت‌شده'] as $value=>$label) { echo '<button class="button" name="state" value="'.$value.'">'.esc_html($label).'</button> '; }
            echo '</form></td></tr>';
        }
        wp_reset_postdata();
        echo '</tbody></table></div>';
    }
}
