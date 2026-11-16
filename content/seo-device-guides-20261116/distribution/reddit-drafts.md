# Reddit Response Drafts (DRAFT_ONLY)

> وضعیت: DRAFT_ONLY. هیچ پستی منتشر/ارسال نشده.
> قوانین subredditها قبل از انتشار باید دوباره بررسی شوند.
> بدون لینک تبلیغاتی، چندحسابی، پیام خصوصی یا تماس با moderator.

---

## Reddit ۱: r/mikrotik — سؤال رایج دربارهٔ hEX قدیمی و جدید

**سؤال فرضی:** "Is the old hEX still worth buying or should I get the new one?"

**پاسخ پیشنهادی (انگلیسی):**

The old hEX (RB750Gr3) with 256MB RAM and dual-core 880MHz is still fine for basic home routing. The new hEX refresh (E50UG) has an ARM32 CPU (EN7562CT) at 950MHz with 512MB RAM — noticeably faster for heavier firewall rules and more active connections.

Key differences:
- E50UG has more RAM (512MB vs 256MB)
- E50UG runs RouterOS v7 natively
- Both have 5x Gigabit Ethernet
- Price difference varies by region

If your current RB750Gr3 handles your firewall rules and connection count without hitting RAM limits, there's no urgent reason to upgrade. If you're setting up a new office or need more headroom, the E50UG is the safer choice.

Note: both models lack PoE-out and SFP. If you need those, look at hEX S (RB760iGS) or L009UiGS-RM.

---

## Reddit ۲: r/mikrotik — CRS310 vs CRS309 for NAS

**سؤال فرضی:** "CRS310 vs CRS309 for 10G NAS setup?"

**پاسخ پیشنهادی (انگلیسی):**

Both are 10G switches but they serve different use cases:

**CRS309-1G-8S+IN**: 8x SFP+ (10G) ports. Best for direct server/NAS attachment when you already have SFP+ NICs. No copper Ethernet for endpoints. Single 24V DC power input.

**CRS310-8G+2S+IN**: 8x 2.5G Ethernet (copper) + 2x SFP+ (10G). Better if you have a mix of copper and fiber endpoints. Dual power inputs.

If your NAS and servers all have SFP+ NICs, CRS309 gives you 8 ports of 10G. If you need copper connections for some devices, CRS310 provides 8x 2.5G copper + 2x SFP+ uplinks.

Both run RouterOS v7 with SwOS dual-boot option. The switch chip on both handles L2 switching in hardware; L3 routing between VLANs is CPU-bound and limited by the 800MHz ARM core.

---

## Reddit ۳: r/networking — PoE budget calculation basics

**سؤال فرضی:** "How do I calculate PoE budget for my office?"

**پاسخ پیشنهادی (انگلیسی):**

PoE budget = sum of all connected device power draws + safety margin.

Steps:
1. List every PoE device and its maximum power draw (from the device datasheet, not the adapter label)
2. Add them up
3. Add 20% headroom for cable losses and startup surges
4. Compare with the switch's total PoE budget (not per-port)

Example:
- 8 IP cameras × 12W (PoE+) = 96W
- 4 IP phones × 6W (PoE/af) = 24W
- Total: 120W
- With 20% margin: 144W minimum PSU capacity

Important: check if the PSU is included with the switch. Some MikroTik switches (like netPower 16P) ship without a PSU — you need to buy one separately with sufficient capacity.

Also check: 802.3af (up to 15.4W/port) vs 802.3at (up to 30W/port) — some devices need at, not just af.

---

## قوانین انجمن‌ها (بررسی مجدد قبل از انتشار)

| subreddit | وضعیت قوانین | نکته |
|---|---|---|
| r/mikrotik | خودتبلیغی بدون تأیید مدیر ممنوع | بدون لینک TehNet؛ فقط پاسخ فنی |
| r/networking | تبلیغ خدمات/محصول ممنوع | پاسخ فنی عمومی بدون برند |
| r/homelab | معمولاً بحث تجهیز آزاد است | قبل از انتشار قوانین جاری چک شود |
