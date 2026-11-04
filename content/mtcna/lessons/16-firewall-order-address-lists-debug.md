> پیش‌نویس مستقل آموزشی تهنت، کوتاه‌شدهٔ تهران نتورک؛ اجرای آزمایشگاه و تهیهٔ تصاویر هنوز انجام نشده است. مبنای برنامه‌ریزی RouterOS 7.25.1 و WinBox 4.5 است؛ نمایش نسخهٔ 7.26 در مستندات جدید، تأیید اجرای این تمرین روی آن نسخه نیست. همهٔ نتیجه‌ها «مورد انتظار» هستند. این متن ادعای تطبیق با ویدئوی منتشرشده یا آزمون رسمی جدید ندارد.

## پاسخ سریع

فایروال را باید از بالا به پایین و برای یک جریان مشخص خواند. قاعدهٔ پایانی مانند accept یا drop که منطبق شود، می‌تواند مانع رسیدن بسته به قواعد بعدی شود؛ بنابراین یک accept درست زیر drop مرتبط، مشکل را حل نمی‌کند. Address List فقط گروهی از نشانی‌ها برای تطبیق است و تا وقتی در یک قانون استفاده نشود، اثری بر عبور ترافیک ندارد. در این درس این دو مفهوم را در یک زنجیرهٔ کوچک و محدود می‌سنجیم.

## هدف‌ها و پیش‌نیاز

باید بتوانید با تعریف مبدأ، مقصد، پروتکل و پورت، مسیر بررسی یک بسته را دنبال کنید و بین «عضو نبودن در فهرست» و «نرسیدن به قانون» فرق بگذارید. درس input/forward و دسترسی HTTP آزمایشگاهی لازم است. تغییرات فقط روی forward مربوط به سرور مشخص انجام می‌شود؛ مدیریت WinBox و input موضوع این آزمایش نیست. انجام کار روی روتر دوردستی که فقط همان مسیر مدیریت را دارید مجاز نیست؛ نسخهٔ جداشده و کنسول محلی لازم است.

## طرح آزمایشگاه

R1 روی bridge-lan برابر 10.77.10.1/24 و روی ether1 برابر 10.77.0.2/24 است. کلاینت A با 10.77.10.10/24 و گیت‌وی 10.77.10.1 در LAN قرار دارد. سرور HTTP روی سگمنت بالادست آدرس اختصاص‌یافتهٔ 10.77.0.10/24 و پورت 8080 دارد. این همان سرویس بی‌حساسیت آزمایشگاهی درس NAT است؛ اینترنت واقعی در کار نیست. برای نتیجهٔ قابل تفسیر، مسیر برگشت سرور باید با route مناسب یا ترجمهٔ محدود درس ۱۳ از قبل کار کند.

## مراحل اجرا

۱. **یک جریان موفق اولیه ثبت کنید.** قبل از افزودن قواعد، A باید صفحهٔ `http://10.77.0.10:8080/` را باز کند. اگر این کار هنوز شکست دارد، این درس را روی خرابی حل‌نشدهٔ route یا سرویس سوار نکنید؛ نخست آن را جدا بررسی کنید. زمان، پاسخ HTTP و سیاست فعلی forward را یادداشت کنید. در صورت وجود FastTrack یا accept established جلوتر، محل ورود زنجیرهٔ آزمایشی باید آگاهانه انتخاب شود.

```routeros
/ip firewall filter print detail where chain=forward
/ip firewall address-list print detail where list="TEHNET-L16-allowed"
/ip firewall nat print detail
```

۲. **فهرست با معنای محدود بسازید.** در WinBox، IP > Firewall > Address Lists، Name را TEHNET-L16-allowed و Address را 10.77.10.10 وارد کنید. این نام به معنی «مبدأ مجاز برای سرویس آزمایشی» است، نه اعتماد کلی به آن دستگاه. از دامنهٔ DNS یا فهرست پویا در این مرحله استفاده نمی‌کنیم تا عضویت قابل پیش‌بینی باشد. پیش از افزودن مطمئن شوید همین فهرست متعلق به آزمایش دیگری نیست.

```routeros
/ip firewall address-list add list="TEHNET-L16-allowed" address=10.77.10.10 comment="TEHNET-L16-member"
```

۳. **قواعد زنجیرهٔ اختصاصی را بسازید.** ابتدا زنجیره را با دو rule تعریف می‌کنیم: اعضای فهرست به سرویس مشخص مجازند و سایر مبدأهای LAN برای همان سرویس رد می‌شوند. هر دو قانون با همان مقصد، پروتکل و پورت محدود شده‌اند. در WinBox در General نام chain سفارشی را وارد و در Advanced، Src. Address List را برای accept انتخاب کنید.

```routeros
/ip firewall filter add chain="TEHNET-L16" src-address-list="TEHNET-L16-allowed" dst-address=10.77.0.10/32 protocol=tcp dst-port=8080 action=accept comment="TEHNET-L16-allow"
/ip firewall filter add chain="TEHNET-L16" src-address=10.77.10.0/24 dst-address=10.77.0.10/32 protocol=tcp dst-port=8080 action=drop comment="TEHNET-L16-deny"
/ip firewall filter add chain=forward in-interface=bridge-lan out-interface=ether1 src-address=10.77.10.0/24 dst-address=10.77.0.10/32 protocol=tcp dst-port=8080 action=jump jump-target="TEHNET-L16" disabled=yes comment="TEHNET-L16-jump"
```

