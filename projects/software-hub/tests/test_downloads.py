import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from app.auth import AuthStore
from app.config import Settings
from app.db import initialize
from app.cli import seed_public_research
from app.external_storage import ExternalRegistry
from app.main import create_app
import test_http_client as fixture

class DownloadTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.settings=Settings(data_dir=self.root/'research',metadata_dir=self.root/'metadata',auth_dir=self.root/'auth',restricted_enabled=True)
        initialize(self.settings.database);seed_public_research(self.settings.database)
        self.auth=AuthStore(self.settings.auth_dir/'auth.sqlite');self.auth.initialize();self.auth.set_password('fixture-only password 123!')
        self.records={}
        for visibility in ['public','restricted']:
            case=fixture.FetchTests();case.setUp();self.addCleanup(case.doCleanups)
            store=ExternalRegistry(self.settings.metadata_dir/visibility,visibility=visibility);store.initialize()
            item=fixture.artifact().model_copy(update={'visibility':visibility,'name':'public fixture' if visibility=='public' else 'PRIVATE-SENTINEL'})
            source=case.source.model_copy(update={'visibility':visibility})
            store.register_verified(source,'fixture.bin',item,case.client(fixture.Reply()),license_approved=True,provenance='test only')
            self.records[visibility]=item
        self.client=TestClient(create_app(self.settings),base_url='https://tehnet.ir',follow_redirects=False);self.addCleanup(self.client.close)
    def path(self,visibility):
        item=self.records[visibility]
        return '/software/'+('private/' if visibility=='restricted' else '')+'download/'+item.sha256+'/'+item.filename
    def authorize(self):
        nonce,csrf=self.auth.challenge();token,context=self.auth.login(nonce,csrf,'fixture-only password 123!')
        self.client.cookies.set('__Secure-tehnet-software-session',token,domain='tehnet.ir',path='/software');return token,context
    def test_registered_public_get_head_range_and_conditionals_redirect_without_fetch_or_disk(self):
        before=set(self.root.rglob('*'))
        for method in ['GET','HEAD']:
            r=self.client.request(method,self.path('public'),headers={'Range':'bytes=1-4','If-None-Match':'*'})
            self.assertEqual(r.status_code,307);self.assertEqual(r.headers['location'],'https://mirror.example/kit/fixture.bin')
            self.assertIn('no-store',r.headers['cache-control'])
        self.assertEqual(set(self.root.rglob('*')),before)
        self.assertFalse(any(p.name in ['objects','staging'] for p in self.root.rglob('*')))
    def test_private_known_unknown_all_methods_deny_before_lookup(self):
        for method in ['GET','HEAD','POST','OPTIONS']:
            one=self.client.request(method,self.path('restricted'),headers={'Range':'bytes=0-4','If-None-Match':'*'})
            other=self.client.request(method,'/software/private/download/'+'a'*64+'/fixture.bin')
            self.assertEqual(one.status_code,404);self.assertEqual(one.content,other.content)
            self.assertNotIn('location',one.headers)
    def test_authenticated_private_never_leaks_external_target_and_revoke_precedes_range(self):
        self.authorize()
        for method in ['GET','HEAD']:
            r=self.client.request(method,self.path('restricted'),headers={'Range':'bytes=0-3','If-None-Match':'*'})
            self.assertEqual(r.status_code,503);self.assertNotIn('location',r.headers);self.assertNotIn('mirror.example',r.text)
        self.auth.revoke_all()
        self.assertEqual(self.client.get(self.path('restricted')).status_code,404)
    def test_public_counts_search_openapi_static_exclude_private(self):
        self.authorize()
        for path in ['/software/v1/artifacts','/software/v1/artifacts?q=PRIVATE','/software/','/software/openapi.json']:
            r=self.client.get(path);self.assertNotIn('PRIVATE-SENTINEL',r.text);self.assertNotIn('source_json',r.text)
        result=self.client.get('/software/v1/artifacts').json();self.assertEqual(result['total'],1)
        for key in ['visibility','provenance','url','relative_path','source_json']:self.assertNotIn(key,result['items'][0])
        self.assertEqual(self.client.get('/software/v1/artifacts?q=PRIVATE').json()['total'],0)
        self.assertEqual(self.client.get('/software/static/../restricted/external.sqlite').status_code,404)
    def test_wrong_name_unknown_identity_arbitrary_url_and_path_deny(self):
        for path in [self.path('public').replace('fixture.bin','other.bin'),'/software/download/'+'a'*64+'/fixture.bin','/software/download?url=https://evil.invalid','/software/objects/'+self.records['public'].sha256]:
            self.assertEqual(self.client.get(path).status_code,404)
    def test_metadata_expiry_returns_503_without_redirect(self):
        store=ExternalRegistry(self.settings.metadata_dir/'public',visibility='public')
        with store.connection(write=True) as db:db.execute('UPDATE external SET verified_at=0')
        r=self.client.get(self.path('public'));self.assertEqual(r.status_code,503);self.assertNotIn('location',r.headers)
