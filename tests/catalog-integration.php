<?php
/** Run only inside the isolated local WordPress, via wp eval-file. */
if (!class_exists('TehNet_Store_Catalog')) {
    fwrite(STDERR, "FAIL: native catalog importer missing\n"); exit(1);
}
if (wp_get_environment_type() !== 'local') { throw new RuntimeException('Local tests only'); }
$check = static function(bool $ok, string $message): void {
    if (!$ok) { throw new RuntimeException($message); }
    echo "PASS: $message\n";
};
$path = '/catalog/saieedshabake-2026-10-15.json';
$manifest = json_decode(file_get_contents($path), true, 512, JSON_THROW_ON_ERROR);
$service = new TehNet_Store_Catalog();
$first = $service->import($manifest);
$check(count($first['created']) === 25, 'first import creates exactly 25 draft products');
$second = $service->import($manifest);
$check(count($second['created']) === 0 && count($second['skipped']) === 25, 'repeat import creates no duplicates');
foreach ($first['created'] as $id) {
    $product = wc_get_product($id);
    $check($product->get_status() === 'draft' && $product->get_price() === '' && $product->get_stock_quantity() === 0 && $product->get_backorders() === 'no', 'safe catalog state');
}
$edited = wc_get_product($first['created'][0]);
$original = $edited->get_name();
$edited->set_name('LOCAL EDIT MUST SURVIVE'); $edited->save();
try { $service->rollback($first['run_id']); throw new RuntimeException('rollback should refuse edited product'); }
catch (RuntimeException $e) { $check(str_contains($e->getMessage(), 'edited'), 'rollback refuses human edits before changing any product'); }
$check(wc_get_product($first['created'][1])->get_status() === 'draft', 'refused rollback has no partial changes');
$edited->set_name($original); $edited->save();
$rolled = $service->rollback($first['run_id']);
$check(count($rolled['trashed']) === 25, 'rollback soft-trashes only products created by its run');
$again=$service->rollback($first['run_id']);
$check(count($again['trashed']) === 0, 'rollback is idempotent');
echo "CATALOG_INTEGRATION=PASSED\n";
