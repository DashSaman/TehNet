# مأموریت جامع SEO + GEO + AEO — Tehran Network / TehNet
**Review date:** 2026-11-11 | **Market:** Persian-speaking B2B in Tehran | **Delivery state:** RESEARCH_AND_PLANNING_PREPARED_NOT_DEPLOYED

> این بسته برای جذب درخواست خدمات معتبر طراحی شده است؛ رتبه ۱–۱۰ واقعی گوگل ایران، ترافیک/کلیک حقیقی، علت قطعی رتبه، تعداد بک‌لینک یا citation موتورهای AI اندازه‌گیری نشده‌اند. هیچ صفحه عمومی، تنظیم production یا PR دیگری تحت این شاخه منتشر یا merge نشده است.

## 01 — معرفی و روش انتخاب رقیب
- ۲۰ موضوع seed کاربر در جست‌وجوی تازهٔ چندمنبعی با برخی بازنویسی‌ها بررسی شد؛ ثبت 10 organic Google results برای **هر** query و صفحه‌های 2–5 به‌علت عدم دسترسی قابل تأیید نشد. فایل `serp-observation-20.csv` این محدودیت را آشکار می‌گذارد؛ Ads/Maps/Organic و rank گوگل نامعلوم‌اند.
- انتخاب ده شرکت بر اساس هم‌پوشانی خدمت، نمایش صفحات واقعی تهران، غنای محتوای قابل بررسی و اهمیت قیاس B2B است؛ نه رتبه عددی.
- بنچمارک‌ها: ترازنت، ایمن‌نت، رایکانت، پیراسیس، پردیس پارس، شبکه ارغوان، ایران هلپ‌دسک، آی‌تی‌خانه، واریان و پیشگام رایانه. واریان صفحه تهران دارد ولی نتیجه فیزیکیِ یافت‌شده برای کرج است؛ نسخهٔ پیشگام قدیمی است.
- جزئیات کامل A تا F و هر سایت در `competitor-dossiers-10.md` و مقایسه ۱۱ سایت در `competitor-matrix-11.csv`.
- **معیار اعتماد:** اعداد/مجوز/مشتری مندرج در صفحه رقیب، ادعای خودش است. SEO correlation ≠ causal reason for Google rank.

## 02 — ماتریس Keyword Gap و Content Gap
**۹۰ عبارت** در `keywords-90.csv`: intent، مرحله سفر، URL هدف، وضعیت، ظرفیت تجاری تخمینی کیفی، اولویت، رقیب با *محتوای مربوط* (نه SERP rank)، منبع و محدودیت. Numeric difficulty و search volume نادرست تولید نشده‌اند.

| Gap/Opportunity | Evidence | Current TehNet | Action/Gate |
|---|---|---|---|
| خدمات شبکه تهران | صفحه مادر و زیرصفحه موجود | owner29 | PR94 S1 تطبیق شود؛ URL تازه نساخت |
| راه‌اندازی/طراحی | owner33 منتشر | صفحه موجود با مثال فرضی | PR94 S2 و N1 بدون هم‌پوشانی |
| پسیو و کابل‌کشی | taraznet/raykanet/ardhavan صفحات جزئی دارند؛ در inventory صفحه منتشر مستقل TehNet نبود | فقط پوشش خدمت عمومی | page مادر فقط بعد از تأیید capability/تجهیزات/حضور |
| اکتیو | رقبای متعدد صفحه مستقل | owner35 میکروتیک و setup موجود | ابتدا وظایف/تمایز را تثبیت؛ لندینگ جدا فقط اگر distinct |
| قرارداد پشتیبانی | imennet/iranhelpdesk قرارداد/پلن | owner31؛ PR94 A1 آماده | PR94 اولویت به‌جای duplicate |
| قیمت شبکه/کابل‌کشی | رایکانت، آی‌تی‌خانه و هوم‌سرویز توضیح هزینه دارند | Draft WP287 | بررسی فنی/حقوقی + بدون قیمت ساختگی |
| تست فلوک | راهنما در پردیس و رایکانت | Draft WP288 | راهنمای تفسیر، نه ادعای مالکیت تستر |
| Case/Trust | برخی رقبا مشتری، پروژه و تصاویر عرضه کرده‌اند | case رسمی مجاز تأیید نشده | مشتری واقعی + رضایت + مدرک تست |
| AEO/GEO | پاسخ‌محور و جدول تصمیم بعضی رقبا | مفاهیم پراکنده، noindex عمدی | مستندسازی سؤال/جواب و eligibility پس از launch |

