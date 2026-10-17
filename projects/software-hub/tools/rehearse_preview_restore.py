"""Same-host Linux preview restore with preloaded image; never accepts an Iran migration."""
import argparse
from contextlib import closing
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import tempfile
import time

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--image',required=True)
parser.add_argument('--database',type=Path,required=True)
args=parser.parse_args()
if not re.fullmatch(r'sha256:[a-f0-9]{64}',args.image):parser.error('immutable image ID required')
started=time.perf_counter()
with tempfile.TemporaryDirectory(prefix='tehnet-preview-restore-') as temp:
    root=Path(temp);root.chmod(0o755)
    with closing(sqlite3.connect(args.database.resolve().as_uri()+'?mode=ro',uri=True)) as source:
        with closing(sqlite3.connect(root/'catalog.sqlite')) as target:
            source.backup(target)
            assert target.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    os.chmod(root/'catalog.sqlite',0o444)
    snapshot_seconds=time.perf_counter()-started
    check='''import json,subprocess,time,urllib.request
p=subprocess.Popen(['python','-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8000','--no-access-log'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for i in range(100):
        try:
            data=json.load(urllib.request.urlopen('http://127.0.0.1:8000/software/readyz',timeout=1));break
        except Exception:time.sleep(.1)
    else:raise AssertionError('startup timeout')
    assert data['status']=='ready' and not data['capabilities']['downloads']
    sources=json.load(urllib.request.urlopen('http://127.0.0.1:8000/software/v1/sources'))
    assert sources['total']==27 and not any(x['routing_enabled'] for x in sources['items'])
    for path in ['', 'static/style.css','static/ui.js','static/fonts/Vazirmatn-Regular.woff2','static/fonts/Vazirmatn-ExtraBold.woff2']:
        with urllib.request.urlopen('http://127.0.0.1:8000/software/'+path) as r:assert r.status==200 and len(r.read())>0
    print(json.dumps({'ready':True,'source_rows':sources['total'],'local_assets':True}))
finally:p.terminate();p.wait(timeout=5)
'''
    proc=subprocess.run(['docker','run','--rm','--network','none','--read-only','--cap-drop','ALL',
        '--security-opt','no-new-privileges:true','--tmpfs','/tmp:size=16777216',
        '-v',str(root)+':/data:ro',args.image,'python','-c',check],capture_output=True,text=True,timeout=45,check=True)
    print(json.dumps({'tested_at_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'same-host-Linux-preview-cold-process-preloaded-image',
        'image':args.image,'database_bytes':(root/'catalog.sqlite').stat().st_size,
        'snapshot_sha256':hashlib.sha256((root/'catalog.sqlite').read_bytes()).hexdigest(),
        'snapshot_seconds':snapshot_seconds,'total_seconds':time.perf_counter()-started,
        'network':'none','root_filesystem':'read-only','user':'image default 10001:10001',
        'result':json.loads(proc.stdout),'production_migration_accepted':False,
        'not_tested':['Iran target','WAN transfer','DNS or ingress cutover','private authentication','verified offline installs','post-write rollback']},indent=2))
