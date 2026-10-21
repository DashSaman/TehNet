import os,subprocess,unittest
from pathlib import Path

@unittest.skipUnless(os.name=='posix','Linux shell rollback execution')
class CatalogRollbackShellTests(unittest.TestCase):
    def test_every_failed_restore_step_returns_failure_without_false_success(self):
        script=(Path(__file__).resolve().parents[1]/'deployment/scripts/update-public-catalog.sh').read_text()
        rollback=script[script.index('rollback(){'):script.index('\nfailure(){')]
        # Execute the actual rollback function with only its external commands replaced.
        harness='''BACKUP=/fixture
systemctl(){ [[ "$*" != "$FAIL_STEP" ]]; }
install(){ [[ "install ${@: -1}" != "$FAIL_STEP" ]]; }
flock(){ [[ "$FAIL_STEP" != flock ]]; }
python3(){ cat >/dev/null; [[ "$FAIL_STEP" != metadata ]]; }
'''+rollback+'\nrollback\n'
        steps=['stop tehnet-software-mirrors.timer','stop tehnet-software-mirrors.service','flock','metadata','install /etc/systemd/system/tehnet-software-mirrors.service','install /etc/systemd/system/tehnet-software-mirrors.timer','daemon-reload','start tehnet-software-mirrors.timer']
        for step in steps:
            with self.subTest(step=step):
                result=subprocess.run(['bash'],input=harness,text=True,capture_output=True,env={**os.environ,'FAIL_STEP':step})
                self.assertNotEqual(result.returncode,0,result.stdout+result.stderr)
                self.assertNotIn('SCOPED_CATALOG_ROLLBACK_PASS',result.stdout)
        result=subprocess.run(['bash'],input=harness,text=True,capture_output=True,env={**os.environ,'FAIL_STEP':'none'})
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('SCOPED_CATALOG_ROLLBACK_PASS',result.stdout)
