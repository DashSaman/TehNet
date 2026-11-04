# برنامه بازآرایی MTCNA تهران نتورک: جلسات ۱۰ تا ۱۵ دقیقه‌ای

**وضعیت: طرح اجرایی، نه ادعای آماده‌بودن ۴۰ پیش‌نویس یا زمان‌بندی WordPress.** تهیه‌شده بر پایه ۲۴ متن موجود، ۹ ماژول رسمی سال ۲۰۱۶ و مستندات RouterOS 7. نسل تازه سرفصل‌های رسمی را باید مستقلاً رصد کرد.

## قرارداد محتوایی و ضبط

- هر جلسه یک هدف مشخص: روایت ۶–۸ دقیقه + نمایش عملی ۴–۶ دقیقه + مرور ۱ دقیقه؛ ضبط نهایی ۱۰–۱۵ دقیقه.
- متن خواندنی و مستقل فارسی: پاسخ کوتاه، پیش‌نیاز، توپولوژی، GUI/CLI، علت هر تنظیم، نتایج مورد انتظار (نه ادعای واقعی)، خطاهای رایج، rollback، تمرین، منبع رسمی.
- هر آزمایش عملی و اسکرین‌شات باید واقعی و مبتنی بر نسخه مشخص RouterOS باشد؛ عکس فنی SVG صرفاً تصویر توضیحی است.
- اعتبارسنجی محتوا: متخصص + اجرای CHR/سخت‌افزار متناسب + دقت نسخه + ذخیره Gutenberg + تست پیوند/اسلاگ و noindex.
- دوره مستقل است؛ بخش Queue در فیلم‌های قبلی تدریس مفصل نشده و به آن‌ها نسبت داده نشود.
- صفحات ۴۰ و ۶۲–۶۷ منتشر هستند؛ با Future کردن منتشرشده‌ها یا انتشار دوباره همان متن به URL دیگر، محتوا را تکراری نکنید.
- نخستین پنجره انتشار: شنبه ۷ نوامبر ۲۰۲۶، ساعت ۹ تهران، سپس هر ۳ روز یک نوبت. Future در خود WP تنها برای درس بررسی‌شده و با URL متمایز.

## پیشنهاد ۴۰ قسمت در ۱۰ فصل

| جلسه | فصل | موضوع | منبع ۲۴ درس قبلی | تمرکز تخصصی | نوبت پیشنهادی UTC |
|---:|---:|---|---|---|---|
| 1 | 1 | آشنایی با MTCNA، RouterOS و RouterBOARD | 01 | هدف دوره، پیش‌نیاز، تمایز CHR | 2026-11-07 05:30 |
| 2 | 1 | ساخت لابراتوار ایزوله CHR و کنترل NIC | 01 | نصب، network isolation، نسخه، rollback | 2026-11-10 05:30 |
| 3 | 1 | اولین اتصال WinBox؛ MAC در برابر IP | 02 | دسترسی دوم، شناسایی و آزمون | 2026-11-13 05:30 |
| 4 | 1 | WebFig و Quick Set؛ راه‌اندازی اولیه امن | 02+new | انتخاب Quick Set بر اساس مدل و حفاظت از دسترسی | 2026-11-16 05:30 |
| 5 | 1 | CLI، Command History و Safe Mode | 03 | print/find/add/set، راهنمای shell و rollback | 2026-11-19 05:30 |
| 6 | 1 | کانفیگ پیش‌فرض، کاربران و سرویس‌های مدیریتی | 04 | identity، security و SSH/WebFig | 2026-11-22 05:30 |
| 7 | 1 | Backup، Export، Restore بدون از دست‌رفتن دسترسی | 05 | binary/text و restore در lab | 2026-11-25 05:30 |
| 8 | 1 | Reset، Netinstall و license؛ سناریوی نجات | new | حدود نرم‌افزار و سخت‌افزار، license | 2026-11-28 05:30 |
| 9 | 1 | بسته‌ها، ارتقا RouterOS و RouterBOOT | 06 | channel، package، firmware، staged update | 2026-12-01 05:30 |
| 10 | 2 | IPv4، Subnet و Gateway به زبان عملی | 07 | محاسبه و آزمایش /24 و /30 | 2026-12-04 05:30 |
| 11 | 2 | DHCP Client روی WAN و دریافت Gateway/DNS | 08 | تنظیمات، default-route و DNS | 2026-12-07 05:30 |
| 12 | 2 | DHCP Server، Pool، Network، Lease | 08 | ساخت سرور و تحلیل خطاها | 2026-12-10 05:30 |
| 13 | 2 | DNS و ARP Modes و عیب‌یابی شبکه LAN | 09 | ARP table، modes و DNS cache | 2026-12-13 05:30 |
| 14 | 3 | Bridge، Port، RSTP و مقابله با Loop | 10 | پورت‌ها، bridge و topology | 2026-12-16 05:30 |
| 15 | 3 | Bridging Wireless و Station Bridge | new | مرز L2، RF compatibility | 2026-12-19 05:30 |
| 16 | 4 | Route Flags، Static Route و Default Route | 11 | route table، distance و gateway | 2026-12-22 05:30 |
| 17 | 4 | دو شبکه LAN و مسیر برگشت | 12 | دو روتر و return route | 2026-12-25 05:30 |
| 18 | 4 | شناخت مسیرهای Dynamic در RouterOS | new | connected، flags؛ تمایز از OSPF پیشرفته | 2026-12-28 05:30 |
| 19 | 5 | Source NAT و Masquerade | 13 | src-nat، WAN، NAT | 2026-12-31 05:30 |
| 20 | 5 | Destination NAT، Redirect و CGNAT | 14 | dstnat و firewall | 2027-01-03 05:30 |
| 21 | 5 | Connection Tracking، Input و Forward | 15 | state و chains | 2027-01-06 05:30 |
| 22 | 5 | Firewall Filter Order و Address List | 16 |  ترتیب و counters | 2027-01-09 05:30 |
| 23 | 5 | سناریوی محافظت از روتر با Log و Rollback | new | input/forward و حفظ مسیر مدیریت | 2027-01-12 05:30 |
| 24 | 6 | WiFi در RouterOS7؛ Package، Band و Channel | 17 | wifi/wireless، محدودیت مدل، قوانین کشور | 2027-01-15 05:30 |
| 25 | 6 | راه‌اندازی Access Point و Station امن | 18 | SSID، WPA2/WPA3، آزمون RF | 2027-01-18 05:30 |
| 26 | 6 | Access List، Connect List، Registration و Snooper | new | کنترل دسترسی و مانیتورینگ سیگنال | 2027-01-21 05:30 |
| 27 | 7 | Simple Queue و اندازه‌گیری سرعت | 19 | target و fasttrack | 2027-01-24 05:30 |
| 28 | 7 | PCQ و تقسیم منصفانه پهنای باند | 20 | pcq rate/limit/classifier | 2027-01-27 05:30 |
| 29 | 7 | Limit-at، Burst و FastTrack | 20 | burst و queue counters | 2027-01-30 05:30 |
| 30 | 8 | PPP Profile، Secret، Pool | 21 | IP pool و احراز هویت | 2027-02-02 05:30 |
| 31 | 8 | PPPoE Client و Server آزمایشگاهی | 21 | session، service-name و MTU | 2027-02-05 05:30 |
| 32 | 8 | PPTP و SSTP؛ کاربرد تاریخی و خطرات | 22 | legacy و security caveats | 2027-02-08 05:30 |
| 33 | 8 | WireGuard Site-to-Site تحت اختیار | 22 | peer/Allowed Address و route | 2027-02-11 05:30 |
| 34 | 9 | Ping، Traceroute، Torch و Log | 23 | تشخیص از لایه فیزیکی تا TCP/IP | 2027-02-14 05:30 |
| 35 | 9 | Netwatch، SNMP، Graphs و CPU Profiler | new | monitoring، metrics، secret hygiene | 2027-02-17 05:30 |
| 36 | 9 | supout.rif، The Dude و مستندات فنی | new | support diagnostics و privacy | 2027-02-20 05:30 |
| 37 | 10 | پروژه نهایی ۱؛ Bridge، IP، DHCP | 24 | طرح، لایه دو و آدرس | 2027-02-23 05:30 |
| 38 | 10 | پروژه نهایی ۲؛ Routing، Firewall، NAT | 24 | route، policy و SNAT | 2027-02-26 05:30 |
| 39 | 10 | پروژه نهایی ۳؛ Queue، Troubleshooting، Rollback | 24 | آزمون خرابی و بازیابی | 2027-03-01 05:30 |
| 40 | 10 | جمع‌بندی عملی و سوالات مفهومی MTCNA | new | آزمون غیررسمی و نقشه راه بعدی | 2027-03-04 05:30 |

