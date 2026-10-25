"""Synthetic local fixtures only. Never a production migration or opening balance."""
import os
from decimal import Decimal
import frappe

def guard():
    if os.environ.get('TEHNET_SANDBOX')!='1' or frappe.local.site!='frontend':
        frappe.throw('Synthetic fixtures are restricted to the isolated local sandbox')

def setup():
    guard()
    company='TehNet Sandbox';c=frappe.get_doc('Company',company)
    if c.default_currency!='IRR':frappe.throw('Sandbox company must use IRR')
    warehouses=frappe.get_all('Warehouse',filters={'company':company,'is_group':0,'disabled':0},pluck='name')
    warehouse=next((w for w in warehouses if w.startswith('Stores')),warehouses[0])
    price_list='TehNet Sandbox Selling'
    if not frappe.db.exists('Price List',price_list):frappe.get_doc({'doctype':'Price List','price_list_name':price_list,'currency':'IRR','selling':1,'enabled':1}).insert()
    group='TehNet Sandbox Customers'
    if not frappe.db.exists('Customer Group',group):frappe.get_doc({'doctype':'Customer Group','customer_group_name':group,'parent_customer_group':'All Customer Groups','is_group':0}).insert()
    territory='Iran'
    if not frappe.db.exists('Territory',territory):frappe.get_doc({'doctype':'Territory','territory_name':territory,'parent_territory':'All Territories'}).insert()
    def account(name,root,kind):
        current=frappe.db.get_value('Account',{'account_name':name,'company':company},'name')
        if current:return current
        parent=frappe.db.get_value('Account',{'company':company,'root_type':root,'is_group':1,'account_name':'Bank Accounts' if kind=='Bank' else 'Indirect Expenses'},'name')
        if not parent:parent=frappe.db.get_value('Account',{'company':company,'root_type':root,'is_group':1,'parent_account':['in',['',None]]},'name')
        doc=frappe.get_doc({'doctype':'Account','account_name':name,'company':company,'parent_account':parent,'account_type':kind,'account_currency':'IRR','is_group':0});doc.insert();return doc.name
    clearing=account('TehNet Sandbox Gateway Clearing','Asset','Bank')
    bank=account('TehNet Sandbox Bank','Asset','Bank')
    fee=account('TehNet Sandbox Gateway Fees','Expense','Expense Account')
    settings={'company':company,'warehouse':warehouse,'price_list':price_list,'customer_group':group,'territory':territory,'clearing_account':clearing,'bank_account':bank,'fee_account':fee,'shipping_income_account':c.default_income_account}
    for key,value in settings.items():frappe.conf['tehnet_'+key]=value
    from frappe.installer import update_site_config
    for key,value in settings.items():update_site_config('tehnet_'+key,value)
    frappe.db.set_single_value('Stock Settings','enable_stock_reservation',1)
    frappe.db.set_single_value('Stock Settings','allow_partial_reservation',0)
    frappe.db.set_single_value('Stock Settings','allow_negative_stock',0)
    for uom,whole in [('Meter',0),('Roll',1)]:
        if not frappe.db.exists('UOM',uom):frappe.get_doc({'doctype':'UOM','uom_name':uom,'must_be_whole_number':whole}).insert()
    for sku,uom in [('TN-SANDBOX-LAST','Nos'),('TN-SANDBOX-CABLE','Meter')]:
        if not frappe.db.exists('Item',sku):
            doc=frappe.get_doc({'doctype':'Item','item_code':sku,'item_name':sku+' — SYNTHETIC TEST ONLY','item_group':'Products','stock_uom':uom,'is_stock_item':1,'valuation_method':'FIFO','include_item_in_manufacturing':0})
            if uom=='Meter':doc.append('uoms',{'uom':'Roll','conversion_factor':305})
            doc.insert()
        if not frappe.db.exists('Item Price',{'item_code':sku,'price_list':price_list,'uom':uom}):frappe.get_doc({'doctype':'Item Price','item_code':sku,'price_list':price_list,'currency':'IRR','uom':uom,'price_list_rate':1000}).insert()
    if not frappe.db.exists('Stock Entry',{'remarks':'TEHNET SYNTHETIC INITIAL STOCK'}):
        doc=frappe.new_doc('Stock Entry');doc.stock_entry_type='Material Receipt';doc.company=company;doc.remarks='TEHNET SYNTHETIC INITIAL STOCK'
        for sku,qty,uom in [('TN-SANDBOX-LAST',1,'Nos'),('TN-SANDBOX-CABLE',305,'Meter')]:doc.append('items',{'item_code':sku,'qty':qty,'uom':uom,'conversion_factor':1,'t_warehouse':warehouse,'basic_rate':600,'allow_zero_valuation_rate':0})
        doc.insert();doc.submit()
    user='tehnet-integration@example.invalid'
    if not frappe.db.exists('User',user):
        frappe.get_doc({'doctype':'User','email':user,'first_name':'TehNet Sandbox Integration','enabled':1,'send_welcome_email':0,'user_type':'System User','roles':[{'role':r} for r in ['TehNet Integration','Sales User','Stock User','Accounts User']]}).insert()
    frappe.db.commit()
    return {'company':company,'warehouse':warehouse,'currency':'IRR','stock_fixture':'SYNTHETIC ONLY','user':user}

def credentials():
    guard()
    from frappe.core.doctype.user.user import generate_keys
    user='tehnet-integration@example.invalid'
    secret=generate_keys(user)['api_secret']
    return {'api_key':frappe.db.get_value('User',user,'api_key'),'api_secret':secret}

@frappe.whitelist(methods=['POST'])
def audit(order_ref):
    guard();frappe.only_for('TehNet Integration')
    from .api import outcome
    row=frappe.get_doc('TehNet Reservation',{'order_ref':order_ref})
    stock=frappe.db.get_value('Bin',{'warehouse':frappe.conf.tehnet_warehouse,'item_code':'TN-SANDBOX-CABLE'},'actual_qty')
    gl=frappe.db.sql('SELECT voucher_type,voucher_no,SUM(debit)-SUM(credit) AS difference FROM `tabGL Entry` WHERE company=%s AND is_cancelled=0 GROUP BY voucher_type,voucher_no',(frappe.conf.tehnet_company,),as_dict=True)
    return {**outcome(row),'cable_stock':str(stock),'unbalanced_vouchers':[x for x in gl if Decimal(str(x.difference))!=0]}

@frappe.whitelist(methods=['POST'])
def expire(order_ref):
    guard();frappe.only_for('TehNet Integration')
    from frappe.utils import add_to_date,now_datetime
    from .api import reservation,expire_reservations,outcome
    row=reservation(order_ref)
    if row.state!='reserved':frappe.throw('Only synthetic unpaid reservation may be advanced past expiry')
    row.expires_at=add_to_date(now_datetime(),minutes=-1);row.save(ignore_permissions=True);expire_reservations()
    row.reload();return outcome(row)
