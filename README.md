# TehNet | تهران نتورک

برای ادامهٔ کار ایجنت‌ها: [راهنمای جامع تحویل و نقشهٔ شواهد](docs/agent-continuation.fa.md). تدوین ۲۵ اکتبر ۲۰۲۶؛ وضعیت زنده را از تاریخ آخرین رسید تفکیک کنید.

## فارسی

TehNet (`tehnet.ir`) پلتفرم تخصصی شبکه با چهار مسیر اصلی کسب‌وکار است:

- **Learn / آموزش** — آموزش‌های رایگان و دوره‌ها
- **Lab / لاب** — اسکریپت، کانفیگ، دیاگرام و سناریوهای عملی
- **Services / خدمات** — خدمات شبکه حضوری تهران و پشتیبانی ریموت سراسر ایران
- **Shop / فروشگاه** — تجهیزات شبکه، محصولات دیجیتال و جریان استعلام/خرید

### وضعیت پروژه

این مخزن منبع اصلی و رسمی TehNet برای محصول، پیاده‌سازی، عملیات، SEO و استقرار است. توسعه روی feature branch انجام می‌شود و فقط بعد از تست و تأیید به `main` ادغام می‌شود.

### محیط Production

- دامنه: `tehnet.ir`
- نشانی Origin و اطلاعات دسترسی فقط در تنظیمات خصوصی اپراتور نگهداری می‌شوند.
- CDN/DNS: Cloudflare
- میزبان canonical: `https://tehnet.ir`
- `www.tehnet.ir` باید به دامنه اصلی redirect دائمی شود.

### ساختار مخزن

- `docs/` — طراحی، معماری و implementation planها
- `ops/` — نصب، deploy، backup، recovery و شواهد production
- `site/` — قالب و پلاگین‌های اختصاصی WordPress
- `seo/` — تحقیق و معماری SEO مخصوص TehNet
- `content/` — محتوای سایت و mapping ویدیوها
- `HANDOFF.md` / `PROGRESS.md` / `TASKS.md` — وضعیت جاری، ادامه کار و backlog

## English

TehNet (`tehnet.ir`) is a Persian networking platform with four core business journeys:

- **Learn** — free tutorials and courses
- **Lab** — scripts, configs, diagrams and hands-on scenarios
- **Services** — on-site networking services in Tehran and nationwide remote support
- **Shop** — networking equipment, digital products, and inquiry/purchase flows

### Project status

This repository is the canonical source of truth for TehNet product, implementation, operations, SEO and deployment work. Development happens on feature branches and is merged to `main` only after verification.

### Production target

- Domain: `tehnet.ir`
- Origin address and access details are maintained in private operator configuration.
- CDN/DNS: Cloudflare
- Canonical host: `https://tehnet.ir`
- `www.tehnet.ir` must permanently redirect to the apex host.

### Repository map

- `docs/` — product/design/architecture/implementation plans
- `ops/` — installation, deployment, backup, recovery and production evidence
- `site/` — custom WordPress theme/plugins
- `seo/` — TehNet-specific SEO research and architecture
- `content/` — site content and video mapping
- `HANDOFF.md` / `PROGRESS.md` / `TASKS.md` — continuation state, verified progress and backlog

See `PROGRESS.md` and `HANDOFF.md` for the current implementation state.

Publication policy: [public-repository hygiene](docs/publication-privacy-2026-10-31.fa.md). Sanitized historical evidence can contain documentation-only replacement addresses and `[PRIVATE_LOCAL_PATH]`; those values are never deployment targets. Run `python tools/publication_guard.py` before publishing.

## آرشیو نرم‌افزار تهران نتورک — پژوهش و برنامه مستقل / TehNet Software Archive

[Start here: projects/software-hub/README.md](projects/software-hub/README.md) — isolated research copy, roadmap, agent workstreams, privacy and portable migration design. This is not a deployed service; original TehNet site/runtime is unchanged.


## تحویل جامع آرشیو نرم‌افزار به ایجنت بعدی — ۲۵ اکتبر ۲۰۲۶

برای ادامهٔ این بخش از [AGENT_HANDOFF](projects/software-hub/AGENT_HANDOFF.md) شروع کنید: تمام کارهای انجام‌شده با لینک شواهد، نتیجهٔ آزمون‌ها، خطاهای محفوظ، محدودیت‌ها، مسئولیت‌ها و قدم‌های باز در آن جمع‌بندی شده‌اند. [task جمع‌بندی](projects/software-hub/tasks/DOCS-AGENT-HANDOFF-20261025.md) نتیجهٔ کنترل مستندات و ref انتشار را ثبت می‌کند.

عبارت قدیمی «This is not a deployed service» در معرفی اولیهٔ بالا، وضعیت زمان کپی پژوهش بود. موتور بعداً زیر /software/ فعال شد؛ آخرین بررسی عملیاتی این گفتگو ۲۱ اکتبر است. پایش محدود با completed_with_incidents پایان یافت و پیگیری آن بازنشسته شد؛ تایمرهای انتشار و بازآزمایی در همان کنترل فعال ماندند. وضعیت زندهٔ امروز از آن نتیجه نمی‌شود. این تغییر ۲۵ اکتبر فقط مستندات است؛ سایت و سرویس‌ها تغییر نکردند.
