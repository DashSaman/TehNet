"""Actual shell flow with isolated fake services; GPG is tested separately."""
import os,shutil,sqlite3,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FAKE='''#!/usr/bin/env python3
import os,sys,pathlib,json,io,tarfile,signal
r=pathlib.Path(os.environ['ACTIVATION_FIXTURE']);a=sys.argv[1:];name=pathlib.Path(sys.argv[0]).name;scenario=os.environ['SCENARIO']
old='sha256:'+'a'*64;new='sha256:'+'b'*64
if name=='id':print('0');sys.exit(0)
if name in ['flock','sleep','chown','nginx','systemctl']:sys.exit(0)
if name=='curl':
 p=a[-1]
 if p.endswith('/readyz'):print('{"status":"ready"}')
 elif '-w' in a:print('404' if '/private/' in p else '503')
 sys.exit(0)
if name=='python3':
 if a[:2]==['-m','app.recovery']:
  if a[2]=='backup':
   if scenario=='backup':sys.exit(1)
   target=pathlib.Path(a[a.index('--destination')+1]);target.write_bytes(b'fixture');print(json.dumps({'cipher_sha256':'c'*64}))
  else:
   stage=pathlib.Path(a[a.index('--staging')+1]);stage.mkdir();(stage/'RESTORE_VERIFIED.json').write_text('{"verified":true}')
 else:print('c'*64) if 'cipher_sha256' in a[1] else None
 sys.exit(0)
if a[:1]==['inspect']:
 print(str(r/'opt/tehnet-software/releases/old/compose.yaml') if 'Labels' in a[2] else (r/'image').read_text());sys.exit(0)
if a[:1]==['port']:print('127.0.0.1:18082');sys.exit(0)
if a[:1]==['ps']:print('wordpress|original|original|loopback');sys.exit(0)
if a[:2]==['container','inspect']:sys.exit(1)
if a[:1]==['image'] or a[:1]==['stop'] or a[:1]==['rm']:sys.exit(0)
if a[:1]==['run']:print('fixture-probe');sys.exit(0)
if 'compose' in a:
 if 'up' in a:
  image=os.environ['TEHNET_SOFTWARE_IMAGE'];(r/'image').write_text(image)
  if image==new:
   (r/'srv/tehnet-software/auth/new-write').write_text('retain-new-auth-write')
   if scenario=='partial':sys.exit(1)
   if scenario=='signal':os.kill(os.getppid(),signal.SIGTERM)
 sys.exit(0)
if 'exec' in a and 'tehnet-db' in a:print('CREATE TABLE fixture(x);');sys.exit(0)
if 'exec' in a and 'tar' in a:
 out=io.BytesIO()
 with tarfile.open(fileobj=out,mode='w:gz') as t:
  info=tarfile.TarInfo('wp-content/file');info.size=8;t.addfile(info,io.BytesIO(b'original'))
 sys.stdout.buffer.write(out.getvalue());sys.exit(0)
if 'exec' in a:sys.exit(0)
sys.exit(99)
'''
@unittest.skipUnless(os.name=='posix' and shutil.which('bash'),'Linux shell integration fixture')
class EngineActivationTests(unittest.TestCase):
    def scenario(self,case):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t)
            for name in ['opt/tehnet-software/releases/new','opt/tehnet-software/releases/old','root/tehnet-backups','etc/nginx/snippets','etc/nginx/sites-enabled','opt/tehnet','srv/tehnet-software/auth','run/lock','keys','bin']:(r/name).mkdir(parents=True,exist_ok=True)
            release=r/'opt/tehnet-software/releases/new';(release/'deployment').mkdir()
            for name in ['opt/tehnet-software/releases/old/compose.yaml','opt/tehnet/compose.yaml','etc/nginx/sites-enabled/tehnet.ir.conf','etc/nginx/snippets/tehnet-software.conf']:(r/name).write_text('original')
            (release/'compose.engine.yaml').write_text('engine');(release/'deployment/nginx-engine.conf').write_text('privacy-off')
            (r/'image').write_text('sha256:'+'a'*64)
            for name in ['docker','curl','id','flock','sleep','chown','nginx','systemctl','python3']:
                target=r/'bin'/name;target.write_text(FAKE.replace('#!/usr/bin/env python3','#!'+shutil.which('python3'),1));target.chmod(0o755)
            script=(ROOT/'deployment/scripts/activate-engine.sh').read_text()
            for name in ['/opt/tehnet-software','/root/tehnet-backups','/etc/nginx/','/opt/tehnet/','/srv/tehnet-software','/run/lock/']:script=script.replace(name,str(r)+name)
            path=r/'activation.sh';path.write_text(script)
            result=subprocess.run(['bash',str(path),str(release),'sha256:'+'b'*64,str(r/'keys'),'A'*40,'--rehearse' if case=='rehearse' else '--activate'],capture_output=True,text=True,timeout=20,env={**os.environ,'PATH':str(r/'bin')+':'+os.environ['PATH'],'ACTIVATION_FIXTURE':str(r),'SCENARIO':case})
            text=result.stdout+result.stderr
            success=case in ['success','rehearse'];self.assertEqual(result.returncode==0,success,text)
            expected='b' if case=='success' else 'a';self.assertEqual((r/'image').read_text(),'sha256:'+expected*64,text)
            self.assertEqual((r/'etc/nginx/sites-enabled/tehnet.ir.conf').read_text(),'original')
            self.assertEqual((r/'etc/nginx/snippets/tehnet-software.conf').read_text(),'privacy-off' if case=='success' else 'original')
            if case!='backup':self.assertEqual((r/'srv/tehnet-software/auth/new-write').read_text(),'retain-new-auth-write')
            if not success:self.assertIn('ROLLBACK_PASS',text)
    def test_success_preserves_other_website_and_metadata(self):self.scenario('success')
    def test_rehearsal_returns_to_exact_old_image_without_state_restore(self):self.scenario('rehearse')
    def test_partial_new_container_failure_restores_old_code_and_keeps_new_write(self):self.scenario('partial')
    def test_backup_failure_restarts_old_container(self):self.scenario('backup')
    def test_sigterm_restores_old_code_and_keeps_new_write(self):self.scenario('signal')
