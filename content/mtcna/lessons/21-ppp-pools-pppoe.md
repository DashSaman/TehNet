> پیش‌نویس تهنت (تهران نتورک)، مبنای RouterOS 7.25.1 و WinBox 4.5؛ این آزمایش اجرا نشده و تصاویر واقعی موجود نیستند.

## پاسخ کوتاه: تفاوت PPP، Pool و PPPoE چیست؟

PPP چارچوب برقراری نشست نقطه‌به‌نقطه است. PPPoE این نشست را روی Ethernet حمل می‌کند. Pool مجموعه‌ای از آدرس‌های قابل‌تخصیص، Profile سیاست مشترک نشست و Secret حساب کاربری است. هیچ‌کدام جای دیگری را نمی‌گیرد: ساخت Pool، کاربر ایجاد نمی‌کند و ساخت Secret، PPPoE Server را روی پورت روشن نمی‌کند. این درس فصل هشتم را با ساخت یک سرویس محدود در آزمایشگاه آغاز می‌کند.

پس از درس باید بتوانید وابستگی Pool، Profile، Secret و Server را توضیح دهید، اتصال کلاینت را در Active Connections ببینید و خطای Discovery را از خطای احراز هویت جدا کنید. PPPoE به‌خودی‌خود معادل VPN رمزگذاری‌شده نیست؛ در این تمرین از رمز و حساب آزمایشگاهی استفاده می‌کنیم و امنیت محرمانگی را از وجود نام کاربری نتیجه نمی‌گیریم.

## توپولوژی اختصاصی این آزمایش

R1 از ether2 و `bridge-lan` مدیریت می‌شود؛ IP مدیریت `10.77.10.1/24` است. یک پورت آزاد مانند ether4 را فقط برای PPPoE به روتر دوم یا کلاینت وصل کنید. این پورت نباید عضو Bridge، دارای IP، DHCP Client یا DHCP Server باشد. R2 نیز از LAN مستقل خودش مدیریت شود و ether1 آن فقط کلاینت PPPoE باشد. اگر روی ether1 روتر دوم لینک Transit درس‌های مسیریابی وجود دارد، از پورت آزاد دیگر یا نمونهٔ آزمایش جدا استفاده کنید؛ همان پورت را هم‌زمان برای هر دو سناریو به کار نبرید.

| جزء | مقدار آموزشی |
|---|---|
| رابط سرویس روی R1 | ether4 آزاد و جدا از LAN |
| سرویس | TehNet-PPPoE |
| آدرس محلی PPP | 10.77.30.1 |
| Pool کلاینت | 10.77.30.10 تا 10.77.30.20 |
| حساب تمرین | tehnet-l21 |
| Default route خودکار کلاینت | غیرفعال |

این آدرس‌ها با LAN و Transit دوره هم‌پوشانی ندارند. روی حامل Ethernet برای این تمرین IP عادی تخصیص نمی‌دهیم؛ آدرس IP پس از ایجاد نشست PPP به رابط منطقی مربوط می‌شود. مستند رسمی نیز دربارهٔ استفاده از IP ثابت یا DHCP روی رابط ارائهٔ PPPoE هشدار می‌دهد. [۱]

## ۱. بررسی آماده‌بودن رابط

در WinBox **Bridge → Ports** و سپس **IP → Addresses** را ببینید. پورت آزاد را از روی نام فیزیکی و کابل مشخص کنید. فرمان‌های خواندنی روی R1:

```routeros
/interface bridge port print where interface=ether4
/ip address print where interface=ether4
/ip dhcp-client print where interface=ether4
/ip dhcp-server print where interface=ether4
```

اگر خروجی تنظیمی نشان داد که متعلق به سناریوی دیگری است، آن را کورکورانه حذف نکنید؛ پورت آزاد دیگری انتخاب کنید یا در یک نمونهٔ مستقل تمرین کنید. پیش‌شرط این درس پورت آزاد است، نه پاک‌کردن شبکهٔ موجود. در R2 نیز همین بررسی را برای رابط حامل کلاینت انجام دهید.

## ۲. ساخت Pool و Profile

در **IP → Pool**، Pool با نام `tehnet-pool21` و بازهٔ جدول بسازید. سپس در **PPP → Profiles** پروفایل `tehnet-prof21` بسازید؛ Local Address برابر `10.77.30.1` و Remote Address برابر نام Pool باشد. برای این آزمایش نیازی به دادن DNS عمومی یا مسیر پیش‌فرض نیست.

```routeros
/ip pool add name=tehnet-pool21 ranges=10.77.30.10-10.77.30.20
/ppp profile add name=tehnet-prof21 local-address=10.77.30.1 remote-address=tehnet-pool21
```

Local Address سمت سرور نشست است و Remote Address به کلاینت تعلق می‌گیرد. آدرس محلی را در بازهٔ Pool قرار ندهید. اگر همهٔ آدرس‌ها مصرف شوند، صرف صحیح‌بودن رمز برای ایجاد نشست کافی نیست. Pool را با subnet mask وارد نمی‌کنیم؛ مقدار خواسته‌شده در اینجا بازهٔ آدرس است.

## ۳. ساخت حساب و Server

در **PPP → Secrets** حساب `tehnet-l21` را ایجاد کنید، Service را PPPoE و Profile را `tehnet-prof21` بگذارید. رمز نمونه را پیش از اجرا با مقدار منحصربه‌فرد جایگزین کنید. سپس در **PPP → PPPoE Servers** سرویس را روی ether4 فعال کنید. در این محیط CHAP را صریح انتخاب می‌کنیم؛ این انتخاب به معنای رمزگذاری ترافیک کاربران نیست.

