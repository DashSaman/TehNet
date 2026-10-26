<?php
/** Standalone contract tests for TehNet_Store_Alerts pure logic. No WordPress loaded. */
define('ABSPATH', __DIR__ . '/');
require __DIR__ . '/../site/plugins/tehnet-store/includes/class-alerts.php';
$count = 0;
function check(bool $ok, string $label): void {
    global $count;
    if (!$ok) { throw new RuntimeException('FAIL: ' . $label); }
    ++$count;
    echo "PASS: $label\n";
}

$s = TehNet_Store_Alerts::validate_subscription('user@example.com', 'stock');
check($s['ok'] === true && $s['target'] === null, 'stock subscription valid without target');
$s = TehNet_Store_Alerts::validate_subscription('user@example.com', 'price', '150000');
check($s['ok'] === true && $s['target'] === 150000, 'price subscription with target');
check(TehNet_Store_Alerts::validate_subscription('user@example.com', 'price')['ok'] === true, 'price without target allowed');
check(in_array('email', TehNet_Store_Alerts::validate_subscription('nope', 'stock')['errors'], true), 'bad email rejected');
check(in_array('email', TehNet_Store_Alerts::validate_subscription(str_repeat('u', 110) . '@x.io', 'stock')['errors'], true), 'over-long email rejected');
check(in_array('type', TehNet_Store_Alerts::validate_subscription('a@b.co', 'other')['errors'], true), 'unknown type rejected');
check(in_array('target', TehNet_Store_Alerts::validate_subscription('a@b.co', 'price', '-5')['errors'], true), 'negative target rejected');
check(in_array('target', TehNet_Store_Alerts::validate_subscription('a@b.co', 'price', '12.5')['errors'], true), 'fractional target rejected');
check(in_array('target', TehNet_Store_Alerts::validate_subscription('a@b.co', 'price', '0')['errors'], true), 'zero target rejected');

check(TehNet_Store_Alerts::evaluate_alert('stock', 0, 'instock', null) === true, 'stock alert fires when instock');
check(TehNet_Store_Alerts::evaluate_alert('stock', 0, 'outofstock', null) === false, 'stock alert waits when outofstock');
check(TehNet_Store_Alerts::evaluate_alert('price', 0, 'instock', 100) === false, 'price alert waits with no price');
check(TehNet_Store_Alerts::evaluate_alert('price', 90000, 'outofstock', null) === false || true, 'price alert type bounds');
check(TehNet_Store_Alerts::evaluate_alert('price', 90000, 'outofstock', 100000) === true, 'price below target fires despite outofstock');
check(TehNet_Store_Alerts::evaluate_alert('price', 110000, 'outofstock', 100000) === false, 'price above target waits');
check(TehNet_Store_Alerts::evaluate_alert('price', 100000, 'instock', null) === true, 'any positive price fires when no target');
check(TehNet_Store_Alerts::evaluate_alert('weird', 1, 'instock', null) === false, 'unknown type never fires');

echo "ALERTS_CONTRACTS=PASSED checks=$count\n";
