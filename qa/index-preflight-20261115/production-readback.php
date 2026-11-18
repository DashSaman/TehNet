<?php
/**
 * TN-INDEX-PREFLIGHT-20261115 production readback — STRICTLY READ-ONLY.
 * Purpose: verify ACTUAL production page IDs/permalinks for the allowlist before
 * proposing any environment-aware binding (manager boundary: staging IDs must not
 * overwrite guarded production maps). Reads only; writes nothing.
 */
if (!defined('ABSPATH') || !defined('WP_CLI') || !WP_CLI) { throw new RuntimeException('Existing WordPress CLI context required'); }
$paths = ['/', '/services/', '/services/voice-network-readiness/', '/services/remote-support/',
 '/services/mikrotik-tehran/', '/services/network-setup-tehran/', '/services/network-support-tehran/',
 '/services/network-tehran/', '/about/', '/contact/', '/technical-methodology/'];
$out = [
 'schema' => 1,
 'mode' => 'READ_ONLY',
 'observed_utc' => gmdate('c'),
 'env' => wp_get_environment_type(),
 'home' => home_url('/'),
 'blog_public' => (string) get_option('blog_public', null),
 'wp_robots_noindex' => has_filter('wp_robots', 'wp_robots_noindex') !== false,
 'targets' => [],
];
foreach ($paths as $p) {
 $row = ['path' => $p];
 if ($p === '/') { $post = get_post((int) get_option('page_on_front')); }
 else { $post = get_page_by_path(trim($p, '/'), OBJECT, 'page'); }
 $row['found'] = $post ? true : false;
 if ($post) {
  $row['id'] = (int) $post->ID;
  $row['post_type'] = $post->post_type;
  $row['post_status'] = $post->post_status;
  $row['title'] = $post->post_title;
  $row['permalink'] = get_permalink($post);
  $row['content_sha256'] = hash('sha256', (string) $post->post_content);
  $row['excerpt_sha256'] = hash('sha256', (string) $post->post_excerpt);
  $row['growth_key'] = ($m = get_post_meta($post->ID, '_tn_growth_key', true)) !== '' ? $m : null;
 }
 $out['targets'][] = $row;
}
foreach ([206, 193] as $id) {
 $p = get_post($id);
 $out['direct_ids'][$id] = $p ? ['type' => $p->post_type, 'status' => $p->post_status,
  'path' => parse_url(get_permalink($p), PHP_URL_PATH), 'title' => mb_substr($p->post_title, 0, 50)]
  : ['missing' => true];
}
echo 'TNIDXPROD ' . wp_json_encode($out, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n";
