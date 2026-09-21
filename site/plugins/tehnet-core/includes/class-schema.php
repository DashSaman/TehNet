<?php
/** TehNet structured-data output. */

defined('ABSPATH') || exit;

final class TehNet_Core_Schema {
    public function register(): void {
        add_action('wp_head', [$this, 'render'], 30);
    }

    public function render(): void {
        // Implemented in the next plan task after the settings contract is green.
    }
}
