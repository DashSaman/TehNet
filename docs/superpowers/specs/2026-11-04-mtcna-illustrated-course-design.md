# TehNet illustrated MTCNA article series — production design

Status: RESEARCHED_PROPOSAL; article production, RouterOS lab execution, original screenshots and publication are not complete.

Requested: 2026-11-04. The owner asked for accurate, illustrated, step-by-step MTCNA articles using the latest RouterOS, after the current work, to build useful organic search discovery.

## 1. Deliverable and editorial position

Create a free Persian learning series in the existing TehNet Learn and Lab journeys. Use the existing MTCNA hub and the current intent-owning articles before creating new URLs. Each article must solve a practical problem and fit a coherent learning order.

Proposed public series name: **آموزش تصویری MTCNA با RouterOS 7؛ از اولین اتصال تا عیب‌یابی شبکه**.

This is an independent TehNet learning resource mapped to the official training outline. Do not describe TehNet as a MikroTik authorized training centre or promise an official certificate unless independently established.

The existing recorded videos are separate sources. A new written lesson must not be presented as a transcript or as a topic taught in a numbered video without verified audio/screen evidence. In particular, the instructor reports that a full Queue lesson was not taught in the existing recordings. Preserve that distinction.

### Approaches considered

1. Expand existing video descriptions: inexpensive, but cannot create a complete current-version course where videos lack coverage or show older interfaces.
2. Build a written series with repeatable labs and original screenshots, linking verified video segments only when useful: recommended because it meets the requested format and creates practical evidence.
3. Produce a new video course first: valuable later, but unnecessary for the requested article-first delivery.

The recommendation is an implementation proposal, not a claim that the owner approved a detailed design.

## 2. Verified starting point

Sources were inspected on 2026-11-04.

- TehNet uses WordPress, the custom TehNet theme and TehNet Core. Free education is an existing phase-1 decision.
- Hub ID 40, https://tehnet.ir/learn/mikrotik/mtcna/, was read through the connected WordPress REST API. It now separates the recorded videos, independent written tutorials and the Queue supplement.
- Existing intent owners include RouterOS/WinBox (62), IP/DHCP/DNS (63), static routing (64), NAT (65), firewall (66), Queue/troubleshooting (67), and the separate GNS3 lab.
- The latest retrieved HANDOFF records deployment of educational attribution fixes. It explicitly does not establish a complete review of all eight recordings. Issue 75 and Issue 63 remain open in that checkpoint.
- The site launch/indexing gate is separate. Keep the intentional noindex setting until the existing launch requirements and owner authorization are satisfied.
- Connected WordPress authenticated reading was verified. Uploading and publishing were not tested in this investigation.
- The current execution environment did not have QEMU, VirtualBox, Docker or a KVM device. No RouterOS VM was run and no screenshot or command output was produced from a router.
- This proposal changes neither the existing working queue nor production configuration by itself.

Repository starting point observed for this proposal: main 7062a514948b0e6701f84782f20f9b5066db88e6. Re-read current HANDOFF and live state before later implementation; other authorized work is active.

## 3. Version policy

The official stable changelog listed **RouterOS 7.25.1**, dated **2026-11-03**, at retrieval. The official download page listed **WinBox 4.5**, also dated **2026-11-03**.

Recheck the stable channel immediately before the first lab capture. Pin the selected versions for the first batch. Record the version actually used, not just the current download-page version. If a later release changes a demonstrated behaviour or menu, update affected lessons after a real retest; a calendar change alone is not an update.

Each published article displays:

- actual RouterOS version and release channel;
- actual WinBox version, or WebFig if that interface was used;
- device model or CHR, architecture and relevant packages;
- starting state and prerequisite lesson;
- actual last test date, separate from editorial revision date.

The current official manual may display a newer documentation version than stable RouterOS. A manual version label is not a stable release declaration. Do not copy version-specific commands from it into a stable-version lesson without checking actual availability.

The official training page currently links to an outline whose internal revision date is January 22, 2016. Use it as a coverage checklist; do not invent a new official “MTCNA 2026 syllabus”. Modern additions must be identified as TehNet supplements.

