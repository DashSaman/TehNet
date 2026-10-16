"""Read-only public HTTP acceptance from the managed host; no origin/WAF bypass."""
from pathlib import Path
import json,shlex,subprocess
root=Path(__file__).resolve().parents[1]
remote=r'''
import concurrent.futures,datetime,json,urllib.request
base='https://tehnet.ir'
def get(url):
 request=urllib.request.Request(url,headers={'User-Agent':'TehNet-read-only-release-QA/0.4'})
 with urllib.request.urlopen(request,timeout=30)as r:return {'status':r.status,'final_url':r.url},r.read().decode('utf-8')
api,body=get(base+'/wp-json/wc/store/v1/products?per_page=100');products=json.loads(body)
assert len(products)==25 and all(not p['is_purchasable']for p in products)
def product(p):
 assert p['permalink'].startswith(base+'/product/')
 result,body=get(p['permalink']);assert result['status']==200 and 'tn-shop-experience-css'in body and 'noindex'in body and 'data-tn-reviewed-model'not in body and 'data-tn-spin='not in body
 return {'sku':p['sku'],**result,'shared_style':True,'noindex':True,'unapproved3D_absent':True}
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:pages=list(pool.map(product,products))
shop,body=get(base+'/shop/');assert shop['status']==200 and 'tn-shop-category'in body and 'tn-filter-advanced'in body and 'tn-card-identity'in body
home,body=get(base+'/');assert home['status']==200 and 'tn-shop-experience-css'not in body and 'زیرساخت شبکه'in body
search,body=get(base+'/shop/?post_type=product&s=TN-SN-%DB%B1%DB%B8%DB%B0%DB%B0%DB%B2');assert search['status']==200 and 'TN-SN-18002'in body
print(json.dumps({'status':'passed','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'route':'Public HTTPS through Cloudflare from managed host; certificate verification enabled','scope':'HTTP/HTML/API, not a replacement for complete real-browser production acceptance; no writes/forms/orders','products':pages,'shop':shop,'home':home,'persian_sku_redirect':search,'published_products':25,'purchasable_products':0}))
'''
compile(remote,'public-readonly-acceptance','exec')
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','netauto-main','python3 -c '+shlex.quote(remote)],capture_output=True,timeout=180)
if r.returncode:raise RuntimeError((r.stdout+r.stderr).decode(errors='replace'))
result=json.loads(r.stdout);p=root/'qa/shop-ux-2026-10-16/production/public-http.json';p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print('PUBLIC_HTTP=PASS;25products+shop+home+PersianSKU;no writes;browser scope separate')
