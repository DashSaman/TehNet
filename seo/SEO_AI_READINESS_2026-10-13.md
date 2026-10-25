# TehNet — SEO / AEO / GEO readiness

Reviewed: 2026-10-13. Scope: the existing TehNet site and its approved public résumé; not MyTel production changes.

## وضعیت واقعی / Current state

The visual release is already deployed as **TehNet 0.5.1**. WPVibe site_info independently confirmed that version at 2026-10-13T13:00:56Z. The source baseline is branch `feat/portfolio-visual-20261013`, commit `0fa72b57db77c63598c839a7d32aa223312598f9`; do not redeploy older main over it.

The prior release's evidence lives in `ops/VISUAL_REFRESH_2026-10-13.md`, `qa/live-browser-report.json` and `qa/public-verification.json`. Those record 40 browser checks and 26 public HTTP checks; they are prior release evidence, not a new full retest in this continuation.

The public profile at `/amirreza-golavar/` renders its title, description and `noindex,nofollow`. The excluded partner brand and personal mobile must stay absent from public profile HTML, metadata, text downloads and VCF. Do not confuse the existing business office number with the excluded personal mobile.

## Fresh live mobile audit / ممیزی زنده جدید

Tool: WPVibe audit_page, homepage, mobile, all four categories, 2026-10-13.

| Observation | Result | Interpretation |
|---|---|---|
| Performance | 93/100 | Laboratory score; not a ranking metric |
| Accessibility | 100/100 | Tool still reported label-content-name-mismatch; not proof of full WCAG compliance |
| Best Practices | 100/100 | No issues flagged in this category |
| SEO | 61/100 | Two flagged findings below; not a Google ranking score |
| LCP | 2.7 s | Lab observation; improve without promising field CWV |
| CLS | 0.02 | Lab observation |
| TBT | 110 ms | Lab observation; not a substitute for INP |
| FCP / Speed Index | 2.0 s / 3.3 s | Lab observations |
| Unused CSS | Estimated 11 KiB saving | Review after functional stability; do not blanket-remove block styles |
| Real-user CrUX data | None available | Do not claim field CWV PASS |
| Homepage meta description | Missing | Open implementation defect |
| Indexing | Blocked | Intentional prelaunch constraint; not automatically changed |

## Reusable MyTel lessons / درس‌های قابل انتقال

1. Preserve proven URL/H1 ownership and existing intent-specific pages rather than churn metadata for scores.
2. Maintain one owner for each metadata/schema responsibility; reuse stable entity IDs and avoid duplicate Organization/LocalBusiness nodes.
3. Personal identity, brand identity and company contact information are distinct. Never use a brand's social profile as a person's sameAs without evidence.
4. Publish useful, source-backed technical resources: real commands, supported versions, diagnostic steps and limitations. Do not manufacture case studies, customer proof, tests or citations.
5. Validate stored content and public output separately. A successful write is not a successful release.
6. Existing indexation/crawl observations are dated evidence, not proof of current rankings or why a page ranks.
7. Search discovery bots, user-requested retrieval and training bots have different controls. Do not disable WAF or alter training preferences to chase a GEO score.
8. Avoid thin synonym pages, doorway locations, repeated submission requests, manufactured mentions and duplicate indexing tools.

Source: `DashSaman/mytel.one/SEO_AUTHORITY_AI_EXECUTION_LOG_2026-08-26.md` (historical project execution evidence). Sensitive MyTel backups, secrets and customer data are not copied here.

## Foundation decisions / تصمیم‌های اجرایی

- Retain Learn, Lab, Services and Shop journeys and existing lesson/service URLs.
- Keep text server-rendered and usable without JavaScript; graphics supplement text rather than replace it.
- Add a minimal tested metadata layer without replacing the live Core plugin, whose runtime version differs from its repository header. Fresh runtime comparison is mandatory before any code deployment.
- Keep the existing résumé meta description as its owner; do not print a second description. Add only supported identity markup, based on visible content, without personal telephone, fabricated credentials or metrics.
- Prefer editable page excerpts for descriptions with explicit bounded fallbacks; do not overwrite editorial content in bulk.
- No special llms.txt or universal AI schema is required for Google Search. This task prioritizes crawl/index controls, useful content, identity, internal links and evidence.
- Keep `blog_public=0` and existing noindex until the separate launch gate and explicit owner approval. Do not submit a currently disabled sitemap or call IndexNow for noindex URLs.
- A content methodology/correction page is a useful next content item, but must describe actual practice, not invent past tests or reviewers.

## Official guidance rechecked today

- Google generative Search fundamentals: https://developers.google.com/search/docs/fundamentals/ai-optimization-guide — ordinary SEO, helpful differentiated content and technical clarity remain foundational; no special AI markup or artificial chunking required.
- Google AI features: https://developers.google.com/search/docs/appearance/ai-features — indexed/snippet-eligible content, accessible crawling, internal discovery and visible matching structured data.
- ProfilePage: https://developers.google.com/search/docs/appearance/structured-data/profile-page — a page's actual person/organization is its mainEntity; eligibility does not guarantee display.
- OpenAI crawlers: https://developers.openai.com/api/docs/bots — independently documented crawler roles; confirm current policy before any robots/WAF change.

The newer Google generative guide refers to Search Console generative controls/reporting while the older AI-features page describes aggregate Web reporting. Record actual property availability; do not claim a control/report is enabled without inspecting it.

## Blockers / موانع فعلی

- Remote Desktop Commander reported device RoboT online, but this continuation's start_process timed out; list_sessions and ping each ended with `Timeout - no response from device`. This is a management-channel problem, not proof that the website is down. Do not enqueue repeated deployment commands with unknown outcomes.
- GSC Wizard list_sites returned `payment_required` (trial ended/no active subscription). No purchase, upgrade or property-data claims were made. GSC/GA4/AI measurement configuration remains unverified in this continuation.
- WPVibe authenticated reads succeed; WPVibe site plugin remains missing. Do not claim native theme-writing capability was tested or enabled.

## Release gate / شرط اعلام تکمیل

1. Capture fresh targeted backup and current-file hashes; compare runtime/source drift.
2. Test the metadata addition in isolation; then deploy only its explicit allowlist.
3. Recheck title, exactly one H1, one description, canonical, intentional noindex and valid/consistent JSON-LD on all target routes.
4. Check homepage, profile, Learn, Lab, Services, Shop, blog and 404; verify important internal links and downloads.
5. Recheck mobile navigation, labels, dark/light, keyboard and reduced motion; distinguish lab from field performance.
6. Keep all payment/order/inquiry/core settings, unrelated services, ports and existing page content unchanged.
7. Commit evidence and update HANDOFF/PROGRESS/TASKS. Report prepared, deployed and live-verified separately.

## Reporting contract / گزارش‌دهی

At each phase boundary send the owner: completed work, actual test result, blocker if any, next action and commit/checkpoint. Report a blocked command promptly, without implying work is happening in the background. Save code, tests, redacted evidence and continuation instructions; do not publish secrets, database dumps, customer data or font files.
