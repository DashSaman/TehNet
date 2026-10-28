# سرویس زمان عمومی TehNet — time.tehnet.ir

سرویس NTP عمومی و کم‌فشار روی سرور اصلی (مالک ۲۰۲۶-۱۰-۲۵ رکورد DNS را ۲۰۲۶-۱۰-۲۸ فعال کرد).

## وضعیت (۲۰۲۶-۱۰-۲۸)
- `time.tehnet.ir` → A → `91.107.138.246` (DNS only، بدون پراکسی Cloudflare — NTP از UDP مستقیم عبور می‌کند)
- UDP 123 باز و پاسخ‌گو؛ تست بیرونی موفق (stratum 3-4، آفست سرور ~0.4ms)
- IPv6: سرور آدرس جهانی `2a01:4f8:c010:1bac::1` دارد و `allow ::/0` فعال است؛ تا زمان افزودن رکورد AAAA توسط مالک، کلاینت‌های IPv6 از نام دامنه استفاده نمی‌کنند (اختیاری: AAAA → همان آدرس، DNS only)

## فایل‌های پیکربندی (روی سرور)
- `/etc/chrony/conf.d/tehnet-public-ntp.conf` — سرویس عمومی: `allow 0.0.0.0/0` + `allow ::/0` + `ratelimit interval 3 burst 8 leak 2` (ضد تقویت/acknowledgmentabus)
- `/etc/chrony/sources.d/iran-ntp.sources` — `pool ir.pool.ntp.org iburst maxsources 2` (تأیید دسترسی ۱۰۹ms؛ a.nic.ir و time.ir از هتزنر فیلتر بودند)
- منابع پایه: پول‌های رسمی اوبونتو (maxsources محدود)

## مانیتورینگ
- `mytel-health.timer` هر ۵ دقیقه `/opt/tehnet/ops/health.sh` را اجرا و `/tools/status` را بازنویسی می‌کند
- فیلدهای جدید: `ntp` (ok/fail)، `ntp_stratum`، `ntp_offset_ms`
- `/tools/time` زمان HTTP + فیلد `ntp_host` برای کشف‌پذیری

## راهنمای کلاینت
- ویندوز (Admin):
  ```
  w32tm /config /manualpeerlist:time.tehnet.ir /syncfromflags:manual /update
  w32tm /resync
  ```
- لینوکس (chrony): `server time.tehnet.ir iburst` در `/etc/chrony/chrony.conf` یا `/etc/chrony/sources.d/tehnet.sources`
- systemd-timesyncd: `NTP=time.tehnet.ir` در `/etc/systemd/timesyncd.conf`
- روترها/سوئیچ‌ها: همان نام میزبان روی UDP 123

## عملیات
- ری‌استارت: `systemctl restart chrony` (سریع؛ resync با iburst در ثانیه‌ها)
- بارگذاری منابع بدون قطعی: `chronyc reload sources`
- آمار سرویس: `chronyc serverstats` — ردیابی: `chronyc tracking`
- اسکریپت پایش نباید بایت کنترلی خام داشته باشد (bash بایت NUL را حذف می‌کند) — از `bytes([27])+47*bytes([0])` استفاده کنید
