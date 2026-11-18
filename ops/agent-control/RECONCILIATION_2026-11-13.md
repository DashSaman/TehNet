# تطبیق وضعیت و توالی ادغام — ۱۳ نوامبر ۲۰۲۶

## Phase 0 — وضعیت تأییدشده (همه با readback واقعی)

| مورد | وضعیت | شاهد |
|---|---|---|
| origin/main | `04c2af9` (PR92 docs handoff) — بدون merge جدید | git log origin/main |
| PR89/90/91/93/94/95/96/82/79 | همگی OPEN، CI سبز | API check-runs 2026-11-13 |
| Watchdog | فعال، Next Run 17:50، لاگ 13:50:04Z سالم | schtasks + ~/.zcode/tehnet-watchdog.log |
| Site | 200 + noindex, nofollow برقرار | GET مستقل |
| Worktree | تمیز روی `ops/agent-control-20261111` همگام با origin | git status |
| Backup | `netauto-main:/root/backups/tehnet-20261113` SHA256SUMS OK + restore rehearsal PASS (۱۲-۱۱) | SSH readback |

## Phase 2 — تطبیق PR93 با کار محلی Queue

PR93 (cloud-queue) یک بستهٔ **کامل** Queue ID67 است: ۱۲ فریم واقعی WinBox از CHR ابری، native52/renderer8/browser518، rollback و scope-guard کامل. کار محلی نیمه‌تمام `feat/queue-winbox-20261106` دیگر ادامه نمی‌یابد (duplicate)؛ دستورالعمل آن در `handoff/queue-in-progress-20261106` فقط به‌عنوان سابقه می‌ماند.

## توالی ادغام بدون تداخل (۷ PR مشترک‌فایل)

فایل‌های مشترک بین شاخه‌ها: `ops/release-growth-content.py`، `ops/migrate-growth-content.php`، `site/themes/tehnet/assets/css/visual-refresh.css` (appends تجمعی).

هر شاخه از main (04c2af9/69243f4) منشعب شده؛ تداخل‌ها در سه فایل مشترک قابل حل‌اند چون appends تجمعی‌اند (هر شاخه فقط بلوک خودش را اضافه می‌کند) و scopeهای migrator مستقل‌اند (WINBOX/NAT/FW/QUEUE-CLOUD).

**توالی پیشنهادی (هر گام پس از CI سبزِ rebase/merge-test):**
1. PR95 (docs/SEO فقط — بدون کد؛ صفر تداخل)
2. PR93 (queue cloud — migrator+CSS)
3. PR89 → PR90 → PR91 (سه بسته WinBox — migrator+CSS؛ حل تعارض appends به‌ترتیب)
4. PR96 (agent-control — فقط docs/script؛ صفر تداخل)
5. PR94 (index readiness — ۱۰۷ فایل؛ گسترده‌ترین؛ آخرین، با CI تازهٔ head)
6. هر گام merge فقط با مجوز صریح مالک (RELEASE_GATES.md)

**نکتهٔ مهم:** ادغام هر شاخه، appends CSS و scopeهای migrator شاخه‌های بعدی را هم وارد می‌کند — پس پس از هر ادغام، rebase شاخه‌های بعدی و اجرای مجدد native/browser tests ضروری است. artifact نهایی هر انتشار باید با SHA شاخهٔ متناظر تطبیق داده شود.

## Phase 1 — قید بازگشت

restore rehearsal فقط DB-only و same-host بود. بازیابی wp-content و مقصد off-host آزمون نشده (دیسک ۸۴٪)؛ این محدودیت در بستهٔ تصمیم مالک (OWNER_DECISION_INDEXABILITY v3) صادقانه ثبت شده و بزرگ‌تر از پاکسازی cache است.
