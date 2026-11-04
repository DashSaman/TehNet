# استاندارد ۴۰ قسمت — اسکرین‌شات واقعی WinBox / RouterOS برای تهنت

**نسخهٔ مستند:** ۲۰۲۶-۱۱-۰۴. وضعیت: مشخصات اجرایی و فهرست شات‌ها؛ نه ادعای ۱۶۰ تصویر تولیدشده.

## قرارداد غیرقابل مذاکره

هر قسمت حداقل چهار شات حقیقی بگیرد: (۱) نمای منو/شروع از WinBox، (۲) پیمایش دقیق تا پنجرهٔ مربوط، (۳) فرم با فیلدهای آزمایشی پرشده قبل از Apply، (۴) نتیجهٔ واقعی و قابل تأیید بعد از Apply و Undo؛ اگر درس ماهیت خواندنی دارد، شات سوم پنل/دستور read-only واقعی باشد. اسکرین‌شات از نرم‌افزار واقعاً اجراشده باشد، نه SVG، UI بازسازی‌شده، تصویر ساختگی یا عکس قدیمی بدون تأیید نسخه.

هر تصویر PNG/WebP با نسخهٔ صریح WinBox و RouterOS، تاریخ تست، شناسهٔ لاب، آدرس/بازهٔ آزمایشی، منو، فیلدها، Alt فارسی، توضیح زیر تصویر و لینک منبع به صفحهٔ مربوط ذخیره شود. هیچ رمز، توکن، کلید خصوصی، IP عمومی مشتری یا دادهٔ محرمانه در عکس دیده نشود؛ به‌جای انتشار اطلاعات و بعد محوکردن، از قبل از دادهٔ صرفاً آزمایشی استفاده شود.

CHR به‌تنهایی برای رادیو، RouterBOOT و Netinstall واقعی کافی نیست. دستگاه فیزیکی سازگار و مجوز لازم پیش‌نیاز شات‌های سخت‌افزاری است. در صورت نبود سخت‌افزار، در آن جلسه صریحاً NOT_CAPTURED بزنید.

WPVibe در ۴ نوامبر به محدودیت استفاده رسید: هیچ محتوای تازه‌ای از این استاندارد به WordPress ارسال نشده است. تا قبل از بازگشت REST، فقط فایل مخزن را آماده کنید و وضعیت Draft/Noindex/Canonical اصلی را حفظ کنید.

## تصاویر واقعی موجود در همین checkpoint

- [WinBox 4.5: پنجرهٔ واقعی اتصال](screenshots/real-lab/2026-11-04/01-winbox-login-cropped.png) — CHR هنوز Login نشده در این لحظه.
- [WinBox 4.5: اولین ورود واقعی و الزام تغییر رمز](screenshots/real-lab/2026-11-04/02-winbox-first-login-password-required-cropped.png) — تأیید Auth و RouterOS 7.25.1، **نه** تکمیل Password Change یا منوهای دیگر.
- [متادیتای لاب و تأیید صداقت تصاویر](screenshots/real-lab/2026-11-04/capture-metadata.json)

## ماتریس چهار شات پایه برای همهٔ قسمت‌ها

