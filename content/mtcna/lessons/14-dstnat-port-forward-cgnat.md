> پیش‌نویس مستقل آموزشی تهنت، کوتاه‌شدهٔ تهران نتورک؛ اجرای آزمایشگاه و تهیهٔ تصاویر هنوز انجام نشده است. مبنای برنامه‌ریزی RouterOS 7.25.1 و WinBox 4.5 است؛ نمایش نسخهٔ 7.26 در مستندات جدید، تأیید اجرای این تمرین روی آن نسخه نیست. همهٔ نتیجه‌ها «مورد انتظار» هستند. این متن ادعای تطبیق با ویدئوی منتشرشده یا آزمون رسمی جدید ندارد.

## پاسخ سریع

dstnat مقصد اتصال ورودی را به سرور داخلی تغییر می‌دهد؛ Port Forwarding معمولاً ترجمهٔ یک پورت مشخص به سرویس داخلی است. این قانون باید همراه با اجازهٔ محدود forward، سرویس فعال و مسیر برگشت درست باشد. اگر اتصال ورودی پشت NAT بالادست یا CGNAT به روتر شما نرسد، قانون داخلی نمی‌تواند آن را از شبکهٔ ارائه‌دهنده عبور دهد. این تمرین فقط روی بالادست خصوصی و جداشده انجام می‌شود.

## هدف‌ها و پیش‌نیاز

باید بتوانید تفاوت پورت بیرونی و داخلی را توضیح دهید، مقصدی را که فیلتر forward می‌بیند درست بنویسید و آزمایش بیرونی را از آزمایش داخل LAN تفکیک کنید. route و NAT درس قبل پیش‌نیاز است. دسترسی محلی کنسول لازم است؛ هیچ rule کلی input یا drop سراسری اضافه نمی‌کنیم. سرویس مدیریتی واقعی، دوربین یا فایل خصوصی در این آزمایش منتشر نمی‌شود.

## آدرس‌بندی و سرویس

R1 روی ether1 آدرس 10.77.0.2/24 و روی bridge-lan آدرس 10.77.10.1/24 دارد. سرور آزمایشگاهی داخل LAN با IP اختصاص‌یافتهٔ 10.77.10.10/24 و گیت‌وی 10.77.10.1، HTTP را فقط روی پورت 8080 ارائه می‌کند. کلاینت بیرونی آزمایشگاهی 10.77.0.10/24 است و به همان سگمنت ether1 متصل می‌شود. آدرس درخواست بیرونی `http://10.77.0.2:18080/` است. این آدرس خصوصی ادعای دسترسی از اینترنت ندارد و وجود گیت‌وی 10.77.0.1 برای این آزمایش هم‌شبکه لازم نیست.

## مراحل اجرا

۱. **سرور را از داخل بررسی کنید.** ابتدا از میزبان دوم LAN، آدرس `http://10.77.10.10:8080/` را باز کنید. پاسخ باید فقط محتوای آزمایشی بی‌حساسیت باشد. اگر سرویس روی loopback میزبان گوش کند، روتر نمی‌تواند آن را به یک سرویس قابل دسترسی شبکه تبدیل کند. گیت‌وی سرور و اجازهٔ فایروال سیستم‌عامل برای مبدأ بیرونی آزمایش را بررسی کنید. لازم نیست همهٔ پورت‌ها یا فایروال میزبان باز شوند.

۲. **وضعیت قوانین را بخوانید.** در WinBox، IP > Firewall > NAT و Filter Rules را بررسی کنید. اگر قانون dstnat دیگری همین مقصد و پورت را می‌گیرد، جریان آزمایشی مستقل نیست. اگر drop زودهنگام forward وجود دارد، افزودن accept به آخر جدول لزوماً مؤثر نیست. شمارهٔ ردیف‌ها را به‌عنوان هویت ثابت ذخیره نکنید؛ بعد از تغییر جدول ممکن است عوض شوند.

```routeros
/ip firewall nat print detail
/ip firewall filter print detail where chain=forward
/ip address print detail where interface=ether1
```

۳. **dstnat محدود را بسازید.** General شامل Chain=dstnat، In. Interface=ether1، Src. Address=10.77.0.10/32، Dst. Address=10.77.0.2/32، Protocol=tcp و Dst. Port=18080 است. در Action، dst-nat و To Addresses=10.77.10.10 و To Ports=8080 را بگذارید. محدود کردن مبدأ، آزمایش را فقط برای همان کلاینت تعریف می‌کند.

```routeros
/ip firewall nat add chain=dstnat in-interface=ether1 src-address=10.77.0.10/32 dst-address=10.77.0.2/32 protocol=tcp dst-port=18080 action=dst-nat to-addresses=10.77.10.10 to-ports=8080 comment="TEHNET-L14-dnat"
```

