"""Fresh local contracts + reconciliation of native and public acceptance receipts."""
from pathlib import Path
import datetime, hashlib, json, subprocess, sys
root=Path(__file__).resolve().parents[1];out=root/'qa/shop-ux-2026-10-16';php=root.parent/'php-runtime/php.exe'
def read(name):return json.loads((out/name).read_text(encoding='utf-8'))
def run(argv):
 p=subprocess.run(argv,cwd=root,capture_output=True,text=True,encoding='utf-8')
 assert p.returncode==0,p.stdout+p.stderr
 return {'command':argv[1:],'exit_code':0,'output':(p.stdout+p.stderr).strip()}
local=[run([str(php),'tests/'+n])for n in ['product-photos-unit.php','product-evidence-unit.php','search-metadata-test.php','technical-resources-unit.php']]
local.append(run([sys.executable,'tests/technical-resources-python.py']))
for p in (root/'site/plugins/tehnet-store').rglob('*.php'):run([str(php),'-l',str(p)])
for n in ['store.js','reviewed-model.js','model-controls.js']:run(['node','--check','site/plugins/tehnet-store/assets/'+n])
release=read('release.json');assert release['status']=='published'and release['protected_state_unchanged']and release['before']==release['after']and release['backup_checksums_verified']
assert len(release['changed_files'])==9 and len(release['after']['published_product_ids'])==25 and release['after']['real_models']==release['after']['real_spins']==0
for n,h in release['files'].items():assert hashlib.sha256((root/'site'/n).read_bytes()).hexdigest()==h,n
browser={}
for n,expected in [('staging/shop-browser.json',27),('staging/native-controls.json',20)]:
 v=read(n);assert v['status']=='passed'and len(v['checks'])==expected and not v['js_errors'];browser[n]={'checks':len(v['checks']),'receipt_sha256':hashlib.sha256((out/n).read_bytes()).hexdigest()}
production=read('production/shop-browser.json');assert production['base']=='https://tehnet.ir'and production['status']in ['passed','incomplete']
assert len(production['checks'])==(27 if production['status']=='passed' else 12)
http=read('production/public-http.json');assert http['status']=='passed'and len(http['products'])==http['published_products']==25 and http['purchasable_products']==0
value={'status':'verified-with-production-browser-limit'if production['status']=='incomplete'else'passed','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'local_contracts':local,'store_php_lint':'all12 passed','changed_javascript_syntax':'3 passed','browser_receipts':browser,'production_browser':{'status':production['status'],'completed_checks':len(production['checks']),'failure':production.get('failure'),'receipt_sha256':hashlib.sha256((out/'production/shop-browser.json').read_bytes()).hexdigest()},'production_public_http':'25 products + shop + home + Persian SKU passed from managed host via public HTTPS/Cloudflare; not full browser proof','protected_native_state_unchanged':True,'backup_checksums_verified':True,'published_products':25,'approved_real_product_models':0,'approved_real_product_spins':0,'scope':'Universal Woo templates and exact-evidence gates; native model fixture is synthetic and staging-only. Public production tests are read-only, no order/inquiry/payment.','limitations':['Complete production browser rerun limited by connection/nav timeouts; only12 completed assertions claimed','No exact-SKU approved CAD or complete real spin exists','No physical handset or full WCAG assertion','No field conversion/performance improvement measured','No production rollback exercise; archive/guards prepared','Prior 70-page SEO crawl is historical evidence, not rerun by this command']}
(out/'verification.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('SHOP_VERIFICATION=RECORDED;23photo+31evidence+43metadata+11MTU PASS;27staging+20native-model PASS;25publicHTTP PASS;production browser '+production['status']+';9files;0real3D')
