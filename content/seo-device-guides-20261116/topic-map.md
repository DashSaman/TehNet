# Topic Map — TN-TEHNET-SEARCH-LEARNING-REVENUE-V2

> سه خوشهٔ محتوایی مرتبط با خدمات واقعی TehNet؛ هر خوشه شامل intent، مخاطب، URL مقصد، زیرموضوع، سؤال مشتری، منبع و خدمت مرتبط.
> **هم‌سازمان با سرفصل مصوب Mission V2 (MANAGER_FLOW_V2):** شماره‌گذاری N1-N6 همان سرفصل مصوب است ‏(N1 طراحی دفتر، ‏N2 رک/کابل، ‏N3 گزارش تست کابل، ‏N4 عیب‌یابی، ‏N5 مانیتورینگ، ‏N6 انتخاب پشتیبانی)؛ درس‌های مکمل ‏(supplementary) جدا و با برچسب «مکمل» فهرست می‌شوند. وضعیت اجرا در انتهای همین فایل و ledger اجرایی در `WORKQUEUE.md` (ریپو) نگه‌داری می‌شود.

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
| S4 | آموزشی | کارشناس شبکه | /guides/switch-vlan-l2/ ‏(پیشنهادی — سرفصل مصوب، تصمیم تفکیک مدیر 6935206213) | /services/network-setup-tehran/ | **مصوب: VLAN روی سوئیچ، لایه۲ ‏(CRS326): access/pvid، جدول VLAN، ترانک تگ‌دار، مسیر CPU، احراز آفلود، مرز لایه۲/۳** | «VLAN روی سوئیچ چطور اجرا می‌شود؟» | سند RouterOS + صفحهٔ رسمی محصول | کانفیگ VLAN |
| S5 | آموزشی | کارشناس شبکه | /guides/switch-loop-rstp-lacp/ ‏(پیشنهادی — سرفصل مصوب) | /services/network-setup-tehran/ | **مصوب: حلقهٔ تصادفی، RSTP، باند LACP** | «حلقهٔ شبکه چطور شکل می‌گیرد و چطور بسته می‌شود؟» | سند MikroTik + صفحات محصول | طراحی توپولوژی |
| S6 | آموزشی | مدیر IT/خریدار | /guides/switch-nas-server-upgrade/ ‏(پیشنهادی — سرفصل مصوب) | /services/network-setup-tehran/ | **مصوب: ارتقای NAS/سرور به ‏2.5G/10G ‏(CRS309، DAC، NIC سرور)** | «اتصال NAS/سرور را چطور ارتقا بدهم؟» | صفحات رسمی محصول | طراحی برق و اجرا |
| S5-مکمل | آموزشی | کارشناس شبکه | /guides/switch-uplink-trunk/ ‏(پیشنهادی) | /services/network-setup-tehran/ | مکمل: انتخاب uplink ‏(GbE/SFP)، ترانک تگ‌دار، محدودیت پهنای‌باند ‏(CRS112/CRS326) | «بین سوئیچ‌ها چه uplink‌ای بگذارم؟» | سند MikroTik + صفحات محصول | طراحی توپولوژی |
| S6-مکمل | آموزشی | مدیر IT/خریدار | /guides/switch-psu-power/ ‏(پیشنهادی) | /services/network-setup-tehran/ | مکمل: PSU پیوست/جدا ‏(نمونهٔ سندشده: netPower 16P بدون PSU)، ظرفیت PSU نسبت به بودجهٔ PoE | «آداپتور/PSU سوئیچ کافی است؟» | صفحات رسمی محصول | طراحی برق و اجرا |

## خوشهٔ ج: پشتیبانی، مانیتورینگ و قرارداد خدمات — شماره‌گذاری مصوب

