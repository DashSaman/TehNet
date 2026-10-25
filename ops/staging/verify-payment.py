"""Portable protocol/state checks. Mocks Woo/ERP; does not claim native checkout.

Provide --php for an installed PHP >=8.2. No downloads, secrets or production I/O.
"""
import argparse,datetime,json,re,subprocess,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--php',default='php');args=parser.parse_args()
    results=[]
    def run(name,command,expected_failure=False):
        process=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60)
        output=(process.stdout+process.stderr).decode('utf-8',errors='replace')
        ok=(process.returncode!=0 and 'Sandbox payment is not verified' in output) if expected_failure else process.returncode==0
        results.append({'name':name,'passed':ok,'expected_failure':expected_failure,'exit_code':process.returncode,'output':output})
        print(name+': '+('PASS' if ok else 'FAIL'),flush=True)
        if not ok:print(output,flush=True)
    for path in sorted((ROOT/'site/plugins/tehnet-store').rglob('*.php')):
        run('lint '+str(path.relative_to(ROOT)),[args.php,'-n','-l',str(path)])
    for name in ['zarinpal-protocol','zarinpal-lifecycle']:
        run(name,[args.php,'-n',str(ROOT/'tests'/f'{name}.php')])
    run('blocks JavaScript syntax',['node','--check',str(ROOT/'site/plugins/tehnet-store/assets/zarinpal-blocks.js')])
    # Prove that removing 101 support breaks the recovery contract; live source is untouched.
    scratch=ROOT/'ops/staging/.local';scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='tn-zarinpal-regression-',dir=scratch) as folder:
        if not Path(folder).resolve().is_relative_to(scratch.resolve()):raise RuntimeError('Scratch path escaped the local workspace')
        source=Path(folder)/'adapter.php';test=Path(folder)/'test.php'
        source.write_text((ROOT/'site/plugins/tehnet-store/includes/class-zarinpal-sandbox.php').read_text(encoding='utf-8').replace('[100,101]','[100]'),encoding='utf-8')
        test.write_text((ROOT/'tests/zarinpal-protocol.php').read_text(encoding='utf-8').replace("__DIR__.'/../site/plugins/tehnet-store/includes/class-zarinpal-sandbox.php'","'"+source.as_posix()+"'"),encoding='utf-8')
        run('code 101 regression mutation',[args.php,'-n',str(test)],expected_failure=True)
    counts={name.lower():int(number) for result in results if not result['expected_failure'] for name,number in re.findall(r'ZARINPAL_(PROTOCOL|LIFECYCLE)=PASSED checks=(\d+)',result['output'])}
    evidence={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Portable PHP protocol and state machine with mocked Woo/ERP/HTTP; no native checkout claim','unique_assertions':counts,'checks':results}
    (ROOT/'qa/store-2026-10-15/payment-verification.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    if not all(r['passed'] for r in results):raise SystemExit(1)
    print('PAYMENT_CONTRACTS=PASSED')
if __name__=='__main__':main()
