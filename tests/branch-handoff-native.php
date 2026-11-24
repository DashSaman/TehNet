<?php
define('WP_USE_THEMES', false);
define('WP_INSTALLING', true);
require '/var/www/html/wp-load.php';
require_once ABSPATH . 'wp-admin/includes/upgrade.php';

function check_branch_fixture(bool $condition, string $message): void {
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

check_branch_fixture(wp_get_environment_type() === 'local', 'Fixture requires local WordPress');
check_branch_fixture(DB_NAME === 'tehnet_branch_fixture', 'Fixture requires its disposable database');
check_branch_fixture(!is_blog_installed(), 'Fixture requires an empty installation');
add_filter('pre_wp_mail', '__return_true');
wp_install('TehNet branch fixture', 'fixture-operator', 'fixture@example.invalid', false, '', bin2hex(random_bytes(18)));
wp_installing(false);

$manifest = json_decode(file_get_contents('/tmp/branch-fixture/manifest.json'), true, 512, JSON_THROW_ON_ERROR);
$baseline = file_get_contents('/tmp/branch-fixture/base.html');
$fragment = file_get_contents('/tmp/branch-fixture/branch-handoff.html');
check_branch_fixture(hash('sha256', $baseline) === $manifest['expected_live_body_sha256'], 'Baseline mismatch');
check_branch_fixture(hash('sha256', $fragment) === $manifest['payload_sha256'], 'Candidate mismatch');
check_branch_fixture(substr_count($baseline, $manifest['after_heading']) === 1, 'Heading must resolve once');
check_branch_fixture(!str_contains($baseline, 'id="' . $manifest['fragment'] . '"'), 'Existing fragment must be absent');
$heading = strpos($baseline, $manifest['after_heading']);
$section = strpos($baseline, 'id="' . $manifest['anchor_before'] . '"');
$listStart = strpos($baseline, '<!-- wp:list', $heading);
$listEndMarker = '<!-- /wp:list -->';
$listEnd = strpos($baseline, $listEndMarker, $listStart);
check_branch_fixture($section !== false && $section < $heading && $listStart !== false && $listEnd !== false, 'Insertion section order');
$position = $listEnd + strlen($listEndMarker);
$insert = "\n\n" . trim($fragment);
$candidate = substr_replace($baseline, $insert, $position, 0);
check_branch_fixture(substr_replace($candidate, '', $position, strlen($insert)) === $baseline, 'Only exact addition allowed');

$blocks = array_values(array_filter(array_column(parse_blocks($fragment), 'blockName')));
check_branch_fixture($blocks === ['core/heading', 'core/paragraph', 'core/table', 'core/paragraph'], 'Unexpected WordPress block order');
$id = wp_insert_post(['post_type' => 'page', 'post_status' => 'publish', 'post_title' => 'Branch fixture', 'post_name' => 'branch-fixture', 'post_content' => wp_slash($baseline)], true);
check_branch_fixture(is_int($id), 'Synthetic page was not created');
check_branch_fixture(get_post($id)->post_content === $baseline, 'Synthetic baseline did not roundtrip');
$result = wp_update_post(['ID' => $id, 'post_content' => wp_slash($candidate)], true);
check_branch_fixture($result === $id && get_post($id)->post_content === $candidate, 'Candidate did not roundtrip');
$dom = new DOMDocument();
@$dom->loadHTML('<?xml encoding="UTF-8">' . do_blocks(get_post($id)->post_content));
$xp = new DOMXPath($dom);
$prefix = '//*[@id="' . $manifest['fragment'] . '"]';
check_branch_fixture($xp->query($prefix)->length === 1, 'Fragment must render once');
$table = $prefix . '/following-sibling::figure[1]/table';
check_branch_fixture($xp->query($table . '/thead/tr/th')->length === 2, 'Expected two column headers');
check_branch_fixture($xp->query($table . '/tbody/tr')->length === 4, 'Expected four acceptance rows');
$domain = $xp->query($table . '/tbody/tr[3]')->item(0)->textContent;
foreach (['کنترل‌کنندهٔ دامنه', 'احراز هویت تازه', 'آزموده‌نشده'] as $expected) {
    check_branch_fixture(str_contains($domain, $expected), 'Domain acceptance evidence incomplete');
}
check_branch_fixture(get_post($id)->post_title === 'Branch fixture' && get_post($id)->post_name === 'branch-fixture' && get_post($id)->post_status === 'publish', 'Synthetic page metadata changed');
check_branch_fixture(wp_update_post(['ID' => $id, 'post_content' => wp_slash($baseline)], true) === $id && get_post($id)->post_content === $baseline, 'Exact body rollback failed');
echo json_encode(['wp' => get_bloginfo('version'), 'baseline_sha256' => hash('sha256', $baseline), 'candidate_sha256' => hash('sha256', $candidate), 'payload_sha256' => hash('sha256', $fragment), 'checks' => 'save-render-restore', 'rows' => 4, 'rollback_body_exact' => true], JSON_THROW_ON_ERROR) . PHP_EOL;
