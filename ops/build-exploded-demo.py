"""Original normalized cable teaching model, never manufacturer CAD.

Reference photograph bytes remain unchanged. They do not establish the
identity, dimensions or materials of this geometry or any commercial SKU.
"""
from pathlib import Path
import argparse
import hashlib
import html
import json
import math
import shutil
import struct

ROOT = Path(__file__).resolve().parents[1]
TAU = math.tau


def unit(v):
    length = math.sqrt(sum(x*x for x in v))
    return [x/length for x in v]


def cross(a, b):
    return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]


def horizontal(v):
    # Proper rotation preserving winding: cable axis becomes world X.
    return [v[1], -v[0], v[2]]


class Cable:
    def __init__(self):
        self.g = {
            'asset': {'version': '2.0', 'generator': 'TehNet original educational cable v2; normalized units, not product CAD'},
            'scene': 0, 'scenes': [{'nodes': []}], 'nodes': [], 'meshes': [],
            'materials': [], 'buffers': [], 'bufferViews': [], 'accessors': [], 'animations': [],
            'extras': {'educational': True, 'physical_dimensions_verified': False, 'product_mpn': None},
        }
        self.binary = bytearray()

    def accessor(self, values, components=3, indices=False):
        while len(self.binary) % 4:
            self.binary.append(0)
        kind = (5123 if max(values) < 65536 else 5125) if indices else 5126
        fmt = {5123: 'H', 5125: 'I', 5126: 'f'}[kind]
        start = len(self.binary)
        self.binary.extend(struct.pack('<'+fmt*len(values), *values))
        view = len(self.g['bufferViews'])
        self.g['bufferViews'].append({'buffer': 0, 'byteOffset': start, 'byteLength': len(self.binary)-start})
        a = {'bufferView': view, 'componentType': kind, 'count': len(values)//components,
             'type': {1: 'SCALAR', 3: 'VEC3'}[components]}
        if not indices:
            a.update(min=[min(values[k::components]) for k in range(components)],
                     max=[max(values[k::components]) for k in range(components)])
        self.g['accessors'].append(a)
        return len(self.g['accessors'])-1

    def material(self, name, color, metallic=0, roughness=.5):
        self.g['materials'].append({'name': name, 'doubleSided': True,
            'pbrMetallicRoughness': {'baseColorFactor': color+[1], 'metallicFactor': metallic, 'roughnessFactor': roughness}})
        return len(self.g['materials'])-1

    def attach(self, parent, name, geometry, material):
        positions, normals, indices = geometry
        mesh = len(self.g['meshes'])
        self.g['meshes'].append({'name': name, 'primitives': [{
            'attributes': {'POSITION': self.accessor(positions), 'NORMAL': self.accessor(normals)},
            'indices': self.accessor(indices, 1, True), 'material': material}]})
        node = len(self.g['nodes'])
        self.g['nodes'].append({'name': name, 'mesh': mesh})
        self.g['nodes'][parent]['children'].append(node)

    def write(self, target):
        self.g['buffers'] = [{'byteLength': len(self.binary)}]
        j = json.dumps(self.g, separators=(',', ':')).encode()
        j += b' '*(-len(j) % 4)
        self.binary.extend(b'\0'*(-len(self.binary) % 4))
        glb = (b'glTF'+struct.pack('<II', 2, 28+len(j)+len(self.binary))
               +struct.pack('<II', len(j), 0x4e4f534a)+j
               +struct.pack('<II', len(self.binary), 0x004e4942)+self.binary)
        target.write_bytes(glb)
        return glb


