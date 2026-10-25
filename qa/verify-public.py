"""Read-only public-site verification using curl, without changing WAF settings."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,concurrent.futures,subprocess
R=Path(__file__).parent
class Page(HTMLParser):
 def __init__(self):super().__init__();self.h1=0;self.canon=[];self.robots=''
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='h1':self.h1+=1
  if tag=='link' and a.get('rel')=='canonical':self.canon.append(a.get('href'))
  if tag=='meta' and a.get('name')=='robots':self.robots=a.get('content','')
def retrieve(url):
 if not url.startswith('https://tehnet.ir/'):raise ValueError('Out-of-scope URL')
 value=subprocess.check_output(['curl','--silent','--show-error','--location','--compressed','--max-time','30','--write-out','\n%{http_code}',url],text=True)
 text,code=value.rsplit('\n',1);return text,int(code)
def excluded(text):
 text=text.translate(str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩','01234567890123456789'))
 return bool(re.search(r'pv[\s_-]*network|پیوی|(?<!\d)(?:\+?98|0098|0)9[0-9]{9}(?!\d)',text,re.I))
def verify(url):
 try:
  text,code=retrieve(url);p=Page();p.feed(text)
  out={'url':url,'http':code,'h1':p.h1,'canonical':p.canon,'robots':p.robots,'excluded_data_found':excluded(text)}
  out['ok']=code==200 and p.h1==1 and p.canon==[url] and 'noindex' in p.robots and not out['excluded_data_found']
  return out
 except Exception as error:return {'url':url,'ok':False,'error':str(error)}
urls=json.loads((R/'public-routes.json').read_text())
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(verify,urls))
for name in ['Amirreza-Golavar-Resume.txt','Amirreza-Golavar.vcf']:
 url='https://tehnet.ir/wp-content/themes/tehnet/assets/profile/'+name
 try:
  text,code=retrieve(url);ok=code==200 and not excluded(text) and not re.search(r'(?im)^TEL[;:]',text)
  results.append({'url':url,'ok':ok,'http':code,'type':'download-privacy'})
 except Exception as error:results.append({'url':url,'ok':False,'error':str(error)})
(R/'public-verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
failed=[r for r in results if not r['ok']]
print('PUBLIC_CHECKS',len(results),'FAILURES',len(failed))
for r in failed:print(json.dumps(r,ensure_ascii=False))
raise SystemExit(bool(failed))
