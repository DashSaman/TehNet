<?php
/** Standalone contract tests for TehNet_Store_Price_Rate pure pricing math. No WordPress loaded. */
define('ABSPATH', __DIR__ . '/');
require __DIR__ . '/../site/plugins/tehnet-store/includes/class-price-rate.php';
$count = 0;
function check(bool $ok, string $label): void {
    global $count;
    if (!$ok) { throw new RuntimeException('FAIL: ' . $label); }
    ++$count;
    echo "PASS: $label\n";
}
function rejected(callable $fn, string $label): void {
    try { $fn(); } catch (InvalidArgumentException $e) { check(true, $label); return; }
    throw new RuntimeException('Accepted: ' . $label);
}

check(TehNet_Store_Price_Rate::compute('1', 100000.0) === 100000, '1 USD at 100000 rounds to 100000 IRR');
check(TehNet_Store_Price_Rate::compute('12.5', 100000.0) === 1250000, '12.5 USD exact multiply');
check(TehNet_Store_Price_Rate::compute('1.0001', 100000.0) === 101000, 'fractional result rounds up to next 1000');
check(TehNet_Store_Price_Rate::compute('2', 99999.5) === 200000, '0.5-rial fraction rounds up');
check(TehNet_Store_Price_Rate::compute('1', 1234.0) === 2000, 'tiny result still rounds up to 1000 multiple');
check(TehNet_Store_Price_Rate::compute('3', 50000.0, 5000) === 150000, 'custom 5000 rounding step');
check(TehNet_Store_Price_Rate::compute('0.000001', 1000000.0) === 1000, 'minimal positive base produces 1000');
rejected(fn() => TehNet_Store_Price_Rate::compute('-1', 100.0), 'negative base rejected');
rejected(fn() => TehNet_Store_Price_Rate::compute('0', 100.0), 'zero base rejected');
rejected(fn() => TehNet_Store_Price_Rate::compute('abc', 100.0), 'non-numeric base rejected');
rejected(fn() => TehNet_Store_Price_Rate::compute('1e9', 100.0), 'scientific notation rejected');
rejected(fn() => TehNet_Store_Price_Rate::compute('1', 0.0), 'zero rate rejected');
rejected(fn() => TehNet_Store_Price_Rate::compute('1', -5.0), 'negative rate rejected');
rejected(fn() => TehNet_Store_Price_Rate::compute('1', 100.0, 0), 'zero rounding rejected');
rejected(fn() => TehNet_Store_Price_Rate::compute('1', 100.0, -1000), 'negative rounding rejected');
rejected(fn() => TehNet_Store_Price_Rate::compute('92233720368547', 1000000.0), 'overflow rejected');

$plan = TehNet_Store_Price_Rate::plan([
    ['id' => 1, 'sku' => 'A', 'base' => '10', 'price' => 900000],
    ['id' => 2, 'sku' => 'B', 'base' => '', 'price' => 0],
    ['id' => 3, 'sku' => 'C', 'base' => '7.25', 'price' => 0],
    ['id' => 4, 'sku' => 'D', 'base' => 'x', 'price' => 0],
], 100000.0);
check(count($plan['rows']) === 2 && count($plan['skipped']) === 2, 'plan splits priced and skipped');
check($plan['rows'][0]['proposed_irr'] === 1000000, 'plan computes 10 USD row');
check($plan['rows'][1]['proposed_irr'] === 725000, 'plan computes 7.25 USD row');
check($plan['rows'][0]['current_irr'] === 900000, 'plan carries current price');
check($plan['skipped'][0]['reason'] === 'no-base-price', 'missing base reported');
check($plan['skipped'][1]['reason'] === 'invalid-base-price', 'invalid base reported');

echo "FX_RATE_CONTRACTS=PASSED checks=$count\n";
