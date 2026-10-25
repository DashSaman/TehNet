<?php
/** Standalone contract tests for TehNet_Store_Accounting pure parts. No WordPress loaded. */
define('ABSPATH', __DIR__ . '/');
require __DIR__ . '/../site/plugins/tehnet-store/includes/class-accounting.php';
$count = 0;
function check(bool $ok, string $label): void {
    global $count;
    if (!$ok) { throw new RuntimeException('FAIL: ' . $label); }
    ++$count;
    echo "PASS: $label\n";
}

check(TehNet_Store_Accounting::jalali(1979, 2, 11) === [1357, 11, 22], 'revolution anchor 1357/11/22');
check(TehNet_Store_Accounting::jalali(2024, 3, 20) === [1403, 1, 1], 'nowruz 2024 = 1403/01/01');
check(TehNet_Store_Accounting::jalali(2026, 3, 21) === [1405, 1, 1], 'nowruz 2026 = 1405/01/01');
check(TehNet_Store_Accounting::jalali(2026, 9, 23) === [1405, 7, 1], '1405/07/01 = 2026-09-23');
check(TehNet_Store_Accounting::jalali(2026, 10, 25) === [1405, 8, 3], 'audit day 1405/08/03');
check(TehNet_Store_Accounting::jalali_date('2026-10-25T14:00:00+00:00') === '1405/08/03', 'jalali_date ISO string');
check(TehNet_Store_Accounting::jalali_date('2026-10-25') === '1405/08/03', 'jalali_date plain date');
check(TehNet_Store_Accounting::jalali_date('not-a-date') === '', 'jalali_date rejects garbage');
check(TehNet_Store_Accounting::jalali_date('') === '', 'jalali_date rejects empty');
check(TehNet_Store_Accounting::jalali(2026, 3, 20) === [1404, 12, 29], 'day before nowruz 2026 is 1404/12/29');

echo "ACCOUNTING_CONTRACTS=PASSED checks=$count\n";