۴. **ورودی زنجیره را جای‌گذاری کنید.** jump ابتدا غیرفعال است. در Filter Rules آن را بالاتر از نخستین accept، drop، FastTrack یا jump مرتبط با همین جریان بگذارید؛ سپس فقط همین rule را enable کنید. چون تطبیقش به زوج شبکه و سرور و پورت محدود است، جریان مدیریت روتر را نمی‌گیرد. accept در زنجیرهٔ سفارشی تصمیم نهایی اجازه برای همین بسته است و سیاست‌های پایین‌تر را دور می‌زند؛ به همین دلیل این الگو باید فقط در آزمایشگاه و با محدودهٔ نوشته‌شده استفاده شود.

```routeros
/ip firewall filter enable [find where comment="TEHNET-L16-jump"]
/ip firewall filter print stats where chain="TEHNET-L16"
```

۵. **حالت مجاز را بررسی کنید.** از A درخواست تازه بفرستید. نتیجهٔ مورد انتظار، افزایش شمارندهٔ allow و دریافت صفحه است؛ شمارندهٔ deny نباید برای همان درخواست افزایش یابد. کلاینت دیگری مانند 10.77.10.11، فقط اگر واقعاً به آزمایشگاه اختصاص یافته، عضو فهرست نیست و درخواستش به همان سرویس باید drop شود. از جعل IP میزبان دیگر برای این مقایسه استفاده نکنید.

۶. **اثر ترتیب را با همان قواعد نشان دهید.** در زنجیرهٔ TEHNET-L16 فقط deny را بالاتر از allow منتقل کنید. هر دو قانون ممکن است برای A منطبق باشند، ولی drop زودتر تصمیم می‌گیرد. فرمان زیر به توضیح‌های اختصاصی تکیه دارد؛ پیش از اجرا مطمئن شوید هر جست‌وجو دقیقاً یک قانون برمی‌گرداند. پس از آزمون، accept را به جای اول برگردانید.

```routeros
/ip firewall filter move [find where comment="TEHNET-L16-deny"] destination=[find where comment="TEHNET-L16-allow"]
# After the isolated test, restore the intended order:
/ip firewall filter move [find where comment="TEHNET-L16-allow"] destination=[find where comment="TEHNET-L16-deny"]
```

برای مقایسه از درخواست تازه و زمان مشخص استفاده کنید. اگر اتصال قبلی FastTrack شده باشد، رفتار همان اتصال شاهد مناسبی برای ترتیب جدید نیست؛ آن را از سمت برنامه تمام کنید و پس از انقضا دوباره آزمایش کنید. خاموش کردن همهٔ FastTrackها یا پاک کردن تمام connection tracking برای این درس لازم نیست.

## جدول عیب‌یابی

| نشانه | بررسی بعدی | فرضیهٔ محدود |
|---|---|---|
| jump صفر است | رابط خروجی، پورت و تصمیم قبلی | بسته به ورودی زنجیره نمی‌رسد |
| jump زیاد، allow صفر، deny زیاد | عضویت و ترتیب | عضو درست نیست یا deny جلوتر است |
| allow زیاد، صفحه باز نمی‌شود | پاسخ سرور، NAT و جهت برگشت | اجازهٔ درخواست، پاسخ سرویس را تضمین نمی‌کند |
| عضو فهرست هست ولی نتیجه تغییر نکرد | قانون استفاده‌کننده و اتصال قبلی | خود فهرست عمل مستقلی انجام نمی‌دهد |

## تمرین و معیار پذیرش

پیش از هر درخواست، نام اولین rule تصمیم‌گیرنده را پیش‌بینی کنید. سه وضعیت را ثبت کنید: allow بالا و عضو حاضر؛ deny بالا و عضو حاضر؛ allow بالا و عضو حذف‌شده از همان فهرست. برای وضعیت سوم فقط ردیف با توضیح TEHNET-L16-member را موقتاً disable کنید و بعد enable کنید. معیار موفقیت، تطبیق پیش‌بینی با شمارنده و رفتار برنامه است. در گزارش بین حدس، نتیجهٔ مورد انتظار و مشاهدهٔ واقعی مرز روشن بگذارید.

## بازگشت محدود

ابتدا jump را حذف کنید تا ترافیک دیگر وارد زنجیرهٔ آزمایشی نشود، سپس فقط دو قانون و عضو فهرست همین درس را حذف کنید. قوانین دیگر و NAT آزمایش قبلی را دست‌نخورده نگه دارید مگر در بازگشت همان درس. سرور آزمایشی را پس از پایان کار متوقف کنید.

```routeros
/ip firewall filter remove [find where comment="TEHNET-L16-jump"]
/ip firewall filter remove [find where comment="TEHNET-L16-allow"]
/ip firewall filter remove [find where comment="TEHNET-L16-deny"]
/ip firewall address-list remove [find where comment="TEHNET-L16-member" and list="TEHNET-L16-allowed"]
```


## منابع رسمی

- [Address lists](https://manual.mikrotik.com/docs/firewall-and-quality-of-service/firewall/address-lists/)
- [Common Firewall Matchers and Actions](https://help.mikrotik.com/docs/spaces/ROS/pages/250708064/Common%2BFirewall%2BMatchers%2Band%2BActions)
- [Filter](https://manual.mikrotik.com/docs/firewall-and-quality-of-service/firewall/filter/)
