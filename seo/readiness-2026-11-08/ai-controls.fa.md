# کنترل‌های AI و سنجش — بازبینی۸نوامبر۲۰۲۶
این یادداشت پیشنهاد تغییر WAF/robots یا شاهد ترافیک نیست. وضعیت کنترل حساب TehNet و گزارش واقعی آن UNKNOWN است؛ ابزار GSC خطا داد.

| موضوع | منبع رسمی | برداشت محدود |
|---|---|---|
| گزارش Generative AI مستقل | [اعلان۳ژوئن۲۰۲۶](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports)، [Help جاری](https://support.google.com/webmasters/answer/16984139?hl=en) | Google گزارش مستقل impression/page/country/device/date برای ویژگی‌های AI دارد؛ داده در گزارش کلی هم هست. «نبود گزارش جدا» در متن قدیمی AI features را مبنای امروز قرار ندهید. Help از rollout جهانی۳۱اوت و احتمال کمبود impression برای دیده‌نشدن گزارش می‌گوید. داده TehNet دریافت نشده؛ صفرِ حضور نتیجه نمی‌شود. |
| کنترل جدید Search Generative AI | [Help رسمی](https://support.google.com/webmasters/answer/16908024) | Settings→Search generative AI با Include/Exclude/Inherit و ارث‌بری parent/child وجود دارد؛ این کنترل با training و noindex عمومی یکی نیست. انتخاب مؤثر TehNet/والد/فرزند نامعلوم است؛ هیچ تنظیمی عوض نشد. |
| Google-Extended | [crawler reference](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers#google-extended) | token مستقلtraining/برخی grounding است؛ اثر مستقیم بر inclusion یا ranking Search ندارد. با کنترل جدید Search AI و Googlebot خلط نشود. |
| OpenAI | [Bots رسمی](https://developers.openai.com/api/docs/bots) | OAI-SearchBot برای Search، GPTBot برای training و ChatGPT-User برای درخواست کاربرند؛ تنظیمات مستقل‌اند و user fetch ممکن است robots را اعمال نکند. |
| Anthropic | [Help رسمی](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) | ClaudeBot برایtraining، Claude-SearchBot برایsearch و Claude-User برایuser fetch است. منع ClaudeBot به‌تنهایی منع تمام این کاربردها نیست. |
| Perplexity | [مرجع رسمی](https://docs.perplexity.ai/docs/resources/perplexity-crawlers) | PerplexityBot برایsearch و Perplexity-User برایuser request، نهtraining معرفی شده‌اند؛ user fetch عموماً robots را نادیده می‌گیرد. پیشنهاد skip گسترده WAF در صفحه، مجوز اجرای آن روی TehNet نیست. |

robots فعلی Cloudflare طبق baseline عمومی search=yes و ai-train=no و use=reference دارد؛ ai-input صریح مشاهده نشد. این signal قراردادی را به مجوز فنی همهٔ AIها یا وضعیت کنترل GSC تبدیل نکنید. در گروه‌های صریح، Google-Extended/GPTBot/ClaudeBot مسدودند؛ OAI-SearchBot/Claude-SearchBot/PerplexityBot گروه deny صریح در برداشت حاضر ندارند، ولی نبود deny صریح، دسترسی از WAF یا توصیه‌شدن را ثابت نمی‌کند. UA قابل جعل است؛ هر تصمیم شبکه پس از بررسی هویت واقعی و قواعد جاری و مجوز جدا انجام شود.

## پذیرش پایش پس از انتشار مجاز
URL Inspection و canonical منتخب، sitemap پذیرفته‌شده و index verdict را جدا ثبت کنید. برای گزارش AI، property مؤثر و کنترل inherited، بازه، timezone،dimension و metric را ثبت و missing/insufficient data را از صفر جدا کنید. گزارش Web را به گزارش AI rename نکنید؛ impression باcitation/لید/conversion یکی نیست. Bing citation فقط با ابزار دادهٔ همان دامنه سنجیده شود. هیچ گزارش حساب مایتل یا نتیجهٔ عمومی جای TehNet نیست. noindex امروز هنوز عمداً برقرار و تغییرنکرده است.
