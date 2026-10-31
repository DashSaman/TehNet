# بهبود صفحهٔ موجود مسیریابی استاتیک

وضعیت فعلی: **DEPLOYED؛ بهبود همان صفحهٔ موجود**. مقصد همان صفحه64، [مسیریابی استاتیک](https://tehnet.ir/learn/mikrotik/mtcna/static-routing/) است. عنوان، URL و نیت آموزشی حفظ می‌شوند. این بسته پنج نیاز C02، یعنی TN-T006 تا TN-T010، را در یک درس پوشش می‌دهد؛ پنج مقالهٔ جدید نیست. پرتفوی تاریخی کاندیداها سند انتشار نیست.

شاهد نیاز: متن موجود، تیتر «سه‌روتری» با توضیح دو روتر، توضیح مبهم src-address، مثال route check بدون تعیین ورودی‌های نسخهٔ فعلی و نتیجه‌گیری بیش‌ازحد از traceroute داشت. متن کامل از موجودی خواندنی بومیِ خصوصی بررسی شد؛ هیچ پروندهٔ مشتری یا خروجی پیکربندی در Git نیست. منبع فعلی check را موجود فهرست می‌کند؛ ادعای حذف آن درست نیست.

## منابعی که واقعاً خوانده شدند

بازبینی: ۱ نوامبر ۲۰۲۶ به وقت تهران. نوع: منابع رسمی/اولیه. انتخابگر Manual مقدار7.26 داشت؛ نسخهٔ هدف دستگاه نیست. دامنهٔ بررسی فقط بخش‌های زیر است، نه تمام مستندات یا تغییرات همهٔ نسخه‌ها.

| منبع | بخش خوانده‌شده و کاربرد | محدودیت |
|---|---|---|
| [Routing Decision](https://manual.mikrotik.com/docs/user-guides/routing-and-networking-protocols/routing-decision/) | RIB، انتخاب route، nexthop و FIB lookup؛ prefix در برابر distance، recursive gateway | رفتار دستگاه یا زمان failover آزمایش نشده |
| [ip route](https://manual.mikrotik.com/docs/cli-reference/ip/route/) | flags و gateway/immediate-gw/distance/table | خروجی واقعی ساخته نشده |
| [route check](https://manual.mikrotik.com/docs/cli-reference/ip/route/check/) | دستور با src-ip/dst-ip و فیلدهای نتیجه | پشتیبانی نسخهٔ دستگاه نامشخص؛ دستور مقاله اجرا نشده |
| [Ping](https://manual.mikrotik.com/docs/diagnostics-monitoring-and-troubleshooting/ping/) | count، src-address، timeout و سیاست مبدأ | پاسخ ICMP پذیرش سرویس نیست |
| [Traceroute](https://manual.mikrotik.com/docs/diagnostics-monitoring-and-troubleshooting/traceroute/) | count/max-hops، سکوت hop، loss میانی و مبدأ | از timeout محل قطعی قطعی نتیجه نمی‌گیریم |
| [Packet Flow](https://manual.mikrotik.com/docs/firewall-and-quality-of-service/packet-flow-in-routeros/) | Chains و routed Forward/Output | شرح MPLS/bridge/FastTrack این درس نیست |
| [Policy Routing](https://manual.mikrotik.com/docs/user-guides/routing-and-networking-protocols/policy-routing/) | table، rule/mangle و lookup/lookup-only-in-table | طرح آمادهٔ چند WAN ارائه نشده |
| [RFC5737](https://www.rfc-editor.org/rfc/rfc5737.html) | سه prefix مستندسازی و عدم استفاده در اینترنت عمومی/شبکهٔ محلی | نشانی‌ها فقط تصویرند؛ اجرای لاب نیازمند جایگزینی طرح خصوصیِ مجاز است |

## سنتز و ارزش افزوده

سناریوی دو روتر، نمودار عمودی مناسب عرض کم، مسیر رفت و برگشت، تفاوت Ping روتر با آزمون میزبان، ترتیب بررسی مبتنی بر مشاهده، طرح پذیرش و مرز failover/policy/هم‌پوشانی آدرس. ویدیوی موجود به‌شکل لینک حفظ می‌شود؛ پخش خارجی شرط خواندن نیست. CTA به خدمات میکروتیک موجود می‌رود. لینک‌های داخلی از موجودی واقعی انتخاب و با GET دارای TLS معتبر بررسی می‌شوند.

RouterOS/CHR یا سخت‌افزار شبکه اجرا نشده است. محاسبهٔ آدرس‌ها و آزمون وردپرس، آزمون RouterOS نیستند. کدهای add تغییردهنده و probeها ارسال‌کنندهٔ بسته‌اند؛ متن آن‌ها را خواندنی معرفی نمی‌کند. قالب عمومی خروجی، رخداد مشتری، زمان بازیابی یا درصد موفقیت جعل نشده است.

آزمون و انتشار در رسیدهای `qa/growth-2026-10-31/routing-*.json` ثبت می‌شوند. مانيفستِ ایجاد پیش‌نویس، وضعیت زنده نیست؛ وضعیت نهایی باید از رسید انتشار و HANDOFF خوانده شود. MyTel، خانه، منو،25 کالای استعلامی، موجودی و noindex خارج دامنهٔ تغییر هستند. هیچ ادعای رتبه/ترافیک/حجم جست‌وجو یا توصیه‌شدن توسط AI از این بهبود نتیجه نمی‌شود.


## نتیجهٔ انتشار واقعی

Source e2dcf87 در۰۱:۵۷تهران با backup تازه و checksum/drift منتشر شد؛9GET دارایTLS و35کنترل browser عمومی پاس. فقط body، تاریخ واقعی و revision متعلق به این تغییر؛ هویت/meta/دادهٔ محافظت‌شده/runtime ثابت. [رسید واقعی](../qa/growth-2026-10-31/routing-production-release.json) وضعیت فعلی را ثبت می‌کند؛ manifest و رسید draft/rehearsal checkpoint تاریخی‌اند. RouterOS/failover اجرا یا اندازه‌گیری نشده است.