| جلسه | موضوع | شات ۱: شروع و مسیر منو | شات ۲: پنل مقصد | شات ۳: فیلدهای واقعی لاب | شات ۴: نتیجهٔ واقعی | وضعیت |
|---:|---|---|---|---|---|
| 1 | مقدمه و ابزارها | WinBox / System → Resources | System → Resources | نسخه، معماری و نوع RouterBOARD/CHR فقط خواندنی | Version/architecture و نمای اصلی WinBox | NOT_CAPTURED |
| 2 | ساخت CHR ایزوله | WinBox / Interfaces | Interfaces؛ IP → Addresses | نشان‌دادن NIC/Bridge مجازی و IP 10.77.10.1/24 روی LAB-LAN پس از بررسی عدم تکرار | ترتیب NIC و IP واقعی کنسول/WinBox | ۲ تصویر اولیه ثبت؛ ۲ شات فرم/نتیجه کم است |
| 3 | اتصال WinBox با MAC/IP | WinBox / WinBox → Connect to / Login; پس از ورود Interfaces و IP → Addresses | WinBox → Connect to / Login; پس از ورود Interfaces و IP → Addresses | Connect to=IP محلی ایزوله؛ Login=حساب لاب؛ Password هرگز در تصویر نمایش داده نشود | ورود واقعی، Version/Identity و منوی Interfaces | NOT_CAPTURED |
| 4 | WebFig و Quick Set | WinBox / IP → Services | IP → Services؛ Quick Set (فقط اگر مدل پشتیبانی می‌کند) | دیدن Mode/WAN/LAN بدون دستکاری دستگاه پیکربندی‌شده؛ Apply تنها در لاب تازه | حفظ مسیر مدیریت و تفاوت Quick Set/WebFig | NOT_CAPTURED |
| 5 | Terminal و Safe Mode | WinBox / New Terminal | New Terminal؛ Safe Mode | دستورهای print و یک Comment آزمایشی، Ctrl+X / rollback طبق نسخه | تغییر/بازگشت تأییدشده در همان Session | NOT_CAPTURED |
| 6 | کاربران و خدمات مدیریت | WinBox / System → Users | System → Users؛ IP → Services | حساب آزمایشی و Address Allow-list فقط روی لاب؛ کلیدها پنهان | ورود حساب محدود و بسته‌بودن دسترسی نامجاز | NOT_CAPTURED |
| 7 | Backup/Export/Restore | WinBox / Files | Files؛ System → Backup (منوی واقعی را کنترل کنید) | نام فایل Backup و Export، تفاوت binary/text | فایل‌ها و بازیابی روی clone ایزوله | NOT_CAPTURED |
| 8 | Reset/Netinstall/License | WinBox / System → Reset Configuration | System → Reset Configuration؛ System → License | خواندن و مقایسه؛ عمل مخرب فقط روی دستگاه آزمایشی و با rollback واقعی | بوت و آدرس مدیریت پس از بازیابی؛ برای Netinstall تصویر دستگاه فیزیکی | NOT_CAPTURED |
| 9 | Upgrade/RouterBOOT | WinBox / System → Packages | System → Packages؛ System → RouterBOARD | Version/Channel و Firmware در دستگاه سازگار | قبل و بعد از Update و Checksum/بازگشت | NOT_CAPTURED |
| 10 | IPv4/Subnet/Gateway | WinBox / IP → Addresses | IP → Addresses | Address=10.77.10.1/24, Interface=LAB-LAN فقط در لاب | IP list و ping واقعی Client | NOT_CAPTURED |
| 11 | DHCP Client | WinBox / IP → DHCP Client | IP → DHCP Client | Interface=lab-WAN, Add Default Route و Use Peer DNS طبق طرح | Bound Status، Dynamic Address و Routes | NOT_CAPTURED |
| 12 | DHCP Server | WinBox / IP → DHCP Server | IP → DHCP Server؛ IP → Pool | DHCP Setup روی Bridge LAN، Pool، Network/Lease | Lease واقعی و IP Client | NOT_CAPTURED |
| 13 | DNS/ARP | WinBox / IP → DNS | IP → DNS؛ IP → ARP | Static DNS و ARP Modes فقط در لاب | DNS cache، ARP mapping و تست query | NOT_CAPTURED |
| 14 | Bridge/RSTP | WinBox / Bridge → Bridges | Bridge → Bridges؛ Ports؛ STP | Bridge name، ether2/ether3، Protocol Mode=RSTP با کنترل Topology | Bridge Ports و Host table بدون Loop | NOT_CAPTURED |
| 15 | Wireless Station Bridge | WinBox / WiFi/Wireless | WiFi/Wireless؛ Bridge | AP و Station روی رادیوی واقعی، بسته/Mode متناسب با مدل | MAC table، Registration و Traffic واقعی | NOT_CAPTURED |
| 16 | Static/default Route | WinBox / IP → Routes | IP → Routes | Dst. Address=10.77.20.0/24, Gateway=10.77.12.2 روی R1 ایزوله | Active Route و Ping با Source درست | NOT_CAPTURED |
| 17 | Dual LAN Return Route | WinBox / IP → Routes روی R1 و R2 | IP → Routes روی R1 و R2 | Route رفت/برگشت با IPهای آزمایشگاهی مجزا | Traceroute و Ping دو طرف | NOT_CAPTURED |
| 18 | Dynamic Route/Flags | WinBox / IP → Routes | IP → Routes؛ IP → DHCP Client | فقط نمایش Flags و Source مسیر Dynamic | Active/Inactive و Gateway Resolve | NOT_CAPTURED |
| 19 | Source NAT | WinBox / IP → Firewall → NAT | IP → Firewall → NAT | Chain=srcnat، Out Interface=lab-WAN، Action=masquerade فقط در لاب | Rule Counter و IP Source سمت Server | NOT_CAPTURED |
| 20 | Destination NAT/CGNAT | WinBox / IP → Firewall → NAT | IP → Firewall → NAT | Chain=dstnat، Dst-Port آزمایشی، To-Addresses/Ports سرور لاب | اتصال Client آزمایشی و Counter Forward | NOT_CAPTURED |
| 21 | Connection Tracking | WinBox / IP → Firewall → Connections | IP → Firewall → Connections | خواندن New/Established/Related/Invalid بدون تغییر غیرضروری | State و ارتباط با Input/Forward | NOT_CAPTURED |
| 22 | Filter/Address List | WinBox / IP → Firewall → Filter Rules / Address Lists | IP → Firewall → Filter Rules / Address Lists | Rule comment/name، Src Address List و Action محدود | ترتیب Rule و Counter واقعی | NOT_CAPTURED |
| 23 | Firewall hardening | WinBox / IP → Firewall → Filter Rules | IP → Firewall → Filter Rules؛ Log | قانون محدود Input، Log Prefix، preserving management | تست Allow/Deny و Undo با Console | NOT_CAPTURED |
| 24 | WiFi Package/Frequency | WinBox / WiFi/Wireless و System → Packages | WiFi/Wireless و System → Packages | نوع درایور، Frequency و Country مجاز، فقط رادیوی واقعی | Version + Radio info + Scan تحت مجوز | NOT_CAPTURED |
| 25 | AP/Station Security | WinBox / WiFi → Configuration/Security | WiFi → Configuration/Security؛ Registration | SSID آزمایشی و WPA2/3 امن با رمز مخفی | Association + IP/DHCP + Signal واقعی | NOT_CAPTURED |
| 26 | Access/Connect List | WinBox / WiFi/Wireless → Access List / Registration | WiFi/Wireless → Access List / Registration | MAC آزمایشگاهی، Rule Allow/Deny محدود و برگشت | Registration before/after و log | NOT_CAPTURED |
| 27 | Simple Queue | WinBox / Queues → Simple Queues | Queues → Simple Queues | Target=10.77.10.10/32، Max Limit سقف لاب | Counters، نمودار سرعت و FastTrack Path | NOT_CAPTURED |
| 28 | PCQ | WinBox / Queues → Queue Types / Simple Queues | Queues → Queue Types / Simple Queues | Classifier=src/dst طبق جهت و PCQ Rate آزمایشی | Traffic ۲ Client و Counter زیرصف | NOT_CAPTURED |
| 29 | Burst/Limit-at/FastTrack | WinBox / Queues → Simple Queues | Queues → Simple Queues؛ IP → Firewall Filter | Limit-at / Max Limit / Burst با طرح دقیق؛ FastTrack کنترل‌شده | اندازه‌گیری قبل/بعد و CPU/Traffic | NOT_CAPTURED |
| 30 | PPP Profile/Secret/Pool | WinBox / PPP → Profiles/Secrets | PPP → Profiles/Secrets؛ IP → Pool | Local=10.77.30.1 و Remote=Pool لاب، رمز محرمانه | Profile/Pool تطبیق‌شده و Active Sessions صفر تا اتصال | NOT_CAPTURED |
| 31 | PPPoE Client/Server | WinBox / PPP → PPPoE Servers | PPP → PPPoE Servers؛ Interfaces → PPPoE Client | Service Name، Interface، Secret/Client فقط لاب | Active PPP، Remote IP و MTU | NOT_CAPTURED |
| 32 | PPTP/SSTP | WinBox / PPP → Client و Certificates | PPP → Client و Certificates | فقط بررسی تاریخی PPTP؛ SSTP با TLS و گواهی معتبر در لاب | Certificate validation، Session + Route | NOT_CAPTURED |
| 33 | WireGuard | WinBox / WireGuard → Interfaces/Peers | WireGuard → Interfaces/Peers؛ IP → Addresses | Public Key، Allowed Address، Endpoint آزمایشی؛ Private Key پنهان | Handshake واقعی و Route/Firewall | NOT_CAPTURED |
| 34 | Ping/Torch/Log | WinBox / Tools → Ping/Traceroute/Torch | Tools → Ping/Traceroute/Torch؛ Log | Destination، Source و Interface واقعی در لاب | Ping/Trace/Traffic با Timestamp | NOT_CAPTURED |
| 35 | Netwatch/SNMP | WinBox / Tools → Netwatch | Tools → Netwatch؛ IP → SNMP (مسیر بررسی شود)؛ Tools → Profile | Probe زمان‌دار، SNMP restricted، بدون Credential عمومی | Probe State و SNMP Counter/CPU | NOT_CAPTURED |
| 36 | Supout/The Dude | WinBox / Make Supout.rif | Make Supout.rif؛ Files؛ The Dude در محیط سازگار | فقط خروجی آزمایشگاهی و تنظیمات مانیتورینگ مجاز | فایل داخلی، Version و گزارش Sanitized | NOT_CAPTURED |
| 37 | پروژه پایانی ۱ | WinBox / Interfaces/Bridge/IP/DHCP | Interfaces/Bridge/IP/DHCP | توپولوژی و IP و DHCP آزمایشگاه نهایی | Lease و Route/Bridge واقعی | NOT_CAPTURED |
| 38 | پروژه پایانی ۲ | WinBox / IP → Routes | IP → Routes؛ Firewall NAT/Filter؛ Queues | Route برگشت، Ruleهای محدود، NAT و Queue با Comment | Counters/Acceptance matrix | NOT_CAPTURED |
| 39 | پروژه پایانی ۳ | WinBox / Tools → Ping/Traceroute | Tools → Ping/Traceroute؛ Log؛ Files | خرابی کنترل‌شده، رفع مشکل و بازیابی | شواهد قبل/بعد/rollback | NOT_CAPTURED |
| 40 | جمع‌بندی و آزمون عملی | WinBox / System Resources | System Resources؛ Terminal؛ IP/FW/Queues | هیچ تغییر تازه‌ای لازم نیست؛ بازخوانی شواهد واقعی از پروژه | ماتریس توانمندی و ۱۲ سؤال غیررسمی | NOT_CAPTURED |

