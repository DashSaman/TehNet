from pathlib import Path
from datetime import datetime,timezone,timedelta
from tempfile import TemporaryDirectory
import hashlib,json,unittest
from unittest.mock import patch
try:
    from tools import provider_auto as auto
except ImportError:
    auto=None

class ProviderAutoPolicyTests(unittest.TestCase):
    def setUp(self):self.assertIsNotNone(auto,'Automatic per-publication provider worker is not implemented')
    def test_one_profile_processes_each_source_once_and_crash_is_not_replayed(self):
        state=auto.new_generation('a'*64)
        self.assertEqual(auto.next_provider(state),'arvan')
        state['providers']['arvan']={'outcome':'running','started_at':'2026-10-19T16:00:00+00:00'}
        auto.recover_interrupted(state)
        self.assertEqual(state['providers']['arvan']['outcome'],'interrupted')
        self.assertEqual(auto.next_provider(state),'linuxmirrors')
        for identity in auto.PROVIDERS:state['providers'][identity]={'outcome':'failed'}
        self.assertIsNone(auto.next_provider(state))

    def test_separate_budget_is_durable_bounded_and_refuses_clock_rollback(self):
        now=datetime(2026,10,19,tzinfo=timezone.utc)
        with TemporaryDirectory() as temp:
            path=Path(temp)/'budget.json'
            for i in range(8):auto.reserve(path,now,('a' if i<4 else 'b')*64,auto.PROVIDERS[i%4])
            self.assertEqual(json.loads(path.read_text())['reserved_bytes'],1536*1024**2)
            with self.assertRaises(ValueError):auto.reserve(path,now,'c'*64,'arvan')
            with self.assertRaises(ValueError):auto.reserve(path,now-timedelta(days=1),'c'*64,'arvan')
            self.assertEqual(json.loads(path.read_text())['attempts'],8)

    def test_duplicate_intent_never_reserves_again_or_resets_failed_charge(self):
        with TemporaryDirectory() as temp:
            path=Path(temp)/'budget.json';now=datetime(2026,10,19,tzinfo=timezone.utc)
            auto.reserve(path,now,'a'*64,'arvan')
            with self.assertRaises(ValueError):auto.reserve(path,now,'a'*64,'arvan')
            self.assertEqual(json.loads(path.read_text())['attempts'],1)

    def test_receipt_is_profile_bound_and_only_passed_rows_can_be_projected(self):
        state=auto.new_generation('a'*64)
        state['providers']['arvan']={'provider':'arvan','outcome':'failed','error':'fixture'}
        receipt=auto.receipt(state)
        self.assertEqual(receipt['profile_sha256'],'a'*64)
        self.assertEqual(receipt['providers'][0]['outcome'],'failed')
        self.assertNotIn('error',receipt['providers'][0])

    def test_systemd_lab_keeps_noswap_caps_and_private_engine_inaccessible(self):
        text=auto.lab_unit(Path('/opt/tehnet-software/operations/provider-auto-v1'),Path('/opt/tehnet-software/operations/provider-auto-state/runs/'+'a'*64+'/arvan'),'arvan',Path('/host-site'))
        for gate in ['MemoryMax=900M','MemorySwapMax=0','TimeoutStartSec=1200','InaccessiblePaths=/srv/tehnet-software','NoNewPrivileges=true','LAB_STATE_READ=0','tools.provider_lab']:
            self.assertIn(gate,text)

    def test_preflight_error_is_recorded_without_budget_or_download(self):
        with TemporaryDirectory() as temp:
            root=Path(temp);state=root/'state'
            argv=['provider_auto','--state',str(state),'--receipts',str(root/'receipt'),'--seed',str(root/'seed'),'--host-site',str(root/'host')]
            with patch('sys.argv',argv),patch.object(auto,'lock'),patch.object(auto,'current',side_effect=ValueError('fixture unreadable publication')):
                with self.assertRaisesRegex(ValueError,'fixture unreadable'):auto.main()
            self.assertEqual(json.loads((state/'latest.json').read_text())['stage'],'preflight_failed')
            self.assertFalse((state/'daily-budget.json').exists())

    def test_protection_snapshot_outlives_finite_watch_and_uses_current_owned_files(self):
        self.assertTrue(hasattr(auto,'protected_snapshot'),'Automatic qualifications must not depend on an expired finite watch directory')
        with TemporaryDirectory() as temp:
            root=Path(temp);seed=root/'seed';seed.mkdir();owned=root/'site.conf';owned.write_bytes(b'current owner configuration')
            snippet=root/'software.conf';snippet.write_bytes(b'current software routes')
            (seed/'protected.before').write_text('0'*64+'  '+str(owned)+'\n'+'1'*64+'  /srv/tehnet-software/auth/auth.sqlite\n')
            result=auto.protected_snapshot(seed,snippet)
            self.assertEqual(result[str(owned)],hashlib.sha256(owned.read_bytes()).hexdigest())
            self.assertEqual(result[str(snippet)],hashlib.sha256(snippet.read_bytes()).hexdigest())
            self.assertNotIn('/srv/tehnet-software/auth/auth.sqlite',result)

if __name__=='__main__':unittest.main()
