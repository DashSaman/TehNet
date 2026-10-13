<?php
/** CLI-only, narrow TehNet content deployment with concurrent-edit guards. */
if (PHP_SAPI !== 'cli') { http_response_code(403); exit; }
require '/var/www/html/wp-load.php';
$dir = '/tmp/tehnet-visual-release';
$mode = $argv[1] ?? 'check';
function fail_visual(string $message): void { fwrite(STDERR, $message . "\n"); exit(1); }
function visual_options(): array {
    $out = [];
    foreach (['blogname','blog_public','show_on_front','page_on_front','stylesheet','active_plugins','woocommerce_currency','woocommerce_cart_page_id','woocommerce_checkout_page_id','woocommerce_myaccount_page_id','woocommerce_bacs_settings','woocommerce_cheque_settings','woocommerce_cod_settings'] as $key) $out[$key] = get_option($key);
    return $out;
}
function protected_pages(int $home_id): array {
    $out = [];
    foreach (get_posts(['post_type'=>'page','post_status'=>'any','numberposts'=>-1,'exclude'=>[$home_id]]) as $p) {
        if ($p->post_name === 'amirreza-golavar') continue;
        $out[$p->ID] = hash('sha256', $p->post_title . $p->post_content . $p->post_status . $p->post_name . $p->post_parent);
    }
    ksort($out); return $out;
}
if (get_option('home') !== 'https://tehnet.ir' || (string)get_option('blog_public') !== '0') fail_visual('Unexpected site identity or indexing state.');
$home_id = (int)get_option('page_on_front');
$home = get_post($home_id);
$expected = trim(file_get_contents($dir . '/baseline-home.sha256'));
if ($mode === 'prepare') {
    if (get_page_by_path('amirreza-golavar', OBJECT, 'page')) fail_visual('Profile slug already exists; manual reconciliation required.');
    if (!$home || hash('sha256', $home->post_content) !== $expected) fail_visual('Homepage changed since baseline; no content overwritten.');
    $state = ['home_id'=>$home_id,'home_content'=>$home->post_content,'options'=>visual_options(),'protected_pages'=>protected_pages($home_id)];
    if (file_put_contents($dir . '/state-before.json', wp_json_encode($state, JSON_UNESCAPED_UNICODE)) === false) fail_visual('Cannot save content recovery state.');
    echo "CONTENT_PREFLIGHT=PASS\n"; exit;
}
$state = json_decode(file_get_contents($dir . '/state-before.json'), true, 512, JSON_THROW_ON_ERROR);
if ($mode === 'apply') {
    if (!$home || hash('sha256', $home->post_content) !== $expected) fail_visual('Homepage changed after preflight.');
    if (get_page_by_path('amirreza-golavar', OBJECT, 'page')) fail_visual('Profile slug occupied after preflight.');
    $owner = get_user_by('login', 'AmirrezaGol');
    if (!$owner) fail_visual('Expected site owner missing.');
    wp_set_current_user($owner->ID);
    if (!current_user_can('edit_pages') || !current_user_can('publish_pages') || !current_user_can('unfiltered_html')) fail_visual('Required content permissions missing.');
    $profile_content = file_get_contents($dir . '/content/pages/amirreza-golavar.html');
    $new_home = file_get_contents($dir . '/content/pages/home.html');
    $profile_id = wp_insert_post(wp_slash(['post_type'=>'page','post_status'=>'publish','post_title'=>'امیررضا گل‌آور | رزومه حرفه‌ای','post_name'=>'amirreza-golavar','post_content'=>$profile_content,'post_author'=>$owner->ID]), true);
    if (is_wp_error($profile_id)) fail_visual($profile_id->get_error_message());
    update_post_meta($profile_id, '_wp_page_template', 'page-portfolio.php');
    file_put_contents($dir . '/created-profile-id', (string)$profile_id);
    $result = wp_update_post(wp_slash(['ID'=>$home_id,'post_content'=>$new_home]), true);
    if (is_wp_error($result)) fail_visual($result->get_error_message());
    clean_post_cache($profile_id); clean_post_cache($home_id);
    if (hash('sha256', get_post($home_id)->post_content) !== hash('sha256', $new_home)) fail_visual('Home content persistence mismatch.');
    if (hash('sha256', get_post($profile_id)->post_content) !== hash('sha256', $profile_content)) fail_visual('Profile content persistence mismatch.');
    echo "PROFILE_ID=" . $profile_id . "\n";
}
if ($mode === 'rollback') {
    wp_update_post(wp_slash(['ID'=>$state['home_id'],'post_content'=>$state['home_content']]));
    if (is_file($dir . '/created-profile-id')) {
        $id = (int)file_get_contents($dir . '/created-profile-id');
        $p = get_post($id);
        if ($p && $p->post_name === 'amirreza-golavar') wp_update_post(['ID'=>$id,'post_status'=>'draft']);
    }
    echo "CONTENT_ROLLED_BACK\n"; exit;
}
if ($state['options'] !== visual_options()) fail_visual('Protected options changed.');
if ($state['protected_pages'] != protected_pages($home_id)) fail_visual('An unrelated page changed.');
echo "PROTECTED_OPTIONS_AND_PAGES=UNCHANGED\n";
