"""Explicit, standalone public sandbox probe. Never connects to production or ERP.

request: prints a sandbox StartPay URL; complete only its synthetic Pay/Cancel UI.
verify AUTHORITY: checks mismatched amount, valid receipt and repeated verification.
This is NOT an end-to-end Woo checkout test. No personal/card data is sent/stored.
"""
import argparse,datetime,json,re,urllib.request,urllib.error
from pathlib import Path
BASE='https://sandbox.zarinpal.com/pg/v4/payment/'
MERCHANT='e6374c3a-e0f0-553f-ae81-32734b0bc0a8'
def call(method,payload):
    request=urllib.request.Request(BASE+method+'.json',data=json.dumps({'merchant_id':MERCHANT,**payload}).encode(),headers={'Content-Type':'application/json','Accept':'application/json'})
    try: response=urllib.request.urlopen(request,timeout=30)
    except urllib.error.HTTPError as error: response=error
    with response:
        body=json.load(response)
        # Preserve only protocol evidence; never retain PAN/hash or customer fields.
        return {'http':response.status,'data':{k:v for k,v in body.get('data',{}).items() if k in ['code','message','authority','ref_id','fee','fee_type']},'errors':body.get('errors',[])}
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['request','verify']);parser.add_argument('authority',nargs='?')
    parser.add_argument('--output',type=Path);args=parser.parse_args()
    if args.action=='request':
        result=call('request',{'amount':11000,'currency':'IRR','description':'TehNet SYNTHETIC sandbox probe; no real money','callback_url':'http://localhost:18083/?tn_sandbox_probe=1'})
        authority=result['data'].get('authority','')
        if result['http']!=200 or result['data'].get('code')!=100 or not re.fullmatch(r'S[A-Za-z0-9]{35}',authority):raise RuntimeError('Sandbox request failed: '+json.dumps(result))
        print('https://sandbox.zarinpal.com/pg/StartPay/'+authority)
        results=[result]
    else:
        if not re.fullmatch(r'S[A-Za-z0-9]{35}',args.authority or ''):parser.error('Sandbox S authority required')
        results=[{'amount_irr':n,**call('verify',{'authority':args.authority,'amount':n})} for n in [11001,11000,11000]]
        if results[0]['data'].get('code') in [100,101] or not isinstance(results[0]['errors'],dict) or results[0]['errors'].get('code')!=-50:raise RuntimeError('Mismatched amount was not rejected')
        if results[1]['data'].get('code') not in [100,101] or results[2]['data'].get('code')!=101:raise RuntimeError('Sandbox payment is not verified')
        if results[1]['data'].get('ref_id')!=results[2]['data'].get('ref_id'):raise RuntimeError('Receipt changed on replay')
    evidence={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Actual public provider sandbox, standalone protocol only; no Woo/ERP checkout','authority':authority if args.action=='request' else args.authority,'merchant_test_uuid':MERCHANT,'results':results}
    if args.output:args.output.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(evidence,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
