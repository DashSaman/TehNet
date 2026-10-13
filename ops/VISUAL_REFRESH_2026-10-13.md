# TehNet — live visual refresh / گزارش انتشار بازطراحی

Date: 2026-10-13. Deployed theme: **TehNet 0.5.1**.

## نتیجه فارسی
بازطراحی روی سایت زنده `https://tehnet.ir/` اعمال شد. رنگ‌بندی سرمه‌ای و فیروزه‌ای، گرافیک برداری سرور و شبکه، کارت‌ها، حالت روشن/تیره و منوی موبایل از طراحی تأییدشده رزومه اقتباس شده‌اند. لوگوی موجود حفظ شد.

رزومه امیررضا گل‌آور در `https://tehnet.ir/amirreza-golavar/` به‌صورت برگه بومی وردپرس، با شناسه ۸۰ منتشر شد؛ صفحه تصویر یا iframe نیست. متن رزومه و کارت تماس قابل دریافت‌اند. شماره موبایل شخصی و برند مستثناشده در صفحه، دانلودها و متادیتای جدید وجود ندارند. شماره ثابت کاری سایت، جدا از شماره شخصی، حفظ شد.

آموزش، لاب، خدمات، فروشگاه و صفحات درس‌های موجود حفظ شدند. محتوای صفحه اصلی همچنان در Gutenberg قابل ویرایش است. پروفایل در بلوک HTML وردپرس و قالب اختصاصی نمایش داده می‌شود.

## Verification evidence
- 16 existing repository contract scripts: PASS.
- 7 new visual/privacy regression tests: PASS; initially observed failing before implementation.
- Product inquiry logic test: PASS. No production inquiry/order was created for this design change.
- Theme PHP and front-end JavaScript syntax checks: PASS.
- Chromium 154 browser suite: 40 checks passed on the deployed homepage/profile, dark/light modes, widths 320, 375, 390, 768, 1024 and 1440; navigation, Escape, theme toggle, animation pause, skill filters and print-state restoration included.
- Public HTTP suite: 26 checks passed — 24 published page routes plus two résumé/contact downloads. Pages have HTTP 200, one H1, expected canonical and noindex; exclusions checked.
- Origin smoke: homepage, profile, Learn, Services and Shop returned HTTP 200.
- WordPress content persistence checked by SHA256 immediately after writing.
- Protected WordPress/payment settings and all pre-existing non-home page content: unchanged.
- Non-TehNet container/image/port fingerprint, TehNet Core files and existing font files: unchanged before/after deployment.
- No Nginx, Compose, firewall, port, gateway or indexing changes; no service restart.

Machine-readable evidence: `qa/live-browser-report.json`, `qa/public-verification.json`.

## Issues found and disposition
1. Production presentation was newer than main. Captured the deployed header/footer/index/styles, existing logo/banner and current homepage in isolated baseline commits instead of overwriting them with older source.
2. Legacy mobile-header layout and contact-button color conflicted with the new layer. Corrected after screenshot inspection and repeated browser checks.
3. Pre-existing `/blog/` had no H1 or canonical. Repaired its archive heading, empty-state heading handling and self-canonical without enabling indexing; public regression now passes.
4. An initial urllib download probe returned HTTP 403. Ordinary curl and Chromium retrievals succeeded with HTTP 200; no access-control or security setting was changed.
5. An initial privacy test falsely matched the suffix of MyTel as a telephone scheme; corrected the boundary, keeping actual mobile-number and VCF restrictions. Test sources use generic number patterns rather than publishing personal numbers.

## Recovery / بازیابی
Validated server-side backups were taken before changes and again immediately before deployment. Final release recovery point: `/root/tehnet-backups/20261013-123014-visual-release`.
It contains the validated database dump, theme archive, target-content state and before/after isolation evidence. A `blog-metadata-fix` subdirectory preserves the three files before the blog correction. Backup bytes remain private on the production host and are not committed.

Use targeted theme/home/profile recovery when needed; do not restore an old full database over newer customer data. The new profile can be reverted to draft. Historical one-shot scripts in `ops/visual/` are guarded and should not be blindly rerun against the now-updated site.

## Limits / موارد خارج از این مرحله
Search indexing intentionally remains disabled (`blog_public=0`, noindex/nofollow). Payment and full account/support lifecycle work remain separate tasks. Browser checks cover Chromium, not Safari/Firefox or an exhaustive accessibility audit. The WordPress editor and live transaction workflows were not end-to-end exercised. The preview DOM simulation is not counted as production publishing evidence; the live checks above are separate.

## Source checkpoint
Branch: `feat/portfolio-visual-20261013`. Keep this branch and its worktree until integration/review; do not discard live-only work. Main was not force-updated or automatically merged.
