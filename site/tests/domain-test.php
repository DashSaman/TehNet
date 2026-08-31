<?php
$domain = dirname(__DIR__) . '/wp-content/plugins/tehnet-core/src/domain.php';
if (!is_file($domain)) {
    fwrite(STDERR, "domain.php missing\n");
    exit(1);
}
require_once $domain;

function tn_assert($condition, string $message): void {
    if (!$condition) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
}

tn_assert(tehnet_normalize_sale_mode('direct') === 'direct', 'direct sale mode remains direct');
tn_assert(tehnet_normalize_sale_mode('inquiry') === 'inquiry', 'inquiry sale mode remains inquiry');
tn_assert(tehnet_normalize_sale_mode('unexpected') === 'direct', 'unknown sale mode falls back to direct');

$day = 86400;
$now = 1_700_000_000;
tn_assert(tehnet_pro_next_expiry($now, 0) === $now + (30 * $day), 'new Pro access grants 30 days');
tn_assert(tehnet_pro_next_expiry($now, $now + (10 * $day)) === $now + (40 * $day), 'renewal extends existing active access');
tn_assert(tehnet_pro_next_expiry($now, $now - 10) === $now + (30 * $day), 'expired access renews from now');
tn_assert(tehnet_pro_is_active($now + 1, $now) === true, 'future expiry is active');
tn_assert(tehnet_pro_is_active($now, $now) === false, 'expiry at current time is inactive');

echo "domain-test: PASS\n";
