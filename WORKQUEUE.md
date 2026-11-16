# WORKQUEUE — TN-TEHNET-SEARCH-LEARNING-REVENUE-V2

> وضعیت‌ها: READY / IN_PROGRESS / REVIEW_REQUEST / NEEDS_CHANGES / DONE / BLOCKED / PAUSED
> فقط با تغییر واقعی state را به‌روزرسان؛ برای polling بی‌تغییر کامیت یا comment نساز.
> اصلاح ساختار طبق MANAGER_REVIEW 6922214726: وضعیت DONE فقط برای شرطِ بسته‌شدهٔ واقعی؛
> source-only بسته‌شده از output/test باز جدا می‌شود.

---

| id | priority | dependencies | status | acceptance | artifact | full_sha | receipt | blocker | next_action |
|---|---|---|---|---|---|---|---|---|---|
| P0-poe-scenario-source | P0 | — | DONE | netPower OUT variant + جداسازی کاربران؛ بازنگری ca307ae | articles/mikrotik-switches-crs.fa.md (سناریوها) | ca307ae7321735ba | — | — | بسته‌شده با تأیید مفروضات در 6921626767 |
| P0-poe-scenario-output | P0 | P0-poe-scenario-source | REVIEW_REQUEST | sync خروجی با MD + build-summary | articles/mikrotik-switches-crs.gutenberg.html | (این تیک) | validation-receipt rev7 (c10-freshness) | مرور مدیر 6922464979 | REVIEW_REQUEST ارسال‌شده |
| P0-crs354-ram | P0 | — | DONE | 128MB official | 6251514 | — | — | — | — |
| P0-builder-gate-source | P0 | — | DONE | router-only in router guide | a3543b5 | — | — | — | — |
| P0-builder-rev3 | P0 | — | REVIEW_REQUEST | fence/quote/image/ol + tutorial jobs؛ خروجی مقالهٔ روتر byte-identical | articles/build-gutenberg.cjs | (این تیک) | build-summary.json rev3 | مرور مدیر | در RR این تیک |
| P0-afterd1-patches | P0 | — | REVIEW_REQUEST | hash guard + after-D1 bodies؛ صفحات پیشنهادی؛ **guard اجراپذیر: GUARD=PASS (G1-G4 روی هر ۳ بسته؛ بازسازی byte-identical)** | page-edits/*.proposed.html + qa/verify-afterd1-guard.cjs | (این تیک) | afterd1-guard-receipt.json (LOCAL_TEST) | مرور مدیر | در RR این تیک |
| M2-tutorial-vlan | P4 | — | REVIEW_REQUEST | مبنا/سیاست/DHCP-network/sequencing/فایروال/تست مثبت-منفی/نمودار/تمرین/پیوند/منبع — بازنگری کامل 6923833096 | tutorials/m2-vlan-small-office.fa.md + .gutenberg.html | (این تیک) | validation-receipt rev7 | مرور مدیر 6923833096 | RR این تیک |
| M3-tutorial-dhcp-dns | P4 | M2 | REVIEW_REQUEST | گره‌زدن interface/gateway + مرز 53 + تست کلاینت + تفکیک lease/دستی + نمودار/تمرین/پیوند/منبع — بازنگری کامل 6923833096 | tutorials/m3-dhcp-dns.fa.md + .gutenberg.html | (این تیک) | validation-receipt rev7 | مرور مدیر 6923833096 | RR این تیک |
| P4-educational-backlog (M4-M6/S2-S6/N1-N6) | P4 | M2+M3 acceptance | PAUSED | توقف توسعهٔ درس تا پذیرش M2/M3 (6923833096 اصلاحیهٔ 1) | — | — | — | — | بعد از ACCEPT M2/M3 |
| P1-discovery-matrix | P1 | P0 | REVIEW_REQUEST | 16 URLs با GET واقعی 2026-11-16 سند شد: 11 زنده (200، canonical=self، در wp-sitemap) + 5 مرده (404، بدون canonical، خارج از sitemap) | qa/seo-device-guides-20261116/discovery-matrix.csv | (این تیک) | discovery-http-receipt.json (LOCAL_TEST read-only) | مرور مدیر؛ تصمیم مالک دربارهٔ 5 URL مرده | بازنگری 5 slug مرده قبل از هر لینک داخلی |
| P1-topic-map | P1 | P0 | REVIEW_REQUEST | Masterplan 18/18 واحد (S5/S6+N1-N6 اضافه شد) + topic-map با ردیف‌های S5/S6/N4-N6، هدف N3 اصلاح شد (slug مردهٔ 404 → پیشنهادی)، ردیف لینک قرارداد BLOCKED، وضعیت اجرا صادقانه (PLANNED نه READY) | MASTERPLAN.md + content/.../topic-map.md | (این تیک) | — | مرور مدیر؛ تصمیم مالک روی 5 slug مرده | در RR این تیک |
| P1-internal-links | P1 | P1-topic-map | REVIEW_REQUEST | source→target→anchor applied in candidate pages | page-edits/*.proposed.html | — | — | مرور مدیر | همراه P0-afterd1-patches |
| P2-driver-integration | P2 | fixture-ownership | BLOCKED | app/DB disposable + ownership verified pre-effects | — | — | — | fixture ownership unverified; no disposable cloud env | await manager acceptance |
| P3-service-pages | P3 | P0 | REVIEW_REQUEST | 3 pages title/H1/direct-answer/deliverables/limits/CTA | content/seo-device-guides-20261116/page-edits/ | — | — | مرور مدیر | — |
| P3-articles-complete | P3 | P0 | REVIEW_REQUEST | router+switch articles intent/selection/limits/upgrade؛ switch HTML همگام شد (این تیک) | content/seo-device-guides-20261116/articles/ | (این تیک) | validation-receipt rev7 | مرور مدیر | — |
| P5-distribution | P5 | P3 | REVIEW_REQUEST | LinkedIn×3 + Gamma×20 + Reddit≤3 + Zenodo protocol | distribution/* | f8e11f45d23aaa0e | — | مرور مدیر (RR 6923439838) | DRAFT_ONLY |
| P5-favicon-live | P5 | P0 | NOT_RUN | verify rendered head output | site/themes/tehnet/assets/img/ | — | — | NOT_RUN: live-site check نیازمند محیط مجاز | owner action via wp-admin |
