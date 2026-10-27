<?php
/** Standalone contract tests for search-miss aggregation. No WordPress loaded. */
define('ABSPATH', __DIR__ . '/');
require __DIR__ . '/../site/plugins/tehnet-store/includes/class-storefront.php';
$count = 0;
function check(bool $ok, string $label): void {
    global $count;
    if (!$ok) { throw new RuntimeException('FAIL: ' . $label); }
    ++$count;
    echo "PASS: $label\n";
}

$a = TehNet_Store_Storefront::record_search_miss('کابل Cat7', []);
check(count($a) === 1 && $a['کابل Cat7'] === 1, 'first miss recorded');
$a = TehNet_Store_Storefront::record_search_miss('کابل Cat7', $a);
check($a['کابل Cat7'] === 2, 'repeat increments');
check(TehNet_Store_Storefront::record_search_miss('a', ['x ی' => 1]) === ['x ی' => 1], 'short term ignored');
check(TehNet_Store_Storefront::record_search_miss('  ', ['x' => 1]) === ['x' => 1], 'blank term ignored');
$long = str_repeat('ک', 80);
$out = TehNet_Store_Storefront::record_search_miss($long, []);
check(mb_strlen((string)array_key_first($out)) === 60, 'term truncated to 60');
$many = [];
for ($i = 0; $i < 130; $i++) { $many = TehNet_Store_Storefront::record_search_miss('عبارت ' . $i, $many); }
check(count($many) === 100, 'capped at 100 terms');
$last = TehNet_Store_Storefront::record_search_miss('عبارت 0', $many);
$last = TehNet_Store_Storefront::record_search_miss('عبارت 0', $last);
arsort($last, SORT_NUMERIC);
check(array_key_first($last) === 'عبارت 0' && $last['عبارت 0'] === 3, 'frequent term survives cap ranked first');

echo "SEARCH_MISS_CONTRACTS=PASSED checks=$count\n";
