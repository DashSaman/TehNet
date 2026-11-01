# اصلاح نقش صفحات خدمات در داده‌های ساختاریافته

وضعیت: VERIFIED_LOCAL_NATIVE_CHECKER_NOT_DEPLOYED. چهار صفحهٔ موجود راه‌اندازی شبکه، MikroTik، ریموت و آمادگی VoIP در بررسی ۱۷ مسیر عمومی با TLS معتبر، Article داشتند. تشخیص مستقیم ماژول با یادداشت منابع همین رفتار را بازتولید کرد؛ کش یا افزونهٔ دیگر برای وقوع آن لازم نبود. صفحهٔ پشتیبانی فعلی و دو هاب خدمات Article نداشتند، اما آزمون مسیرهای خدمات فعلی/آینده نیز از برگشت خطا جلوگیری می‌کند.

یادداشت منبع روی صفحهٔ خدمات، به‌تنهایی مقاله بودن آن را ثابت نمی‌کند. [سیاست Google دربارهٔ داده‌های ساختاریافته](https://developers.google.com/search/docs/appearance/structured-data/sd-policies) بر بازنمایی محتوای اصلی صفحه تأکید دارد؛ [راهنمای Article](https://developers.google.com/search/docs/appearance/structured-data/article) برای صفحات مقاله است. این شواهد، گزارش جریمه یا نتیجهٔ Rich Results/GSC/رتبه نیستند. noindex فعلی به دستور مالک حفظ می‌شود.

اصلاح محدود: فقط WP page با URI برابر services یا پیشوند services/ از Article کنار گذاشته می‌شود. نوشته با slug مشابه، درس مستقل و قواعد قبلی چهار collection حفظ‌اند. یادداشت، توضیح، OG، عنوان، canonical، تاریخ واقعی و محتوای قابل مشاهده دست‌نخورده‌اند؛ نوع Service یا ادعای Review/Offer ساخته نمی‌شود. هیچ صفحه یا مقالهٔ تازه‌ای ساخته نشده است.

RED واقعی: ۷ شکست از۷۴ بررسی ماژول؛ GREEN:۷۴PASS. محدودهٔ جدید ابتدا رد شد، سپس۲۴case اپراتور شامل۲۳PASS/۱SKIP مجوز symlink ویندوز و۱۸assertion بومی checker بدون DBwrite پاس شدند. تمرین immutable، مرورگر و انتشار هنوز PENDING هستند؛ رسید qa/growth-2026-10-31/service-metadata-role-draft.json مرجع این checkpoint است. خطاهای محلی آماده‌سازی با حدود اثرشان در همان رسید ثبت‌اند.

بازنویسی ID29 فعلاً انجام نمی‌شود؛ /services نقش انتخاب خدمت را دارد و ساخت هاب هم‌نیت توجیه نشده است. MyTel زنده read-only؛ rotationUNKNOWN/historyNEEDS_APPROVAL/originUNDETERMINED و منعforce-push پابرجا هستند.
