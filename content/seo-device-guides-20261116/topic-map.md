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
| S5 | آموزشی | کارشناس شبکه | /guides/switch-uplink-trunk/ | /services/network-setup-tehran/ | انتخاب uplink (GbE/2.5G/SFP+)، ترانک تگ‌دار، محدودیت پهنای‌باند | «بین سوئیچ‌ها چه uplink‌ای بگذارم؟» | سند MikroTik + صفحات محصول | طراحی توپولوژی |
| S6 | آموزشی | مدیر IT/خریدار | /guides/switch-psu-power/ | /services/network-setup-tehran/ | PSU پیوست/جدا (نمونهٔ سندشده: netPower 16P بدون PSU)، ظرفیت PSU نسبت به بودجهٔ PoE | «آداپتور/PSU سوئیچ کافی است؟» | صفحات رسمی محصول | طراحی برق و اجرا |

## خوشهٔ ج: پشتیبانی، مانیتورینگ و قرارداد خدمات

| id | intent | مخاطب | URL هدف | صفحهٔ مادر | زیرموضوع | سؤال مشتری | منبع لازم | خدمت مرتبط |
|---|---|---|---|---|---|---|---|---|
| N1 | عیب‌یابی | کاربر/مدیر شبکه | /guides/network-troubleshooting/ | /services/network-support-tehran/ | مسیر تشخیص، ابزارها، جدول عیب‌یابی | «شبکه قطع است، از کجا شروع کنم؟» | تجربهٔ فنی | پشتیبانی شبکه |
| N2 | آموزشی | مدیر IT | /guides/network-monitoring/ | /services/network-support-tehran/ | معیارها، ابزارها، هشدارها | «شبکه را چطور مانیتور کنم؟» | تجربهٔ فنی | پشتیبانی دوره‌ای |
| N3 | تصمیم/قرارداد | مدیر کسب‌وکار | /guides/support-contract-questions/ (پیشنهادی — جایگزین slug مردهٔ 404) | /services/network-support-tehran/ | محدوده، مسئول تأیید، SLA | «قرارداد پشتیبانی چه چیزهایی را روشن کند؟» | تجربهٔ فنی | قرارداد پشتیبانی |
| N4 | آموزشی/چک‌لیست | کارشناس/مدیر شبکه | /guides/network-delivery-acceptance/ | /services/network-setup-tehran/ | تست‌های مثبت/منفی پذیرش، ثبت قبل/بعد، مستندسازی تحویل | «چطور تحویل شبکه را بپذیرم؟» | تجربهٔ فنی + الگوی درس‌های M2/M3 | راه‌اندازی شبکه |
| N5 | آموزشی | کارشناس شبکه | /guides/mikrotik-config-backup/ | /services/network-support-tehran/ | تفاوت backup و export، آزمون بازیابی، زمان‌بندی نگهداری | «از کانفیگ میکروتیک بکاپ بگیرم؟» | سند RouterOS | پشتیبانی دوره‌ای |
| N6 | آموزشی/فرایند | مدیر کسب‌وکار | /guides/network-incident-path/ | /services/network-support-tehran/ | تشدید، ثبت رخداد، اثر اختلال و استثناهای اینترنت/تأمین قطعه | «وقت قطعی چه مسیری طی می‌شود؟» | تجربهٔ فنی | پشتیبانی شبکه |

## لینک‌های داخلی

| source | target | anchor | محل درج | دلیل ارتباط |
|---|---|---|---|---|
| /services/mikrotik-tehran/ | /guides/mikrotik-routers/ | راهنمای انتخاب روتر میکروتیک | انتهای بخش خدمات | کاربر برای انتخاب مدل به راهنما نیاز دارد |
| /services/network-setup-tehran/ | /guides/mikrotik-switches-crs/ | راهنمای انتخاب سوئیچ CRS | انتهای بخش تجهیزات | کاربر برای انتخاب سوئیچ به راهنما نیاز دارد |
| /services/network-support-tehran/ | /network-support-contract-guide/ | راهنمای قرارداد پشتیبانی | بخش قرارداد | **BLOCKED 2026-11-16: مقصد 404 شده (دیسکاوری) — تا تصمیم مالک دربارهٔ بازتولید/ریدایرکت، این ردیف اعمال نشود** |
| /services/remote-support/ | /services/mikrotik-tehran/ | خدمات میکروتیک | بخش خدمات مرتبط | کاربر ریموت برای MikroTik نیاز به پشتیبانی دارد |

## وضعیت اجرا (به‌روزرسانی 2026-11-17 — صادقانه)

**همهٔ ۱۸ واحد Masterplan ‏(M1-M6، ‏S1-S6، ‏N1-N6) اکنون authored شده‌اند** — هرکدام DRAFT با pipeline کامل ‏(MD+SVG+HTML+validator+رندر+رسید):

- M1: مقالهٔ موجود (articles/mikrotik-routers.fa.md) — READY_FOR_REVIEW
- S1: مقالهٔ موجود (articles/mikrotik-switches-crs.fa.md) — READY_FOR_REVIEW (خروجی HTML همگام شد)
- M2/M3: بازنگری سوم (طبق MANAGER_REVIEW 6926700769) — REVIEW_REQUEST (RR 6927129500)
- M4/M5/M6: authored این نوبت‌ها — REVIEW_REQUEST (M4 در RR 6928866485؛ ‏M5 در RR 6929152100؛ ‏M6 در RR 6929419821)
- S2: بودجهٔ PoE — REVIEW_REQUEST (RR 6927296031) · ‏S3: ماژول‌ها — REVIEW_REQUEST (RR 6927493389)
- S5 آپ‌لینک/ترانک و ‏S6 برق/PSU: authored — REVIEW_REQUEST (RR 6929623471 و بخش در RRهای بعدی)
- N1 عیب‌یابی، ‏N2 مانیتورینگ، ‏N3 قرارداد/SLA، ‏N4 پذیرش، ‏N5 بکاپ، ‏N6 مسیر رخداد: authored — REVIEW_REQUEST (RRهای 6927622932 تا 6929900858)
- S4 (طراحی VLAN سوئیچ): هم‌پوشان با M2 — تصمیم ادغام/جداسازی با مرور مدیر (فقط ردیف topic-map، درس مستقل authored نشده)
- N3: slug واقعی پیشنهادی (راهنمای قبلی 404 شده — دیسکاوری)؛ ردیف لینک قرارداد BLOCKED تا تصمیم مالک
- لینک‌های داخلی: ردیف‌های مقصدهای زنده معتبر؛ ردیف قرارداد BLOCKED — بدون تصمیم مالک اعمال نشود
- بقیهٔ بسته‌ها (دیسکاوری، گارد/Masterplan، نقشهٔ لینک، کاندیدها): در صف مرور مدیر

## ملاحظات

- هر آموزش: متن کامل + نمودار/تصویر + تمرین/آزمون + منابع + لینک/CTA مرتبط
- URLهای پیشنهادی (/guides/...) URLهای منتشرشده نیستند و انتشارشان مستلزم گیت است
- هیچ مشتری، تجربه، پروژه، نتیجه یا آمار ساختگی اضافه نشده
- Word count و تعداد مقاله معیار اعتبار موضوعی نیستند؛ پوشش intent و عمق فنی ملاک است
