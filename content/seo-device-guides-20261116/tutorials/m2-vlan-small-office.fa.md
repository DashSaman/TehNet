# VLAN برای دفتر کوچک — راهنمای MikroTik (M2)

> آموزش تصویری از سری MikroTik و routing؛ مخاطب: کارشناس شبکهٔ مبتدی تا متوسط.
> سناریوی فرضی آموزشی با دادهٔ ساختگی؛ بدون دستکاری شبکهٔ واقعی.

## پاسخ کوتاه

VLAN ترافیک را روی یک سوئیچ به بخش‌های منطقی جدا می‌کند: کاربران، دوربین، تلفن و مهمان هرکدام VLAN مستقل می‌گیرند. این جداسازی امنیت (جلوگیری از دسترسی بین بخش‌ها)، مدیریت پهنای باند و عیب‌یابی را ساده‌تر می‌کند. برای راه‌اندازی، هر پورت سوئیچ یک VLAN ID می‌گیرد و روتر بین VLANها مسیر می‌دهد.

## پیش‌نیازها

- سوئیچ MikroTik با RouterOS (CRS یا hEX با پورت کافی)
- روتر MikroTik برای inter-VLAN routing (RB أو hEX با VLAN interface)
- اتصال کنسول یا WinBox به سوئیچ و روتر

## سناریوی فرضی

| پارامتر | مقدار |
|---|---|
| VLAN 10 | کاربران (VLAN10-Office) |
| VLAN 20 | دوربین (VLAN20-CCTV) |
| VLAN 30 | تلفن IP (VLAN30-Voice) |
| VLAN 40 | مهمان (VLAN40-Guest) |
| پورت‌های access | هر دستگاه یک VLAN فقط |
| پورت trunk | بین سوئیچ و روتر (حامل همهٔ VLANها) |

## مرحلهٔ ۱: تعریف VLAN روی روتر

```routeros
/interface vlan
add name=vlan10-office vlan-id=10 interface=ether1
add name=vlan20-cctv vlan-id=20 interface=ether1
add name=vlan30-voice vlan-id=30 interface=ether1
add name=vlan40-guest vlan-id=40 interface=ether1
```

هر VLAN interface یک آدرس IP جدا می‌گیرد:

```routeros
/ip address
add address=192.168.10.1/24 interface=vlan10-office
add address=192.168.20.1/24 interface=vlan20-cctv
add address=192.168.30.1/24 interface=vlan30-voice
add address=192.168.40.1/24 interface=vlan40-guest
```

## مرحلهٔ ۲: DHCP Server برای هر VLAN

```routeros
/ip pool
add name=pool10 ranges=192.168.10.10-192.168.10.250
add name=pool20 ranges=192.168.20.10-192.168.20.250
add name=pool30 ranges=192.168.30.10-192.168.30.250
add name=pool40 ranges=192.168.40.10-192.168.40.250

/ip dhcp-server
add name=dhcp10 interface=vlan10-office address-pool=pool10
add name=dhcp20 interface=vlan20-cctv address-pool=pool20
add name=dhcp30 interface=vlan30-voice address-pool=pool30
add name=dhcp40 interface=vlan40-guest address-pool=pool40
```

## مرحلهٔ ۳: پیکربندی سوئیچ

روی سوئیچ MikroTik، پورت‌های access و trunk تعریف می‌شوند:

```routeros
/interface bridge
add name=bridge-vlan vlan-filtering=yes

/interface bridge port
add bridge=bridge-vlan interface=ether2 pvid=10  # کاربران
add bridge=bridge-vlan interface=ether3 pvid=20  # دوربین
add bridge=bridge-vlan interface=ether4 pvid=30  # تلفن
add bridge=bridge-vlan interface=ether5 pvid=40  # مهمان
add bridge=bridge-vlan interface=ether1          # trunk به روتر
```

پورت trunk (ether1) باید tagged برای همهٔ VLANها باشد:

```routeros
/interface bridge vlan
add bridge=bridge-vlan vlan-ids=10,20,30,40 tagged=ether1
```

## مرحلهٔ ۴: فایروال بین VLANها

```routeros
/ip firewall filter
# دوربین‌ها فقط به DVR دسترسی دارند
add chain=forward src-address=192.168.20.0/24 dst-address=!192.168.10.0/24 action=drop place-before=0
# مهمان فقط اینترنت
add chain=forward src-address=192.168.40.0/24 dst-address=192.168.0.0/16 action=drop place-before=1
```

## مرحلهٔ ۵: آزمون

1. از یک پورت VLAN 10، لپ‌تاپ وصل کنید → باید IP از pool10 بگیرد
2. از پورت VLAN 20، دوربین وصل کنید → باید فقط به DVR دسترسی داشته باشد
3. از پورت VLAN 40، موبایل وصل کنید → باید فقط اینترنت داشته باشد (بدون دسترسی به LAN)
4. ping بین VLANها را تست کنید → باید فقط مسیرهای مجاز کار کنند

## عیب‌یابی رایج

| نشانه | علت محتمل | راه‌حل |
|---|---|---|
| IP نمی‌گیرد | DHCP server روی VLAN interface فعال نیست | dhcp-server را چک کنید |
| پورت tagged نیست | bridge port بدون pvid درست | pvid و vlan-ids را چک کنید |
| بین VLAN ارتباط نیست | فایروال مسیر را بسته | firewall filter را بررسی کنید |
| سوئیچ حلقه می‌سازد | STP فعال نیست | `/interface bridge set bridge-vlan protocol-mode=rstp` |

## چک‌لیست تحویل

- [ ] هر پورت access فقط یک VLAN دارد
- [ ] پورت trunk همهٔ VLANهای لازم را tagged حمل می‌کند
- [ ] DHCP server روی هر VLAN interface فعال است
- [ ] فایروال بین VLANها طبق policy تنظیم شده
- [ ] فایل backup قبل از تغییر گرفته شده
- [ ] آزمون ارتباط از هر VLAN انجام شده

## منابع

- help.mikrotik.com/docs/spaces/ROS/pages/139331aba/Bridging-and-Switching
- wiki.mikrotik.com/wiki/VLANs_on_Cloud_Router_Switches
- manual.mikrotik.com (RouterOS v7 documentation)

---

## آموزش‌های مرتبط در این سری

| درس | عنوان | وضعیت |
|---|---|---|
| M1 | مقایسهٔ روترهای میکروتیک | READY_FOR_REVIEW |
| **M2** | **VLAN برای دفتر کوچک (همین درس)** | **READY_FOR_REVIEW** |
| M3 | DHCP و DNS در MikroTik | READY (تولید در نوبت بعد) |
| M4 | inter-VLAN و L3HW | READY |
| M5 | انتخاب VPN برای شعبه | READY |
| M6 | dual-WAN و failover | READY |
