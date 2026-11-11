# Local SEO تهران، GEO و AEO — برنامه شواهد‌محور
Reviewed: 2026-11-11. TehNet کسب‌وکار خدمات شبکه با حضور در تهران و پشتیبانی از راه دور در ایران است. نوشتن این برنامه **مجوز تغییر robots/WAF، ثبت مکان جعلی یا انتشار عمومی نیست**.

## هویت واحد محلی
- Brand: تهران نتورک / TehNet.
- URL canonical planned: https://tehnet.ir/
- Public phone in repository: 021-91018746.
- Public address in repository: تهران، آیت‌الله کاشانی، شاهین جنوبی.
- On-site: تهران (پس از هماهنگی). Remote: ایران. متن «سراسر کشور» نباید به بازدید حضوری تعمیم یابد.
- Source: https://github.com/DashSaman/TehNet/blob/main/AGENTS.md و https://tehnet.ir/contact/
- هر اصلاح NAP باید از تنظیمات مرکزی WordPress انجام و متن فوتر، LocalBusiness، صفحات تماس، پیش‌فاکتور و کانال‌های رسمی بازخوانی شود. نشانی دقیق، ساعات و اطلاعات حقوقیِ تأییدنشده اختراع نشوند.

## Google Business Profile / Maps
Google طبق صفحه رسمی Supported countries/regions، Business Profile را در ایران پشتیبانی نمی‌کند: https://support.google.com/business/answer/6270107?hl=en (بررسی 2026-11-11). بنابراین ایجاد/تأیید GBP برای تهران را به‌عنوان milestone قابل اجرا پیشنهاد نمی‌کنیم. وجود پین یا review در ارائه‌دهنده کسب‌وکار دیگر، **اثبات GBP verified نیست**. Local SEO روی اطلاعات واقعی سایت، پوشش تهران، صفحات خدمات معتبر و منابع محلی/صنفی مجاز متمرکز باشد. صفحه شهر/محله مصنوعی ممنوع.

## معماری محلی
- https://tehnet.ir/services/network-tehran/ صفحه مادر و قصد «خدمات شبکه تهران».
- https://tehnet.ir/services/network-setup-tehran/ برای طراحی/راه‌اندازی.
- https://tehnet.ir/services/network-support-tehran/ برای قرارداد/عیب‌یابی.
- https://tehnet.ir/services/mikrotik-tehran/ برای روتر/MikroTik.
- پیشنهاد مشروط: /services/passive-network-tehran/ **فقط** پس از تأیید خدمات واقعی پسیو. کابل‌کشی و پسیو را در فاز اول بی‌دلیل به دو صفحه هم‌معنی تقسیم نکنید.
- صفحه «در غرب/شمال/شرق تهران» تنها وقتی قابل دفاع است که تجربه، بازه سرویس‌دهی، تصاویر واقعی یا فرآیند متفاوت و مستقل داشته باشد؛ در غیر این صورت هیچ URL محلی اضافه نشود.

## ساختار پاسخ قابل ارجاع — AEO
صفحه‌ای که مخاطب سؤال مشخص دارد با پاسخ کوتاه و دقیق 2–4 جمله‌ای شروع شود؛ سپس شرایط، استثنا، جدول تصمیم و منبع معتبر را بیاورد. نمونه پاسخ‌ها:
1. هزینه کابل‌کشی = متره، نقاط، قطعات، دستمزد، مسیر، آزمون و مدارک تحویل؛ بدون نقشه/بازدید عدد قطعی ندهید.
2. اکتیو/پسیو = پسیو بستر کابل/رک/پچ؛ اکتیو پیکربندی سوئیچ، روتر و سرویس؛ تحویل هر دو با آزمون خودش.
3. قرارداد پشتیبانی = دارایی مشمول، ساعات پوشش، اولویت رخداد، Response vs Resolution، خروجی گزارش و استثنا.
4. دفتر ۲۰ نفره = تعداد کاربر با تعداد پورت برابر نیست؛ چاپگر/AP/PoE/رشد و بازدید را لحاظ کنید.
5. تست فلوک = برند ابزار نیست معادل گزارش certification؛ تست‌لیمیت، شناسه لینک، Permanent Link یا Channel و تاریخ بررسی شوند.
6. تعویض کابل = تنها بر اساس نشانه اختلال تصمیم نگیرید؛ نتیجه عیب‌یابی اتصال، محیط، آسیب و آزمون لازم است.
7. هزینه نگهداری = تجهیزات، کاربران، دامنه، ساعات حضور/ریمو‌ت، هزینه قطعه/لایسنس و مسئولیت طرف ثالث.

