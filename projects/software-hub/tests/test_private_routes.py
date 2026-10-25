from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from fastapi.testclient import TestClient
from app.auth import AuthStore
from app.config import Settings
from app.db import initialize
from app.cli import seed_public_research
from app.main import create_app

PASSWORD='fixture-only never a production password 123!'
class CSRF(HTMLParser):
    token=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='input' and a.get('name')=='csrf':self.token=a['value']

class PrivateRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.settings=Settings(data_dir=self.root/'research',auth_dir=self.root/'auth',metadata_dir=self.root/'store',restricted_enabled=True)
        initialize(self.settings.database);seed_public_research(self.settings.database)
        self.auth=AuthStore(self.settings.auth_dir/'auth.sqlite');self.auth.initialize();self.auth.set_password(PASSWORD)
        self.client=TestClient(create_app(self.settings),base_url='https://tehnet.ir');self.addCleanup(self.client.close)
    def form(self):
        r=self.client.get('/software/access/');self.assertEqual(r.status_code,200)
        p=CSRF();p.feed(r.text);return p.token
    def login(self):
        csrf=self.form()
        r=self.client.post('/software/access/',data={'password':PASSWORD,'csrf':csrf},headers={'Origin':'https://tehnet.ir'},follow_redirects=False)
        self.assertEqual(r.status_code,303,r.text);return r
    def test_login_cookie_flags_fixed_redirect_and_local_assets(self):
        r=self.login();cookie=r.headers['set-cookie']
        for value in ['Secure','HttpOnly','SameSite=strict','Path=/software']:self.assertIn(value,cookie)
        self.assertEqual(r.headers['location'],'/software/private/')
        view=self.client.get('/software/private/')
        self.assertEqual(view.status_code,200);self.assertIn('VPN',view.text)
        self.assertIn('no-store',view.headers['cache-control'])
    def test_anonymous_private_methods_are_uniform_and_no_store(self):
        for method in ['GET','HEAD','POST','PUT','OPTIONS']:
            known=self.client.request(method,'/software/private/v1/artifacts')
            unknown=self.client.request(method,'/software/private/not-a-record')
            self.assertEqual(known.status_code,404);self.assertEqual(known.content,unknown.content)
            self.assertIn('no-store',known.headers['cache-control'])
    def test_cross_origin_missing_csrf_and_oversized_body_are_rejected(self):
        csrf=self.form()
        for headers,data in [({'Origin':'https://evil.invalid'},{'csrf':csrf,'password':PASSWORD}),
            ({'Origin':'https://tehnet.ir'},{'password':PASSWORD}),({}, {'csrf':csrf,'password':PASSWORD})]:
            self.assertEqual(self.client.post('/software/access/',data=data,headers=headers).status_code,403)
        r=self.client.post('/software/access/',content=b'x'*5000,headers={'Origin':'https://tehnet.ir','Content-Type':'application/x-www-form-urlencoded'})
        self.assertEqual(r.status_code,413)
    def test_login_wrong_password_has_generic_message_and_rate_limit(self):
        for _ in range(5):
            csrf=self.form();r=self.client.post('/software/access/',data={'csrf':csrf,'password':'wrong'},headers={'Origin':'https://tehnet.ir'})
            self.assertEqual(r.status_code,401);self.assertNotIn('wrong',r.text)
        csrf=self.form();r=self.client.post('/software/access/',data={'csrf':csrf,'password':PASSWORD},headers={'Origin':'https://tehnet.ir'})
        self.assertEqual(r.status_code,429);self.assertIn('retry-after',r.headers)
    def test_logout_csrf_revocation_and_no_get_mutation(self):
        self.login();view=self.client.get('/software/private/');p=CSRF();p.feed(view.text)
        self.assertEqual(self.client.get('/software/access/logout').status_code,404)
        self.assertEqual(self.client.post('/software/access/logout',data={'csrf':p.token},headers={'Origin':'https://evil.invalid'}).status_code,403)
        self.assertEqual(self.client.get('/software/private/').status_code,200)
        r=self.client.post('/software/access/logout',data={'csrf':p.token},headers={'Origin':'https://tehnet.ir'},follow_redirects=False)
        self.assertEqual(r.status_code,303);self.assertEqual(self.client.get('/software/private/').status_code,404)
    def test_public_surfaces_never_contain_private_navigation_or_rows(self):
        self.login()
        for path in ['/software/','/software/v1/artifacts','/software/v1/sources','/software/openapi.json','/software/static/ui.js']:
            r=self.client.get(path);self.assertEqual(r.status_code,200)
            for value in ['VPN',PASSWORD,'auth.sqlite','csrf','/private/']:
                self.assertNotIn(value,r.text,path)
    def test_unconfigured_password_stays_closed_without_initializing_state(self):
        self.auth.path.unlink()
        self.assertEqual(self.client.get('/software/access/').status_code,503)
        self.assertEqual(self.client.get('/software/private/').status_code,404)
        self.assertFalse(self.auth.path.exists())
    def test_password_change_invalidates_current_browser(self):
        self.login();self.auth.set_password(PASSWORD+' changed')
        self.assertEqual(self.client.get('/software/private/').status_code,404)
