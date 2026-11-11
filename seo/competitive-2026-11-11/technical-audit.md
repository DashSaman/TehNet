# ممیزی فنی و محتوایی TehNet — SEO/GEO/AEO
Reviewed: 2026-11-11 | Target: https://tehnet.ir | Evidence levels: OBSERVED / REPO-RECEIPT / INFERENCE / NOT-MEASURED

## مرز مشاهده
اتصال WPVibe در 2026-11-11 خواندنی پاسخ داد: theme TehNet 0.5.1، Core 0.3.1، Store 0.7.0، WooCommerce 11.2.1. در فراخوانی بعدی سهمیه روزانه WPVibe Free مصرف شد؛ **هیچ ریست، خرید، deploy یا ویرایش تازه‌ای انجام نشد.** سه Draft قبلی (دو post 287/288 و یک page 289) در همان روز پیش از اتمام سهمیه ذخیره و خوانده شده بودند. این نوبت خواندن تازه وضعیت هر سه را نتوانست تکرار کند. Source: https://tehnet.ir/ و اتصال WPVibe.

گیت پروژه با سند https://github.com/DashSaman/TehNet/blob/main/AGENTS.md و HANDOFF/PROGRESS/TASKS، ورود حضوری فقط تهران و پشتیبانی ریموت ایران را قفل می‌کند. آخرین main شناخته‌شده از بازخوانی قبلی 04c2af953b6676306b702933aecc412a76d67730 بود؛ تغییرات پس از آن باید قبل از merge دوباره چک شوند.

## مشاهدات فنی و اولویت
| مسئله/سنجش | شاهد دقیق و تاریخ | شدت/اطمینان | اقدام بی‌خطر | گیت انتشار |
|---|---|---|---|---|
| Indexability | روی صفحه /services/network-support-tehran/ meta robots=noindex,nofollow مشاهده شد (11 Nov); PR94 علت را Reading/blog_public=0 و wp_robots_noindex ثبت کرده است (8 Nov) | P0 مشروط؛ مشاهده بالا | حفظ کنترل تا آماده بودن launch؛ فعال‌سازی فقط allowlist دقیق پس از آزمون | چهار تأیید مستقل PR94 لازم |
| Sitemap | درخواست https://tehnet.ir/wp-sitemap.xml در 11 Nov به 404 ختم شد؛ PR94 نشان می‌دهد تا index OFF، این وضعیت عمدی است | P0 برای Launch، بالا | پس از تصمیم ایندکس، XML فقط URLهای مجاز را بسازد؛ exclude private | تأیید activation و GET/XML |
| robots.txt | فایل https://tehnet.ir/robots.txt در 11 Nov بازیابی شد؛ User-agent * Allow:/؛ Cloudflare Content-Signal و ممنوعیت برخی training botها مشاهده شد | P1، بالا برای متن فایل | حفظ policy؛ Google Search crawl را از Google-Extended/training جدا تحلیل کن | بدون تغییر WAF/robots تا مالک تأیید کند |
| Canonical | self-canonical در HTML نمونه صفحه پشتیبانی و 68 سند در ممیزی تاریخ 1 Nov گزارش شد | P1، متوسط | پس از launch برای 16 URL و www/non-www HTTP/HTML مستقل تست | آزمون URL کامل |
| HTTP/HTTPS | ممیزی 1 Nov: 73 درخواست؛ 68 سند HTML موفق؛ این نتیجه آزمون تاریخی است نه crawl امروز | P1، متوسط | بازاجرای بومی فقط‌خواندنی با خروجی status/redirect | بدون login و mutation |
| Title/H1/Meta | صفحه پشتیبانی title/H1 و description مرتبط، یک H1 مشاهده شد؛ هاب /services عنوان عمومی دارد؛ تمام 32 صفحه دوباره ممیزی نشده‌اند | P1، بالا برای نمونه | عنوان هاب خدمات و برچسب بخش‌ها را با intent اصلاح کن | نسبت با PR94 و owner8 |
| JSON-LD | نمونه /services/network-support-tehran/ نوع LocalBusiness با نام، تلفن، نشانی و areaServed ایران/تهران دارد؛ محتوای شواهد معتبر باید مطابق صفحه باشد | P2، متوسط | تست parse/validator با داده‌های موجود؛ از Review/Rating ساختگی اجتناب | تأیید NAP و محدوده service |
| CLS آزمایشگاهی | Lighthouse موبایل در بررسی قبلی همان روز: CLS=0.229، LCP=1.2s، TBT=0ms، Perf=88، SEO=69؛ CrUX field data نبود | P1 UX، بالا برای snapshot، پایین برای UX میدانی | آزمون ریشه جابه‌جایی فونت/تصویر/ارتفاع سپس staging remeasure | CSS scope، هیچ تغییر زنده |
| Internal links | مسیر Learn→Lab→Services وجود دارد؛ PR94 لینک‌های گسترش owner8 و صفحات تصمیم خرید را آماده دارد؛ گراف دقیق امروز کامل نیست | P1، متوسط | نگاشت hub→service→case/guide؛ no orphan; لینک به PR94 فقط بعد از انتشار | guard لینک 200 و canonical |
| Service gaps | صفحه مستقل پسیو/کابل‌کشی در inventory منتشرشده WP تا 11 Nov ثبت نشد، **نه اثبات نبود محتوای صفحه غیرمنتشر**؛ خدمت و تجهیزات باید تأیید شوند | P1 مشروط، بالا برای inventory | brief و draft آماده، بدون ادعای Fluke/project تا تأیید | SME + commercial approval |
| Assets/images | ممیزی قبلی alt و dimensions تصاویر نمونه را دید؛ کیفیت معنایی alt، مجوز عکس و تمام media بررسی نشد | P2، محدود | فقط عکس حقیقی مجاز، اندازه بهینه، alt توصیفی بدون keyword-stuff | مجوز تصویر |
| Redirects | www→apex و 301های صفحات حذف‌شده در این پاس دوباره تست نشده‌اند | P2، NOT-MEASURED | قبل از launch جدول 301/chain و alternate canonicals | read-only HEAD/GET |
| Broken links | تمام صفحات deep-crawl نشده؛ PR94 مسیرهای جدید را در fixture تست کرده ولی live نیست | P1، NOT-MEASURED برای همه | crawl مسیرهای حیاتی + 404+خارجی؛ بدون bulk redirects | تکرار بعد از هر release |
| GA4/GSC | Windsor.ai Free دو حساب متصل، read paused؛ GSC Wizard payment_required؛ هیچ عدد query/click/CTR واقعی دریافت نشد | P0 Measurement، قطعی برای محدودیت | export مستقیم از GSC یا اصلاح دسترسی connector با اقدام مالک | قبل از پیش‌بینی رشد کمی |
| Form/conversion | PR94 روی WordPress synthetic تست کرده: N1→فرم موجود→private ticket؛ ایمیل/Google CAPTCHA واقعی و production submit تست نشد | P1، receipt staging | بعد از approval تست end-to-end مجاز بدون اطلاعات مشتری واقعی | webhook/receipt/privacy |
| Analytics attribution | گزارش رویدادهای تماس و درخواست قرارداد، GA4 و CRM قابل اتکا خوانده نشده | P1، NOT-MEASURED | طرح رویدادها؛ de-duplicate lead؛ رضایت حریم خصوصی | QA واقعی و GA4 |
| Security/privacy | پروژه درباره MyTel فقط خواندنی، پرداخت و CAPTCHA با gate مستقل، 25 محصول inquiry-only ثبت دارد | P0 محافظت، repo receipt | هیچ secret/DB/customer table/credential در SEO branch نباشد | publication_guard CI |
| Google AI features | گوگل شرط indexable + snippet-eligible را لازم می‌داند و schema ویژه AI لازم نیست | P1 پس از Launch، رسمی | answer-first، منبع، مؤلف و تست؛ status AI citations unknown | اندازه‌گیری دستی با تاریخ |

