"""Run the real local checks and preserve full diagnostics; no production target."""
from pathlib import Path
import datetime,json,subprocess,sys
root=Path(__file__).resolve().parents[2]
wp=['docker','exec','tehnet-woo-stage-woo-1','php','/stage/wp-cli.phar','--allow-root','--path=/var/www/html','eval-file']
checks=[('python-contracts',[sys.executable,'-X','utf8','-m','unittest','discover','-s','tests','-p','test_*.py','-v']),
        ('visual-regression',[sys.executable,'-X','utf8','tests/visual-refresh-test.py'])]
for name in ['store-policy','catalog-integration','commerce-capabilities','store-roles','erp-bridge','erp-lifecycle','online-release','store-discovery']:
    checks.append((name,wp+['/tests/'+name+'.php']))
results=[]
for name,command in checks:
    process=subprocess.run(command,cwd=root,capture_output=True,timeout=180)
    output=(process.stdout+process.stderr).decode('utf-8',errors='replace')
    results.append({'name':name,'exit_code':process.returncode,'output':output})
    print(name+': '+('PASS' if process.returncode==0 else 'FAIL'),flush=True)
    if process.returncode:print(output,flush=True)
path=root/'qa/store-2026-10-15/local-verification.json'
path.write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Local synthetic fixtures only','checks':results},ensure_ascii=False,indent=2),encoding='utf-8')
if any(row['exit_code'] for row in results):raise SystemExit(1)
print('LOCAL_VERIFICATION=PASSED',flush=True)
