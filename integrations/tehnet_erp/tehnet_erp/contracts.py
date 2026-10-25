"""Exact, side-effect-free boundary validation. ERPNext owns all ledger posting."""
from decimal import Decimal
import hashlib
import json
import re

def money(value):
    if type(value) not in (str,int) or not re.fullmatch(r'(0|[1-9][0-9]{0,11})',str(value)):
        raise ValueError('IRR amount must be a bounded nonnegative integer')
    return int(value)

def quantity(value):
    if not isinstance(value,str) or not re.fullmatch(r'(0|[1-9][0-9]{0,5})(\.[0-9]{1,3})?',value):
        raise ValueError('Quantity must be a plain decimal string with up to 3 decimal places')
    number=Decimal(value)
    if number<=0:raise ValueError('Quantity must be positive')
    return number

def line_total(qty,unit_price):
    value=quantity(qty)*money(unit_price)
    if value!=value.to_integral_value() or value>Decimal('999999999999'):
        raise ValueError('Line total must be whole IRR within the amount limit')
    return int(value)

def validate_money_event(payload):
    if payload.get('currency')!='IRR':raise ValueError('Only explicit IRR is accepted')
    actual=money(payload['amount_irr']);expected=money(payload['expected_amount_irr'])
    if actual!=expected:raise ValueError('Payment amount does not match order')
    return actual

def payload_hash(payload):
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