## موارد جاافتاده و منابع

سرفصل قابل تطبیق: Quick Set، Netinstall، licensing، ARP modes، station bridge، route flags/dynamic routes، Access/Connect list، Snooper/Registration، redirect/FastTrack، PCQ/limit-at، SSTP، Netwatch/SNMP/Profiler/Graphs/The Dude و supout.rif. در موارد وابسته به سخت‌افزار باید برچسب شود که CHR به‌تنهایی کافی نیست.

- https://mikrotik.com/training/about
- https://i.mt.lv/cdn/training_pdf/mtcna_outline_2019181161836.pdf (فایل رسمی دارای تاریخ ویرایش ۲۰۱۶)
- https://manual.mikrotik.com/docs/introduction/
- https://make.wordpress.org/support/user-manual/pages/schedule-a-page/

## مراحل باقی مانده تا ادعای آماده و Scheduled

۱. تبدیل ۲۴ منبع فعلی به ۴۰ متن کامل و متمایز، افزودن بخش‌های فاقد درس و کنترل مدت واقعی از روی تمرین ضبط‌شده.
۲. انتشار صرفاً نسخه پیش‌نویس کامل در WP و readback تمام محتوا؛ هر صفحه parent=40 و بدون ایجاد URL عمومی تکراری.
۳. لاب واقعی، اسکرین‌شات‌های اصیل و تأیید فنی برای هر جلسه؛ اجرای موارد WiFi و RouterBOOT تنها با دستگاه سازگار.
۴. تصمیم content owner: درس متمایز -> URL ویژه؛ درس هم‌پوشان -> افزودن بخش به صفحه موجود بدون انتشار صفحه تکراری.
۵. پس از تأیید برای عنوان مستقل، ثبت status=future و date در WP و readback. برای اصلاح منتشرشده از automation کنترل‌شده استفاده شود؛ منتشرشده به future تبدیل نشود.
۶. تأیید WordPress Cron و مراقبت از Missed Schedule؛ کنترل‌کننده قدیمی نباید درس را دوبار منتشر کند.

**حقیقت این checkpoint:** ۲۴ پیش‌نویس موجود هنوز Draft و ۴۰ جلسه صرفاً طرح بازآرایی است. زمان‌بندی Native WP هنوز اجرا نشده و هیچ ادعای آزمایش واقعی وجود ندارد.
