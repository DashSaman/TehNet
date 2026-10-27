<?php
/** Standalone contract tests for category guide lookup. No WordPress loaded. */
define('ABSPATH', __DIR__ . '/');
require __DIR__ . '/../site/plugins/tehnet-store/includes/class-storefront.php';
$count = 0;
function check(bool $ok, string $label): void {
    global $count;
    if (!$ok) { throw new RuntimeException('FAIL: ' . $label); }
    ++$count;
    echo "PASS: $label\n";
}

check(TehNet_Store_Storefront::guide_for('کابل شبکه CAT6')['title'] === 'راهنمای خرید کابل شبکه', 'cable category mapped');
check(TehNet_Store_Storefront::guide_for('کابل شبکه لگراند (Legrand)')['title'] === 'راهنمای خرید کابل شبکه', 'brand cable category mapped to cable guide');
check(TehNet_Store_Storefront::guide_for('کیستون تلفن')['title'] === 'راهنمای خرید کیستون شبکه', 'phone keystone mapped to keystone guide');
check(TehNet_Store_Storefront::guide_for('اتصالات')['title'] === 'راهنمای خرید اتصالات و سوکت شبکه', 'connector category mapped');
check(TehNet_Store_Storefront::guide_for('انواع پریز شبکه')['title'] === 'راهنمای خرید تجهیزات پسیو شبکه', 'unknown category falls back to general');
check(TehNet_Store_Storefront::guide_for('')['title'] === 'راهنمای خرید تجهیزات پسیو شبکه', 'empty name falls back');
foreach (['cable','keystone','connector','general'] as $probe_name) { }
$g = TehNet_Store_Storefront::guide_for('کابل');
check(count($g['body']) >= 2 && count($g['tips']) >= 4, 'guide has 2+ paragraphs and 4+ tips');
foreach (['کابل','کیستون','اتصالات','پسیو'] as $name) {
    $g = TehNet_Store_Storefront::guide_for($name);
    foreach (array_merge($g['body'], $g['tips']) as $text) {
        if (mb_strlen($text) > 500) { throw new RuntimeException('guide text too long'); }
    }
}
check(true, 'all guide texts bounded');

echo "GUIDES_CONTRACTS=PASSED checks=$count\n";
