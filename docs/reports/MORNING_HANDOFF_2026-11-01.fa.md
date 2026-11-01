# تحویل صبح TehNet × MyTel × SEO — ۱ نوامبر ۲۰۲۶

**LIVE_NOT_FINAL — نسخهٔ یکپارچهٔ زنده، checkpoint: 2026-11-01 07:16 تهران.** موعد نهایی ۰۸:۰۰ است. این فایل نتیجهٔ قابل‌اثبات را از کار ناتمام جدا می‌کند؛ اتمام کامل فروشگاه، امنیت، سئو یا کل دستور مالک ادعا نشده است. لاگ تاریخی در [overnight progress](../overnight-progress-2026-10-31.fa.md) حفظ شده؛ دادهٔ خام، رمز، نشانی عملیاتی و backup در Git نیستند.

## تصمیم‌های باز و امنیت

| اولویت / دامنه | وضعیت واقعی | اقدام باقی‌مانده |
|---|---|---|
| Potential P0 / رمز تاریخی | متن جاری حذف شده؛ اعتبار UNKNOWN و NOT_ROTATED | مسیر حساب، وابستگی‌ها و مجوز امن باید تأیید شود؛ ورود آزمایشی، reset یا تعویض حدسی انجام نشد. قدیمی‌بودن رمز دلیل بی‌خطری نیست. |
| P1 / مهار جاری و جلوگیری از تکرار | PRهای پاک‌سازی33/3/2 ادغام؛ guard/CI و کنترل انتشار فعال در دامنهٔ ثبت‌شده | این نتیجه با بستن رخداد یا اثبات نبود هر نوع افشا برابر نیست. |
| P2 / تاریخچه و نسخه‌های باقی‌مانده | کپی محلی تمیز، backup/restore و ref map خصوصی آزموده؛ remote purge انجام نشده | NEEDS_APPROVAL؛ force-push در غیاب مالک ممنوع. پیش‌نویس GitHub Support آماده و ارسال‌نشده است. |
| P2 / پوشش کامل اسکن فایل | اصلاح واقعی در TehNet#60، MyTel#5 و -SEO#19 ادغام شد | اسکن باید تعداد enumerated/read برابر داشته باشد؛ خطای خواندن فایل دیگر بی‌صدا رد نمی‌شود. |
| P3 / Origin و شبکهٔ مشترک | UNDETERMINED؛ مسیر خواندنی و OOB برای تغییر امن تأیید نشده | هیچ DNS/firewall/SSH/Origin یا سرویس مشترکی تغییر نکرد. backup/rollback/OOB و مجوز شرط تغییر هستند. |

جزئیات عمومی در [incident](../../security/INCIDENT_RESPONSE_2026-10-31.md)، [matrix](../../security/EXPOSURE_REMEDIATION_MATRIX.md)، [prevention](../../security/PREVENTION_CONTROLS.md) و [رویهٔ تاریخچه](../../security/HISTORY_PURGE_PLAN_2026-10-31.md) است. مقدار دقیق و گزارش خصوصی خارج Git مانده‌اند. MyTel production در تمام کارهای این شب read-only ماند؛ freeze مربوط به URL/Title/H1/performance حفظ شد.

## آنچه واقعاً روی TehNet منتشر شد

