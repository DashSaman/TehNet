"""Prevent legacy preview deployment from bypassing new-state recovery gates."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

@unittest.skipUnless(os.name=='posix' and shutil.which('bash'),'Linux shell integration fixture')
class EngineOperationTests(unittest.TestCase):
    def guarded_release(self,name):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);base=root/'opt/tehnet-software';release=base/'releases/engine'
            (release/'app').mkdir(parents=True);(release/'app/external_storage.py').write_text('# engine marker')
            binary=root/'bin';binary.mkdir();docker=binary/'docker'
            docker.write_text('#!/bin/sh\necho UNEXPECTED_DOCKER >&2\nexit 99\n');docker.chmod(0o755)
            source=(ROOT/'deployment/scripts'/name).read_text().replace('/opt/tehnet-software',str(base))
            script=root/name;script.write_text(source)
            result=subprocess.run(['bash',str(script),str(release),'sha256:'+'a'*64],capture_output=True,text=True,
                env={**os.environ,'PATH':str(binary)+':'+os.environ['PATH']},timeout=5)
            self.assertEqual(result.returncode,2,result.stdout+result.stderr)
            self.assertIn('ENGINE_RELEASE_REQUIRES_NEW_STATE_BACKUP_AND_ROLLBACK_GATE',result.stdout+result.stderr)
            self.assertNotIn('UNEXPECTED_DOCKER',result.stdout+result.stderr)
    def test_first_preview_install_refuses_engine_before_docker(self):self.guarded_release('deploy-preview.sh')
    def test_preview_update_refuses_engine_before_docker(self):self.guarded_release('update-preview.sh')
    def test_password_wrapper_rejects_pipe_without_touching_state(self):
        result=subprocess.run(['bash',str(ROOT/'deployment/scripts/set-password.sh'),'sha256:'+'a'*64],input='not-a-password\n',capture_output=True,text=True,timeout=5)
        self.assertEqual(result.returncode,2)
        self.assertIn('interactive SSH terminal',result.stderr)
        self.assertNotIn('not-a-password',result.stdout+result.stderr)
