# مجموعهٔ ۱۶۰ اسکرین‌شات واقعی WinBox — MTCNA تهنت

**تاریخ: ۴ نوامبر ۲۰۲۶.** این تصاویر از اجرای واقعی **WinBox Linux 4.5** متصل به **CHR RouterOS 7.25.1** در QEMU گرفته شدند؛ از هوش مصنوعی یا بازسازی رابط استفاده نشده است. محیط لاب به شبکهٔ خصوصیِ فقط Loopback محدود بود، با ۱ vCPU و ۵۱۲MiB RAM، بدون اتصال به سرویس‌های تولید.

**تفاوت حیاتی:** ۴ تصویر در هر پوشه به معنی ۴ مرحلهٔ تنظیمِ موفق نیست. مرحلهٔ ۳ ممکن است فرم New ذخیره‌نشده باشد و مرحلهٔ ۴ ممکن است فقط تغییر فوکوس باشد. عکس‌ها منبع اولیهٔ تدوین‌اند، نه مدرک آزمون عملی تکمیل‌شده یا مجوز انتشار عمومی.

## ممیزی کیفیت

- تعداد فایل خام واقعی: **۱۶۰ PNG**، در ۴۰ پوشه
- **۲۰ درس** دارای ۴ نمای متفاوت از ناحیهٔ اصلی WinBox هستند. سنجهٔ فنی (حذف ساعت و نوار کناری) در مجموع **۱۲۷ نمای متفاوت** از ۱۶۰ فایل را نشان داد. تفاوت پیکسل به معنای تأیید فنیِ دستورها نیست.
- درس‌های **۱۵، ۲۴، ۲۵ و ۲۶** مربوط به Wireless هستند؛ CHR رادیوی واقعی ندارد و چهار تصویر تکراری همان درس‌ها نباید به‌عنوان شواهد AP/Station استفاده شوند.
- باقی درس‌هایی که همهٔ چهار نما در آن‌ها متفاوت نیستند: ۲، ۳، ۴، ۵، ۷، ۱۳، ۱۴، ۲۷، ۲۸، ۲۹، ۳۰، ۳۱، ۳۲، ۳۳، ۳۶، ۴۰
- مجموعهٔ **[IP → Addresses با Apply واقعی](verified-ip-address-demo/)** دارای چهار مرحلهٔ جداگانه و خوانا، ورود IP آزمایشگاهی `10.77.10.1/24` روی `ether2` و ثبت نتیجه است.
- تست RouterBOOT، Netinstall یا عملکرد رادیویی واقعی از طریق CHR انجام نشده است.
- فقط در GitHub ذخیره شده‌اند؛ **هیچ بارگذاری جدیدی در رسانهٔ وردپرس یا تغییر وضعیت Scheduled/Published تأیید نشده است**.

## مشاهدهٔ ۴ تصویر هر جلسه

