from pathlib import Path
from datetime import datetime,timezone,timedelta
import copy,hashlib,json,os,tempfile,unittest
from unittest.mock import patch
from tools.offline_refresh import reserve_attempt,should_refresh,validate_acceptance,render_guide,failure_summary
from tools.refresh_transport import reserve_request

ROOT=Path(__file__).resolve().parents[1]
NOW=datetime(2026,10,18,18,tzinfo=timezone.utc)
class OfflineRefreshTests(unittest.TestCase):
    def test_durable_failed_attempts_are_charged_and_next_day_resets(self):
        with tempfile.TemporaryDirectory() as tmp:
            state=Path(tmp)/'state.json'
            for _ in range(2):reserve_attempt(state,NOW)
            with self.assertRaisesRegex(ValueError,'budget'):reserve_attempt(state,NOW)
            reserve_attempt(state,NOW+timedelta(days=1))
            self.assertEqual(json.loads(state.read_text())['attempts'],1)
    def test_last_failure_summary_keeps_reason_and_is_bounded(self):
        summary=failure_summary(ValueError('Candidate too old/changed at publication'))
        self.assertTrue(summary.startswith('ValueError: Candidate too old'))
        self.assertLessEqual(len(summary),len('ValueError')+2+200)
        self.assertEqual(failure_summary(ValueError('x'*999))[-3:],'xxx')
        self.assertIn('RuntimeError',failure_summary(RuntimeError('boom')))

    def test_first_run_is_due_but_success_is_not_repeated_until_twelve_hours(self):
        self.assertTrue(should_refresh({},NOW))
        self.assertFalse(should_refresh({'accepted_at':NOW.isoformat()},NOW+timedelta(hours=11)))
        self.assertTrue(should_refresh({'accepted_at':NOW.isoformat()},NOW+timedelta(hours=12)))
        self.assertTrue(should_refresh({'accepted_at':(NOW-timedelta(hours=13)).isoformat(),'last_failure':'no signature'},NOW))
    def test_each_request_is_charged_before_transport_and_cannot_overrun(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'budget.json';path.write_text('{"used":0,"limit":1048576,"requests":0}')
            reserve_request(path,100000)
            with self.assertRaisesRegex(ValueError,'budget'):reserve_request(path,1048576)
            self.assertEqual(json.loads(path.read_text())['requests'],1)
    def test_foreign_or_missing_install_proof_never_accepts_a_candidate(self):
        profile=json.loads((ROOT/'profiles/noble-devtools-amd64/manifest.json').read_text());profile['accepted']=False
        actual={'installed_packages':len(profile['packages']),'external_connect_refused':True,'offline_lists_before':0,'functional_tools':['git','curl','jq','python','pip','wget','rsync','ssh'],'copyrights':[p['package'] for p in profile['packages']],'negative_checks':{name:{'exit':1,'dpkg_unchanged':True} for name in ['corrupt_required_archive','missing_required_archive','forged_signed_metadata','newer_nonseed_dependency']}}
        actual['negative_checks']['clean_offline_install']={'exit':0,'dpkg_audit':'empty'}
        for evidence in [{},actual,{**actual,'qualified_profile_sha256':'0'*64}]:
            with self.subTest(evidence=bool(evidence)):
                with self.assertRaises(ValueError):validate_acceptance(profile,evidence)
        exact=hashlib.sha256((json.dumps(profile,indent=2)+'\n').encode()).hexdigest()
        self.assertEqual(validate_acceptance(profile,{**actual,'qualified_profile_sha256':exact}),exact)
    def test_guide_uses_current_snapshot_and_preserves_copy_hash(self):
        profile=json.loads((ROOT/'profiles/noble-devtools-amd64/manifest.json').read_text());profile['generated_at_utc']='2026-10-19T12:00:00+00:00'
        text=render_guide(profile)
        self.assertIn('2026-10-19',text)
        self.assertIn('fd35d9874932bc35fa8ff026c8608c61ed86533fc46d9ac56d00387e710e0fc9',text)
        self.assertNotIn('۱۸ اکتبر ۲۰۲۶',text)
        self.assertIn('خودکار',text)
    def test_clock_rollback_cannot_reset_daily_budget(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'ledger.json';reserve_attempt(path,NOW)
            with self.assertRaisesRegex(ValueError,'clock'):reserve_attempt(path,NOW-timedelta(days=1))
    @unittest.skipUnless(os.name=='posix','Directory fsync is a Linux durability gate')
    def test_reservation_directory_is_synced_after_atomic_replace(self):
        from tools.refresh_transport import save
        with tempfile.TemporaryDirectory() as tmp:
            events=[];real_sync=os.fsync;real_replace=os.replace
            def sync(fd):events.append('sync');real_sync(fd)
            def replace(a,b):events.append('replace');real_replace(a,b)
            with patch('tools.refresh_transport.os.fsync',side_effect=sync),patch('tools.refresh_transport.os.replace',side_effect=replace):save(Path(tmp)/'budget.json',{'reserved':True})
            self.assertEqual(events,['sync','replace','sync'])
    def test_pending_publication_is_checked_before_being_recovered(self):
        from tools.offline_refresh import reconcile_pending
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);snippet=root/'snippet';snippet.write_bytes(b'new');backup=root/'before';backup.write_bytes(b'old')
            status={'stage':'publishing','pending':{'old_sha256':hashlib.sha256(b'old').hexdigest(),'new_sha256':hashlib.sha256(b'new').hexdigest(),'before_file':str(backup),'public':'candidate'}}
            calls=[]
            result=reconcile_pending(status,snippet,check=lambda path:calls.append(path),reload=lambda:calls.append('reload'))
            self.assertEqual(calls,['reload','candidate']);self.assertEqual(result['stage'],'recovered_publication')
            snippet.write_bytes(b'new');status['stage']='publishing';calls=[]
            with self.assertRaisesRegex(ValueError,'restored'):
                reconcile_pending(status,snippet,check=lambda path:(_ for _ in ()).throw(ValueError('injected live mismatch')),reload=lambda:calls.append('reload'))
            self.assertEqual(snippet.read_bytes(),b'old');self.assertEqual(calls,['reload','reload'])
    def test_old_operator_runs_are_bounded_and_protected_run_is_kept(self):
        from tools.offline_refresh import prune_runs
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for i in range(16):
                child=root/('run-20261018-1800%02d-aaaaaaaa'%i);child.mkdir();(child/'auto-owned.json').write_text('{"owner":"tehnet-offline-refresh"}')
            keep=sorted(root.iterdir())[0].name;prune_runs(root,keep)
            self.assertEqual(len(list(root.iterdir())),12);self.assertTrue((root/keep).exists())
