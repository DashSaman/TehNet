<?php
/** Local-only transport guard. Never reports an email as delivered. */
defined('ABSPATH') || exit;
if (wp_get_environment_type()==='local') {
    add_filter('pre_wp_mail',static fn()=>false,PHP_INT_MAX);
}
