"""Read-only native published URL/media inventory. No settings or content writes."""
from pathlib import Path
import argparse,datetime,json,shlex,subprocess
parser=argparse.ArgumentParser();parser.add_argument('--out',default='seo/audit-2026-10-16');args=parser.parse_args()
root=Path(__file__).resolve().parents[1];out=root/args.out;out.mkdir(parents=True,exist_ok=True)
php=r'''
$types=get_post_types(['public'=>true],'names');unset($types['attachment']);$posts=[];
foreach(get_posts(['post_type'=>array_values($types),'post_status'=>'publish','numberposts'=>-1,'orderby'=>'ID','order'=>'ASC'])as $p){
 $row=['id'=>$p->ID,'type'=>$p->post_type,'parent'=>$p->post_parent,'slug'=>$p->post_name,'title'=>get_the_title($p),'url'=>get_permalink($p),'modified'=>$p->post_modified_gmt,'content_chars'=>mb_strlen(wp_strip_all_tags($p->post_content)),'content_sha256'=>hash('sha256',wp_strip_all_tags($p->post_content)),'excerpt_chars'=>mb_strlen(wp_strip_all_tags($p->post_excerpt))];
 if($p->post_type==='product'){$x=wc_get_product($p->ID);$frames=$x->get_meta('_tn_spin_attachment_ids',true);$row['media']=['primary'=>(int)$x->get_image_id(),'gallery'=>array_map('intval',$x->get_gallery_image_ids()),'spin_reviewed'=>$x->get_meta('_tn_spin_reviewed'),'spin_ids'=>$frames,'sku'=>$x->get_sku(),'source_key'=>$x->get_meta('_tn_source_key'),'sale_approved'=>$x->get_meta('_tn_sale_approved')];}
 $posts[]=$row;
}
$terms=[];foreach(get_taxonomies(['public'=>true],'names')as $tax){foreach(get_terms(['taxonomy'=>$tax,'hide_empty'=>true])as $t){$url=get_term_link($t);if(!is_wp_error($url))$terms[]=['taxonomy'=>$tax,'id'=>$t->term_id,'name'=>$t->name,'count'=>$t->count,'description_chars'=>mb_strlen(wp_strip_all_tags($t->description)),'url'=>$url];}}
$files=[];foreach(['wp-content/mu-plugins/tehnet-search-metadata.php','wp-content/plugins/tehnet-core/includes/class-schema.php','wp-content/plugins/tehnet-store/includes/class-product-visuals.php']as $f){$p=ABSPATH.$f;$files[$f]=['exists'=>is_file($p),'sha256'=>is_file($p)?hash_file('sha256',$p):null];}
$menus=[];foreach(wp_get_nav_menus()as $m){foreach(wp_get_nav_menu_items($m->term_id)?:[] as $i)$menus[]=['menu'=>$m->name,'title'=>$i->title,'url'=>$i->url];}
echo wp_json_encode(['home'=>home_url('/'),'blog_public'=>get_option('blog_public'),'front_page_id'=>get_option('page_on_front'),'permalink_structure'=>get_option('permalink_structure'),'theme'=>wp_get_theme()->get('Version'),'posts'=>$posts,'terms'=>$terms,'menus'=>$menus,'runtime_files'=>$files]);
'''
remote=r'''
import subprocess,sys
p=subprocess.run(['docker','exec','tehnet-wordpress','php','/tmp/tn-store-review/wp-cli.phar','--allow-root','--path=/var/www/html','--user=AmirrezaGol','eval',sys.stdin.read()],capture_output=True,timeout=120)
if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
sys.stdout.buffer.write(p.stdout)
'''
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','netauto-main','python3 -c '+shlex.quote(remote)],input=php.encode(),capture_output=True,timeout=150)
if r.returncode:raise RuntimeError((r.stdout+r.stderr).decode(errors='replace'))
data=json.loads(r.stdout);data['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();data['scope']='Native read-only published content inventory; no private posts, orders or customer data.'
(out/'native-inventory.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
from collections import Counter
print(json.dumps({'published_types':dict(Counter(p['type']for p in data['posts'])),'terms':len(data['terms']),'menu_links':len(data['menus']),'blog_public':data['blog_public'],'runtime_files':data['runtime_files']},ensure_ascii=True))
