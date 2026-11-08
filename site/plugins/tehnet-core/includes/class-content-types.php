<?php
/** TehNet public content models. */

defined('ABSPATH') || exit;

final class TehNet_Core_Content_Types {
    public function register(): void {
        add_action('init', [$this, 'register_types']);
        add_filter('option_rewrite_rules', [$this, 'existing_lab_page_rules']);
    }

    /**
     * Three existing public page URLs precede the generic tn_lab rewrite.
     * Filters the read value only: no permalink/URL/role/option write or flush.
     * Preserve a real same-slug CPT collision for explicit reconciliation.
     */
    public function existing_lab_page_rules($rules) {
        if (!is_array($rules)) return $rules;
        $prefix=[];
        foreach ([76=>'gns3-mikrotik',188=>'wireguard-mtu',207=>'voice-network-checklist'] as $id=>$slug) {
            $page=get_post($id);
            if (!$page || $page->post_type!=='page' || $page->post_status!=='publish' || $page->post_password!=='' || get_page_uri($id)!=='lab/'.$slug || get_page_by_path($slug,OBJECT,'tn_lab')) continue;
            $prefix['lab/'.$slug.'/?
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
            'rewrite' => false,
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
]='index.php?page_id='.$id;
        }
        return $prefix+$rules;
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
            'rewrite' => false,
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
