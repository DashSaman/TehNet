<?php
// Invoke inside a running, isolated WordPress fixture after loading WooCommerce.
if (PHP_SAPI !== 'cli' || !defined('ABSPATH') || wp_get_environment_type() !== 'local') {
    throw new RuntimeException('Use a local WordPress CLI fixture.');
}
$roles = array_map('wc_get_page_id', ['cart', 'checkout', 'myaccount']);
if (min($roles) <= 0 || count(array_unique($roles)) !== 3) {
    throw new RuntimeException('Assign three different WooCommerce pages in the fixture.');
}
$other = max($roles) + 1;
$filter = static fn($args, $type) => apply_filters('wp_sitemaps_posts_query_args', $args, $type);
$cases = [
    [$filter(['post__in' => $roles], 'page')['post__in'], [0]],
    [$filter(['post__in' => [$roles[0], $other]], 'page')['post__in'], [$other]],
    [$filter(['post__not_in' => [$other]], 'page')['post__not_in'], array_merge([$other], $roles)],
    [$filter(['post__in' => $roles], 'post')['post__in'], $roles],
];
foreach ($cases as [$received, $expected]) {
    if ($received !== $expected) {
        throw new RuntimeException('Unexpected sitemap query.');
    }
}
echo "PASS: page roles, include lists, exclusions, posts\n";
