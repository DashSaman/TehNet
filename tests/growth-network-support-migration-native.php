<?php
/** Owned staging only. Actual WordPress/database acceptance, not a production runner. */
if (wp_get_environment_type() !== 'staging' || home_url('/') !== 'http://localhost:18085/' || !WP_HTTP_BLOCK_EXTERNAL || !DISABLE_WP_CRON || (string)get_option('blog_public') !== '0') {
    throw new RuntimeException('Independently isolated native staging required');
}
define('TN_GROWTH_LIBRARY_ONLY', true);
require getenv('TN_TEST_MIGRATION');
// WP-CLI eval-file evaluates in method scope; helper functions need explicit globals.
global $template, $content, $directory, $checks;
$template = json_decode(file_get_contents(getenv('TN_TEST_MANIFEST')), true, 512, JSON_THROW_ON_ERROR);
$content = file_get_contents(dirname(getenv('TN_TEST_MANIFEST')) . '/network-support.html');
$directory = getenv('TN_TEST_DIRECTORY');
if (!is_dir($directory) || (fileperms($directory) & 0077) !== 0) { throw new RuntimeException('Private test evidence directory required'); }
$checks = 0;
function expect(bool $condition, string $label): void {
    global $checks;
    if (!$condition) { throw new RuntimeException('FAIL: ' . $label); }
    ++$checks; echo 'PASS: ' . $label . "\n";
}
function state(): array {
    global $wpdb;
    $rows = [];
    foreach (['posts','postmeta','users','usermeta'] as $name) {
        $key = $name === 'postmeta' ? 'meta_id' : ($name === 'usermeta' ? 'umeta_id' : 'ID');
        $rows[$name] = $wpdb->get_results("SELECT * FROM {$wpdb->$name} ORDER BY $key", ARRAY_A);
    }
    return $rows;
}
function attempt(string $name, array $manifest): TehNet_Growth_Content_Migration {
    global $directory, $content;
    if (!is_string($directory) || !str_starts_with($directory, '/tmp/tn-editorial-native-') || basename($directory) !== 'evidence') { throw new RuntimeException('Owned attempt root required'); }
    $root = $directory . '/' . $name;
    if (!mkdir($root, 0700) || !mkdir($root . '/journal', 0700)) { throw new RuntimeException('New owned attempt directory required'); }
    file_put_contents($root . '/network-support.html', $content);
    file_put_contents($root . '/manifest.json', json_encode($manifest, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES));
    return new TehNet_Growth_Content_Migration($root . '/manifest.json', hash_file('sha256', $root . '/manifest.json'), $root . '/journal');
}
function refused(callable $action, string $label): void {
    try { $action(); } catch (Throwable $error) { expect(true, $label); return; }
    throw new RuntimeException('FAIL: did not refuse ' . $label);
}
$before = state();
expect(TehNet_Growth_Content_Migration::authorizes('tehnet-service-network-support-20261101-v1', $template), 'Explicit service scope accepted by CLI entry gate');
expect(!TehNet_Growth_Content_Migration::authorizes('tehnet-editorial-routing-20261101-v1', $template), 'Other scope cannot authorize this manifest');
expect(!TehNet_Growth_Content_Migration::authorizes(false, $template), 'Missing authorization marker refused');
expect(!TehNet_Growth_Content_Migration::authorizes('arbitrary', ['key'=>'arbitrary']), 'Unknown scope marker refused');
foreach (['tehnet-growth-20261031-v1','tehnet-editorial-routeros-20261101-v1','tehnet-editorial-routing-20261101-v1'] as $scope) {
    expect(TehNet_Growth_Content_Migration::authorizes($scope, ['key'=>$scope]), 'Earlier explicit CLI scope remains accepted');
}
$post = get_post(31);
if (!$post || $post->post_type !== 'page' || get_page_uri($post) !== 'services/network-support-tehran') { throw new RuntimeException('Original service page identity required'); }
$template['target']['expected_content_sha256'] = hash('sha256', $post->post_content);
$template['target']['title_observed'] = $post->post_title;
$originalPost = (array)$post;
$originalMeta = get_post_meta(31);
$revisionRows = wp_get_post_revisions(31);
$retention = static fn() => 0;
add_filter('wp_revisions_to_keep', $retention, 10);
$migration = attempt('success', $template);
$ready = $migration->run('check');
expect($ready['status'] === 'READY' && $ready['pages_pending'] === 0 && $ready['hubs_pending'] === 1, 'Exactly one existing service page pending');
expect(state() === $before, 'Preflight changes no records');
$result = $migration->run('apply');
expect($result['status'] === 'APPLIED' && $result['pages_created'] === 0 && $result['hubs_updated'] === 1, 'One body updated, no page created');
expect(get_post(31)->post_content === $content, 'Exact immutable body stored');
expect(get_post(31)->post_title === $post->post_title && get_post(31)->post_name === $post->post_name && (int)get_post(31)->post_parent === (int)$post->post_parent, 'Title slug parent preserved');
expect(get_post_meta(31) === $originalMeta, 'All service page meta preserved');
expect(abs(time() - strtotime(get_post(31)->post_modified_gmt . ' UTC')) < 30, 'Actual modification timestamp recorded');
foreach ($revisionRows as $id => $revision) { expect((array)get_post($id) === (array)$revision, 'Preexisting revision retained'); }
$after = state();
$repeat = $migration->run('apply');
expect($repeat['pages_created'] === 0 && $repeat['hubs_updated'] === 0 && state() === $after, 'Repeat is record-idempotent');
global $wpdb;
$wpdb->update($wpdb->posts, ['post_content' => $content . "\nTNQA-owned-drift"], ['ID' => 31]); clean_post_cache(31);
refused(fn() => $migration->run('rollback'), 'Rollback preserves a later service page edit');
expect(str_ends_with(get_post(31)->post_content, 'TNQA-owned-drift'), 'Foreign-edit sentinel not overwritten');
$wpdb->update($wpdb->posts, ['post_content' => $content], ['ID' => 31]); clean_post_cache(31);
$rolled = $migration->run('rollback');
expect($rolled['status'] === 'ROLLED_BACK' && $rolled['hubs_restored'] === 1 && $rolled['pages_drafted'] === 0, 'Rollback restores only existing service page');
expect(state() === $before, 'All original posts meta users and revisions exactly restored');
expect($migration->run('rollback')['status'] === 'ROLLED_BACK' && state() === $before, 'Rollback repeat is idempotent');
refused(fn() => $migration->run('apply'), 'Rolled-back journal cannot be reused');
foreach (['id'=>63,'url'=>'https://tehnet.ir/learn/wrong/','title_observed'=>'TNQA wrong identity'] as $key => $value) {
    $bad = $template; $bad['target'][$key] = $value;
    refused(fn() => attempt('bad-' . $key, $bad), 'Unapproved target ' . $key . ' refused');
}
$bad = $template; $bad['key'] = 'tehnet-editorial-routing-20261101-v1';
refused(fn() => attempt('cross-scope', $bad), 'Other approved scope cannot adopt page31');
$bad = $template; $bad['key'] = 'tehnet-editorial-arbitrary-v1';
refused(fn() => attempt('unknown-scope', $bad), 'Unregistered scope refused');
$bad = $template; $bad['content_sha256_lf'] = str_repeat('0',64);
refused(fn() => attempt('bad-content-digest', $bad), 'Body digest drift refused');
$bad = $template; $bad['target']['change_fields'][] = 'post_title';
refused(fn() => attempt('bad-fields', $bad), 'Wider field scope refused');
$bad = $template; $bad['content_file'] = '../network-support.html';
refused(fn() => attempt('bad-path', $bad), 'Body path escape refused');
$bad = $template; $bad['target']['expected_content_sha256'] = str_repeat('0',64);
refused(fn() => attempt('bad-baseline', $bad)->run('apply'), 'Changed baseline refused');
expect(state() === $before, 'Negative manifest cases change no records');
$injected = false;
$metaHook = static function() use (&$injected): void { $injected = true; update_post_meta(31, '_tnqa_unapproved_hook', 'owned-test-only'); };
add_action('save_post_page', $metaHook, 50);
try { refused(fn() => attempt('hook-field-drift', $template)->run('apply'), 'Hook cannot change service page metadata'); }
finally { remove_action('save_post_page', $metaHook, 50); }
expect($injected && state() === $before, 'Rejected hook side effect transaction rolled back');
$locked = false;
$concurrent = static function() use (&$locked): void {
    global $wpdb;
    $other = new wpdb(DB_USER, DB_PASSWORD, DB_NAME, DB_HOST); $other->suppress_errors(true);
    $other->query('SET SESSION innodb_lock_wait_timeout=1');
    $r = $other->update($wpdb->posts, ['post_content' => 'TNQA concurrent'], ['ID' => 31]);
    $locked = $r === false && str_contains(strtolower($other->last_error), 'lock wait timeout');
    $other->close();
};
add_action('save_post_page', $concurrent, 50);
$locking = attempt('row-lock', $template);
try { $locking->run('apply'); expect($locked, 'Second database writer blocked by managed row lock'); }
finally { remove_action('save_post_page', $concurrent, 50); $locking->run('rollback'); }
expect(state() === $before, 'Concurrent-writer case fully restored');
remove_filter('wp_revisions_to_keep', $retention, 10);
echo 'EDITORIAL_MIGRATION=PASS checks=' . $checks . "\n";
