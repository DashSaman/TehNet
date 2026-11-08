"""Read-only, bounded HTTPS metadata observation. Never changes indexability."""
import concurrent.futures,hashlib,json,ssl,urllib.request,urllib.error
from html.parser import HTMLParser
from pathlib import Path
from datetime import datetime,timezone
POLICY=Path("seo/readiness-2026-11-08/index-policy.json")
class Head(HTMLParser):
 def __init__(self):
  super().__init__();self.robots=[];self.canonicals=[];self.h1=0;self.forms=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="meta" and a.get("name","").lower() in ("robots","googlebot"):self.robots.append({"agent":a["name"],"content":a.get("content","")})
  if tag=="link" and "canonical" in a.get("rel","").lower().split():self.canonicals.append(a.get("href",""))
  if tag=="h1":self.h1+=1
  if tag=="form":self.forms+=1
class SafeRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  from urllib.parse import urlsplit
  u=urlsplit(newurl)
  if u.scheme!="https" or u.hostname not in ("tehnet.ir","www.tehnet.ir"):raise ValueError("Out-of-scope redirect")
  return super().redirect_request(req,fp,code,msg,headers,newurl)
def observe(url):
 row={"url":url,"method":"GET","observed_utc":datetime.now(timezone.utc).isoformat(),"production_mutations":0}
 try:
  opener=urllib.request.build_opener(SafeRedirect(),urllib.request.HTTPSHandler(context=ssl.create_default_context()))
  req=urllib.request.Request(url,headers={"User-Agent":"TehNetReadOnlyReadiness/1.0","Accept":"text/html,text/plain,application/xml"})
  try:r=opener.open(req,timeout=15)
  except urllib.error.HTTPError as error:r=error
  with r:
   data=r.read(2*1024*1024+1)
   if len(data)>2*1024*1024:raise ValueError("Response exceeds observation boundary")
   row.update(status=r.status,final_url=r.geturl(),body_sha256=hashlib.sha256(data).hexdigest(),
    headers={k:r.headers.get(k) for k in ("Content-Type","X-Robots-Tag","CF-Cache-Status")})
   text=data.decode("utf-8",errors="replace");h=Head();h.feed(text)
   row.update(meta_robots=h.robots,canonical=h.canonicals,h1_count=h.h1,form_count=h.forms)
   if url.endswith("/robots.txt"):
    row["directives"]=[l.strip() for l in text.splitlines() if l.strip().lower().startswith(("user-agent:","disallow:","allow:","sitemap:","content-signal:"))]
   if "sitemap" in url:row["xml_detected"]="<sitemapindex" in text or "<urlset" in text
   row["interpretation"]="OBSERVED_ONLY_NOT_INDEX_VERDICT"
 except Exception as error:row.update(status=None,error_type=type(error).__name__,interpretation="ACCESS_UNVERIFIED_NOT_SITE_FAILURE")
 return row
if __name__=="__main__":
 policy=json.loads(POLICY.read_text())
 urls=[x["url"] for x in policy["candidates"]]+["https://tehnet.ir/robots.txt","https://tehnet.ir/wp-sitemap.xml"]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(observe,urls))
 print("TN_SEO_BASELINE "+json.dumps({"schema":1,"rows":rows,"no_form_submissions":True,"no_control_changes":True},ensure_ascii=False))
