"""Normalize public facts into a conservative, reviewable WooCommerce manifest.

No third-party prose, media, reviews, sale prices or stock are imported.
The public source must be fetched separately; this module has no network side effects.
"""
import argparse
import copy
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

SOURCE='https://saieedshabake.ir'

def text(value):
    return re.sub(r'\s+',' ',html.unescape(re.sub(r'<[^>]*>','',str(value)))).strip()

def build_manifest(products, categories):
    category_ids={int(c['id']) for c in categories}
    if len(category_ids)!=len(categories):
        raise ValueError('duplicate category ID')
    for c in categories:
        if int(c.get('parent',0)) not in category_ids|{0}:
            raise ValueError('missing category parent')
        seen=set();parent=int(c['id'])
        while parent:
            if parent in seen: raise ValueError('category parent cycle')
            seen.add(parent)
            parent=int(next(x for x in categories if int(x['id'])==parent).get('parent',0))
    ids=set(); rows=[]
    for source in products:
        source_id=int(source['id'])
        if source_id<1 or source_id in ids: raise ValueError('duplicate or invalid product ID')
        ids.add(source_id)
        parsed=urlsplit(source['permalink'])
        if parsed.scheme!='https' or parsed.netloc!='saieedshabake.ir':
            raise ValueError('unexpected source URL')
        if source.get('type')!='simple':
            raise ValueError('unsupported product type: '+str(source.get('type')))
        assigned=[int(c['id']) for c in source.get('categories',[])]
        if not set(assigned)<=category_ids: raise ValueError('unknown category')
        title=text(source['name']);flags=['manufacturer-part-number-unverified','image-license-unverified','tehnet-price-and-stock-required']
        clean=re.sub(r'^خرید\s+','',title)
        clean=re.sub(r'\s*[|–—-]\s*(?:قیمت|مناسب|پشتیبانی).*','',clean)
        if re.search(r'تست|فلوک|پرمننت|چنل|Channel|Permanent',title,re.I):
            flags.append('test-certificate-required')
            clean=re.sub(r'\s*(?:تست\s*)?(?:فلوک\s*)?(?:پرمننت|چنل|Channel|Permanent)\b','',clean,flags=re.I)
            clean=re.sub(r'\s*تست\s*فلوک?','',clean)
        if 'تلفن' in title and re.search(r'Cat\s*6',title,re.I):
            flags.append('telephone-category-conflict')
        source_sku=text(source.get('sku',''))
        if source_id==17989:
            flags.append('title-part-number-and-source-sku-conflict')
        if source_sku and (('نگزنس' in title and re.search(r'Legrand|لگراند',source_sku,re.I)) or ('لگراند' in title and 'نگزنس' in source_sku)):
            flags.append('source-sku-brand-conflict')
        rows.append({
            'source_id':source_id,'source_url':source['permalink'],'source_title':title,
            'source_key':f'saieedshabake.ir:product:{source_id}',
            'sku':f'TN-SN-{source_id}','name':text(clean),'status':'draft',
            'description':'این قلم در کاتالوگ بررسی تهران نتورک ثبت شده است. مدل دقیق، مشخصات فنی، واحد فروش، محتویات بسته و شرایط تأمین باید پیش از فروش تأیید شوند. قیمت و موجودی این کالا نیازمند استعلام است.',
            'short_description':'نیازمند تأیید مشخصات و استعلام قیمت و موجودی تهران نتورک.',
            'regular_price':'','stock_quantity':0,'manage_stock':True,'backorders':'no',
            'images':[],'media_license':'unverified-not-imported',
            'category_source_ids':assigned,'verified_specifications':[],
            'source_attributes':copy.deepcopy(source.get('attributes',[])),
            'review_flags':flags,'sale_unit':None,'minimum_quantity':None,
            'source_observation':{'price':copy.deepcopy(source.get('prices',{})),'in_stock':bool(source.get('is_in_stock',False)), 'supplier_sku':source_sku,'image_urls':[i['src'] for i in source.get('images',[])]},
        })
    return {'schema_version':1,'source':SOURCE,'products':rows,'categories':[{'id':int(c['id']),'name':text(c['name']),'slug':c['slug'],'parent':int(c.get('parent',0))} for c in categories]}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('products',type=Path);parser.add_argument('categories',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args()
    result=build_manifest(json.loads(args.products.read_text(encoding='utf-8-sig')),json.loads(args.categories.read_text(encoding='utf-8-sig')))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    args.output.write_bytes(data)
    print(json.dumps({'count':len(result['products']),'categories':len(result['categories']),'sha256':hashlib.sha256(data).hexdigest()}))

if __name__=='__main__':main()
