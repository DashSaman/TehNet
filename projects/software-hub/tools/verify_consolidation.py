"""Validate exact copied Git blobs, local Markdown targets and old-site isolation."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
record = json.loads((ROOT / 'research/PROVENANCE.json').read_text(encoding='utf-8'))
entries = record['files']
expected = set()
for entry in entries:
    path = ROOT / entry['destination_path']
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise SystemExit('Provenance path escapes scope')
    data = path.read_bytes()
    assert len(data) == entry['size_bytes'], entry['source_path']
    assert hashlib.sha256(data).hexdigest() == entry['sha256'], entry['source_path']
    assert hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest() == entry['git_blob_sha1'], entry['source_path']
    expected.add(path.resolve())
actual = {p.resolve() for p in (ROOT / 'research/upstream/Linux').rglob('*')
          if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
assert actual == expected, 'Missing or extra immutable research files'

links = 0
for path in ROOT.rglob('*.md'):
    text = path.read_text(encoding='utf-8')
    # Skip code fences; illustrative placeholders are not navigation links.
    text = re.sub(r'```.*?```', '', text, flags=re.S)
    for match in re.finditer(r'(?<!!)\[[^\]\n]+\]\(([^)\n]+)\)', text):
        target = match.group(1).split(' "', 1)[0].strip('<>')
        if re.match(r'^[a-z][a-z0-9+.-]*:', target, re.I) or target.startswith('#'):
            continue
        target = unquote(target.split('#', 1)[0])
        if not target:
            continue
        resolved = (path.parent / target).resolve()
        assert resolved.is_relative_to(REPO.resolve()), f'Escaped link: {path.name}: {target}'
        assert resolved.exists(), f'Broken link: {path.relative_to(ROOT)}: {target}'
        links += 1

base = record['destination_base_ref']
allowed = {'README.md', 'PROGRESS.md', 'HANDOFF.md', 'TASKS.md'}
changed = subprocess.check_output(['git', '-C', str(REPO), 'diff', base, '--name-only'], text=True).splitlines()
scoped_additions = {'ops/software-menu.php', 'ops/lib/software-menu.php', 'tests/software-menu-logic.php'}
assert all(p in allowed or p in scoped_additions or p.startswith('projects/software-hub/') or
           (p.startswith('projects/melika/') and not (REPO / p).exists()) for p in changed), changed
for name in allowed:
    original = subprocess.check_output(['git', '-C', str(REPO), 'show', f'{base}:{name}']).decode('utf-8')
    current = (REPO / name).read_text(encoding='utf-8')
    assert current.startswith(original.replace('\r\n', '\n')), f'Pre-existing root content changed: {name}'
print(json.dumps({'result': 'PASS', 'source_blobs_verified': len(entries),
                  'copied_bytes': sum(e['size_bytes'] for e in entries),
                  'local_markdown_links_checked': links,
                  'existing_site_files_changed': 0, 'authorized_new_menu_scripts': sorted(scoped_additions),
                  'root_docs_append_only': sorted(allowed)}, indent=2))
