"""Fresh local contracts plus reconciliation of the recorded native/public release evidence."""
from pathlib import Path
import datetime,hashlib,json,subprocess,sys
root=Path(__file__).resolve().parents[1];out=root/'seo/remediation-2026-10-16';php=root.parent/'php-runtime/php.exe'
results=[]
for script in ['search-metadata-test.php','product-evidence-unit.php','technical-resources-unit.php','product-photos-unit.php']:
 r=subprocess.run([str(php),str(root/'tests'/script)],cwd=root,capture_output=True,text=True,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr;results.append({'command':script,'exit_code':r.returncode,'output':r.stdout.strip()})
r=subprocess.run([sys.executable,str(root/'tests/technical-resources-python.py')],cwd=root,capture_output=True,text=True,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr;results.append({'command':'technical-resources-python.py','exit_code':0,'output':(r.stdout+r.stderr).strip()})
for path in [root/'site/mu-plugins/tehnet-search-metadata.php',root/'site/mu-plugins/tehnet-technical-resources.php',root/'site/plugins/tehnet-store/includes/class-product-evidence.php',root/'ops/remediate-site-content.php']:
 r=subprocess.run([str(php),'-l',str(path)],capture_output=True,text=True,encoding='utf-8');assert r.returncode==0,r.stdout+r.stderr
read=lambda name:json.loads((out/name).read_text(encoding='utf-8'))
crawl=read('public-crawl.json');native=read('native-inventory.json');release=read('release.json');followup=read('release-followup.json')
assert not crawl['limit_hit']and not any('error'in x for x in crawl['pages']);assert all(any(p['url']==x['url']for p in crawl['pages'])for x in native['posts'])
unique=list({p['final_url']:p for p in crawl['pages']if p.get('status')==200}.values())
assert len(unique)==70
assert all(len(x['descriptions'])==len(x['canonicals'])==len(x['h1'])==len(x['og']['image'])==1 for x in unique)
assert all(any('noindex'in r for r in x['robots'])for x in unique)
assert not any(s.get('invalid')for x in unique for s in x['schemas'])
assert all(x.get('status')==200 or '/cdn-cgi/l/email-protection'in x['url']for x in crawl['pages'])
products=[p for p in native['posts']if p['type']=='product'];assert len(products)==25;assert len({p['title']for p in products})==len({p['content_sha256']for p in products})==25
assert all(p['media']['sale_approved']!='yes'and not p['media']['spin_ids']and p['media']['spin_reviewed']!='yes'for p in products)
assert native['blog_public']=='0'and len(native['menus'])==8
assert release['applied']['protected_state_unchanged']and followup['applied']['protected_state_unchanged']and release['backup_checksums_verified']and followup['backup_checksums_verified']
assert all(release['repeat'][k]==0 for k in ['posts_updated','terms_updated','pages_created'])
assert release['preflight']['guarded']==release['after']['guarded']==followup['after']['guarded']
for name,digest in followup['files'].items():assert hashlib.sha256((root/'site'/name).read_bytes()).hexdigest()==digest,'Source differs from latest native release: '+name
assert read('live-browser.json')['status']=='passed';assert len(read('local-browser.json')['checks'])>=13;assert all(not r['violations']for r in read('a11y-after.json'))
for name in ['qa/store-2026-10-15/live-browser.json','qa/store-2026-10-16/live-photos-browser.json']:
 v=json.loads((root/name).read_text(encoding='utf-8'));assert v['status']=='passed'
value={'status':'passed','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Fresh local tests; recorded native release invariants, full public crawl and fresh production browser results. No real payment/order/router test or genuine product360 asserted.','local_contracts':results,'public_unique_successful_pages':len(unique),'published_items':len(native['posts']),'products':len(products),'unique_product_bodies':25,'unique_product_titles':25,'single_description_og_h1_canonical':70,'noindex_preserved_pages':70,'main_home_menu_product_meta_orders_gates_preserved':True,'browser_checks':len(read('live-browser.json')['checks']),'synthetic_renderer_checks':len(read('local-browser.json')['checks']),'real_product_models':0,'real_product_spin_sequences':0,'limitations':['GSC/Ahrefs plan access remains unavailable','Product physical identity and exact-model licensed360 media unverified','Index activation awaits separate launch approval','No new live ERP/payment or full local Docker stack test','Public full renderer download attempt aborted after HTTP200; HEAD200, native file SHA and actual synthetic local rendering verified']}
(out/'verification.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('REMEDIATION_VERIFICATION=PASSED;70 pages;25 distinct products;noindex and protected data preserved')
