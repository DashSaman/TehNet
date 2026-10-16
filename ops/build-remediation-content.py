from pathlib import Path
import json,hashlib,re,html,collections
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--before',type=Path,required=True);args=parser.parse_args()
root=Path(__file__).resolve().parents[1];base=json.loads(args.before.read_text(encoding='utf-8'));out=root/'content/remediation-2026-10-16';out.mkdir(parents=True,exist_ok=True)
assert all(base['blocks'].values()),'Only registered core blocks may be used'
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
def blocks(source):
 result=[]
 for line in source.strip().splitlines():
  line=line.strip()
  if not line:continue
  if line.startswith('[tn_'):result.append('<!-- wp:shortcode -->\n'+line+'\n<!-- /wp:shortcode -->');continue
  tag=re.match(r'<([a-z0-9]+)',line)[1]
  if tag=='p':name='paragraph';attrs='';markup=line
  elif tag=='h2':name='heading';attrs='';markup=line.replace('<h2>','<h2 class="wp-block-heading">',1)
  elif tag in ['ul','ol']:
   name='list';attrs=' {"ordered":true}'if tag=='ol'else'';items=re.findall(r'<li>(.*?)</li>',line);markup='<'+tag+' class="wp-block-list">'+''.join('<!-- wp:list-item --><li>'+x+'</li><!-- /wp:list-item -->'for x in items)+'</'+tag+'>'
  elif tag=='table':name='table';attrs=' {"hasFixedLayout":false}';markup='<figure class="wp-block-table">'+line+'</figure>'
  else:raise ValueError('Unsupported editable block '+tag)
  result.append('<!-- wp:'+name+attrs+' -->'+markup+'<!-- /wp:'+name+' -->')
 return '\n\n'.join(result)
