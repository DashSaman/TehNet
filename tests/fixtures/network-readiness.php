<?php
// Component fixture only: no WordPress database, credentials or customer data.
declare(strict_types=1);
define('ABSPATH', __DIR__);
function add_shortcode(...$args): void {}
function add_action(...$args): void {}
function esc_attr($value): string { return htmlspecialchars((string)$value, ENT_QUOTES, 'UTF-8'); }
function esc_html($value): string { return esc_attr($value); }
function wp_unique_id($prefix = ''): string { static $n = 0; return $prefix . ++$n; }
require __DIR__ . '/../../site/mu-plugins/tehnet-technical-resources/network-readiness.php';
?><!doctype html>
<html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>TehNet readiness component fixture</title>
<style>body{margin:0;background:#081522;color:#e5eff8;font:16px/1.9 sans-serif}main{max-width:1080px;margin:auto;padding:16px}*{box-sizing:border-box}</style>
<link rel="stylesheet" href="/network-readiness.css"></head><body><main><h1>آزمون مؤلفهٔ چک‌لیست</h1>
<?php echo TehNet\TechnicalResources\readiness_checklist(); ?>
<?php echo TehNet\TechnicalResources\readiness_checklist(); ?>
</main><script src="/network-readiness.js" defer></script></body></html>
