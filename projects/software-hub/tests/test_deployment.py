"""Run the real deployment flow in a temp filesystem with fake external services."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
FAKE='''#!/usr/bin/env python3
import io,json,os,pathlib,sys,tarfile
r=pathlib.Path(os.environ['DEPLOY_FIXTURE']); name=pathlib.Path(sys.argv[0]).name;a=sys.argv[1:]
scenario=os.environ['DEPLOY_SCENARIO']
if name in ['ss','systemctl','nginx','chown','sleep']: sys.exit(0)
if name=='curl':
    if scenario=='convergence' and '--resolve' in a and a[-1].endswith('/software/readyz') and not (r/'edge-converged').exists():
        (r/'edge-converged').write_text('first request still old worker');sys.exit(22)
    if '%{http_code}' in a: print('200' if scenario=='conflict' or not a[-1].endswith('/software/') else '404',end='')
    else: print('{"status":"ready"}')
    sys.exit(0)
if a[:1]==['port']: print('127.0.0.1:18082');sys.exit(0)
if a[:2]==['container','inspect']: sys.exit(1)
if a[:1]==['ps']: print('tehnet-wordpress|original|wordpress|127.0.0.1:18082');sys.exit(0)
if 'compose' in a:
    if 'up' in a:
        (r/'container').write_text('created')
        sys.exit(1 if scenario=='compose' else 0)
    if 'down' in a: (r/'container').unlink(missing_ok=True)
    sys.exit(0)
if 'exec' in a and 'tehnet-db' in a: print('CREATE TABLE fixture(x);');sys.exit(0)
if 'exec' in a and 'tar' in a:
    out=io.BytesIO()
    with tarfile.open(fileobj=out,mode='w:gz') as t:
        b=b'fixture';info=tarfile.TarInfo('wp-content/file');info.size=len(b);t.addfile(info,io.BytesIO(b))
    sys.stdout.buffer.write(out.getvalue());sys.exit(0)
if 'exec' in a and 'php' in a:
    if 'apply' in a: (r/'menu').write_text('owned');print('{"id":10,"created":true,"menu":3}')
    elif 'rollback' in a or 'rollback-owner' in a: (r/'menu').unlink(missing_ok=True);print('OK')
    else: print('{"primary":3,"items":[]}')
sys.exit(0)
'''


@unittest.skipUnless(os.name=='posix' and shutil.which('bash'),'Linux shell integration fixture')
class DeploymentTests(unittest.TestCase):
    def run_scenario(self,scenario):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);release=root/'opt/tehnet-software/releases/test';release.mkdir(parents=True)
            (root/'opt/tehnet').mkdir();(root/'opt/tehnet/compose.yaml').write_text('original')
            (root/'root/tehnet-backups').mkdir(parents=True)
            (root/'srv').mkdir()
            (root/'etc/nginx/sites-enabled').mkdir(parents=True);(root/'etc/nginx/snippets').mkdir()
            original='server {\n    server_name tehnet.ir www.tehnet.ir;\n    listen 443 ssl;\n}\nserver {\n    server_name tehnet.ir www.tehnet.ir;\n    listen 80;\n}\n'
            conf=root/'etc/nginx/sites-enabled/tehnet.ir.conf';conf.write_text(original)
            binary=root/'bin';binary.mkdir()
            for name in ['docker','curl','ss','nginx','systemctl','chown','sleep']:
                path=binary/name;path.write_text(FAKE);path.chmod(0o755)
            script=(ROOT/'deployment/scripts/deploy-preview.sh').read_text()
            for path in ['/opt/tehnet-software','/opt/tehnet/','/root/tehnet-backups','/srv/tehnet-software','/etc/nginx/']:
                script=script.replace(path,str(root)+path)
            points={'data':'docker run --rm --network none','snippet':'python3 - "$CONF"',
                    'reload':'# deployment-stage: edge-check',
                    'menu':'for path in / /learn/ /services/ /shop/ /contact/ /software/; do'}
            if scenario in points:
                script=script.replace(points[scenario],'false\n'+points[scenario],1)
            if scenario=='signal': script=script.replace(points['menu'],'kill -TERM $$\n'+points['menu'],1)
            path=root/'deploy.sh';path.write_text(script)
            env={**os.environ,'PATH':str(binary)+':'+os.environ['PATH'],'DEPLOY_FIXTURE':str(root),'DEPLOY_SCENARIO':scenario}
            result=subprocess.run(['bash',str(path),str(release),'sha256:'+'a'*64],env=env,capture_output=True,text=True,timeout=20)
            if scenario in ['success','convergence']:
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                data=conf.read_text()
                self.assertEqual(data.count('include '),1)
                self.assertNotIn('include ',data.split('\nserver {',1)[1])
                self.assertTrue((root/'menu').exists())
                self.assertTrue((root/'container').exists())
                return
            self.assertNotEqual(result.returncode,0,result.stdout)
            if scenario!='conflict':
                self.assertIn('DEPLOY_FAILED_ROLLED_BACK',result.stdout+result.stderr)
            self.assertEqual(conf.read_text(),original,result.stdout+result.stderr)
            self.assertFalse((root/'container').exists(),result.stdout+result.stderr)
            self.assertFalse((root/'menu').exists(),result.stdout+result.stderr)
            self.assertFalse((root/'etc/nginx/snippets/tehnet-software.conf').exists(),result.stdout+result.stderr)
            self.assertFalse((root/'srv/tehnet-software/data').exists(),result.stdout+result.stderr)

    def test_existing_route_conflict_stops_before_install(self): self.run_scenario('conflict')
    def test_partial_compose_creation_is_cleaned_up(self): self.run_scenario('compose')
    def test_failure_after_data_creation_is_recoverable(self): self.run_scenario('data')
    def test_failure_after_snippet_creation_is_recoverable(self): self.run_scenario('snippet')
    def test_failure_after_nginx_reload_restores_config(self): self.run_scenario('reload')
    def test_failure_after_menu_addition_removes_only_added_item(self): self.run_scenario('menu')
    def test_sigterm_rolls_back_owned_state(self): self.run_scenario('signal')
    def test_success_changes_only_https_server_when_host_has_http_and_https(self): self.run_scenario('success')
    def test_graceful_reload_waits_for_new_worker_readiness(self): self.run_scenario('convergence')
