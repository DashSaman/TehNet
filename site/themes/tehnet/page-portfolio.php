<?php
/** Template Name: رزومه حرفه‌ای — TehNet */
defined('ABSPATH') || exit;
get_header();
while (have_posts()) {
    the_post();
    echo '<article class="tn-profile">';
    the_content();
    echo '</article>';
}
?>
</main>
<footer class="tn-container tn-profile-foot"><span>امیررضا گل‌آور | شبکه، زیرساخت و آموزش</span><a href="<?php echo esc_url(home_url('/')); ?>">بازگشت به تهران نتورک ←</a></footer>
<?php wp_footer(); ?>
</body></html>
