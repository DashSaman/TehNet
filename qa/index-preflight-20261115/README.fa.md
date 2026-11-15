# TN-INDEX-PREFLIGHT-20261115 — پکیج پیش‌پرواز مسیر ایندکس (PR100)

## وضعیت کلی

| بخش | نتیجه |
|---|---|
| A — قرارداد استاتیک (manifest ها، runtime class، migration PHP، operator، bundle ها) | **45/45 PASS** |
| php -l (فقط syntax، بدون اجرا) | class-index-policy.php + migrate-index-policy.php → سالم |
| B — readback فقط‌خواندنی staging (wp-cli، بدون هیچ write) | اجرا شد؛ **13/16 منطبق** |
| توصیهٔ نهایی | **DRIFT DETECTED — قبل از D2/D3 نیازمند re-qualification** |

- PR100 head پین‌شده: `a54198ce7ed3535d6783432d8401660e2e023f9d`
- همهٔ artifactها از git (نه worktree) خوانده شدند تا drift بررسی، خودش drift نسازد.
- staging readback: `staging-readback.json` — فقط‌خواندنی؛ `policy_option_present=false`، `blog_public="0"`، فیلتر core noindex فعال.

## سه drift واقعی (runtime به‌صورت fail-closed رد می‌کند — دقیقاً طبق طراحی)

1. **`/` (id 5) — body_hash_drift**
   - staging `1a05541d…` ≠ manifest `6ba0eb04…` (excerpt منطبق است)
   - علت محتمل: تغییرات محتوای مشروع پس از 2026-11-08 (دسته‌های D1 و پاک‌سازی لینک‌های home طبق 8c74794)

2. **`/services/voice-network-readiness/` — id_drift + excerpt**
   - manifest و `$fixed` در `ops/migrate-index-policy.php` هر دو id=206 انتظار دارند
   - probe (`staging-id-check.php`, read-only): **id 206 در staging وجود ندارد** (`{"id":206,"missing":true}`)؛ صفحه فقط با **id=193** هست (publish، permalink درست، **hash محتوا با manifest منطبق**)؛ excerpt 202 بایتی اضافه شده
   - یعنی اصلاح فقط manifest کافی نیست؛ `$fixed` هم باید به 193 اصلاح شود — هر دو artifact گاردشدهٔ PR100

3. **`/services/remote-support/` (id 37) — excerpt_hash_drift**
   - manifest انتظار excerpt خالی دارد؛ staging excerpt دارد (`60e99cdc…`)؛ محتوا منطبق

## وضعیت پیش‌نیازها (D2/D3)

- **M0**: PR100 هنوز merge نشده (PR100 باز است، head `a54198ce`)
- **D1**: محتوای PR100 قبلاً روی staging verify شده (cycle 25)
- **D2 (install-off)**: `runtime_class=false` در readback → نصب runtime هنوز انجام نشده — وضعیت انتظارِ پیش از D2
- **D3 (activate 16 URL)**: `production_authorization = NEEDS_SEPARATE_EXACT_ALLOWLIST_OWNER_APPROVAL` — هنوز unauthorized؛ علاوه بر آن تا re-qualification سه drift بالا، `plan()` خودش activation را رد می‌کند
- **مقصد off-host**: آماده نیست (آخرین recovery فقط same-host DB-only بود) — پیش‌نیاز صریح دستور

## تصمیم دقیق (نه پرسش مجدد از هدف کلی ایندکس)

قبل از هر اجرای D2 روی staging، سه اصلاح نیازمند review است:
1. بازتولید `activation-manifest.json` با hashهای فعلی staging (بعد از تصمیم دربارهٔ excerptهای اضافه‌شده)
2. اصلاح `$fixed` در `ops/migrate-index-policy.php`: `/services/voice-network-readiness/` از 206 به 193 (با اثبات مبدأ id 206 در inventory)
3. تعیین تکلیف drift محتوای `/` (پذیرش نسخهٔ فعلی در manifest جدید یا بازگردانی محتوا)

هر سه تغییر محدود به artifactهای PR100 است و مسیر تأیید همان GUARDED_SCOPES موجود را طی می‌کند. هیچ تغییری در این پکیج روی PR100 اعمال نشد.

## حدود انتشار

بدون IP، بدون secret، بدون raw log، بدون محتوای خام صفحات (فقط hash و ID و عنوان‌هایی که خودشان در manifest گیت هستند).
