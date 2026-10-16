<?php
defined('ABSPATH') || exit;
get_header();
$tn_blog_archive = is_home() && ! is_front_page();
if ($tn_blog_archive) {
    echo '<header class="tn-section"><p class="tn-kicker">یادگیری، تجربه و فناوری</p><h1>بلاگ تهران نتورک</h1></header>';
}
elseif (is_category() || is_tag()) {
    echo '<header class="tn-section"><p class="tn-kicker">آرشیو نوشته‌ها</p><h1>'.esc_html(single_term_title('',false)).'</h1>';
    if (term_description()) echo '<div class="tn-archive-description">'.wp_kses_post(term_description()).'</div>';
    echo '</header>';
}


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
        <?php if ($tn_blog_archive) : ?><p><?php esc_html_e('هنوز نوشته‌ای منتشر نشده است.', 'tehnet'); ?></p><?php else : ?><h1><?php esc_html_e('محتوایی پیدا نشد', 'tehnet'); ?></h1><?php endif; ?>
    </section>
    <?php
}

get_footer();
