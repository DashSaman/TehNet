from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError

origin='--origin' in sys.argv
expected_downloads='--expect-downloads' in sys.argv
allow_configured_access='--allow-configured-access' in sys.argv
class Document(HTMLParser):
    def __init__(self):super().__init__();self.h1=0;self.canonical=[];self.robots=[];self.software_links=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='h1':self.h1+=1
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
        if tag=='meta' and a.get('name')=='robots':self.robots.append(a.get('content'))
        if tag=='a' and a.get('href') in ['/software/','https://tehnet.ir/software/']:self.software_links+=1

def get(path,method='GET',binary=False):
    url='https://tehnet.ir'+path
    if origin:
        with tempfile.TemporaryDirectory() as temp:
            header=Path(temp)/'headers';body=Path(temp)/'body'
            command=['curl','--silent','--show-error','--max-time','20','--noproxy','*','--resolve','tehnet.ir:443:127.0.0.1',
                     '-D',str(header),'-o',str(body),'-w','%{http_code}']
            command+=['--head'] if method=='HEAD' else ['-X',method]
            if '/private/' in path:command+=['-H','Range: bytes=0-4','-H','If-None-Match: *']
            proc=subprocess.run(command+[url],capture_output=True,text=True,check=True)
            headers={}
            for line in header.read_text().splitlines():
                if ':' in line:
                    k,v=line.split(':',1);headers[k.lower()]=v.strip()
            data=body.read_bytes()
            return int(proc.stdout),headers,data if binary else data.decode('utf-8')
    request=Request(url,method=method,headers={'User-Agent':'TehNet-Software-Acceptance/0.1'})
    if '/private/' in path:
        request.add_header('Range','bytes=0-4');request.add_header('If-None-Match','*')
    try:response=urlopen(request,timeout=20)
    except HTTPError as exc:response=exc
    with response:
        data=response.read(1500000)
        return response.status,{k.lower():v for k,v in response.headers.items()},data if binary else data.decode('utf-8')

report={'tested_at_utc':datetime.now(timezone.utc).isoformat(),'vantage':'origin-loopback-valid-TLS' if origin else 'independent-Windows-public-TLS','checks':[]}
for path in ['/','/learn/','/services/','/shop/','/contact/','/software/']:
    code,headers,body=get(path);doc=Document();doc.feed(body)
    assert code==200,(path,code)
    assert doc.h1==1,(path,doc.h1)
    if path!='/software/':assert doc.canonical==['https://tehnet.ir'+path],(path,doc.canonical)
    assert any('noindex' in (x or '') for x in doc.robots),(path,doc.robots)
    if path=='/':assert doc.software_links==1,doc.software_links
    if path=='/software/':assert 'ملیکا' not in body and 'آرشیو نرم‌افزار' in body
    report['checks'].append({'path':path,'status':code,'h1':doc.h1,'canonical':doc.canonical,'robots':doc.robots,'software_links':doc.software_links})
for path in ['/software/readyz','/software/v1/sources','/software/static/style.css','/software/openapi.json']:
    code,headers,body=get(path);assert code==200,(path,code)
    if path.endswith('readyz'):
        data=json.loads(body)
        restricted=data['capabilities']['restricted_access']
        assert isinstance(restricted,bool) and (allow_configured_access or restricted is False)
        assert data['capabilities']=={'public_research':True,'downloads':expected_downloads,'apt_profile_accepted':False,'restricted_access':restricted,'rubika':False}
    if path.endswith('sources'):
        data=json.loads(body);assert data['total']==27 and not any(x['routing_enabled'] for x in data['items'])
    report['checks'].append({'path':path,'status':code,'cache_control':headers.get('cache-control')})
for method in ['GET','HEAD','POST']:
    code,headers,body=get('/software/private/fixture',method)
    assert code==404 and 'no-store' in headers.get('cache-control',''),(method,code,headers)
    report['checks'].append({'path':'/software/private/fixture','method':method,'status':code,'cache_control':headers.get('cache-control')})
for asset in ['ui.js','fonts/Vazirmatn-Regular.woff2','fonts/Vazirmatn-ExtraBold.woff2']:
    code,headers,data=get('/software/static/'+asset,binary=True)
    assert code==200 and len(data)>100,(asset,code)
    report['checks'].append({'path':'/software/static/'+asset,'status':code,'bytes':len(data)})
print(json.dumps(report,ensure_ascii=False,indent=2))
