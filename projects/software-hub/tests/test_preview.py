from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from fastapi.testclient import TestClient
from app.config import Settings
from app.db import initialize
from app.main import create_app
from app.cli import seed_public_research


class PreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.settings=Settings(data_dir=Path(self.temp.name))
        initialize(self.settings.database)
        seed_public_research(self.settings.database)
        with closing(sqlite3.connect(self.settings.database)) as db:
            db.execute("INSERT INTO sources(id,provider,ecosystem,base_url,allowed_hosts_json,config_json,created_at,updated_at) VALUES ('secret-source','SECRET-VPN','vpn','https://secret.invalid/','[]','{}','test','test')")
            db.execute("INSERT INTO artifacts(sha256,size_bytes,ecosystem,name,version,architecture,filename,license_state,created_at) VALUES (?,?,?,'SECRET-ARTIFACT','1','all','private.deb','unreviewed','test')",('a'*64,1,'vpn'))
            db.commit()
        self.client=TestClient(create_app(self.settings),base_url='https://tehnet.ir')

    def tearDown(self):
        self.client.close()
        self.temp.cleanup()

    def test_public_ui_has_tehnet_brand_prefix_and_no_private_data(self):
        response=self.client.get('/software/')
        self.assertEqual(response.status_code,200)
        self.assertIn('آرشیو نرم‌افزار تهران نتورک',response.text)
        self.assertIn('/software/static/style.css',response.text)
        self.assertNotIn('SECRET',response.text)
        self.assertNotIn('ملیکا',response.text)
        self.assertIn('noindex',response.headers['x-robots-tag'])

    def test_source_search_and_counts_exclude_private_records(self):
        response=self.client.get('/software/v1/sources')
        self.assertEqual(response.json()['total'],27)
        self.assertNotIn('SECRET',response.text)
        search=self.client.get('/software/v1/sources?q=SECRET')
        self.assertEqual(search.json()['total'],0)
        self.assertTrue(all(x['routing_enabled'] is False for x in response.json()['items']))
        self.assertNotIn('config_json',response.text)

    def test_private_and_unimplemented_surfaces_deny_all_methods(self):
        for path in ['/private/known','/private/random','/download/'+('a'*64)+'/private.deb']:
            for method in ['GET','HEAD','POST']:
                response=self.client.request(method,'/software'+path,headers={'Range':'bytes=0-4','If-None-Match':'*'})
                self.assertEqual(response.status_code,404)
                self.assertIn('no-store',response.headers['cache-control'])
                self.assertNotIn('SECRET',response.text)

    def test_unregistered_downloads_do_not_redirect_or_probe(self):
        response=self.client.get('/software/download/'+('b'*64)+'/x.deb',follow_redirects=False)
        self.assertEqual(response.status_code,404)
        self.assertNotIn('location',response.headers)
        self.assertEqual(self.client.get('/software/v1/artifacts').json(),{'items':[],'total':0})

    def test_health_does_not_claim_real_apt_or_private_acceptance(self):
        response=self.client.get('/software/readyz')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json()['capabilities'],{'public_research':True,'downloads':False,'apt_profile_accepted':False,'restricted_access':False,'rubika':False})

    def test_api_pagination_limits_and_markup_are_safe(self):
        self.assertEqual(self.client.get('/software/v1/sources?limit=101').status_code,422)
        self.assertEqual(self.client.get('/software/v1/sources?cursor=-1').status_code,422)
        response=self.client.get('/software/?q=%3Cscript%3Ealert(1)%3C/script%3E')
        self.assertNotIn('<script>',response.text)

    def test_profile_is_plan_only_and_openapi_is_local(self):
        response=self.client.get('/software/v1/profiles/noble-core')
        self.assertFalse(response.json()['accepted'])
        self.assertEqual(self.client.get('/software/openapi.json').status_code,200)
        self.assertEqual(self.client.get('/software/docs').status_code,404)

    def test_preview_does_not_capture_wordpress_root_paths(self):
        for path in ['/','/shop/','/services/','/wp-admin/']:
            self.assertEqual(self.client.get(path).status_code,404)

    def test_reseed_keeps_disabled_sources_and_private_rows(self):
        seed_public_research(self.settings.database)
        self.assertEqual(self.client.get('/software/v1/sources').json()['total'],27)
        with closing(sqlite3.connect(self.settings.database)) as db:
            self.assertEqual(db.execute("SELECT visibility FROM sources WHERE id='secret-source'").fetchone(),('restricted',))

    def test_easy_install_has_explained_copyable_online_commands(self):
        response=self.client.get('/software/')
        self.assertTrue('نصب آسان' in response.text,'Easy-install section is absent')
        self.assertIn('data-copy',response.text)
        self.assertIn('sudo apt-get update',response.text)
        self.assertIn('sudo apt-get install --no-install-recommends curl',response.text)
        self.assertIn('نصب آنلاین',response.text)
        self.assertIn('Ubuntu 24.04',response.text)
        self.assertNotIn('curl | bash',response.text)
        self.assertNotIn('trusted=yes',response.text)

    def test_theme_and_copy_assets_are_local_and_csp_allows_only_self_script(self):
        page=self.client.get('/software/')
        self.assertTrue('data-theme="dark"' in page.text,'TehNet theme mode is absent')
        self.assertIn('/software/static/ui.js',page.text)
        self.assertIn("script-src 'self'",page.headers['content-security-policy'])
        js=self.client.get('/software/static/ui.js')
        self.assertEqual(js.status_code,200)
        self.assertIn('navigator.clipboard.writeText',js.text)
        self.assertIn('tn-theme',js.text)
        css=self.client.get('/software/static/style.css').text
        self.assertIn('#080f18',css)
        self.assertIn('#79e7f7',css)
        self.assertIn('Vazirmatn',css)

    def test_home_distinguishes_research_and_live_downloads_without_obsolete_claims(self):
        page=self.client.get('/software/').text
        self.assertFalse('نیازمند آزمون' in page,'Home still renders the same untested badge on every research card')
        self.assertNotIn('هیچ منبعی هنوز برای دانلود خودکار فعال نشده',page)
        self.assertNotIn('بسته آفلاین این ابزارها هنوز آزموده و منتشر نشده',page)
        self.assertIn('href="/software/offline/"',page)
        self.assertIn('<details class="research-archive"',page)
        self.assertIn('زمان و دامنه آزمون',page)


if __name__ == '__main__': unittest.main()
