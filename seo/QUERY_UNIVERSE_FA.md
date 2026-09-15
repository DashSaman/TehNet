# جهان کوئری فارسی TehNet

**تاریخ مشاهده:** 2026-09-15  
**بازار:** ایران / فارسی  
**قاعده:** اول Intent و Page Type، سپس Business Value و Owner URL. برای ایران هیچ Volume یا KD ساختگی ثبت نمی‌شود.

| Cluster | Query | Intent | Page Type | Business Value | Owner URL | Decision |
|---|---|---|---|---|---|---|
| MikroTik Learn | آموزش میکروتیک | آموزشی/یادگیری | Topic hub | جذب مخاطب تخصصی و اتصال به Lab/Services | `/learn/mikrotik/` | GO |
| MikroTik Learn | آموزش RouterOS | آموزشی عملی | Tutorial/Hub child | تخصص مستقیم TehNet | `/learn/mikrotik/routeros/` | GO |
| MikroTik Learn | آموزش MTCNA فارسی | دوره/آموزشی | Guide / course-comparison style | رقابت با دوره‌های تجاری؛ فاز اول رایگان | `/learn/mikrotik/mtcna/` | GO-LONG-TERM |
| Network Learn | آموزش شبکه کامپیوتری | آموزشی گسترده | Topic hub | ورودی بالای قیف ولی رقابت/ابهام زیاد | `/learn/networking/` | GO-LONG-TERM |
| Services | خدمات شبکه تهران | تراکنشی محلی | Service landing | هسته درآمد حضوری | `/services/network-tehran/` | GO |
| Services | پشتیبانی شبکه تهران | تراکنشی محلی | Service landing | قرارداد/پشتیبانی سازمانی | `/services/network-support-tehran/` | GO |
| Services | راه اندازی شبکه شرکت تهران | تراکنشی محلی | Service landing | پروژه اجرایی | `/services/network-setup-tehran/` | GO |
| MikroTik Services | خدمات میکروتیک تهران | تراکنشی محلی | Service landing | تطابق مستقیم با تخصص | `/services/mikrotik-tehran/` | GO |
| Remote Support | پشتیبانی شبکه از راه دور | تراکنشی | Service landing | پوشش سراسر ایران | `/services/remote-support/` | GO |
| Shop | خرید روتر میکروتیک | تجاری/خرید | Product category | فروش/استعلام تجهیز | `/shop/mikrotik-routers/` | GO |
| Shop | قیمت کابل شبکه cat6 | تجاری/قیمت | Category / product | استعلام قیمت و تأمین | `/shop/network-cable/cat6/` | NOT-YET |
| Local expansion | خدمات شبکه غرب تهران / محله‌ها | تراکنشی محلی | Doorway risk | فقط در صورت محتوای/عملیات واقعی مستقل | owner اصلی خدمات تهران | LOW-PRIORITY |

## قواعد تصمیم
- یک Intent منسجم فقط یک Owner URL اصلی دارد؛ صفحات مترادف برای تصاحب یک کوئری ساخته نمی‌شوند.
- Learn برای آموزش، Services برای تقاضای اجرا/پشتیبانی، Shop برای خرید/استعلام و Lab برای فایل/اسکریپت است.
- ویدیوهای YouTube خودکار یک URL جدید نمی‌گیرند؛ فقط وقتی Intent مستقل و محتوای کافی وجود داشته باشد صفحه مستقل می‌سازیم.
- صفحات محله‌ای تهران تا زمانی که خدمت، شواهد و محتوای واقعاً مستقل ندارند ساخته نمی‌شوند.