## 03 — ممیزی فنی TehNet
- `noindex,nofollow` در HTML دیده شد؛ علتِ ثبت‌شده در PR94 `blog_public=0` و callback WordPress است. این **گیت عمدی prelaunch** است. سراسری غیرفعال نشود.
- 2026-11-11 درخواست `https://tehnet.ir/wp-sitemap.xml` به 404 ختم شد. PR94 بسته allowlist16 OFF را در staging آماده دارد.
- robots.txt در 2026-11-11 بازیابی شد: User-agent * Allow:/ و Cloudflare training-bot policy. از طریق `Content-Signal` رتبه یا قابلیت AI استنباط نکنید.
- نمونه صفحه پشتیبانی canonical خودارجاع، meta description، H1 و JSON-LD LocalBusiness دارد. بررسی ۱ نوامبرِ مخزن روی مجموعه‌ای از HTMLهای عمومی دامنه این الگو را ثبت کرده بود؛ crawl کامل امروز نیست.
- آزمون آزمایشگاهی موبایل قبلی 2026-11-11: performance 88، SEO 69، LCP1.2s، CLS0.229، TBT0ms؛ **داده CrUX میدانی ندارد**. اعداد نمره رتبه گوگل نیستند.
- GSC Wizard با `payment_required` و Windsor.ai با محدودیت Free (۲ حساب/۱ مجاز) خواندن داده را رد کردند؛ no click/impression/CTR numbers.
- WPVibe site_info پاسخ داد (TehNet theme0.5.1، Core0.3.1، Store0.7.0، Woo11.2.1). سپس اتصال Free به سقف روزانه رسید؛ reset مصرف نشد.
- شواهد کامل، اطمینان و آزمایش‌های انجام‌نشده: `technical-audit.md`.

## 04 — معماری انتشار پیشنهادی (اولویت با حفظ URL)
```text
/ → /services/ → /services/network-tehran/
                      ├── /services/network-setup-tehran/ (existing)
                      ├── /services/network-support-tehran/ (existing)
                      ├── /services/mikrotik-tehran/ (existing)
                      ├── /services/remote-support/ (existing)
                      ├── /services/voice-network-readiness/ (existing)
                      ├── /services/passive-network-tehran/ (conditional NEW draft)
                      └── /services/server-virtualization-tehran/ (PR94 NEW not live)
/learn/mikrotik/mtcna/ → relevant tutorial → relevant live service (contextual only)
/lab/ → verified technical worksheet → corresponding service/guide
/network-support-contract-guide/ → PR94 A1 (not live)
/network-project-proposal-checklist/ → PR94 A2 (not live)
/business-server-planning-guide/ → PR94 A3 (not live)
/server-backup-restore-acceptance/ → PR94 A4 (not live)
```
**Policy:** هر خدمت/نیت متمایز یک preferred URL؛ چند صفحه هم‌معنی «پسیو غرب/شمال/جنوب تهران» ممنوع. Archive/Shop/Ticket/Checkout/Account طبق گیت exact16 خصوصی یا غیرقابل ایندکس بمانند.

## 05 — استراتژی Local SEO و اعتبار
NAP عمومی کنترل‌شده از AGENTS.md: «تهران نتورک / TehNet»، تلفن 021-91018746، «تهران، آیت‌الله کاشانی، شاهین جنوبی». حضور فیزیکی فقط تهران، ریموت سراسری ایران. Google Business Profile به‌طور رسمی ایران را پشتیبانی نمی‌کند؛ GBP verification را نتیجه/شرط تلقی نکنید. فقط منابع واقعی با پروفایل قابل‌ویرایش و توافق‌نامه مشتری/تأمین‌کننده.
12 گزینه white-hat در `authority-opportunities-12.csv` و توضیح پروتکل در `local-geo-aeo-authority.md`.
منابع: https://support.google.com/business/answer/6270107?hl=en و https://developers.google.com/search/docs/appearance/structured-data/local-business

