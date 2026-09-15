<?php
defined('ABSPATH') || exit;
get_header();

while (have_posts()) {
    the_post();
    ?>
    <article <?php post_class(); ?> id="post-<?php the_ID(); ?>">
        <div class="entry-content">
            <?php the_content(); ?>
        </div>
    </article>
    <?php
}

get_footer();
