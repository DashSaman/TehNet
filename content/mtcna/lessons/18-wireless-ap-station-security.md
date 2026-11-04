> پیش‌نویس تهنت (تهران نتورک)، مبنای RouterOS 7.25.1 و WinBox 4.5. آزمایش سخت‌افزاری اجرا نشده و اسکرین‌شات‌ها هنوز تهیه نشده‌اند.

## پاسخ کوتاه و هدف آزمایش

برای اتصال امن یک کلاینت به AP، ابتدا مسیر صحیح درایور را پیدا کنید، سپس کشور، نقش، SSID و امنیت را تنظیم کنید و در پایان سرویس IP را بررسی کنید. دیده‌شدن نام شبکه یا حتی حضور Station در Registration Table، دریافت IP و دسترسی به مقصد را تضمین نمی‌کند. در این درس اتصال را در دو لایه می‌سنجیم: برقراری ارتباط رادیویی و انتقال ترافیک IP.

در پایان باید بتوانید AP رمزدار بسازید، اتصال یک Station را از جدول ثبت‌نام اثبات کنید، مشکل رمز را از مشکل DHCP جدا کنید و تغییرات را بدون Reset کامل برگردانید. هدف ساخت یک AP مستقل آزمایشگاهی است؛ پوشش سازمانی، رومینگ و طراحی چند AP به اندازه‌گیری و درس‌های تکمیلی نیاز دارند.

## تجهیزات و توپولوژی

روتر R1 باید رادیوی واقعی سازگار داشته باشد. مدیریت از کابل ether2 انجام می‌شود؛ `bridge-lan` از قبل آدرس `10.77.10.1/24` دارد. کلاینت بی‌سیم عضو همان LAN خواهد شد. اتصال ether1 به WAN آزمایشگاهی اختیاری است و برای اثبات اتصال WiFi لازم نیست. برای تمرین Station می‌توانید از لپ‌تاپ استفاده کنید؛ یک روتر میکروتیک دوم نیز باید رادیوی واقعی داشته باشد. CHR جای این تجهیزات را نمی‌گیرد.

| جزء | نقش |
|---|---|
| ether2 روی bridge-lan | راه مدیریت کابلی |
| wifi1 یا wlan1 روی R1 | AP آزمایشگاهی |
| لپ‌تاپ یا رادیوی دوم | Station |
| 10.77.10.10/24 | آدرس نمونهٔ کلاینت، فقط در صورت آزادبودن |

اگر DHCP درس ۸ روی `bridge-lan` فعال است، کلاینت را روی دریافت خودکار بگذارید. در غیر این صورت یک IP آزاد همان شبکه و gateway برابر `10.77.10.1` بدهید. هم‌زمان از یک IP ثابت برای دو کلاینت استفاده نکنید. ابتدا از وضعیت رادیوی موجود و عضویت Bridge یادداشت بگیرید؛ این مراحل برای رادیوی آزاد آزمایشگاه هستند و تنظیمات AP فعال سازمان را جایگزین نمی‌کنند.

## ۱. تنظیم AP با مسیر WiFi

در WinBox وارد **WiFi** شوید. در بخش Security یک پروفایل با نام `tehnet-sec18` بسازید، `WPA2 PSK` را انتخاب کنید و گذرواژهٔ طولانی و منحصربه‌فرد تعیین کنید. در سخت‌افزار و کلاینت سازگار می‌توانید WPA3 را نیز مطابق مستند مدل فعال کنید؛ برای آزمایش پایه ابتدا یک روش مشترک و مشخص داشته باشید. WPS را غیرفعال کنید. استفاده از WPA2 در این سناریو برای سازگاری و تفکیک خطاهاست؛ ادعای بهترین سیاست برای هر محیط نیست.

در Configuration پروفایل `tehnet-ap18` بسازید: Mode برابر AP، SSID برابر `TehNet-Lab18` و Country برابر کشور واقعی محل آزمایش. پروفایل امنیت را انتخاب کنید، سپس روی رابط واقعی اعمال کنید. فرمان زیر نمونهٔ آموزشی است؛ مقدار کشور و رمز باید پیش از اجرا جایگزین شود، نه اینکه عیناً با جای‌نگهدار اجرا شود:

```routeros
/interface wifi security add name=tehnet-sec18 authentication-types=wpa2-psk passphrase="REPLACE-WITH-UNIQUE-LAB-PASSPHRASE" wps=disable
/interface wifi configuration add name=tehnet-ap18 mode=ap ssid="TehNet-Lab18" country="REPLACE-WITH-ACTUAL-COUNTRY" security=tehnet-sec18
/interface wifi set [find where name="wifi1"] configuration=tehnet-ap18 disabled=no
```

نام رابط را از دستگاه بخوانید. اگر کشور پذیرفته نمی‌شود، با تکمیل خودکار CLI یا فهرست GUI مقدار معتبر همان نسخه را انتخاب کنید. کانال و باند را مطابق رادیو تعیین کنید؛ نمونهٔ یک دستگاه دو بانده را روی رادیوی دیگر کپی نکنید. سپس در **Bridge → Ports** رابط AP را به `bridge-lan` اضافه کنید، فقط اگر از قبل عضو هیچ Bridge نیست:

```routeros
/interface bridge port print where interface=wifi1
/interface bridge port add bridge=bridge-lan interface=wifi1 comment="tehnet-l18"
```

اگر ردیف موجود است، دستور add را اجرا نکنید. تنظیم Bridge فقط مسیر لایهٔ دو به LAN را فراهم می‌کند؛ خودش DHCP Server نمی‌سازد. ساختار پروفایل و ارث‌بری تنظیمات WiFi در مرجع رسمی توضیح داده شده است. [۱]