pages={
6:'''<p>آموزش‌های موجود تهران نتورک برای یادگیری شبکه در محیط آزمایشگاهی و بررسی سناریوهای MikroTik دسته‌بندی شده‌اند. از مسیر پایه شروع کنید و پیش از هر تغییر عملیاتی، امکان بازیابی را بررسی کنید.</p>
<h2>مسیر میکروتیک و MTCNA</h2>
<p><a href="/learn/mikrotik/">هاب آموزش میکروتیک</a> و <a href="/learn/mikrotik/mtcna/">مسیر MTCNA</a>، ترتیب مطالعه و تمرین را نشان می‌دهند. درس‌های نوشتاری موجود:</p>
<ul><li><a href="/learn/mikrotik/mtcna/routeros-winbox/">اتصال به RouterOS، Winbox و بازیابی</a></li><li><a href="/learn/mikrotik/mtcna/ip-dhcp-dns/">آدرس‌دهی IP، DHCP و DNS</a></li><li><a href="/learn/mikrotik/mtcna/static-routing/">مسیریابی استاتیک</a></li><li><a href="/learn/mikrotik/mtcna/nat-masquerade/">NAT و Masquerade</a></li><li><a href="/learn/mikrotik/mtcna/firewall-basics/">فایروال پایه</a></li><li><a href="/learn/mikrotik/mtcna/queues-troubleshooting/">پهنای باند و عیب‌یابی</a></li></ul>
<h2>تمرین و منابع</h2>
<p>در <a href="/lab/">Lab</a> راه ساخت محیط GNS3 و ابزار محاسباتی MTU را ببینید. ویدیو و متن، مکمل تمرین‌اند؛ خواندن درس به معنی تأیید آمادگی برای تغییر شبکهٔ سازمانی نیست.</p>
<p><a href="/technical-methodology/">روش منابع و اصلاح محتوای تهران نتورک</a>، تفاوت مثال آموزشی و نتیجهٔ آزمایش واقعی را توضیح می‌دهد.</p>
[tn_editorial_note]''',
7:'''<p>Lab تهران نتورک برای تمرین جدا از شبکهٔ عملیاتی و بررسی مسئله‌های فنی است. هر ابزار یا سناریو باید فرض‌ها، ورودی و محدودیت‌های خود را روشن کند.</p>
<h2>محیط تمرین میکروتیک</h2>
<p><a href="/lab/gns3-mikrotik/">ساخت روتر میکروتیک مجازی با GNS3</a> نقطهٔ شروع تمرین است. مجوز و نسخهٔ تصویر RouterOS/CHR را از سازنده بررسی کنید؛ کلید یا تصویر دارای محدودیت را در اختیار دیگران نگذارید.</p>
<h2>ابزار محاسباتی WireGuard</h2>
<p><a href="/lab/wireguard-mtu/">برآورد MTU داخلی WireGuard</a>، سربار پایه را با انتخاب IPv4/IPv6 بیرونی محاسبه می‌کند. ابزار محلی است، داده‌ای به روتر نمی‌فرستد و نتیجهٔ تست مسیر یا سرعت نیست. کد Python برای استفادهٔ آفلاین نیز در همان صفحه قرار دارد.</p>
<h2>چطور نتیجهٔ تمرین را ثبت کنیم؟</h2>
<ul><li>نسخهٔ نرم‌افزار، توپولوژی و تنظیمات اثرگذار را ثبت کنید.</li><li>ورودی، خروجی، انتظار و نتیجهٔ واقعی را از هم جدا بنویسید.</li><li>پیش از اشتراک خروجی، رمز، کلید خصوصی، نشانی حساس و دادهٔ مشتری را حذف کنید.</li><li>قبل از اجرای تغییر در تولید، محدودهٔ کار و راه بازگشت را مشخص کنید.</li></ul>
<p><a href="/technical-methodology/">روش منابع، آزمون و اصلاح</a> · <a href="/learn/mikrotik/mtcna/">بازگشت به مسیر MTCNA</a></p>
[tn_editorial_note]''',
10:'''<p>تهران نتورک یک پلتفرم فارسی برای آموزش عملی شبکه، لاب، خدمات فنی و استعلام تجهیزات است. مسیر آموزش و خدمات در همین سایت کنار هم قرار دارند تا مفهوم، تمرین و نیاز اجرایی از هم قابل‌تشخیص باشند.</p>
<h2>حوزهٔ فعالیت</h2>
<ul><li>آموزش‌های موجود MikroTik و MTCNA و تمرین‌های مرتبط با RouterOS.</li><li>خدمات حضوری طراحی، راه‌اندازی و پشتیبانی شبکه در تهران، پس از بررسی نیاز.</li><li>پشتیبانی ریموت در سراسر ایران در صورت امکان دسترسی و مناسب‌بودن مسئله.</li><li>بررسی و استعلام تجهیزات؛ قیمت، مدل و شرایط تأمین پیش از سفارش تأیید می‌شوند.</li></ul>
<h2>مرز ادعا و مدرک</h2>
<p>مشخصات اعلام‌شدهٔ فروشنده، تصویر کاتالوگ و نتیجهٔ آزمون واقعی یکسان نیستند. نام سازنده یا لینک مستندات، به معنی نمایندگی رسمی نیست. <a href="/technical-methodology/">روش بررسی و اصلاح محتوا</a> را برای جزئیات ببینید.</p>
<h2>مسئول و راه ارتباط</h2>
<p><a href="/amirreza-golavar/">رزومه و فعالیت حرفه‌ای امیررضا گل‌آور</a> در صفحهٔ مستقل قابل مشاهده است. برای خدمات، تجهیزات و پیشنهاد اصلاح محتوا از <a href="/contact/">راه‌های تماس کسب‌وکار</a> استفاده کنید.</p>''',
11:'''<p>برای خدمات شبکه، پشتیبانی ریموت، استعلام تجهیزات یا پیشنهاد اصلاح محتوا با تهران نتورک در تماس باشید.</p>
<h2>تماس کسب‌وکار</h2>
<p>تلفن: <a href="tel:+982191018746">021-91018746</a><br>محدودهٔ نشانی: تهران، آیت‌الله کاشانی، شاهین جنوبی.</p>
<h2>برای بررسی درخواست چه اطلاعاتی لازم است؟</h2>
<ul><li>شرح نیاز یا نشانهٔ مشکل، زمان شروع و تغییرات اخیر.</li><li>شهر و امکان دسترسی ریموت، بدون ارسال رمز عبور یا کلید خصوصی.</li><li>برای کالا: کد کاتالوگ، شماره فنی موردنظر، مقدار و واحد فروش مدنظر.</li><li>برای اصلاح محتوا: نشانی صفحه، بخش موردنظر، نسخه یا مدرک عمومی مرتبط.</li></ul>
<p>قبل از دریافت دسترسی یا اجرای کار، محدوده و روش دسترسی بررسی می‌شود. اطلاعات محرمانه و دادهٔ مشتری را در پیام اولیه قرار ندهید. زمان اجرا، موجودی و هزینهٔ نهایی پس از بررسی اعلام می‌شوند.</p>
<p><a href="/services/">خدمات حضوری تهران و پشتیبانی ریموت ایران</a> · <a href="/technical-methodology/">روش منابع و اصلاح محتوا</a></p>'''}
excerpts={
5:'تهران نتورک؛ آموزش عملی شبکه و میکروتیک، لاب، خدمات حضوری تهران، پشتیبانی ریموت ایران و استعلام تجهیزات شبکه.',
6:'آموزش‌های موجود شبکه و میکروتیک تهران نتورک؛ مسیر MTCNA، شش درس نوشتاری و دسترسی به تمرین‌های Lab.',
7:'لاب تهران نتورک؛ محیط GNS3، برآورد MTU در WireGuard و روش ثبت نتیجهٔ تمرین، جدا از شبکهٔ عملیاتی.',
8:'خدمات شبکه تهران نتورک؛ بررسی نیاز، طراحی و پشتیبانی حضوری تهران یا ریموت در ایران، با تعیین محدودهٔ کار.',
9:'کاتالوگ تجهیزات شبکه تهران نتورک؛ بررسی تصاویر و اطلاعات اعلامی و استعلام مدل، قیمت، موجودی و شرایط تأمین.',
10:'درباره تهران نتورک؛ حوزهٔ آموزش، لاب، خدمات شبکه و استعلام تجهیزات، روش بررسی محتوا و راه ارتباط کسب‌وکار.',
11:'راه‌های تماس تهران نتورک برای خدمات شبکه، پشتیبانی ریموت، استعلام تجهیزات و گزارش اشکال محتوا؛ تلفن021-91018746.',
26:'مسیر آموزش میکروتیک در تهران نتورک؛ RouterOS، لاب GNS3 و دسترسی به مباحث دوره MTCNA.',
40:'آموزش MTCNA میکروتیک؛ ترتیب مطالعه و تمرین RouterOS، IP، مسیریابی، NAT، فایروال و عیب‌یابی.',
62:'شروع با RouterOS و Winbox؛ اتصال، محدودیت‌های Safe Mode، backup و export در مسیر آموزشی MTCNA تهران نتورک.',
63:'آدرس‌دهی IP، DHCP و DNS در RouterOS؛ درس پایهٔ MTCNA تهران نتورک برای تمرین و بررسی ارتباط کاربران.',
64:'مسیریابی استاتیک در RouterOS؛ درس MTCNA درباره مسیر، gateway و بررسی دسترسی در لاب.',
65:'NAT و Masquerade در میکروتیک؛ درس MTCNA برای شناخت ترجمهٔ آدرس و بررسی سناریوی آزمایشگاهی.',
66:'فایروال میکروتیک؛ درس پایهٔ MTCNA برای تعیین هدف قانون، ترتیب بررسی و تمرین جدا از تولید.',
67:'مدیریت پهنای باند و عیب‌یابی پایه در RouterOS؛ آخرین بخش مسیر نوشتاری MTCNA تهران نتورک.',
69:'فهرست نوشته‌های منتشرشدهٔ تهران نتورک درباره یادگیری میکروتیک، لاب و تجربهٔ فنی شبکه.',
70:'مسیر یادگیری میکروتیک و دسترسی به دوره MTCNA تهران نتورک؛ ترتیب مباحث و پیشنهاد تمرین در لاب.',
71:'چرا قبل از تغییر شبکهٔ واقعی، لاب بسازیم؟ یادداشت تهران نتورک درباره تمرین، کاهش ریسک و بررسی روش بازگشت.',
76:'ساخت روتر مجازی میکروتیک در GNS3 برای تمرین؛ محیط آزمایشگاهی، منابع و ارتباط با مسیر MTCNA.',
80:'رزومه امیررضا گل‌آور؛ شبکه، زیرساخت، پشتیبانی فناوری اطلاعات و فعالیت آموزشی در تهران نتورک.',
107:'سبد خرید تهران نتورک؛ اقلام کاتالوگ فعلی برای استعلام مدل، قیمت و موجودی ارائه می‌شوند.',
109:'تسویه حساب تهران نتورک؛ ثبت سفارش و پرداخت فقط پس از تأیید شرایط و فعال‌شدن مسیر مجاز انجام می‌شود.',
110:'حساب کاربری تهران نتورک؛ ورود و دسترسی به امکانات حساب و درخواست‌های مرتبط.'}
for p in base['posts']:
 if p['id'] in [29,31,33,35,37]:excerpts[p['id']]=p['title']+'؛ بررسی نیاز، تعیین محدودهٔ کار و انتخاب حضور در تهران یا دسترسی ریموت در صورت امکان.'
