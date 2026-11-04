# تمرین مفهومی Static Routing —۴نوامبر۲۰۲۶

وضعیت: **SOURCE_READY، NATIVE_NOT_RUN، NOT_DEPLOYED**. شاخهٔ مستقل `feat/conceptual-routing-lab-20261104` از head PR81 ساخته شده تا تغییرِ FeatureB، head واجد آزمون FeatureA را عوض نکند. **انتشار B به انتشار تأییدشدهٔ A وابسته است**؛ A هنوز به CI صف‌شدهٔ GitHub وابسته است و production منتشر نشده.

چهار گرهٔ فرضی رایانه/R1/R2/سرویس، آدرس‌ها و Gatewayهای مشخص، دو انتخاب مستقل برای مسیر رفت و برگشت، مقایسهٔ prefix و next-hop، نمایش مرحله‌ای بسته و بازخورد پاسخ پیاده شده‌اند. مقصد نامنطبق، next-hop خارج لینک و نبود مسیر از هم جدا هستند. یک مسیرِ صحیح، پاسخ رفت‌وبرگشت موفق محسوب نمی‌شود؛ انتخاب‌نکردن هم نتیجهٔ خرابی واقعی تولید نمی‌کند. تغییر انتخاب، نتیجهٔ قبلی را پاک می‌کند؛ reset و حرکت گام قبل/بعد محدودند.

این یک مدل محدود آموزشی است؛ RouterOS/GNS3، emulator، packet engine، روتر متصل یا خروجی واقعی Ping نیست. شبکهٔ عملیاتی یا مهارت حرفه‌ای کاربر را ارزیابی نمی‌کند. توپولوژی، پاسخ و نحو نمونهٔ آموزشی در SSR هستند؛ بدون JS، اعتبارسنجی تعاملی و حرکت بسته غیرفعال‌اند و این مرز دیده می‌شود. هیچ مقصد، رمز، ورودی آزاد، تیکت یا درخواست شبکه‌ای از کاربر نمی‌گیرد.

## فرض‌ها و منابع

روابط لینک/ARP/هاست/Gateway و routing فعال از قبل درست فرض می‌شوند. فقط مسیرهای متصل و گزینه‌های ثابت مدل هستند؛ default route، ACL، NAT، IPv6، VRF، ECMP و policy routing مدل نشده‌اند. مسیر برگشت جدا بررسی می‌شود، حتی اگر در مدلِ رفت مقصد هنوز نرسیده باشد؛ این بررسیِ فرضی، تولید پاسخ واقعی نیست.

در۴نوامبر، بخش‌های destination/RIB/connected networks/default route/route selection/nexthop lookup از [MikroTik Routing Decision](https://manual.mikrotik.com/docs/user-guides/routing-and-networking-protocols/routing-decision/) خوانده شد؛ selector7.26 مشاهده شد و نسخهٔ دستگاه مشتری نتیجه‌گیری نشد. مدل تمام رفتارهای آن مستند، RouterOS یا انتخاب مسیر پیچیده را پیاده نمی‌کند. [RFC5737](https://www.rfc-editor.org/rfc/rfc5737.html) سند Informational ژانویه۲۰۱۰ دربارهٔ بلوک‌های مستندسازی است؛ آدرس‌های مدل برای استفادهٔ عملیاتی یا ارسال روی اینترنت نیستند. مثال‌های CLI خودمان‌اند؛ اجرا یا گواهی سازنده نیستند. این‌ها به بازبینی ویدیوی دوره یا منبع تدریس‌شده نسبت داده نشده‌اند.

## دامنهٔ تغییر و شواهد تا این مرحله

یک shortcode جدید روی همان Lab7؛ دسترسی سریع به هر دو ابزار و تمام محتوای پیشین/FeatureA حفظ می‌شوند. چهار فایل component/loader، فقط post_content7 و0صفحه/فرم/backend تازه. guard جدید، سه فایل A را نیز کنترل می‌کند؛ scope قبلی A تغییر داده نشده تا qualification قبلی‌اش معتبر بماند. title/excerpt/URL/meta، Home/menu، محصولات و دادهٔ تجاری، noindex/payment/CAPTCHA و MyTel در دامنه نیستند.

منطق مدل با5آزمون و هر16جفت انتخاب، رفت‌وبرگشت مستقل، prefix عددی و next-hop بررسی شد. یک آزمون، تعبیر انتخاب‌نشده به قطع مدل را RED کرد؛ با وضعیت NEEDS_CHOICES سبز شد. مجموع9آزمون Node برای A+B موفق؛ scope جدید ابتدا RED و پس از ثبت32آزمون اجرا شد:31PASS/1SKIP Windows. native migration/renderer و مرورگر واقعی سایت هنوز NOT_RUN؛ تا آن شواهد و CI، تحویل production محسوب نشود.

گام بعد: rehearsal بومی با fixtureهای عمومیِ A و original-state restore، رندر چند نمونه و سایت desktop/tablet/mobile/light/dark/no-JS، سپس PR/CI. انتشار B تنها بعد از رسید production واقعی A و برابری bundle/backup/checksum/drift/rollback مجاز است. هیچ network/project، ranking، traffic، conversion یا parity اندازه‌گیری نشده؛ Issues63/75 و بازبینی کامل8ضبط بازند.
