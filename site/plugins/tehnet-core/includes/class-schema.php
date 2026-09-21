<?php
/** TehNet structured-data output. */

defined('ABSPATH') || exit;

final class TehNet_Core_Schema {
    public function register(): void {
        add_action('wp_head', [$this, 'render'], 30);
    }

    public function render(): void {
        if (! $this->should_render()) {
            return;
        }

        $schema = $this->build_local_business();
        if ($schema === []) {
            return;
        }

        echo "\n<script type=\"application/ld+json\" class=\"tehnet-localbusiness-schema\">";
        echo wp_json_encode($schema, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        echo "</script>\n";
    }

    private function should_render(): bool {
        if (is_admin() || is_feed() || is_404()) {
            return false;
        }

        if (is_front_page() || is_page(['about', 'contact', 'services'])) {
            return true;
        }

        if (! is_page()) {
            return false;
        }

        $page = get_queried_object();
        $services = get_page_by_path('services', OBJECT, 'page');
        return $page instanceof WP_Post
            && $services instanceof WP_Post
            && (int) $page->post_parent === (int) $services->ID;
    }

    private function build_local_business(): array {
        $name = trim(TehNet_Core_Settings::value('tehnet_business_name'));
        $display_address = trim(TehNet_Core_Settings::value('tehnet_address'));
        $locality = trim(TehNet_Core_Settings::value('tehnet_address_locality'));
        $region = trim(TehNet_Core_Settings::value('tehnet_address_region'));
        $country = strtoupper(trim(TehNet_Core_Settings::value('tehnet_address_country')));

        $required = [$name, $display_address, $locality, $country];
        if (in_array('', $required, true)) {
            return [];
        }

        $address = [
            '@type' => 'PostalAddress',
            'streetAddress' => $this->street_address($display_address, $locality),
            'addressLocality' => $locality,
            'addressCountry' => $country,
        ];
        if ($region !== '') {
            $address['addressRegion'] = $region;
        }

        $schema = [
            '@context' => 'https://schema.org',
            '@type' => 'LocalBusiness',
            '@id' => home_url('/#localbusiness'),
            'name' => $name,
            'url' => home_url('/'),
            'address' => $address,
        ];

        $phone = $this->normalize_phone(TehNet_Core_Settings::value('tehnet_phone'));
        if ($phone !== '') {
            $schema['telephone'] = $phone;
        }

        $same_as = array_values(array_filter([
            TehNet_Core_Settings::value('tehnet_youtube_url'),
            TehNet_Core_Settings::value('tehnet_telegram_url'),
            TehNet_Core_Settings::value('tehnet_instagram_url'),
        ], static fn(string $url): bool => $url !== '' && filter_var($url, FILTER_VALIDATE_URL) !== false));
        if ($same_as !== []) {
            $schema['sameAs'] = $same_as;
        }

        $area_served = [];
        $onsite = trim(TehNet_Core_Settings::value('tehnet_onsite_area'));
        $remote = trim(TehNet_Core_Settings::value('tehnet_remote_area'));
        if ($onsite !== '') {
            $area_served[] = ['@type' => 'City', 'name' => $onsite];
        }
        if ($remote !== '' && $remote !== $onsite) {
            $area_served[] = ['@type' => 'Country', 'name' => $remote];
        }
        if ($area_served !== []) {
            $schema['areaServed'] = $area_served;
        }

        return $schema;
    }

    private function normalize_phone(string $phone): string {
        $phone = trim($phone);
        if ($phone === '') {
            return '';
        }

        $digits = preg_replace('/\D+/', '', $phone) ?? '';
        if ($digits === '') {
            return '';
        }
        if (str_starts_with($phone, '+')) {
            return '+' . $digits;
        }
        if (str_starts_with($digits, '0098')) {
            return '+98' . substr($digits, 4);
        }
        if (str_starts_with($digits, '98')) {
            return '+' . $digits;
        }
        if (str_starts_with($digits, '0')) {
            return '+98' . substr($digits, 1);
        }
        return '+98' . $digits;
    }

    private function street_address(string $address, string $locality): string {
        $pattern = '/^\s*' . preg_quote($locality, '/') . '\s*[،,]\s*/u';
        $street = trim((string) preg_replace($pattern, '', $address, 1));
        return $street !== '' ? $street : $address;
    }
}
