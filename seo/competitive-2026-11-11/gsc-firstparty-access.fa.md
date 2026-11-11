# جایگزین رایگان برای اتصال مستقیم Google Search Console — TehNet
Reviewed: 2026-11-11 | State: **PROCEDURE_READY / NOT_AUTHORIZED / NO_REAL_DATA_READ**

## چرا این مسیر؟
GSC Wizard متصل با `subscription_required` از پاسخ‌گویی امتناع می‌کند. Windsor.ai Free به خاطر اتصال دو property و سقف یک property خواندن داده را متوقف کرد. Ahrefs Free صفر واحد API دارد و SERP ایران را پشتیبانی نکرد. این مانع به معنی «صفر کلیک» نیست.

**راه امن بدون سرویس اشتراکی:** استفاده از Google Search Console UI export یا دسترسی مستقیم رسمی Search Console API به property `sc-domain:tehnet.ir`. API خود Google به مجوز property و OAuth صاحب حساب نیاز دارد؛ عامل/ابزار جاری این توکن یا مجوز را در اختیار ندارد. هیچ رمز عبور یا client_secret نباید در chat، GitHub، artifact عمومی یا CI upload شود.

## راه یک: خروجی CSV با کمترین اصطکاک
در https://search.google.com/search-console/ وارد property `sc-domain:tehnet.ir` شوید؛ Performance > Search results؛ محدوده `Last 3 months` با dates دقیق ثبت شود؛ `Search type=Web`؛ هر دو برگه **Queries** و **Pages** و در صورت امکان **Devices/Countries** را Export کنید. نسخه export و date range را کنار فایل نگه دارید. CSVها به‌تنهایی هم اطلاعات first-party کافی برای محاسبه opportunity هستند؛ نام/شناسه خصوصی مشتری در خروجی عمومی Git نباید وارد شود.

- Queries: high impressions/low CTR با توجه به position و مقیاس (نه فرض CTR واحد برای همه رتبه‌ها)؛ branded/nonbranded جدا.
- Pages: تمرکز `/services/`, `/services/network-tehran/`, `/services/network-setup-tehran/`, `/services/network-support-tehran/`, `/services/mikrotik-tehran/`.
- URL Inspection برای صفحات کلیدی: index state، canonical منتخب Google، تاریخ crawl و دلیل excluded؛ وضعیت sitemap/index را فقط از فایل قابل crawl و داده Google به‌طور هم‌زمان نتیجه‌گیری کنید.
- API/CSV query rows در برخی شرایط به علت privacy filtering تمام جست‌وجوها را نشان نمی‌دهد؛ `sum(query clicks)` را به جای `site totals` اعلام نکنید.

## راه دو: Google Search Console API با OAuth فقط‌خواندنی
1. در Google Cloud project خودتان OAuth consent screen و Desktop OAuth client را ایجاد کنید (بدون scope و credential اضافی)؛ فقط `https://www.googleapis.com/auth/webmasters.readonly`.
2. OAuth client JSON را در مسیر **خصوصی خارج از Git** نگه دارید. Local InstalledAppFlow + loopback redirect؛ consent در مرورگر خود مالک انجام شود.
3. به Search Analytics endpoint POST بزنید:
   `https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Atehnet.ir/searchAnalytics/query`
4. برای date range با تاریخ دقیق از `type=web`, `dataState=final`, `dimensions=["query","page"]`, `rowLimit=25000` و `startRow=0,25000,...` استفاده کنید. همچنین درخواست **بدون dimensions** برای totals بزنید. Google نتایج query/page را به‌صورت aggregated و محدود به داده قابل مشاهده برمی‌گرداند.
5. خروجی‌ها را با private permissions در یک پوشه خارج repository نگه دارید. فقط خلاصه **غیرحساس** و بدون query محرمانه را پس از بازبینی در `seo/` commit کنید.
6. کلیدها/refresh tokens را در GitHub Actions Free runner، گزارش public branch، library report و فایل artifact عمومی قرار ندهید.

نمونه payload:
```json
{
  "startDate": "2026-08-11",
  "endDate": "2026-11-08",
  "type": "web",
  "dataState": "final",
  "dimensions": ["query", "page"],
  "rowLimit": 25000,
  "startRow": 0
}
```

**فقط نمونه ساختاری است؛ این درخواست در این مأموریت با دسترسی واقعی اجرا نشده.** برای گزارش وضعیت اول باید از وجود داده در date window مطمئن شد؛ API می‌تواند queryهای کم‌حجم/حساس را حذف کند.

## روش محاسبه فرصت (پس از دریافت داده)
- Near-page-one: queryهای خدماتی با `position` در محدوده میانی و نمایش کافی (آستانه باید با حجم مشاهده‌شده تعیین شود).
- CTR opportunity: هر query را با بازه رتبه، ویژگی SERP و device خودش مقایسه کنید؛ از جدول CTR کلی و قطعی استفاده نکنید.
- Cannibalization: چند URL هدف برای یک query/intent، بررسی canonical و تفاوت واقعی هدف صفحات.
- Lead attribution: ارسال فرم معتبر/تماس پاسخ داده‌شده/درخواست پیش‌فاکتور را جدا شمارش کنید و با CRM/سند قرارداد تطبیق دهید؛ tel-click مساوی تماس موفق نیست.
- برای سناریوی ۱۸۰روزه، تا وقتی `GSC valid_sessions`, `qualified_lead_CVR`, `proposal_rate` و `win_rate` واقعی نداریم، خروجی فقط مدل نمادین باشد، نه وعده رشد عددی.

## اعتبار منابع و تاریخ
- Google API endpoint: https://developers.google.com/webmaster-tools/v1/searchanalytics/query
- Official how-to: https://developers.google.com/webmaster-tools/v1/how-tos/search_analytics
- Installed application OAuth: https://developers.google.com/identity/protocols/oauth2/native-app
- Google data privacy, report definitions: https://support.google.com/webmasters/answer/7576553

## گیت فعلی
`NEEDS_USER_AUTHENTICATED_GSC_EXPORT_OR_OAUTH_CLIENT_PERMISSION`. هیچ خواندن حقیقی GSC/GA4، اتصال تازه، خرید/تمدید اشتراک، مصرف reset ذخیره‌شده، تغییر server/WordPress یا release انجام نشده است.
