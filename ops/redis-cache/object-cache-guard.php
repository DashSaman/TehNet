<?php
/**
 * Guard loader: uses the official Redis Object Cache drop-in when the PHP Redis
 * extension is present, and falls back to WordPress core's in-memory cache
 * otherwise (e.g. after a container recreation without the extension).
 */
if ( ! defined( 'ABSPATH' ) ) { exit; }
if ( extension_loaded( 'redis' ) && file_exists( __DIR__ . '/object-cache-redis.php' ) ) {
    require_once __DIR__ . '/object-cache-redis.php';
} else {
    require_once ABSPATH . WPINC . '/cache.php';
}
