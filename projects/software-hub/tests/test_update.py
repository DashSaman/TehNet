"""Execute preview update and rollback against a sandbox, with real SQLite backup."""
from pathlib import Path
import os
import shutil
import sqlite3
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
FAKE='''#!/usr/bin/env python3
import io,os,pathlib,sys,tarfile
r=pathlib.Path(os.environ['UPDATE_FIXTURE']);name=pathlib.Path(sys.argv[0]).name;a=sys.argv[1:]
old='sha256:'+'a'*64;new='sha256:'+'b'*64
if name=='sleep':sys.exit(0)
if name=='curl':print('{"status":"ready"}');sys.exit(0)
if a[:1]==['inspect']:print((r/'image').read_text());sys.exit(0)
if a[:1]==['port']:print('127.0.0.1:18082');sys.exit(0)
if a[:1]==['ps']:print('wordpress|original|original|loopback');sys.exit(0)
if 'compose' in a:
    if 'up' in a:
        image=os.environ['TEHNET_SOFTWARE_IMAGE'];(r/'image').write_text(image)
        if image==new and os.environ['UPDATE_SCENARIO']=='partial':sys.exit(1)
    sys.exit(0)
if 'exec' in a and 'tehnet-db' in a:print('CREATE TABLE fixture(x);');sys.exit(0)
if 'exec' in a and 'tar' in a:
    out=io.BytesIO()
    with tarfile.open(fileobj=out,mode='w:gz') as t:
        b=b'original';info=tarfile.TarInfo('wp-content/file');info.size=len(b);t.addfile(info,io.BytesIO(b))
    sys.stdout.buffer.write(out.getvalue())
'''

@unittest.skipUnless(os.name=='posix' and shutil.which('bash'),'Linux shell integration fixture')
class UpdateTests(unittest.TestCase):
    def scenario(self,case):
        with tempfile.TemporaryDirectory() as temp:
            r=Path(temp)
            for p in ['opt/tehnet-software/releases/test','root/tehnet-backups','srv/tehnet-software/data','etc/nginx/sites-enabled','opt/tehnet','bin']:
                (r/p).mkdir(parents=True,exist_ok=True)
            for p in ['opt/tehnet/compose.yaml','opt/tehnet-software/releases/test/compose.yaml','etc/nginx/sites-enabled/tehnet.ir.conf']:
                (r/p).write_text('unchanged')
            db=sqlite3.connect(r/'srv/tehnet-software/data/catalog.sqlite');db.execute('CREATE TABLE original(id)');db.close()
            (r/'image').write_text('sha256:'+'a'*64)
            for name in ['docker','curl','sleep']:
                path=r/'bin'/name;path.write_text(FAKE);path.chmod(0o755)
            script=(ROOT/'deployment/scripts/update-preview.sh').read_text()
            for p in ['/opt/tehnet-software','/root/tehnet-backups','/srv/tehnet-software','/etc/nginx/','/opt/tehnet/']:
                script=script.replace(p,str(r)+p)
            path=r/'update.sh';path.write_text(script)
            result=subprocess.run(['bash',str(path),str(r/'opt/tehnet-software/releases/test'),'sha256:'+'b'*64],capture_output=True,text=True,timeout=20,
                env={**os.environ,'PATH':str(r/'bin')+':'+os.environ['PATH'],'UPDATE_FIXTURE':str(r),'UPDATE_SCENARIO':case})
            if case=='success':self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            else:
                self.assertNotEqual(result.returncode,0)
                self.assertIn('UPDATE_FAILED_ROLLED_BACK',result.stderr)
            self.assertEqual((r/'image').read_text(),'sha256:'+('b' if case=='success' else 'a')*64)
            self.assertEqual((r/'etc/nginx/sites-enabled/tehnet.ir.conf').read_text(),'unchanged')
            self.assertEqual(len(list((r/'root/tehnet-backups').glob('*/software.sqlite'))),1)
    def test_update_preserves_wordpress_and_backups(self):self.scenario('success')
    def test_partial_container_update_restores_previous_image(self):self.scenario('partial')
