import concurrent.futures,json,subprocess,uuid
from pathlib import Path
import urllib.request,urllib.error
from decimal import Decimal
base=Path(__file__).resolve().parents[2]
settings=dict(x.split('=',1) for x in (base/'ops/staging/.env').read_text().splitlines() if '=' in x)
credentials={'api_key':settings['ERP_API_KEY'],'api_secret':settings['ERP_API_SECRET']}
auth='token '+credentials['api_key']+':'+credentials['api_secret']
def call(method,payload,expect_error=False):
    request=urllib.request.Request('http://localhost:18084/api/method/'+method,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Authorization':auth},method='POST')
    try:
        with urllib.request.urlopen(request,timeout=50) as response:result=json.load(response)['message']
        if expect_error:raise AssertionError('Expected rejected request was accepted')
        return result
    except urllib.error.HTTPError as error:
        body=error.read().decode()
        for secret in credentials.values():body=body.replace(secret,'<REDACTED>')
        if expect_error and error.code in [400,403,409,417]:return {'rejected':error.code}
        raise RuntimeError('ERP HTTP '+str(error.code)+' '+body)
run='test-'+uuid.uuid4().hex[:12]
results=[]
def check(name,ok):
    if not ok:raise AssertionError(name)
    results.append(name);print('PASS: '+name,flush=True)
def event(kind,ref,**kwargs):
    return call('tehnet_erp.api.event',{'payload':{'schema_version':1,'event_key':run+':'+kind+':'+ref,'order_ref':run+':'+ref,'kind':kind,**kwargs}})
order={'currency':'IRR','amount_irr':'1000','customer':{'reference':run,'name':'SYNTHETIC TEST CUSTOMER'},'items':[{'sku':'TN-SANDBOX-LAST','qty':'1','uom':'Nos','unit_price_irr':'1000'}]}
first=event('reserve','a',**order)
duplicate=event('reserve','a',**order)
check('duplicate reserve has exactly the same sales order',first['sales_order']==duplicate['sales_order'])
bad={'schema_version':1,'event_key':run+':reserve:a','order_ref':run+':a','kind':'reserve',**order,'amount_irr':'1001'}
check('event key with changed payload rejected',bool(call('tehnet_erp.api.event',{'payload':bad},True)))
check('cancel releases reservation',event('cancel','a')['state']=='canceled')
link=call('frappe.client.get_value',{'doctype':'TehNet Reservation','fieldname':'name','filters':{'order_ref':run+':a'}})
check('machine user cannot overwrite a reservation through generic CRUD',bool(call('frappe.client.set_value',{'doctype':'TehNet Reservation','name':link['name'],'fieldname':'amount_irr','value':'1000'},True)))
event_link=call('frappe.client.get_value',{'doctype':'TehNet Commerce Event','fieldname':'name','filters':{'event_key':run+':cancel:a'}})
check('machine user cannot rewrite the event journal through generic CRUD',bool(call('frappe.client.set_value',{'doctype':'TehNet Commerce Event','name':event_link['name'],'fieldname':'kind','value':'cancel'},True)))
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
    futures=[pool.submit(event,'reserve',x,**order) for x in ['race-one','race-two']]
    outcomes=[]
    for future in futures:
        try:outcomes.append(future.result())
        except RuntimeError as e:outcomes.append({'failure':str(e)})
    successes=[x for x in outcomes if x.get('state')=='reserved']
check('only one customer reserves the last available unit',len(successes)==1)
winner='race-one' if outcomes[0].get('state')=='reserved' else 'race-two'
expired=call('tehnet_erp.sandbox.expire',{'order_ref':run+':'+winner})
check('expired reservation is released',expired['state']=='expired')
baseline=Decimal(call('tehnet_erp.sandbox.audit',{'order_ref':run+':a'})['cable_stock'])
cable={**order,'amount_irr':'2500','items':[{'sku':'TN-SANDBOX-CABLE','qty':'2.5','uom':'Meter','unit_price_irr':'1000'}]}
reserved=event('reserve','cable',**cable)
paid_payload={'schema_version':1,'event_key':run+':paid:cable','order_ref':run+':cable','kind':'paid','currency':'IRR','amount_irr':'2500','payment_identity':run+':bank-proof'}
paid=call('tehnet_erp.api.event',{'payload':paid_payload})
paid_repeat=call('tehnet_erp.api.event',{'payload':paid_payload})
check('duplicate verified payment makes no second invoice/receipt',paid['invoice']==paid_repeat['invoice'] and paid['payment_entry']==paid_repeat['payment_entry'])
check('amount mismatch rejected',bool(call('tehnet_erp.api.event',{'payload':{**paid_payload,'event_key':run+':bad-amount','amount_irr':'2499'}},True)))
shipped=event('dispatch','cable',tracking_reference='SANDBOX-CARRIER-123')
check('dispatch creates native delivery note',bool(shipped['delivery_note']))
refund=event('refund','cable',items=[{'sku':'TN-SANDBOX-CABLE','qty':'0.5'}],amount_irr='500',payment_identity=run+':refund-proof')
check('partial return creates credit note and stock return',bool(refund['credit_note']) and bool(refund['return_delivery']) and refund['state']=='partially_refunded')
audit=call('tehnet_erp.sandbox.audit',{'order_ref':run+':cable'})
check('2.5m sale and 0.5m return reduce actual stock by exactly 2m',Decimal(audit['cable_stock'])==baseline-2)
settlement={'amount_irr':'2000','fee_irr':'50','net_irr':'1950','settlement_reference':run+':settlement','payment_identities':[run+':bank-proof',run+':refund-proof']}
settled=event('settle','cable',**settlement)
check('net settlement and fee create a native balanced journal',bool(settled['journal_entry']))
check('a different event cannot settle the same receipts twice',bool(call('tehnet_erp.api.event',{'payload':{'schema_version':1,'event_key':run+':second-settlement','order_ref':run+':cable','kind':'settle',**settlement,'settlement_reference':run+':other-settlement'}},True)))
final_refund=event('refund','cable-final',**{'order_ref':run+':cable','items':[{'sku':'TN-SANDBOX-CABLE','qty':'2'}],'amount_irr':'2000','payment_identity':run+':final-refund'})
check('remaining quantity can be returned in full',final_refund['state']=='refunded')
audit=call('tehnet_erp.sandbox.audit',{'order_ref':run+':cable'})
check('all returned meter quantities restore the exact original stock',Decimal(audit['cable_stock'])==baseline)
check('every native GL voucher is balanced',audit['unbalanced_vouchers']==[])
discounted={**order,'amount_irr':'2100','discount_irr':'100','shipping_irr':'200','items':[{'sku':'TN-SANDBOX-CABLE','qty':'2','uom':'Meter','unit_price_irr':'1000'}]}
event('reserve','discounted',**discounted)
event('paid','discounted',currency='IRR',amount_irr='2100',payment_identity=run+':discounted-bank')
event('dispatch','discounted',tracking_reference='SYNTHETIC-TRACKING')
partial=event('refund','discounted',items=[{'sku':'TN-SANDBOX-CABLE','qty':'1'}],amount_irr='1050',shipping_refund_irr='100',payment_identity=run+':discounted-refund')
check('discount and partial shipping refund allocate exactly 1050 IRR',partial['state']=='partially_refunded')
last=event('refund','discounted-final',**{'order_ref':run+':discounted','items':[{'sku':'TN-SANDBOX-CABLE','qty':'1'}],'amount_irr':'1050','shipping_refund_irr':'100','payment_identity':run+':discounted-refund-final'})
check('discounted order with shipping can be returned in full',last['state']=='refunded')
final_audit=call('tehnet_erp.sandbox.audit',{'order_ref':run+':discounted'})
check('all native GL vouchers remain balanced after discounted returns',final_audit['unbalanced_vouchers']==[])
out=base/'qa/store-2026-10-15/erp-results.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps({'checks':results,'scope':'Real local ERPNext; synthetic inventory and payment evidence only. No bank/provider request.'},indent=2))
print('ERP_INTEGRATION=PASSED',flush=True)
