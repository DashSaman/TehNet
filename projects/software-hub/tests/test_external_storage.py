"""External payload architecture: only metadata may be persisted by the site."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from app.models import Artifact
from app.external_storage import ExternalRegistry
from app.http_client import FetchRejected
import test_http_client as fixture
from test_http_client import Reply,BODY,artifact

class NoDiskVerificationTests(unittest.TestCase):
    def setUp(self):
        self.case=fixture.FetchTests();self.case.setUp();self.addCleanup(self.case.doCleanups)
        self.root=self.case.root;self.source=self.case.source;self.client=self.case.client
    def test_full_verification_never_creates_payload_or_staging_file(self):
        before=set(self.root.rglob('*'))
        with patch('tempfile.mkstemp',side_effect=AssertionError('payload disk write')):
            result=self.client(Reply()).verify_remote(self.source,'fixture.bin',artifact())
        self.assertTrue(result.full_hash_verified)
        self.assertEqual(set(self.root.rglob('*')),before)
    def test_bad_full_hash_rejected_without_payload_files(self):
        with self.assertRaises(FetchRejected):
            self.client(Reply(b'x'*len(BODY))).verify_remote(self.source,'fixture.bin',artifact())
        self.assertEqual(list(self.root.glob('.fetch-*')),[])

class ExternalRegistryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.store=ExternalRegistry(self.root/'registry',visibility='public');self.store.initialize()
        self.case=fixture.FetchTests();self.case.setUp();self.addCleanup(self.case.doCleanups)
        self.case.source=self.case.source.model_copy(update={'visibility':'public'})
        self.item=artifact().model_copy(update={'visibility':'public'})
    def register(self,**kw):
        return self.store.register_verified(self.case.source,'fixture.bin',self.item,self.case.client(Reply()),license_approved=True,provenance='self-created fixture',**kw)
    def test_only_small_metadata_is_persisted_and_exact_url_registered(self):
        self.register()
        self.assertEqual([p.name for p in self.store.root.iterdir()],['external.sqlite'])
        self.assertEqual(self.store.download_target(self.item.sha256),'https://mirror.example/kit/fixture.bin')
        self.assertEqual(self.store.list_artifacts()['total'],1)
    def test_permission_license_full_hash_and_classification_gates(self):
        with self.assertRaises(ValueError):self.store.register_verified(self.case.source,'fixture.bin',self.item,self.case.client(Reply()),license_approved=False,provenance='test')
        with self.assertRaises(FetchRejected):self.store.register_verified(self.case.source,'fixture.bin',self.item,self.case.client(Reply(b'bad')),license_approved=True,provenance='test')
        with self.assertRaises(ValueError):self.store.register_verified(self.case.source,'fixture.bin',artifact(),self.case.client(Reply()),license_approved=True,provenance='test')
        self.assertEqual(self.store.list_artifacts()['total'],0)
    def test_private_external_catalog_requires_live_auth_and_never_redirects(self):
        private=ExternalRegistry(self.root/'private',authorize=lambda context:context=='live');private.initialize()
        private.register_verified(self.case.source,'fixture.bin',artifact(),self.case.client(Reply()),license_approved=True,provenance='test')
        with self.assertRaises(Exception):private.list_artifacts()
        self.assertEqual(private.list_artifacts(context='live')['total'],1)
        with self.assertRaises(ValueError):private.download_target(artifact().sha256,context='live')
    def test_expired_verification_fails_closed(self):
        self.register();self.store.clock=lambda:10**12
        with self.assertRaises(ValueError):self.store.download_target(self.item.sha256)
