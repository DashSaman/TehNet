# -*- coding: utf-8 -*-
"""TN-M2-M3-TUTORIAL-DIAGRAMS-20261116 — deterministic conceptual SVG generator.
Generates the two tutorial diagrams (M2 topology, M3 DHCP/DNS flow) as original
TehNet-authored conceptual drawings (labeled as such; NOT photos, NOT executed
labs). No timestamps inside output except the fixed sources-access date string.
Run: python -I make-tutorial-diagrams.py   (from qa/seo-device-guides-20261116/)
"""
import io, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   '../../content/seo-device-guides-20261116/assets')
ACCESS_DATE = '2026-11-16'

FONT = 'font-family="Tahoma, Segoe UI, Arial, sans-serif"'

def rect(x, y, w, h, fill, stroke='#37474f', sw=2, rx=8):
    return '<rect x="%d" y="%d" width="%d" height="%d" rx="%d" fill="%s" stroke="%s" stroke-width="%d"/>' % (x, y, w, h, rx, fill, stroke, sw)

def text(x, y, s, size=13, anchor='middle', fill='#1a1a1a', weight='normal'):
    return '<text x="%d" y="%d" %s font-size="%d" text-anchor="%s" fill="%s" font-weight="%s">%s</text>' % (x, y, FONT, size, anchor, fill, weight, s)

def line(x1, y1, x2, y2, stroke='#37474f', sw=2, dash=''):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return '<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="%d"%s/>' % (x1, y1, x2, y2, stroke, sw, d)

def svg(w, h, title, desc, body):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">\n'
            '<title>%s</title>\n<desc>%s</desc>\n%s\n</svg>\n' % (w, h, w, h, title, desc, body))

# ---------------- M2 topology ----------------
C10, C20, C30, C40 = '#1e88e5', '#fb8c00', '#43a047', '#8d6e63'
b = []
b.append(rect(340, 20, 280, 60, '#eceff1'))
b.append(text(480, 45, 'اینترنت (فرضی آموزشی)', 14, 'middle', '#1a1a1a', 'bold'))
b.append(line(480, 80, 480, 110, '#37474f', 3))
b.append(text(500, 100, 'ether1 = WAN', 12, 'start'))
b.append(rect(340, 110, 280, 90, '#ffffff', '#0d47a1', 3))
b.append(text(480, 138, 'روتر: hEX (RB750Gr3)', 15, 'middle', '#0d47a1', 'bold'))
b.append(text(480, 160, 'VLAN interfaceها + فایروال + NAT', 12))
b.append(text(480, 180, 'RouterOS v7.16+ (مبنای سند)', 11, 'middle', '#546e7a'))
# trunk double line
b.append(line(430, 200, 430, 300, '#37474f', 4))
b.append(line(438, 200, 438, 300, '#37474f', 4))
b.append(text(450, 255, 'trunk — تگ‌دار 10,20,30,40', 12, 'start', '#37474f', 'bold'))
b.append(rect(280, 300, 400, 80, '#ffffff', '#6a1b9a', 3))
b.append(text(480, 328, 'سوئیچ: CRS112-8P-4S-IN', 15, 'middle', '#6a1b9a', 'bold'))
b.append(text(480, 350, 'bridge1 — vlan-filtering (آخرین گام)', 11, 'middle', '#546e7a'))
# access ports — spacing 100px, boxes 92px wide → no overlap
ports = [
    ('ether2 → ACC-10', 320, C10, 'لپ‌تاپ دفتر (VLAN10)'),
    ('ether3 → ACC-20', 420, C20, 'DVR 192.168.20.10 + دوربین‌ها (VLAN20)'),
    ('ether4 → ACC-30', 520, C30, 'تلفن IP (VLAN30)'),
    ('ether5 → ACC-40', 620, C40, 'AP مهمان (VLAN40)'),
]
for label, x, color, dev in ports:
    b.append(line(x, 380, x, 430, color, 3))
    # port label stacked in two centered lines (no horizontal overlap)
    pl = label.split(' → ')
    b.append(text(x, 402, pl[0], 12, 'middle', color, 'bold'))
    b.append(text(x, 418, pl[1] if len(pl) > 1 else '', 11, 'middle', color, 'bold'))
    b.append(rect(x - 46, 430, 92, 58, color + '22', color, 2))
    # three-line wrap, max ~17 chars per line
    words, lines, cur = dev.split(' '), [], ''
    for w in words:
        if len(cur + ' ' + w) <= 17 or not cur:
            cur = (cur + ' ' + w).strip()
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    for li, ln in enumerate(lines[:3]):
        b.append(text(x, 448 + li * 14, ln, 11, 'middle', '#1a1a1a'))