این پاسخ‌ها **برای تولید محتوای متخصص** هستند و عملکرد واقعی مشتری/گواهی Fluke یا قیمت TehNet را ادعا نمی‌کنند.

## GEO / AI Search
Google Search Central در https://developers.google.com/search/docs/appearance/ai-features و https://developers.google.com/search/docs/fundamentals/ai-optimization-guide می‌گوید قابلیت AI Search بر crawl/index/snippet و اصول SEO متکی است؛ schema یا llms.txt ویژه لازم نیست. تشخیص و رفع noindex و تولید متن/شواهد واقعی اولویت بالاتر از ترفندهای «AI chunking» هستند. Schema.org Service/Organization/LocalBusiness/Breadcrumb/Article فقط با entity واقعاً نمایان و بدون Review ساختگی.

### کنترل تفکیک crawlerها
robots.txt فعلی TehNet (خوانش 2026-11-11) Cloudflare Content-Signal search=yes,ai-train=no,use=reference و Disallow: / برای تعدادی training bot از جمله GPTBot، Google-Extended، ClaudeBot دارد. این policy را بی‌مجوز تغییر ندهید. Google-Extended کنترل آموزشی/کاربری دیگر است؛ نشانه‌گذاری Search Googlebot را با training conflated نکنید. پاسخ‌دهی موتورهای AI و crawl/training یک رویداد نیستند.

### ماتریس آزمون AI citation (مدارک، نه ادعا)
۷ prompt بالا را در یک مجموعه ثابت، برای هر موتور مجاز (Google AI Overviews/AI Mode در صورت نمایش، ChatGPT Search، Perplexity، Bing/Copilot در صورت دسترسی) اجرا و ثبت کنید:
- تاریخ و ساعت منطقه، زبان، کشور/دستگاه در صورت اطلاع، موتور و مدل/سطح، نسخه prompt.
- نمایش یا عدم نمایش AI پاسخ، نام دامنه ذکرشده، URL منبع کلیک‌پذیر، صحت پاسخ و وجود تضاد.
- اگر موتور پاسخ AI نداد، N/A بنویسید نه 0 citation.
- منبع ورودی درخواست واقعی/پرسش مشتری هرگز بدون مجوز در جست‌وجوی عمومی تزریق نشود.
- سه نوبت هم‌روش در روزهای جدا بهتر از ادعای «۱۰۰٪ AI citation» با نمونه یک‌باره است.

## Local authority و لینک‌سازی
- صفحه درباره و تماس با مسئول متخصص واقعی، نقش و روش کار؛ سابقه/مجوز فقط با مدرک.
- پروژه با اجازه کتبی، عکس و خروجی فنی سانسورشده؛ نام برند کارفرما فقط با رضایت.
- معرفی در سازمان صنفی، تأمین‌کننده و مشتری تنها با رابطه واقعی. جدول ۱۲ فرصت در authority-opportunities-12.csv آماده است.
- از لینک انبوه، PBN، رپورتاژ فریبنده و خرید نظر خودداری کنید. لینک‌سازی باید نتیجه همکاری/ارزش واقعی باشد، نه ساخت سیگنال مصنوعی.
- پوشش NAP در 3–5 منبع واقعی کافی‌تر از ساخت هزار citation ناهمسان است؛ عدد هدف صرفاً برنامه عملیاتی قابل تعدیل است، نه معیار رتبه گوگل.

## معیارهای کنترل کیفیت و تبدیل
Page/Query Clicks/Impressions/CTR (GSC پس از رفع دسترسی)، lead generated و accepted، quote request، contract request، signed contract، و lead source attribution. هر فرم یک شناسه غیرحساس داشته باشد و تماس روی لینک، تماس موفق فرض نشود. ثبت consent و جلوگیری از duplicate لازم است.

## منابع
- Google AI requirements: https://developers.google.com/search/docs/appearance/ai-features
- Google helpful content: https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- GBP availability: https://support.google.com/business/answer/6270107?hl=en
- LocalBusiness schema: https://developers.google.com/search/docs/appearance/structured-data/local-business
- Google Spam: https://developers.google.com/search/docs/essentials/spam-policies
