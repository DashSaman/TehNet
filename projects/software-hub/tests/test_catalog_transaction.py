import tempfile,unittest
from pathlib import Path
from tools.catalog_transaction import snapshot,restore_public,fingerprint
from app.external_storage import ExternalRegistry

class CatalogRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.store=ExternalRegistry(self.root/'public',visibility='public');self.store.initialize()
        self.backup=self.root/'before.sqlite';snapshot(self.store.database,self.backup)
    def mutate(self):
        with self.store.connection(write=True) as db:db.execute("INSERT INTO external VALUES('fixture','{}','{}','path','https://example.org/file',123,'fixture metadata only')")
    def test_scoped_round_trip_keeps_owner_and_does_not_touch_network_or_other_state(self):
        untouched=self.root/'network.sqlite';untouched.write_bytes(b'budget fixture remains charged')
        owner=self.store.database.stat().st_uid;self.mutate()
        restore_public(self.store.database,self.backup,fingerprint(self.store.database))
        with self.store.connection() as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM external').fetchone(),(0,))
        self.assertEqual(self.store.database.stat().st_uid,owner)
        self.assertEqual(untouched.read_bytes(),b'budget fixture remains charged')
        self.assertEqual(sorted(x.name for x in self.store.root.iterdir()),['external.sqlite'])
    def test_concurrent_new_metadata_refuses_restore_and_preserves_current_bytes(self):
        expected=fingerprint(self.store.database);self.mutate();current=self.store.database.read_bytes()
        with self.assertRaisesRegex(ValueError,'Concurrent metadata'):restore_public(self.store.database,self.backup,expected)
        self.assertEqual(current,self.store.database.read_bytes())
    def test_restricted_snapshot_is_refused(self):
        private=ExternalRegistry(self.root/'private',visibility='restricted');private.initialize()
        with self.assertRaisesRegex(ValueError,'Public snapshot'):restore_public(self.store.database,private.database,fingerprint(self.store.database))