```routeros
/ppp secret add name=tehnet-l21 password="REPLACE-WITH-UNIQUE-LAB-PASSWORD" service=pppoe profile=tehnet-prof21
/interface pppoe-server server add interface=ether4 service-name="TehNet-PPPoE" default-profile=tehnet-prof21 authentication=chap one-session-per-host=yes disabled=no
```

محدودکردن Service در Secret کمک می‌کند حساب آزمایش به سرویس PPP دیگری تسری پیدا نکند. Profile در Secret می‌تواند سیاست کاربر را تعیین کند؛ فقط به default-profile سرور نگاه نکنید. در صورت وجود Firewall سفارشی، قواعد لازم همان آزمایش را بازبینی کنید؛ خاموش‌کردن کل Firewall راه‌اندازی سرویس را قابل‌اعتماد نمی‌کند.

## ۴. ساخت کلاینت روی R2

در **PPP → Interfaces** یک PPPoE Client اضافه کنید. Interface حامل را انتخاب، Service Name و حساب را وارد و گزینه‌های Add Default Route و Use Peer DNS را خاموش نگه دارید. این تصمیم از تغییر ناخواستهٔ مسیر و DNS مدیریت R2 جلوگیری می‌کند.

```routeros
/interface pppoe-client add name=tehnet-pppoe21 interface=ether1 service-name="TehNet-PPPoE" user=tehnet-l21 password="REPLACE-WITH-SAME-LAB-PASSWORD" allow=chap add-default-route=no use-peer-dns=no disabled=no
```

اگر ether1 آزاد نیست، نام رابط آزاد واقعی را جایگزین کنید. روی R1 در **PPP → Active Connections** انتظار یک نشست با نام کاربر و IP تخصیص‌یافته داریم. روی R2 وضعیت رابط باید نشان دهد نشست برقرار شده است. بررسی خواندنی:

```routeros
/ppp active print detail
```

فرمان بالا روی سرور اجرا می‌شود. روی کلاینت:

```routeros
/interface pppoe-client monitor tehnet-pppoe21 once
/ip address print
/ping 10.77.30.1 interface=tehnet-pppoe21 count=5
```

این‌ها نتایج مورد انتظارند؛ خروجی واقعی باید پس از اجرا ثبت شود. هدف فعلی ping سمت سرور PPP است. نبود اینترنت طبیعی است، چون route و NAT مربوط به اینترنت برای Pool این تمرین ساخته نشده‌اند.

## ۵. خواندن مراحل و MTU

PPPoE ابتدا سرور را در لایهٔ دو پیدا می‌کند و بعد نشست، احراز هویت و مذاکرهٔ IP انجام می‌شود. در گزارش تشخیص دهید توقف پیش از دریافت پاسخ سرور است یا پس از ارسال اطلاعات کاربر. با عوض‌کردن رمز، مشکل کابل یا انتخاب رابط حل نمی‌شود. تفاوت این دو نوع خطا اساس عیب‌یابی مرحله‌ای است.

PPPoE سربار اضافه دارد؛ روی Ethernet معمولی ۱۵۰۰ بایتی، عدد ۱۴۹۲ برای MTU IP متداول است. مقدار نهایی را از نشست بخوانید و قابلیت فریم بزرگ‌تر را بدون بررسی دو سمت و مسیر فرض نکنید. اگر ping کوچک جواب می‌دهد ولی انتقال بزرگ گیر می‌کند، MTU، Path MTU Discovery و MSS را بررسی کنید؛ کاهش تصادفی MTU به عددهای بسیار کوچک روش تشخیص نیست. [۱]

## جدول عیب‌یابی

| نشانه | مرحلهٔ محتمل | بررسی بعدی |
|---|---|---|
| کلاینت دنبال سرویس می‌گردد | Discovery | کابل، رابط، Service Name و سرور |
| Log خطای حساب می‌دهد | Authentication | Secret، رمز و allow مشترک |
| حساب درست است ولی IP نمی‌گیرد | تخصیص آدرس | Pool آزاد و Profile مؤثر |
| نشست هست ولی LANها وصل نیستند | Routing | مسیر رفت‌وبرگشت جداگانه |
| فقط انتقال بزرگ مشکل دارد | MTU یا MSS | اندازهٔ بسته و ICMP موردنیاز |
| مدیریت R2 تغییر کرده | تنظیم خودکار کلاینت | default route و peer DNS |

## تمرین و بازگشت امن

یک بار Service Name و یک بار رمز را اشتباه کنید؛ هر بار فقط یک تغییر بدهید، Log و وضعیت رابط را ثبت کنید و مقدار صحیح را برگردانید. معیار قبولی تشخیص دو خطا از روی مرحلهٔ توقف و دریافت IP در محدودهٔ Pool پس از اصلاح است.

برای پایان، ابتدا کلاینت `tehnet-pppoe21` را Disable و حذف کنید. روی R1 همان ردیف PPPoE Server را غیرفعال و حذف کنید، سپس Secret و Profile اختصاصی و در آخر Pool را حذف کنید. ترتیب وابستگی‌ها را رعایت کنید. پورت را تنها به تنظیمی برگردانید که پیش از درس مستند کرده‌اید؛ آن را حدسی عضو Bridge مدیریت نکنید.

## منابع رسمی

۱. [PPPoE: مراحل، آدرس‌دهی و مثال سرور/کلاینت](https://manual.mikrotik.com/docs/virtual-private-networks/pppoe/)

۲. [PPP Active؛ مشخصات نشست‌های فعال](https://manual.mikrotik.com/docs/cli-reference/ppp/active/)

۳. [PPPoE Server CLI reference](https://manual.mikrotik.com/docs/cli-reference/interface/pppoe-server/server/)
