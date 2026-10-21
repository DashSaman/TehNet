import hashlib,json,shutil,sqlite3,subprocess,tarfile,tempfile,unittest
from contextlib import closing
from pathlib import Path
from app.recovery import backup_state,restore_state,validate_manifest,validate_state,valid_decryption_status,RecoveryRejected,STATE_FILES
from app.auth import AuthStore
from app.db import initialize
from app.external_storage import ExternalRegistry
from app.health import NetworkBudget

IMAGE='sha256:'+'a'*64
def state(root):
    initialize(root/'data/catalog.sqlite')
    for v in ['public','restricted']:ExternalRegistry(root/'metadata'/v,visibility=v).initialize()
    AuthStore(root/'auth/auth.sqlite').initialize();NetworkBudget(root/'ops/network.sqlite').initialize()

class RecoveryContractTests(unittest.TestCase):
    def test_authenticated_aes256_mdc_and_ocb_status_only(self):
        for info in [b'2 9',b'2 9 0',b'0 9 2']:
            self.assertTrue(valid_decryption_status(b'[GNUPG:] DECRYPTION_INFO '+info+b'\n[GNUPG:] DECRYPTION_OKAY\n[GNUPG:] GOODMDC\n',0))
        for value in [b'[GNUPG:] PLAINTEXT 62 1 name\n',b'[GNUPG:] DECRYPTION_INFO 0 9 0\n',b'[GNUPG:] DECRYPTION_INFO 2 3 0\n']:
            self.assertFalse(valid_decryption_status(value+b'[GNUPG:] DECRYPTION_OKAY\n[GNUPG:] GOODMDC\n',0))
    def test_manifest_rejects_traversal_duplicate_unknown_and_excess_sizes(self):
        records=[{'path':n,'size':1,'sha256':'b'*64} for n in STATE_FILES]
        base={'format':1,'image':IMAGE,'files':records}
        validate_manifest(base)
        for changed in [{**base,'format':2},{**base,'files':records+records[:1]},
                        {**base,'files':[{**records[0],'path':'../auth.sqlite'},*records[1:]]},
                        {**base,'files':[{**records[0],'size':2**40},*records[1:]]}]:
            with self.assertRaises(RecoveryRejected):validate_manifest(changed)
    def test_actual_schema_required_not_just_identity_and_future_versions_fail(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);state(root);validate_state(root)
            with closing(sqlite3.connect(root/'auth/auth.sqlite')) as db:db.execute('DROP TABLE credential');db.commit()
            with self.assertRaises(RecoveryRejected):validate_state(root)

@unittest.skipUnless(shutil.which('gpg'),'Real GPG tests require Linux GPG')
class EncryptedRecoveryTests(unittest.TestCase):
    def restore(self,bundle,target):return restore_state(bundle,target,self.keys,expected_sha256=hashlib.sha256(bundle.read_bytes()).hexdigest())
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.keys=Path(cls.tmp.name);cls.keys.chmod(0o700)
        subprocess.run(['gpg','--no-options','--homedir',str(cls.keys),'--batch','--pinentry-mode','loopback','--passphrase','','--quick-generate-key','TehNet TEST ONLY <recovery@invalid>','rsa2048','encr','1d'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        text=subprocess.check_output(['gpg','--no-options','--homedir',str(cls.keys),'--batch','--with-colons','--list-keys'],text=True,stderr=subprocess.DEVNULL)
        cls.fpr=next(x.split(':')[9] for x in text.splitlines() if x.startswith('fpr:'))
    @classmethod
    def tearDownClass(cls):
        subprocess.run(['gpgconf','--homedir',str(cls.keys),'--kill','gpg-agent'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);cls.tmp.cleanup()
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.active=self.root/'active';state(self.active)
        self.auth=AuthStore(self.active/'auth/auth.sqlite');self.auth.set_password('fixture-only recovery password 123!')
        nonce,csrf=self.auth.challenge();self.token,_=self.auth.login(nonce,csrf,'fixture-only recovery password 123!')
    def backup(self):
        target=self.root/'backup.gpg';backup_state(self.active,target,self.keys,self.fpr,IMAGE,quiesced=True);return target
    def test_real_roundtrip_invalidates_restored_sessions_preserves_active_and_credentials(self):
        target=self.backup();before=(self.active/'auth/auth.sqlite').read_bytes()
        result=self.restore(target,self.root/'restore')
        self.assertTrue(result['verified']);self.assertEqual(before,(self.active/'auth/auth.sqlite').read_bytes())
        auth=AuthStore(self.root/'restore/auth/auth.sqlite');self.assertIsNone(auth.session(self.token))
        nonce,csrf=auth.challenge();self.assertTrue(auth.login(nonce,csrf,'fixture-only recovery password 123!')[0])
    def test_corrupt_ciphertext_and_existing_restore_never_activate(self):
        bundle=self.backup();data=bytearray(bundle.read_bytes());data[-20]^=1;bundle.write_bytes(data)
        with self.assertRaises(RecoveryRejected):self.restore(bundle,self.root/'bad')
        self.assertFalse((self.root/'bad/RESTORE_VERIFIED.json').exists())
        with self.assertRaises(RecoveryRejected):self.restore(bundle,self.active)
        self.assertTrue(self.auth.configured)
    def test_plain_openpgp_store_packet_is_not_accepted_as_encrypted(self):
        bundle=self.backup();plain=self.root/'plain.tar'
        subprocess.run(['gpg','--no-options','--homedir',str(self.keys),'--batch','--output',str(plain),'--decrypt',str(bundle)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        unencrypted=self.root/'store.gpg'
        subprocess.run(['gpg','--no-options','--homedir',str(self.keys),'--batch','--output',str(unencrypted),'--store',str(plain)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        with self.assertRaises(RecoveryRejected):self.restore(unencrypted,self.root/'plaintext-rejected')
    def test_untrusted_ciphertext_digest_is_rejected(self):
        bundle=self.backup()
        with self.assertRaises(RecoveryRejected):restore_state(bundle,self.root/'wrong-digest',self.keys,expected_sha256='0'*64)
    def test_backup_requires_writer_freeze_and_exclusive_output(self):
        with self.assertRaises(RecoveryRejected):backup_state(self.active,self.root/'bad',self.keys,self.fpr,IMAGE,quiesced=False)
        bundle=self.backup();before=bundle.read_bytes()
        with self.assertRaises(RecoveryRejected):backup_state(self.active,bundle,self.keys,self.fpr,IMAGE,quiesced=True)
        self.assertEqual(before,bundle.read_bytes())
