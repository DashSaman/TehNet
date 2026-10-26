<?php
/** Standalone contract tests for TehNet_Store_Quotes pure validation. No WordPress loaded. */
define('ABSPATH', __DIR__ . '/');
require __DIR__ . '/../site/plugins/tehnet-store/includes/class-quotes.php';
$count = 0;
function check(bool $ok, string $label): void {
    global $count;
    if (!$ok) { throw new RuntimeException('FAIL: ' . $label); }
    ++$count;
    echo "PASS: $label\n";
}

$base = static fn(array $overrides = []) => array_merge([
    'company' => 'شرکت شبکه پارس', 'contact' => 'مهندس رضایی', 'phone' => '021-91001000',
    'email' => 'purchase@pars.example', 'items' => [['product_id' => 82, 'qty' => '2.5']], 'notes' => 'تحویل تهران',
], $overrides);

$v = TehNet_Store_Quotes::validate_request(...array_values($base()));
check($v['ok'] === true && $v['items'][0]['qty'] === '2.5', 'valid request accepted with fractional qty');
check(TehNet_Store_Quotes::validate_request(...array_values($base(['company' => 'ش'])))['ok'] === false, 'short company rejected');
check(TehNet_Store_Quotes::validate_request(...array_values($base(['contact' => ''])))['ok'] === false, 'empty contact rejected');
check(TehNet_Store_Quotes::validate_request(...array_values($base(['phone' => 'abc'])))['ok'] === false, 'non-numeric phone rejected');
check(TehNet_Store_Quotes::validate_request(...array_values($base(['phone' => '+98 21 9100 1000'])))['ok'] === true, 'international-format phone accepted');
check(TehNet_Store_Quotes::validate_request(...array_values($base(['email' => 'nope'])))['ok'] === false, 'invalid email rejected');
check(TehNet_Store_Quotes::validate_request(...array_values($base(['items' => []])))['ok'] === false, 'zero items rejected');
check(TehNet_Store_Quotes::validate_request(...array_values($base(['items' => array_fill(0, 6, ['product_id' => 1, 'qty' => '1'])])))['ok'] === false, 'more than five items rejected');
check(TehNet_Store_Quotes::validate_request(...array_values($base(['items' => [['product_id' => 0, 'qty' => '1']]])))['ok'] === false, 'zero product id rejected');
check(TehNet_Store_Quotes::validate_request(...array_values($base(['items' => [['product_id' => 82, 'qty' => '-3']]])))['ok'] === false, 'negative qty rejected');
check(TehNet_Store_Quotes::validate_request(...array_values($base(['items' => [['product_id' => 82, 'qty' => '1.234']]])))['ok'] === false, 'too-precise qty rejected');
check(TehNet_Store_Quotes::validate_request(...array_values($base(['items' => [['product_id' => 82, 'qty' => '10.25']]])))['ok'] === true, 'two-decimal qty accepted');
check(TehNet_Store_Quotes::validate_request(...array_values($base(['items' => [['product_id' => 82, 'qty' => '1e6']]])))['ok'] === false, 'scientific-notation qty rejected');
check(TehNet_Store_Quotes::validate_request(...array_values($base(['notes' => str_repeat('ت', 1001)])))['ok'] === false, 'long notes rejected');
check(TehNet_Store_Quotes::validate_request(...array_values($base(['items' => [['product_id' => 82, 'qty' => '999999']]])))['ok'] === true, 'six-digit integer qty accepted');

echo "QUOTES_CONTRACTS=PASSED checks=$count\n";
