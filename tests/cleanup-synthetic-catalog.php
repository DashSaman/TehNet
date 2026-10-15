<?php
if (wp_get_environment_type()!=='local') { throw new RuntimeException('Local fixtures only'); }
$groups=[];
foreach (get_posts(['post_type'=>'product','post_status'=>'draft','numberposts'=>-1,'meta_query'=>[['key'=>'_tn_source_id','value'=>100000000,'compare'=>'>','type'=>'NUMERIC']]]) as $post) {
    if (!str_starts_with($post->post_title,'SYNTHETIC IMPORT TEST: ')) { continue; }
    $run=get_post_meta($post->ID,'_tn_catalog_run',true);
    if ($run) { $groups[$run]=true; }
}
foreach (array_keys($groups) as $run) {
    $journal=get_option('tn_catalog_run_'.$run);
    foreach ($journal['created']??[] as $id) {
        if (!str_starts_with(get_the_title($id),'SYNTHETIC IMPORT TEST: ')) { throw new RuntimeException('Fixture ownership is not intact'); }
    }
    $result=(new TehNet_Store_Catalog())->rollback($run);
    echo 'Own interrupted fixture run soft-trashed: '.count($result['trashed'])."\n";
}