## ساختار نام فایل و تعریف انجام‌شده

برای هر قسمت: `LNN-01-entry.png`، `LNN-02-navigation.png`، `LNN-03-fields.png`، `LNN-04-result.png`. برای آزمون بازگشت مستقل، در صورت نیاز `LNN-05-rollback.png`. فایل‌ها در `content/mtcna/screenshots/real-lab/YYYY-MM-DD/` با `capture-metadata.json` ثبت شوند.

قبل از انتقال به WordPress باید این موارد PASS شوند: خوانایی در موبایل، شماره‌گذاری متوالی، تصحیح واقعی مسیر WinBox4.5، اختلاف مورد انتظار/مشاهده، عدم نمایش رمز و دادهٔ دیگران، نبود تکرار با صفحات منتشرشده ۴۰ و ۶۲–۶۷، انطباق تصاویر با متن، تست لغزش/سئو، ثبت نسخه/تاریخ، آزمون بازیابی، WordPress Gutenberg editor-save/readback و گیت انتشار.

بعد از تأیید برای هر قسمت، متن آموزش باید زیر هر تصویر با شمارهٔ مرحله، نام فیلد و مقدار آزمایشی دقیق نوشته شود؛ تصویر بی‌توضیح یا اسکرین‌شات از سایت ثالث به اسم لاب تهنت مجاز نیست.
