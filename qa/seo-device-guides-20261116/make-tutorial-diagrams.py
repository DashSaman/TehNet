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

os.makedirs(OUT, exist_ok=True)
for name, content in (('tutorial-m2-topology.svg', m2), ('tutorial-m3-dhcp-dns-flow.svg', m3), ('tutorial-s2-poe-budget.svg', s2)):
    p = os.path.join(OUT, name)
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('WROTE', name, len(content.encode('utf-8')), 'bytes')
