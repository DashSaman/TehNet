"""Bounded public-page evidence collection. A missing HTML signal is unknown, never absence."""
from pathlib import Path
import concurrent.futures,datetime,hashlib,json,re,urllib.request,urllib.error
from html.parser import HTMLParser
root=Path(__file__).resolve().parents[1];out=root/'docs/research/store-benchmark-2026-10-15';out.mkdir(exist_ok=True)
foreign='''Amazon|amazon.com
eBay|ebay.com
Walmart|walmart.com
AliExpress|aliexpress.com
Temu|temu.com
Etsy|etsy.com
Rakuten|rakuten.co.jp
Target|target.com
Best Buy|bestbuy.com
Newegg|newegg.com
Costco|costco.com
Sam's Club|samsclub.com
Home Depot|homedepot.com
Lowe's|lowes.com
Wayfair|wayfair.com
IKEA|ikea.com
Chewy|chewy.com
Nike|nike.com
Adidas|adidas.com
Apple|apple.com
Samsung|samsung.com
Dell|dell.com
HP|hp.com
Lenovo|lenovo.com
ASUS|asus.com
Logitech|logitech.com
Ubiquiti Store|store.ui.com
FS|fs.com
Monoprice|monoprice.com
Cable Matters|cablematters.com
StarTech|startech.com
CDW|cdw.com
Insight|insight.com
Connection|connection.com
Provantage|provantage.com
B&H Photo|bhphotovideo.com
Adorama|adorama.com
Crutchfield|crutchfield.com
Micro Center|microcenter.com
Scan|scan.co.uk
Overclockers UK|overclockers.co.uk
Ebuyer|ebuyer.com
Currys|currys.co.uk
Argos|argos.co.uk
John Lewis|johnlewis.com
Very|very.co.uk
AO|ao.com
Richer Sounds|richersounds.com
Alternate|alternate.de
Notebooksbilliger|notebooksbilliger.de
Cyberport|cyberport.de
Reichelt|reichelt.com
Conrad|conrad.com
Mouser|mouser.com
DigiKey|digikey.com
RS|rs-online.com
Farnell|farnell.com
Newark|newark.com
Arrow|arrow.com
LCSC|lcsc.com
Seeed Studio|seeedstudio.com
Adafruit|adafruit.com
SparkFun|sparkfun.com
DFRobot|dfrobot.com
Pololu|pololu.com
Pimoroni|pimoroni.com
RobotShop|robotshop.com
AutomationDirect|automationdirect.com
Grainger|grainger.com
McMaster-Carr|mcmaster.com
Uline|uline.com
Zoro|zoro.com
Fastenal|fastenal.com
MSC Industrial|mscdirect.com
Global Industrial|globalindustrial.com
Thomann|thomann.de
Sweetwater|sweetwater.com
Guitar Center|guitarcenter.com
REI|rei.com
Decathlon|decathlon.com
Backcountry|backcountry.com
Patagonia|patagonia.com
The North Face|thenorthface.com
Uniqlo|uniqlo.com
H&M|hm.com
Zara|zara.com
ASOS|asos.com
Zalando|zalando.com
Otto|otto.de
Bol|bol.com
Coolblue|coolblue.nl
MediaMarkt|mediamarkt.de
Fnac|fnac.com
Darty|darty.com
Cdiscount|cdiscount.com
LDLC|ldlc.com
Galaxus|galaxus.ch
Digitec|digitec.ch
Alza|alza.cz
eMAG|emag.ro'''
iran='''دیجی‌کالا|digikala.com
تکنولایف|technolife.com
لیون کامپیوتر|lioncomputer.com
مقداد آی‌تی|meghdadit.com
اگزو|exo.ir
فافا|fafait.net
کالاتیک|kalatik.com
گوشی‌شاپ|gooshishop.com
موبایل ۱۴۰|mobile140.com
موبیت|mobit.ir
بانی‌مد|banimode.com
مدیسه|modiseh.com
خانومی|khanoumi.com
روژاشاپ|rojashop.com
اکالا|okala.com
اسنپ مارکت|snapp.market
باسلام|basalam.com
تکنوسان|technosun.ir
نتران|netran.net
شبکه‌چی|shabakechi.com'''
rows=[{'name':n,'domain':d,'region':region,'url':'https://'+d+'/'} for region,group in [('foreign',foreign),('iran',iran)] for n,d in [line.split('|') for line in group.splitlines()]]
assert sum(r['region']=='foreign' for r in rows)==100 and sum(r['region']=='iran' for r in rows)==20
assert len({r['domain'] for r in rows})==120
class Page(HTMLParser):
    def __init__(self):super().__init__();self.title='';self.in_title=False;self.links=[];self.search=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='title':self.in_title=True
        if tag=='a' and a.get('href'):self.links.append(a['href'])
        if tag=='input' and (a.get('type')=='search' or 'search' in a.get('name','').lower()):self.search=True
    def handle_endtag(self,tag):
        if tag=='title':self.in_title=False
    def handle_data(self,data):
        if self.in_title:self.title+=data
