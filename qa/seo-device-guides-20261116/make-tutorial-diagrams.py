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

os.makedirs(OUT, exist_ok=True)
for name, content in (('tutorial-m2-topology.svg', m2), ('tutorial-m3-dhcp-dns-flow.svg', m3), ('tutorial-s2-poe-budget.svg', s2), ('tutorial-s3-module-decision.svg', s3), ('tutorial-n1-layer-ladder.svg', n1), ('tutorial-n4-acceptance-phases.svg', n4), ('tutorial-n2-monitoring-loop.svg', n2), ('tutorial-n3-sla-timeline.svg', n3)):
    p = os.path.join(OUT, name)
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('WROTE', name, len(content.encode('utf-8')), 'bytes')