## پاسخ به پرسش‌های فاز TehNet
1. «در کدام کلمات حضور دارد؟» پاسخ VERIFIED نداریم؛ از وجود صفحه هدف نمی‌توان impression استنباط کرد.
2. «Impression بالا، کلیک کم؟» GSC غیرقابل دریافت؛ فهرست UNKNOWN. جدولی با صفر تقلبی پر نشود.
3. غیبت/شکاف مشروط: صفحه پسیو و کابل‌کشی اختصاصی، خدمات اکتیو عمومی مستقل، نمونه‌کار واقعی با مجوز.
4. بهبود ضروری: /services/، /services/network-tehran/، /services/network-support-tehran/، /services/network-setup-tehran/، /services/mikrotik-tehran/؛ تغییرات چهار مورد آخر در PR94 آماده و release نشده.
5. مانع اصلی فعلی: noindex عمدی + sitemap OFF و نبود baseline داده/لید.
6. لینک داخلی پایه موجود است؛ سنجش گراف کامل انجام نشده و PR94 برای تکمیل لازم است.
7. راهنماهای موجود به تشخیص نیاز کمک می‌کنند، اما نمونه قرارداد/قیمت/مدرک واقعی ناقص یا هنوز در PR94 است.
8. دوره MTCNA و خدمات میکروتیک قابل پیوند هستند؛ از هر درس صرفاً برای SEO دکمه فروش نسازید.
9. TehNet تجربه آموزشی/لاب مستند دارد؛ رقبا نمونه پروژه/پلن/مجوز ادعایی بیشتری نمایش می‌دهند. صحت مستقل این ادعاها نامعلوم.
10. ترتیب Quick Wins: launch index eligibility (مشروط)، تسهیل درخواست، صفحه پسیو مشروط، نمونه‌کار معتبر، پیوندهای درون‌موضوعی، محتوای هزینه/قرارداد.

## شرط‌های پذیرش قبل از تغییر تولید
- PR94 در حالت draft است و merge/content OFF install/activation exact16 چهار گیت مجزای نیازمند تأیید دارند.
- قبل از هر action: reconcile PR89/90/91/93/94؛ HEAD و منبع سورس واجد تست؛ snapshot خصوصی + SHA/checksum + recovery rehearsal + diff scope + guard.
- بعد از تغییر فقط در صورت approval: GET200، self-canonical، HTML/index directives، sitemap دقیق، عدم حضور query/account/cart/checkout/ticket، mobile/no-JS، schema، CTA و rollback.
- هیچ تغییر در store/payment/CAPTCHA/MyTel/Cloudflare یا robots training؛ بدون مجوز صریح.
- «تست Stage» نه رتبه را ثابت می‌کند و نه اتصال Googlebot.

## منابع اولیه بررسی‌شده
- Google noindex: https://developers.google.com/search/docs/crawling-indexing/block-indexing
- Technical requirements: https://developers.google.com/search/docs/essentials/technical
- Google sitemap: https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview
- AI Search: https://developers.google.com/search/docs/appearance/ai-features
- GBP ایران: https://support.google.com/business/answer/6270107?hl=en
- PR94: https://github.com/DashSaman/TehNet/pull/94
- Repository technical receipt: https://github.com/DashSaman/TehNet/blob/main/seo/technical-audit-2026-11-01.fa.md
