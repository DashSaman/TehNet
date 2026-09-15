# معماری اطلاعات و URL تهران نتورک

**تاریخ:** 2026-09-15  
**اصل:** هر Intent اصلی فقط یک Owner URL دارد. URL جدید زمانی ساخته می‌شود که Intent، نوع صفحه و ارزش کسب‌وکاری آن واقعاً مستقل باشد.

## Journeyهای اصلی
- `/learn/` — آموزش‌های عمومی و Topic Hubها.
- `/lab/` — فایل، اسکریپت، کانفیگ و دارایی عملی.
- `/services/` — هاب خدمات واقعی تهران و Remote Support سراسر ایران.
- `/shop/` — فروشگاه، محصولات دیجیتال و تجهیزات فیزیکی.

## Learn
- `/learn/mikrotik/` — Owner اصلی آموزش میکروتیک.
- `/learn/mikrotik/routeros/` — آموزش عملی RouterOS؛ فقط وقتی محتوای مستقل کافی دارد.
- `/learn/mikrotik/mtcna/` — راهنمای مسیر MTCNA؛ اولویت بلندمدت.
- `/learn/networking/` — مبانی شبکه؛ اولویت بلندمدت و فقط با پوشش عمیق.
- موضوعات Routing، VPN، Firewall و Linux می‌توانند بعد از پژوهش جداگانه hub یا child page شوند؛ نام URL از روی حدس ساخته نمی‌شود.

## Services
- `/services/` — صفحه هاب خدمات، نه archive خودکار CPT.
- `/services/network-tehran/` — خدمات شبکه تهران.
- `/services/network-support-tehran/` — پشتیبانی شبکه تهران.
- `/services/network-setup-tehran/` — راه‌اندازی شبکه شرکت در تهران.
- `/services/mikrotik-tehran/` — نصب/کانفیگ/رفع مشکل MikroTik در تهران.
- `/services/remote-support/` — پشتیبانی ریموت برای سراسر ایران.

## Shop و Lab
- `/shop/` — هاب تجاری.
- `/shop/mikrotik-routers/` — category مالک Intent خرید روتر MikroTik.
- `/shop/network-cable/cat6/` — فقط بعد از آماده‌شدن کاتالوگ/دسته واقعی؛ فعلاً NOT-YET.
- `/lab/` — هاب فایل‌ها؛ آیتم‌های مستقل در `/lab/{slug}/` ولی بدون archive جداگانه روی همان slug.

## Cannibalization
- مترادف‌های «خدمات شبکه تهران» نباید چند landing page هم‌هدف بسازند.
- یک ویدیوی YouTube به‌تنهایی دلیل ساخت URL نیست؛ ویدیو باید داخل Owner URL مرتبط قرار گیرد مگر Intent مستقل داشته باشد.
- صفحات محله‌ای/منطقه‌ای تهران ممنوع‌اند مگر خدمت، شواهد و محتوای منحصربه‌فرد واقعی وجود داشته باشد.
- مقاله آموزشی نباید برای Intent خرید یا درخواست خدمت مالک اصلی باشد؛ باید به Shop/Services لینک دهد.
