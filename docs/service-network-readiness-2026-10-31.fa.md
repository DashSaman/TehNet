# مسیر درخواست شبکه و ابزار آمادگی —۳۱اکتبر۲۰۲۶

وضعیت: **کد و دو صفحه در preview خصوصی پذیرفته شده‌اند؛ production تغییر نکرده است.** شاخه `feat/tehnet-mytel-seo-20261031` و [PR34](https://github.com/DashSaman/TehNet/pull/34) محل بازبینی‌اند.

Checkpoint تازه‌تر: [پذیرش editor و آمادگی release](editor-release-acceptance-2026-10-31.fa.md). مرور کامل desktop/mobile و۵۶ بلوک معتبر گوتنبرگ با edit/reset بدون ذخیره تأیید شدند؛ دادهٔ قبلی بعد از cleanup ثابت ماند. preflight خواندنی live برای۶فایل/۲hub/path نیز پاس شد. بندهای پایین سابقهٔ آزمون پیشین را نگه می‌دارند؛ migration/release production هنوز انجام نشده است.

## تغییر قابل استفاده

- nonce تیکت و B2B داخل HTML بازگشتی همان form قرار می‌گیرد. اعتبارسنجی، throttle و private بودن رکوردها حفظ شده‌اند.
- لینک درخواست `/support/?tn_service_context=voice-network` فقط context مشخص شبکه را می‌پذیرد و موضوع قابل‌ویرایش پیشنهاد می‌دهد. کلید قبلیِ آزمایشی `tn_service` با query variable نوع محتوای خدمات تداخل داشت و در وردپرس404 می‌داد؛ کنار گذاشته شد. نوع محتوا/URLهای موجود تغییر نکردند.
- `[tn_voice_network_readiness]` ابزار۸پرسشی دستی با حالت نامعلوم/مدرک/نیاز به اصلاح/بدون کاربرد، summary، reset، JSON محلی، چند نمونه مستقل و fallback بدونJS است. اندازه‌گیری، امتیاز یا تأیید مهندسی تولید نمی‌کند؛ چیزی ارسال یا ذخیره نمی‌کند.
- دو صفحهٔ ویرایش‌پذیر در `content/growth-2026-10-31/`: `/services/voice-network-readiness/` و `/lab/voice-network-checklist/`. دامنهٔ شبکه از نصب PBX/داخلی/IVR مایتل جداست؛ قیمت/SLA یا رابطهٔ حقوقی ساخته نشده است. Services/Lab در clone فقط append شده‌اند؛ خانه و منو تغییر نکردند.

## شواهد و محدودیت

رسیدها در `qa/growth-2026-10-31/` هستند:۶۴ assertion PHP،۴ assertion وضعیتJS،۲۶ بررسی مؤلفهٔ مرورگر و۲۴ بررسی native. native شامل200، یکH1، canonical، noindex، enqueued assets، دانلود و نبود overflow موبایل، nonce داخل FormData و POST واقعی مصنوعی است. backend دو تیکت و یک پیش‌فاکتور private، context صحیح/رد آرایه و مقدار2.5 را تأیید کرد؛ nonce نامعتبر رکوردی نساخت. هر۳ رکورد مصنوعی حذف و hash رکوردهای قبلی ثابت ماند. SMTP/HTTP بیرونی/پرداخت/cron در clone مسدود بودند؛ هیچ مشتری/سفارش/پرداخت/ERP/مایتل واقعی در آزمون درگیر نشد.

preview پیشین Store0.4.0 بود؛ هویت/شبکهٔ internal/guardها بررسی و پیش از sync محدود، SQL و فایل‌ها در محل خصوصی backup شدند.۴۱ فایل allowlist و۲۰ PHP lint شد. hash خانه/منو/محصولات و isolation ثابت ماند.۲ صفحه ساخته و۲ hub append شد؛۴۱ بلوک parse/serialize شد و repeat بدون تغییر بود. پس از اصلاح query، فقط۲ body با hash قبلیِ موردانتظار به‌روز و repeat دوباره صفر شد. این آزمون، بازبینی کامل editor گوتنبرگ نیست.

شکست‌ها پنهان نشده‌اند: آزمایش اولیهٔ native به404 ناشی از query برخورد کرد؛ regression محلی۱۹check/۳FAIL علیه نسخهٔ قبلی و پس از اصلاح۱۹/۰ شد. helper journal ابتدا مسیر host را در container به‌کار می‌برد و نبود کنترل خطا باعث شد آن journal قابل اتکا نباشد؛ backup کاملِ پیش از stage محفوظ بود. مسیر خصوصیِ container/host، کنترل خطا و تأیید کپی اصلاح شد. بازنویسی تاریخچه و Origin/credentialهای باز از این نتیجه بسته نمی‌شوند.

## اجرای دوباره و گام بعد

تست محلی با PHP دارایmbstring: `php tests/service-intake-contract.php`، `php tests/network-readiness-unit.php` و suiteهای ticket/quote/technical-resources. آزمون مؤلفه با `PHP_BINARY` و Playwright موجود در `NODE_PATH`: `node tests/network-readiness-browser.cjs`. تست native به تأیید مستقل isolation، URL فقطloopback و run marker مصنوعی نیاز دارد؛ اجرای آن روی tunnel تولید مجاز نیست. orchestrator خصوصی، identity/egress را قبل از POST چک و فقط رکوردهای همان marker را cleanup کرد. محل دقیق/backup/forward در تنظیمات و checkpoint خصوصی‌اند و در Git نمی‌آیند.

هر۵ لینک داخلیِ متمایزِ دو body در clone با GET ناشناس200 دادند؛ رسید `internal-links.json` است. قبل از production: full-page visual/editor review، مقایسهٔ تازهٔ file/body با live و main، backup کاملِ تازه و checksum/restore، migration idempotent با journal و rollback محافظت‌شده، سپس release محدود در مجوز موجود و smoke واقعی. فقط همین دو class و MU/module/content لازم بررسی شوند؛ sync چهل‌ویک‌فایلیِ preview مجوز sync کامل به تولید نیست. noindex،۲۵ inquiry-only، MyTel freeze و پرداخت/ERP حفظ شوند.۱۰۰موضوع، batch مقالات، معیارهای رقبا و مدل دقیق۲۵کالا همچنان برنامهٔ ناتمام‌اند؛ تعداد draft، انتشار زنده نیست.

شناسهٔ صفحات جدیدِ receipt مربوط به clone است؛ در تولید همان ID می‌تواند متعلق به B2B یا صفحهٔ دیگری باشد. new page را با parent/path، marker و body guard ایجاد/پیدا کنید و ID خروجی همان محیط را در journal بگیرید؛ ID193/194 آزمایش را روی live به‌کار نبرید. helperهای خصوصی نیز snapshot دارند؛ قبل از اجرای دوباره، هویت/فایل/body را تازه بررسی کنید.