۴. **اجازهٔ forward را به مقصد ترجمه‌شده بنویسید.** در مسیر عادی این بستهٔ عبوری، dstnat پیش از تصمیم forward اعمال شده است؛ بنابراین شرط destination در filter باید سرور داخلی و پورت 8080 باشد. در connection tracking، نگاشت اتصال اصلی با مقصد 10.77.0.2:18080 حفظ می‌شود؛ دیدن آن مقصد در اطلاعات اتصال به معنی اشتباه بودن شرط 8080 در forward نیست. باز کردن input پورت 18080، مجوز عبور به سرور را ایجاد نمی‌کند.

```routeros
/ip firewall filter add chain=forward in-interface=ether1 out-interface=bridge-lan src-address=10.77.0.10/32 dst-address=10.77.10.10/32 protocol=tcp dst-port=8080 connection-nat-state=dstnat action=accept comment="TEHNET-L14-forward-in"
/ip firewall filter add chain=forward in-interface=bridge-lan out-interface=ether1 src-address=10.77.10.10/32 dst-address=10.77.0.10/32 protocol=tcp src-port=8080 connection-state=established,related action=accept comment="TEHNET-L14-forward-reply"
```

این دو accept را در WinBox پس از بررسی سیاست موجود، بالاتر از اولین drop یا reject مرتبط با همین جریان قرار دهید. این یک تصمیم بر اساس جدول واقعی است؛ فرمانی با شمارهٔ فرضی برای جابه‌جایی نمی‌دهیم. قانون پاسخ فقط همین زوج میزبان و پورت را پوشش می‌دهد. اگر قاعدهٔ معتبر established/related از قبل پاسخ را می‌پذیرد، شمارندهٔ قانون پاسخ جدید ممکن است صفر بماند و این به‌تنهایی خطا نیست.

۵. **از بیرون آزمایشگاه درخواست تازه بدهید.** روی 10.77.0.10 آدرس بیرونی را باز کنید. نتیجهٔ مورد انتظار، صفحهٔ همان سرور و مشاهدهٔ انطباق NAT است. در Connections، جریان TCP مربوط را با مبدأ و مقصد اصلی پیدا کنید و نگاشت reply را بخوانید. پس از تغییر NAT، اتصال قبلی مرورگر را پایان دهید و برای آزمون جدید از اتصال تازه استفاده کنید؛ جدول اتصال‌های دیگر را پاک نکنید.

```routeros
/ip firewall nat print stats where comment="TEHNET-L14-dnat"
/ip firewall filter print stats where comment="TEHNET-L14-forward-in"
/ip firewall connection print detail where protocol=tcp
```

## CGNAT و آزمون داخل LAN

وقتی WAN خود روتر یک IP خصوصی یا آدرسی در محدودهٔ اشتراکی 100.64.0.0/10 دارد، احتمال وجود NAT بالادست را بررسی کنید. برای دسترسی ورودی واقعی باید همهٔ نقاط ترجمه و سیاست ارائه‌دهنده شناخته شوند؛ گاهی IP عمومی یا راهکار دسترسی مجاز دیگری لازم است. DDNS فقط نام را به آدرس مرتبط می‌کند و عبور ورودی از CGNAT را تضمین نمی‌کند. از سوی دیگر، بازکردن آدرس بیرونی از داخل همان LAN مسئلهٔ hairpin NAT است و این سناریوی «کلاینت روی ether1» را آزمایش نمی‌کند.

## جدول عیب‌یابی

| نشانه | بررسی محدود | تفسیر |
|---|---|---|
| NAT شمارنده ندارد | کلاینت بیرونی، ether1 و پورت 18080 | درخواست به این rule نرسیده است |
| NAT منطبق، forward صفر | rule زودتر، مقصد 8080 و ترتیب | ممکن است drop یا accept دیگری جلوتر باشد |
| درخواست به سرور رسیده، پاسخ نیست | gateway و فایروال سرور | مسیر پاسخ یا سرویس مسئله دارد |
| فقط آزمون داخل LAN شکست دارد | hairpin و محل واقعی مبدأ | این نتیجه شکست آزمون بیرونی را ثابت نمی‌کند |

## تمرین و بازگشت

پیش و پس از ترجمه، چهار مقدار مبدأ، مقصد، پورت مبدأ و پورت مقصد را برای درخواست و پاسخ بنویسید. پذیرش نیازمند پاسخ برنامه‌ای از کلاینت بیرونی مجاز و توضیح صحیح مقصد forward است. سپس هر سه rule این درس را حذف و سرویس آزمایشی را متوقف کنید. سایر قوانین NAT و مدیریت روتر نباید تغییر کنند.

```routeros
/ip firewall filter remove [find where comment="TEHNET-L14-forward-in"]
/ip firewall filter remove [find where comment="TEHNET-L14-forward-reply"]
/ip firewall nat remove [find where comment="TEHNET-L14-dnat"]
```


## منابع رسمی

- [NAT and CGNAT](https://manual.mikrotik.com/docs/firewall-and-quality-of-service/firewall/nat/)
- [Packet Flow](https://manual.mikrotik.com/docs/firewall-and-quality-of-service/packet-flow-in-routeros/)
- [Filter](https://manual.mikrotik.com/docs/firewall-and-quality-of-service/firewall/filter/)