## 4. Proposed 24-article coverage and canonical ownership

This is a coverage inventory, not permission to create 24 new URLs. Reuse or improve existing owners where the search intent is the same. A substantial existing article may cover more than one inventory row.

| No. | Persian working title | Main outcome | Ownership / evidence |
|---|---|---|---|
| 01 | نقشهٔ راه MTCNA و ساخت آزمایشگاه میکروتیک | Reproducible isolated lab and prerequisites | Existing hub plus GNS3 lab; separate navigation from detailed setup |
| 02 | اولین اتصال با WinBox و WebFig | Verified management access | Existing RouterOS/WinBox article |
| 03 | ترمینال، Safe Mode و مدیریت تغییرات | Execute and reverse a scoped lab change | Expand owner or distinct tutorial after intent check |
| 04 | تنظیمات پیش‌فرض، کاربر و سرویس‌های مدیریتی | Understand starting state and access | Explicit CHR versus RouterBOARD differences |
| 05 | Backup، Export، Restore و بازیابی | Restore a known lab checkpoint | Original files with no private data |
| 06 | ارتقای RouterOS، Packageها و RouterBOOT | Read version/channel and validate upgrade | RouterBOOT requires physical RouterBOARD evidence |
| 07 | IP، Subnet، Gateway و طراحی آدرس‌دهی | Explain and validate a subnet plan | Existing IP/DHCP/DNS article |
| 08 | DHCP Client، DHCP Server و Leaseها | Obtain a valid client lease | Existing IP/DHCP/DNS article |
| 09 | DNS و ARP؛ تشخیص علت قطع ارتباط | Distinguish resolution and reachability | Existing IP/DHCP/DNS article |
| 10 | Bridge و پورت‌ها | Connect a lab LAN with clear boundaries | Original bridge membership evidence |
| 11 | Default Route و Static Route | Build and inspect routing state | Existing static-routing article |
| 12 | اتصال دو شبکه و بررسی مسیر برگشت | Prove both directions of communication | Extend routing owner or separate full scenario |
| 13 | NAT، Masquerade و دسترسی اینترنت | Verify address translation | Existing NAT article; record upstream assumptions |
| 14 | Destination NAT و Port Forwarding | Expose only an isolated lab service | Explicit topology, double-NAT and CGNAT caveats |
| 15 | Connection Tracking، Input و Forward | Explain packet paths and state | Existing firewall article |
| 16 | قواعد فایروال، Address List و ترتیب اجرا | Verify allowed and blocked traffic | Existing firewall article; preserve management access |
| 17 | Wi-Fi جدید و Wireless قدیمی | Select the right menu for actual hardware | Physical compatible radios and package manifest |
| 18 | Access Point، Station و امنیت بی‌سیم | Establish and diagnose a real radio link | Physical lab; no CHR-only Wi-Fi execution claim |
| 19 | Simple Queue و کنترل پهنای باند | Demonstrate a measurable queue effect | Existing independent Queue article |
| 20 | PCQ، Burst و اثر FastTrack بر Queue | Diagnose bandwidth-policy behaviour | Fresh written lesson; no old-video attribution |
| 21 | PPP، Pool و PPPoE | Establish and inspect a lab session | Client/server evidence in isolated lab |
| 22 | تونل‌ها؛ تطبیق سرفصل قدیمی با کاربرد امروزی | Understand applicable tunnel choices | Historical syllabus items separated from current operational recommendations |
| 23 | Ping، Traceroute، Torch، Log و مانیتورینگ | Diagnose a deliberately introduced fault | Recorded failure and recovery |
| 24 | پروژهٔ نهایی و تمرین عیب‌یابی | Build and explain a small branch network | Reproducible acceptance record and solution |

Coverage beyond the original outline, such as a deeper VLAN lab, modern VPN extensions or advanced wireless management, belongs in clearly labelled supplements rather than silently changing the claimed official syllabus.

## 5. Laboratory and image production

