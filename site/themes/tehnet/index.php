<?php
defined('ABSPATH') || exit;
get_header();

if (have_posts()) {
    while (have_posts()) {
        the_post();
        ?>
        <article <?php post_class('tn-card'); ?> id="post-<?php the_ID(); ?>">
            <?php if (! is_singular()) : ?>
                <h2><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
            <?php else : ?>
                <h1><?php the_title(); ?></h1>
            <?php endif; ?>
            <div class="entry-content">
                <?php the_content(); ?>
            </div>
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
