import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools.mirror_operations import load_manifest,refresh
from app.external_storage import ExternalRegistry
import test_http_client as fixture

class MirrorOperationsTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        self.store=ExternalRegistry(self.root/'public',visibility='public');self.store.initialize()
        self.case=fixture.FetchTests();self.case.setUp();self.addCleanup(self.case.doCleanups)
        self.source=self.case.source.model_copy(update={'visibility':'public'})
        self.item=fixture.artifact().model_copy(update={'visibility':'public'})
        self.entry={'source':self.source.model_dump(mode='json'),'artifact':self.item.model_dump(mode='json'),'relative_path':'fixture.bin','license_evidence':'https://example.org/license','identity_evidence':'https://example.org/checksum','approved_cidrs':['93.184.216.0/24']}
    def manifest(self,entries=None):return {'format':1,'entries':entries or [self.entry]}
    def test_manifest_rejects_unknown_fields_duplicates_private_or_unapproved(self):
        path=self.root/'manifest.json'
        for value in [{**self.manifest(),'unknown':True},self.manifest([self.entry,self.entry]),self.manifest([{**self.entry,'artifact':{**self.entry['artifact'],'visibility':'restricted'}}])]:
            path.write_text(json.dumps(value))
            with self.assertRaises(ValueError):load_manifest(path)
        path.write_text(json.dumps(self.manifest()));self.assertEqual(len(load_manifest(path)),1)
    def test_actual_stream_verification_publishes_only_metadata_and_preserves_owner(self):
        before=self.store.database.stat()
        with patch('tools.mirror_operations.time.sleep'):
            result=refresh([self.entry],self.store.root,None,client=self.case.client(fixture.Reply()))
        self.assertEqual(result['updated'],1);self.assertEqual(self.store.list_artifacts()['total'],1)
        self.assertEqual([x.name for x in self.store.root.iterdir()],['external.sqlite'])
        self.assertEqual(self.store.database.stat().st_uid,before.st_uid)
        self.assertEqual(self.store.download_target(self.item.sha256),'https://mirror.example/kit/fixture.bin')
    def test_second_failed_verification_leaves_whole_live_registry_unchanged(self):
        original=self.store.database.read_bytes()
        other={**self.entry,'artifact':{**self.entry['artifact'],'sha256':'b'*64,'filename':'second.bin'},'relative_path':'second.bin'}
        with patch('tools.mirror_operations.time.sleep'):
            with self.assertRaises(Exception):refresh([self.entry,other],self.store.root,None,client=self.case.client(fixture.Reply()))
        self.assertEqual(self.store.database.read_bytes(),original)
        self.assertEqual([x.name for x in self.store.root.iterdir()],['external.sqlite'])
    def test_existing_identity_conflict_is_not_overwritten(self):
        with patch('tools.mirror_operations.time.sleep'):refresh([self.entry],self.store.root,None,client=self.case.client(fixture.Reply()))
        original=self.store.database.read_bytes()
        changed={**self.entry,'artifact':{**self.entry['artifact'],'name':'different'}}
        with self.assertRaises(ValueError):refresh([changed],self.store.root,None,client=self.case.client(fixture.Reply()))
        self.assertEqual(original,self.store.database.read_bytes())
    def test_changed_verification_peer_outside_approved_network_never_publishes(self):
        original=self.store.database.read_bytes()
        entry={**self.entry,'approved_cidrs':['8.8.8.0/24']}
        with self.assertRaises(ValueError):refresh([entry],self.store.root,None,client=self.case.client(fixture.Reply()))
        self.assertEqual(original,self.store.database.read_bytes())