| جلسه | موضوع | شروع / منو | پنل | فرم یا نمای خواندنی | فوکوس/تب | نماهای متمایز |
|---:|---|---|---|---|---|---:|
| 1 | System Resources | [۱](lesson-01/01-menu.png) | [۲](lesson-01/02-panel.png) | [۳](lesson-01/03-form-or-readonly.png) | [۴](lesson-01/04-field-focus.png) | 4/4 |
| 2 | Interfaces | [۱](lesson-02/01-menu.png) | [۲](lesson-02/02-panel.png) | [۳](lesson-02/03-form-or-readonly.png) | [۴](lesson-02/04-field-focus.png) | 3/4 |
| 3 | IP Neighbors | [۱](lesson-03/01-menu.png) | [۲](lesson-03/02-panel.png) | [۳](lesson-03/03-form-or-readonly.png) | [۴](lesson-03/04-field-focus.png) | 2/4 |
| 4 | Quick Set | [۱](lesson-04/01-menu.png) | [۲](lesson-04/02-panel.png) | [۳](lesson-04/03-form-or-readonly.png) | [۴](lesson-04/04-field-focus.png) | 2/4 |
| 5 | Terminal | [۱](lesson-05/01-menu.png) | [۲](lesson-05/02-panel.png) | [۳](lesson-05/03-form-or-readonly.png) | [۴](lesson-05/04-field-focus.png) | 3/4 |
| 6 | System Users | [۱](lesson-06/01-menu.png) | [۲](lesson-06/02-panel.png) | [۳](lesson-06/03-form-or-readonly.png) | [۴](lesson-06/04-field-focus.png) | 4/4 |
| 7 | Files | [۱](lesson-07/01-menu.png) | [۲](lesson-07/02-panel.png) | [۳](lesson-07/03-form-or-readonly.png) | [۴](lesson-07/04-field-focus.png) | 3/4 |
| 8 | Reset Configuration | [۱](lesson-08/01-menu.png) | [۲](lesson-08/02-panel.png) | [۳](lesson-08/03-form-or-readonly.png) | [۴](lesson-08/04-field-focus.png) | 4/4 |
| 9 | Packages | [۱](lesson-09/01-menu.png) | [۲](lesson-09/02-panel.png) | [۳](lesson-09/03-form-or-readonly.png) | [۴](lesson-09/04-field-focus.png) | 4/4 |
| 10 | IP Address | [۱](lesson-10/01-menu.png) | [۲](lesson-10/02-panel.png) | [۳](lesson-10/03-form-or-readonly.png) | [۴](lesson-10/04-field-focus.png) | 4/4 |
| 11 | DHCP Client | [۱](lesson-11/01-menu.png) | [۲](lesson-11/02-panel.png) | [۳](lesson-11/03-form-or-readonly.png) | [۴](lesson-11/04-field-focus.png) | 4/4 |
| 12 | DHCP Server | [۱](lesson-12/01-menu.png) | [۲](lesson-12/02-panel.png) | [۳](lesson-12/03-form-or-readonly.png) | [۴](lesson-12/04-field-focus.png) | 4/4 |
| 13 | DNS | [۱](lesson-13/01-menu.png) | [۲](lesson-13/02-panel.png) | [۳](lesson-13/03-form-or-readonly.png) | [۴](lesson-13/04-field-focus.png) | 3/4 |
| 14 | Bridge | [۱](lesson-14/01-menu.png) | [۲](lesson-14/02-panel.png) | [۳](lesson-14/03-form-or-readonly.png) | [۴](lesson-14/04-field-focus.png) | 3/4 |
| 15 | Station Bridge | [۱](lesson-15/01-menu.png) | [۲](lesson-15/02-panel.png) | [۳](lesson-15/03-form-or-readonly.png) | [۴](lesson-15/04-field-focus.png) | 1/4 |
| 16 | Routes | [۱](lesson-16/01-menu.png) | [۲](lesson-16/02-panel.png) | [۳](lesson-16/03-form-or-readonly.png) | [۴](lesson-16/04-field-focus.png) | 4/4 |
| 17 | Return Route | [۱](lesson-17/01-menu.png) | [۲](lesson-17/02-panel.png) | [۳](lesson-17/03-form-or-readonly.png) | [۴](lesson-17/04-field-focus.png) | 4/4 |
| 18 | Routing Nexthops | [۱](lesson-18/01-menu.png) | [۲](lesson-18/02-panel.png) | [۳](lesson-18/03-form-or-readonly.png) | [۴](lesson-18/04-field-focus.png) | 4/4 |
| 19 | Source NAT | [۱](lesson-19/01-menu.png) | [۲](lesson-19/02-panel.png) | [۳](lesson-19/03-form-or-readonly.png) | [۴](lesson-19/04-field-focus.png) | 4/4 |
| 20 | Destination NAT | [۱](lesson-20/01-menu.png) | [۲](lesson-20/02-panel.png) | [۳](lesson-20/03-form-or-readonly.png) | [۴](lesson-20/04-field-focus.png) | 4/4 |
| 21 | Connection Tracking | [۱](lesson-21/01-menu.png) | [۲](lesson-21/02-panel.png) | [۳](lesson-21/03-form-or-readonly.png) | [۴](lesson-21/04-field-focus.png) | 4/4 |
| 22 | Firewall Filter | [۱](lesson-22/01-menu.png) | [۲](lesson-22/02-panel.png) | [۳](lesson-22/03-form-or-readonly.png) | [۴](lesson-22/04-field-focus.png) | 4/4 |
| 23 | Firewall Hardening | [۱](lesson-23/01-menu.png) | [۲](lesson-23/02-panel.png) | [۳](lesson-23/03-form-or-readonly.png) | [۴](lesson-23/04-field-focus.png) | 4/4 |
| 24 | WiFi Package | [۱](lesson-24/01-menu.png) | [۲](lesson-24/02-panel.png) | [۳](lesson-24/03-form-or-readonly.png) | [۴](lesson-24/04-field-focus.png) | 1/4 |
| 25 | Access Point | [۱](lesson-25/01-menu.png) | [۲](lesson-25/02-panel.png) | [۳](lesson-25/03-form-or-readonly.png) | [۴](lesson-25/04-field-focus.png) | 1/4 |
| 26 | WiFi Registration | [۱](lesson-26/01-menu.png) | [۲](lesson-26/02-panel.png) | [۳](lesson-26/03-form-or-readonly.png) | [۴](lesson-26/04-field-focus.png) | 1/4 |
| 27 | Simple Queue | [۱](lesson-27/01-menu.png) | [۲](lesson-27/02-panel.png) | [۳](lesson-27/03-form-or-readonly.png) | [۴](lesson-27/04-field-focus.png) | 3/4 |
| 28 | PCQ | [۱](lesson-28/01-menu.png) | [۲](lesson-28/02-panel.png) | [۳](lesson-28/03-form-or-readonly.png) | [۴](lesson-28/04-field-focus.png) | 3/4 |
| 29 | Burst/FastTrack | [۱](lesson-29/01-menu.png) | [۲](lesson-29/02-panel.png) | [۳](lesson-29/03-form-or-readonly.png) | [۴](lesson-29/04-field-focus.png) | 3/4 |
| 30 | PPP Profiles | [۱](lesson-30/01-menu.png) | [۲](lesson-30/02-panel.png) | [۳](lesson-30/03-form-or-readonly.png) | [۴](lesson-30/04-field-focus.png) | 2/4 |
| 31 | PPPoE | [۱](lesson-31/01-menu.png) | [۲](lesson-31/02-panel.png) | [۳](lesson-31/03-form-or-readonly.png) | [۴](lesson-31/04-field-focus.png) | 2/4 |
| 32 | PPP Tunnels | [۱](lesson-32/01-menu.png) | [۲](lesson-32/02-panel.png) | [۳](lesson-32/03-form-or-readonly.png) | [۴](lesson-32/04-field-focus.png) | 2/4 |
| 33 | WireGuard | [۱](lesson-33/01-menu.png) | [۲](lesson-33/02-panel.png) | [۳](lesson-33/03-form-or-readonly.png) | [۴](lesson-33/04-field-focus.png) | 3/4 |
| 34 | Ping | [۱](lesson-34/01-menu.png) | [۲](lesson-34/02-panel.png) | [۳](lesson-34/03-form-or-readonly.png) | [۴](lesson-34/04-field-focus.png) | 4/4 |
| 35 | Netwatch | [۱](lesson-35/01-menu.png) | [۲](lesson-35/02-panel.png) | [۳](lesson-35/03-form-or-readonly.png) | [۴](lesson-35/04-field-focus.png) | 4/4 |
| 36 | Files/Supout | [۱](lesson-36/01-menu.png) | [۲](lesson-36/02-panel.png) | [۳](lesson-36/03-form-or-readonly.png) | [۴](lesson-36/04-field-focus.png) | 3/4 |
| 37 | Final IP/DHCP | [۱](lesson-37/01-menu.png) | [۲](lesson-37/02-panel.png) | [۳](lesson-37/03-form-or-readonly.png) | [۴](lesson-37/04-field-focus.png) | 4/4 |
| 38 | Final Route/NAT | [۱](lesson-38/01-menu.png) | [۲](lesson-38/02-panel.png) | [۳](lesson-38/03-form-or-readonly.png) | [۴](lesson-38/04-field-focus.png) | 4/4 |
| 39 | Traceroute | [۱](lesson-39/01-menu.png) | [۲](lesson-39/02-panel.png) | [۳](lesson-39/03-form-or-readonly.png) | [۴](lesson-39/04-field-focus.png) | 4/4 |
| 40 | System Review | [۱](lesson-40/01-menu.png) | [۲](lesson-40/02-panel.png) | [۳](lesson-40/03-form-or-readonly.png) | [۴](lesson-40/04-field-focus.png) | 3/4 |

## شرایط استفاده در مقاله‌های سایت

فقط اسکرین‌شات‌هایی را منتشر کنید که با قدمِ واقعی همان درس مطابقت دارند و نسخه، تاریخ، منو، فیلدهای پرشده، نتیجهٔ مشاهده‌شده و روش بازگشت آن‌ها ثبت شده باشد. تصاویر تکراری یا بدون مرحلهٔ واقعی باید پیش از درج نهایی جایگزین شوند. در WiFi و RouterBOOT سخت‌افزار سازگار نیاز است.

**سرور:** پس از ثبت تصویر، پروسه‌های آزمایشی QEMU/Xvfb/WinBox متوقف شده‌اند؛ فایل‌های موقت فقط پس از پایداری کامل در GitHub حذف می‌شوند. شبکهٔ میزبان، Docker و وردپرس دست‌نخورده باقی مانده‌اند.

- [چک‌لیست تصاویر هر ۴۰ درس](../../../../SCREENSHOT_RUNBOOK_40.fa.md)
- [گزارش کیفیت ماشین‌خوان](quality-report.json)