notes={17989:'شمارهٔ درج‌شده در عنوان منبع با شناسهٔ اعلامی آن یکسان نیست؛ شماره فنی روی خود قطعه باید تطبیق داده شود.',17941:'دسته‌بندی تلفن و عبارت Cat6 در دادهٔ منبع کنار هم آمده‌اند؛ نوع پورت RJ11/RJ45 را پیش از انتخاب مشخص کنید.',17935:'عنوان تلفن و عبارت Cat6 نیاز به بررسی دارند؛ تصویر و ابعاد ماژول باید با شماره فنی همان قطعه تطبیق یابند.',17888:'عنوان SFTP و ویژگی اعلامی STP یکسان نیستند؛ نوع شیلد را با دیتاشیت و قطعه تطبیق دهید.',17873:'در عنوان منبع LSZH و در ویژگی آن PVC ثبت شده است؛ نوع روکش و مدرک همان قرقره باید روشن شود.',17851:'عنوان اولیهٔ منبع دارای عبارت مبهم052 است؛ آن را شماره فنی معتبر یا ویژگی فیزیکی فرض نکنید.',17929:'در تصویر جعبه، نوشتهٔ076561 دیده می‌شود؛ این مشاهده به‌تنهایی تطبیق جعبه و قطعهٔ قابل‌تأمین را ثابت نمی‌کند.'}
catalog=json.loads((root/'content/catalog/saieedshabake-2026-10-15.json').read_text(encoding='utf-8'));by_source={p['source_id']:p for p in catalog['products']};dupes=collections.Counter(p['title']for p in base['posts']if p['type']=='product')
updates=[]
for p in base['posts']:
 after={}
 if p['id']==2:after={'post_status':'draft'}
 else:
  if p['id'] in excerpts:after['post_excerpt']=excerpts[p['id']]
  if p['id'] in pages:after['post_content']=blocks(pages[p['id']])
  if p['id'] in [109,110]:after['post_title']='تسویه حساب'if p['id']==109 else'حساب کاربری'
  if p['id']==62:
   body=p['content'];old='اگر اتصال شما قطع شود، روتر همه تغییرات جلسه را خودکار برمی‌گرداند و از قفل‌شدن بیرون از دستگاه جلوگیری می‌کند. این عادت ساده، رایج‌ترین فاجعه آموزشی را غیرممکن می‌کند.'
   assert old in body
   body=body.replace(old,'Safe Mode خطر از دست‌رفتن دسترسی را کم می‌کند، اما تضمین نیست. در قطع غیرعادی نشست، تغییرات قابل‌برگشت طبق رفتار RouterOS بازگردانده می‌شوند؛ این کار ممکن است تا پایان timeout طول بکشد. ظرفیت تاریخچه محدود است؛ با پرشدن آن، حالت امن می‌تواند خاتمه یابد. دستورهایی که reboot لازم دارند، مانند reset یا restore از backup، تحت این حفاظت نیستند. قبل از تغییر، نسخهٔ پشتیبان و مسیر دسترسی جایگزین داشته باشید.')
   body=body.replace('— بدون ترس از قفل‌شدن خودتان بیرون از روتر.','؛ با شناخت خطر از دست‌رفتن دسترسی و روش بازیابی.')
   body=body.replace('Safe Mode؛ بیمه‌نامه شما','Safe Mode؛ کاهش ریسک با محدودیت مشخص')
   body+='\n\n'+blocks('<p>منبع رفتار Safe Mode: <a href="https://help.mikrotik.com/docs/spaces/ROS/pages/8978498/Console">مستند رسمی MikroTik Console</a>. این درس برای تمرین است؛ نتیجهٔ تست روی مدل و نسخهٔ شما در این صفحه ادعا نشده است.</p>')
   after['post_content']=body
  if p['id'] in [26,40,62,63,64,65,66,67,70,71,76]:after['post_content']=after.get('post_content',p['content'])+'\n\n'+blocks('[tn_editorial_note]')
  if p['id'] in [8,29,31,33,35,37]:after['post_content']=p['content']+'\n\n'+blocks('<p>محدودهٔ کار، روش دسترسی و شرایط انجام خدمت پیش از اجرا مشخص می‌شود. <a href="/technical-methodology/">روش منابع و مستندسازی</a> و <a href="/contact/">اطلاعات لازم برای شروع درخواست</a> را ببینید.</p>')
  if p['type']=='product':
   sid=int(p['name'].split('-')[-1]);src=by_source[sid];sku=src['sku'];name=p['title'];newtitle=name+' — '+sku if dupes[name]>1 else name
   after['post_title']=newtitle;after['post_excerpt']=f'استعلام {name}؛ کد تهران نتورک {sku}. مدل، واحد فروش، موجودی و قیمت نهایی پیش از سفارش تطبیق داده می‌شوند.'
   kind='کابل'if sid<17880 else('پریز'if sid in [17989,17982]else('سوکت'if sid in [18002,17991]else'کیستون'))
   intro={'کابل':'برای انتخاب کابل، محیط نصب، شیلد، جنس روکش، متراژ و نوع اتصال ابتدا با نیاز پروژه تطبیق داده شوند. نام Cat6 به‌تنهایی نتیجهٔ تست مسیر را ثابت نمی‌کند.','پریز':'در انتخاب پریز، شماره فنی، رنگ، ابعاد ماژول، استاندارد اتصال و مشخصات درج‌شده روی خود قطعه اهمیت دارند. مشخصات الکتریکی را از ظاهر تصویر حدس نزنید.','سوکت':'برای انتخاب سوکت، نوع کابل، شیلد، قطر هادی و شیوهٔ نصب باید با مشخصات همان اتصال سازگار باشند. تصویر و نام دسته برای تأیید همهٔ این موارد کافی نیستند.','کیستون':'پیش از انتخاب کیستون، نوع پورت، پهن یا باریک‌بودن ماژول، نوع شیلد و سازگاری با قاب و کابل را بررسی کنید. شماره فنی، مبنای تطبیق نهایی است.'}[kind]
   attrs=src.get('source_attributes',[]);items=[]
   for a in attrs:
    key=a.get('name','');v=a.get('terms',a.get('options',[]));v='، '.join(str(t.get('name',t))if isinstance(t,dict)else str(t)for t in v)if isinstance(v,list)else str(v)
    if key and v:items.append('<li>'+html.escape(key)+': '+html.escape(v)+'</li>')
   declared='<ul>'+''.join(items)+'</ul>'if items else'<p>جزئیات فنی قابل‌اتکای بیشتری در ویژگی‌های ساختاریافتهٔ منبع ثبت نشده است؛ عبارت‌های عنوان باید با مدرک همان مدل بررسی شوند.</p>'
   review=notes.get(sid,'شماره فنی و تطبیق تصویر با همان کالای قابل‌تأمین هنوز نیازمند تأیید است.')
   if 'brand' in ' '.join(src['review_flags']):review+=' برند در بخش‌های منبع یکسان نیست؛ نام سازنده پیش از استعلام نهایی باید روشن شود.'
   if 'test-certificate-required' in src['review_flags']:review+=' ادعای Channel، Permanent یا Fluke بدون گزارش قابل‌انتساب به همان کالا، گواه عملکرد محسوب نمی‌شود.'
   body=f'<p>این رکورد کاتالوگ برای بررسی و استعلام <strong>{html.escape(name)}</strong> با کد <strong>{sku}</strong> است. کد تهران نتورک، شماره فنی سازنده نیست.</p>\n<h2>در انتخاب این {kind} چه چیزهایی را بررسی کنیم؟</h2>\n<p>{intro}</p>\n<h2>اطلاعات اعلامی منبع؛ نیازمند تطبیق</h2>\n{declared}\n<h2>مواردی که قبل از سفارش باید روشن شوند</h2>\n<p>{review}</p>\n<p>واحد فروش، محتویات بسته، شرایط ضمانت و ارسال، موجودی و قیمت نهایی در استعلام تهران نتورک مشخص می‌شوند. تصویر کاتالوگ، اعلام موجودی فیزیکی یا اثبات اصالت نیست.</p>\n<p>برای پیگیری این قلم، کد {sku} و شماره فنی موردنظر را اعلام کنید. <a href="/technical-methodology/">روش بررسی مشخصات و تصاویر</a> · <a href="/contact/">تماس برای استعلام</a></p>'
   after['post_content']=blocks(body)
 after={k:v for k,v in after.items()if v!=p[{'post_title':'title','post_content':'content','post_excerpt':'excerpt','post_status':'status'}[k]]}
 if after:updates.append({'id':p['id'],'type':p['type'],'url':p['url'],'before':{k:sha(p[{'post_title':'title','post_content':'content','post_excerpt':'excerpt','post_status':'status'}[k]])for k in after},'after':after})
