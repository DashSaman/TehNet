# درس قابل انتقال: آموزش تصویریِ مبتنی بر لاب و مرز شواهد
Reviewed: 2026-11-08
Status: READY_FOR_CENTRAL_REVIEW — فقط در شاخهٔ لاب TehNet؛ هنوز به main مرجع -SEO منتقل نشده است.

مرجع عملیاتی: [قرارداد -SEO](https://github.com/DashSaman/-SEO/blob/main/AGENTS.md)، [فصل رسانه](https://github.com/DashSaman/-SEO/blob/main/docs/media-seo.md)، [PR27 قبلی](https://github.com/DashSaman/-SEO/pull/27).
استثنای اسکن خصوصی فقط شاخهٔ `lab/cloud-queue-20261108` است؛ این بسته مجوز commit/merge در -SEO نیست. درصد baseline و شمارش dashboard مرکزی تغییر نکرده‌اند.

## منابع و دامنهٔ ادعا
| شناسه | طبقه / وضعیت | منبعِ بازبینی‌شده در ۸ نوامبر | برداشت و محدودیت |
|---|---|---|---|
| Q-CONTENT-01 | FACT-OFFICIAL / VERIFIED | [Google: people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) | اطلاعات و تجربهٔ اصیل، منابع روشن و ارزش افزوده به کاربر کمک می‌کنند؛ این راهنما فرمول تضمین رتبه نیست. |
| Q-IMAGE-01 | FACT-OFFICIAL / VERIFIED | [Google: image SEO](https://developers.google.com/search/docs/appearance/google-images) | تصویر اصلی با `img src` قابل کشف باشد؛ کادر کلیک CSS مکمل تصویر است. responsive، alt توصیفی و کیفیت/حجم باید بررسی شوند. |
| Q-VIDEO-01 | FACT-OFFICIAL / VERIFIED | [Google: video SEO](https://developers.google.com/search/docs/appearance/video) | احراز ویژگی‌های ویدیو به ویدیوی واقعی و الزامات صفحهٔ آن وابسته است. سناریوی ضبط، screenshot یا thumbnail به‌تنهایی ویدیو یا شاهد index شدن نیست. |
| Q-LAB-01 | OBSERVED / VERIFIED | [لاب واقعی Queue](https://github.com/DashSaman/TehNet/actions/runs/42483186544)، [رسید](../../docs/evidence/2026-11-08/cloud-queue/lab-verification.json) | ۱۲ فریم واقعی WinBox4.5/CHR7.25.1؛ قانون از GUI، Toggle و حذف محدود آزموده شد. نتیجه به همین سناریو محدود است. |
| Q-STAGE-01 | OBSERVED / SYNTHETIC_FIXTURE | [رسید staging](../../docs/evidence/2026-11-08/cloud-queue/native-staging.json) | رندر و انتشار برگشت‌پذیرِ یک بدنه روی fixture ساختگی؛ نسخه‌ها و حدود دقیق در همان رسید. این آزمایش شاهد سایت زنده، گردش فروش یا رشد جست‌وجو نیست. |

## روش قابل استفادهٔ مجدد
1. صفحهٔ موجود با همان intent را تقویت کنید؛ برای همان آموزش صفحهٔ هم‌نیت جدید نسازید. URL/title/excerpt/meta فقط با دامنهٔ تأییدشده تغییر کنند.
2. نسخهٔ ابزار، توپولوژی، پیش‌شرط، مسیر کلیک، نتیجهٔ قابل مشاهده و برگشت امن را کنار تصویر واقعی بنویسید. تصویر تولیدی یا عکس مفهومی را UI واقعی جا نزنید.
3. PNG اصلی را با hash حفظ کنید. کادر نمایشیِ درصدی روی همان تصویر و لینک اصلِ تمام‌اندازه را جدا آزمون کنید؛ گزینهٔ کلیک در متن هم پررنگ باشد تا آموزش به رنگ/کادر وابسته نباشد.
4. قبل/فعال/غیرفعال/دوباره‌فعال را با بار یکسان بسنجید. در این لاب missing reply در ping با Dropped صف یکی نبود؛ Bytes یا RTT جای نرخ مستقل دریافت یا ظرفیت سخت‌افزار را نمی‌گیرد.
5. مدرک لاب، مدرک staging، مجوز merge، backup/drift/recovery، مدرک production و پیامد SEO وضعیت‌های جدا هستند. CI یا تعداد check را به انتشار یا parity تبدیل نکنید.
6. ضبط ویدیو، زمان واقعی، بازبینی تدوین و هماهنگی با فیلم موجود را مستقل نگه دارید. برای Queue سناریوی هدف۶دقیقه موجود است؛ ضبط تازه۰ و زمان واقعی/تأیید null هستند.
7. رندر RTL موبایل، بدون JS، اصل عکس، bytes سرو‌شده، alt، canonical/noindex و نبود ارسال فرم را واقعاً بررسی کنید. noindex عمدی با هدف «بهبود سئو» خودکار برداشته نشود.
8. fixture شامل همان افزونه‌های فعال باشد؛ دادهٔ واقعی برای این کار لازم نیست. فعال‌بودن WooCommerce در production از خواندن مجاز connector مشاهده شد؛ fixture اولیه بدون آن، معادل production شمرده نشد.

## مدرک قبل/بعد و محدودیت نتیجه
[نمای پیش از افزودن راهنما](../../docs/evidence/2026-11-08/cloud-queue/staging/before-67-375-light.png) در ابتدای نوشته است؛ [نمای پس از افزودن بخش](../../docs/evidence/2026-11-08/cloud-queue/staging/after-67-375-light.png) در لنگر بخش تازه است. موقعیت scroll یکسان نیست و مقایسهٔ pixel-diff ادعا نمی‌شود. [کادر کلیک روی موبایل](../../docs/evidence/2026-11-08/cloud-queue/staging/callout-67-375-light.png) شاهد UI همان fixture است.

هیچ اندازه‌گیری GSC، رتبه، ترافیک، conversion یا پیشنهادشدن توسط AI برای این تغییر وجود ندارد. noindex عمدی حفظ شده؛ نتیجهٔ فعلی به کیفیت محتوا و آزمون فنی محدود است. انتقال به -SEO نیازمند گیت همان مخزن و به‌روزرسانی منابع/خروجی/هماهنگی آن است.
