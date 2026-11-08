# درس‌های قابل انتقال به چارچوب مرکزی SEO — نسخهٔ دوم
وضعیت: پیش‌نویس قابل بازبینی در شاخهٔ SEO تهران نتورک؛ به مخزن DashSaman/-SEO نوشته یا merge نشده است. استثنای اسکن خصوصی مالک فقط همین شاخهٔ TehNet را پوشش می‌دهد. چارچوب مرکزی با ref52cc1f110e18a8111eda657ae92368e837d46fb3 و docs/content-quality.md و اسناد مالکیت intent/پذیرش خدمات استفاده شد. پوشهٔ تحقیق تاریخ‌دار404 مانع استفاده از اسناد واقعی ریشه نبود.

۱. **موجودی URL از هویت داده استخراج شود:** نام‌های رایج cart/checkout/my-account به‌تنهایی کافی نیست. این سایت pageهای منتشرشدهٔ cart-2/tn-checkout/tn-account دارد و aliasهای قدیمی draft هستند. inventory هویت و status را از دادهٔ واقعی بخواند؛ خواندن هویت یک URL را با crawl کامل آن یکی نگیرد.

۲. **مالکیت intent تغییر محتوا را تعیین کند:** owner29 انتخاب مسیر، owner33 زیرساخت پروژه، owner31 رخداد/نگهداری، owner35 تغییر RouterOS و N1 workload/سرور هستند. هنگام مستقل‌کردن N1، بخش مفصل تکراری در33 به خلاصه و لینک تبدیل شد و anchor قبلی حفظ شد. صرف ساخت صفحهٔ بلندتر، دلیل مقصد مستقل نیست.

۳. **مقالهٔ تجاری باید ابزار تصمیم داشته باشد:** چهار متن کامل همراه جدول خالی، مثال صریحاً فرضی، ستون منبع/سؤال باز/پذیرش و نسخهٔ CSV/چاپی آماده شدند. UNKNOWN و NOT_TESTED برای دادهٔ واقعاً نامعلوم‌اند؛ ادعای سناریوی مشتری یا اندازه‌گیری نیستند. قالب کامل با عنوان/outline کاندیدا تفاوت دارد.

۴. **اعتبار فنی به محصول/نسخه محدود شود:** checkpoint در Hyper-V و snapshot در فرایند Azure Backup یک حکم عام و متناقض نمی‌سازند. صفحهٔ frozen سازنده را جاری معرفی نکنید؛ URL403 یا مسیر حدسی خوانده‌نشده شاهد فنی نیست. نام Hyper-V/VMware/Proxmox در یک خدمت، تأیید مجوز، نسخه یا سازگاری آن پروژه نیست.

۵. **مدل محتوا، مسیر انتشار و schema هماهنگ باشند:** این چهار مقاله pageهای تحریریهٔ Gutenberg هستند، چون مدل واقعی سایت آموزش/تحریریه را هم با page اداره می‌کند. author سازمان واقعی است. خدمت N1 نباید با Article یا reviewer ساختگی علامت‌گذاری شود. title/H1/meta و body هر کدام باید در دامنهٔ manifest روشن باشند.

۶. **ثبت فرم را با ذخیرهٔ تیکت بسنجید:** CTA در N1 باید به context مجاز همان فرم و handler قدیمی برسد؛ اثبات موفقیت شامل رسید بدون دادهٔ خصوصی، ذخیرهٔ canonical private ticket/thread، منفی‌های nonce/context/honeypot/CAPTCHA و حذف رکورد خود آزمون است. transport ساختگی Google، چالش واقعی CAPTCHA نیست.

۷. **noindex را با producers و حدود اختیار گزارش کنید:** source blog_public0 قبلاً ثابت شده است. حذف متن meta، خاموش‌کردن global visibility یا پاک‌کردن همهٔ فیلترها راهکار محدود نیست. پیشنهاد این بسته option صریح OFF/allowlist است؛ فقط producer شناخته‌شدهٔ هسته را برای درخواست canonical مجاز کنار می‌گذارد و تعارض دیگر را برای توقف پذیرش باقی می‌گذارد. crawl، index، رتبه، AI discovery و AI training مترادف نیستند.

۸. **پذیرش publisher با rollback و دادهٔ واقعیِ fixture است:** scope جدید باید همان immutable bundle، backup، guard، journal و native migration را گسترش دهد. پنج owner موجود، پنج page تازه و دارایی‌های static دقیق مالکیت دارند؛ rollback ownerها را برمی‌گرداند و page تازه را draft می‌کند. «همه‌چیز کامل restore شد» بدون توضیح این رفتار درست نیست. index rollback فقط option و فایل خود را برمی‌گرداند و نباید مشتری تازه را از DB حذف کند.

۹. **آزمون خودکار جای مشاهدهٔ بصری انسانی نیست:** چهار اندازه، حالت‌های واقعی JS، RTL، DOM، overflow و HTTP می‌توانند خودکار آزموده شوند. وقتی مالک انتشار تصویر را نخواسته، تصاویر/ویدیو تولید نکنید و ادعای بازبینی دستی ظاهر نداشته باشید. no-JS فعلی روشن است؛ dark بدون JS را از color-scheme شبیه‌سازی‌شده نتیجه نگیرید.

۱۰. **وضعیت‌ها را جمع نکنید:** متن کامل، fixture پذیرفته، merge، publication و indexed URL پنج شمارندهٔ مستقل‌اند. CI سبز شاهد competitive parity نیست. دادهٔ GSC/Bing سایت ناموجود را با property برند دیگر جایگزین نکنید. MyTel مالک تخصص PBX/IVR می‌ماند و لینک زمینه‌دار تعهد عملیاتی مشترک ایجاد نمی‌کند.

پیوندهای بازبینی:
- ../../content/commercial-decision-2026-11-08-v2/README.fa.md
- ../../seo/index-decision-2026-11-08-v2/README.fa.md
- https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- https://developers.google.com/search/docs/crawling-indexing/block-indexing
