"""Authenticated ERP boundary. Native ERPNext documents perform every stock/GL posting."""
from decimal import Decimal
import hashlib
import json
import re
import frappe
from frappe.utils import add_to_date,now_datetime,today,get_datetime
from .contracts import money,quantity,line_total,payload_hash,validate_money_event

def config(key):
    value=frappe.conf.get('tehnet_'+key)
    if not value:frappe.throw('TehNet configuration incomplete: '+key)
    return value

def authorize():
    frappe.only_for('TehNet Integration')

def lock_stock(items):
    warehouse=config('warehouse')
    for sku in sorted({row['sku'] for row in items}):
        rows=frappe.db.sql('SELECT name FROM `tabBin` WHERE item_code=%s AND warehouse=%s FOR UPDATE',(sku,warehouse))
        if not rows:frappe.throw('No verified stock bin for '+sku)

def reservation(order_ref):
    rows=frappe.db.sql('SELECT name FROM `tabTehNet Reservation` WHERE order_ref=%s FOR UPDATE',(order_ref,))
    if not rows:frappe.throw('Reservation not found')
    return frappe.get_doc('TehNet Reservation',rows[0][0])

def outcome(row):
    return {'order_ref':row.order_ref,'currency':'IRR','state':row.state,'sales_order':row.sales_order,'invoice':row.invoice,'delivery_note':row.delivery_note,'payment_entry':row.payment_entry,'amount_irr':str(int(Decimal(str(row.amount_irr))))}

@frappe.whitelist(methods=['POST'])
def status(order_ref):
    authorize()
    if not isinstance(order_ref,str) or not re.fullmatch(r'[A-Za-z0-9:._-]{1,120}',order_ref):frappe.throw('Invalid order reference')
    if not frappe.db.exists('TehNet Reservation',{'order_ref':order_ref}):return {'order_ref':order_ref,'found':False}
    row=reservation(order_ref)
    refunds=[]
    if row.invoice:
        for name in frappe.get_all('Sales Invoice',filters={'return_against':row.invoice,'is_return':1,'docstatus':1},pluck='name',order_by='creation'):
            credit=frappe.get_doc('Sales Invoice',name)
            paid_refs=frappe.db.sql('SELECT pe.tn_payment_identity FROM `tabPayment Entry` pe JOIN `tabPayment Entry Reference` ref ON ref.parent=pe.name WHERE pe.docstatus=1 AND pe.payment_type=%s AND ref.reference_doctype=%s AND ref.reference_name=%s',('Pay','Sales Invoice',name))
            if not any(p[0] for p in paid_refs):continue
            refunds.append({'credit_note':name,'amount_irr':whole_irr(abs(Decimal(str(credit.grand_total)))),'shipping_irr':whole_irr(abs(Decimal(str(credit.total_taxes_and_charges)))),
                'items':[{'sku':x.item_code,'uom':x.uom,'qty':str(abs(Decimal(str(x.qty)))),'amount_irr':whole_irr(abs(Decimal(str(x.net_amount))))} for x in credit.items]})
    return {**outcome(row),'found':True,'tracking_reference':row.tracking_reference,'refund_total_irr':str(int(Decimal(str(row.refund_total_irr or 0)))),'refunds':refunds}

def whole_irr(value):
    number=Decimal(str(value))
    if number<0 or number!=number.to_integral_value():frappe.throw('Fractional-rial accounting allocation requires review')
    return str(money(str(int(number))))

@frappe.whitelist(methods=['POST'])
def invoice_document(order_ref):
    authorize();row=reservation(order_ref)
    if not row.invoice:frappe.throw('No submitted invoice for this order')
    doc=frappe.get_doc('Sales Invoice',row.invoice)
    if doc.docstatus!=1 or doc.currency!='IRR':frappe.throw('Invoice is not a submitted IRR document')
    return {'invoice':doc.name,'currency':'IRR','date':str(doc.posting_date),'amount_irr':whole_irr(doc.grand_total),
        'discount_irr':whole_irr(doc.discount_amount),'shipping_irr':whole_irr(doc.total_taxes_and_charges),
        'items':[{'name':x.item_name,'sku':x.item_code,'qty':str(x.qty),'uom':x.uom,'amount_irr':whole_irr(x.net_amount)} for x in doc.items]}

