# PROPOSAL — environment-aware ID binding برای مسیر ایندکس (فقط SOURCE؛ اعمال نشده)

مرجع: MANAGER_REVIEW 6902078070 — «Preserve production206 and prepare an environment-aware SOURCE proposal with the current intended production bundle, leaving guarded release/runtime/activation and off-host gates intact.»

## مشکل فعلی (با شواهد readback)

`ops/migrate-index-policy.php` در `plan()` برای هر هدف، post را با `get_page_by_path` resolve می‌کند و سپس ID آن را با مقدار `t['id']` manifest مقایسه می‌کند؛ در `$fixed` هم همان ID production نسخه‌گذاری شده. روی staging، صفحهٔ voice-network-readiness با ID 193 resolve می‌شود (206 آنجا وجود ندارد) → «Index managed owner mismatch» حتی با manifest سازگار.

شواهد: production `206=voice-network-readiness (hash منطبق manifest body)`، staging `193` با همان body hash؛ ID مقابل در هر محیط absent. یعنی تفاوت ID مشروعِ ناشی از sync/re-release است، نه drift هویت.

## پیشنهاد source (schema 2 — روی PR100 اعمال نمی‌شود در این commit)

۱) activation-manifest.json → schema 2 با binding مختص محیط؛ `id` زمینهٔ production می‌ماند (guarded production map دست‌نخورده):

```json
{
  "schema": 2,
  "key": "tehnet-index-allowlist-20261108-v1",
  "operation": "activate",
  "identity_base": "production",
  "targets": [
    { "path": "/services/voice-network-readiness/", "id": 206,
      "env_ids": { "production": 206, "staging": 193 },
      "body_sha256": "<از bundle مقصود production>",
      "excerpt_sha256": "<همان>" }
  ]
}
```

۲) `plan()` در migrate-index-policy.php — فقط انتخاب ID مورد انتظار بر اساس محیط؛ بقیهٔ چک‌ها دست‌نخورده:

```php
-$expectedId=(int)($t['id']??0);
+$env=wp_get_environment_type();
+$expectedId=(int)(($t['env_ids'][$env]??null)?:($t['id']??0));
 // بقیه: publish/password/permalink/title/body_sha256/excerpt/growth_key بدون تغییر
```

همچنین `$fixed` داخل plan() به دو نسخهٔ env-aware تبدیل می‌شود (`fixed_by_env`)؛ مقادیر production دقیقاً همان مقادیر فعلی می‌مانند.

## تطبیق hash/excerpt با bundle مقصود production (بدون پذیرش خودکار drift)

1. منبع حقیقت = bundle‌های immutable در PR100 (`content/commercial-decision-2026-11-08-v2/manifest.json` + همان transform در migrate-growth-content.php)
2. بازتولید body/excerpt hash با اجرای همان transform روی bundle (نه خواندن از DB staging یا production)
3. verify متقاطع: hash بازتولیدشده باید با readback فقط‌خواندنی production مقایسه شود؛ اختلاف = تکلیف محتوایی برای مالک (مثل تغییرات مجاز 8c74794 روی home)، نه پذیرش یک‌طرفه
4. سپس manifest schema 2 با hashهای مصوب تولید و از مسیر GUARDED_SCOPES review می‌گذرد

## گیت‌های دست‌نخورده

- M0=PR100 merge، D2 install-off، D3 activation با `NEEDS_SEPARATE_EXACT_ALLOWLIST_OWNER_APPROVAL`
- انتشار PR101/102/103 و off-host/full recovery همچنان پیش‌نیاز صریح D3
- هیچ تغییر در این proposal به شاخهٔ PR100 یا هر محیطی اعمال نشده است — فقط سند source برای review
