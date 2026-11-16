# Topic Map — TN-TEHNET-SEARCH-LEARNING-REVENUE-V2

> سه خوشهٔ محتوایی مرتبط با خدمات واقعی TehNet؛ هر خوشه شامل intent، مخاطب، URL مقصد، زیرموضوع، سؤال مشتری، منبع و خدمت مرتبط.

## خوشهٔ الف: MikroTik و مسیریابی

| id | intent | مخاطب | URL هدف | صفحهٔ مادر | زیرموضوع | سؤال مشتری | منبع لازم | خدمت مرتبط |
|---|---|---|---|---|---|---|---|---|
| M1 | مقایسه/انتخاب | مدیر IT | /guides/mikrotik-routers/ | /services/mikrotik-tehran/ | جدول مدل/نسخه، انتخاب دفتر/VPN/ارتقا | «کدام روتر میکروتیک برای شرکت من؟» | router-catalog.csv | کانفیگ و پشتیبانی میکروتیک |
| M2 | آموزشی | کارشناس شبکه | /guides/mikrotik-vlan/ | /services/mikrotik-tehran/ | VLAN access/trunk، جدول پورت/VLAN | «چطور VLAN راه‌اندازی کنم؟» | سند RouterOS | کانفیگ VLAN |
| M3 | آموزشی/عیب‌یابی | کارشناس/مدیر IT | /guides/mikrotik-dhcp-dns/ | /services/mikrotik-tehran/ | DHCP lease، DNS static/forwarder، عیب‌یابی | «چرا DHCP کار نمی‌کند؟» | سند RouterOS | عیب‌یابی DHCP/DNS |
| M4 | آموزشی پیشرفته | کارشناس ارشد | /guides/mikrotik-l3hw/ | /services/mikrotik-tehran/ | L3HW vs CPU routing، محدودیت مدل/نسخه | «L3HW روی CRS326 چطور است؟» | help.mikrotik.com | طراحی L3 شبکه |
| M5 | آموزشی/انتخاب | مدیر IT | /guides/mikrotik-vpn/ | /services/mikrotik-tehran/ | IPsec/WireGuard/OVPN، diagram معماری | «کدام VPN برای شعبه؟» | سند RouterOS | کانفیگ VPN شعبه |
| M6 | آموزشی | مدیر شبکه | /guides/mikrotik-dual-wan/ | /services/mikrotik-tehran/ | failover، load-balance، نمودار قطع لینک | «چطور دو اینترنت را failover کنم؟» | سند RouterOS | کانفیگ dual-WAN |

## خوشهٔ ب: طراحی و اجرای شبکه، switching و PoE

| id | intent | مخاطب | URL هدف | صفحهٔ مادر | زیرموضوع | سؤال مشتری | منبع لازم | خدمت مرتبط |
|---|---|---|---|---|---|---|---|---|
| S1 | مقایسه/انتخاب | مدیر IT/خریدار | /guides/mikrotik-switches-crs/ | /services/network-setup-tehran/ | CSS/CRS/RouterOS/SwOS، PoE، L2/L3HW | «کدام سوئیچ میکروتیک برای شرکت؟» | switch-catalog.csv | طراحی و اجرای شبکه |
| S2 | آموزشی | کارشناس شبکه | /guides/switch-poe-budget/ | /services/network-setup-tehran/ | PoE af/at/پسیو، بودجهٔ توان، PSU | «چقدر PoE مصرف می‌کند؟» | سند MikroTik | طراحی PoE |
| S3 | آموزشی | کارشناس شبکه | /guides/sfp-sfp-plus-guide/ | /services/network-setup-tehran/ | ماژول نوری، تک/دو-موج، سرعت، سازگاری | «کدام ماژول SFP بخرم؟» | سند سازنده | اجرای فیبر |
| S4 | آموزشی | کارشناس شبکه | /guides/switch-vlan-design/ | /services/network-setup-tehran/ | access/trunk، جدول پورت/VLAN، امنیت | «چطور VLAN طراحی کنم؟» | سند RouterOS | کانفیگ VLAN |

## خوشهٔ ج: پشتیبانی، مانیتورینگ و قرارداد خدمات

| id | intent | مخاطب | URL هدف | صفحهٔ مادر | زیرموضوع | سؤال مشتری | منبع لازم | خدمت مرتبط |
|---|---|---|---|---|---|---|---|---|
| N1 | عیب‌یابی | کاربر/مدیر شبکه | /guides/network-troubleshooting/ | /services/network-support-tehran/ | مسیر تشخیص، ابزارها، جدول عیب‌یابی | «شبکه قطع است، از کجا شروع کنم؟» | تجربهٔ فنی | پشتیبانی شبکه |
| N2 | آموزشی | مدیر IT | /guides/network-monitoring/ | /services/network-support-tehran/ | معیارها، ابزارها، هشدارها | «شبکه را چطور مانیتور کنم؟» | تجربهٔ فنی | پشتیبانی دوره‌ای |
| N3 | تصمیم/قرارداد | مدیر کسب‌وکار | /network-support-contract-guide/ | /services/network-support-tehran/ | محدوده، مسئول تأیید، SLA | «قرارداد پشتیبانی چه چیزهایی را روشن کند؟» | تجربهٔ فنی | قرارداد پشتیبانی |

## لینک‌های داخلی

| source | target | anchor | محل درج | دلیل ارتباط |
|---|---|---|---|---|
| /services/mikrotik-tehran/ | /guides/mikrotik-routers/ | راهنمای انتخاب روتر میکروتیک | انتهای بخش خدمات | کاربر برای انتخاب مدل به راهنما نیاز دارد |
| /services/network-setup-tehran/ | /guides/mikrotik-switches-crs/ | راهنمای انتخاب سوئیچ CRS | انتهای بخش تجهیزات | کاربر برای انتخاب سوئیچ به راهنما نیاز دارد |
| /services/network-support-tehran/ | /network-support-contract-guide/ | راهنمای قرارداد پشتیبانی | بخش قرارداد | کاربر برای تصمیم قرارداد به راهنما نیاز دارد |
| /services/remote-support/ | /services/mikrotik-tehran/ | خدمات میکروتیک | بخش خدمات مرتبط | کاربر ریموت برای MikroTik نیاز به پشتیبانی دارد |

## وضعیت اجرا

- M1: مقالهٔ موجود (articles/mikrotik-routers.fa.md) — READY_FOR_REVIEW
- S1: مقالهٔ موجود (articles/mikrotik-switches-crs.fa.md) — READY_FOR_REVIEW
- M2–M6, S2–S6, N1–N6: آموزش‌های READY — تولید در نوبت بعدی
- لینک‌های داخلی: لینک‌های موجود در مقاله‌ها + patches سه صفحهٔ خدمات (page-edits/*.proposed.html) — آماده اعمال

## ملاحظات

- هر آموزش: متن کامل + نمودار/تصویر + تمرین/آزمون + منابع + لینک/CTA مرتبط
- URLهای پیشنهادی (/guides/...) URLهای منتشرشده نیستند و انتشارشان مستلزم گیت است
- هیچ مشتری، تجربه، پروژه، نتیجه یا آمار ساختگی اضافه نشده
- Word count و تعداد مقاله معیار اعتبار موضوعی نیستند؛ پوشش intent و عمق فنی ملاک است
