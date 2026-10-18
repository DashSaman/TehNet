<?php
/** Read-only exact-media inventory. Invoke with authorized native WP-CLI. */
if (!defined('WP_CLI') || !WP_CLI || !current_user_can('manage_options') || home_url('/') !== 'https://tehnet.ir/') {
    throw new RuntimeException('Authorized production TehNet CLI required');
}
$products = [];
$keys = ['_tn_verified_mpn', '_tn_identity_source', '_tn_identity_reviewed',
    '_tn_model_mpn', '_tn_model_attachment_id', '_tn_model_source', '_tn_model_rights',
    '_tn_model_reviewed', '_tn_model_sha256', '_tn_parts_reviewed',
    '_tn_parts_model_sha256', '_tn_spin_rights', '_tn_spin_reviewed'];
foreach (get_posts(['post_type' => 'product', 'post_status' => 'publish', 'numberposts' => -1, 'orderby' => 'ID', 'order' => 'ASC']) as $post) {
    $product = wc_get_product($post->ID);
    $fields = [];
    foreach ($keys as $key) $fields[$key] = $product->get_meta($key);
    $meta = get_post_meta($post->ID);
    ksort($meta);
    $model = (new TehNet_Store_Product_Evidence())->model($product);
    $spin = (new TehNet_Store_Product_Visuals())->spin_frames($product);
    $products[] = [
        'id' => $post->ID, 'sku' => $product->get_sku(),
        'evidence_fields' => $fields,
        'body_sha256' => hash('sha256', wp_json_encode([$post->post_title, $post->post_content, $post->post_excerpt, $post->post_status])),
        'all_meta_sha256' => hash('sha256', wp_json_encode($meta)),
        'image_ids' => array_values(array_filter(array_merge([$product->get_image_id()], $product->get_gallery_image_ids()))),
        'model_available' => (bool)$model, 'parts_available' => !empty($model['parts']),
        'spin_frame_count' => count($spin), 'purchasable' => $product->is_purchasable(),
    ];
}
echo wp_json_encode(['schema' => 1, 'observed_utc' => gmdate('c'), 'site' => home_url('/'),
    'mode' => 'read-only', 'blog_public' => get_option('blog_public'), 'products' => $products]);