class Geometry:
    """Combine capped sweeps into one mesh to limit draw calls."""
    def __init__(self):
        self.positions, self.normals, self.indices = [], [], []

    def vertex(self, position, normal):
        self.positions.extend(horizontal(position))
        self.normals.extend(horizontal(normal))

    def data(self):
        return self.positions, self.normals, self.indices

    def tube(self, radius, lower, upper, path=lambda y: (0, 0), inner=None,
             segments=32, steps=1, start=0, span=TAU, profile=None, caps=True):
        def frame(y):
            cx, cz = path(y)
            left, right = path(y-.0001), path(y+.0001)
            t = unit([(right[0]-left[0])/.0002, 1, (right[1]-left[1])/.0002])
            u = unit([t[1], -t[0], 0])
            return [cx, y, cz], t, u, cross(u, t)

        def point(y, theta, r, surface):
            c, _, u, v = frame(y)
            r += profile(y, theta) if profile and surface else 0
            return [c[k]+r*(u[k]*math.cos(theta)+v[k]*math.sin(theta)) for k in range(3)]

        for r, sign in [(radius, 1)]+([(inner, -1)] if inner else []):
            base = len(self.positions)//3
            for row in range(steps+1):
                y = lower+(upper-lower)*row/steps
                for col in range(segments+1):
                    angle = start+span*col/segments
                    p = point(y, angle, r, sign == 1)
                    dy = [b-a for a, b in zip(point(y-.0001, angle, r, sign == 1), point(y+.0001, angle, r, sign == 1))]
                    da = [b-a for a, b in zip(point(y, angle-.0001, r, sign == 1), point(y, angle+.0001, r, sign == 1))]
                    n = unit(cross(dy, da))
                    self.vertex(p, [sign*x for x in n])
            for row in range(steps):
                for col in range(segments):
                    a = base+row*(segments+1)+col
                    b = a+segments+1
                    self.indices.extend([a, b, a+1, a+1, b, b+1] if sign == 1 else [a, a+1, b, a+1, b+1, b])
        if caps:
            for y, sign in [(lower, -1), (upper, 1)]:
                _, tangent, _, _ = frame(y)
                normal = [sign*x for x in tangent]
                base = len(self.positions)//3
                for col in range(segments+1):
                    angle = start+span*col/segments
                    self.vertex(point(y, angle, radius, True), normal)
                    self.vertex(point(y, angle, inner or 0, False), normal)
                for col in range(segments):
                    a = base+2*col
                    face = [a, a+2, a+1]
                    if inner:
                        face += [a+1, a+2, a+3]
                    self.indices.extend(face if sign == -1 else [face[k+j] for k in range(0, len(face), 3) for j in [0, 2, 1]])


DEFINITIONS = [
    ('jacket', 'روکش بیرونی', 'روکش ماتِ این مدل، محافظ بیرونی کابل را نمایش می‌دهد. انتهای آن باز است تا ساختار داخلی دیده شود؛ جنس و ضخامتِ کالای واقعی به دیتاشیت همان شماره فنی نیاز دارد.'),
    ('braid', 'شیلد بافته‌شده', 'دو دسته رشتهٔ مارپیچ در جهت‌های مخالف، ظاهر بافت فلزی را می‌سازند. تعداد رشته‌ها و تراکم بافت در این مدل آموزشی انتخاب شده‌اند و مشخصات یک کالای واقعی نیستند.'),
    ('foils', 'فویل زوج‌ها', 'چهار پوشش نازک با سطح نامنظم، جای فویل‌های پیرامون زوج‌ها را توضیح می‌دهند. ظاهر نقره‌ای، ترکیب و ضخامت واقعی فویل را اثبات نمی‌کند.'),
    ('insulation', 'عایق و زوج‌سیم‌ها', 'زوج‌های آبی، نارنجی، سبز و قهوه‌ای همراه رشته‌های سفیدِ راه‌دار نمایش داده شده‌اند. گام تاب، جنس عایق و ابعاد این هندسه برای آموزش انتخاب شده‌اند.'),
    ('conductors', 'هادی‌ها', 'انتهای هادی‌ها با سطح فلزی و رنگ مسی دیده می‌شود. از رنگ یا مدل سه‌بعدی نمی‌توان جنس، خلوص، AWG یا قطر واقعی یک محصول را نتیجه گرفت.'),
]


