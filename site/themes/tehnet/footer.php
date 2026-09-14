<?php
defined('ABSPATH') || exit;
?>
</main>
<footer class="tn-site-footer">
    <div class="tn-container">
        <strong><?php bloginfo('name'); ?></strong>
        <p><?php echo esc_html(get_option('tehnet_phone', '021-91018746')); ?></p>
        <p><?php echo esc_html(get_option('tehnet_address', 'تهران، آیت‌الله کاشانی، شاهین جنوبی')); ?></p>
        <?php wp_nav_menu(['theme_location' => 'footer', 'container' => false, 'fallback_cb' => false]); ?>
    </div>
</footer>
<?php wp_footer(); ?>
</body>
</html>
