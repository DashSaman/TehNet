<?php
/**
 * Plugin Name: TehNet WooCommerce sitemap
 * Description: Omit the active cart, checkout and account pages from the WordPress page sitemap.
 */
defined( 'ABSPATH' ) || exit;

add_filter(
	'wp_sitemaps_posts_query_args',
	static function ( $args, $post_type ) {
		if ( 'page' !== $post_type || ! function_exists( 'wc_get_page_id' ) ) {
			return $args;
		}

		$excluded = array();
		foreach ( array( 'cart', 'checkout', 'myaccount' ) as $role ) {
			$id = wc_get_page_id( $role );
			if ( $id > 0 ) {
				$excluded[] = (int) $id;
			}
		}
		if ( ! $excluded ) {
			return $args;
		}

		if ( ! empty( $args['post__in'] ) ) {
			// An empty inclusion list would make WP_Query select every page.
			$remaining = array_diff( $args['post__in'], $excluded );
			$args['post__in'] = $remaining ? array_values( $remaining ) : array( 0 );
		} else {
			$existing = $args['post__not_in'] ?? array();
			$args['post__not_in'] = array_values( array_unique( array_merge( $existing, $excluded ) ) );
		}
		return $args;
	},
	30,
	2
);