## 06 — GEO/AEO
برای ۷ سؤال نمونه هزینه کابل، تفاوت اکتیو/پسیو، قرارداد پشتیبانی، شبکه ۲۰ نفره، تست فلوک، تعویض کابل و هزینه نگهداری، متن پاسخ اول کوتاه، سپس فرض/تست/منبع و جدول تصمیم. Google AI Overviews/AI Mode بدون index + snippet eligibility قابل اتکا نیستند و schema خاص AI نمی‌خواهند؛ `llms.txt` به‌تنهایی رتبه نمی‌سازد.
حضور AI با prompt/engine/geo/date/URL citation log شود؛ فعلاً UNKNOWN. منبع رسمی: https://developers.google.com/search/docs/appearance/ai-features و https://developers.google.com/search/docs/fundamentals/ai-optimization-guide

## 07 — تقویم و شواهد اصیل
۳۰ طرح در `content-calendar-30.csv` و پرونده‌های جامع شامل H2/H3، پرسش، منبع/تصویر، schema، پیوند، CTA و Quality Gate در `content-briefs-30.md`.
- WP drafts موجود و در مرحله قبل خوانده‌شده: post287 «برآورد هزینه کابل‌کشی»، post288 «تفسیر گزارش فلوک»، page289 فقط نسخه بازبینی خصوصی پشتیبانی owner31.
- PR94 از قبل 4 owner خدمات + N1 سرور + A1–A4 را آماده دارد؛ این‌ها duplicate نشوند.
- قابلیت عملی پسیو/تست فلوک/کارفرماهای واقعی تأیید نشده؛ ادعای ارائه آن‌ها یا تصویر/گواهی/Review ساختگی ممنوع.
- همه محتوا قبل انتشار نیازمند SME review و تأیید Owner است.

## 08 — اولویت و نقشه ۱۸۰ روزه
۲۸ اقدام در `roadmap-180-days.csv` با P0–P3، Owner، اثر کیفی، effort برآوردی، dependency، زمان و معیار موفقیت. نسخه توضیحی `roadmap-180-days.md`.
- P0 (0–30): بازیابی GSC، gate index و امنیت، برنامه تست/rollback.
- P1 (0–60): مسیر خرید، hub خدمات، تقویت owners، Draft پسیو مشروط، دو مطالعه موردی مجاز.
- P1/P2 (61–90): پس از تأیید release، صفحات و آموزش تصمیم خرید، ثبت lead/citation.
- P2/P3 (91–180): اعتبار واقعی، Lab asset، مقاله متخصص، بازبینی conversion و به‌روزرسانی.

## 09 — سنجش و رشد (بدون پیش‌بینی ساختگی)
KPI: web clicks/impressions/CTR/average position با فیلتر تاریخ و country؛ branded/nonbranded؛ nonbrand service page engagement؛ qualified leads؛ calls connected; quotes; contract requests; signed contracts; referring domains quality; AI citation tested.
`Qualified Leads = Valid Organic Sessions × Qualified Lead CVR` و `Signed Contracts = Qualified Leads × Quote Rate × Win Rate`. تا وقتی ورودی معتبر نداریم، ۱۸۰ روز بعد «۱۰ برابر رشد» یا هر عدد درآمد وعده داده نشود. مقایسه ۱۰ رقیب با مشاهده صفحات/حضور SERP واقعی در تاریخ‌های همسان، نه تخمین DA/DR.

