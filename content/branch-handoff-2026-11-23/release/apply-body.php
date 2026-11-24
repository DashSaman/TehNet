<?php
// Invoke from the CLI, outside the web root, while holding the release locks.
if (PHP_SAPI !== 'cli' || $argc !== 5) {
    fwrite(STDERR, "Usage: php apply-body.php manifest.json private-body-directory path apply|revert\n");
    exit(2);
}
require (defined('ABSPATH') ? ABSPATH : '/var/www/html/') . 'wp-load.php';
[, $manifestFile, $directory, $path, $action] = $argv;
if (!in_array($action, ['apply', 'revert'], true)) {
    throw new RuntimeException('Unknown action');
}
$spec = json_decode(file_get_contents($manifestFile), true, 512, JSON_THROW_ON_ERROR)['bodies'][$path] ?? null;
if (!$spec) {
    throw new RuntimeException('Unknown page');
}
$from = $action === 'apply' ? 'before' : 'after';
$to = $action === 'apply' ? 'after' : 'before';
$payload = file_get_contents($directory . '/' . basename($path) . '.' . $to . '.html');
if ($payload === false || hash('sha256', $payload) !== $spec[$to]) {
    throw new RuntimeException('Invalid payload');
}
$fixture = wp_get_environment_type() === 'local' && DB_NAME === 'tn_training';
if (!$fixture && wp_parse_url(home_url(), PHP_URL_HOST) !== 'tehnet.ir') {
    throw new RuntimeException('Unexpected WordPress site');
}
$type = $spec['post_type'] ?? (str_contains($path, '/') ? 'page' : 'post');
if (!in_array($type, ['page', 'post'], true)) {
    throw new RuntimeException('Invalid body type');
}
$id = get_page_by_path($path, OBJECT, $type)->ID ?? 0;
if (!$id) {
    throw new RuntimeException('Missing page');
}
global $wpdb;
if ($wpdb->query('START TRANSACTION') === false) {
    throw new RuntimeException('Transaction unavailable');
}
try {
    $read = $wpdb->prepare("SELECT post_content FROM $wpdb->posts WHERE ID = %d AND post_status = 'publish' FOR UPDATE", $id);
    $current = $wpdb->get_var($read);
    if ($current === null) {
        throw new RuntimeException('Missing published body');
    }
    $hash = hash('sha256', $current);
    if ($hash !== $spec[$from] && $hash !== $spec[$to]) {
        throw new RuntimeException('Body changed; review the new version');
    }
    $changed = $hash !== $spec[$to];
    if ($changed) {
        clean_post_cache($id);
        $result = wp_update_post(['ID' => $id, 'post_content' => wp_slash($payload)], true);
        if (is_wp_error($result) || (int) $result !== (int) $id || $wpdb->get_var($read) !== $payload) {
            throw new RuntimeException('WordPress body verification failed');
        }
    }
    if ($wpdb->query('COMMIT') === false) {
        throw new RuntimeException('Commit failed; re-read the stored body');
    }
} catch (Throwable $e) {
    $wpdb->query('ROLLBACK');
    clean_post_cache($id);
    throw $e;
}
clean_post_cache($id);
echo json_encode(['path' => $path, 'action' => $action, 'changed' => $changed, 'sha256' => $spec[$to]]) . "\n";
