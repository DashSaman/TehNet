# DHCP و DNS در MikroTik — راهنمای پیکربندی و عیب‌یابی (M3)

> آموزش تصویری از سری MikroTik و routing؛ مخاطب: کارشناس شبکهٔ مبتدی.
> سناریوی فرضی آموزشی با دادهٔ ساختگی؛ بدون دستکاری شبکهٔ واقعی.

## پاسخ کوتاه

DHCP Server در MikroTik آدرس IP به دستگاه‌ها می‌دهد (pool + gateway + DNS) و DNS Cache سرعت حل نام را بالا می‌برد. اگر دستگاه IP نمی‌گیرد، ترتیب بررسی: lease فعال؟ pool خالی؟ interface درست؟ فایروال مسیر DHCP را باز؟

## پیش‌نیازها

- روتر MikroTik با RouterOS
- دسترسی WinBox یا SSH
- حداقل یک interface فعال با IP

## پیکربندی DHCP Server

### گام ۱: تعریف pool آدرس

```routeros
/ip pool
add name=lan-pool ranges=192.168.88.10-192.168.88.254
```

### گام ۲: تعریف DHCP Server

```routeros
/ip dhcp-server
add name=lan-dhcp interface=ether2 address-pool=lan-pool lease-time=8h disabled=no
```

### گام ۳: شبکه و gateway

```routeros
/ip dhcp-server network
add address=192.168.88.0/24 gateway=192.168.88.1 dns-server=192.168.88.1
```

### گام ۴: Static Lease برای دستگاه‌های مهم

```routeros
/ip dhcp-server lease
add address=192.168.88.10 mac-address=AA:BB:CC:DD:EE:01 server=lan-dhcp comment="NAS"
add address=192.168.88.11 mac-address=AA:BB:CC:DD:EE:02 server=lan-dhcp comment="Printer"
```

## پیکربندی DNS

### DNS Cache به‌عنوان forwarder

```routeros
/ip dns
set servers=8.8.8.8,1.1.1.1 allow-remote-requests=yes
```

### Static DNS entries برای سرویس‌های داخلی

```routeros
/ip dns static
add name=nas.lan address=192.168.88.10
add name=printer.lan address=192.168.88.11
add name=router.lan address=192.168.88.1
```

## عیب‌یابی DHCP

| نشانه | علت محتمل | دستور بررسی | راه‌حل |
|---|---|---|---|
| IP نمی‌گیرد | DHCP server disabled | `/ip dhcp-server print` | disabled=no |
| IP می‌گیرد ولی gateway ندارد | network بدون gateway | `/ip dhcp-server network print` | gateway را اضافه کنید |
| IP conflict می‌دهد | pool و static overlap | `/ip dhcp-server lease print` | static خارج از pool |
| lease منقضی سریع | lease-time کوتاه | `/ip dhcp-server print` | lease-time را افزایش دهید |
| DNS resolve نمی‌شود | dns-server اشتباه | `/ip dns print` | dns-server درست تنظیم شود |

## دستورهای عیب‌یابی

```routeros
# مشاهدهٔ leaseهای فعال
/ip dhcp-server lease print

# بررسی آمار DHCP
/ip dhcp-server print stats

# لاگ DHCP
/log print where message~"dhcp"

# تست DNS از طرف روتر
/put [:resolve www.google.com]
```

## چک‌لیست تحویل

- [ ] pool آدرس خارج از range روتر و بدون overlap با static
- [ ] DHCP server روی interface درست فعال
- [ ] network با gateway و DNS درست
- [ ] static lease برای دستگاه‌های مهم
- [ ] DNS cache فعال (allow-remote-requests)
- [ ] فایروال UDP 67/68 را مسدود نکرده

## آموزش‌های مرتبط در این سری

| درس | عنوان | وضعیت |
|---|---|---|
| M1 | مقایسهٔ روترهای میکروتیک | READY_FOR_REVIEW |
| M2 | VLAN برای دفتر کوچک | READY_FOR_REVIEW |
| **M3** | **DHCP و DNS در MikroTik (همین درس)** | **READY_FOR_REVIEW** |
| M4 | inter-VLAN و L3HW | READY |
| M5 | انتخاب VPN برای شعبه | READY |
| M6 | dual-WAN و failover | READY |