def build_model(out):
    model = Cable()
    jacket = model.material('Illustrative matte grey jacket', [.31, .33, .35], roughness=.74)
    braid = model.material('Illustrative woven silver strands', [.65, .68, .71], 1, .29)
    foil = model.material('Illustrative rippled foil', [.72, .74, .77], 1, .22)
    copper = model.material('Illustrative copper tone; not a material certificate', [.90, .48, .22], 1, .30)
    white = model.material('Illustrative white insulation', [.86, .87, .84], roughness=.47)
    pair_colors = [model.material(name+' insulation', c, roughness=.41) for name, c in [
        ('Blue', [.025, .17, .47]), ('Orange', [.92, .20, .025]),
        ('Green', [.025, .35, .12]), ('Brown', [.21, .075, .028])]]
    groups, parts, samplers, channels = [], [], [], []
    times = model.accessor([0, 1], 1)
    for i, (name, label, description) in enumerate(DEFINITIONS):
        node = len(model.g['nodes'])
        model.g['nodes'].append({'name': name, 'children': []})
        model.g['scenes'][0]['nodes'].append(node)
        groups.append(node)
        target = [0, (i-2)*1.12, 0]
        samplers.append({'input': times, 'output': model.accessor([0, 0, 0]+target), 'interpolation': 'LINEAR'})
        channels.append({'sampler': i, 'target': {'node': node, 'path': 'translation'}})
        parts.append({'name': label, 'node': name, 'description': description,
            'material': 'جنس واقعی تأیید نشده؛ وابسته به شماره فنی',
            'source': 'https://tehnet.ir/technical-methodology/', 'target': target, 'measurements': []})

    shell = Geometry()
    shell.tube(.56, -2.25, .12, inner=.519, steps=12, segments=64,
               profile=lambda y, a: .0008*math.sin(y*90+a*27))
    model.attach(groups[0], 'Capped matte jacket', shell.data(), jacket)

    weave = Geometry()
    for direction in [-1, 1]:
        for carrier in range(12):
            for filament in range(2):
                phase = carrier*TAU/12+(filament-.5)*.025
                def path(y, direction=direction, phase=phase):
                    angle = phase+direction*y*3.3
                    r = .485+direction*.005*math.cos(y*3.3*24+phase*12)
                    return r*math.cos(angle), r*math.sin(angle)
                weave.tube(.006, -2.24, .66, path, steps=64, segments=6)
    model.attach(groups[1], 'Woven shield - 48 illustrative filaments', weave.data(), braid)

    for pair in range(4):
        angle = math.pi/4+pair*math.pi/2
        cx, cz = .26*math.cos(angle), .26*math.sin(angle)
        def pair_path(y, cx=cx, cz=cz):
            spread = max(0, y-.65)**2*.12
            return cx*(1+spread), cz*(1+spread)
        wrap = Geometry()
        wrap.tube(.184, -2.23, 1.15, pair_path, inner=.173, steps=80,
                  segments=40, start=math.pi*.88, span=math.pi*1.67,
                  profile=lambda y, a: .0019*math.sin(y*39+a*5)+.0008*math.sin(y*81-a*7))
        model.attach(groups[2], 'Rippled foil pair '+str(pair+1), wrap.data(), foil)
        for wire in range(2):
            phase = wire*math.pi
            def wire_path(y, phase=phase, pair=pair, pair_path=pair_path):
                x, z = pair_path(y)
                tail = max(0, y-1.1)
                t = y if y <= 1.1 else 1.1+.35*tail+.195*(1-math.exp(-tail/.3))
                twist = t*(4.5+pair*.29)+phase
                return x+.070*math.cos(twist), z+.070*math.sin(twist)
            insulation = Geometry()
            insulation.tube(.051, -2.22, 1.82+pair*.035, wire_path, inner=.029, steps=100, segments=20)
            model.attach(groups[3], 'Insulation pair '+str(pair+1)+' wire '+str(wire+1), insulation.data(), pair_colors[pair] if wire == 0 else white)
            if wire == 1:
                stripe = Geometry()
                stripe.tube(.0514, -2.22, 1.82+pair*.035, wire_path, steps=100, segments=4,
                            start=.4, span=.55, caps=False)
                model.attach(groups[3], 'Colour stripe pair '+str(pair+1), stripe.data(), pair_colors[pair])
            core = Geometry()
            core.tube(.0275, -2.22, 2.06+pair*.035, wire_path, steps=108, segments=16)
            model.attach(groups[4], 'Capped conductor pair '+str(pair+1)+' wire '+str(wire+1), core.data(), copper)

    model.g['animations'] = [{'name': 'Explode', 'samplers': samplers, 'channels': channels}]
    for part, node in zip(parts, groups):
        boxes = []
        for child in model.g['nodes'][node]['children']:
            mesh = model.g['meshes'][model.g['nodes'][child]['mesh']]
            accessor = model.g['accessors'][mesh['primitives'][0]['attributes']['POSITION']]
            boxes.append(accessor)
        # Normalized illustration coordinates, not physical measurements.
        part['illustration_bounds'] = [[min(b['min'][k] for b in boxes) for k in range(3)],
                                       [max(b['max'][k] for b in boxes) for k in range(3)]]
    glb = model.write(out/'educational-cable.glb')
    return {'mpn': 'EDUCATIONAL-NOT-A-PRODUCT', 'animation': 'Explode', 'parts': parts}, len(glb)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    out = parser.parse_args().out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    reference = ROOT/'content/media/educational-cable-reference'
    provenance = json.loads((reference/'provenance.json').read_text(encoding='utf-8'))
    for asset in provenance['files']:
        original = reference/asset['file']
        if hashlib.sha256(original.read_bytes()).hexdigest() != asset['sha256']:
            raise ValueError('Reference photograph checksum mismatch: '+asset['file'])
        shutil.copyfile(original, out/asset['file'])
    shutil.copyfile(reference/'provenance.json', out/'photo-provenance.json')
    data, size = build_model(out)
    template = (ROOT/'ops/visuals/cable-demo.html').read_text(encoding='utf-8')
    (out/'index.html').write_text(template.replace('@@PARTS@@', html.escape(json.dumps(data, ensure_ascii=False), quote=True)), encoding='utf-8')
    for name in ['cable-demo.css', 'cable-demo.js', 'cable-controls.js']:
        shutil.copyfile(ROOT/'ops/visuals'/name, out/name)
    for src, dest in [('assets/reviewed-model.js', 'reviewed-model.js'), ('assets/store.css', 'store.css'),
                      ('assets/vendor/model-viewer/model-viewer.min.js', 'model-viewer.min.js'),
                      ('assets/vendor/model-viewer/LICENSE', 'LICENSE-model-viewer'),
                      ('assets/vendor/model-viewer/PROVENANCE.json', 'model-viewer-provenance.json')]:
        shutil.copyfile(ROOT/'site/plugins/tehnet-store'/src, out/dest)
    (out/'README.fa.txt').write_text(
        'نمونهٔ آموزشی تهران نتورک؛ عکس‌های واقعیِ کابل Cat7 با منبع و مجوز عمومی هستند و عکس کالای فروشگاه نیستند. '
        'مدل سه‌بعدی، هندسهٔ تألیفی و غیرمقیاس است؛ CAD سازنده و بازسازی دقیق عکس نیست. ابعاد و مواد واقعی تأیید نشده‌اند. '
        'اجرا: python -m http.server 18084 --bind 127.0.0.1 --directory همین‌پوشه سپس http://localhost:18084 '
        'فایل‌ها محلی و بدون analytics هستند. حقوق تصاویر در photo-provenance.json و مجوز نمایشگر Apache-2.0 پیوست است.', encoding='utf-8')
    print('EDUCATIONAL_VISUAL_DEMO_BUILT; photographs=2; parts=5; physical claims=0; GLB bytes='+str(size))


if __name__ == '__main__':
    main()
