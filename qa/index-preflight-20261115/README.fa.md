# TN-INDEX-PREFLIGHT-20261115 — پکیج پیش‌پرواز مسیر ایندکس (PR100) — rev2

rev2: شواهد فقط‌خواندنی PRODUCTION اضافه شد؛ مرز مدیر (عدم بازنویسی production map با staging ID) رعایت شد.

## وضعیت کلی

| بخش | نتیجه |
|---|---|
| A — قرارداد استاتیک (manifest ها، runtime class، migration PHP، operator، bundle ها) | **45/45 PASS** |
| php -l (فقط syntax، بدون اجرا) | هر سه PHP سالم |
| B — readback فقط‌خواندنی staging | **13/16 منطبق** (۳ drift) |
| B′ — readback فقط‌خواندنی production | **هر ۱۱ fixed ID منطبق manifest**؛ 206=voice-network-readiness، 193 absent |
| توصیهٔ نهایی | **MANIFEST RE-QUALIFICATION لازم است؛ binding باید محیط‌آگاه باشد** |

- PR100 head پین‌شده: `a54198ce7ed3535d6783432d8401660e2e023f9d`
- هر دو readback فقط‌خواندنی‌اند: هیچ write، هیچ wp_mail، هیچ HTTP؛ فقط get_option/get_post/get_page_by_path/get_permalink/get_post_meta/hash

## یافتهٔ کلیدی ۱ — تفاوت ID بین محیط‌ها مشروع است (مرز مدیر تأیید به شواهد)

| | production (tehnet.ir) | staging (localhost:18085) |
|---|---|---|
| voice-network-readiness | **id=206** (page/publish، permalink درست) | **id=193** (page/publish، permalink درست) |
| id مقابل | 193 → **absent** | 206 → **absent** |
| content hash | `7f384153…` | `7f384153…` — **هر دو منطبق manifest body** |
| excerpt | موجود `c3e9109a…` | موجود `c3e9109a…` (یکسان در دو محیط) |

- manifest از هویت production ساخته شده بود (هر ۱۱ fixed id منطبق) → **production map صحیح است و دست‌نخورده می‌ماند؛ 206→193 رد می‌شود**
- staging طی sync/re-release صفحه را با ID جدید بازساخته است — تفاوت مشروع محیط‌ها
- **پیشنهاد (تصمیم مدیر):** binding محیط‌آگاه — یا map مختص هر محیط در manifest، یا plan() هنگام check روی هر محیط، expected id را از منبع همان محیط بردارد. هر دو تغییر محدود به artifact گاردشدهٔ PR100 است

## یافتهٔ کلیدی ۲ — manifest hash/عنوان در هر دو محیط نسبت به وضعیت فعلی کهنه است

- production: `/`، `/services/`، چهار صفحهٔ service، `/about/`، remote-support → body hash با manifest تفاوت دارد (تغییرات مجاز پس از 2026-11-08: دسته‌های محتوایی + اصلاح زندهٔ 8c74794). `/contact/`، `/technical-methodology/` و body سه صفحهٔ دیگر منطبق‌اند
- عنوان ۴ صفحهٔ service در production تغییر کرده (اصلاحات محتوایی ثبت‌شده)
- excerpt: voice-network و remote-support در **هر دو محیط** excerpt دارند ولی manifest انتظار خالی دارد → انتظار excerpt در manifest کهنه است، نه اختلاف محیطی
- طبق مرز مدیر: تطبیق باید با **bundle منتشرشدهٔ مقصود production** انجام شود، نه پذیرش خودکار DB staging

## گام‌های دقیق re-qualification (تصمیم، نه پرسش مجدد از هدف کلی)

1. بازتولید `activation-manifest.json` از bundle مقصود + وضعیت تأییدشدهٔ production (hash/عنوان/excerpt)
2. تعیین مکانیزم binding محیط‌آگاه برای id (206/193) در migration و manifest
3. اجرای D2 (install-off) روی staging پس از تعیین مکانیزم — وضعیت فعلی: runtime class در staging absent
4. D3 همچنان `NEEDS_SEPARATE_EXACT_ALLOWLIST_OWNER_APPROVAL` + پیش‌نیازهای PR101/102/103 و off-host/full recovery

## حدود انتشار

بدون IP، بدون secret، بدون raw log، بدون محتوای خام (فقط hash/ID/عنوان موجود در manifest گیت).