| بسته | نتیجه و مقصد | PR / source واقعی |
|---|---|---|
| فرم تیکت و B2B، زمینهٔ درخواست | nonce داخل فرم مالک؛ زمینهٔ درخواست شبکه حفظ می‌شود. ارسال واقعی فرم/سفارش/ایمیل روی production صفر. | [PR34](https://github.com/DashSaman/TehNet/pull/34)، `ac506f16f1f34d2f83fb8404eceb18f7fd54a1af` |
| آمادگی شبکهٔ VoIP و Services/Lab | [صفحهٔ خدمت](https://tehnet.ir/services/voice-network-readiness/) و [چک‌لیست دستی](https://tehnet.ir/lab/voice-network-checklist/)؛ دو صفحهٔ جدید و دو hub موجود با بلوک‌های قابل‌ویرایش. JSON، reset، چند نمونه و fallback بدون JS آزموده شدند. دادهٔ ابزار اندازه‌گیری واقعی نیست. | همان PR34؛ [رسید](../../qa/growth-2026-10-31/production-release.json) |
| سه درس موجود MTCNA | توسعهٔ [RouterOS/WinBox](https://tehnet.ir/learn/mikrotik/mtcna/routeros-winbox/)، [مسیریابی ایستا](https://tehnet.ir/learn/mikrotik/mtcna/static-routing/) و [IP/DHCP/DNS](https://tehnet.ir/learn/mikrotik/mtcna/ip-dhcp-dns/)، در همان ID/URL. مثال‌ها آموزشی و اجرا‌نشده روی شبکهٔ واقعی‌اند. | [PR37](https://github.com/DashSaman/TehNet/pull/37) `e5fd6319df95db4d45c3760106ca873989d8c8e5`؛ [PR39](https://github.com/DashSaman/TehNet/pull/39) `e2dcf87e3c20ca9919829000d239bd62e3ff3723`؛ [PR47](https://github.com/DashSaman/TehNet/pull/47) `65f0757940bb4942b2001bf81a4a0d4e9eb905b7` |
| چهار صفحهٔ خدمات موجود | [پشتیبانی شبکه](https://tehnet.ir/services/network-support-tehran/)، [راه‌اندازی شبکه](https://tehnet.ir/services/network-setup-tehran/)، [پشتیبانی ریموت](https://tehnet.ir/services/remote-support/) و [MikroTik](https://tehnet.ir/services/mikrotik-tehran/) با دامنهٔ کار، ورودی، پذیرش، محدودیت و تحویل روشن‌تر؛ همان URL/ID/عنوان/والد. | [PR43](https://github.com/DashSaman/TehNet/pull/43) `933bc33065295a018182104626ac7a7ba78bd55c`؛ [PR50](https://github.com/DashSaman/TehNet/pull/50) `420e757e7d1a78e67adfeb0f95fc253547740537`؛ [PR52](https://github.com/DashSaman/TehNet/pull/52) `d2f032f9a5532bccb92b09768d018299abba1dc0`؛ [PR54](https://github.com/DashSaman/TehNet/pull/54) `918c6c2186d5f82196471d3e0a2588661df7bef8` |
| نقش درست متادیتا | metadata0.2.2: Article نامناسب از hubهای مشخص و چهار صفحهٔ خدمات حذف شد؛ مقاله‌های واقعی درس، متن، title/H1/canonical و سایر داده‌ها حفظ شدند. صفر DB/content write برای این اصلاح. | [PR41](https://github.com/DashSaman/TehNet/pull/41)، سپس [PR56](https://github.com/DashSaman/TehNet/pull/56) `d2d081ce919c4817e7c746883b9909b6a3b3ae6f` |
| گالری محصول با کیبورد | انتخاب thumbnail با Tab/Enter/Space، label فارسی، aria-current و focus قابل‌دیدن؛ کلیک و fullscreen/Escape حفظ شدند. [نمونهٔ واقعی](https://tehnet.ir/product/tn-sn-17868/). محصولات عادی آینده همان asset مشترک محصول را می‌گیرند. | [PR58](https://github.com/DashSaman/TehNet/pull/58)، `4af1ff42ba2d427c9e7d55751b611f0a6cd4a5d4`؛ [رسید](../../qa/growth-2026-10-31/gallery-keyboard-production-release.json) |

خانه و منو حفظ شدند و فروشگاه در [‎/shop/](https://tehnet.ir/shop/) است. ۲۵ کالا همچنان **استعلامی و غیرقابل خرید** هستند؛ ERP/sandbox=false و پرداخت واقعی بسته ماند. حفظ قیمت/تصویر/وضعیت ثبت‌شده در API، تأیید قیمت یا موجودی واقعی منبع نیست. دادهٔ مشتری، سفارش و انبار برای این انتشارها جایگزین یا پاک نشد. noindex موجود TehNet عمداً حفظ شد.

## شواهد آزمون و حدود آن

هر انتشار پس از staging بومی با خروجی شبکه/ایمیل/پرداخت بسته، backup تازه، checksum، drift guard و پذیرش محدود انجام شد. rollback/repeat در staging آزموده و fixtureهای اصلی بازگردانده شدند؛ rollback اضطراری production لازم نشد. ادعای تمرین قطع برق/ازکارافتادن host وجود ندارد.

- فرم/ابزار: ۶۴ بررسی PHP، ۴ contract JS و ۲۶ بررسی مرورگر fixture؛ native acceptance و بازیابی جدا، ۸ TLS GET و ۲۵ بررسی عمومی در رسید PR34. چند نمونه، دانلود واقعی JSON و no-JS پوشش دارند؛ فرم مشتری واقعی ارسال نشد.
- سرویس‌ها: پشتیبانی شبکه ۳۷ native/۴۱ مرورگر عمومی؛ راه‌اندازی ۳۹ native/۴۴ عمومی؛ ریموت ۴۰ native/۴۴ عمومی؛ MikroTik ۴۱ native/۴۴ عمومی، همراه با regressionهای قبلی و آزمون staging جدا. این‌ها تست UI/محتوا هستند، نه اثبات SLA یا تست شبکه/دستگاه واقعی.
- متادیتای نقش خدمات: ۷ RED پیش از اصلاح، سپس ۷۴ PHP و ۱۸ native، ۳۸۶ بررسی staging و ۳۸۶ عمومی در ۵۱ حالت. مقایسهٔ مستقل ۱۷ صفحه، حذف فقط چهار Article خدمات را تأیید کرد. مجموعه‌های ۱۹ و ۱۷ درخواست عمومی همپوشان‌اند؛ آن‌ها ۳۶ URL یکتا نیستند. در staging فقط یک صفحهٔ service متأثر بود، در production چهار؛ این دو شمار خلط نشده‌اند.
- گالری: ۶ PHP، ۱۳ component و ۱۸ native checker؛ ۴۴ بررسی واقعی عمومی در desktop1440/mobile375/no-JS. ۲۰ TLS smoke، بارگذاری asset روی ۲۵ محصول و تطبیق hash دو asset پاس؛ این دو مجموعهٔ URL همپوشانی دارند. فقط یک محصول چندعکسی با کیبورد کامل آزموده شد؛ این نتیجه ممیزی ۲۵ محصول، WCAG کامل، screen reader یا دستگاه فیزیکی نیست.
- گالری پیش از انتشار با source `e4fbe5f720b916869dd23cd5f8e637b297510aee`، ۴۴ native check داشت. harness اصلاح‌شده با source `70edb33383cde3f777fd9ce2aa93c73c5bfc5e8b` پس از انتشار دوباره در native پاس شد؛ payload/tool/۱۳guard همان بودند و production دوباره منتشر نشد. دو شاهد تاریخی جدا هستند.
- آخرین CI کد گالری ۲۵ operator/۹ privacy پاس داشت. پس از اصلاح guard، هر سه ریپو ۱۲ Windows test محلی پاس کردند؛ CI Linux در هرکدام ۱۱PASS/۱SKIP صریحِ Windows-only است. TehNet همچنان ۲۵ operator پاس دارد. counts و skipها در رسیدهای هر PR ثبت‌اند.

شکست‌های واقعی محفوظ‌اند: چهار تلاش غیرqualified گالری با بازگشت دقیق، baseline موقت metadata در web SAPI، دو ناحیهٔ پیشنهاد تصادفی محصول، quote متفاوت HTML و زمان‌سنجی اسکرول؛ خطای summary wrapper بعد از PASS واقعی مرورگر؛ و هم‌پوشانی writerهای QA در بستهٔ راه‌اندازی که guard آن را متوقف کرد. بازیابی آن مورد فقط روی دادهٔ fixture متعلق به همان آزمون، با backup تازه و guard انجام شد؛ قفل writer مشترک سپس آزمایش شد. هیچ ادعای «همهٔ تلاش‌ها از اول سبز بود» نداریم. لاگ و رسیدها در `qa/growth-2026-10-31/` هستند؛ helperهای انتشار/بازیابی قبلی بازپخش نشوند.

## دامنهٔ تکمیل‌شدهٔ P2

اصلاح پوشش فایل یک یافتهٔ تازه بود: checkout عمیق ۱۵۱۳ فایل tracked داشت، اما guard قدیمی به‌دلیل مسیر طولانی Windows فقط ۱۲۷۶ را می‌خواند. RED واقعی ۹PASS/۲FAIL/۱ERROR؛ پس از اصلاح ۱۲PASS و اسکن همان checkout بدون تغییر، ۱۵۱۳/۱۵۱۳. خطای فایل خوانده‌نشده اکنون FAIL با diagnostic بدون مقدار است. [رسید پوشش](../../qa/security-2026-10-31/publication-file-coverage.json).

snapshot محلی پاک‌سازی در سه ریپو، به‌ترتیب TehNet/MyTel/-SEO، ۲۶۳۶/۱۲۰۶/۳۲۰ blob و ۲۸۳/۱۶۸/۲۳۵ commit و ۶۹/۱۲/۳۰ ref داشت؛ مقادیر شناسایی‌شده و الگوی مسیر شخصی در blob/commit/tag خروجی صفر، tree جاری main برابر اصل و backup verify/restore پاس. tests Windows هر سه ۱۲/۱۲ و guard کامل ۱۵۱۵/۵۲/۶۸ بود. این اعداد snapshot دارای source مشخص‌اند؛ ادغام بعدی آن را تاریخی می‌کند. ref map دقیق و کپی تمیز خصوصی‌اند؛ بازنویسی remote انجام نشده. تازه‌سازی خصوصی پس از آخرین ادغام عادی هنوز برای تحویل نهایی لازم است.

API سه ریپوی اصلی با pagination کامل تا PRهای ۶۰/۵/۱۹ بازبینی شد: ۱۷۸ آرشیو CI جدید با HTTP200، همراه با ۲۴ آرشیو قبلی، تمام ۲۰۲ اجرای فهرست‌شده را پوشش داد؛ هیچ exclusion حجمی/آرشیو خراب و هیچ match مقادیر شناسایی‌شده/الگوی token در این دامنه نبود. core metadata هفت ریپو هم جدا با پاسخ200 و بدون match شناخته‌شده/token بررسی شد؛ visibility تغییر نکرد. چهار ریپوی عمومی مرتبط هم جدا بررسی شدند؛ تنها MyTellPBX ref جدید داشت، ۲۸blob/۲commit/۲tag جدید و Gitleaks کل reachable history آن بدون candidate بود. سه ref map دیگر تغییر نداشتند و اسکن object بدون دلیل تکرار نشد.

در API آن چهار ریپو، ۱۴ release، دو release asset، پنج artifact و پنج CI run دیده شد؛ issue/PR/comment/fork در همان snapshot صفر بود. پنج log200 و هفت payload واقعی با ۵۴۵ عضو آرشیو/۳۱٬۵۵۰٬۷۲۳ بایت بازشده بدون اجرای فایل یا بازکردن اعضا به مسیر اصلی آن‌ها بررسی شدند؛ لایهٔ Gitleaks محتوای decoded را در یک stream ترکیب‌شدهٔ خصوصی نگه داشت. known-value/token و قواعد guard و Gitleaks تکمیلی candidate صفر داشتند. [رسید لایهٔ تکمیلی payload](../../qa/security-2026-10-31/related-payload-candidate-layers.json) و [metadata ریپوها](../../qa/security-2026-10-31/repository-core-metadata.json). این گواه نبود هر رمز ناشناخته، دادهٔ باینری/رسانه یا حساب فعال نیست. artifact ابتدا به‌دلیل Accept نامناسب 415 داد؛ درخواست مطابق [مستند رسمی GitHub](https://docs.github.com/en/rest/actions/artifacts#download-an-artifact) موفق شد. خطای تشخیص depth روی فایل عادی با بازبینی همان hashهای cache اصلاح شد؛ خطاها حذف نشده‌اند. wikiهای درخواستی قابل‌دسترسی نبودند؛ نبود محتوا نتیجه‌گیری نشد. [رسید snapshot/مرتبط](../../qa/security-2026-10-31/history-ref-refresh-2026-11-01.json) و [رسید API اصلی](../../qa/security-2026-10-31/main-api-refresh-2026-11-01.json).

## محتوا، رقابت و انتقال دانش

**مقالهٔ تازه منتشرشده در این شب: صفر؛ سه درس و چهار صفحهٔ خدمات موجود بهبود یافتند.** بستهٔ جدید ۱۰۰ موضوع منتشر نشده است. [پرتفوی](../../seo/intent-portfolio-2026-11-01.fa.md) و [CSV قابل‌ویرایش](../../seo/topic-portfolio-2026-11-01.csv) دارای ۱۰۰ کار خواننده در ۲۰ خوشه‌اند: ۳۳ کار به ۱۳ مقصد موجود، ۶۷ کار به ۱۴ گروه پیشنهادی. ۹۳ مورد فرضیه و ۷ مورد دارای سرنخ محدود جست‌وجو هستند؛ تحقیق بازار کامل یا ۱۰۰ تقاضای اثبات‌شده نیستند. validator دارای ۲۰ کنترل ساختاری است، نه crawl تازه یا اثبات یکتایی معنایی.

TehNet مالک intent زیرساخت و آمادگی شبکه؛ MyTel مالک خدمات تخصصی PBX/VoIP روی مسیرهای موجود است. [پیشنهاد برگشت contextual link در MyTel PR4](https://github.com/DashSaman/mytel.one/pull/4) فقط مستند و **NOT_DEPLOYED / NEEDS_APPROVAL** است. هیچ URL/Title/H1/performance مایتل تغییر نکرد. پیشنهاد/نامزد با انتشار حساب نشده و صفحهٔ هم‌نیت برای افزایش شمار نساختیم.

[مقایسهٔ رقبا](../../seo/competitor-services-2026-11-01.fa.md) دقیقاً سه صفحهٔ first-party از TarazNet، Parag و Varianet را در ۱۵ بُعد پوشش می‌دهد؛ self-copy آن‌ها اثبات نیروی انسانی، SLA، قیمت یا کیفیت تحویل نیست. ۹ مشاهدهٔ مرورگر: ۶ پاسخ200/۳ پاسخ403 مربوط به Parag؛ no-JS موبایل TarazNet محدودیت داشت و حالت JS متفاوت بود. ادعای بررسی ۱۲۰ سایت انجام نشده است.

منابع، پذیرش‌ها و خطاهای قابل‌انتقال تا [-SEO PR20](https://github.com/DashSaman/-SEO/pull/20) در موضوع موجود/source ledger/ادامهٔ کار ثبت شدند؛ dashboard ۱۸ مقصد و baseline تحقیق ۷۱٪ باقی ماند. baseline میزان تکمیل پژوهش است، نه امتیاز SEO سایت. ادامهٔ canonical مایتل در [PR6](https://github.com/DashSaman/mytel.one/pull/6) به‌روزرسانی شد؛ اصلاح tooling آن در PR5 است. GLM/ZAI یا provider محلی در این نوبت اجرا نشد؛ تیم/CLI بیرونی نامحدود ساخته نشد.

## فروشگاه، رسانه و قابلیت واقعی ۳D

این شب عکس، watermark، شماره فنی یا مدل دقیق محصول تغییر نکرد. بهبود نرم‌افزاری گالری مشترک است؛ مدل دقیق بازشونده یا توالی واقعی ۳۶۰ برای ۲۵ کالا تهیه/منتشر نشده است. نمایش آموزشی باید با همان برچسب آموزشی بماند. ضخامت میکرونی، اجزای داخلی، برند یا MPN از ظاهر عکس حدس زده نمی‌شود. وضعیت و موانع هر قلم در [پروندهٔ تطبیق مدل](../research/exact-product-models-2026-10-18.fa.md) و رسیدهای کاتالوگ ثبت شده‌اند؛ دسترسی عمومی یک CAD، به‌تنهایی تأیید مجوز انتشار/تطبیق قطعات همان SKU نیست.

فروش واقعی، موجودی/قیمت تهران نتورک، واحد/MOQ و نمونهٔ فاکتور/حسابداری واقعی باید با داده و پذیرش مجاز تأیید شوند. در این شب خرید یا پرداخت واقعی، آزمون حسابداری روی دادهٔ مشتری یا استقرار روی MyTel اجرا نشد؛ چنین workflowهایی تکمیل‌شده اعلام نمی‌شوند.

## صف تحویل و گام بعد

| بسته | وضعیت | شرط ادامه |
|---|---|---|
| اصلاحات سایت و محتوای هفت صفحهٔ موجود | DEPLOYED و پذیرش محدود VERIFIED | helperهای قدیمی بازپخش نشوند؛ baseline/guard هر انتشار آینده تازه شود. |
| ابزار دستی و فرم‌ها | DEPLOYED / VERIFIED در دامنهٔ رسید | ارسال production یا ادعای سنجش واقعی انجام نشود. |
| ۱۰۰ موضوع و مقایسهٔ سه رقیب | VERIFIED_INVENTORY / پژوهش گسترده IN_PROGRESS | موضوع بعدی فقط با شکاف مستقل، منبع معتبر و بهبود مقصد موجود؛ نامزد منتشرشده نیست. |
| MyTel پیشنهادهای محتوایی | VERIFIED_REPO_ONLY / NOT_DEPLOYED | freeze و تأیید مالک برای production پابرجا. |
| credential / shared history / origin | BLOCKED یا NEEDS_APPROVAL طبق matrix | elapsed time، اعلان automation یا حذف متن جای مجوز و prerequisites نیست. |
| مدل دقیق/اجزای واقعی ۲۵ کالا | BLOCKED در تطبیق/مجوز/منبع | MPN، نمونه/سند و فایل مجاز دقیق؛ مدل مشابه به نام کالای واقعی منتشر نشود. |
| P10 گزارش نهایی | IN_PROGRESS — این نسخه زنده است | نزدیک ۰۸:۰۰: read-only smoke نهایی، current main/CI/خصوصی ref snapshot پس از ادغام نهایی و جمع‌بندی واقعی؛ سپس برنامه پایان یابد. |

رتبه، ترافیک، backlink، توصیهٔ هوش مصنوعی، تبدیل، CWV میدانی، URL Inspection یا نتیجهٔ Rich Results با دادهٔ واقعی این نوبت اندازه‌گیری نشده‌اند. noindex عمداً فعال است؛ «سئو و رقابت تکمیل شد» یا «فروشگاه فروش واقعی آماده است» از خروجی حاضر نتیجه نمی‌شود. منابع قدیمی/403/آزمایشگاهی و مثال‌های ساختگی در رسیدهای خودشان محدود شده‌اند.
