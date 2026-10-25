import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def after_install():
    if not frappe.db.exists('Role','TehNet Integration'):
        frappe.get_doc({'doctype':'Role','role_name':'TehNet Integration','desk_access':0}).insert()
    definitions={
        'TehNet Commerce Event':[
            ('event_key','Data',None,1),('payload_hash','Data',None,1),('order_ref','Data',None,0),
            ('kind','Data',None,1),('outcome','Long Text',None,0),
        ],
        'TehNet Reservation':[
            ('order_ref','Data',None,1),('sales_order','Link','Sales Order',1),('state','Select','reserved\npaid\ncanceled\nexpired\ndispatched\npartially_refunded\nrefunded',1),
            ('expires_at','Datetime',None,1),('order_hash','Data',None,1),('amount_irr','Currency',None,1),
            ('invoice','Link','Sales Invoice',0),('payment_entry','Link','Payment Entry',0),('delivery_note','Link','Delivery Note',0),
            ('payment_identity','Data',None,0),('refund_total_irr','Currency',None,0),('shipping_refund_irr','Currency',None,0),('tracking_reference','Data',None,0),
        ],
    }
    for name,fields in definitions.items():
        if frappe.db.exists('DocType',name):
            doc=frappe.get_doc('DocType',name)
            for key,kind,options,required in fields:
                if not any(f.fieldname==key for f in doc.fields):
                    doc.append('fields',{'fieldname':key,'label':key.replace('_',' ').title(),'fieldtype':kind,'options':options,'reqd':required})
            for permission in doc.permissions:
                if permission.role=='TehNet Integration':permission.read=1;permission.write=0;permission.create=0;permission.delete=0
            doc.save()
            continue
        frappe.get_doc({'doctype':'DocType','name':name,'module':'TehNet Operations','custom':1,'track_changes':1,
            'fields':[{'fieldname':key,'label':key.replace('_',' ').title(),'fieldtype':kind,'options':options,'reqd':required,'unique':1 if key in ('event_key','order_ref') and name=='TehNet Reservation' else 0} for key,kind,options,required in fields],
            'permissions':[{'role':'TehNet Integration','read':1,'write':0,'create':0,'delete':0,'report':1},{'role':'System Manager','read':1,'write':1,'create':1,'delete':0,'report':1}],
        }).insert()
    create_custom_fields({
        'Payment Entry':[
            {'fieldname':'tn_payment_identity','label':'TehNet external payment identity','fieldtype':'Data','unique':1,'read_only':1,'no_copy':1},
            {'fieldname':'tn_settlement_journal','label':'TehNet settlement journal','fieldtype':'Link','options':'Journal Entry','read_only':1,'no_copy':1},
        ],
        'Journal Entry':[{'fieldname':'tn_settlement_reference','label':'TehNet settlement reference','fieldtype':'Data','unique':1,'read_only':1,'no_copy':1}],
    })