## 10 — اقدامات اجراشده در این شاخه
- branch `seo/competitive-research-20261111` از main موجود، بدون تغییر runtime سایت.
- ۹۰ عبارت؛ ۲۰ query log؛ ۱۰ پرونده رقیب؛ ماتریس ۱۱ سایت؛ ۳۰ brief؛ ۱۲ فرصت authority؛ ۲۸ اقدام roadmap؛ technical audit؛ local/GEO playbook.
- WordPress روز جاریِ مأموریت قبل سه Draft ذخیره و تأیید خوانده شده بودند؛ **در این نوبت** به‌خاطر محدودیت Free تغییر تازه WordPress انجام نشده است.
- PR94 از قبل `VERIFIED_STAGING_NOT_DEPLOYED` و independent؛ merge/deploy، نصب index runtime OFF و activation exact16 هر یک تأیید مستقل می‌خواهند.
- تغییرات فعلی فقط متن/CSV است؛ نه تغییر Sitemap/robots، نه تولید secret، نه merge، نه publish، نه WAF.
- آزمایش جدید production فنی اجرا نشده؛ گزارش قبلی staging متعلق به PR94 در https://github.com/DashSaman/TehNet/pull/94 است، نه این شاخه پژوهش.

## 11 — چه چیزی هنوز صادقانه BLOCKED/NOT_DONE است؟
1. **Rank SERP exact**: 200 نتیجه ۲۰×۱۰ و صفحه ۲–۵؛ نیاز به ابزار معتبر با منطقه و دستگاه گوگل ایران و snapshot است.
2. **GSC/GA4**: داده real query/page clicks/conversions غیرقابل دریافت تا اصلاح اشتراک/اتصال؛ نبود داده صفر نیست.
3. **Competitor full technical crawl**: Core Web Vitals میدانی، backlink count، Meta در همه URLها، 404 و duplicate کلیه ۱۰ دامنه؛ ابزار و پوشش لازم موجود نبود.
4. **Real case evidence**: فقط با فایل حقیقی و اجازه کارفرما.
5. **Production deployment**: نیازمند چند گیت مستقل و rollback؛ انجام نشده است.
6. **Commercial outcomes**: هیچ لید یا قرارداد تازه به این پژوهش نسبت داده نشده.

## 12 — Definition of Done
Research dossier and actionable plan **PREPARED_FOR_REVIEW**. SERP-rank verification, quantitative performance baseline, real case approval, production gate and post-launch measurement **NOT_COMPLETE**. برای هر milestone بعدی نتیجه واقعی GSC/HTTP/Lead ثبت شود.

## 13 — خط مبنای اعتبار لینک (داده ۱۱ نوامبر ۲۰۲۶)
اتصال رایگان Ahrefs برای **نسخه DR3** و هر ۱۱ دامنه قابل خواندن بود: TehNet=0؛ ترازنت=26؛ ایمن‌نت=26؛ رایکانت=22؛ پیشگام رایانه=16؛ ایران هلپ‌دسک=10؛ پردیس پارس/واریان=9؛ پیراسیس/ارغوان=7؛ آی‌تی‌خانه=6. DR شاخص لگاریتمی ثالث برای پروفایل لینک است، نه Google Ranking، تعداد واقعی بک‌لینک یا مشروعیت کسب‌وکار. مدل DR4 در نوامبر ۲۰۲۶ به صورت preview ارائه شد؛ مقایسه تغییرات DR3 و DR4 بدون تفکیک معتبر نیست.

[فایل DR3 یازده دامنه](ahrefs-dr3-11.csv) و [روش‌شناسی و محدودیت](ahrefs-dr3-notes.md). منابع: https://ahrefs.com/seo/glossary/domain-rating و https://ahrefs.com/blog/domain-rating-dr4/ (2026-11-05).

**موانع اندازه‌گیری باقی:** Ahrefs Free دارای API units=0 است، SERP Overview برای country=ir خطای «کشور پشتیبانی‌نشده» می‌دهد. GSC Wizard به subscription فعال نیاز دارد و Windsor.ai به علت دو حساب روی پلن رایگان خواندن گزارش را نمی‌پذیرد. Google.com/search?gl=ir در ابزار وب در 2026-11-11 قابل بازیابی نبود. رتبه دقیق تهران و کلیک/ایمپرشن TehNet همچنان NOT_MEASURED هستند، نه صفر.
