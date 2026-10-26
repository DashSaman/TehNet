<?php
/** Standalone contract tests for TehNet_Store_Storefront::sanitize_wishlist. No WordPress loaded. */
if (!function_exists('wp_parse_url')) {
    function wp_parse_url($url, $component = -1) { return parse_url($url, $component); }
}
define('ABSPATH', __DIR__ . '/');
require __DIR__ . '/../site/plugins/tehnet-store/includes/class-storefront.php';
$count = 0;
function check(bool $ok, string $label): void {
    global $count;
    if (!$ok) { throw new RuntimeException('FAIL: ' . $label); }
    ++$count;
    echo "PASS: $label\n";
}

$good = ['id' => 82, 'name' => 'سوکت شبکه Cat6 SFTP', 'sku' => 'TN-SN-18002', 'url' => 'https://tehnet.ir/product/tn-sn-18002/'];
$out = TehNet_Store_Storefront::sanitize_wishlist([$good]);
check(count($out) === 1 && $out[0]['id'] === 82 && $out[0]['sku'] === 'TN-SN-18002', 'valid entry kept with sku');
check(TehNet_Store_Storefront::sanitize_wishlist([['id' => 82, 'name' => 'x', 'url' => '']]) === [], 'empty url dropped');
check(TehNet_Store_Storefront::sanitize_wishlist([['id' => 0, 'name' => 'x', 'url' => 'https://tehnet.ir/a']]) === [], 'zero id dropped');
check(TehNet_Store_Storefront::sanitize_wishlist([['id' => '82', 'name' => 'x', 'url' => 'https://tehnet.ir/a']])[0]['id'] === 82, 'numeric string id coerced');
check(TehNet_Store_Storefront::sanitize_wishlist([['id' => 82, 'name' => str_repeat('ن', 250), 'url' => 'https://tehnet.ir/a']])[0]['name'] !== '' , 'long name bounded') ;
check(mb_strlen(TehNet_Store_Storefront::sanitize_wishlist([['id' => 82, 'name' => str_repeat('ن', 250), 'url' => 'https://tehnet.ir/a']])[0]['name']) === 200, 'name truncated to 200');
check(!isset(TehNet_Store_Storefront::sanitize_wishlist([['id' => 82, 'name' => 'x', 'url' => 'https://tehnet.ir/a']])[0]['sku']), 'missing sku omitted');
$dup = TehNet_Store_Storefront::sanitize_wishlist([$good, $good]);
check(count($dup) === 1 && $dup[0]['id'] === 82, 'duplicates removed');
check(count(TehNet_Store_Storefront::sanitize_wishlist(array_fill(0, 30, $good))) === 1, 'same-id flood collapses');
$many = [];
for ($i = 1; $i <= 30; $i++) { $many[] = ['id' => $i, 'name' => 'n' . $i, 'url' => "https://tehnet.ir/p$i/"]; }
check(count(TehNet_Store_Storefront::sanitize_wishlist($many)) === 24, 'list capped at 24');
check(TehNet_Store_Storefront::sanitize_wishlist(['not-an-item', 5, null]) === [], 'garbage rows dropped');

echo "WISHLIST_CONTRACTS=PASSED checks=$count\n";
