<?php
defined('ABSPATH') || exit;
get_header();

while (have_posts()) {
    the_post();
    ?>
    <article <?php post_class('tn-card'); ?> id="post-<?php the_ID(); ?>">
        <h1><?php the_title(); ?></h1>
        <div class="entry-content">
            <?php the_content(); ?>
        </div>
    </article>
    <?php
}

get_footer();
