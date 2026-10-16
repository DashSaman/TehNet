"""One bounded repair of four runtime directories created by the recorded release."""
from pathlib import Path
import json,shlex,subprocess
root=Path(__file__).resolve().parents[1];release=json.loads((root/'seo/remediation-2026-10-16/release.json').read_text())
remote=r'''
import pathlib,json,os,hashlib
d=pathlib.Path(DIRECTORY);m=json.loads((d/'release.json').read_text());base=pathlib.Path('/var/lib/docker/volumes/tehnet_tehnet-wp-data/_data/wp-content')
for n,sha in m['new'].items():assert hashlib.sha256((base/n).read_bytes()).hexdigest()==sha,'File drift before permission repair'
names=['mu-plugins','mu-plugins/tehnet-technical-resources','plugins/tehnet-store/assets/vendor','plugins/tehnet-store/assets/vendor/model-viewer'];records=[]
for n in names:
 p=base/n;s=p.stat();assert not p.is_symlink()and p.is_dir()and s.st_mode&0o777 in [0o700,0o755]
 records.append({'path':n,'before_mode':oct(s.st_mode&0o777),'before_uid':s.st_uid,'after_mode':'0o755','after_uid':33})
for n in names:os.chmod(base/n,0o755);os.chown(base/n,33,33)
result={'status':'repaired','scope':'Only four release-created public runtime directories; file bytes unchanged','directories':records};(d/'permissions-repair.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''.replace('DIRECTORY',repr(release['directory']))
r=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=10','-o','StrictHostKeyChecking=yes','netauto-main','python3 -c '+shlex.quote(remote)],capture_output=True,timeout=60)
if r.returncode:raise RuntimeError((r.stdout+r.stderr).decode(errors='replace'))
(root/'seo/remediation-2026-10-16/permissions-repair.json').write_bytes(r.stdout);print('PUBLIC_RUNTIME_DIRECTORY_PERMISSIONS_REPAIRED')
