# Ahrefs Domain Rating benchmarking — TehNet & ten comparable firms
Reviewed: **2026-11-11**. Directly measured through authenticated Ahrefs MCP `public_domain_rating_free`, `version=dr3` (default), targets exactly the 11 domains in CSV. This is an Ahrefs third-party indicator, not Google's ranking signal or a measurement of referring-domain counts.
 
| Target | DR3 |
|---|---:|
| تهران نتورک / TehNet (tehnet.ir) | 0 |
| ترازنت (taraznet.com) | 26 |
| ایمن شبکه هوشمند (www.imennet.net) | 26 |
| رایکانت (raykanet.com) | 22 |
| پیراسیس (www.pirasys.com) | 7 |
| پردیس پارس (pardispars.com) | 9 |
| شبکه ارغوان (arghavannet.com) | 7 |
| ایران هلپ‌دسک (iranhelpdesk.com) | 10 |
| آی‌تی‌خانه (itkhaneh.com) | 6 |
| واریان شبکه گستر (varianet.ir) | 9 |
| پیشگام رایانه (www.pishgamrayaneh.com) | 16 |

## Meaning and limits
- DR is Ahrefs' logarithmic third-party score from 0 to 100 for the strength of a domain's backlink profile; it is **not** a literal number or percentage of links, not Google Domain Authority, not a keyword position, not the number of quality backlinks and not proof of SEO success.
- TehNet DR=0 in Ahrefs' snapshot, **not proof of zero backlinks** nor that its content or business is low-quality.
- Ahrefs released a **DR4 preview on 2026-11-05**: these specifically measured DR3 values may change when the provider migrates; future longitudinal comparisons must pin the metric version.
- Do not treat a difference of 10 DR points as a linear quantitative advantage; avoid promising a target DR value. Prioritize documented, genuine citations, customer case links by consent and vendor relationships only if real.

## Sources and reproducibility
- Tool: `mcp__Ahrefs__public_domain_rating_free({targets:[...],version:"dr3",output:"json"})`; same default model DR3 used; returned all 11 targets.
- Definition: https://ahrefs.com/seo/glossary/domain-rating
- Search engine use: https://help.ahrefs.com/en/articles/907673-do-search-engines-use-domain-authority-domain-rating-as-a-ranking-factor
- DR4 update: https://ahrefs.com/blog/domain-rating-dr4/ (2026-11-05)
- Licensing notice: https://ahrefs.com/legal/domain-rating-license

## Next phase
A genuine referring-domain/link-quality gap analysis remains `NOT_MEASURED` because authenticated Ahrefs API project/units are unavailable on current Free plan. For meaningful earned-link strategy, use no-cost manual vetting of a small set of real supplier/customer references with permission and publicly visible content; do not manufacture backlinks.
