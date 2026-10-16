"""Fresh independent checks for this media change; does not claim local Docker/Woo/ERP ran."""
from pathlib import Path
import datetime,json,subprocess
root=Path(__file__).resolve().parents[1];php=str(root.parent/'php-runtime/php.exe')
checks=[('photo-render-contracts',[php,'tests/product-photos-unit.php']),('photo-import-contracts',[php,'tests/photo-import-unit.php'])]
for file in ['ops/import-catalog-photos.php','site/plugins/tehnet-store/includes/class-product-visuals.php','site/plugins/tehnet-store/includes/class-storefront.php','site/plugins/tehnet-store/tehnet-store.php']:
 checks.append(('php-lint:'+file,[php,'-l',file]))
checks.append(('photo-spin-js-syntax',['node','--check','site/plugins/tehnet-store/assets/photo-spin.js']))
results=[]
for name,command in checks:
 p=subprocess.run(command,cwd=root,capture_output=True,timeout=60);output=(p.stdout+p.stderr).decode('utf-8',errors='replace');results.append({'name':name,'exit_code':p.returncode,'output':output});print(name+': '+('PASS'if not p.returncode else 'FAIL'))
 if p.returncode:print(output)
out=root/'qa/store-2026-10-16/photo-verification.json';out.write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':results,'local_docker_woo_erp_rerun':False,'docker_limitation':'Docker Desktop WSL bootstrap exit 0xc00000fd. No data reset or WSL shutdown attempted.','earlier_python_contracts':{'status':'passed','count':20,'evidence':'Fresh unittest full output in native task tool transcript on 2026-10-16'}},ensure_ascii=False,indent=2),encoding='utf-8')
if any(x['exit_code']for x in results):raise SystemExit(1)
print('PHOTO_CHANGE_VERIFICATION=PASSED')
