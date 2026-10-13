"""Render the owner-approved public résumé as native editable WordPress content."""
from pathlib import Path
import html
R=Path(__file__).resolve().parents[2];T=R/'site/themes/tehnet'
art=(T/'assets/img/network-art.svg').read_text()
figure='<figure class="tn-home-network"><div class="tn-art-label"><span>AG / DIGITAL CONNECTIONS</span><b>✳</b></div>'+art+'<figcaption><span>شبکه، زیرساخت و ارتباطات</span><span>تصویرسازی مفهومی</span></figcaption></figure>'
skills=[('Network+','پیشرفته','network'),('DHCP Administration','پیشرفته','network'),('MTCNA','پیشرفته','network'),('CCNA','متوسط','network'),('MikroTik','متوسط','network'),('Routing','متوسط','network'),('VMware / ESXi','متوسط','systems'),('Active Directory','متوسط','systems'),('SQL Server','متوسط','systems'),('A+','متوسط','systems'),('Photoshop','متوسط','tools'),('Linux','مقدماتی','systems'),('Windows Server','مقدماتی','systems'),('WordPress','مقدماتی','tools')]
items=''.join(f'<div class="tn-skill" data-group="{group}"><strong lang="en" dir="ltr">{name}</strong><small>{level}</small></div>' for name,level,group in skills)
profile='''<!-- wp:html -->
<section class="tn-profile-hero" aria-labelledby="tn-profile-name"><div><p class="tn-kicker">شبکه، زیرساخت و آدم‌ها</p><h1 class="tn-profile-name" id="tn-profile-name">امیررضا <span>گل‌آور.</span></h1><p class="tn-name-en" lang="en" dir="ltr">AMIRREZA GOLAVAR</p><h2 class="tn-profile-title">کارشناس شبکه و زیرساخت<br>پشتیبانی فناوری اطلاعات</h2><p class="tn-profile-lead">از پشتیبانی محیط‌های سازمانی تا آموزش کاربردی شبکه؛ تمرکزم بر حل مسئله، یادگیری عملی و تبدیل دانش فنی به راهکار قابل استفاده است.</p><div class="tn-v-buttons"><a class="tn-v-button" href="#experience">مسیر حرفه‌ای من ↙</a><a class="tn-v-button tn-v-outline" href="/wp-content/themes/tehnet/assets/profile/Amirreza-Golavar-Resume.txt" download>دریافت رزومه ↓</a></div><p class="tn-profile-meta">تهران، ایران · <a href="https://tehnet.ir" lang="en">tehnet.ir</a></p></div>'''+figure+'''</section>
<nav class="tn-profile-nav" aria-label="بخش‌های رزومه"><a href="#about-me">درباره من</a><a href="#skills">مهارت‌ها</a><a href="#experience">سوابق حرفه‌ای</a><a href="#brands">برندها</a><a href="#education">تحصیلات</a><a href="#profile-contact">ارتباط با من</a></nav>
<section class="tn-profile-section tn-profile-columns" id="about-me"><div><p class="tn-kicker">01 / درباره من</p><h2>از تجربه عملی،<br>تا راهکار قابل استفاده.</h2></div><div><p>من امیررضا گل‌آور هستم؛ دانش‌آموخته مهندسی کامپیوتر، با تجربه در شبکه، پشتیبانی فنی و سامانه‌های ارتباطی سازمانی.</p><p>مسیر حرفه‌ای من از مدیریت دفتر فنی و چاپ دیجیتال عبور کرده و به پشتیبانی فناوری اطلاعات و فعالیت مستقل آموزشی و پروژه‌ای رسیده است. در تهران نتورک، آموزش را در کنار تجربه عملی و خدمات فنی دنبال می‌کنم.</p><p>تک‌پاتوق، تهران نتورک و TehNet بخش‌های یک مسیر شخصی‌اند. در کنار این فعالیت، با سامان کلانتری و محمدرضا وظیفه اردلانی در برند MyTel شریک هستم.</p><div class="tn-profile-tags"><span>یادگیری عملی</span><span>عیب‌یابی دقیق</span><span>مستندسازی</span></div></div></section>
<section class="tn-profile-section" id="skills"><p class="tn-kicker">02 / مهارت‌ها</p><h2>ابزارهایی برای ساختن ارتباط.</h2><div class="tn-skill-filters tn-js-only" role="group" aria-label="فیلتر مهارت‌ها"><button type="button" data-tn-filter="all" aria-pressed="true">همه</button><button type="button" data-tn-filter="network" aria-pressed="false">شبکه</button><button type="button" data-tn-filter="systems" aria-pressed="false">سیستم‌ها</button><button type="button" data-tn-filter="tools" aria-pressed="false">ابزارها</button></div><div class="tn-skills">'''+items+'''</div><p class="tn-disclaimer">سطوح مهارت مطابق ارزیابی اعلام‌شده در رزومه ارائه‌شده‌اند؛ نام دوره‌ها به معنی دریافت گواهینامه رسمی بین‌المللی نیست.</p></section>
<section class="tn-profile-section tn-profile-columns" id="experience"><div><p class="tn-kicker">03 / مسیر حرفه‌ای</p><h2>تجربه‌هایی که<br>نگاهم را شکل داده‌اند.</h2><p>از مدیریت دفتر فنی تا پشتیبانی سازمانی و فعالیت مستقل در شبکه و آموزش.</p><div class="tn-founder-monogram" aria-hidden="true">AG</div></div><div class="tn-profile-timeline">
<details class="tn-work" open><summary><small>شروع ثبت‌شده: اسفند ۱۴۰۳</small><strong>کارشناس فنی شبکه</strong><span>رایان نیک تجهیز — در محیط بانک صادرات</span></summary><p>پشتیبانی فنی در محیط سازمانی و کار با سامانه‌های ارتباطی و جلسات مجازی؛ بررسی مسائل کاربران، اتاق‌ها، تنظیمات جلسات و سرویس‌ها.</p><div class="tn-profile-tags"><span>Cisco Meeting Server</span><span>Cisco Meeting Management</span><span>Call Profile</span></div><p class="tn-disclaimer">تاریخ درج‌شده، زمان شروع این سابقه است.</p></details>
<details class="tn-work" open><summary><small>فعالیت مستقل آموزشی و پروژه‌ای</small><strong>تهران نتورک | TehNet</strong><span>شبکه، آموزش و خدمات فنی</span></summary><p>فعالیت شخصی در زمینه محتوای آموزشی فناوری، موضوعات شبکه، سرورهای لینوکسی و تونل‌سازی. این مسیر با هویت تک‌پاتوق شناخته شده و با نام تهران نتورک و TehNet ادامه یافته است.</p><div class="tn-profile-tags"><span>آموزش کاربردی</span><span>فعالیت پروژه‌ای</span><span>محتوای فنی</span></div></details>
<details class="tn-work"><summary><small>فروردین ۱۳۹۸ — شهریور ۱۴۰۱</small><strong>مدیر دفتر فنی</strong><span>چاپ پازل</span></summary><p>امور دفتر فنی، تجهیزات چاپ Ricoh و Konica، پلاتر، چاپ Eco-Solvent، لیزر غیرفلزات و شناخت متریال‌های چاپ.</p><div class="tn-profile-tags"><span>Digital Printing</span><span>Ricoh / Konica</span><span>Eco-Solvent</span></div></details>
<details class="tn-work"><summary><small>اردیبهشت ۱۳۹۳ — اسفند ۱۳۹۷</small><strong>مدیر دفتر فنی</strong><span>چاپ فتوتایپ</span></summary><p>مدیریت امور دفتر فنی، کار با تجهیزات چاپ، خدمات تبلیغاتی و پیگیری عملیات سفارش و تولید.</p><div class="tn-profile-tags"><span>دفتر فنی</span><span>سفارش و تولید</span><span>خدمات چاپ</span></div></details>
</div></section>
<section class="tn-profile-section" id="brands"><p class="tn-kicker">04 / برندها</p><h2>آموزش، فناوری و همکاری.</h2><div class="tn-profile-brands"><article class="tn-profile-brand"><div class="tn-brand-visual" aria-hidden="true"><span>TehNet</span></div><p class="tn-kicker">برند شخصی</p><h3 lang="en">TehNet</h3><p>تهران نتورک؛ آموزش کاربردی، محتوای تخصصی و فعالیت‌های خدماتی شبکه، در ادامه مسیر تک‌پاتوق.</p><a href="/">ورود به تهران نتورک ←</a></article><article class="tn-profile-brand"><div class="tn-brand-visual" aria-hidden="true"><span>MyTel</span></div><p class="tn-kicker">برند مشترک</p><h3 lang="en">MyTel</h3><p>خدمات VoIP و ارتباطات سازمانی؛ یک فعالیت مشترک در زمینه سیستم‌های تلفنی کسب‌وکارها.</p><a href="https://mytel.one" target="_blank" rel="noopener noreferrer">ورود به مایتل ↗</a></article></div><p class="tn-disclaimer">MyTel فعالیت مشترک امیررضا گل‌آور، سامان کلانتری و محمدرضا وظیفه اردلانی است؛ از شراکت، سهم مساوی یا اجرای شخصی تمام خدمات نتیجه گرفته نمی‌شود.</p></section>
<section class="tn-profile-section" id="education"><p class="tn-kicker">05 / یادگیری</p><h2>تحصیلات و دوره‌های آموزشی.</h2><div class="tn-profile-education"><div><article class="tn-degree"><small>۱۳۹۴ — ۱۳۹۷</small><h3>کارشناسی مهندسی کامپیوتر</h3><p>گرایش نرم‌افزار<br>دانشگاه آزاد اسلامی، واحد تهران شمال</p></article><article class="tn-degree" style="margin-top:17px"><small>۱۳۹۲ — ۱۳۹۴</small><h3>کاردانی مهندسی کامپیوتر</h3><p>گرایش نرم‌افزار<br>سما تهران</p></article></div><div><div class="tn-course"><div><strong lang="en">Help Desk</strong><p class="tn-disclaimer">مهندس مهدی شالهی · ۱۴۰۳</p></div><span>۱۶۰ ساعت</span></div><div class="tn-course"><div><strong lang="en">CCNA</strong><p class="tn-disclaimer">مهندس عباس ولی‌زاده · ۱۴۰۳</p></div><span>۱۳۲ ساعت</span></div><div class="tn-course"><div><strong lang="en">MTCNA</strong><p class="tn-disclaimer">مجید برکاتی · ۱۴۰۳</p></div><span>دوره آموزشی</span></div><p class="tn-disclaimer">این بخش، دوره‌های آموزشی گذرانده‌شده را معرفی می‌کند؛ ادعایی درباره دریافت گواهینامه رسمی Cisco یا MikroTik مطرح نیست.</p></div></div></section>
<section class="tn-profile-section" id="profile-contact"><div class="tn-profile-contact"><p class="tn-kicker">06 / ارتباط حرفه‌ای</p><h2>یک گفت‌وگوی خوب،<br>شروع یک ارتباط تازه.</h2><p>برای گفت‌وگو درباره شبکه، پشتیبانی فنی، آموزش یا همکاری‌های مرتبط، از راه‌های زیر در ارتباط باشیم.</p><p>تهران، ایران</p><div class="tn-contact-list"><a href="mailto:golamirreza1995@gmail.com" dir="ltr">golamirreza1995@gmail.com</a><a href="https://t.me/tehrannetwork021" target="_blank" rel="noopener noreferrer" dir="ltr">@tehrannetwork021 ↗</a><a href="https://www.youtube.com/@tehran.network021" target="_blank" rel="noopener noreferrer" dir="ltr">YouTube ↗</a></div><div class="tn-v-buttons"><a class="tn-v-button tn-v-outline" href="/wp-content/themes/tehnet/assets/profile/Amirreza-Golavar.vcf" download>ذخیره کارت تماس</a><button class="tn-v-button tn-v-outline tn-js-only" type="button" data-tn-print>چاپ رزومه</button></div></div></section>
<!-- /wp:html -->
'''
(R/'content/pages/amirreza-golavar.html').write_text(profile)
resume='''امیررضا گل‌آور | Amirreza Golavar
کارشناس شبکه، زیرساخت و پشتیبانی فناوری اطلاعات
تهران، ایران
ایمیل: golamirreza1995@gmail.com
وب‌سایت: https://tehnet.ir

معرفی
دانش‌آموخته مهندسی کامپیوتر ـ نرم‌افزار و فعال حوزه شبکه و پشتیبانی سازمانی. فعالیت مستقل آموزشی و خدماتی با هویت تک‌پاتوق، تهران نتورک و TehNet. یکی از سه شریک MyTel، همراه با سامان کلانتری و محمدرضا وظیفه اردلانی.

سوابق حرفه‌ای
رایان نیک تجهیز، در محیط بانک صادرات — کارشناس فنی شبکه
شروع ثبت‌شده: اسفند ۱۴۰۳. پشتیبانی سازمانی و سامانه جلسات، Cisco Meeting Server و Cisco Meeting Management، تنظیمات کاربران، اتاق‌ها و Call Profile. ادامه اشتغال فعلی در این سند تأیید نشده است.

تهران نتورک | TehNet — فعالیت مستقل آموزشی و پروژه‌ای
آموزش و محتوای فنی شبکه، فعالیت‌های پروژه‌ای و موضوعات سرورهای لینوکسی و تونل‌سازی. به دلیل نیاز به تطبیق تاریخچه برند، بازه استخدامی قطعی برای این بخش درج نشده است.

چاپ پازل — مدیر دفتر فنی
فروردین ۱۳۹۸ تا شهریور ۱۴۰۱. تجهیزات Ricoh و Konica، پلاتر، چاپ Eco-Solvent و لیزر غیرفلزات.

چاپ فتوتایپ — مدیر دفتر فنی
اردیبهشت ۱۳۹۳ تا اسفند ۱۳۹۷. امور دفتر فنی، تجهیزات چاپ، سفارش و تولید و خدمات تبلیغاتی.

تحصیلات
کارشناسی مهندسی کامپیوتر ـ نرم‌افزار، دانشگاه آزاد اسلامی واحد تهران شمال، ۱۳۹۴ تا ۱۳۹۷.
کاردانی مهندسی کامپیوتر ـ نرم‌افزار، سما تهران، ۱۳۹۲ تا ۱۳۹۴.

دوره‌های آموزشی
Help Desk، ۱۶۰ ساعت، مهندس مهدی شالهی، ۱۴۰۳.
CCNA، ۱۳۲ ساعت، مهندس عباس ولی‌زاده، ۱۴۰۳.
MTCNA، مجید برکاتی، ۱۴۰۳.
دوره‌های آموزشی به‌عنوان گواهینامه رسمی بین‌المللی معرفی نمی‌شوند.

مهارت‌ها — سطح اعلام‌شده در رزومه ارائه‌شده
پیشرفته: Network+، DHCP Administration، MTCNA.
متوسط: CCNA، MikroTik، Routing، VMware/ESXi، Active Directory، SQL Server، A+ و Photoshop.
مقدماتی: Linux، Windows Server و WordPress.

برندها
TehNet / تهران نتورک: برند شخصی امیررضا؛ ادامه فعالیت محتوایی تک‌پاتوق.
MyTel: برند مشترک سه‌نفره خدمات VoIP و ارتباطات سازمانی.
هیچ سهم مساوی، عنوان حقوقی یا اجرای شخصی همه پروژه‌های برندهای مشترک ادعا نشده است.

مبنای محتوا: اطلاعات ارائه‌شده و اصلاح انتساب هویت‌ها در ۱۳ اکتبر ۲۰۲۶.
'''
(T/'assets/profile/Amirreza-Golavar-Resume.txt').write_text(resume)
vcf=['BEGIN:VCARD','VERSION:3.0','N:گل‌آور;امیررضا;;;','FN:امیررضا گل‌آور','TITLE:کارشناس شبکه و زیرساخت','EMAIL;TYPE=INTERNET:golamirreza1995@gmail.com','URL:https://tehnet.ir/amirreza-golavar/','END:VCARD']
(T/'assets/profile/Amirreza-Golavar.vcf').write_bytes(('\r\n'.join(vcf)+'\r\n').encode())
print('Prepared editable public résumé, text download and contact card.')
