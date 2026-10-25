# سرویس‌های سبک عمومی سرور تهران نتورک — ۲۰۲۶-۱۰-۲۵

**تصمیم مالک:** چند سرویس کم‌فشار روی خود سرور اجرا شود (نمونهٔ اعلام‌شده: تایم‌سرور). پیاده‌سازی زیر بدون تغییر پورت/کانتینر/سرویس‌های موجود انجام شد.

## ۱. تایم‌سرور NTP عمومی (UDP 123)

- بسته: `chrony` (سیستمی، خارج از Docker)؛ فعال و enabled.
- کانفیگ: `/etc/chrony/conf.d/tehnet-public-ntp.conf`
  - `allow 0.0.0.0/0` (سرویس عمومی) + `ratelimit interval 3 burst 8 leak 2` (محدودسازی سوءاستفاده).
- وضعیت در لحظهٔ تحویل: Stratum 3، همگام با pool اوبونتو، اختلاف ~۰ms؛ پاسخگویی از بیرون سرور تأیید شد (reply 48 bytes, roundtrip ~84ms).
- آدرس فعلی: `91.107.138.246` (پورت 123/UDP). پیشنهاد: رکورد `time.tehnet.ir` به همین IP (نیازمند دسترسی DNS مالک).

### rollback
`rm /etc/chrony/conf.d/tehnet-public-ntp.conf && systemctl restart chrony` (یا `systemctl disable --now chrony` برای حذف کامل).

## ۲. ابزارهای HTTP سبک (صفر بار back-end، فقط nginx)

- کانفیگ: `/etc/nginx/snippets/tehnet-tools.conf`، include شده در بالای `tehnet.ir.conf` (بکاپ قبل از تغییر: `/root/tehnet-backups/tehnet.ir.conf.pre-tools-20261025`).
- `https://tehnet.ir/tools/ip` → IP عمومی بازدیدکننده (پشت Cloudflare از `CF-Connecting-IP`).
- `https://tehnet.ir/tools/time` → زمان ISO-8601 سرور (جهت زمان تقریبی؛ برای زمان دقیق شبکه NTP همین سرور).
- هر دو `no-store` و `noindex` هستند و به هیچ upstream/PHP وصل نیستند.

### rollback
حذف خط include از `sites-available/tehnet.ir.conf` + `nginx -t && systemctl reload nginx`.

## عدم‌تغییرها

هیچ کانتینر، پورت موجود، پیکربندی وردپرس/آرشیو یا سرویس تونل تغییر نکرد؛ `nginx -t` قبل از reload سبز بود و اسموک سایت پس از تغییر ۲۰۰ ماند.
