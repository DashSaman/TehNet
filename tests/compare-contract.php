<?php
/** Standalone contract tests for TehNet_Store_Storefront::source_specs projection. No WordPress loaded. */
define('ABSPATH', __DIR__ . '/');
require __DIR__ . '/../site/plugins/tehnet-store/includes/class-storefront.php';
$count = 0;
function check(bool $ok, string $label): void {
    global $count;
    if (!$ok) { throw new RuntimeException('FAIL: ' . $label); }
    ++$count;
    echo "PASS: $label\n";
}

check(TehNet_Store_Storefront::source_specs(null) === [], 'non-array rejected');
check(TehNet_Store_Storefront::source_specs('garbage') === [], 'string rejected');
check(TehNet_Store_Storefront::source_specs([]) === [], 'empty array');

$valid = [
    ['name' => 'رده شبکه (Category)', 'terms' => [['name' => 'Cat6']]],
    ['name' => 'نوع شیلد', 'terms' => [['name' => 'SFTP'], ['name' => 'F/UTP']]],
];
$out = TehNet_Store_Storefront::source_specs($valid);
check($out === ['رده شبکه (Category)' => 'Cat6', 'نوع شیلد' => 'SFTP / F/UTP'], 'names and joined terms projected');

check(TehNet_Store_Storefront::source_specs([['name' => '', 'terms' => [['name' => 'x']]]]) === [], 'empty name skipped');
check(TehNet_Store_Storefront::source_specs([['name' => 'نوع', 'terms' => []]]) === [], 'empty terms skipped');
check(TehNet_Store_Storefront::source_specs([['name' => 'نوع', 'terms' => [['name' => '  ']]]]) === [], 'blank term skipped');
check(TehNet_Store_Storefront::source_specs([['name' => 'نوع', 'terms' => [['id' => 5]]]]) === [], 'term without name skipped');

$four = TehNet_Store_Storefront::source_specs([['name' => 'ن', 'terms' => [['name' => 'a'], ['name' => 'b'], ['name' => 'c'], ['name' => 'd']]]]);
check($four['ن'] === 'a / b / c', 'terms capped at three');

$many = [];
for ($i = 0; $i < 12; $i++) { $many[] = ['name' => 'صفت ' . $i, 'terms' => [['name' => 'v']]]; }
check(count(TehNet_Store_Storefront::source_specs($many)) === 8, 'attributes capped at eight');

$long = TehNet_Store_Storefront::source_specs([['name' => str_repeat('ن', 100), 'terms' => [['name' => str_repeat('م', 100)]]]]);
check(mb_strlen((string)key($long)) === 60 && mb_strlen((string)reset($long)) === 60, 'long strings truncated to 60 chars');

$mixed = TehNet_Store_Storefront::source_specs(['not-an-attr', ['name' => 'ok', 'terms' => [['name' => 'v']]]]);
check($mixed === ['ok' => 'v'], 'non-array attribute rows skipped without abort');

echo "COMPARE_SOURCE_SPECS=PASSED checks=$count\n";