| id | intent | مخاطب | URL هدف | صفحهٔ مادر | زیرموضوع | سؤال مشتری | منبع لازم | خدمت مرتبط |
|---|---|---|---|---|---|---|---|---|
| N1 | آموزشی/طراحی | مدیر IT | /guides/office-network-design/ ‏(پیشنهادی — سرفصل مصوب) | /services/network-setup-tehran/ | **مصوب: طراحی شبکهٔ دفتر — نیازسنجی تا نقشهٔ نهایی** | «شبکهٔ دفتر را چطور طراحی کنم؟» | تجربهٔ فنی + سند RouterOS | راه‌اندازی شبکه |
| N2 | آموزشی | کارشناس شبکه | /guides/rack-cabling-standard/ ‏(پیشنهادی — سرفصل مصوب) | /services/network-setup-tehran/ | **مصوب: رک و کابل‌کشی — چیدمان، برچسب‌گذاری، استاندارد** | «رک و کابل‌کشی استاندارد چه چیزی دارد؟» | تجربهٔ فنی | راه‌اندازی شبکه |
| N3 | آموزشی/کنترل کیفی | کارشناس شبکه | /guides/cable-certification-report/ ‏(پیشنهادی — سرفصل مصوب) | /services/network-setup-tehran/ | **مصوب: گزارش تست کابل — پنج معیار، ابزار، قالب گزارش** | «تست کابل قابل‌استناد چه شکلی است؟» | TIA/EIA-568.2-D ‏(مرجع عمومی) | راه‌اندازی شبکه |
| N4 | عیب‌یابی | کاربر/مدیر شبکه | /guides/network-troubleshooting/ | /services/network-support-tehran/ | **مصوب: مسیر تشخیص، ابزارها، جدول عیب‌یابی** | «شبکه قطع است، از کجا شروع کنم؟» | تجربهٔ فنی | پشتیبانی شبکه |
| N5 | آموزشی | مدیر IT | /guides/network-monitoring/ | /services/network-support-tehran/ | **مصوب: معیارها، ابزارها، هشدارها** | «شبکه را چطور مانیتور کنم؟» | تجربهٔ فنی | پشتیبانی دوره‌ای |
| N6 | تصمیم/انتخاب | مدیر کسب‌وکار | /guides/network-support-selection/ ‏(پیشنهادی — مسیر مصوب تصمیم مدیر 6938667416) | /services/network-support-tehran/ | **مصوب: انتخاب پشتیبانی — نیازسنجی تا بازنگری دوره‌ای** | «کدام ساختار پشتیبانی برای سازمان من مناسب است؟» | تجربهٔ فنی | قرارداد پشتیبانی |

| N-مکمل: قرارداد/SLA | تصمیم/قرارداد | مدیر کسب‌وکار | /guides/support-contract-questions/ ‏(پیشنهادی — جایگزین slug مردهٔ 404) | /services/network-support-tehran/ | مکمل: سؤالات کلیدی قرارداد و SLA سنجش‌پذیر | «قرارداد پشتیبانی چه چیزهایی را روشن کند؟» | تجربهٔ فنی | قرارداد پشتیبانی |
| N-مکمل: پذیرش تحویل | آموزشی/چک‌لیست | کارشناس/مدیر شبکه | /guides/network-delivery-acceptance/ ‏(پیشنهادی) | /services/network-setup-tehran/ | مکمل: تست‌های مثبت/منفی پذیرش، ثبت قبل/بعد، مستندسازی تحویل | «چطور تحویل شبکه را بپذیرم؟» | تجربهٔ فنی + الگوی درس‌های M2/M3 | راه‌اندازی شبکه |
| N-مکمل: بکاپ/export | آموزشی | کارشناس شبکه | /guides/mikrotik-config-backup/ ‏(پیشنهادی) | /services/network-support-tehran/ | مکمل: تفاوت backup و export، آزمون بازیابی، زمان‌بندی نگهداری | «از کانفیگ میکروتیک بکاپ بگیرم؟» | سند RouterOS | پشتیبانی دوره‌ای |
| N-مکمل: مسیر رخداد | آموزشی/فرایند | مدیر کسب‌وکار | /guides/network-incident-path/ ‏(پیشنهادی) | /services/network-support-tehran/ | مکمل: تشدید، ثبت رخداد، اثر اختلال و استثناهای اینترنت/تأمین قطعه | «وقت قطعی چه مسیری طی می‌شود؟» | تجربهٔ فنی | پشتیبانی شبکه |

## لینک‌های داخلی

| source | target | anchor | محل درج | دلیل ارتباط |
|---|---|---|---|---|
| /services/mikrotik-tehran/ | /guides/mikrotik-routers/ | راهنمای انتخاب روتر میکروتیک | انتهای بخش خدمات | کاربر برای انتخاب مدل به راهنما نیاز دارد |
| /services/network-setup-tehran/ | /guides/mikrotik-switches-crs/ | راهنمای انتخاب سوئیچ CRS | انتهای بخش تجهیزات | کاربر برای انتخاب سوئیچ به راهنما نیاز دارد |
| /services/network-support-tehran/ | /network-support-contract-guide/ | راهنمای قرارداد پشتیبانی | بخش قرارداد | **BLOCKED 2026-11-16: مقصد 404 شده (دیسکاوری) — تا تصمیم مالک دربارهٔ بازتولید/ریدایرکت، این ردیف اعمال نشود** |
| /services/remote-support/ | /services/mikrotik-tehran/ | خدمات میکروتیک | بخش خدمات مرتبط | کاربر ریموت برای MikroTik نیاز به پشتیبانی دارد |

