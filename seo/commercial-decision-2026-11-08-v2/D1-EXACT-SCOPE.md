# دامنهٔ دقیق D1 — استخراج از کد و bundle (۱۴ نوامبر ۲۰۲۶)

منبع: `ops/release-growth-content.py::scope_spec('tehnet-commercial-decision-20261108-v2')` + `content/commercial-decision-2026-11-08-v2/manifest.json` + payload بستهٔ d457580. این فایل خلاصهٔ پکت را با واقعیت کد تطبیق می‌دهد.

## ۱۵ فایل runtime (مالکیت release؛ rollback همه را برمی‌گرداند)
- `site/plugins/tehnet-core/includes/class-content-types.php` (جایگزین نسخهٔ live `2d3059386df1` با نسخهٔ resolver `9d4c240edd87...` — رفتار: resolver سه مسیر Lab واقعی، fail-safe برای مسیرهای غایب/تداخلی؛ آزمون رفتاری: docs/evidence/2026-11-14/baseline/lab-behavioral-20261114.json)
- ۱۲ فایل PHP کاربرگ/چاپ decision-aids زیر `mu-plugins/tehnet-technical-resources/decision-aids-20261108/` + `.htaccess` همان پوشه
- `site/themes/tehnet/assets/css/visual-refresh.css` (CSS جدول‌های scoped)

## ۵ owner موجود
| ID (production) | مسیر | تغییر |
|---|---|---|
| 8 | /services/ | فقط body |
| 29 | /services/network-tehran/ | body+title+excerpt |
| 31 | /services/network-support-tehran/ | body+title+excerpt |
| 33 | /services/network-setup-tehran/ | body+title+excerpt — **بدنهٔ reconciled ab56940e** |
| 35 | /services/mikrotik-tehran/ | body+title+excerpt |

## ۵ صفحهٔ تازه (A1-A4 مقاله + N1 خدمت)
A1 `network-support-contract-guide` · A2 `network-project-proposal-checklist` · A3 `business-server-planning-guide` · A4 `server-backup-restore-acceptance` (والد 0) · N1 `services/server-virtualization-tehran` (والد 8)

## جمع: ۱۰ صفحه (۵ اصلاح + ۵ تازه) + ۱۵ فایل runtime — با بستهٔ d457580.
## رول‌بک معکوس: حذف/برگردان ۱۵ فایل → draft کردن ۵ تازه → بازیابی body/title/excerpt/metای ۵ owner → برگرداندن ctt.php به بایت‌های hotfix (2d3059386df1، موجود در ref reconcile-baseline-7ce37e0e).
