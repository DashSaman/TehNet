# نقشه راه ۱۸۰ روزه — TehNet

Reviewed 2026-11-11. **نه برنامه زمان‌بندی اجرای خودکار است، نه تعهد تحقق رتبه/ترافیک.** زمان‌ها و ساعت‌های effort برآورد کارشناسی اولیه‌اند و بعد از ظرفیت تیم/داده اصلاح شوند. هیچ کدام مجوز انتشار ندارند.

## روز 0-30

| Priority | Owner | Action | Impact | Effort | Dependency | Success evidence |
|---|---|---|---|---|---|---|
|P0|SEO Engineer|Verify noindex producer and exact eligible URL list; do NOT change live|High|4-8h|PR94 exact16 decision + latest main|16 intended URL directives documented and owner-approved|
|P0|Analytics|Get valid 28/90d Web query/page/device/country baseline|High|2-6h|GSC access or property export|Raw report includes dates, totals, hidden share and no fabricated zeros|
|P0|DevOps|Capture scoped backup, hashes, drift and rollback checklist|High|3-8h|PR94+89/90/91/93 reconciliation|Executable checklist reviewed, no credentials or production write|
|P0|WP Developer|Review four distinct approvals: merge / content / OFF runtime / exact16 activation|High|3-6h|Owner-approved PR94 gate|Explicit owner gates all separate; no silent merge/deploy|
|P1|SEO Lead|Fix service hub title/H1 and connect appropriate existing service URLs in staged diff|High|3-5h|Inventory owner8+29+31+33+35|No duplicate targets; 200 canonical targets|
|P1|CRO Analyst|Plan and QA click→form→ticket attribution with privacy-safe IDs|High|4-8h|Current ticket form context|Valid lead definition and duplicate prevention|
|P1|Front-end|Find layout shift source in isolated responsive staging|Medium|4-8h|Lighthouse baseline CLS .229|CLS improved on consistent lab setup without broken menu|
|P1|Sales Lead|Confirm which passive, Fluke, rack and cabling work TehNet actually provides|High|2-4h|Service catalog scope|Service capability signed by accountable operator|

## روز 31-60

| Priority | Owner | Action | Impact | Effort | Dependency | Success evidence |
|---|---|---|---|---|---|---|
|P1|SEO + Network SME|Prepare one distinct passive/cabling landing as draft, no mass local pages|High|10-20h|Confirmed real passive scope|Detailed deliverables, exclusions, case evidence or explicit unavailability|
|P1|Project Manager|Create two anonymized case-study drafts|High|6-12h|Two real past projects + consent|Date/scope/photos/technical receipts consented and reviewed|
|P1|SEO Engineer|Map Services→support/setup/mikrotik and Learn→relevant services|High|3-6h|PR94 URL collision matrix|No broken or pre-publication link; crawlable contextual anchors|
|P1|Editor|Review cabling cost and Fluke report drafts with SME and primary citations|High|4-8h|Existing WP drafts 287/288 and subject review|No false price/equipment promise; ready as approved draft|
|P1|Marketing|Normalize TehNet name, public phone/address/hours across eligible profiles|Medium|4-8h|Verified public contact details|No fake location; exact NAP matches canonical source|
|P2|WP Developer|Validate Organization/LocalBusiness/Breadcrumb/Article when applicable|Medium|3-6h|Canonical URL and visible facts|JSON-LD valid and aligned with visible page; no fabricated reviews|

## روز 61-90

| Priority | Owner | Action | Impact | Effort | Dependency | Success evidence |
|---|---|---|---|---|---|---|
|P1|DevOps + Owner|After approval, execute scoped rollback-capable release and independent HTTP validation|High|6-12h|4 separate PR94 approvals + requalification|200, allowlist, private exclusions, sitemap, 0 protected changes|
|P1|Editor + SME|Publish only separately approved distinct buyer guides|High|10-20h|Approved brief/real sources|Each guide solves task and contains source/evidence + CTA|
|P1|GEO Lead|Create documented answer-first FAQ and 7-question citation test|Medium|4-8h|Indexable pages + eligible snippets|Manual citation/no-citation log with time/engine/source|
|P1|Sales Ops|Audit real inquiry/quote call disposition and lead quality|High|4-8h|Valid live lead events|Lead→qualified→proposal→signed pipeline measurable|

