# بستهٔ تولید ویدیوی آموزشی تهران نتورک

درخواست مالک۴نوامبر۲۰۲۶: لحن، نحوهٔ آموزش، تصویر/گزینهٔ کلیک و زمان‌بندی هر قسمت جداگانه در ریپو نگهداری شود.

این پوشه شامل **۹ سناریوی پیشنهادی ضبط تازه** است:۸ردیف پیگیری آرشیو (۷قسمت MTCNA با۵٫۵ + GNS3)، به‌علاوهٔ ویدیوی پایلوت راهنمای مصور مرورگری. این‌ها transcript، فصل تأییدشده یا زمان واقعی ضبط‌های قدیمی نیستند. دربارهٔ۵٫۵ منبع متن در دسترس نبود؛ Bridge صرفاً پیشنهاد مستقل ضبط تازه است. Queue راهنمای نوشتاری مستقل می‌ماند و در هیچ سناریویی درس جامعِ ضبط قدیمی حساب نشده است.

هر فایل لحن ویژه،۸نما، حرکت روی صفحه، گزینهٔ برجسته، متن پیشنهادی گوینده، زمان هدف، مکث‌ها و گیتِ اجرای فنی/ویرایش دارد. [manifest](manifest.json) زمان واقعی/بازبین/approval را تا انجام واقعی null نگه می‌دارد. ویدیوی جدید ساخته نشده است. برای WinBox، نبود Docker daemon محلی و نداشتن لاب نسخه‌ثبت‌شده هنوز مانع capture واقعی است؛ هیچ تغییری به شبکهٔ مشترک داده نشد.

| فایل | موضوع |
|---|---|
| [01-routeros-overview](01-routeros-overview.fa.md) | RouterOS، معماری و انتخاب ابزار مدیریت |
| [02-first-access-safe-mode](02-first-access-safe-mode.fa.md) | اولین اتصال و یک تغییر کوچک قابل بازگشت |
| [03-addressing-package-management](03-addressing-package-management.fa.md) | آدرس‌دهی و مدیریت نسخه؛ دو تمرین جدا |
| [04-backup-export-recovery](04-backup-export-recovery.fa.md) | Backup و Export؛ فایل داشتن با بازیابی موفق فرق دارد |
| [05-dhcp-client-server](05-dhcp-client-server.fa.md) | DHCP Client، Server و انتخاب Offer |
| [05b-bridge-proposal](05b-bridge-proposal.fa.md) | پیشنهاد قسمت تازه: Bridge و مرز Broadcast |
| [06-dhcp-snooping-arp](06-dhcp-snooping-arp.fa.md) | DHCP Snooping، Alert و فرق ARP با جدول MAC |
| [07-gns3-environment](07-gns3-environment.fa.md) | ساخت محیط تمرین GNS3 و CHR با منبع مجاز |
| [08-browser-routing-pilot](08-browser-routing-pilot.fa.md) | ویدیوی پیشنهادی راهنمای تصویری مسیر رفت و برگشت |

ترتیب پیشنهادی تولید: پایلوت مرورگری با تصاویر موجود؛ سپس GNS3/لاب مجاز و نسخه‌ثبت‌شده؛ سپس اولین اتصال و بقیهٔ مباحث. نسخهٔ واقعی RouterOS/WinBox با شمارهٔ بالای صفحهٔ مستندات یکسان فرض نشود. برای تطبیق با ضبط‌های قبلی، ledger بازبینی `seo/mtcna-video-evidence-2026-11-04.json` مرجع جداگانه است.
