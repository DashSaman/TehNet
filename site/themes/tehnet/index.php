<?php
defined('ABSPATH') || exit;
get_header();

if (have_posts()) {
    while (have_posts()) {
        the_post();
        ?>
        <article <?php post_class('tn-card tn-post-card'); ?> id="post-<?php the_ID(); ?>">
            <?php if (! is_singular()) : ?>
                <h2 class="tn-post-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
                <div class="tn-post-meta"><?php echo esc_html(get_the_date()); ?></div>
                <div class="entry-content tn-post-excerpt">
                    <?php
                    if (has_excerpt()) {
                        the_excerpt();
                    } else {
                        echo '<p>' . esc_html(wp_trim_words(get_the_content(), 32, '…')) . '</p>';
                    }
                    ?>
                    <p class="tn-readmore"><a class="wp-block-button__link" href="<?php the_permalink(); ?>">ادامه مطلب</a></p>
                </div>
            <?php else : ?>
                <h1><?php the_title(); ?></h1>
                <div class="tn-post-meta"><?php echo esc_html(get_the_date()); ?></div>
                <div class="entry-content">
                    <?php the_content(); ?>
                </div>
            <?php endif; ?>
        </article>
        <?php
    }
} else {
    ?>
    <section class="tn-card">
        <h1><?php esc_html_e('محتوایی پیدا نشد', 'tehnet'); ?></h1>
    </section>
    <?php
}

get_footer();