new=[{'key':'methodology','slug':'technical-methodology','parent':0,'title':'روش منابع، آزمون و اصلاح محتوا','excerpt':'روش تهران نتورک برای منابع رسمی، تفکیک دادهٔ کاتالوگ از نتیجهٔ آزمایش، شناسایی مدل، نویسندگی و اصلاح خطاها.','content':blocks((root/'content/pages/technical-methodology.html').read_text(encoding='utf-8'))}, {'key':'mtu','slug':'wireguard-mtu','parent':7,'title':'برآورد MTU در WireGuard؛ ابزار محلی و محدودیت‌ها','excerpt':'محاسبهٔ محلی سربار پایهٔ WireGuard برای IPv4/IPv6 بیرونی، با نمونه‌های آزمودهٔ محاسبات، کد Python و محدودیت‌های روشن.','content':blocks((root/'content/pages/lab-wireguard-mtu.html').read_text(encoding='utf-8'))}]
terms=[{'id':t['id'],'taxonomy':t['taxonomy'],'before_sha256':sha(t['description']),'description':('مرور نوشته‌های منتشرشدهٔ '+t['name']+' در تهران نتورک؛ برای متن کامل، منابع و زمان ویرایش، صفحهٔ هر نوشته را ببینید.'if t['taxonomy']=='category'else'کالاهای دستهٔ '+t['name']+' در کاتالوگ تهران نتورک؛ تصویر و اطلاعات اعلامی را بررسی و مدل، قیمت، موجودی و شرایط تأمین را پیش از سفارش استعلام کنید.')}for t in base['terms']]
manifest={'schema':1,'operation':'approved-site-audit-remediation','posts':updates,'new_pages':new,'terms':terms,'files_before':base['files'],'preserve_noindex':True,'preserve_commercial_fields':True}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('CONTENT_REMEDIATION_MANIFEST',len(updates),'existing posts,',len(new),'new pages,',len(terms),'terms;no price/stock/media/source mutation')
