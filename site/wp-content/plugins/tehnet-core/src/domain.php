<?php
/**
 * Pure TehNet domain helpers.
 *
 * This file intentionally has no WordPress dependency so core business
 * behavior can be tested without bootstrapping WordPress.
 */

function tehnet_normalize_sale_mode($mode): string {
    return $mode === 'inquiry' ? 'inquiry' : 'direct';
}

function tehnet_pro_next_expiry(int $now, int $current_expiry): int {
    $base = $current_expiry > $now ? $current_expiry : $now;
    return $base + (30 * 86400);
}

function tehnet_pro_is_active(int $expiry, int $now): bool {
    return $expiry > $now;
}