Recommended default: the existing GNS3 learning path with official CHR images and isolated networks. A direct VM workflow can be used for the first lesson if it materially reduces beginner setup friction; document one primary path and keep alternatives brief.

Baseline topology:

- simulated upstream network;
- R1 branch router;
- two client nodes on a lab-only LAN;
- R2 and a second LAN introduced for routing and PPP lessons;
- an isolated service host for NAT and troubleshooting exercises;
- dedicated management access and clean-state checkpoints.

Never bridge a lab DHCP server into the user's normal LAN. Addresses, interface names and starting configuration must be consistent across screenshots, diagrams and commands.

CHR Free has a 1 Mbps transmit limit per interface according to the official licensing documentation. It is suitable for many low-rate connectivity demonstrations. Queue demonstrations must use rates and traffic sources that do not mistake the licence ceiling for the queue result. No paid licence or recurring service is needed by default.

CHR can support the virtual routing lab; it does not provide evidence of a physical Wi-Fi association, signal level, radio performance or RouterBOOT operation. Those lessons need compatible physical devices, original instructor evidence, or an honest incomplete status.

### Original image requirements

- Capture the real RouterOS management interface from the actual lab and pinned version.
- Keep original captures; use numbered callouts, crops and readable captions that do not alter UI text, state or measured results.
- Never fabricate WinBox screenshots, terminal output, version labels or test results with image generation.
- Use precise original SVG diagrams for topology and packet paths.
- Show enough context to identify the menu and relevant interface. Supply a full-resolution view where small text matters.
- Use a consistent light interface style where possible, with adequate contrast on mobile.
- Remove credentials and identifiers that belong to real environments. Prefer purpose-created lab values from the start.
- Use responsive image sizes and compressed WebP/AVIF only if command and label legibility remains intact; keep a suitable original.
- Write meaningful Persian alt text and captions near the relevant step.
- Do not reuse third-party screenshots without suitable permission and attribution.

Do not force a fixed image count. Typically 6–12 useful captures may fit a practical lesson, but a concept may require one clear diagram and a longer configuration may require more.

## 6. Reusable article contract

Every practical article contains:

1. The problem and the concrete result the learner should reach.
2. Prerequisites, exact lab starting point and version/device box.
3. A topology diagram and small addressing/interface table.
4. Numbered UI steps, each paired with a relevant real capture.
5. Equivalent CLI commands when helpful, with explanations of variables and scope.
6. An expected-result section clearly distinguished from actually observed test output.
7. Verification steps and the observed acceptance result.
8. A concise troubleshooting table: symptom, check, likely cause and correction.
9. A way to undo the lesson's changes or restore its dedicated checkpoint.
10. One practical exercise and a separately revealed solution.
11. Official technical sources, useful prior/next lesson links, and any verified related video.
12. A natural link to the relevant existing service or Lab resource where the reader needs it.

Persian prose and headings; preserve exact English menu names and command syntax. Keep code blocks left-to-right. Do not add unverified credentials, testimonials, exam affiliation, result claims or fake “tested” badges.

## 7. First production batch

Produce one complete pilot before multiplying the format:

**Pilot:** the existing RouterOS/WinBox owner at /learn/mikrotik/mtcna/routeros-winbox/.

Proposed capture list:

- official source/version selection;
- clean lab console and RouterOS version;
- WinBox version and connection screen;
- successful connection and router identity;
- interface list tied to the diagram;
- initial access protection relevant to the actual starting state;
- one scoped Safe Mode demonstration;
- final read-only verification and checkpoint.

A screenshot request is not a completed screenshot. Mark every missing capture as pending in the production manifest and keep incomplete articles out of publication.

After the pilot passes, finish a cohesive entry package: hub/navigation, lab setup, RouterOS/WinBox, IP/DHCP/DNS, NAT/basic connectivity and the necessary management/firewall prerequisites. Publish only individually verified pages, with no dead “next lesson” links.

Then extend routing, firewall, Queue, PPP, wireless and the final project. Grouping by learner outcomes is more important than achieving an arbitrary article count.

## 8. Acceptance and publication

Per-lesson evidence record:

