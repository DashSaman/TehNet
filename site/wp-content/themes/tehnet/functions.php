<?php
if(!defined('ABSPATH'))exit;
function tehnet_theme_setup():void{add_theme_support('title-tag');add_theme_support('post-thumbnails');add_theme_support('html5',['search-form','comment-form','comment-list','gallery','caption','style','script']);add_theme_support('woocommerce');register_nav_menus(['primary'=>__('منوی اصلی','tehnet'),'footer'=>__('منوی فوتر','tehnet')]);}
add_action('after_setup_theme','tehnet_theme_setup');
function tehnet_assets():void{$v=wp_get_theme()->get('Version');wp_enqueue_style('tehnet-app',get_template_directory_uri().'/assets/css/app.css',[],$v);wp_enqueue_script('tehnet-theme-toggle',get_template_directory_uri().'/assets/js/theme-toggle.js',[],$v,true);}
add_action('wp_enqueue_scripts','tehnet_assets');
