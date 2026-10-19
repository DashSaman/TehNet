from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json,unittest
from fastapi.testclient import TestClient
from app.config import Settings
from app.db import initialize
from app.cli import seed_public_research
from app.main import create_app

class ProviderRoutesTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory();self.root=Path(self.temp.name)
        self.settings=Settings(data_dir=self.root/'data');initialize(self.settings.database);seed_public_research(self.settings.database)
        self.path=self.root/'receipts.json'
        self.path.write_text(json.dumps({'format':1,'profile_sha256':'a'*64,'providers':[
            {'provider':'arvan','outcome':'pass','qualified_profile_sha256':'a'*64,'packages':58,'accepted_at':'2026-10-19T15:00:00+00:00','install_evidence_sha256':'b'*64,'complete_hash_verified_downloads':64,'functional_tools':['git','curl','jq','python','pip','wget','rsync','ssh'],'negative_checks':{**{key:{'exit':1,'dpkg_unchanged':True} for key in ['corrupt_required_archive','missing_required_archive','forged_signed_metadata','newer_nonseed_dependency']},'clean_offline_install':{'exit':0,'dpkg_audit':'empty'}}},
            {'provider':'liara','outcome':'failed','error':'fixture','private_token':'SECRET'},
            {'provider':'private-vpn','outcome':'pass','qualified_profile_sha256':'a'*64,'private_token':'SECRET'}]}))
        self.patch=patch('app.provider_routes.RECEIPTS',self.path);self.patch.start()
        self.client=TestClient(create_app(self.settings),base_url='https://tehnet.ir')

    def tearDown(self):self.client.close();self.patch.stop();self.temp.cleanup()

    def test_only_accepted_known_sources_get_copy_commands(self):
        response=self.client.get('/software/offline/sources/')
        self.assertEqual(response.status_code,200)
        self.assertIn('--provider arvan',response.text)
        self.assertNotIn('--provider liara',response.text);self.assertNotIn('SECRET',response.text)
        self.assertIn('sha256sum --check',response.text);self.assertIn('/software/offline/profile.json',response.text)
        self.assertIn('name="theme-color"',response.text)

    def test_public_receipt_projection_excludes_unknown_private_and_config(self):
        response=self.client.get('/software/offline/sources/acceptance.json')
        self.assertEqual(response.status_code,200)
        self.assertEqual([x['provider'] for x in response.json()['providers']],['arvan'])
        self.assertNotIn('SECRET',response.text);self.assertNotIn('private-vpn',response.text)

    def test_missing_or_mismatched_proof_does_not_offer_activation(self):
        self.path.write_text(json.dumps({'format':1,'profile_sha256':'c'*64,'providers':[{'provider':'arvan','outcome':'pass','qualified_profile_sha256':'a'*64}]}))
        self.assertNotIn('--provider arvan',self.client.get('/software/offline/sources/').text)

    def test_archive_card_links_only_to_accepted_kit_and_uses_dated_install_scope(self):
        response=self.client.get('/software/?q=Arvan')
        self.assertIn('/software/offline/sources/#provider-arvan',response.text)
        self.assertIn('58',response.text)
        self.assertIn('18:30:00+03:30',response.text)

    def test_unknown_provider_and_all_archive_paths_stay_closed(self):
        for path in ['/software/offline/sources/unknown','/software/offline/sources/arvan/file.deb']:
            for method in ['GET','HEAD','POST']:
                response=self.client.request(method,path)
                self.assertEqual(response.status_code,404);self.assertIn('no-store',response.headers['cache-control'])

if __name__=='__main__':unittest.main()
