# ممیزی پوشش سرفصل رسمی MTCNA — تهنت

تاریخ بررسی: ۴ نوامبر ۲۰۲۶. مرجع اولیه: [سرفصل رسمی در سایت MikroTik](https://mikrotik.com/training/about) که به PDF با **آخرین ویرایش ۲۲ ژانویهٔ ۲۰۱۶** لینک می‌دهد: https://i.mt.lv/cdn/training_pdf/mtcna_outline_2019181161836.pdf. این تاریخ به معنی نسخهٔ ۲۰۲۶ سند نیست. تفاوت RouterOS 7.25.1/WinBox 4.5 و درایورهای جدید را باید مستقل بررسی کرد. هیچ دورهٔ مستقل تهنت گواهی رسمی سازنده را صادر نمی‌کند.

## سرفصل‌ها و مقصد در برنامهٔ ۴۰ قسمتی

| ماژول رسمی | جلسات پیشنهادی | وضعیت پوشش تحریریه | ایراد / اقدام پیش از مرجع‌نامیدن |
|---|---|---|---|
| ۱. Introduction | ۱–۹ و ۱۱ | محتوای قبلی و چند منبع مستقل موجود | Null Modem/Console و Telnet legacy، تاریخچه CLI، Quick Set نسخه‌محور، License و Netinstall با سخت‌افزار واقعی؛ باید شاهد واقعی داشته باشند |
| ۲. DHCP | ۱۱–۱۳ | متن DHCP و ARP تهیه شده | DHCP Client مستقل فقط GitHub است؛ ARP modes نیاز به آزمایش و screenshot دارد |
| ۳. Bridging | ۱۴–۱۵ | مبانی Bridge در WP و Station Bridge در GitHub | L2 bridge و Station Bridge بدون AP/Station سازگار تأیید عملی ندارد |
| ۴. Routing | ۱۶–۱۸ | Route Static و Dual LAN در WP، Dynamic و Flags در GitHub | Route flags و Source/Return route هنوز تست اجرای RouterOS 7 ندارند |
| ۵. Wireless | ۲۴–۲۶ | دو متن قدیمی WP و Access/Registration در GitHub | WPS accept/client و default-authenticate/default-forward میراث قدیمی، پشتیبانی جدید وابسته به سخت‌افزار؛ نباید آن را پیش‌فرض برای هر مدل فرض کرد |
| ۶. Firewall | ۱۹–۲۳ | Source/Dest NAT، ConnTrack، Filter و تقویت امن | Redirect و FastTrack باید تست هدفمند، Rule Order و rollback کامل و قابل نمایش داشته باشند |
| ۷. QoS | ۲۷–۲۹ | Simple Queue و PCQ/Burst پایه WP، PCQ مستقل GitHub | pcq-rate، pcq-limit و limit-at با دو کلاینت و ترافیک واقعی باید ثابت شوند |
| ۸. Tunnels | ۳۰–۳۳ | PPPoE و WireGuard WP، Profile و SSTP/PPTP GitHub | سرویس PPP و جزییات امنیت TLS آزموده نشده؛ PPTP فقط تاریخی/نامناسب برای استقرار امن |
| ۹. Misc | ۳۴–۳۶ | ابزارهای Ping و Netwatch، Supout منابع | E-mail tool، autosupout.rif و viewer باید اضافه شوند؛ جمع‌آوری شواهد نباید دادهٔ شبکه را عمومی کند |

## کمبودهای محتوایی اولویت‌دار

۱. **Telnet/Null Modem:** صرفاً به‌عنوان روش Legacy و ناامن معرفی شود؛ برای مدیریت فعلی SSH امن، WinBox مجاز، کنسول محدود توصیه شود.
۲. **WPS:** فقط با توجه به مدل و Package توضیح داده شود؛ استفادهٔ عمومی یا روشن‌کردن بی‌دلیل توصیه نشود.
۳. **E-mail Tool:** تنظیم SMTP و alert فقط در Lab مجاز و با مخفی‌سازی Credential آموزش داده شود؛ ارسال ایمیل واقعی به مقصد تصادفی یا عمومی انجام نشود.
۴. **Autosupout.rif:** علت تولید خودکار، مسیر فایل، نحوهٔ دریافت امن و محدودیت اطلاعات پشتیبانی مشخص شود.
۵. **دقت سئو:** برای هر URL intent اختصاصی و canonical تکلیف شود؛ استناد به کلیدواژه بدون محتوا و شواهد معتبر رتبه نمی‌آورد. سایت فعلاً noindex است.
۶. **مدت هر درس:** ۱۰–۱۵ دقیقه یک هدف ضبط است، نه تایم ثبت‌شده. پس از اجرای سناریو و ضبط، متن باید به این زمان برسد.
۷. **چشم‌انداز تصویری:** دیاگرام‌های کنونی مفهومی‌اند. اسکرین‌شات‌های اصلی با نسخه، مسیر منو و Alt فارسی لازم‌اند.

## آدرس‌های شاهد کار

- [فهرست لینک‌های ۴۰ درس](microcourse-drafts/PREVIEW_INDEX.fa.md)
- [نقشهٔ ۴۰ درس](10-15min-course-plan-2026-11-04.fa.md)
- [رسید ۳۰ WordPress Draft / یازده GitHub-only](microcourse-draft-receipts-2026-11-04.json)

**مرز حقیقت:** ۲۹ صفحهٔ WordPress در نگاشت جدید، یک پیش‌نویس legacy باقیمانده، ۱۱ درس source-only، صفر درس تازه واجد تأیید لاب، صفر وضعیت WordPress Native Future. ادعای «پوشش کاملاً تأییدشده MTCNA» هنوز مجاز نیست.
