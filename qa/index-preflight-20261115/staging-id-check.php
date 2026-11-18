<?php
/**
 * TN-INDEX-PREFLIGHT-20261115 id-drift probe — STRICTLY READ-ONLY.
 * Clarifies voice-network-readiness identity: manifest expects id 206, staging resolves 193.
 */
if (!defined('ABSPATH') || !defined('WP_CLI') || !WP_CLI) { throw new RuntimeException('Existing WordPress CLI context required'); }
foreach ([206, 193] as $id) {
	$p = get_post($id);
	$r = $p ? ['id' => $id, 'type' => $p->post_type, 'status' => $p->post_status,
		'path' => parse_url(get_permalink($p), PHP_URL_PATH), 'title' => mb_substr($p->post_title, 0, 40),
		'modified' => $p->post_modified, 'excerpt_len' => strlen((string) $p->post_excerpt)]
		: ['id' => $id, 'missing' => true];
	echo 'TNROW ' . wp_json_encode($r, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n";
}
$q = new WP_Query(['post_type' => 'page', 'post_status' => 'any', 'name' => 'voice-network-readiness', 'posts_per_page' => 5]);
$ids = [];
foreach ($q->posts as $p) { $ids[] = ['id' => (int) $p->ID, 'status' => $p->post_status]; }
echo 'TNQ ' . wp_json_encode(['slug_matches' => $ids], JSON_UNESCAPED_SLASHES) . "\n";
