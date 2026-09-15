<?php
/** TehNet public content models. */

defined('ABSPATH') || exit;

final class TehNet_Core_Content_Types {
    public function register(): void {
        add_action('init', [$this, 'register_types']);
    }

    public function register_types(): void {
        register_post_type('tn_service', [
            'labels' => [
                'name' => __('خدمات', 'tehnet-core'),
                'singular_name' => __('خدمت', 'tehnet-core'),
                'add_new_item' => __('افزودن خدمت', 'tehnet-core'),
                'edit_item' => __('ویرایش خدمت', 'tehnet-core'),
            ],
            'public' => true,
            'show_in_rest' => true,
            'menu_icon' => 'dashicons-hammer',
            'supports' => ['title', 'editor', 'excerpt', 'thumbnail', 'revisions'],
            'has_archive' => false,
            'rewrite' => ['slug' => 'services', 'with_front' => false],
        ]);

        register_post_type('tn_lab', [
            'labels' => [
                'name' => __('لاب و فایل', 'tehnet-core'),
                'singular_name' => __('لاب', 'tehnet-core'),
                'add_new_item' => __('افزودن لاب', 'tehnet-core'),
                'edit_item' => __('ویرایش لاب', 'tehnet-core'),
            ],
            'public' => true,
            'show_in_rest' => true,
            'menu_icon' => 'dashicons-editor-code',
            'supports' => ['title', 'editor', 'excerpt', 'thumbnail', 'revisions'],
            'has_archive' => false,
            'rewrite' => ['slug' => 'lab', 'with_front' => false],
        ]);
    }
}
