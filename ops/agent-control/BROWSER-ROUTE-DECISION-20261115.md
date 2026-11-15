# وضعیت مسیر اجرای مرورگر — ۱۵ نوامبر ۲۰۲۶ (بعد از بازبینی مدیر)

## حکم مدیر (MANAGER_REVIEW_V1، کامنت 6893046637، 10:34:12Z)
Packet: TN-BROWSER-20261115-PACKAGE-1 · reviewed source: 6271001b821627fe82732d165a24c9704b920f53
**NEEDS_CHANGES** — پیشرفت واقعی به رسمیت شناخته شد (درایورها/رسیدها خوانده شدند) اما اجرا روی مرورگرِ میزبانِ مالک انجام شده بود.

## دستور اجرایی (CORRECTION #1 — مقدم بر بقیه)
مرورگر میزبان مالک = مسیر متوقف. هیچ launch مرورگر دیگری روی میزبان؛ هیچ تغییر setup میزبان.
اگر runner ابری مجاز موجود نباشد → فقط اجرای مرورگر BLOCKED ثبت شود و کار مستقل ادامه یابد.

## runner ابری مجاز موجود: GitHub-hosted runner
- ریپو از قبل Actions دارد (release-operator-boundaries، tracked-file-privacy) — محیط مجاز و ایزوله.
- الگوی پذیرفته‌شده: tests/commercial-decision-native.sh روی github-hosted runner یک fixture کامل WordPress+Woo+store می‌سازد و Playwright را همان‌جا اجرا می‌کند (run 42503696771 قبلاً پذیرفته شده).
- مسیر ادامه: workflow مخصوص مجموعهٔ مرورگری (Case 1-4 drivers) روی همین الگو؛ رسید با run/job ID + URL گیت‌هاب.

## وضعیت مسیرها
| مسیر | وضعیت |
|---|---|
| Chromium روی میزبان مالک | **STOPPED** (دستور مدیر) |
| GitHub-hosted runner | مجاز — authoring در جریان |
| browser execution کلی | BLOCKED تا اجرای اول روی runner ابری؛ کار مستقل ادامه دارد |

## اصلاحات دیگر مدیر (ترتیب اجرا پس از runner)
2. TIME/SOURCE: timestampهای اصلی + provenance ساعت + run ID یکتا + hashهای bundle در هر رسید.
3. SERVICES از صفحهٔ مبدأ + CTA واقعی + keyboard-only واقعی با focus assertions.
4. CSS اصلی برای run پذیرش؛ variantهای override جدا برچسب بخورند.
5. B2B/Support: success state خاص + هویت quote/ticket متعلق به تست + private + thread؛ no-JS باید submit و به نتیجهٔ persist شده برسد.
6. finally-safe browser/context close + teardown متعلق به fixture در drivers.