- content owner ID/URL and status;
- RouterOS, WinBox, hardware and package versions;
- prerequisite state and lab configuration fingerprint;
- source URL and retrieval date for important technical claims;
- original capture files and their hashes;
- command transcript and checks actually performed;
- expected versus observed result;
- validation of both successful behaviour and the relevant failure case;
- rollback/checkpoint evidence;
- reviewer and actual review date;
- video attribution status, default NONE unless independently verified.

Publication requires a complete tested lesson, real readable visuals, a technical/editorial review, and the existing TehNet staging/release checks. Preserve current canonical URLs and protected site data. Do not bypass the educational content gate. Do not mark video review complete merely because the new written article is valid.

Search launch is separate: intentional noindex and other existing launch requirements remain governed by the current project instructions. Preparing or publishing a page under noindex does not establish search visibility.

This document creates no scheduled automation, no public post, no upload and no change to indexing.

## 9. Discovery and measurement

The search sample found Persian MTCNA resources, including a written RouterOS 7 “30 nights” learning series. It does not support a claim that no Iranian equivalent exists or that TehNet is the first. The defensible differentiation is coherent tested exercises, current exact-version screenshots, useful troubleshooting and maintained updates.

Initial search-intent candidates, not measured keyword-volume claims:

- آموزش تصویری MTCNA
- آموزش میکروتیک RouterOS 7
- اتصال میکروتیک به اینترنت
- تنظیم DHCP میکروتیک
- تفاوت Input و Forward میکروتیک
- مشکل کار نکردن Simple Queue
- آموزش WinBox 4

Use a hub plus substantial intent-owning pages. Avoid duplicate thin pages per recording or per near-identical keyword. Match page title, heading, excerpt, images and structured data to actual content.

After a controlled indexable launch, review Search Console queries, impressions, clicks and CTR for the course pages; track lab downloads and relevant service enquiries as practical outcomes. Do not invent baseline traffic or promise rankings, visitor counts or a date for results.

## 10. Sources and handoff

Official primary sources:

- Stable releases, checked 2026-11-04: https://mikrotik.com/download/changelogs?channelFilter=stable&versionFilter=7.14-7.99
- WinBox download/version: https://mikrotik.com/download/winbox
- Official training page: https://mikrotik.com/training/about
- Outline linked by that page: https://i.mt.lv/cdn/training_pdf/mtcna_outline_2019181161836.pdf
- Current CHR licensing: https://manual.mikrotik.com/docs/getting-started/routeros-licensing/chr/chr-licensing/
- Current CHR installation: https://manual.mikrotik.com/docs/getting-started/installation-and-upgrade/install/chr-installation/
- Current wireless overview: https://manual.mikrotik.com/docs/wireless/
- Current Wi-Fi reference: https://manual.mikrotik.com/docs/wireless/wifi/
- Google content guidance: https://developers.google.com/search/docs/fundamentals/creating-helpful-content
- Google image guidance: https://developers.google.com/search/docs/appearance/google-images
- Google noindex behaviour: https://developers.google.com/search/docs/crawling-indexing/block-indexing

Bounded market observation:

- Persian written learning path: https://mehdimj.ir/learn/
- Sample Persian lab article: https://mehdimj.ir/blog/2026/10/02/mtcna-night-12-static-routing-lab/

Existing TehNet sources:

- AGENTS.md; HANDOFF.md; PROGRESS.md; ROADMAP.md; TASKS.md.
- docs/superpowers/specs/2026-09-14-tehnet-platform-design.md.
- seo/MTCNA_VIDEO_CONTENT_VERIFICATION_2026-11-04.fa.md.
- The live hub: https://tehnet.ir/learn/mikrotik/mtcna/.
- DashSaman/-SEO/README.md.

### Next executable action

Reconcile with the active TehNet worker and current canonical state, establish one authorized isolated CHR lab, reverify the stable release, execute the pilot from a known start, capture original screenshots and attach actual test evidence. Complete that pilot before generating the rest. Missing lab access, physical-radio evidence and launch readiness remain explicit dependencies rather than invented completed work.

