"""Check the exact-product evidence packet against original files/native receipts.

This validates recorded evidence and existing PHP contracts; it cannot prove
physical-stock identity, model licensing or a successful production UI test.
"""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess

root = Path(__file__).resolve().parents[1]
qa = root / 'qa/exact-media-2026-10-18'
def read(path):
    return json.loads(path.read_text(encoding='utf-8'))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
manifest_path = root / 'content/media/exact-product-review-2026-10-18/manifest.json'
manifest = read(manifest_path)
catalog = read(root / 'content/catalog/saieedshabake-2026-10-15.json')['products']
native = read(qa / 'native-inventory.json')
public = read(qa / 'public-records.json')
expected = {p['sku']: p['source_id'] for p in catalog}
products = manifest['products']
assert len(products) == len(expected) == 25
assert len({p['sku'] for p in products}) == 25
assert {p['sku']: p['source_id'] for p in products} == expected
assert {p['sku'] for p in native['products']} == set(expected)
assert len(native['products']) == len(public['products']) == 25
assert native['mode'] == 'read-only' and native['site'] == 'https://tehnet.ir/'
assert native['audit_source_sha256'] == sha(root / 'ops/audit-exact-media.php')
assert native['state_source_sha256'] == sha(root / 'ops/shop-experience-state.php')
assert native['protected_state_unchanged']
assert native['protected_state_before'] == native['protected_state_after']
assert native['blog_public'] == '0'
assert public['catalogue_sha256'] == sha(root / 'content/catalog/saieedshabake-2026-10-15.json')
assert len(public['source_responses']) == 2
assert all(r['status'] == 200 and r['products'] == 25 for r in public['source_responses'])
assert {p['sku']: p['source_id'] for p in public['products']} == expected
assert all(p['supplier_present'] for p in public['products'])
ni = {p['sku']: p for p in native['products']}
pi = {p['sku']: p for p in public['products']}
source_ids = {s['id'] for s in manifest['sources']}
assert len(source_ids) == len(manifest['sources']) == 17
assert all(s['url'].startswith('https://') and s['access'] for s in manifest['sources'])
images = set()
for p in products:
    n = ni[p['sku']]
    assert p['live_product_id'] == n['id'] == pi[p['sku']]['tehnet_product_id']
    assert not p['candidate_is_verified_stock_identity']
    assert not p['web_model_approved'] and p['model_file'] is None
    assert p['blockers'] and p['finding_fa'] and p['next_step_fa']
    assert set(p['manufacturer_source_ids']) <= source_ids
    assert not n['model_available'] and not n['parts_available'] and n['spin_frame_count'] == 0
    assert not n['purchasable'] and not any(n['evidence_fields'].values())
    assert p['native_model_available'] == n['model_available']
    assert p['native_parts_available'] == n['parts_available']
    assert p['native_spin_frame_count'] == n['spin_frame_count']
    assert not p['real_spin_frames']
    assert set(map(int, n['image_ids'])) == set(pi[p['sku']]['tehnet_image_ids'])
    for image in p['image_evidence']:
        path = root / image['file']
        assert path.resolve().is_relative_to((root / 'content/media').resolve())
        assert sha(path) == image['sha256'], image['file']
        images.add(image['sha256'])
assert len(images) == 23
assert manifest['measurement_caveat']['reported'] == '>0.8 micrometre'
assert manifest['qualified_exact_models_obtained'] == manifest['new_models_published'] == 0
assert manifest['production_writes'] is False and manifest['source_images_modified'] is False
contracts = []
php = root.parent / 'php-runtime/php.exe'
for name in ['product-evidence-unit.php', 'product-photos-unit.php']:
    result = subprocess.run([str(php), 'tests/' + name], cwd=root, capture_output=True, text=True, encoding='utf-8')
    assert result.returncode == 0, result.stdout + result.stderr
    contracts.append({'command': 'php tests/' + name, 'exit_code': result.returncode, 'output': (result.stdout + result.stderr).strip()})
lint = subprocess.run([str(php), '-l', 'ops/audit-exact-media.php'], cwd=root, capture_output=True, text=True, encoding='utf-8')
assert lint.returncode == 0, lint.stdout + lint.stderr
result = {'status': 'evidence-verified-publication-incomplete',
    'verified_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'catalogue_products': 25, 'public_api_products_each': 25, 'original_image_files_sha256_verified': 23,
    'manufacturer_research_sources': 17, 'native_verified_stock_identities': 0,
    'qualified_exact_models_obtained': 0, 'new_models_published': 0,
    'native_models': 0, 'native_parts': 0, 'native_spins': 0, 'protected_state_unchanged': True,
    'manifest_sha256': sha(manifest_path), 'native_receipt_sha256': sha(qa / 'native-inventory.json'),
    'public_receipt_sha256': sha(qa / 'public-records.json'), 'contracts': contracts,
    'php_audit_lint': lint.stdout.strip(), 'production_writes': False,
    'limitations': ['No exact physical-stock identity proved', 'No new licensed fully separated model obtained or published',
        'Linked BIM binary not downloaded or parsed', 'No new production UI acceptance run; prior browser limitation remains',
        'No stock, price, payment, order or indexing change', 'Research coverage does not prove absence of other models on the Internet']}
(qa / 'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print('EXACT_MEDIA_EVIDENCE=VERIFIED;25 source/native products;23 original SHA;17 sources;31 model+23 photo contracts;0 new models;PUBLICATION_INCOMPLETE')
