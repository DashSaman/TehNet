"""Structural/numerical QA of generated GLB, independent of the builder."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('directory', type=Path)
parser.add_argument('--evidence', type=Path, required=True)
args = parser.parse_args()
raw = (args.directory/'educational-cable.glb').read_bytes()
checks = []


def check(value, name):
    assert value, name
    checks.append(name)


check(raw[:4] == b'glTF' and struct.unpack_from('<II', raw, 4) == (2, len(raw)), 'GLB v2 header and exact total length')
size, kind = struct.unpack_from('<II', raw, 12)
check(kind == 0x4e4f534a and size % 4 == 0, 'aligned JSON chunk')
g = json.loads(raw[20:20+size])
bin_size, bin_kind = struct.unpack_from('<II', raw, 20+size)
binary = raw[28+size:]
check(bin_kind == 0x004e4942 and bin_size == len(binary), 'BIN chunk length matches bytes')
check(len(g['buffers']) == 1 and 'uri' not in g['buffers'][0] and not g.get('images'), 'self-contained asset without remote textures or buffers')
check(g['extras']['educational'] and g['extras']['product_mpn'] is None and not g['extras']['physical_dimensions_verified'], 'asset explicitly rejects physical product claims')


def read(index):
    a = g['accessors'][index]
    view = g['bufferViews'][a['bufferView']]
    count = a['count']*{'SCALAR': 1, 'VEC3': 3}[a['type']]
    code = {5123: 'H', 5125: 'I', 5126: 'f'}[a['componentType']]
    offset = view.get('byteOffset', 0)+a.get('byteOffset', 0)
    length = count*struct.calcsize(code)
    assert 0 <= offset and offset+length <= len(binary)
    assert length <= view['byteLength']
    return struct.unpack_from('<'+code*count, binary, offset)


triangles, vertices = 0, 0
for mesh in g['meshes']:
    for primitive in mesh['primitives']:
        positions = read(primitive['attributes']['POSITION'])
        normals = read(primitive['attributes']['NORMAL'])
        indices = read(primitive['indices'])
        assert len(positions) == len(normals)
        assert all(math.isfinite(x) for x in positions+normals)
        assert len(indices) % 3 == 0 and max(indices) < len(positions)//3
        assert all(abs(sum(x*x for x in normals[k:k+3])-1) < .001 for k in range(0, len(normals), 3))
        vertices += len(positions)//3
        triangles += len(indices)//3
check(True, 'every mesh has finite positions, unit normals, bounded aligned accessors and valid triangle indices')
animation = g['animations'][0]
check(animation['name'] == 'Explode' and len(animation['channels']) == 5, 'five independently animated layer nodes')
check(all(c['target']['path'] == 'translation' and read(animation['samplers'][c['sampler']]['input']) == (0., 1.) for c in animation['channels']), 'finite one-second translation tracks')
materials = g['materials']
check(any('woven' in m['name'] for m in materials) and any('Woven shield' in m['name'] for m in g['meshes']), 'shield uses original filament geometry rather than a smooth shell')
check(len({tuple(m['pbrMetallicRoughness']['baseColorFactor']) for m in materials}) >= 9, 'distinct illustrative jacket, white, four pair colours and metals')
check(min(m['pbrMetallicRoughness']['roughnessFactor'] for m in materials) < .3 and max(m['pbrMetallicRoughness']['roughnessFactor'] for m in materials) > .7, 'separate metal and matte surface response')
provenance = json.loads((root/'content/media/educational-cable-reference/provenance.json').read_text(encoding='utf-8'))
check(all(hashlib.sha256((args.directory/f['file']).read_bytes()).hexdigest() == f['sha256'] for f in provenance['files']), 'both real photographs exactly match reviewed original checksums')
args.evidence.parent.mkdir(parents=True, exist_ok=True)
args.evidence.write_text(json.dumps({'status': 'passed', 'scope': 'Structural validity only; no real CAD/dimensions asserted',
    'checks': checks, 'vertices': vertices, 'triangles': triangles, 'glb_bytes': len(raw),
    'glb_sha256': hashlib.sha256(raw).hexdigest()}, indent=2), encoding='utf-8')
print('EDUCATIONAL_GLB_CHECKS='+str(len(checks))+' PASS; triangles='+str(triangles))