## ۲. مسیر جایگزین روی بستهٔ قدیمی wireless

این بخش جایگزین بخش اول است و هم‌زمان روی همان رادیو اجرا نمی‌شود. در **Wireless → Security Profiles** یک پروفایل dynamic keys با WPA2 PSK و AES بسازید. روی رابط wlan1، Mode را `ap bridge`، SSID را نام آزمایش و Security Profile را پروفایل جدید قرار دهید. کشور باید همان محل واقعی باشد.

```routeros
/interface wireless security-profiles add name=tehnet-sec18 mode=dynamic-keys authentication-types=wpa2-psk unicast-ciphers=aes-ccm group-ciphers=aes-ccm wpa2-pre-shared-key="REPLACE-WITH-UNIQUE-LAB-PASSPHRASE"
/interface wireless set [find where name="wlan1"] mode=ap-bridge ssid="TehNet-Lab18" country="REPLACE-WITH-ACTUAL-COUNTRY" security-profile=tehnet-sec18 wps-mode=disabled disabled=no
```

سپس عضویت wlan1 در Bridge را مانند بخش اول، پس از بررسی ردیف‌های موجود اضافه کنید. درایور قدیمی و WiFi جدید نام پارامترهای یکسانی برای همهٔ تنظیمات ندارند. خطای فرمان را با حدس‌زدن رمز یا نصب بستهٔ تصادفی درمان نکنید. [۲]

## ۳. اتصال Station و خواندن شواهد

روی لپ‌تاپ شبکهٔ آزمایش را انتخاب و رمز را وارد کنید. اگر روتر دوم دارید، فقط رادیوی آن را در حالت Station قرار دهید و SSID و روش احراز هویت یکسان انتخاب کنید. برای مسیر جدید، نمونهٔ تنظیم مستقیم چنین است؛ کشور باید قبلاً صحیح تعیین شده باشد:

```routeros
/interface wifi set [find where name="wifi1"] configuration.mode=station configuration.ssid="TehNet-Lab18" security.authentication-types=wpa2-psk security.passphrase="REPLACE-WITH-SAME-LAB-PASSPHRASE" disabled=no
```

روی AP در WinBox جدول **Registration** را باز کنید و MAC کلاینت، سیگنال و زمان اتصال را ببینید. مسیرهای CLI جایگزین:

```routeros
/interface wifi registration-table print detail
```

یا روی درایور قدیمی:

```routeros
/interface wireless registration-table print detail
```

در این مرحله از Station معمولی، Bridge شفاف برای دستگاه‌های پشت روتر دوم نسازید. حالت‌های Station و سازگاری Bridge محدودیت دارند و باید جداگانه انتخاب شوند. [۳] برای آزمایش حاضر، خود Station یا لپ‌تاپ یک کلاینت است.

## ۴. آزمون IP و نتیجهٔ مورد انتظار

از کلاینت آدرس `10.77.10.1` را ping کنید. انتظار داریم اگر اتصال رادیویی، عضویت Bridge و IP صحیح باشند پاسخ برسد. سپس فقط در صورت آماده‌بودن مسیر WAN آزمایش، مقصد مجاز بیرونی را بررسی کنید. پاسخ‌ندادن اینترنت به‌تنهایی شکست WiFi نیست. رمز را در اسکرین‌شات عمومی نشان ندهید و قدرت سیگنال را عدد ساختگی ننویسید؛ کیفیت واقعی به فاصله، نویز، آنتن و محیط وابسته است.

## جدول عیب‌یابی

| نشانه | بررسی | اصلاح محدود |
|---|---|---|
| SSID دیده نمی‌شود | فعال‌بودن رادیو، باند کلاینت و وضعیت کانال | خطای وضعیت رابط را بخوانید |
| SSID دیده می‌شود ولی ثبت‌نام نداریم | رمز و روش احراز هویت | پروفایل هر دو سمت را تطبیق دهید |
| ثبت‌نام هست ولی IP نداریم | DHCP، Bridge و IP تکراری | سرویس IP را جدا بررسی کنید |
| ping روتر کار می‌کند، اینترنت نه | route، NAT و WAN | از دستکاری رادیو خودداری کنید |
| اتصال متناوب است | سیگنال و محیط، سپس Log | یک متغیر در هر نوبت تغییر دهید |

## تمرین، معیار پذیرش و بازگشت

یک بار گذرواژهٔ Station را عمداً اشتباه کنید، نشانه را ثبت کنید و مقدار صحیح را برگردانید. بار دوم IP کلاینت را خارج از subnet بگذارید و تفاوت نشانه‌ها را توضیح دهید. قبولی یعنی برای هر خرابی، شواهد لایهٔ رادیویی و IP را جدا ارائه کنید؛ گفتن «وصل نمی‌شود» کافی نیست.

برای جمع‌کردن آزمایش، از کابل متصل بمانید، رابط رادیویی آزمایش را غیرفعال کنید و فقط ردیف Bridge با comment `tehnet-l18` را حذف کنید. تنظیم قبلی رابط را از یادداشت اولیه برگردانید؛ سپس اگر دیگر ارجاعی ندارند پروفایل‌های ساخته‌شده را حذف کنید. پروفایل مشترک یا پورت مدیریتی را حذف نکنید. این بازگشت باید صرفاً اشیای همین درس را هدف بگیرد.

## منابع رسمی

۱. [Wi-Fi: configuration، security و registration](https://manual.mikrotik.com/docs/wireless/wifi/)

۲. [Wireless Interface](https://manual.mikrotik.com/docs/wireless/abgn/wireless-interface/)

۳. [Wireless Station Modes](https://manual.mikrotik.com/docs/wireless/user-guides/wireless-station-modes/)