# legend
b.append(rect(40, 496, 880, 48, '#fafafa', '#b0bec5', 1))
b.append(text(60, 522, 'راهنما:', 12, 'start', '#37474f', 'bold'))
b.append(rect(120, 510, 14, 14, C10)); b.append(text(140, 522, 'VLAN10 دفتر', 12, 'start'))
b.append(rect(230, 510, 14, 14, C20)); b.append(text(250, 522, 'VLAN20 دوربین/DVR', 12, 'start'))
b.append(rect(390, 510, 14, 14, C30)); b.append(text(410, 522, 'VLAN30 تلفن', 12, 'start'))
b.append(rect(510, 510, 14, 14, C40)); b.append(text(530, 522, 'VLAN40 مهمان', 12, 'start'))
b.append(line(640, 517, 680, 517, '#37474f', 4)); b.append(line(640, 521, 680, 521, '#37474f', 4))
b.append(text(688, 522, 'trunk (تگ‌دار)', 12, 'start'))
b.append(line(800, 517, 840, 517, '#37474f', 2))
b.append(text(846, 522, 'access', 12, 'start'))
b.append(text(480, 572, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی، نه عکس از آزمایشگاه واقعی — منابع درس: دسترسی %s' % ACCESS_DATE, 11, 'middle', '#78909c'))
m2 = svg(960, 580,
    'نمودار توپولوژی درس M2: روتر hEX و سوئیچ CRS112 با چهار VLAN',
    'اینترنت به ether1 روتر hEX (WAN) می‌رسد. از ether2 روتر تا ether1 سوئیچ CRS112 یک لینک trunk تگ‌دار برای VLANهای 10 و 20 و 30 و 40 کشیده شده. سوئیچ چهار پورت access دارد: ether2 به لپ‌تاپ دفتر در VLAN10، ether3 به DVR با آدرس 192.168.20.10 و دوربین‌ها در VLAN20، ether4 به تلفن IP در VLAN30، ether5 به نقطهٔ دسترسی مهمان در VLAN40. راهنمای رنگ‌ها پایین تصویر است. این نمودار مفهومی و تألیفی TehNet است و از آزمایشگاه واقعی گرفته نشده است.',
    '\n'.join(b))

# ---------------- M3 DHCP/DNS flow ----------------
b = []
b.append(rect(740, 150, 200, 120, '#ffffff', '#1e88e5', 3))
b.append(text(840, 180, 'کلاینت (DHCP گیرنده)', 13, 'middle', '#1e88e5', 'bold'))
b.append(text(840, 205, 'تست: ipconfig، nslookup', 11, 'middle', '#546e7a'))
b.append(text(840, 225, 'DHCP: gateway+DNS=192.168.88.1', 11, 'middle', '#546e7a'))
b.append(text(840, 245, 'کلاینت غیرمورداعتماد: 10.9.9.9', 11, 'middle', '#9e9e9e'))
# router
b.append(rect(360, 120, 260, 200, '#ffffff', '#0d47a1', 3))
b.append(text(490, 145, 'روتر: hEX (RB750Gr3)', 14, 'middle', '#0d47a1', 'bold'))
b.append(rect(375, 160, 230, 60, '#e3f2fd', '#1e88e5', 1))
b.append(text(490, 180, 'DHCP Server — interface=bridge', 11, 'middle', '#0d47a1'))
b.append(text(490, 197, 'pool 192.168.88.20-254', 11, 'middle', '#0d47a1'))
b.append(text(490, 214, 'network: gateway+DNS=192.168.88.1', 11, 'middle', '#0d47a1'))
b.append(rect(375, 230, 230, 70, '#e8f5e9', '#43a047', 1))
b.append(text(490, 250, 'DNS Cache + static entries', 11, 'middle', '#2e7d32'))
b.append(text(490, 267, 'nas.lan → 192.168.88.10', 11, 'middle', '#2e7d32'))
b.append(text(490, 284, 'printer.lan → 192.168.88.11', 11, 'middle', '#2e7d32'))
# upstream
b.append(rect(30, 160, 180, 60, '#eceff1', '#90a4ae', 2))
b.append(text(120, 186, 'اینترنت / upstream DNS', 12, 'middle', '#455a64'))
b.append(text(120, 205, '8.8.8.8 / 1.1.1.1 (مثال)', 10, 'middle', '#78909c'))
# trust boundary
b.append(rect(340, 100, 300, 240, 'none', '#d32f2f', 2))
b.append(text(490, 355, 'مرز مورداعتماد: 53 فقط از 192.168.88.0/24 — rule شمارنده‌دار (ضد open resolver)', 11, 'middle', '#d32f2f'))
# flows
b.append(line(740, 190, 660, 190, '#1e88e5', 3))
b.append(text(700, 180, '① Discover', 10, 'middle', '#1e88e5', 'bold'))
b.append(line(660, 215, 740, 215, '#43a047', 3))
b.append(text(700, 231, '② Offer', 10, 'middle', '#2e7d32', 'bold'))
b.append(text(700, 245, 'آدرس+gateway+DNS', 9, 'middle', '#2e7d32'))
b.append(line(740, 265, 660, 265, '#fb8c00', 3))
b.append(text(700, 260, '③ nas.lan؟ — پورت 53', 10, 'middle', '#e65100', 'bold'))
b.append(line(660, 290, 740, 290, '#43a047', 3))
b.append(text(700, 313, '④ پاسخ از cache/بالادستی', 10, 'middle', '#2e7d32', 'bold'))
b.append(line(360, 190, 210, 190, '#90a4ae', 2, '6,4'))
b.append(text(285, 182, 'forward/query بالادستی', 10, 'middle', '#78909c'))
# untrusted client
b.append(rect(680, 22, 230, 78, '#f5f5f5', '#9e9e9e', 2))
b.append(text(795, 44, 'کلاینت غیرمورداعتماد', 11, 'middle', '#616161'))
b.append(text(795, 64, '10.9.9.9 (gw=192.168.88.1)', 10, 'middle', '#d32f2f'))
b.append(text(795, 80, 'drop شمارنده‌دار روی 53 (×)', 10, 'middle', '#d32f2f'))
b.append(text(795, 94, 'کنترل مثبت: accept موقت کلاینت آزمایشی → پاسخ', 9, 'middle', '#616161'))
b.append(line(710, 100, 640, 138, '#d32f2f', 2, '5,4'))
b.append(text(600, 118, '× timeout', 11, 'middle', '#d32f2f', 'bold'))
b.append(text(480, 533, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی، نه عکس از آزمایشگاه واقعی — منابع درس: دسترسی %s' % ACCESS_DATE, 11, 'middle', '#78909c'))
m3 = svg(960, 540,
    'نمودار جریان DHCP و DNS درس M3 با مرز مورداعتماد',
    'کلاینت با Discover از سرور DHCP که به پل بسته شده آدرس می‌گیرد و در Offer شمارهٔ gateway و DNS یعنی 192.168.88.1 را دریافت می‌کند. سپس کلاینت نام nas.lan را روی پورت 53 از روتر می‌پرسد و روتر از cache یا بالادستی پاسخ می‌دهد. مرز خط‌چین قرمز نشان می‌دهد پورت 53 فقط از زیرشبکهٔ 192.168.88.0/24 پذیرفته می‌شود تا روتر open resolver نشود؛ کلاینت خاکستری با آدرس 10.9.9.9 بیرون مرز است و پرس‌وجویش timeout می‌گیرد. این نمودار مفهومی و تألیفی TehNet است.',
    '\n'.join(b))


# ---------------- S2 PoE budget ----------------
b = []
# PSU (right) -> DC input -> switch (middle) -> devices (left)
b.append(rect(760, 200, 180, 120, '#fff8e1', '#f9a825', 3))
b.append(text(850, 232, 'PSU جداگانه (پیوست نیست)', 12, 'middle', '#e65100', 'bold'))
b.append(text(850, 254, '24V یا 48V', 11, 'middle', '#546e7a'))
b.append(text(850, 274, '24V → PoE پسیو/ناسازگار af', 10, 'middle', '#78909c'))
b.append(text(850, 292, '48V → af/at سندشده', 10, 'middle', '#78909c'))
b.append(rect(430, 180, 260, 160, '#ffffff', '#0d47a1', 3))
b.append(text(560, 208, 'netPower 16P (CRS318-16P-2S+OUT)', 12, 'middle', '#0d47a1', 'bold'))
b.append(rect(445, 222, 230, 42, '#e3f2fd', '#1e88e5', 1))
b.append(text(560, 240, 'مصرف خود سوئیچ ≈ 16W', 11, 'middle', '#0d47a1'))
b.append(text(560, 258, 'سقف هر ورودی DC: 24V→2.8A (≈67W)', 10, 'middle', '#0d47a1'))
b.append(text(560, 274, '                48V→1.4A (≈67W)', 10, 'middle', '#0d47a1'))
b.append(text(560, 322, '16× GbE PoE-out (af/at) + 2× SFP+ uplink', 11, 'middle', '#37474f'))
# arrow PSU -> switch
b.append(line(760, 260, 690, 260, '#f9a825', 4))
b.append(text(725, 250, 'DC', 11, 'middle', '#e65100', 'bold'))
# device stacks (left)
devs = [
    ('۸ دوربین × 10W = 80W', 240, C20 if False else '#fb8c00'),
    ('۴ تلفن × 5W = 20W', 360, C30),
    ('پورت آزاد رشد (ether13-16)', 470, '#9e9e9e'),
]
for label, y, color in devs:
    b.append(rect(60, y - 24, 260, 44, '#fafafa', color, 2))
    b.append(text(190, y + 4, label, 11, 'middle', '#1a1a1a'))
b.append(line(430, 250, 320, 240, '#fb8c00', 3))
b.append(line(430, 265, 320, 360, '#43a047', 3))
b.append(line(430, 290, 320, 470, '#9e9e9e', 3, '6,4'))
b.append(text(375, 232, 'PoE-out', 10, 'middle', '#e65100', 'bold'))
# margin box
b.append(rect(60, 30, 300, 70, '#e8f5e9', '#43a047', 2))
b.append(text(210, 56, 'demand = 80W + 20W = 100W', 12, 'middle', '#2e7d32', 'bold'))
b.append(text(210, 78, 'با حاشیهٔ امن ×1.2 → 120W', 11, 'middle', '#2e7d32'))
b.append(text(480, 533, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — اعداد از صفحهٔ رسمی netPower 16P (دسترسی %s)' % ACCESS_DATE, 11, 'middle', '#78909c'))
s2 = svg(960, 560,
    'نمودار بودجهٔ PoE درس S2: از PSU جداگانه تا هر دستگاه',
    'PSU جداگانه با ولتاژ ۲۴ یا ۴۸ ولت به ورودی DC سوئیچ netPower 16P می‌رسد. سوئیچ حدود ۱۶ وات مصرف خودی دارد و سقف هر ورودی DC سندشده حدود ۶۷ وات است. خروجی PoE به هشت دوربین با جمع هشتاد وات، چهار تلفن با جمع بیست وات و پورت‌های آزاد رشد تقسیم می‌شود. جمع تقاضا صد وات و با حاشیهٔ امن دوازده صد وات است که باید از توان قابل تامین PSU منهای مصرف خود سوئیچ کمتر باشد. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- S3 module decision flow ----------------
b = []
b.append(text(480, 36, 'فاصلهٔ دو سر لینک؟', 14, 'middle', '#1a1a1a', 'bold'))
branches = [
    ('تا ~۳ متر — همان رک', 130, '#1e88e5', 'کابل DAC', 'S+DA0001 (1m) — Discontinued', 'جایگزین رسمی: DAC 3m (جدول سازگاری)', 'بدون ماژول — کابل مستقیم'),
    ('تا ~۳۰۰ متر — داخل ساختمان', 330, '#fb8c00', 'فیبر مالتی‌مود (OM3)', 'ماژول: S+85DLC03D', '850nm — LC — دو سر لینک', '2x $59'),
    ('تا ~۱۰ کیلومتر — بین ساختمان‌ها', 530, '#43a047', 'فیبر تک‌مود (OS2)', 'ماژول: S+31DLC10D', '1310nm — 10GBASE-LR — دو سر لینک', '2x $69'),
]
for title, y, color, med, mod, spec, cost in branches:
    b.append(rect(360, y - 26, 500, 92, '#fafafa', color, 2))
    b.append(text(610, y - 6, title, 13, 'middle', color, 'bold'))
    b.append(text(610, y + 16, med + ' — ' + mod, 11, 'middle', '#1a1a1a'))
    b.append(text(610, y + 36, spec + '  |  ' + cost, 10, 'middle', '#546e7a'))
b.append(line(480, 48, 480, 104, '#37474f', 2))
b.append(line(480, 104, 250, 104, '#37474f', 2)); b.append(line(250, 104, 250, 104 - 0, '#37474f', 2))
b.append(line(480, 104, 610, 104, '#37474f', 2))
b.append(line(250, 104, 250, 160, '#37474f', 2))
b.append(line(610, 104, 610, 304, '#37474f', 2))
b.append(line(480, 104, 480, 504 - 92, '#37474f', 2))
b.append(text(240, 128, '①', 12, 'middle', '#1e88e5', 'bold'))
b.append(text(620, 128, '', 12, 'middle'))
b.append(text(700, 328, '③', 12, 'middle', '#43a047', 'bold'))
# compatibility side note
b.append(rect(30, 190, 300, 150, '#ede7f6', '#6a1b9a', 2))
b.append(text(180, 214, 'قواعد سازگاری (سند رسمی)', 12, 'middle', '#6a1b9a', 'bold'))
notes = ['1G در SFP+ با استثنا و speed اجباری', '(CCR1016 SFP+1 فقط 10G)', '25G: sfp-rate-select=low', 'S+RJ10: CRS309 حداکثر 4 ماژول', 'third-party: MSA باید سازگار باشد', '— ولی تضمین کامل نمی‌شود (UNKNOWN)']
for ni, n in enumerate(notes):
    b.append(text(180, 238 + ni * 17, n, 10, 'middle', '#455a64'))
b.append(text(610, 62, '②', 12, 'middle', '#fb8c00', 'bold'))
b.append(text(480, 652, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — ماژول‌ها از صفحات رسمی mikrotik.com (دسترسی %s)' % ACCESS_DATE, 11, 'middle', '#78909c'))
s3 = svg(960, 680,
    'نمودار تصمیم انتخاب ماژول S3: DAC، مالتی‌مود یا تک‌مود بر پایهٔ فاصله',
    'فلوچارت تصمیم بر پایهٔ فاصلهٔ دو سر لینک: تا حدود سه متر همان رک کابل DAC بدون ماژول؛ تا حدود سیصد متر داخل ساختمان فیبر مالتی‌مود با ماژول S+85DLC03D با طول‌موج ۸۵۰ نانومتر؛ تا ده کیلومتر بین ساختمان‌ها فیبر تک‌مود با ماژول S+31DLC10D با طول‌موج ۱۳۱۰ نانومتر و استاندارد 10GBASE-LR. کنار نمودار قواعد سازگاری سندشده آمده: ماژول 1G در پورت SFP+ با تنظیم اجباری سرعت و استثناهای سخت‌افزاری، rate-select برای 25G، سقف ماژول S+RJ10 روی CRS309 و وضعیت UNKNOWN ماژول‌های غیرمیکروتیک. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- N1 troubleshooting ladder ----------------
b = []
b.append(rect(330, 20, 300, 56, '#ede7f6', '#6a1b9a', 2))
b.append(text(480, 42, 'تعیین دامنه (پیش‌شرط):', 11, 'middle', '#6a1b9a', 'bold'))
b.append(text(480, 62, 'یک دستگاه؟ یک بخش؟ کل شبکه؟', 11, 'middle', '#455a64'))
rungs = [
    ('L1 — لینک', '/interface ethernet monitor — link-ok؟', 130, '#fb8c00'),
    ('L2 — هم‌شبکه‌ای', 'arp -a / /ip neighbor — MAC gateway دیده می‌شود؟', 220, '#8d6e63'),
    ('L3 — gateway/مسیر', 'route print -4 — default gateway درست؟', 310, '#1e88e5'),
    ('DNS', 'nslookup — نام حل می‌شود؟', 400, '#6a1b9a'),
    ('اینترنت', 'ping 8.8.8.8 / tracert — مسیر تا بیرون؟', 490, '#43a047'),
    ('سرویس/پورت', 'Test-NetConnection host -Port X — Established؟', 580, '#d32f2f'),
]
for title, cmd, y, color in rungs:
    b.append(rect(120, y - 30, 720, 66, '#fafafa', color, 2))
    b.append(text(160, y - 6, title, 13, 'middle', color, 'bold'))
    b.append(text(480, y - 4, cmd, 11, 'middle', '#37474f'))
    b.append(text(800, y + 18, 'سبز: پلهٔ بعدی', 9, 'middle', '#43a047'))
    b.append(text(800, y + 32, 'قرمز: علت همین لایه', 9, 'middle', '#d32f2f'))
    if y < 580:
        b.append(line(480, y + 36, 480, y + 90, '#37474f', 2))
        b.append(text(492, y + 60, 'OK', 10, 'start', '#43a047', 'bold'))
b.append(text(120, 632, 'هشدار همسانی: timeout روی ping به خود روتر در شبکه با سیاست ICMP-محدود (M2/M3) رفتار عمدی است نه خرابی', 10, 'middle', '#e65100'))
b.append(text(480, 662, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — سناریو فرضی؛ اجرا NOT_RUN — دستورها از سندهای رسمی (دسترسی %s)' % ACCESS_DATE, 10, 'middle', '#78909c'))
n1 = svg(960, 690,
    'نمودار نردبان عیب‌یابی درس N1: شش لایه از لینک تا سرویس',
    'پیش‌شرط تعیین دامنه است؛ سپس نردبان شش‌پله‌ای: لینک، هم‌شبکه‌ای با ARP، گیت‌وی و مسیر، DNS، اینترنت و در آخر سرویس و پورت. هر پله دستور تست ویندوز یا RouterOS دارد و دو خروجی سبز و قرمز: سبز یعنی به پله بعدی برو، قرمز یعنی علت در همین لایه است. زیر نمودار هشدار همسانی آمده که در شبکه با سیاست ICMP محدود، timeout روی پینگ خود روتر رفتار عمدی است. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- N4 acceptance phases ----------------
b = []
phases = [
    ('۱. معیارها از SOW', 'هر سرویس: تست مثبت + منفی + شاهد — قبل از شروع', '#1e88e5'),
    ('۲. اجرای ماتریس', 'تست‌به‌تست با ثبت خروجی واقعی', '#43a047'),
    ('۳. شواهد', 'خروجی دستورها + اندازه‌گیری‌ها + قبل/بعد', '#f9a825'),
    ('۴. امضای دو طرف', 'فقط ردیف‌های ✓ با تاریخ', '#6a1b9a'),
]
for idx, (title, sub, color) in enumerate(phases):
    x = 60 + idx * 230
    b.append(rect(x, 80, 210, 96, '#fafafa', color, 2))
    b.append(text(x + 105, 106, title, 12, 'middle', color, 'bold'))
    words, lines, cur = sub.split(' '), [], ''
    for w in words:
        if len(cur + ' ' + w) <= 26 or not cur:
            cur = (cur + ' ' + w).strip()
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    for li, ln in enumerate(lines[:2]):
        b.append(text(x + 105, 130 + li * 16, ln, 10, 'middle', '#37474f'))
    if idx < 3:
        b.append(line(x + 210, 128, x + 230, 128, color, 3))
# fail -> back loop
b.append(rect(200, 210, 560, 60, '#fdecea', '#d32f2f', 2))
b.append(text(480, 234, 'ردیف ✗ → اصلاح → اجرای مجدد همان ردیف (+ ردیف‌های وابسته)', 11, 'middle', '#d32f2f', 'bold'))
b.append(text(480, 256, 'پرش از اصلاح = ردیف skip می‌شود و پذیرفته حساب نمی‌آید', 10, 'middle', '#616161'))
b.append(line(300, 210, 300, 190, '#d32f2f', 2, '5,4'))
b.append(line(700, 210, 700, 190, '#d32f2f', 2, '5,4'))
# matrix sample mini-table (left concept)
b.append(rect(60, 300, 840, 180, '#fafafa', '#b0bec5', 2))
b.append(text(480, 326, 'نمونهٔ ماتریس پذیرش (سه ردیف از جدول کامل درس)', 12, 'middle', '#37474f', 'bold'))
rows_n4 = [
    ('۱-۱ اینترنت', 'ping 8.8.8.8 از دفتر', 'reply', '✓'),
    ('۲-۱ جداسازی مهمان', 'ping 192.168.10.1 از مهمان', 'timeout + شمارندهٔ drop', '✓'),
    ('۲-۲ اینترنت مهمان', 'بازکردن سایت از مهمان', 'موفق', '✗ → فاز اصلاح'),
]
for ri, (sv, t, e, res) in enumerate(rows_n4):
    yy = 356 + ri * 34
    b.append(text(110, yy, sv, 11, 'start', '#1a1a1a'))
    b.append(text(320, yy, t, 11, 'start', '#1a1a1a'))
    b.append(text(560, yy, e, 11, 'start', '#1a1a1a'))
    b.append(text(830, yy, res, 12, 'middle', '#43a047' if res == '✓' else '#d32f2f', 'bold'))
b.append(text(480, 533, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — سناریو فرضی؛ اجرا NOT_RUN', 10, 'middle', '#78909c'))
n4 = svg(960, 560,
    'نمودار فازهای پذیرش تحویل درس N4 با نمونهٔ ماتریس',
    'چهار فاز پذیرش تحویل شبکه: اول معیارها از سود خود نوشته می‌شود و هر سرویس یک تست مثبت و یک تست منفی و یک شاهد دارد؛ دوم ماتریس تست به تست با ثبت خروجی اجرا می‌شود؛ سوم بستهٔ شواهد شامل خروجی دستورها و اندازه‌گیری‌ها و گزارش قبل و بعد ساخته می‌شود؛ چهارم امضای دو طرف فقط برای ردیف‌های تاییدشده. ردیف‌های قرمز به فاز اصلاح برمی‌گردند و اجرای مجدد همان ردیف لازم است. جدول پایین سه ردیف نمونه را نشان می‌دهد. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- N2 monitoring loop ----------------
b = []
phases = [
    ('متریک‌ها', 'دسترسی · منابع · دما · خطای پورت · pool', 130, '#1e88e5'),
    ('آستانه‌ها', 'پیشنهاد شروع — کالیبره با دادهٔ واقعی', 250, '#6a1b9a'),
    ('هشدار', 'Netwatch probe + لاگ TN-N2', 370, '#d32f2f'),
    ('اقدام و نگهداری', 'چک‌لیست هفتگی/ماهانه/فصلی + تست بازیابی', 490, '#43a047'),
]
for idx, (title, sub, y, color) in enumerate(phases):
    yy = 90 + idx * 118
    b.append(rect(200, yy, 560, 76, '#fafafa', color, 2))
    b.append(text(480, yy + 26, title, 13, 'middle', color, 'bold'))
    b.append(text(480, yy + 52, sub, 11, 'middle', '#37474f'))
    if idx < 3:
        b.append(line(480, yy + 76, 480, yy + 118, '#37474f', 3))
# loop-back arrow (maintenance -> metrics)
b.append(line(760, 490, 830, 490, '#43a047', 3))
b.append(line(830, 490, 830, 128, '#43a047', 3))
b.append(line(830, 128, 760, 128, '#43a047', 3))
b.append(text(845, 310, 'بازبینی دوره‌ای', 11, 'middle', '#2e7d32', 'bold'))
# dead-end branch
b.append(rect(40, 300, 120, 90, '#fdecea', '#d32f2f', 2))
b.append(text(100, 330, 'هشدار بدون اقدام', 10, 'middle', '#d32f2f', 'bold'))
b.append(text(100, 352, '= بی‌اثر', 10, 'middle', '#d32f2f'))
b.append(line(200, 428, 160, 390, '#d32f2f', 2, '5,4'))
b.append(text(480, 633, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — آستانه‌ها «پیشنهاد شروع»؛ اجرا NOT_RUN', 10, 'middle', '#78909c'))
n2 = svg(960, 660,
    'نمودار حلقهٔ مانیتورینگ و نگهداری درس N2',
    'حلقهٔ چهارمرحله‌ای مانیتورینگ: متریک‌های پایه شامل دسترسی، منابع، دما، خطای پورت و فضای pool؛ آستانه‌های هشدار که پیشنهاد شروع هستند و با داده واقعی کالیبره می‌شوند؛ هشدار با Netwatch probe و ثبت در لاگ؛ و اقدام با چک‌لیست هفتگی ماهانه و فصلی همراه تست بازیابی. انتهای حلقه به متریک‌ها برمی‌گردد. شاخهٔ جدا نشان می‌دهد هشدار بدون اقدام بی‌اثر است. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- N3 SLA incident timeline ----------------
b = []
b.append(text(480, 36, 'خط زمان یک رخداد فرضی و نقاط اندازه‌گیری SLA', 13, 'middle', '#1a1a1a', 'bold'))
b.append(line(60, 220, 900, 220, '#37474f', 3))
points = [
    (120, 'ثبت رخداد', 'مهر شروع ساعت‌شمار', '#1e88e5'),
    (330, 'اولین پاسخ انسانی', 'فاصله = Response Time', '#6a1b9a'),
    (540, 'شروع کار', '—', '#fb8c00'),
    (750, 'رفع + تأیید مسئول', 'فاصلهٔ شروع→تأیید = Resolution', '#43a047'),
    (880, 'گزارش مکتوب', 'قبل/بعد (الگوی N1/N4)', '#78909c'),
]
for x, t, sub, color in points:
    b.append(circle = None) if False else None
    b.append('<circle cx="%d" cy="220" r="9" fill="%s" stroke="#263238" stroke-width="2"/>' % (x, color))
    b.append(text(x, 196, t, 11, 'middle', color, 'bold'))
    b.append(text(x, 246, sub, 9, 'middle', '#546e7a'))
# response bracket
b.append(line(120, 160, 330, 160, '#6a1b9a', 2))
b.append(line(120, 154, 120, 166, '#6a1b9a', 2))
b.append(line(330, 154, 330, 166, '#6a1b9a', 2))
b.append(text(225, 146, 'Response', 11, 'middle', '#6a1b9a', 'bold'))
# resolution bracket
b.append(line(540, 160, 750, 160, '#43a047', 2))
b.append(line(540, 154, 540, 166, '#43a047', 2))
b.append(line(750, 154, 750, 166, '#43a047', 2))
b.append(text(645, 146, 'Resolution', 11, 'middle', '#2e7d32', 'bold'))
# exception band
b.append(rect(560, 280, 340, 46, '#fff3e0', '#ef6c00', 2))
b.append(text(730, 300, 'استثنا: انتظار قطعه — ساعت‌شمار متوقف با توافق کتبی', 10, 'middle', '#e65100'))
b.append(text(730, 318, '(بدون بند استثنا، این بازه علیه هر دو طرف عمل می‌کند)', 9, 'middle', '#8d6e63'))
# six questions box
b.append(rect(60, 360, 840, 150, '#fafafa', '#6a1b9a', 2))
b.append(text(480, 384, 'شش سؤال قبل از امضا', 12, 'middle', '#6a1b9a', 'bold'))
qs = ['۱. دامنهٔ مشمول دستگاه‌به‌دستگاه + استثناهای صریح', '۲. پاسخ و رفع — دو عدد جدا، به‌تفکیک اولویت', '۳. ساعات پوشش + مسیر خارج از ساعت',
      '۴. مسئول تأیید هر کار + معیار تأیید (الگوی N4)', '۵. شواهد انجام کار: ثبت قبل/بعد (الگوی N1)', '۶. مسیر تشدید + گزارش دوره‌ای']
for qi, q in enumerate(qs):
    b.append(text(90, 410 + qi * 16, q, 10, 'start', '#37474f'))
b.append(text(480, 533, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — رخداد و اعداد کاملاً فرضی؛ اجرا NOT_RUN', 10, 'middle', '#78909c'))
n3 = svg(960, 560,
    'نمودار توالی رخداد و نقاط اندازه‌گیری SLA درس N3',
    'خط زمان یک رخداد فرضی از ثبت تا گزارش مکتوب با پنج نقطه: ثبت رخداد، اولین پاسخ انسانی که فاصله‌اش زمان پاسخ است، شروع کار، رفع با تأیید مسئول که فاصله‌اش زمان رفع است، و گزارش مکتوب با ثبت قبل و بعد. بازه استثنای انتظار قطعه با توافق کتبی ساعت‌شمار را متوقف می‌کند. جعبه شش سؤال پیش از امضا دامنه، پاسخ و رفع جدا، ساعات پوشش، مسئول تأیید، شواهد و مسیر تشدید را فهرست می‌کند. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- N5 backup/export two-track ----------------
b = []
b.append(text(480, 36, 'دو مسیر مکمل — نه جایگزین هم', 13, 'middle', '#1a1a1a', 'bold'))
# track 1: backup binary
b.append(rect(80, 90, 380, 210, '#fafafa', '#1e88e5', 2))
b.append(text(270, 116, 'مسیر ۱: backup باینری', 13, 'middle', '#1e88e5', 'bold'))
b.append(text(270, 142, 'فایل کامل تنظیمات — سریع', 11, 'middle', '#1a1a1a'))
b.append(text(270, 162, 'بازگشت روی همان دستگاه/نگارش', 11, 'middle', '#1a1a1a'))
b.append(text(270, 184, 'با رمز محافظت شود', 11, 'middle', '#455a64'))
b.append(text(270, 206, 'هفتگی — Scheduler سندشده', 10, 'middle', '#78909c'))
b.append(rect(140, 232, 260, 48, '#e3f2fd', '#1e88e5', 1))
b.append(text(270, 252, 'بازیابی: /system backup load', 11, 'middle', '#0d47a1'))
b.append(text(270, 272, 'روی دستگاه آزمایشی فصلی', 10, 'middle', '#546e7a'))
# track 2: export text
b.append(rect(500, 90, 380, 210, '#fafafa', '#43a047', 2))
b.append(text(690, 116, 'مسیر ۲: export متنی', 13, 'middle', '#2e7d32', 'bold'))
b.append(text(690, 142, 'فایل خوانا — حسابرسی/مقایسه/مهاجرت', 11, 'middle', '#1a1a1a'))
b.append(text(690, 162, 'بدون مقادیر حساس (این الگو)', 11, 'middle', '#455a64'))
b.append(text(690, 184, 'ماهانه + بعد از هر تغییر مهم', 10, 'middle', '#78909c'))
b.append(rect(560, 232, 260, 48, '#e8f5e9', '#43a047', 1))
b.append(text(690, 252, 'مقایسه: diff دو export', 11, 'middle', '#1b5e20'))
b.append(text(690, 272, 'بین‌مدل = UNKNOWN — آزمون قبل از اتکا', 10, 'middle', '#546e7a'))
# restore-test gate
b.append(rect(200, 350, 560, 64, '#fdecea', '#d32f2f', 2))
b.append(text(480, 374, 'گیت بازیابی‌آزمون (فصلی): load روی دستگاه آزمایشی + مقایسه', 12, 'middle', '#d32f2f', 'bold'))
b.append(text(480, 398, 'تا آزمون نشده: «پشتیبانِ آزموده» حساب نمی‌شود — یا NOT_RUN ثبت', 10, 'middle', '#616161'))
# off-device box
b.append(rect(80, 440, 380, 60, '#fff8e1', '#f9a825', 2))
b.append(text(270, 464, 'یک نسخه خارج از دستگاه (مسیر مالک)', 11, 'middle', '#e65100', 'bold'))
b.append(text(270, 484, 'خرابی دستگاه = رفتن هر دو نسخه‌ی روی آن', 10, 'middle', '#8d6e63'))
b.append(rect(500, 440, 380, 60, '#fff8e1', '#f9a825', 2))
b.append(text(690, 464, 'export متنی: بدون مقادیر حساس نگهداری شود', 11, 'middle', '#e65100', 'bold'))
b.append(text(690, 484, 'نسخهٔ شامل‌رمز ساخته نمی‌شود (این الگو)', 10, 'middle', '#8d6e63'))
b.append(text(480, 533, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — دستورها RouterOS سندشده؛ اجرا NOT_RUN', 10, 'middle', '#78909c'))
n5 = svg(960, 560,
    'نمودار دو مسیر backup و export درس N5 با گیت بازیابی‌آزمون',
    'دو مسیر مکمل: مسیر اول فایل backup باینری رمزدار با کاربرد بازگشت سریع روی همان دستگاه و بازیابی از طریق دستور load روی دستگاه آزمایشی در آزمون فصلی. مسیر دوم فایل export متنی بدون مقادیر حساس برای حسابرسی و مقایسه و مهاجرت با هشدار UNKNOWN بین‌مدل. گیت بازیابی‌آزمون می‌گوید تا آزمون نشده پشتیبان آزموده حساب نمی‌شود. یک نسخه خارج از دستگاه نگهداری می‌شود چون خرابی دستگاه هر دو نسخه روی دستگاه را از بین می‌برد. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- N6 incident path ----------------
b = []
steps = [
    ('۱. ثبت رخداد', 'زمان · دامنه · اثر کسب‌وکاری', '#1e88e5'),
    ('۲. تریاژ', 'جدی/عادی با معیار از پیش‌نوشته', '#6a1b9a'),
    ('۳. اقدام اولیه', 'نردبان N1 — یافته‌ها ثبت', '#fb8c00'),
    ('۴. تشدید (در صورت معیار)', 'handoff کامل: کردم/دیدم/نکردم + اثر + زمان‌ها', '#d32f2f'),
    ('۵. اقدام سطح دو', 'ادامه با ثبت تغییرات', '#f9a825'),
    ('۶. تأیید و بستن', 'کاربر تأیید + قبل/بعد (الگوی N4)', '#43a047'),
    ('۷. گزارش رخداد', 'توالی زمان‌ها · ریشه · استثنا', '#78909c'),
]
for idx, (title, sub, color) in enumerate(steps):
    yy = 60 + idx * 82
    b.append(rect(140, yy, 680, 62, '#fafafa', color, 2))
    b.append(text(190, yy + 24, title, 12, 'middle', color, 'bold'))
    b.append(text(560, yy + 24, sub, 11, 'middle', '#37474f'))
    b.append(text(160, yy + 44, 'فرض آموزشی', 8, 'start', '#90a4ae'))
    if idx < 6:
        b.append(line(480, yy + 62, 480, yy + 82, '#37474f', 2))
# escalation side box
b.append(rect(20, 200, 110, 150, '#fdecea', '#d32f2f', 2))
b.append(text(75, 224, 'معیار تشدید', 10, 'middle', '#d32f2f', 'bold'))
b.append(text(75, 246, 'جدی: 30 دقیقه', 9, 'middle', '#455a64'))
b.append(text(75, 264, 'بدون پیشرفت', 9, 'middle', '#455a64'))
b.append(text(75, 282, 'دو تلاش بی‌نتیجه', 9, 'middle', '#455a64'))
b.append(text(75, 300, 'روی یک فرضیه', 9, 'middle', '#455a64'))
b.append(line(140, 290, 130, 275, '#d32f2f', 2, '4,3'))
# exceptions side box
b.append(rect(830, 200, 110, 160, '#fff3e0', '#ef6c00', 2))
b.append(text(885, 224, 'استثناها', 10, 'middle', '#e65100', 'bold'))
b.append(text(885, 246, 'قطعی ISP', 9, 'middle', '#455a64'))
b.append(text(885, 264, 'تأمین قطعه', 9, 'middle', '#455a64'))
b.append(text(885, 282, 'سخت‌افزار مشتری', 9, 'middle', '#455a64'))
b.append(text(885, 300, 'ساعت‌شمار', 9, 'middle', '#455a64'))
b.append(text(885, 318, 'با توافق (N3)', 9, 'middle', '#455a64'))
b.append(text(480, 633, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — زمان‌ها فرض آموزشی؛ هر سازمان مالکِ تعیین اعداد خودش است؛ اجرا NOT_RUN', 10, 'middle', '#78909c'))
n6 = svg(960, 660,
    'نمودار مسیر رخداد درس N6: هفت مرحله از ثبت تا گزارش با تشدید و استثناها',
    'مسیر هفت‌مرحله‌ای رخداد: ثبت با زمان و دامنه و اثر؛ تریاژ با معیار از پیش‌نوشته؛ اقدام اولیه با نردبان درس N1؛ تشدید در صورت معیار با handoff کامل شامل چه کاری انجام شده دیده شده و نشده؛ اقدام سطح دو؛ تأیید کاربر و بستن با ثبت قبل و بعد؛ و گزارش نهایی ریشه و استثنا. جعبه‌های کناری معیار تشدید و سه استثنا با رفتار ساعت‌شمار را نشان می‌دهند. زمان‌ها فرض آموزشی‌اند و هر سازمان مالک تعیین اعداد خودش است. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- M4 L3HW HW-vs-CPU flow ----------------
b = []
b.append(rect(60, 60, 180, 70, '#fafafa', '#37474f', 2))
b.append(text(150, 90, 'بسته ورودی', 12, 'middle', '#1a1a1a', 'bold'))
b.append(text(150, 112, 'پورت A — l3-hw-offloading=yes', 9, 'middle', '#546e7a'))
# decision diamond (approximated by rect)
b.append(rect(330, 55, 240, 80, '#ede7f6', '#6a1b9a', 2))
b.append(text(450, 82, 'L3HW روشن در هر دو پورت؟', 11, 'middle', '#6a1b9a', 'bold'))
b.append(text(450, 102, 'مقصد prefix سندشده؟', 11, 'middle', '#6a1b9a'))
b.append(line(240, 95, 330, 95, '#37474f', 3))
# HW path (green, top-right)
b.append(line(570, 75, 700, 75, '#43a047', 4))
b.append(text(635, 65, 'بله', 11, 'middle', '#2e7d32', 'bold'))
b.append(rect(700, 45, 220, 64, '#e8f5e9', '#43a047', 3))
b.append(text(810, 68, 'سوییچ‌چیپ — HW route', 11, 'middle', '#2e7d32', 'bold'))
b.append(text(810, 88, 'unicast · ECMP · VLAN (بدون CPU)', 9, 'middle', '#2e7d32'))
b.append(text(810, 102, 'wire speed', 9, 'middle', '#2e7d32'))
# CPU path (orange, bottom-right)
b.append(line(570, 115, 700, 115, '#ef6c00', 4))
b.append(text(635, 135, 'خیر', 11, 'middle', '#e65100', 'bold'))
b.append(rect(700, 125, 220, 90, '#fff3e0', '#ef6c00', 3))
b.append(text(810, 148, 'CPU', 11, 'middle', '#e65100', 'bold'))
b.append(text(810, 168, 'فایروال/NAT روی CPU', 9, 'middle', '#8d6e63'))
b.append(text(810, 186, 'مالتی‌کست · interface-gateway اول', 9, 'middle', '#8d6e63'))
b.append(text(810, 204, 'Fasttrack اتصال‌ها → HW آفلود', 9, 'middle', '#8d6e63'))
# shared memory note
b.append(rect(200, 210, 370, 100, '#fdecea', '#d32f2f', 2))
b.append(text(385, 234, 'حافظهٔ مشترک HW (سند رسمی)', 11, 'middle', '#d32f2f', 'bold'))
notes = ['Fasttrack: 2.25K تا 4.5K اتصال (بسته به مدل)', 'هر ACL = جای 3-6 اتصال Fasttrack', 'توصیه: اول ACL سوییچی، بعد آفلود انتخابی', 'آفلود جزئی: پیشوند بلندتر اول (/30، /29…)', '98DX3236: 13,312 prefix · 8 nexthop · 4K ECMP']
for ni, n in enumerate(notes):
    b.append(text(385, 258 + ni * 17, n, 10, 'middle', '#616161'))
# must-choose box
b.append(rect(200, 330, 720, 44, '#ede7f6', '#6a1b9a', 2))
b.append(text(560, 356, 'انتخاب اجباری سند رسمی: یا مسیریابی سخت‌افزاری یا فایروال (فایروال روی CPU)', 11, 'middle', '#6a1b9a', 'bold'))
# prerequisites box
b.append(rect(60, 400, 860, 130, '#e3f2fd', '#1e88e5', 2))
b.append(text(480, 424, 'الزام‌های سند رسمی قبل از روشن‌کردن', 12, 'middle', '#0d47a1', 'bold'))
reqs = ['۱. فقط مدل‌های فهرست‌شده (98DX3xxx شامل 98DX3236=CRS326-24G-2S+RM؛ 98DX8xxx شامل CRS309/317/354)', '۲. l3-hw-offloading=yes سراسری + هر دو پورت ورودی/خروجی', '۳. پل hardware-offloaded با vlan-filtering — VLAN interface مستقیم روی switch port ممنوع',
        '۴. فقط یک hardware bridge — چند پل = رفتار نامعین', '۵. حین تغییرات L2 (پل/VLAN/MTU/MAC/bonding): L3HW موقتاً خاموش', '۶. نگارش: منوی L3HW از v7.6 · مانیتور از v7.10 · آفلود per-VLAN از v7.21']
for ri, rq in enumerate(reqs):
    b.append(text(90, 448 + ri * 14, rq, 9.5, 'start', '#0d47a1'))
b.append(text(480, 553, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — بر پایهٔ سند رسمی L3HW (دسترسی 2026-11-16)؛ اجرا NOT_RUN', 10, 'middle', '#78909c'))
m4 = svg(960, 580,
    'نمودار مسیر ترافیک HW در برابر CPU درس M4 با الزام‌های L3HW',
    'بسته ورودی اول بررسی می‌شود که آیا در هر دو پورت L3HW روشن است و مقصد پیشوند سندشده دارد؛ در این حالت سوییچ‌چیپ مسیریابی را در سخت‌افزار با سرعت سیم انجام می‌دهد. وگرنه بسته به CPU می‌رود که فایروال و NAT و مسیرهای باقی آنجا پردازش می‌شود. حافظه سخت‌افزار بین Fasttrack و ACL مشترک است و هر قانون ACL جای سه تا شش اتصال Fasttrack را می‌گیرد. شش الزام پیش از روشن‌کردن شامل فهرست مدل‌ها، روشن بودن هر دو پورت، پل vlan-filtering سخت‌افزاری، یک پل واحد، خاموش کردن موقت حین تغییرات لایه دو و نگارش حداقل ۷.۶ آمده است. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- M5 VPN architecture ----------------
b = []
# center tunnel
b.append(rect(330, 220, 300, 110, '#e8eaf6', '#1e88e5', 3))
b.append(text(480, 246, 'تونل site-to-site', 12, 'middle', '#0d47a1', 'bold'))
b.append(rect(345, 258, 270, 30, '#ffffff', '#1e88e5', 1))
b.append(text(480, 278, 'گزینهٔ ۱: WireGuard (کلید عمومی/خصوصی)', 10, 'middle', '#0d47a1'))
b.append(rect(345, 292, 270, 30, '#ffffff', '#43a047', 1))
b.append(text(480, 312, 'گزینهٔ ۲: IPsec/IKEv2 (peer/policy/proposal)', 10, 'middle', '#1b5e20'))
# branch (right)
b.append(rect(700, 150, 220, 130, '#fafafa', '#fb8c00', 3))
b.append(text(810, 176, 'شعبه — hEX (فرضی)', 12, 'middle', '#e65100', 'bold'))
b.append(text(810, 200, 'LAN: 192.168.20.0/24', 11, 'middle', '#37474f'))
b.append(text(810, 222, 'wg/ipsec peer + allowed-address', 10, 'middle', '#546e7a'))
b.append(text(810, 244, 'keepalive 25s (سند WireGuard)', 9, 'middle', '#78909c'))
b.append(text(810, 264, 'endpoint = مرکز', 10, 'middle', '#546e7a'))
# hq (left)
b.append(rect(40, 150, 220, 130, '#fafafa', '#1e88e5', 3))
b.append(text(150, 176, 'مرکز — RB5009 (فرضی)', 12, 'middle', '#0d47a1', 'bold'))
b.append(text(150, 200, 'LAN: 192.168.10.0/24', 11, 'middle', '#37474f'))
b.append(text(150, 222, 'peer + allowed-address متقابل', 10, 'middle', '#546e7a'))
b.append(text(150, 244, 'route متقابل دو سو', 10, 'middle', '#546e7a'))
b.append(text(150, 264, 'فایروال: accept قبل از drop', 10, 'middle', '#546e7a'))
# links
b.append(line(260, 215, 330, 250, '#1e88e5', 3))
b.append(line(330, 300, 260, 265, '#43a047', 3))
b.append(line(630, 250, 700, 215, '#1e88e5', 3))
b.append(line(630, 300, 700, 265, '#43a047', 3))
b.append(text(295, 240, 'wg/ipsec', 9, 'middle', '#455a64'))
b.append(text(665, 240, 'wg/ipsec', 9, 'middle', '#455a64'))
# cross routes
b.append(line(150, 280, 150, 300, '#6a1b9a', 2, '5,4'))
b.append(line(150, 300, 810, 300, '#6a1b9a', 2, '5,4'))
b.append(line(810, 300, 810, 280, '#6a1b9a', 2, '5,4'))
b.append(text(480, 292, 'مسیرهای متقابل: 192.168.20.0/24 ↔ 192.168.10.0/24', 10, 'middle', '#6a1b9a'))
# gotchas box
b.append(rect(60, 370, 840, 130, '#fdecea', '#d32f2f', 2))
b.append(text(480, 394, 'تله‌های سندشده (هر دو گزینه)', 12, 'middle', '#d32f2f', 'bold'))
gotchas = ['WireGuard: فایروال پیش‌فرض جلوی برقراری تونل → accept قبل از drop (سند رسمی)',
           'IPsec: masquerade تونل را می‌شکند → accept/bypass بالای همهٔ NAT (سند رسمی)',
           'IPsec: Fasttrack از روی policy می‌گذرد → accept قبل از Fasttrack یا raw notrack',
           'هشدار رسمی: از PSK پرهیز؛ DH Group 19 پیشنهاد؛ IPsec حساس به تغییر زمان',
           'wg-export شامل IP/route/firewall نیست — روی مقصد جدا تنظیم شود']
for gi, g in enumerate(gotchas):
    b.append(text(90, 418 + gi * 16, g, 10, 'start', '#616161'))
b.append(text(480, 533, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — دستورها از اسناد رسمی (دسترسی 2026-11-17)؛ اجرا NOT_RUN', 10, 'middle', '#78909c'))
m5 = svg(960, 560,
    'نمودار معماری تونل شعبه-مرکز درس M5 با دو گزینهٔ WireGuard و IPsec',
    'شعبه با روتر hEX و شبکهٔ ۱۹۲.۱۶۸.۲۰ و مرکز با RB5009 و شبکهٔ ۱۹۲.۱۶۸.۱۰ با یک تونل بین خودشان وصل شده‌اند. دو گزینهٔ سندشده روی تونل نمایش داده شده: WireGuard با کلید عمومی و خصوصی و allowed-address و keepalive، یا IPsec با peer و policy و proposal. پنج تلهٔ سندشده پایین نمودار آمده: فایروال پیش‌فرض جلوی WireGuard، شکستن تونل با masquerade در IPsec، گذر Fasttrack از روی policy، هشدار PSK و حساسیت زمانی. مسیرهای متقابل دو شبکه با خط‌چین بنفش رسم شده است. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- M6 dual-WAN failover ----------------
b = []
# title states
b.append(text(300, 40, 'حالت عادی — primary', 13, 'middle', '#2e7d32', 'bold'))
b.append(text(660, 40, 'بعد از قطع WAN-A — backup فعال', 13, 'middle', '#e65100', 'bold'))
# center router
b.append(rect(390, 200, 180, 80, '#fafafa', '#0d47a1', 3))
b.append(text(480, 230, 'hEX (RB750Gr3)', 12, 'middle', '#0d47a1', 'bold'))
b.append(text(480, 254, 'LAN: 192.168.88.0/24', 10, 'middle', '#546e7a'))
# WAN-A (top-left) primary green
b.append(rect(60, 130, 180, 64, '#fafafa', '#43a047', 3))
b.append(text(150, 154, 'WAN-A — ISP-A', 12, 'middle', '#2e7d32', 'bold'))
b.append(text(150, 176, 'gateway فرضی 10.111.0.1 — distance 1', 10, 'middle', '#37474f'))
# WAN-B (top-right) backup gray->active dashed after failure
b.append(rect(620, 130, 180, 64, '#fafafa', '#78909c', 3))
b.append(text(710, 154, 'WAN-B — ISP-B', 12, 'middle', '#546e7a', 'bold'))
b.append(text(710, 176, 'gateway فرضی 10.112.0.1 — distance 2', 10, 'middle', '#37474f'))
# test hosts
b.append(rect(60, 300, 180, 56, '#e8f5e9', '#43a047', 2))
b.append(text(150, 322, 'میزبان تست: 8.8.8.8', 11, 'middle', '#2e7d32'))
b.append(text(150, 340, 'scope=10 — check-gateway', 9, 'middle', '#546e7a'))
b.append(rect(620, 300, 180, 56, '#fff3e0', '#fb8c00', 2))
b.append(text(710, 322, 'میزبان تست: 8.8.4.4', 11, 'middle', '#e65100'))
b.append(text(710, 340, 'scope=10 — check-gateway', 9, 'middle', '#546e7a'))
# links normal state
b.append(line(240, 162, 390, 220, '#43a047', 4))
b.append(line(620, 162, 570, 220, '#78909c', 3, '8,6'))
b.append(line(150, 194, 150, 300, '#43a047', 2))
b.append(line(710, 194, 710, 300, '#78909c', 2))
b.append(text(300, 185, 'primary — distance 1', 10, 'middle', '#2e7d32', 'bold'))
b.append(text(600, 185, 'backup — distance 2', 10, 'middle', '#546e7a'))
# LAN below
b.append(rect(390, 360, 180, 60, '#fafafa', '#1e88e5', 2))
b.append(text(480, 386, 'LAN کاربران', 11, 'middle', '#0d47a1'))
b.append(text(480, 406, '192.168.88.0/24', 10, 'middle', '#546e7a'))
b.append(line(480, 280, 480, 360, '#37474f', 3))
# after-failure panel
b.append(rect(60, 440, 840, 56, '#fdecea', '#d32f2f', 2))
b.append(text(480, 462, 'بعد از قطع WAN-A: مسیر primary از دسترس (check-gateway به 8.8.8.8) → مسیر backup فعال می‌شود', 11, 'middle', '#d32f2f', 'bold'))
b.append(text(480, 482, 'اتصال‌های برقرار حین سوییچ شکسته می‌شوند (رفتار موردانتظار این الگو) — DNS cache هم flush شود', 10, 'middle', '#616161'))
b.append(text(480, 533, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — الگوی عیناً از سند رسمی Failover (دسترسی 2026-11-17)؛ اجرا NOT_RUN', 10, 'middle', '#78909c'))
m6 = svg(960, 560,
    'نمودار dual-WAN و failover درس M6 با دو WAN و میزبان‌های تست',
    'روتر hEX با دو خروجی اینترنت: WAN-A به عنوان primary با distance یک که میزبان تست هشت‌هشت‌هشت‌هشت از طریق آن مانیتور می‌شود و WAN-B به عنوان پشتیبان با distance دو و میزبان تست هشت‌هشت‌چهار‌چهار. مسیرهای میزبان با scope ده تعریف شده‌اند و مسیرهای default با target-scope یازده به‌طور recursive از طریق میزبان‌ها حل می‌شوند؛ بدون این مسیرها هر دو default غیرفعال می‌مانند. بعد از قطع WAN-A مسیر پشتیبان فعال می‌شود و اتصال‌های برقرار می‌شکنند که در چک‌لیست پذیرش ثبت شده است. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- S5 uplink/trunk ----------------
b = []
# floor switch (left)
b.append(rect(60, 130, 300, 190, '#fafafa', '#fb8c00', 3))
b.append(text(210, 156, 'سوئیچ طبقه — CRS112-8P-4S-IN', 12, 'middle', '#e65100', 'bold'))
floors = [('۵ کاربر — VLAN10 (ether1-5)', 185), ('۲ دوربین — VLAN20 (ether6-7)', 215), ('آپ‌لینک ترانک — ether8 فقط-تگ‌دار', 245), ('مدیریت — VLAN88 (mgmt88)', 275)]
for t, y in floors:
    b.append(text(210, y, t, 10, 'middle', '#37474f'))
# core switch (right)
b.append(rect(600, 130, 300, 190, '#fafafa', '#1e88e5', 3))
b.append(text(750, 156, 'سوئیچ مرکز — CRS326-24G-2S+RM', 12, 'middle', '#0d47a1', 'bold'))
cores = [('کاربر آزمون — VLAN10 (ether1)', 185), ('دوربین آزمون — VLAN20 (ether2)', 215), ('ترانک ورودی — ether24', 245), ('مدیریت — VLAN88 (mgmt88)', 275)]
for t, y in cores:
    b.append(text(750, y, t, 10, 'middle', '#37474f'))
# trunk link
b.append(line(360, 225, 600, 225, '#43a047', 6))
b.append(text(480, 210, 'آپ‌لینک ترانک تگ‌دار', 12, 'middle', '#2e7d32', 'bold'))
b.append(text(480, 245, 'ترانک تگ‌دار: VLAN 10 / 20 / 88 — Cat6 1G (ether8)', 10, 'middle', '#2e7d32'))
b.append(text(480, 263, 'SFPهای 1G = رشد (10G نیستند) — الگوی S3 برای مدیوم', 9, 'middle', '#78909c'))
# capacity calc box
b.append(rect(60, 350, 840, 120, '#e3f2fd', '#1e88e5', 2))
b.append(text(480, 376, 'محاسبهٔ ظرفیت آپ‌لینک — واحد و جهت درست (فرض سناریو — UNKNOWN per-سازمان)', 12, 'middle', '#0d47a1', 'bold'))
calc = ['مبنا: ۷ پورت استفاده‌شده × 1Gbps = 7Gbps خام (۵ کاربر + ۲ دوربین)',
        '÷4 = 1.75Gbps یک‌جهته · ÷8 = 0.875Gbps یک‌جهته (فرض سناریو — UNKNOWN per-سازمان)',
        'نتیجه: 1G فقط انتهای 8:1 را پوشش می‌دهد (0.875≤1)؛ انتهای 4:1 را نه (1.75>1)',
        'واحد: 1Gbps = 125MB/s خام هر جهت — «250MB/s» یعنی 2Gbps یک‌جهته؛ full-duplex بودجه یک‌جهته را دوبرابر نمی‌کند']
for ci, c in enumerate(calc):
    b.append(text(90, 402 + ci * 16, c, 10, 'start', '#0d47a1'))
# red warning
b.append(rect(60, 490, 840, 44, '#fdecea', '#d32f2f', 2))
b.append(text(480, 512, 'هشدار: ترانک untagged = از دست دادن جداسازی VLANها و مدیریت — ممنوع | CRS112: SFPها 1G هستند نه 10G | VLAN-filtering روی CRS112 مسیر CPU است — بدون ادعای wire-speed', 11, 'middle', '#d32f2f', 'bold'))
b.append(text(480, 533, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — الگوی سند Bridging and Switching (دسترسی 2026-11-16)؛ اجرا NOT_RUN', 10, 'middle', '#78909c'))
s5 = svg(960, 560,
    'نمودار آپ‌لینک و ترانک درس S5 بین دو سوئیچ با محاسبهٔ ظرفیت',
    'دو سوئیچ با یک آپ‌لینک ترانک تگ‌دار وصل شده‌اند که VLANهای ده و بیست و هشتاد و هشت را حمل می‌کند. سوئیچ طبقه هشت پورت RJ45 و چهار پورت SFP یک گیگابیت دارد و هفت پورت استفاده‌شده سقف تئوریک هفت گیگابیت می‌سازد؛ با ضریب تجمعی فرض، نیازمندی یک‌جهته از یک‌وهفتادوپنج صدم گیگابیت در نسبت چهاربه‌یک تا هشتصدوهفتادوپنج هزارم گیگابیت در نسبت هشت‌به‌یک در می‌آید؛ یعنی آپ‌لینک یک گیگابیت فقط انتهای هشت‌به‌یک را پوشش می‌دهد و انتهای چهاربه‌یک را نه. پورت‌های SFP این مدل یک گیگابیت هستند نه ده گیگابیت و فیلترینگ VLAN روی این مدل از مسیر پردازنده می‌گذرد بدون ادعای سرعت سیم. هشدار قرمز نمودار می‌گوید ترانک بدون تگ ممنوع است چون جداسازی از بین می‌رود. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- S6 PSU three-check flow ----------------
b = []
b.append(text(480, 36, 'انتخاب PSU — سه چک سندشده‌محور', 13, 'middle', '#1a1a1a', 'bold'))
checks = [
    ('چک ۱: ولتاژ', 'af/at → 48V (netPower بدون مبدل داخلی: PSU 24V = خروجی 24V پسیو)', '#1e88e5'),
    ('چک ۲: توان اسمی', 'PSU ≥ demand×1.2 + مصرف سوئیچ (136W در این مبنا) — از برگهٔ رسمی PSU', '#43a047'),
    ('چک ۳: ورودی‌های مستقل', 'دو جک DC = دو PSU مستقل؛ سقف هر ورودی ≈67W', '#fb8c00'),
]
for ci, (title, sub, color) in enumerate(checks):
    y = 80 + ci * 86
    b.append(rect(120, y, 720, 66, '#fafafa', color, 2))
    b.append(text(200, y + 26, title, 12, 'middle', color, 'bold'))
    words, lines, cur = sub.split(' '), [], ''
    for w in words:
        if len(cur + ' ' + w) <= 52 or not cur:
            cur = (cur + ' ' + w).strip()
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    for li, ln in enumerate(lines[:2]):
        b.append(text(560, y + 20 + li * 16, ln, 10, 'middle', '#37474f'))
# decision box
b.append(rect(120, 350, 720, 90, '#fdecea', '#d32f2f', 2))
b.append(text(480, 374, 'حکم برای demand ‏120W این مبنا (تفسیر محافظه‌کارانهٔ سقف‌ها):', 11, 'middle', '#d32f2f', 'bold'))
verdicts = ['تک‌ورودی ≈67W → رد', 'دو ورودی ≈134W → مرزی (کسری حاشیه) → کاهش demand یا SKU بالاتر', 'PSU بزرگ‌تر: قبول مشروط به برگهٔ رسمی توان — UNKNOWN تا برگه']
for vi, v in enumerate(verdicts):
    b.append(text(480, 398 + vi * 14, v, 10, 'middle', '#616161'))
# PSU list box
b.append(rect(120, 460, 720, 62, '#e8f5e9', '#43a047', 2))
b.append(text(480, 482, 'PSUهای سازگار از صفحهٔ رسمی netPower 16P (فetch 2026-11-16):', 10, 'middle', '#2e7d32', 'bold'))
b.append(text(480, 502, '24HPOW · MTP250-53V47-OD · MTP250-26V94-OD · 48POW · 48V2A96W — توان اسمی: از برگهٔ رسمی همان PSU (UNKNOWN تا برگه)', 9, 'middle', '#546e7a'))
b.append(text(480, 533, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — اجرا NOT_RUN', 10, 'middle', '#78909c'))
s6 = svg(960, 560,
    'نمودار سه‌چک انتخاب PSU درس S6 با حکم مبنای ۱۲۰ وات',
    'انتخاب PSU سه چک دارد: اول ولتاژ که برای استاندارد af و at باید چهل‌وهشت ولت باشد چون netPower مبدل داخلی ندارد؛ دوم توان اسمی که باید حداقل صد و سی و شش وات باشد یعنی جمع تقاضا با حاشیه و مصرف خود سوئیچ و از برگهٔ رسمی همان PSU گرفته شود؛ سوم ورودی‌های مستقل که دو جک DC با سقف جریان هرکدام حدود شصت‌وهفت وات هستند و دو PSU مستقل بهتر از یک PSU واحد است. حکم مبنا: تک‌ورودی رد، دو ورودی مرزی، و PSU بزرگ‌تر مشروط به برگهٔ رسمی. فهرست PSUهای سازگار از صفحهٔ رسمی محصول آمده است. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- S5c loop/RSTP/LACP ----------------
b = []
# switch A (right) and B (left) with bond links
b.append(rect(620, 140, 240, 170, '#fafafa', '#0d47a1', 3))
b.append(text(740, 166, 'سوئیچ A', 12, 'middle', '#0d47a1', 'bold'))
b.append(text(740, 190, 'protocol-mode=rstp', 10, 'middle', '#37474f'))
b.append(text(740, 210, 'bond1: ether1+ether2', 10, 'middle', '#37474f'))
b.append(text(740, 230, 'lacp-rate=30s · MII', 10, 'middle', '#546e7a'))
b.append(rect(100, 140, 240, 170, '#fafafa', '#0d47a1', 3))
b.append(text(220, 166, 'سوئیچ B', 12, 'middle', '#0d47a1', 'bold'))
b.append(text(220, 190, 'protocol-mode=rstp', 10, 'middle', '#37474f'))
b.append(text(220, 210, 'bond1: ether1+ether2', 10, 'middle', '#37474f'))
b.append(text(220, 230, 'lacp-rate=30s · MII', 10, 'middle', '#546e7a'))
# two bond links
b.append(line(340, 185, 620, 185, '#43a047', 4))
b.append(text(480, 175, 'LACP عضو ۱', 10, 'middle', '#2e7d32'))
b.append(line(340, 225, 620, 225, '#43a047', 4))
b.append(text(480, 215, 'LACP عضو ۲', 10, 'middle', '#2e7d32'))
b.append(text(480, 240, 'bond1 — 802.3ad · hash=layer-2-and-3', 9, 'middle', '#78909c'))
# accidental loop patch (dashed, between upper free ports)
b.append(rect(300, 60, 360, 36, '#fff3e0', '#ef6c00', 2))
b.append(text(480, 82, 'وصلهٔ حلقوی تصادفی (فرض)', 10, 'middle', '#e65100'))
b.append(line(370, 96, 370, 140, '#ef6c00', 3, '6,4'))
b.append(line(590, 96, 590, 140, '#ef6c00', 3, '6,4'))
b.append(text(395, 128, 'بدون RSTP: طوفان broadcast', 10, 'middle', '#d32f2f', 'bold'))
b.append(text(565, 128, 'با RSTP: پورت alternate', 10, 'middle', '#2e7d32', 'bold'))
# side box: LACP rules
b.append(rect(60, 340, 840, 150, '#e3f2fd', '#1e88e5', 2))
b.append(text(480, 364, 'قواعد سند رسمی Bonding', 12, 'middle', '#0d47a1', 'bold'))
rules = ['همهٔ اعضا: هم‌سرعت + هم‌دوبلکس اجباری', 'IP از slaveها حذف شود قبل از bonding', 'link-monitoring=mii توصیه · ARP monitor توصیه نمی‌شود',
         'transmit-hash-policy: فقط layer-2 و layer-2-and-3 با 802.3ad سازگارند', 'layer-3-and-4: fully compliant نیست', 'HW offload باند: فقط چیپ‌های فهرست‌شده — per-model چک شود']
for ri, rq in enumerate(rules):
    b.append(text(90, 390 + ri * 17, rq, 10, 'start', '#0d47a1'))
b.append(text(480, 533, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — بر پایهٔ اسناد رسمی Bonding/Bridging (دسترسی 2026-11-16/17)؛ اجرا NOT_RUN', 10, 'middle', '#78909c'))
s5c = svg(960, 560,
    'نمودار درس S5: حلقه و RSTP و LACP بین دو سوئیچ',
    'دو سوئیچ با دو لینک موازی در حالت باند هشت‌ده‌سه‌اید یا LACP وصل شده‌اند که تنظیمات lacp-rate سی ثانیه و مانیتورینگ MII دارد. یک وصله حلقوی تصادفی بین دو پورت آزاد رسم شده که بدون RSTP طوفان برودکست می‌سازد و با RSTP پورت زائد بلوکه می‌شود. جعبه آبی قواعد سند رسمی باندینگ را فهرست می‌کند: هم‌سراعی اعضا، حذف IP از اسلیوها، مانیتورینگ MII، سازگاری هش لایه دو و دو، و چک HW آفلود بر اساس چیپ. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- S6c NAS/server upgrade ----------------
b = []
# NAS box (top-left)
b.append(rect(60, 80, 200, 100, '#fafafa', '#6a1b9a', 3))
b.append(text(160, 106, 'NAS (فرضی)', 12, 'middle', '#6a1b9a', 'bold'))
b.append(text(160, 130, 'پورت فعلی: 1G RJ45', 10, 'middle', '#546e7a'))
b.append(text(160, 150, 'ارتقا: 10G SFP+ یا 2.5G RJ45', 10, 'middle', '#37474f'))
b.append(text(160, 170, '(UNKNOWN تا برگهٔ NAS)', 9, 'middle', '#78909c'))
# server (bottom-left)
b.append(rect(60, 260, 200, 100, '#fafafa', '#1e88e5', 3))
b.append(text(160, 286, 'سرور (فرضی)', 12, 'middle', '#1e88e5', 'bold'))
b.append(text(160, 310, 'NIC third-party 10G SFP+', 10, 'middle', '#546e7a'))
b.append(text(160, 330, '(UNKNOWN تا برگهٔ سازنده)', 9, 'middle', '#78909c'))
b.append(text(160, 350, 'درایور نصب شود', 10, 'middle', '#546e7a'))
# CRS309 (center-right)
b.append(rect(430, 130, 260, 230, '#fafafa', '#0d47a1', 3))
b.append(text(560, 158, 'CRS309-1G-8S+IN', 13, 'middle', '#0d47a1', 'bold'))
b.append(text(560, 180, '۸× SFP+ 10G', 11, 'middle', '#0d47a1'))
b.append(text(560, 200, '۱× GbE مدیریت (PoE-in)', 10, 'middle', '#546e7a'))
b.append(text(560, 226, 'switching: 162 Gbps', 10, 'middle', '#37474f'))
b.append(text(560, 246, 'non-blocking: 81 Gbps', 10, 'middle', '#37474f'))
b.append(text(560, 266, 'CPU: 98DX8208 ARM 800MHz', 10, 'middle', '#546e7a'))
b.append(text(560, 286, 'RAM: 512 MB', 10, 'middle', '#546e7a'))
b.append(text(560, 306, 'dual boot: RouterOS / SwitchOS', 10, 'middle', '#546e7a'))
b.append(text(560, 330, '(fetch 2026-11-17 از صفحهٔ رسمی)', 9, 'middle', '#90a4ae'))
# DAC links
b.append(line(260, 130, 430, 170, '#43a047', 4))
b.append(text(345, 142, 'DAC 1m/3m', 10, 'middle', '#2e7d32', 'bold'))
b.append(line(260, 310, 430, 290, '#1e88e5', 4))
b.append(text(345, 302, 'DAC 3m', 10, 'middle', '#0d47a1', 'bold'))
# before/after comparison
b.append(rect(60, 400, 840, 44, '#e8f5e9', '#43a047', 2))
b.append(text(480, 426, 'قبل: 1G = 125 MB/s خام هر جهت → بعد: 10G = 1250 MB/s خام هر جهت (۱۰ برابر)', 12, 'middle', '#2e7d32', 'bold'))
# bottleneck note
b.append(rect(60, 460, 840, 44, '#fff3e0', '#ef6c00', 2))
b.append(text(480, 486, 'bottleneck بعدی معمولاً دیسک NAS/سرور است نه شبکه — iperf3 جدا از دیسک سنجیده شود', 10, 'middle', '#e65100'))
b.append(text(480, 533, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — CRS309 از صفحهٔ رسمی mikrotik.com (دسترسی 2026-11-17)؛ اجرا NOT_RUN', 10, 'middle', '#78909c'))
s6c = svg(960, 560,
    'نمودار ارتقای NAS/سرور به 10G درس S6 با CRS309',
    'NAS و سرور با کابل DAC مستقیم به سوئیچ CRS309 که هشت پورت SFP+ ده گیگابیت دارد وصل شده‌اند. سوئیچ ظرفیت سوئیچینگ صد و شصت و دو گیگابیت و throughput هشتاد و یک گیگابیت دارد. سرعت قبل ارتقا صد و بیست و پنج مگابایت بر ثانیه و بعد ارتقا هزار و دویست و پنجاه مگابایت بر ثانیه است. تلهٔ بعدی دیسک است نه شبکه. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- N1c office-design ladder ----------------
b = []
b.append(text(480, 36, 'شش گام طراحی شبکهٔ دفتر', 13, 'middle', '#1a1a1a', 'bold'))
steps_n1 = [
    ('۱. نیازسنجی', 'جدول demand: کاربر · دوربین · تلفن · NAS · AP', 90, '#1e88e5'),
    ('۲. توپولوژی ستاره‌ای', 'سوئیچ مرکز — همه به سوئیچ، سوئیچ به روتر', 190, '#6a1b9a'),
    ('۳. نقشهٔ پورت', 'جدول پورت/دستگاه/VLAN/PoE', 290, '#fb8c00'),
    ('۴. آدرس‌دهی و VLAN', 'جدول VLAN/subnet/gateway', 390, '#43a047'),
    ('۵. انتخاب تجهیز', 'سوئیچ پورت کافی · روتر ظرفیت · PoE budget', 490, '#0d47a1'),
    ('۶. مستندسازی و پذیرش', 'الگوی N4 — ماتریس تست مثبت/منفی', 590, '#d32f2f'),
]
for title, sub, y, color in steps_n1:
    b.append(rect(120, y - 30, 720, 66, '#fafafa', color, 2))
    b.append(text(180, y - 6, title, 12, 'middle', color, 'bold'))
    b.append(text(480, y - 4, sub, 10, 'middle', '#37474f'))
    if y < 590:
        b.append(line(480, y + 36, 480, y + 90, '#37474f', 2))
        b.append(text(494, y + 62, 'OK', 10, 'start', '#43a047', 'bold'))
b.append(text(120, 632, 'رشد ۲۴ ماه: +۲۰-۵۰٪ پورت — در سوئیچ و آپ‌لینک لحاظ شود', 10, 'middle', '#e65100'))
b.append(text(480, 662, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — اجرا NOT_RUN', 10, 'middle', '#78909c'))
n1c = svg(960, 690,
    'نمودار شش‌گام طراحی شبکهٔ دفتر درس N1',
    'شش گام طراحی: نیازسنجی با جدول تقاضا، توپولوژی ستاره‌ای با سوئیچ مرکز، نقشه پورت به پورت، آدرس‌دهی و VLAN، انتخاب تجهیز با PoE، و مستندسازی با آزمون پذیرش. هشدار رشد بیست‌وچهار ماهه در بالای نمودار آمده است. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- N2 rack/cable ----------------
b = []
# rack outline
b.append(rect(200, 60, 300, 420, '#fafafa', '#37474f', 3))
b.append(text(350, 88, 'رک ۱۲U (wall-mount)', 12, 'middle', '#37474f', 'bold'))
# rack units from top
rack_units = [
    ('U1', 'Patch Panel 24P Cat6', 100, 62, 300, 38, '#e3f2fd', '#1e88e5'),
    ('U2', 'فضای خالی', 100, 104, 300, 38, '#f5f5f5', '#90a4ae'),
    ('U3', 'CRS326-24G-2S+RM', 100, 146, 300, 38, '#e8f5e9', '#43a047'),
    ('U4', 'فضای خالی (تهویه)', 100, 188, 300, 38, '#f5f5f5', '#90a4ae'),
    ('U5', 'hEX (RB750Gr3)', 100, 230, 300, 38, '#e8f5e9', '#43a047'),
]
for u, t, x, y, w, h, fill, stroke in rack_units:
    b.append(rect(x, y, w, h, fill, stroke, 2))
    b.append(text(x + w // 2, y + h // 2 + 4, u + ': ' + t, 9, 'middle', '#37474f'))
# cable routing arrows
b.append(line(250, 100, 250, 146, '#43a047', 3))
b.append(text(262, 126, 'patch cable 0.5m', 8, 'middle', '#2e7d32'))
b.append(line(480, 165, 560, 165, '#fb8c00', 3))
b.append(text(575, 158, 'کابل دیواری Cat6', 9, 'middle', '#e65100'))
b.append(text(575, 172, 'از سقف/دیوار', 9, 'middle', '#78909c'))
# labeling example
b.append(rect(520, 350, 380, 130, '#e3f2fd', '#1e88e5', 2))
b.append(text(710, 374, 'الگوی برچسب‌گذاری', 11, 'middle', '#0d47a1', 'bold'))
labels = ['کابل دیواری: طبقه-اتاق-پورت (A-101-P01)', 'پورت سوئیچ: SW1:ether1', 'پورت patch panel: PP1:P01',
          'رزرو/سایر: R-CCTV-01']
for li, l in enumerate(labels):
    b.append(text(710, 398 + li * 16, l, 9, 'start', '#37474f'))
# cable separation warning
b.append(rect(60, 380, 380, 60, '#fdecea', '#d32f2f', 2))
b.append(text(250, 404, 'حداقل 30cm فاصله از کابل برق', 10, 'middle', '#d32f2f', 'bold'))
b.append(text(250, 424, '(تداخل الکترومغناطیسی)', 9, 'middle', '#8d6e63'))
# length rule
b.append(rect(60, 450, 840, 44, '#e8f5e9', '#43a047', 2))
b.append(text(480, 476, 'Cat6: حداکثر ۱۰۰ متر کل مسیر (patch panel تا کاربر شامل patch cable)', 11, 'middle', '#2e7d32', 'bold'))
b.append(text(480, 533, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — سناریو فرضی؛ اجرا NOT_RUN', 10, 'middle', '#78909c'))
n2 = svg(960, 560,
    'نمودار رک و کابل‌کشی درس N2 با چیدمان و برچسب‌گذاری',
    'رک دوازده یونیت با چیدمان از بالا به پایین: patch panel، فضای خالی، سوئیچ CRS326، فضای تهویه، روتر hEX، و فضای رشد. کابل‌های دیواری از سقف یا دیوار به patch panel می‌رسند و با patch cable کوتاه به سوئیچ وصل می‌شوند. الگوی برچسب‌گذاری شامل طبقه اتاق و شماره پورت است. کابل شبکه باید حداقل سی سانتی‌متر از کابل برق فاصله داشته باشد. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- N3c cable-test criteria ----------------
b = []
b.append(text(480, 36, 'پنج معیار تست کابل Cat6 permanent link (TIA/EIA-568.2-D)', 12, 'middle', '#1a1a1a', 'bold'))
criteria = [
    ('Wire-map', 'اتصال صحیح ۸ رشته — بدون miswire', '#43a047', 130),
    ('Length', 'طول هر جفت ≤ ۹۰ متر permanent link', '#1e88e5', 200),
    ('NEXT', 'تداخل جفت‌های مجاور ≥ حد Cat6', '#fb8c00', 270),
    ('Return Loss', 'بازتاب سیگنال ≥ حد Cat6', '#6a1b9a', 340),
    ('Prop. Delay', 'تأخیر انتشار ≤ ۵۵۵ ns', '#d32f2f', 410),
]
for title, desc, color, y in criteria:
    b.append(rect(100, y - 20, 760, 50, '#fafafa', color, 2))
    b.append(text(150, y + 4, title, 12, 'middle', color, 'bold'))
    b.append(text(200, y + 22, desc, 10, 'middle', '#37474f'))
b.append(text(480, 470, 'ابزار: certification tester (نه wire-map tester) — per-link جدا', 10, 'middle', '#37474f'))
b.append(text(480, 492, 'TIA/EIA-568.2-D استاندارد مرجع (دسترسی 2026-11-16)', 10, 'middle', '#90a4ae'))
b.append(text(480, 533, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — اجرا NOT_RUN', 10, 'middle', '#78909c'))
n3c = svg(960, 560,
    'نمودار پنج معیار تست کابل درس N3',
    'پنج معیار تست کابل Cat6 permanent link: وایر مپ اتصال صحیح هشت رشته؛ طول حداکثر نود متر؛ تداخل نزدیک با حد استاندارد؛ بازتاب سیگنال با حد استاندارد؛ و تأخیر انتشار حداکثر پانصد و پنجاه و پنج نانوثانیه. ابزار تستر certification لازم است نه تستر ساده وایرمپ. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))


# ---------------- N6c support selection (six-step flow) ----------------
b = []
b.append(text(480, 36, 'انتخاب پشتیبانی شبکه — فرایند شش‌گامی', 13, 'middle', '#1a1a1a', 'bold'))
steps = [
    ('۱ نیازسنجی', 'ساعات بحرانی · قطعی قابل‌تحمل · مهارت داخلی', '#1e88e5', 620),
    ('۲ گزینه‌ها', 'قرارداد · فریلنسر ساعتی · ترکیبی · بدون قرارداد', '#00897b', 515),
    ('۳ تطبیق', 'ماتریس نیاز × پوشش — هر ✗ یعنی گلوگاه', '#fb8c00', 410),
    ('۴ ارزیابی', 'معیار/وزن/شواهد — وزن‌ها قبل از استعلام', '#8d6e63', 305),
    ('۵ دورهٔ آزمایشی', 'معیار از-پیش‌نوشته · ۳۰-۹۰ روز فرض', '#43a047', 200),
    ('۶ بازنگری', 'جلسهٔ پایان دوره با جدول معیار — تمدید/اصلاح/تعویض', '#6a1b9a', 95),
]
for title, sub, color, x in steps:
    b.append(rect(x, 70, 95, 110, '#fafafa', color, 2))
    b.append(text(x + 47, 96, title, 11, 'middle', color, 'bold'))
    words, lines, cur = sub.split(' '), [], ''
    for w in words:
        if len(cur + ' ' + w) <= 18 or not cur:
            cur = (cur + ' ' + w).strip()
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    for li, ln in enumerate(lines[:4]):
        b.append(text(x + 47, 118 + li * 14, ln, 8, 'middle', '#37474f'))
    if x > 95:
        b.append(line(x, 125, x - 105, 125, '#90a4ae', 2, '4,3'))
# notes box
b.append(rect(95, 210, 770, 88, '#fff8e1', '#f9a825', 2))
b.append(text(480, 234, 'دو قاعدهٔ ثابت فرایند:', 11, 'middle', '#f57f17', 'bold'))
notes = ['قیمت فقط بعد از تکمیل جدول معیار وارد مقایسه می‌شود — نه قبل از آن',
         'نبود دادهٔ مانیتور برای سنجش «بهبود» یعنی UNKNOWN — حدس زده نمی‌شود']
for ni, n in enumerate(notes):
    b.append(text(480, 258 + ni * 16, n, 10, 'middle', '#5d4037'))
# selection decision box
b.append(rect(95, 320, 770, 74, '#e8f5e9', '#43a047', 2))
b.append(text(480, 344, 'حکم برای مبنای فرضی این درس ‏(رخداد ساده داخلی + عمیق بیرونی + ساعت بحرانی محدود):', 11, 'middle', '#2e7d32', 'bold'))
b.append(text(480, 366, 'گزینهٔ ترکیبی بیشترین تطبیق را دارد — حکم هر سازمان از ماتریس خودش می‌آید، نه کپی این جدول', 10, 'middle', '#37474f'))
b.append(text(480, 384, 'همهٔ اعداد این درس فرضی و برچسب‌دارند — انتخاب/خرید واقعی NOT_RUN', 9, 'middle', '#78909c'))
b.append(text(480, 533, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — الگوی درس‌های N همین سری؛ اجرا NOT_RUN', 10, 'middle', '#78909c'))
n6c = svg(960, 560,
    'نمودار فرایند شش‌گامی انتخاب پشتیبانی درس N6',
    'فرایند انتخاب پشتیبانی شبکه شش گام دارد: نیازسنجی با ساعات بحرانی و حداکثر قطعی قابل‌تحمل و مهارت داخلی؛ فهرست چهار گزینه یعنی قرارداد پیمانکار و فریلنسر ساعتی و ترکیبی و بدون قرارداد؛ ماتریس تطبیق نیاز با پوشش؛ ارزیابی ساختاریافته با جدول معیار و وزن و شواهد که وزن‌ها باید قبل از دیدن پیشنهادها نوشته شوند؛ دورهٔ آزمایشی کوتاه با معیار از پیش نوشته؛ و بازنگری دوره‌ای. دو قاعده ثابت: قیمت بعد از جدول معیار و نبود داده مانیتور یعنی نامعلوم. حکم مبنا فرضی: گزینه ترکیبی. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))

# ---------------- S4c VLAN on switch (L2) ----------------
b = []
b.append(text(480, 30, 'VLAN لایه۲ روی CRS326-24G-2S+RM — نقشهٔ پورت، ترانک و مرز لایه۲/۳', 12, 'middle', '#1a1a1a', 'bold'))
# router (top)
b.append(rect(330, 52, 300, 44, '#fafafa', '#6a1b9a', 2))
b.append(text(480, 70, 'روتر بالادستی — سمت روتر خارج از این درس', 10, 'middle', '#6a1b9a', 'bold'))
b.append(text(480, 86, 'پیکربندی مسیر روترِ دفتر: الگوی M2 · مسیریابی بین-VLAN: الگوی M4', 9, 'middle', '#78909c'))
# trunk link + boundary label
b.append(line(480, 96, 480, 128, '#43a047', 5))
b.append(text(560, 112, 'ether23 — ترانک فقط-تگ‌دار: VLAN 10/20/88', 10, 'middle', '#2e7d32', 'bold'))
b.append(text(355, 112, 'مرز لایه۲/لایه۳', 10, 'middle', '#6a1b9a'))
# switch body
b.append(rect(180, 128, 600, 210, '#fafafa', '#1e88e5', 3))
b.append(text(480, 152, 'CRS326-24G-2S+RM — bridge1 · vlan-filtering=yes · چیپ 98DX3236 (آفلود VLAN: سندشده)', 11, 'middle', '#0d47a1', 'bold'))
groups = [
    ('دفتر — ether1-10', 'access · pvid=10 · خروجی untagged', 'H1 H2 H3', '#1e88e5', 700),
    ('دوربین — ether11-14', 'access · pvid=20 · خروجی untagged', 'C1 C2', '#fb8c00', 480),
    ('مدیریت — ether24', 'access · pvid=88', 'M1', '#43a047', 260),
]
for title, sub, hosts, color, x in groups:
    b.append(rect(x - 95, 168, 190, 64, '#fafafa', color, 2))
    b.append(text(x, 188, title, 10, 'middle', color, 'bold'))
    b.append(text(x, 206, sub, 9, 'middle', '#37474f'))
    b.append(text(x, 224, hosts, 9, 'middle', '#546e7a'))
# cpu path inside switch
b.append(rect(180, 244, 600, 40, '#e8f5e9', '#43a047', 2))
b.append(text(480, 262, 'مسیر CPU مدیریت: bridge1 عضو تگ‌دار VLAN88 → mgmt88 → 192.168.88.2', 10, 'middle', '#2e7d32', 'bold'))
b.append(text(480, 278, 'جدول VLAN: سه ردیف (10/20/88) — vlan-ids با untagged اعضای access و tagged ترانک', 9, 'middle', '#546e7a'))
# free ports note
b.append(text(480, 296, 'ether15-22 آزاد (رشد) · sfp-sfpplus1/2 بدون پیکربندی در این درس', 9, 'middle', '#90a4ae'))
# hosts under groups
b.append(text(700, 362, 'H1/H2/H3 ← ether1-3', 9, 'middle', '#546e7a'))
b.append(text(480, 362, 'C1/C2 ← ether11-12', 9, 'middle', '#546e7a'))
b.append(text(260, 362, 'M1 ← ether24', 9, 'middle', '#546e7a'))
# L2/L3 warning box
b.append(rect(95, 390, 770, 74, '#fdecea', '#d32f2f', 2))
b.append(text(480, 414, 'مرز لایه۲/لایه۳ — تعهد صریح درس:', 11, 'middle', '#d32f2f', 'bold'))
b.append(text(480, 434, 'جداسازی لایه۲ = دو دامنهٔ پخش جدا ≠ فایروال · عبور بین-VLAN فقط از مسیریاب لایه۳ (tracert: گام اول = روتر)', 10, 'middle', '#616161'))
b.append(text(480, 452, 'سیاست بین-VLAN: الگوی M2/M4 — این سوئیچ فقط مرز لایه۲ را می‌سازد', 10, 'middle', '#616161'))
# recovery box
b.append(rect(95, 484, 770, 44, '#fff8e1', '#f9a825', 2))
b.append(text(480, 502, 'بازگشت امن: از جلسهٔ MAC-Winbox/Console → /interface bridge set bridge1 vlan-filtering=no — فیلترینگ آخرِ کار روشن می‌شود', 10, 'middle', '#5d4037'))
b.append(text(480, 533, 'نمودار مفهومی تألیفی TehNet — نه عکس واقعی — الگوی سند Bridging and Switching (دسترسی 2026-11-17)؛ اجرا NOT_RUN', 10, 'middle', '#78909c'))
s4c = svg(960, 560,
    'نمودار VLAN لایه۲ روی سوئیچ CRS326 درس S4 با نقشهٔ پورت و ترانک',
    'یک سوئیچ سی آر اس ۳۲۶ با فیلترینگ VLAN فعال روی پل، سه گروه پورت access دارد: ده پورت دفتر با پی‌وید ده، چهار پورت دوربین با پی‌وید بیست، و یک پورت مدیریت با پی‌وید هشتادوهشت. میزبان‌های اچ وان تا اچ سه و سی وان و سی دو و ام یک روی همین پورت‌ها هستند. پورت بیست‌وسه ترانک فقط تگ‌دار است که هر سه VLAN را به روتر بالادستی می‌برد و سمت روتر خارج از این درس است؛ همان‌جا مرز لایه۲ و لایه۳ است. مسیر مدیریت CPU با عضویت تگ‌دار خود پل در VLAN هشتادوهشت ساخته می‌شود و به آدرس صدونوددو وشش هشتادوهشت می‌رسد. نمودار تأکید می‌کند جداسازی لایه۲ دو دامنهٔ پخش جدا می‌سازد و فایروال نیست و عبور بین VLANها فقط از مسیریاب لایه۳ ممکن است. بازگشت امن از جلسهٔ مک‌وین‌باکس با خاموش‌کردن فیلترینگ ممکن است. این نمودار مفهومی و تألیفی TehNet است.',
    chr(10).join(b))

os.makedirs(OUT, exist_ok=True)
for name, content in (('tutorial-m2-topology.svg', m2), ('tutorial-m3-dhcp-dns-flow.svg', m3), ('tutorial-s2-poe-budget.svg', s2), ('tutorial-s3-module-decision.svg', s3), ('tutorial-n1-layer-ladder.svg', n1), ('tutorial-n4-acceptance-phases.svg', n4), ('tutorial-n2-monitoring-loop.svg', n2), ('tutorial-n3-sla-timeline.svg', n3), ('tutorial-n5-backup-export.svg', n5), ('tutorial-n6-incident-path.svg', n6), ('tutorial-m4-l3hw-flow.svg', m4), ('tutorial-m5-vpn-architecture.svg', m5), ('tutorial-m6-dual-wan-failover.svg', m6), ('tutorial-s5-uplink-trunk.svg', s5), ('tutorial-s6-psu-power.svg', s6), ('tutorial-s5-loop-rstp-lacp.svg', s5c), ('tutorial-s6-nas-upgrade.svg', s6c), ('tutorial-n1-office-design.svg', n1c), ('tutorial-n2-rack-cable.svg', n2), ('tutorial-n3-cable-test.svg', n3c), ('tutorial-n6-support-selection.svg', n6c), ('tutorial-s4-vlan-l2.svg', s4c)):
    p = os.path.join(OUT, name)
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('WROTE', name, len(content.encode('utf-8')), 'bytes')
