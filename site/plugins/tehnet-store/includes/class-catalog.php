<?php
defined('ABSPATH') || exit;

/** Creation-only import: reruns preserve human edits; revisions need explicit review. */
final class TehNet_Store_Catalog {
    private const LOCK = 'tn_store_catalog_lock';

    public function import(array $manifest, bool $dry_run = false): array {
        if (!class_exists('WooCommerce')) { throw new RuntimeException('WooCommerce required'); }
        $this->validate($manifest);
        if (!$dry_run) { $this->assert_environment(); }
        $result = ['run_id' => wp_generate_uuid4(), 'created' => [], 'skipped' => [], 'categories_created' => [], 'dry_run' => $dry_run];
        $plan = [];
        foreach ($manifest['products'] as $row) {
            $existing = get_posts(['post_type' => 'product', 'post_status' => array_keys(get_post_stati()), 'numberposts' => 2, 'fields' => 'ids', 'meta_key' => '_tn_source_key', 'meta_value' => $row['source_key']]);
            if (count($existing) > 1) { throw new RuntimeException('Duplicate existing source mapping'); }
            $sku_id = wc_get_product_id_by_sku($row['sku']);
            if ($sku_id && (!$existing || (int)$existing[0] !== (int)$sku_id)) { throw new RuntimeException('SKU ownership conflict'); }
            if ($existing) {
                if (get_post_meta((int)$existing[0], '_tn_catalog_manifest_hash', true) !== $this->row_hash($row)) {
                    throw new RuntimeException('Source revision requires review; existing product preserved');
                }
                $result['skipped'][] = (int)$existing[0];
            } else { $plan[] = $row; }
        }
        if ($dry_run) { $result['would_create'] = count($plan); return $result; }
        if (!add_option(self::LOCK, $result['run_id'], '', false)) { throw new RuntimeException('Catalog import locked; inspect interrupted run before unlocking'); }
        global $wpdb;
        $wpdb->query('START TRANSACTION');
        try {
            $categories = $this->categories($manifest['categories'], $result);
            foreach ($plan as $row) {
                $product = new WC_Product_Simple();
                $product->set_name(sanitize_text_field($row['name']));
                $product->set_slug('tn-sn-' . $row['source_id']);
                $product->set_status('draft');
                $product->set_sku($row['sku']);
                $product->set_description(wp_kses_post($row['description']));
                $product->set_short_description(wp_kses_post($row['short_description']));
                $product->set_regular_price('');
                $product->set_sale_price('');
                $product->set_manage_stock(true);
                $product->set_stock_quantity(0);
                $product->set_stock_status('outofstock');
                $product->set_backorders('no');
                $product->set_category_ids(array_map(static fn($id) => $categories[$id], $row['category_source_ids']));
                $product->update_meta_data('_tn_source_key', $row['source_key']);
                $product->update_meta_data('_tn_source_url', esc_url_raw($row['source_url']));
                $product->update_meta_data('_tn_source_id', (int)$row['source_id']);
                $product->update_meta_data('_tn_catalog_run', $result['run_id']);
                $product->update_meta_data('_tn_catalog_manifest_hash', $this->row_hash($row));
                $product->update_meta_data('_tn_source_attributes', $row['source_attributes']);
                $product->update_meta_data('_tn_review_flags', $row['review_flags']);
                $product->update_meta_data('_tn_media_license', 'unverified-not-imported');
                $product->update_meta_data('_tn_sale_approved', 'no');
                $id = $product->save();
                if (!$id) { throw new RuntimeException('Product save failed'); }
                $result['created'][] = $id;
                $result['fingerprints'][$id] = $this->fingerprint(wc_get_product($id));
            }
            add_option('tn_catalog_run_' . $result['run_id'], $result, '', false);
            $wpdb->query('COMMIT');
            return $result;
        } catch (Throwable $e) {
            $wpdb->query('ROLLBACK');
            foreach ($result['created'] as $id) { clean_post_cache($id); wc_delete_product_transients($id); }
            throw $e;
        } finally { delete_option(self::LOCK); }
    }

    public function rollback(string $run_id): array {
        $this->assert_environment();
        if (defined('EMPTY_TRASH_DAYS') && EMPTY_TRASH_DAYS === 0) { throw new RuntimeException('Soft trash must be enabled'); }
        if (!preg_match('/^[a-f0-9-]{36}$/D', $run_id)) { throw new RuntimeException('Invalid run ID'); }
        $run = get_option('tn_catalog_run_' . $run_id);
        if (!is_array($run)) { throw new RuntimeException('Unknown import run'); }
        if (!empty($run['rolled_back'])) { return ['trashed' => []]; }
        if (!add_option(self::LOCK, $run_id, '', false)) { throw new RuntimeException('Catalog locked'); }
        global $wpdb;
        $wpdb->query('START TRANSACTION');
        try {
            foreach ($run['created'] as $id) {
                $product = wc_get_product($id);
                if (!$product || $product->get_status() !== 'draft' || $product->get_meta('_tn_catalog_run') !== $run_id || $this->fingerprint($product) !== $run['fingerprints'][$id]) {
                    throw new RuntimeException('Product edited since import; rollback refused without changes');
                }
            }
            foreach ($run['created'] as $id) {
                if (!wp_trash_post($id)) { throw new RuntimeException('Could not soft-trash import product'); }
            }
            $run['rolled_back'] = true;
            update_option('tn_catalog_run_' . $run_id, $run, false);
            $wpdb->query('COMMIT');
            return ['trashed' => $run['created'], 'categories_retained' => $run['categories_created']];
        } catch (Throwable $e) { $wpdb->query('ROLLBACK'); throw $e; }
        finally { delete_option(self::LOCK); }
    }