## روز 91-120

| Priority | Owner | Action | Impact | Effort | Dependency | Success evidence |
|---|---|---|---|---|---|---|
|P2|Partnerships|Outreach for authentic supplier/partner mention, no paid links|Medium|6-12h|Real suppliers and project approvals|At least one editorially earned relevant mention with URL|
|P2|SME + Editor|Publish evidence-based network/monitoring guides|Medium|12-20h|Lab proof and technical review|Tracked engagement and links to real service|
|P2|SEO Engineer|Fix discoverability, broken internal links, duplication after launch|Medium|4-8h|GSC and crawl export|No orphan high-priority page; important URLs 200|

## روز 121-150

| Priority | Owner | Action | Impact | Effort | Dependency | Success evidence |
|---|---|---|---|---|---|---|
|P2|Digital PR|Publish useful case/worksheet and pitch to sector publications|Medium|8-16h|Case studies consented|Editorial reference earned; no link exchange|
|P2|Analytics|Compare nonbrand service queries on matched windows|High|3-6h|60+ days settled GSC data|Observed deltas and query/page evidence not SEO plugin scores|
|P2|CRO Analyst|A/B or sequential test CTA clarity, not claims|Medium|6-10h|Enough qualified leads|Measured form completion and lead quality with caveats|

## روز 151-180

| Priority | Owner | Action | Impact | Effort | Dependency | Success evidence |
|---|---|---|---|---|---|---|
|P3|SEO Lead|No cannibalization; unique service and evidence|Medium|4 strong cases + proven demand|Expand only distinct service-intent pages justified by GSC/sales|PLANNED|
|P2|GEO Lead|Source-ref/answer quality measured, no fabricated 0 baseline|Medium|2 comparable test rounds|Repeat AI mention/citation probes with 7 prompts and logged conditions|PLANNED|
|P2|Owner + Sales|Decision on next content/tech work based on business outcomes|High|90+ days leads and proposals|Calculate qualified lead→proposal→deal conversion and ROI|PLANNED|
|P3|Editorial|Every dated claim has source and reviewer|Medium|Freshness/price review schedule|Review prices, dates, outdated tool references and technical versions|PLANNED|

## قانون اولویت
- P0 = پیش‌شرط انتشار/اندازه‌گیری/امنیت. noindex عمدی، حذف کورکورانه مجاز نیست.
- P1 = تبدیل مشتری و ساختار صفحات اصلی.
- P2 = توسعه محتوای متخصص، اعتبار و UX بعد از خط مبنا.
- P3 = گسترش تنها با تقاضا و شواهد.

## معیارهای تجاری
Organic web clicks و impressions و CTR و weighted average position (از GSC در دوره مشخص و source)؛ non-branded by regex؛ qualified leads، quoted opportunities، signed contracts؛ telephone click با تماس موفق یکسان نیست. Track event id، consent، de-duplication و ثبت منبع. هر تغییر را به cohort هم‌زمان و صفحه هدف متصل کن؛ اثر مستقیم رتبه تضمین نمی‌شود.

## سناریوی رشد به شکل مدل، نه پیش‌بینی ساختگی
با نبود GSC و نرخ تبدیل واقعی، سناریوی عددی معتبری برای ۱۸۰ روز نداریم. پس از دسترسی به داده، سه فرض محافظه‌کارانه/پایه/خوش‌بینانه در ابزار محاسبه می‌شوند: Qualified Leads = Valid Organic Sessions × Qualified Lead CVR؛ Signed Deals = Qualified Leads × Proposal Rate × Win Rate. هر ورودی باید با تاریخ، حجم نمونه و بازه اطمینان ثبت شود. نمونه محاسباتی را به عنوان عملکرد TehNet گزارش نکنید.
