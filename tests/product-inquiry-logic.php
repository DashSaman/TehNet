<?php
define('ABSPATH', __DIR__ . '/');
$commerce = __DIR__ . '/../site/plugins/tehnet-core/includes/class-commerce.php';
$inquiries = __DIR__ . '/../site/plugins/tehnet-core/includes/class-inquiries.php';
if (! is_file($commerce)) { fwrite(STDERR, "FAIL: commerce class missing\n"); exit(1); }
if (! is_file($inquiries)) { fwrite(STDERR, "FAIL: inquiries class missing\n"); exit(1); }
require $commerce;
require $inquiries;

final class Fake_Product {
    public function __construct(private bool $virtual, private bool $downloadable) {}
    public function is_virtual(): bool { return $this->virtual; }
    public function is_downloadable(): bool { return $this->downloadable; }
}
$assert = static function (bool $ok, string $message): void {
    if (! $ok) { fwrite(STDERR, "FAIL: $message\n"); exit(1); }
};
$assert(TehNet_Core_Commerce::is_physical_inquiry_product(new Fake_Product(false, false)), 'physical product must be inquiry-only');
$assert(! TehNet_Core_Commerce::is_physical_inquiry_product(new Fake_Product(true, false)), 'virtual product must stay outside physical inquiry');
$assert(! TehNet_Core_Commerce::is_physical_inquiry_product(new Fake_Product(false, true)), 'downloadable product must stay outside physical inquiry');
$assert(TehNet_Core_Inquiries::normalize_mobile('۰۹۱۲ ۳۴۵ ۶۷۸۹') === '09123456789', 'Persian mobile normalization');
$assert(TehNet_Core_Inquiries::normalize_mobile('+98 912 345 6789') === '09123456789', '+98 mobile normalization');
$assert(TehNet_Core_Inquiries::normalize_mobile('0098-912-345-6789') === '09123456789', '0098 mobile normalization');
$assert(TehNet_Core_Inquiries::normalize_mobile('02191018746') === '', 'landline must fail');
$assert(TehNet_Core_Inquiries::normalize_quantity('1') === 1, 'quantity 1');
$assert(TehNet_Core_Inquiries::normalize_quantity('99') === 99, 'quantity 99');
foreach (['0', '-1', '1.5', '100', 'abc'] as $bad) {
    $assert(TehNet_Core_Inquiries::normalize_quantity($bad) === 0, "invalid quantity $bad");
}
echo "PRODUCT_INQUIRY_LOGIC=PASSED\n";
