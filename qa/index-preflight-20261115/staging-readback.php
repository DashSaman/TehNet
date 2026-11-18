<?php
/**
 * TN-INDEX-PREFLIGHT-20261115 staging readback — STRICTLY READ-ONLY.
 * Invoked ONLY via the existing authorized staging WP-CLI (eval-file) over SSH.
 * Reads: options, page rows, permalinks, one meta key, content hashes. Writes: NOTHING.
 * No wp_mail, no HTTP, no transient/post/option writes, no blog_public change.
 */
if (!defined('ABSPATH') || !defined('WP_CLI') || !WP_CLI) { throw new RuntimeException('Existing WordPress CLI context required'); }

$fixed = ['/' => 5, '/services/' => 8, '/services/voice-network-readiness/' => 206, '/services/remote-support/' => 37,
 '/services/mikrotik-tehran/' => 35, '/services/network-setup-tehran/' => 33, '/services/network-support-tehran/' => 31,
 '/services/network-tehran/' => 29, '/about/' => 10, '/contact/' => 11, '/technical-methodology/' => 187];
$created = ['/network-support-contract-guide/' => 'A1', '/network-project-proposal-checklist/' => 'A2',
 '/business-server-planning-guide/' => 'A3', '/server-backup-restore-acceptance/' => 'A4', '/services/server-virtualization-tehran/' => 'N1'];

$out = [
 'schema' => 1,
 'mode' => 'READ_ONLY',
 'observed_utc' => gmdate('c'),
 'env' => wp_get_environment_type(),
 'home' => home_url('/'),
 'blog_public' => (string) get_option('blog_public', null),
 'wp_robots_noindex' => has_filter('wp_robots', 'wp_robots_noindex') !== false,
 'policy_option_present' => get_option('tn_index_policy_20261108', null) !== null,
 'runtime_class' => class_exists('TehNet_Core_Index_Policy'),
 'targets' => [],
];
foreach ($fixed as $p => $unused) { $paths[$p] = true; }
foreach ($created as $p => $k) { $paths[$p] = true; }
foreach ($paths as $p => $unused) {
 $row = ['path' => $p];
 if ($p === '/') { $post = get_post((int) get_option('page_on_front')); }
 else { $post = get_page_by_path(trim($p, '/'), OBJECT, 'page'); }
 $row['found'] = $post ? true : false;
 if ($post) {
  $row['id'] = (int) $post->ID;
  $row['post_type'] = $post->post_type;
  $row['post_status'] = $post->post_status;
  $row['has_password'] = $post->post_password !== '';
  $row['title'] = $post->post_title;
  $row['permalink'] = get_permalink($post);
  $row['content_sha256'] = hash('sha256', (string) $post->post_content);
  $row['excerpt_sha256'] = hash('sha256', (string) $post->post_excerpt);
  $row['growth_key'] = ($meta = get_post_meta($post->ID, '_tn_growth_key', true)) !== '' ? $meta : null;
 }
 $out['targets'][] = $row;
}
echo 'TNIDXPF ' . wp_json_encode($out, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n";
