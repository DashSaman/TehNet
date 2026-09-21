# TehNet | تهران نتورک

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
- سرور Origin: `91.107.138.246`
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
- Origin server: `91.107.138.246`
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