def inspect(row):
    row=dict(row);row['observed_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();row['scope']='One unauthenticated public HTML page; no checkout, mobile or visual score inferred'
    try:
        request=urllib.request.Request(row['url'],headers={'User-Agent':'TehNet-public-UX-research/1.0','Accept':'text/html'})
        with urllib.request.urlopen(request,timeout=15) as response:
            raw=response.read(2_000_000);row.update({'http_status':response.status,'final_url':response.url,'bytes_read':len(raw),'body_sha256':hashlib.sha256(raw).hexdigest()})
            page=Page();page.feed(raw.decode('utf-8',errors='replace'));row['page_title']=re.sub(r'\s+',' ',page.title).strip()[:160]
            challenge=bool(re.search(r'access denied|just a moment|security verification|verify you are human|robot or human',page.title,re.I))
            row['inspection_status']='challenge-page' if challenge else 'public-html-read'
            row['search_input_in_initial_html']=page.search if not challenge else None
            row['candidate_policy_links']={kind:next((urllib.parse.urljoin(response.url,u) for u in page.links if re.search(pattern,u,re.I)),None) for kind,pattern in {'shipping':'shipping|delivery|ارسال','returns':'return|refund|مرجوع','support':'support|help|contact|تماس','comparison':'compare|comparison','3d':'360|3d|augmented','account':'account|login|signin','cart':'cart|basket|سبد'}.items()} if not challenge else {}
    except urllib.error.HTTPError as e:row.update({'http_status':e.code,'inspection_status':'access-limited','error':'Public endpoint denied this research client; no bypass or feature inference'})
    except Exception as e:row.update({'inspection_status':'unavailable','error':type(e).__name__})
    print(row['domain']+' '+row['inspection_status'],flush=True);return row
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(inspect,rows))
data={'method':'100 international and 20 Iranian benchmark candidates selected across retail and relevant technical verticals. This is not a certified top-120 traffic ranking. HTML evidence only; null means unknown. No challenge bypass, authentication or purchase.','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'stores':results}
(out/'public-page-evidence.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
header='# مقایسه ۱۲۰ فروشگاه — شواهد صفحات عمومی\n\n۱۰۰ نمونه خارجی و ۲۰ ایرانی انتخاب شده‌اند؛ این فهرست رتبه‌بندی آماری «۱۰۰/۲۰ سایت برتر» نیست. انتخاب شامل فروشگاه‌های شناخته‌شده عمومی و تخصصی مرتبط است.\n\nاین مرحله HTML عمومی را بررسی می‌کند. وجود لینک یا input، تأیید کیفیت تجربه کاربری یا عملکرد checkout نیست. blocked/unknown به معنی نبود قابلیت نیست. چالش ضدربات دور زده نشده است. بررسی عمیق هر جریان در backlog جدا ثبت می‌شود.\n\n|نمونه|منطقه|وضعیت دسترسی|عنوان مشاهده‌شده|\n|---|---|---|---|\n'
for r in results:header+='|['+r['name']+']('+r['url']+')|'+r['region']+'|'+r['inspection_status']+' / '+str(r.get('http_status','—'))+'|'+r.get('page_title','نامعلوم').replace('|','/')+'|\n'
(out/'README.md').write_text(header,encoding='utf-8');print('BENCHMARK_120_EVIDENCE_SAVED',flush=True)