    private function assert_environment(): void {
        if (!in_array(wp_get_environment_type(), ['local','staging','development'], true)) {
            throw new RuntimeException('Import disabled in production; deployment approval and backup required');
        }
        if (!class_exists('WooCommerce')) { throw new RuntimeException('WooCommerce required'); }
    }

    private function validate(array $manifest): void {
        if (($manifest['schema_version'] ?? null) !== 1 || ($manifest['source'] ?? '') !== 'https://saieedshabake.ir' || !is_array($manifest['products'] ?? null) || !is_array($manifest['categories'] ?? null)) {
            throw new RuntimeException('Invalid catalog schema');
        }
        $ids = []; $categories = [];
        foreach ($manifest['categories'] as $category) {
            $id = (int)($category['id'] ?? 0);
            if ($id < 1 || isset($categories[$id]) || empty($category['name'])) { throw new RuntimeException('Invalid category'); }
            $categories[$id] = (int)($category['parent'] ?? 0);
        }
        foreach ($categories as $id => $parent) {
            $seen = [];
            while ($parent) {
                if (!isset($categories[$parent]) || isset($seen[$parent]) || $parent === $id) { throw new RuntimeException('Invalid category ancestry'); }
                $seen[$parent] = true; $parent = $categories[$parent];
            }
        }
        foreach ($manifest['products'] as $row) {
            $id = $row['source_id'] ?? null;
            if (!is_int($id) || $id < 1 || isset($ids[$id]) || ($row['sku'] ?? '') !== 'TN-SN-' . $id || ($row['source_key'] ?? '') !== 'saieedshabake.ir:product:' . $id) { throw new RuntimeException('Invalid product identity'); }
            $ids[$id] = true;
            if (wp_parse_url($row['source_url'] ?? '', PHP_URL_HOST) !== 'saieedshabake.ir' || wp_parse_url($row['source_url'], PHP_URL_SCHEME) !== 'https') { throw new RuntimeException('Invalid source URL'); }
            if (($row['status'] ?? '') !== 'draft' || ($row['regular_price'] ?? null) !== '' || ($row['stock_quantity'] ?? null) !== 0 || ($row['images'] ?? null) !== []) { throw new RuntimeException('Unsafe imported sale data'); }
            foreach ($row['category_source_ids'] ?? [] as $category_id) { if (!isset($categories[$category_id])) { throw new RuntimeException('Unknown category'); } }
        }
    }

    private function categories(array $rows, array &$result): array {
        $mapping = []; $pending = $rows;
        while ($pending) {
            foreach ($pending as $key => $row) {
                $parent = (int)$row['parent'];
                if ($parent && !isset($mapping[$parent])) { continue; }
                $terms = get_terms(['taxonomy' => 'product_cat', 'hide_empty' => false, 'orderby'=>'term_id', 'menu_order'=>false, 'meta_query'=>[['key'=>'_tn_source_category','value'=>'saieedshabake.ir:' . $row['id'],'compare'=>'=']]]);
                if (is_wp_error($terms) || count($terms) > 1) { throw new RuntimeException('Category mapping conflict'); }
                if ($terms) { $mapping[$row['id']] = $terms[0]->term_id; }
                else {
                    $created = wp_insert_term($row['name'], 'product_cat', ['slug' => 'tn-sn-category-' . $row['id'], 'parent' => $parent ? $mapping[$parent] : 0]);
                    if (is_wp_error($created)) { throw new RuntimeException($created->get_error_message()); }
                    $term_id = (int)$created['term_id'];
                    add_term_meta($term_id, '_tn_source_category', 'saieedshabake.ir:' . $row['id'], true);
                    $mapping[$row['id']] = $term_id; $result['categories_created'][] = $term_id;
                }
                unset($pending[$key]);
            }
        }
        return $mapping;
    }

    private function row_hash(array $row): string { return hash('sha256', wp_json_encode($row)); }
    private function fingerprint(WC_Product $p): string {
        global $wpdb;
        $metadata=$wpdb->get_results($wpdb->prepare("SELECT meta_key,meta_value FROM {$wpdb->postmeta} WHERE post_id=%d AND meta_key NOT IN ('_edit_lock','_edit_last') ORDER BY meta_key,meta_value",$p->get_id()),ARRAY_A);
        return hash('sha256', wp_json_encode([$p->get_name(), $p->get_sku(), $p->get_status(), $p->get_description(), $p->get_short_description(), $p->get_regular_price(), $p->get_sale_price(), $p->get_stock_quantity(), $p->get_category_ids(), $p->get_image_id(), $p->get_gallery_image_ids(), $p->get_manage_stock(), $p->get_backorders(), $p->get_attributes(),$metadata]));
    }
}
