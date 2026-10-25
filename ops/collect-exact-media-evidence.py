"""Read native media approvals and protected hashes. Never write to WordPress.

Uses the existing SSH alias/native WP-CLI identity; no credentials are exported.
The PHP audit code is passed as a subprocess argument, not through shell expansion.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shlex
import subprocess

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--out', type=Path, required=True, help='Local JSON receipt path')
args = parser.parse_args()
sources = {name: (root / 'ops' / filename).read_text(encoding='utf-8') for name, filename in [
    ('audit', 'audit-exact-media.php'), ('state', 'shop-experience-state.php')]}
remote = r'''
import hashlib,json,subprocess,sys
sources=json.loads(sys.stdin.buffer.read())
assert subprocess.check_output(['docker','port','tehnet-wordpress','80/tcp']).decode().strip()=='127.0.0.1:18082'
def evaluate(name):
    p=subprocess.run(['docker','exec','tehnet-wordpress','php','/tmp/tn-store-review/wp-cli.phar','--allow-root','--path=/var/www/html','--user=AmirrezaGol','eval',sources[name].removeprefix('<?php')],capture_output=True,timeout=90)
    if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
    return json.loads(p.stdout)
before=evaluate('state')
value=evaluate('audit')
after=evaluate('state')
assert before==after,'Protected state changed during read-only audit; investigate concurrent edits'
value.update(protected_state_unchanged=True,protected_state_before=before,protected_state_after=after)
print(json.dumps(value))
'''
result = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10', '-o',
    'StrictHostKeyChecking=yes', 'netauto-main', 'python3 -c ' + shlex.quote(remote)],
    input=json.dumps(sources).encode('utf-8'), capture_output=True, timeout=290)
if result.returncode:
    raise RuntimeError((result.stdout + result.stderr).decode(errors='replace'))
value = json.loads(result.stdout)
value['audit_source_sha256'] = hashlib.sha256(sources['audit'].encode()).hexdigest()
value['state_source_sha256'] = hashlib.sha256(sources['state'].encode()).hexdigest()
args.out.parent.mkdir(parents=True, exist_ok=True)
args.out.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({'mode': value['mode'], 'products': len(value['products']),
    'approved_identity': sum(p['evidence_fields']['_tn_identity_reviewed'] == 'yes' for p in value['products']),
    'models': sum(p['model_available'] for p in value['products']),
    'parts': sum(p['parts_available'] for p in value['products']),
    'spins': sum(p['spin_frame_count'] > 0 for p in value['products']),
    'protected_state_unchanged': value['protected_state_unchanged'], 'receipt': str(args.out)}))
