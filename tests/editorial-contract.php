<?php
/** Standalone contract tests for the editorial line parser. No WordPress loaded. */
define('ABSPATH', __DIR__ . '/');
require __DIR__ . '/../site/plugins/tehnet-store/includes/class-storefront.php';
$count = 0;
function check(bool $ok, string $label): void {
    global $count;
    if (!$ok) { throw new RuntimeException('FAIL: ' . $label); }
    ++$count;
    echo "PASS: $label\n";
}

check(TehNet_Store_Storefront::editorial_lines("قابل اعتماد\nارزان") === ['قابل اعتماد', 'ارزان'], 'lines split and kept');
check(TehNet_Store_Storefront::editorial_lines("  فاصله‌دار  \n\n\nبعدی") === ['فاصله‌دار', 'بعدی'], 'blank and whitespace lines dropped');
check(TehNet_Store_Storefront::editorial_lines("") === [], 'empty input yields empty');
check(TehNet_Store_Storefront::editorial_lines("x") === [], 'single-char line dropped');
check(TehNet_Store_Storefront::editorial_lines(str_repeat('ط', 121)) === [], 'over-long line dropped');
check(TehNet_Store_Storefront::editorial_lines(str_repeat('ط', 120)) === [str_repeat('ط', 120)], 'exactly 120 chars kept');
check(count(TehNet_Store_Storefront::editorial_lines("aa
bb
cc
dd
ee
ff
gg
hh")) === 6, 'capped at six lines');
check(TehNet_Store_Storefront::editorial_lines("یک\r\nدو") === ['یک', 'دو'], 'CRLF handled');

echo "EDITORIAL_CONTRACTS=PASSED checks=$count\n";