@frappe.whitelist(methods=['POST'])
def catalog_snapshot(items):
    """Display cache only. Checkout always takes a fresh transactional reservation."""
    from decimal import ROUND_DOWN
    from erpnext.stock.doctype.stock_reservation_entry.stock_reservation_entry import get_available_qty_to_reserve
    authorize()
    if isinstance(items,str):items=json.loads(items)
    if not isinstance(items,list) or not 1<=len(items)<=100:frappe.throw('Invalid snapshot item list')
    result=[]
    for row in items:
        sku=row.get('sku');uom=row.get('uom')
        if not isinstance(sku,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',sku):frappe.throw('Invalid SKU')
        item=frappe.get_doc('Item',sku)
        if item.disabled or not item.is_stock_item or item.has_serial_no or item.has_batch_no:frappe.throw('Item requires a reviewed fulfillment workflow')
        conversion=Decimal(1) if uom==item.stock_uom else next((Decimal(str(x.conversion_factor)) for x in item.uoms if x.uom==uom),None)
        if conversion is None or conversion<=0:frappe.throw('Unverified unit conversion')
        prices=frappe.get_all('Item Price',filters={'item_code':sku,'price_list':config('price_list'),'uom':uom,'currency':'IRR'},fields=['price_list_rate','valid_from','valid_upto'])
        prices=[p for p in prices if (not p.valid_from or str(p.valid_from)<=today()) and (not p.valid_upto or str(p.valid_upto)>=today())]
        if len(prices)!=1:frappe.throw('A single current ERP price is required')
        rate=Decimal(str(prices[0].price_list_rate))
        if rate!=rate.to_integral_value() or rate<=0:frappe.throw('A positive whole-rial ERP price is required')
        available=max(Decimal(0),Decimal(str(get_available_qty_to_reserve(sku,config('warehouse'))))/conversion)
        quantum=Decimal(1) if frappe.db.get_value('UOM',uom,'must_be_whole_number') else Decimal('0.001')
        result.append({'sku':sku,'uom':uom,'stock_uom':item.stock_uom,'conversion_factor':str(conversion),'price_irr':str(int(rate)),'available_qty':str(available.quantize(quantum,rounding=ROUND_DOWN))})
    return {'currency':'IRR','ttl_seconds':60,'items':result}

@frappe.whitelist(methods=['POST'])
def event(payload):
    authorize()
    if isinstance(payload,str):payload=json.loads(payload)
    if not isinstance(payload,dict) or payload.get('schema_version')!=1:frappe.throw('Unsupported event schema')
    key=payload.get('event_key','');order_ref=payload.get('order_ref','')
    if not isinstance(key,str) or not re.fullmatch(r'[A-Za-z0-9:._-]{1,120}',key):frappe.throw('Invalid event key')
    if not isinstance(order_ref,str) or not re.fullmatch(r'[A-Za-z0-9:._-]{1,120}',order_ref):frappe.throw('Invalid order reference')
    handlers={'reserve':reserve,'cancel':cancel,'paid':paid,'dispatch':dispatch,'refund':refund,'settle':settle}
    kind=payload.get('kind')
    if kind not in handlers:frappe.throw('Unsupported event kind')
    name=hashlib.sha256(key.encode()).hexdigest();digest=payload_hash(payload)
    existing=frappe.db.sql('SELECT payload_hash,outcome FROM `tabTehNet Commerce Event` WHERE name=%s FOR UPDATE',(name,),as_dict=True)
    if existing:
        if existing[0].payload_hash!=digest:frappe.throw('Event key reused with conflicting payload')
        return json.loads(existing[0].outcome)
    record=frappe.get_doc({'doctype':'TehNet Commerce Event','name':name,'event_key':key,'payload_hash':digest,'order_ref':order_ref,'kind':kind})
    record.flags.name_set=True;record.insert(ignore_permissions=True)
    try:
        result=handlers[kind](payload)
    except (ValueError,KeyError,TypeError) as exc:
        frappe.throw('Invalid commerce event: '+str(exc),frappe.ValidationError)
    record.outcome=json.dumps(result,separators=(',',':'));record.save(ignore_permissions=True)
    return result

def reserve(payload):
    if payload.get('currency')!='IRR':frappe.throw('Only IRR orders are supported')
    company=config('company');warehouse=config('warehouse')
    if frappe.db.get_value('Company',company,'default_currency')!='IRR':frappe.throw('Company currency must be IRR')
    items=payload.get('items')
    if not isinstance(items,list) or not 1<=len(items)<=100:frappe.throw('Invalid order lines')
    if len({x.get('sku') for x in items})!=len(items):frappe.throw('Duplicate SKU lines must be consolidated')
    subtotal=0
    for item in items:
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',item.get('sku','')):frappe.throw('Invalid SKU')
        subtotal+=line_total(item['qty'],item['unit_price_irr'])
    shipping=money(payload.get('shipping_irr','0'));discount=money(payload.get('discount_irr','0'));total=money(payload['amount_irr'])
    if total<=0 or discount>subtotal or total!=subtotal-discount+shipping:frappe.throw('Order amount mismatch')
    if payload.get('tax_irr','0') not in ('0',0):frappe.throw('Tax integration requires reviewed company-specific configuration')
    order_hash=payload_hash({k:v for k,v in payload.items() if k not in ('event_key','kind')})
    existing=frappe.db.get_value('TehNet Reservation',{'order_ref':payload['order_ref']},'name')
    if existing:
        row=reservation(payload['order_ref'])
        if row.order_hash!=order_hash:frappe.throw('Order reference reused with changed commercial terms')
        return outcome(row)
    if not frappe.db.get_single_value('Stock Settings','enable_stock_reservation'):frappe.throw('Native stock reservation must be enabled')
    if frappe.db.get_single_value('Stock Settings','allow_partial_reservation'):frappe.throw('Partial reservations must be disabled')
    lock_stock(items)
    customer=payload.get('customer',{})
    customer_ref=customer.get('reference','')
    if not re.fullmatch(r'[A-Za-z0-9:._-]{1,100}',customer_ref):frappe.throw('Invalid customer reference')
    customer_id='TN-'+hashlib.sha256(customer_ref.encode()).hexdigest()[:24]
    if not frappe.db.exists('Customer',customer_id):
        doc=frappe.get_doc({'doctype':'Customer','name':customer_id,'customer_name':str(customer.get('name','مشتری وب'))[:140],'customer_type':'Individual','customer_group':config('customer_group'),'territory':config('territory')})
        doc.flags.name_set=True;doc.insert()
        customer_id=doc.name
    order=frappe.new_doc('Sales Order');order.company=company;order.customer=customer_id
    order.transaction_date=today();order.delivery_date=today();order.currency='IRR';order.conversion_rate=1
    order.selling_price_list=config('price_list');order.set_warehouse=warehouse;order.reserve_stock=1
    order.apply_discount_on='Net Total';order.discount_amount=discount
    for item in items:
        uom=item.get('uom');rate=money(item['unit_price_irr'])
        if not isinstance(uom,str) or not uom:frappe.throw('Explicit verified selling UOM required')
        prices=frappe.get_all('Item Price',filters={'item_code':item['sku'],'price_list':order.selling_price_list,'uom':uom,'currency':'IRR'},fields=['price_list_rate','valid_from','valid_upto'])
        valid=[p for p in prices if (not p.valid_from or str(p.valid_from)<=today()) and (not p.valid_upto or str(p.valid_upto)>=today())]
        if len(valid)!=1 or Decimal(str(valid[0].price_list_rate))!=rate:frappe.throw('Authoritative ERP price not verified for '+item['sku'])
        order.append('items',{'item_code':item['sku'],'qty':str(quantity(item['qty'])),'uom':uom,'rate':str(rate),'warehouse':warehouse,'reserve_stock':1})
    if shipping:
        order.append('taxes',{'charge_type':'Actual','account_head':config('shipping_income_account'),'description':'Shipping','tax_amount':str(shipping)})
    order.insert()
    if Decimal(str(order.grand_total))!=total:frappe.throw('ERP calculated amount differs from WooCommerce')
    order.submit()
    for item in order.items:
        reserved=frappe.db.sql('SELECT COALESCE(SUM(reserved_qty),0) FROM `tabStock Reservation Entry` WHERE voucher_no=%s AND voucher_detail_no=%s AND docstatus=1',(order.name,item.name))[0][0]
        if Decimal(str(reserved))!=Decimal(str(item.stock_qty)):frappe.throw('Full stock reservation was not created')
    row=frappe.get_doc({'doctype':'TehNet Reservation','order_ref':payload['order_ref'],'sales_order':order.name,'state':'reserved','expires_at':add_to_date(now_datetime(),minutes=15),'order_hash':order_hash,'amount_irr':str(total),'refund_total_irr':0}).insert(ignore_permissions=True)
    return outcome(row)

def cancel(payload):
    row=reservation(payload['order_ref'])
    if row.state in ('canceled','expired'):return outcome(row)
    if row.state!='reserved':frappe.throw('Paid or fulfilled orders require a return/refund workflow')
    order=frappe.get_doc('Sales Order',row.sales_order);order.check_permission('cancel');order.cancel()
    row.state='canceled';row.save(ignore_permissions=True);return outcome(row)

def paid(payload):
    from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
    from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
    row=reservation(payload['order_ref']);amount=validate_money_event({**payload,'expected_amount_irr':str(int(Decimal(str(row.amount_irr))))})
    identity=payload.get('payment_identity','')
    if not re.fullmatch(r'[A-Za-z0-9:._-]{1,120}',identity):frappe.throw('Verified payment identity required')
    if row.state=='paid' and row.payment_identity==identity:return outcome(row)
    if row.state!='reserved' or get_datetime(row.expires_at)<=now_datetime():frappe.throw('Reservation is no longer payable; reconcile late payment manually')
    if frappe.db.exists('Payment Entry',{'tn_payment_identity':identity}):frappe.throw('Payment identity already used')
    invoice=make_sales_invoice(row.sales_order);invoice.update_stock=0;invoice.insert()
    if Decimal(str(invoice.grand_total))!=amount:frappe.throw('Invoice amount mismatch')
    invoice.submit()
    receipt=get_payment_entry('Sales Invoice',invoice.name,bank_account=config('clearing_account'))
    receipt.reference_no=identity;receipt.reference_date=today();receipt.tn_payment_identity=identity;receipt.insert();receipt.submit()
    row.invoice=invoice.name;row.payment_entry=receipt.name;row.payment_identity=identity;row.state='paid';row.save(ignore_permissions=True)
    return outcome(row)

def dispatch(payload):
    from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
    row=reservation(payload['order_ref'])
    if row.state=='dispatched':return outcome(row)
    if row.state!='paid':frappe.throw('Only paid orders may be dispatched')
    tracking=str(payload.get('tracking_reference','')).strip()
    if not tracking or len(tracking)>140:frappe.throw('Carrier tracking reference required')
    delivery=make_delivery_note(row.sales_order);delivery.insert();delivery.submit()
    row.delivery_note=delivery.name;row.tracking_reference=tracking;row.state='dispatched';row.save(ignore_permissions=True)
    return outcome(row)

def refund(payload):
    from erpnext.controllers.sales_and_purchase_return import make_return_doc
    from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
    row=reservation(payload['order_ref'])
    if row.state not in ('dispatched','partially_refunded'):frappe.throw('Only delivered quantities can be returned')
    lines=payload.get('items',[])
    requested={x['sku']:quantity(x['qty']) for x in lines}
    if not requested or len(requested)!=len(lines):frappe.throw('Invalid return lines')
    invoice=frappe.get_doc('Sales Invoice',row.invoice)
    if any(x.charge_type!='Actual' or x.account_head!=config('shipping_income_account') for x in invoice.taxes):frappe.throw('Tax return requires reviewed company-specific configuration')
    shipping=money(payload.get('shipping_refund_irr','0'))
    prior_shipping=Decimal(str(row.shipping_refund_irr or 0))
    if shipping+prior_shipping>Decimal(str(invoice.total_taxes_and_charges)):frappe.throw('Shipping refund exceeds the original shipping charge')
    original={x.item_code:x for x in invoice.items}
    delivery=make_return_doc('Delivery Note',row.delivery_note)
    credit=make_return_doc('Sales Invoice',row.invoice);credit.update_stock=0
    # Original net rates already include the native invoice discount allocation.
    # Never copy the full header discount or shipping charge into each partial return.
    credit.discount_amount=0;credit.additional_discount_percentage=0;credit.set('taxes',[])
    if shipping:credit.append('taxes',{'charge_type':'Actual','account_head':config('shipping_income_account'),'description':'Returned shipping','tax_amount':str(-shipping)})
    for doc in (delivery,credit):
        retained=[]
        for item in doc.items:
            if item.item_code not in requested:continue
            if requested[item.item_code]>abs(Decimal(str(item.qty))):frappe.throw('Return exceeds remaining delivered quantity')
            if doc.doctype=='Sales Invoice':
                item.rate=original[item.item_code].net_rate;item.discount_percentage=0;item.discount_amount=0
                whole_irr(requested[item.item_code]*Decimal(str(item.rate)))
            item.qty=str(-requested[item.item_code]);retained.append(item)
        if len(retained)!=len(requested):frappe.throw('Return SKU not in original order')
        doc.set('items',retained);doc.calculate_taxes_and_totals();doc.insert()
        if doc.doctype=='Sales Invoice' and abs(Decimal(str(doc.grand_total)))!=money(payload['amount_irr']):frappe.throw('Return amount mismatch')
        doc.submit()
    amount=money(payload['amount_irr']);identity=payload.get('payment_identity','')
    if not re.fullmatch(r'[A-Za-z0-9:._-]{1,120}',identity):frappe.throw('Verified refund identity required')
    payment=get_payment_entry('Sales Invoice',credit.name,bank_account=config('clearing_account'))
    payment.reference_no=identity;payment.reference_date=today();payment.tn_payment_identity=identity;payment.insert();payment.submit()
    row.refund_total_irr=Decimal(str(row.refund_total_irr or 0))+amount
    if row.refund_total_irr>Decimal(str(row.amount_irr)):frappe.throw('Refund exceeds original payment')
    row.shipping_refund_irr=prior_shipping+shipping
    row.state='refunded' if Decimal(str(row.refund_total_irr))==Decimal(str(row.amount_irr)) else 'partially_refunded'
    row.save(ignore_permissions=True);return {**outcome(row),'credit_note':credit.name,'return_delivery':delivery.name,'refund_payment':payment.name}

def settle(payload):
    gross=money(payload['amount_irr']);fee=money(payload['fee_irr']);net=money(payload['net_irr'])
    if gross!=fee+net:frappe.throw('Settlement does not balance')
    # An operator/provider must supply the actual bank settlement evidence; this never calls a bank.
    identity=payload.get('settlement_reference','')
    if not isinstance(identity,str) or not re.fullmatch(r'[A-Za-z0-9:._-]{1,120}',identity):frappe.throw('Actual settlement reference required')
    if frappe.db.exists('Journal Entry',{'tn_settlement_reference':identity}):frappe.throw('Settlement reference already used')
    payments=payload.get('payment_identities',[])
    if not payments or len(set(payments))!=len(payments):frappe.throw('Unique payment identities required')
    # Lock all selected receipts in stable order: a second settlement cannot reuse them.
    for payment in sorted(payments):
        frappe.db.sql('SELECT name FROM `tabPayment Entry` WHERE tn_payment_identity=%s FOR UPDATE',(payment,))
    receipts=frappe.get_all('Payment Entry',filters={'tn_payment_identity':['in',payments],'docstatus':1},fields=['name','paid_amount','payment_type','company','paid_from','paid_to','tn_settlement_journal'])
    expected=Decimal(0)
    for receipt in receipts:
        if receipt.tn_settlement_journal:frappe.throw('Receipt is already settled')
        if receipt.company!=config('company'):frappe.throw('Settlement company mismatch')
        if receipt.payment_type=='Receive' and receipt.paid_to==config('clearing_account'):
            expected+=Decimal(str(receipt.paid_amount))
        elif receipt.payment_type=='Pay' and receipt.paid_from==config('clearing_account'):
            expected-=Decimal(str(receipt.paid_amount))
        else:frappe.throw('Settlement must use the configured gateway clearing account')
    if len(receipts)!=len(payments) or expected!=gross or gross<=0:frappe.throw('Settlement does not match verified receipts and refunds')
    journal=frappe.new_doc('Journal Entry');journal.company=config('company');journal.posting_date=today();journal.user_remark='TehNet verified settlement '+identity
    journal.tn_settlement_reference=identity
    journal.append('accounts',{'account':config('bank_account'),'debit_in_account_currency':str(net)})
    if fee:journal.append('accounts',{'account':config('fee_account'),'debit_in_account_currency':str(fee)})
    journal.append('accounts',{'account':config('clearing_account'),'credit_in_account_currency':str(gross)})
    journal.insert();journal.submit()
    for receipt in receipts:frappe.db.set_value('Payment Entry',receipt.name,'tn_settlement_journal',journal.name)
    return {'journal_entry':journal.name,'gross_irr':str(gross),'fee_irr':str(fee),'net_irr':str(net)}

def expire_reservations():
    for name in frappe.get_all('TehNet Reservation',filters={'state':'reserved','expires_at':['<=',now_datetime()]},pluck='name',limit_page_length=100):
        frappe.db.savepoint('tehnet_expire')
        try:
            row=frappe.get_doc('TehNet Reservation',name);row=reservation(row.order_ref)
            if row.state!='reserved' or get_datetime(row.expires_at)>now_datetime():continue
            order=frappe.get_doc('Sales Order',row.sales_order);order.cancel();row.state='expired';row.save(ignore_permissions=True)
        except Exception:
            frappe.db.rollback(save_point='tehnet_expire');frappe.log_error(title='TehNet reservation expiry failed',message='Reservation '+name+' needs reconciliation')
