"""Local recovery verification. No production host or financial mutation."""
import hashlib
import json
import os
import frappe

def audit():
    if os.environ.get('TEHNET_SANDBOX')!='1' or not (frappe.local.site=='frontend' or frappe.local.site.startswith('tehnet-restore-')):
        frappe.throw('Local recovery sandbox only')
    tables={
        'Company':['name','default_currency'],
        'Item':['name','stock_uom','valuation_method'],
        'Bin':['item_code','warehouse','actual_qty','reserved_stock'],
        'Sales Order':['name','customer','grand_total','docstatus'],
        'Sales Invoice':['name','customer','grand_total','docstatus','is_return'],
        'GL Entry':['name','account','debit','credit','voucher_type','voucher_no','is_cancelled'],
        'TehNet Reservation':['name','order_ref','state','amount_irr'],
        'TehNet Commerce Event':['name','event_key','payload_hash'],
        'DocPerm':['parent','role','read','write','create','delete'],
    }
    result={}
    for table,fields in tables.items():
        rows=frappe.get_all(table,fields=fields,order_by='name',limit_page_length=0)
        result[table]={'count':len(rows),'sha256':hashlib.sha256(json.dumps(rows,sort_keys=True,default=str,separators=(',',':')).encode()).hexdigest()}
    return result