## وضعیت اجرا (هم‌سازی‌شده با سرفصل مصوب Mission V2 — به‌روزرسانی 2026-11-17، صادقانه)

**ادعای قبلی «همهٔ ۱۸ واحد authored شده‌اند» پس گرفته می‌شود.** وضعیت دقیق به تفکیک سرفصل مصوب:

| سرفصل مصوب | وضعیت | artifact |
|---|---|---|
| M1-M6 | authored ‏(DRAFT — در صف مرور) | مقالهٔ روتر + درس‌های M2-M6 |
| S1-S3 | authored ‏(DRAFT — در صف مرور) | مقالهٔ سوئیچ + درس‌های S2/S3 |
| S4 ‏(VLAN روی سوئیچ، لایه۲) | authored ‏(DRAFT): tutorials/s4-vlan-switch-l2.fa.md — طبق تصمیم تفکیک مدیر | مقایسه: M2 مسیر روتر، M4 inter-VLAN |
| S5 ‏(loop/RSTP/LACP) | authored ‏(DRAFT) | tutorials/s5-loop-rstp-lacp.fa.md |
| S6 ‏(ارتقای NAS/سرور) | authored ‏(DRAFT) | tutorials/s6-nas-server-upgrade.fa.md |
| N1 ‏(طراحی دفتر) | authored ‏(DRAFT) | tutorials/n1-office-design.fa.md |
| N2 ‏(رک/کابل) | authored ‏(DRAFT) | tutorials/n2-rack-cable.fa.md |
| N3 ‏(گزارش تست کابل) | authored ‏(DRAFT) | tutorials/n3-cable-test-report.fa.md |
| N4 ‏(عیب‌یابی) | پوشش‌شده: درس n1-network-troubleshooting.fa.md ‏(نام فایل ≠ شناسه مصوب) | همان |
| N5 ‏(مانیتورینگ) | پوشش‌شده: درس n2-monitoring-maintenance.fa.md | همان |
| N6 ‏(انتخاب پشتیبانی) | authored ‏(DRAFT): tutorials/n6-support-selection.fa.md | مکمل قرارداد/SLA جدا حفظ شده |

- **درس‌های مکمل حفظ شده‌اند** ‏(supplementary، جدا از سرفصل مصوب): uplink/trunk ‏(s5-uplink-trunk)، PSU ‏(s6-psu-power)، عیب‌یابی/مانیتورینگ/قرارداد با فایل‌های فعلی‌شان، پذیرش تحویل ‏(n4-delivery-acceptance)، بکاپ ‏(n5-config-backup-export)، مسیر رخداد ‏(n6-incident-path).
- **حالت‌ها جدا هستند:** authored ‏≠ ‏test-qualified ‏≠ ‏accepted ‏≠ ‏published. هیچ درسی منتشر نشده؛ publish مستلزم گیت است.
- ledger اجرایی با وضعیت لحظه‌ای: `WORKQUEUE.md` در ریپو — هر بسته با SHA و رسید خودش.
- نگاشت RRهای درس‌های canonical ‏(از ledger مدیریت): combined fourth revision = ‏6930620309؛ canonical loop/RSTP/LACP = ‏6930807455؛ canonical NAS upgrade = ‏6931021926؛ canonical office design = ‏6931198087 — این RRها «تحویل» را تأیید می‌کنند، نه پذیرش محتوایی.
- سرفصل مصوب ۱۸/۱۸ authored/پوشش‌شده شد ‏(S4 با تصمیم تفکیک مدیر). بقیهٔ بسته‌ها ‏(دیسکاوری، گارد، کاندیدها، رندر، درس‌های authored): در صف مرور مدیر.

## ملاحظات

- هر آموزش: متن کامل + نمودار/تصویر + تمرین/آزمون + منابع + لینک/CTA مرتبط
- URLهای پیشنهادی (/guides/...) URLهای منتشرشده نیستند و انتشارشان مستلزم گیت است
- هیچ مشتری، تجربه، پروژه، نتیجه یا آمار ساختگی اضافه نشده
- Word count و تعداد مقاله معیار اعتبار موضوعی نیستند؛ پوشش intent و عمق فنی ملاک است
