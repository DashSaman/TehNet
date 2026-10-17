<?php
/** TehNet-owned, idempotent navigation addition. No existing items are rewritten. */
declare(strict_types=1);

function tn_software_menu_ensure(string $owner): array {
    $locations = get_nav_menu_locations();
    $menu = (int)($locations['primary'] ?? 0);
    if ($menu <= 0) { throw new RuntimeException('Primary menu is not assigned'); }
    $url = home_url('/software/');
    $matches = [];
    foreach (wp_get_nav_menu_items($menu) ?: [] as $item) {
        if (rtrim((string)$item->url, '/') === rtrim($url, '/')) { $matches[] = $item; }
    }
    if (count($matches) > 1) { throw new RuntimeException('Existing duplicate software items need explicit review'); }
    if ($matches) { return ['id'=>(int)$matches[0]->ID,'created'=>false,'menu'=>$menu]; }
    $id = wp_update_nav_menu_item($menu, 0, [
        'menu-item-title'=>'آرشیو نرم‌افزار', 'menu-item-url'=>$url,
        'menu-item-type'=>'custom', 'menu-item-status'=>'publish',
    ]);
    if (is_wp_error($id) || !$id) { throw new RuntimeException('Menu insertion failed'); }
    update_post_meta((int)$id, '_tehnet_software_owner', $owner);
    return ['id'=>(int)$id,'created'=>true,'menu'=>$menu];
}

function tn_software_menu_rollback(int $id, string $owner): void {
    if ($owner === '' || get_post_meta($id, '_tehnet_software_owner', true) !== $owner) {
        throw new RuntimeException('Refusing to remove an unowned menu item');
    }
    if (!wp_delete_post($id, true)) { throw new RuntimeException('Owned menu rollback failed'); }
}

function tn_software_menu_rollback_owner(string $owner): void {
    if ($owner === '') { throw new RuntimeException('Empty owner'); }
    $locations = get_nav_menu_locations();
    foreach (wp_get_nav_menu_items((int)($locations['primary'] ?? 0)) ?: [] as $item) {
        if (get_post_meta((int)$item->ID, '_tehnet_software_owner', true) === $owner) {
            tn_software_menu_rollback((int)$item->ID, $owner);
        }
    }
}
